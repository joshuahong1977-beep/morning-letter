# Morning Market Brief 자동화

매일 평일 오전 **7:30(KST)**에 구글뉴스에서 관련 뉴스를 자동 수집해 뉴스레터 초안(HTML)을 만들고,
지정한 검토용 이메일로 자동 발송합니다. **직접 발송되는 것이 아니라 검토용으로만 전달**되며,
확인 후 실제 메일링 리스트로는 본인이 직접 전달/발송합니다.

---

## 1. 폴더 구성

```
morning-brief-automation/
├── config/keywords.py          ← 검색 키워드(고객사, 경쟁사 등) 설정
├── scripts/generate_brief.py   ← 뉴스 수집 + 뉴스레터 생성 스크립트
├── templates/brief_template.html
├── .github/workflows/morning-brief.yml   ← 자동 실행 설정
├── output/                     ← 생성된 뉴스레터 HTML 저장 위치
└── requirements.txt
```

---

## 2. 처음 설정하기 (한 번만 하면 됩니다)

### 2-1. GitHub 저장소 만들기
1. https://github.com 에서 계정이 없다면 새로 만듭니다 (무료).
2. 오른쪽 상단 **+** → **New repository** 클릭.
3. 이름 예: `morning-market-brief`. **Private**로 설정하는 것을 추천합니다 (키워드/이메일 정보 보호).
4. 저장소 생성 후, 이 폴더(`morning-brief-automation` 안의 모든 파일)를 그대로 업로드합니다.
   - 웹에서 "Add file" → "Upload files"로 드래그 앤 드롭 해도 되고,
   - Git에 익숙하다면 `git init` → `git add .` → `git commit` → `git push`로 올려도 됩니다.

### 2-2. 키워드 채우기
`config/keywords.py` 파일을 열어서 아래 항목을 실제 정보로 바꿔주세요.
- `CUSTOMERS` : 유비쿼스 고객사명 목록
- `COMPETITORS` : 경쟁사명 목록
- `SEMICONDUCTOR`, `RAW_MATERIALS`, `OTHERS` : 필요시 키워드 추가/삭제

이 파일만 수정하면 되고, 스크립트 코드는 건드릴 필요 없습니다.

### 2-3. 검토용 Gmail 앱 비밀번호 발급
뉴스레터 초안을 보낼 발신 계정이 필요합니다 (Gmail 기준).
1. 발신용으로 쓸 Gmail 계정에서 **2단계 인증**을 켭니다. (설정 안 되어 있으면 앱 비밀번호 생성 불가)
2. https://myaccount.google.com/apppasswords 접속
3. 앱 이름을 아무거나 입력(예: "Morning Brief") 후 **생성**
4. 나오는 16자리 비밀번호를 복사해둡니다 (로그인 비밀번호와 다른 별도 값입니다).

### 2-4. GitHub에 비밀 정보(Secrets) 등록
저장소 페이지에서:
`Settings` → 왼쪽 메뉴 `Secrets and variables` → `Actions` → `New repository secret`

아래 3개를 각각 등록합니다.

| Name | Value |
|---|---|
| `GMAIL_USER` | 발신용 Gmail 주소 (예: yourname@gmail.com) |
| `GMAIL_APP_PASSWORD` | 위에서 발급받은 16자리 앱 비밀번호 |
| `REVIEW_EMAIL` | 초안을 받아볼 본인 이메일 주소 (발신 계정과 같아도 됩니다) |

---

## 3. 정상 작동 테스트하기

설정을 마쳤다면 자동 실행 시각까지 기다리지 않고 바로 테스트할 수 있습니다.

1. 저장소 상단 메뉴에서 **Actions** 탭 클릭
2. 왼쪽 목록에서 **Morning Market Brief** 워크플로우 선택
3. 오른쪽의 **Run workflow** 버튼 클릭 → 다시 **Run workflow** 확인
4. 1~2분 후 실행이 끝나면(초록 체크 표시), `REVIEW_EMAIL`로 지정한 메일함을 확인합니다.
5. 메일이 안 왔다면 실행 로그(초록/빨강 표시 클릭)에서 에러 메시지를 확인하세요. 대부분 Secrets 오타 문제입니다.

---

## 4. 매일 아침 사용하는 방법

1. 평일 오전 **7:30(KST)**, 자동으로 뉴스가 수집되어 실행됩니다.
2. 몇 분 내로 지정한 검토용 이메일로 `[검토용] YYYY년 MM월 DD일 Morning Market Brief 초안` 메일이 도착합니다.
3. 메일을 열어 헤드라인/링크/요약을 확인합니다.
   - 자동 요약은 구글뉴스 RSS 스니펫 기반이라 부정확할 수 있으니 **반드시 검토**하세요.
   - 필요 없는 뉴스는 지우고, 놓친 뉴스는 직접 추가하면 됩니다.
4. 검토가 끝나면 해당 내용을 실제 메일링 리스트로 **직접 전달/발송**합니다.
   - 메일 내용을 복사해서 새 메일로 보내거나,
   - 받은 메일을 그대로 전체 전달(Forward) 해도 됩니다.

> 자동으로 메일링 리스트에 바로 발송되지 않는 것은 의도된 설계입니다 (오탐/오류 방지를 위해 반드시 사람이 최종 확인).

---

## 5. 자주 변경하는 설정

### 실행 시각 바꾸기
`.github/workflows/morning-brief.yml` 파일의 `cron` 값을 수정합니다.
```
- cron: "30 22 * * 0-4"
```
- 시간은 **UTC 기준**이며 KST는 UTC+9입니다. (예: 8:00 KST로 바꾸려면 `"0 23 * * 0-4"`)
- 요일 `0-4`는 UTC 기준 일~목요일로, KST 기준 월~금과 대응됩니다. 요일 계산이 헷갈리면 언제든 물어보세요.

### 뉴스 조회 기간 바꾸기
`config/keywords.py`의 `LOOKBACK_HOURS` 값을 조정합니다. (기본 20시간)

### 섹션별 뉴스 개수 바꾸기
`config/keywords.py`의 `SECTIONS`에서 각 섹션의 `max_items` 값을 조정합니다.

---

## 6. 참고 / 한계

- 뉴스 출처는 **구글뉴스 RSS**(무료)를 사용하므로, 특정 전문 매체만 다루는 뉴스는 누락될 수 있습니다.
  → 필요하다면 이후에 특정 언론사 RSS나 유료 뉴스 API로 교체 가능합니다.
- 요약문은 원문 자동 발췌라 정확한 팩트 요약이 아닐 수 있습니다. 발송 전 확인이 꼭 필요합니다.
- 완전히 전원이 꺼진 PC와 무관하게 클라우드(GitHub)에서 실행되므로 PC 상태는 신경 쓰지 않아도 됩니다.
