# -*- coding: utf-8 -*-
"""
Morning Market Brief 자동 생성 스크립트
========================================
1. 구글뉴스 RSS로 섹션별 키워드 뉴스를 수집
2. 최근 N시간 이내 뉴스만 필터링, 중복 제거
3. templates/brief_template.html 에 채워서 결과 HTML 생성
4. output/ 폴더에 저장 + (설정된 경우) 검토용 이메일로 자동 발송

실행: python scripts/generate_brief.py
"""

import os
import re
import html
import smtplib
import calendar
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.keywords import SECTIONS, LOOKBACK_HOURS

KST = timezone(timedelta(hours=9))
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "brief_template.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"


def clean_text(raw_html: str) -> str:
    """RSS 요약에서 HTML 태그 제거 + 공백 정리"""
    text = re.sub(r"<[^>]+>", "", raw_html or "")
    text = html.unescape(text)
    return " ".join(text.split())


def fetch_keyword_entries(keyword: str, lookback_hours: int):
    """키워드 하나로 구글뉴스 RSS 검색, 최근 N시간 이내 항목만 반환"""
    url = GOOGLE_NEWS_RSS.format(query=keyword.replace(" ", "+"))
    feed = feedparser.parse(url)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    results = []
    for entry in feed.entries:
        published_dt = None
        if getattr(entry, "published_parsed", None):
            published_dt = datetime.fromtimestamp(
                calendar.timegm(entry.published_parsed), tz=timezone.utc
            )
        # 시간 정보가 없으면 일단 포함 (구글뉴스는 대부분 시간 정보 있음)
        if published_dt and published_dt < cutoff:
            continue

        source = ""
        if getattr(entry, "source", None) and hasattr(entry.source, "title"):
            source = entry.source.title

        summary = clean_text(getattr(entry, "summary", ""))
        if len(summary) > 110:
            summary = summary[:110].rstrip() + "…"

        results.append({
            "title": clean_text(entry.title),
            "link": entry.link,
            "source": source,
            "published_dt": published_dt,
            "summary": summary,
        })
    return results


def dedupe_and_limit(entries, max_items):
    """제목 기준 중복 제거 후 최신순 정렬, 최대 max_items개만 반환"""
    seen_titles = set()
    unique = []
    for e in entries:
        key = e["title"][:40]  # 제목 앞부분 기준 중복 판단 (완전 일치 아니어도 유사 기사 걸러줌)
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(e)

    unique.sort(key=lambda x: x["published_dt"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return unique[:max_items]


def format_time_label(published_dt):
    if not published_dt:
        return "시간 미상"
    local = published_dt.astimezone(KST)
    return local.strftime("%m/%d %H:%M")


def build_item_html(entry):
    source = entry["source"] or "출처 미상"
    time_label = format_time_label(entry["published_dt"])
    summary = entry["summary"] or "[요약 없음 — 원문 확인 필요]"
    return f"""
  <tr>
    <td style="padding:16px 36px 0 36px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-bottom:1px solid #ececef; padding-bottom:14px;">
        <tr>
          <td style="padding-bottom:14px;">
            <a href="{entry['link']}" style="font-size:15px; font-weight:600; color:#1a1a1f; text-decoration:none; line-height:1.4;">
              {html.escape(entry['title'])}
            </a>
            <div style="font-size:13px; color:#5a5a62; line-height:1.6; margin-top:6px;">
              {html.escape(summary)}
            </div>
            <div style="font-size:11.5px; color:#a0a0a8; margin-top:6px;">
              {html.escape(source)} · {time_label}
            </div>
          </td>
        </tr>
      </table>
    </td>
  </tr>"""


def build_section_html(title, entries):
    header = f"""
  <tr>
    <td style="padding:26px 36px 0 36px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="font-size:14px; font-weight:700; color:#1a1a1f; padding-bottom:6px; border-bottom:2px solid #1a1a1f;">
            {html.escape(title)}
          </td>
        </tr>
      </table>
    </td>
  </tr>"""

    if not entries:
        empty_item = """
  <tr>
    <td style="padding:16px 36px 24px 36px;">
      <div style="font-size:13px; color:#a0a0a8;">최근 시간대 내 관련 뉴스가 검색되지 않았습니다.</div>
    </td>
  </tr>"""
        return header + empty_item

    items_html = "".join(build_item_html(e) for e in entries)
    return header + items_html


def build_top_summary(all_section_entries):
    """전 섹션에서 가장 최신 3건을 뽑아 상단 요약으로 사용 (초안이므로 검토 필요)"""
    flat = []
    for sec in all_section_entries:
        flat.extend(sec["entries"])
    flat.sort(key=lambda x: x["published_dt"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    top = flat[:3]
    if not top:
        return "<li>자동 추출된 뉴스가 없습니다. 직접 확인해주세요.</li>"
    return "".join(f"<li>{html.escape(e['title'])}</li>" for e in top)


def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_section_entries = []
    for section in SECTIONS:
        raw_entries = []
        for kw in section["keywords"]:
            raw_entries.extend(fetch_keyword_entries(kw, LOOKBACK_HOURS))
        final_entries = dedupe_and_limit(raw_entries, section["max_items"])
        all_section_entries.append({
            "key": section["key"],
            "title": section["title"],
            "entries": final_entries,
        })

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    now_kst = datetime.now(KST)
    date_korean = now_kst.strftime("%Y년 %m월 %d일") + " (" + "월화수목금토일"[now_kst.weekday()] + ")"

    replacements = {
        "{{DATE_KOREAN}}": date_korean,
        "{{GENERATED_TIME}}": now_kst.strftime("%H:%M"),
        "{{PREHEADER}}": "오늘의 자동 수집 브리핑 초안입니다. 발송 전 검토해주세요.",
        "{{TOP_SUMMARY_ITEMS}}": build_top_summary(all_section_entries),
    }

    section_map = {
        "customers": "{{CUSTOMERS_SECTION}}",
        "competitors": "{{COMPETITORS_SECTION}}",
        "semiconductor": "{{SEMICONDUCTOR_SECTION}}",
        "raw_materials": "{{RAW_MATERIALS_SECTION}}",
        "others": "{{OTHERS_SECTION}}",
    }
    for sec in all_section_entries:
        placeholder = section_map[sec["key"]]
        replacements[placeholder] = build_section_html(sec["title"], sec["entries"])

    result_html = template
    for key, value in replacements.items():
        result_html = result_html.replace(key, value)

    output_filename = f"{now_kst.strftime('%Y-%m-%d')}_morning_brief.html"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_html)

    print(f"[OK] 브리핑 생성 완료: {output_path}")
    return output_path, result_html, date_korean


def send_review_email(html_content: str, date_korean: str):
    """검토용 이메일 발송 (GitHub Secrets에 설정된 경우에만 동작)"""
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    review_email = os.environ.get("REVIEW_EMAIL")

    if not (gmail_user and gmail_app_password and review_email):
        print("[SKIP] 이메일 발송 환경변수가 설정되지 않아 발송을 건너뜁니다. (로컬 테스트 시 정상)")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[검토용] {date_korean} Morning Market Brief 초안"
    msg["From"] = gmail_user
    msg["To"] = review_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, [review_email], msg.as_string())

    print(f"[OK] 검토용 이메일 발송 완료 → {review_email}")


if __name__ == "__main__":
    _, html_out, date_kr = generate()
    send_review_email(html_out, date_kr)
