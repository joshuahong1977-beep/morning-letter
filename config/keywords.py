# -*- coding: utf-8 -*-
"""
키워드 설정 파일
=================
아래 각 리스트에 실제 회사명/키워드를 입력하세요.
한 섹션에 여러 키워드를 넣으면 각각 검색해서 모두 합쳐줍니다.

주의:
- 너무 일반적인 단어(예: "반도체")만 넣으면 관련 없는 뉴스가 많이 섞일 수 있어요.
- 회사명 + 업종 키워드를 함께 넣는 것을 추천합니다. (예: "OO전자 스위치")
"""

# 1) 유비쿼스 고객사 (실제 고객사명으로 교체하세요)
CUSTOMERS = [
    "KT",
    "SK브로드밴드",
    "LG유플러스",
    # "고객사명4",
]

# 2) 경쟁사 (실제 경쟁사명으로 교체하세요)
COMPETITORS = [
    "유비쿼스 경쟁사1",
    "유비쿼스 경쟁사2",
    # "경쟁사명3",
]

# 3) 반도체 / 부품 시장
SEMICONDUCTOR = [
    "DDR5 가격",
    "낸드플래시 가격",
    "MLCC 시장",
    "네트워크 칩셋",
    "반도체 공급망",
]

# 4) 원자재 시장
RAW_MATERIALS = [
    "구리 가격",
    "희토류 수출",
    "원자재 가격 동향",
]

# 5) 기타 주요 뉴스 (자유롭게 추가/삭제)
OTHERS = [
    "네트워크 장비 시장",
    "통신 장비 정책",
]

# 섹션별 표시 이름과 키워드를 묶어서 관리
SECTIONS = [
    {"key": "customers", "title": "고객사 동향", "keywords": CUSTOMERS, "max_items": 5},
    {"key": "competitors", "title": "경쟁사 동향", "keywords": COMPETITORS, "max_items": 5},
    {"key": "semiconductor", "title": "반도체 · 부품 시장 (칩셋 / DDR / Flash / MLCC)", "keywords": SEMICONDUCTOR, "max_items": 6},
    {"key": "raw_materials", "title": "원자재 시장 동향", "keywords": RAW_MATERIALS, "max_items": 4},
    {"key": "others", "title": "기타 주요 뉴스", "keywords": OTHERS, "max_items": 4},
]

# 몇 시간 이내 뉴스까지 포함할지 (예: 20시간 = 전날 밤부터 당일 아침까지)
LOOKBACK_HOURS = 20
