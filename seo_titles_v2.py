#!/usr/bin/env python3
"""
SEO 최적화 제목 생성기 v2 — 대폭 강화판
- 50+ 제목 변형 per area/category
- 해시 절대 포함 안 함 (버그 수정)
- 7가지 카테고리별 템플릿
- 한국인 여행자 검색 의도 반영
"""

import random
from datetime import datetime

YEAR = datetime.now().year

# ============================================================
# 7가지 제목 유형별 템플릿 (각 8~10개 = 50+ 총)
# ============================================================

# 1. Guide type: 가이드, 완벽 정리, 총정리, 초보 가이드
GUIDE_TEMPLATES = [
    "{area} {cat} 완벽 가이드 — 가격·위치·팁 총정리 ({year})",
    "{area} {cat} 총정리 — 이것만 보면 끝 ({year})",
    "{area} {cat} 초보 가이드 — 처음 가는 사람을 위해",
    "{area} 자유여행 {cat} 완벽 정리 — {year} 최신판",
    "{area} {cat} 가이드 — 10년차 블로거가 정리한 정보",
    "{area} 여행 {cat} — A to Z 완벽 가이드",
    "{area} {cat} 정석 가이드 — 비용·일정·팁 총정리",
    "{area} {cat} 완벽 분석 — 장단점 비교 ({year})",
]

# 2. List type: TOP5, BEST10, 추천 리스트, 필수 코스
LIST_TEMPLATES = [
    "{area} {cat} BEST{N} — 현지인 추천 ({year})",
    "{area} {cat} TOP{N} — 놓치면 후회하는 곳",
    "{area} {cat} 추천 리스트 — 예산별 BEST ({year})",
    "{area} {cat} 필수 코스 — 하루 일정 추천",
    "{area} 여행 {cat} 추천 TOP{N} ({year})",
    "{area} {cat} 순위 — 가성비 기준 BEST{N}",
    "{area} {cat} PICK — {year} 인기 장소 TOP{N}",
    "{area} {cat} 추천 — 꼭 가봐야 할 {N}곳 ({year})",
]

# 3. Review type: 솔직 후기, 실제 후기, 직접 다녀온
REVIEW_TEMPLATES = [
    "{area} {cat} 솔직 후기 — 직접 다녀온 후기",
    "{area} {cat} 실제 후기 — 가격·팁·총평 ({year})",
    "{area} {cat} 리뷰 — 10년차 블로거 솔직 평가",
    "{area} 여행 {cat} 후기 — 좋은 점만 말하지 않겠습니다",
    "{area} {cat} 탐방기 — 현장에서 느낀 그대로",
    "{area} {cat} 체험 후기 — 재방문 의사 있습니다 ({year})",
    "{area} {cat} 솔직 리뷰 — 기대 vs 현실 비교",
    "{area} {cat} 다녀온 후기 — 사진과 함께 ({year})",
]

# 4. Comparison type: 가격 비교, 비용 정리, 가성비
COMPARISON_TEMPLATES = [
    "{area} {cat} 가격 비교 — 로컬 vs 투어 vs 호텔 ({year})",
    "{area} {cat} 비용 정리 — 예산별 추천",
    "{area} {cat} 가성비 비교 — 어디가 좋을까? ({year})",
    "{area} 여행 {cat} 비용 — 절약 꿀팁 총정리",
    "{area} {cat} 가격 정보 — {year} 최신 업데이트",
    "{area} {cat} 예산 가이드 — 하루/1박/3박 비용 비교",
    "{area} {cat} 비용 비교 — 현지인 vs 관광지 가격 ({year})",
    "{area} {cat} 가성비 분석 — 최저가 코스 추천",
]

# 5. Tip type: 꿀팁, 숨은 명소, 현지인 추천
TIP_TEMPLATES = [
    "{area} {cat} 꿀팁 — 현지인이 알려주는 비법 ({year})",
    "{area} {cat} 숨은 명소 — 관광객 모르는 곳",
    "{area} {cat} 현지인 추천 — 진짜 맛집/명소 ({year})",
    "{area} 여행 {cat} 꿀팁 — 모르면 손해인 정보",
    "{area} {cat} 블로그에 없는 진짜 정보 ({year})",
    "{area} {cat} 꿀팁 대방출 — 실전 경험 기반",
    "{area} {cat} 숨겨진 스팟 — 로컬만 아는 곳 ({year})",
    "{area} {cat} 비법 공개 — 시간·비용 절약 팁",
]

# 6. Season type: 최신, 최신판, 업데이트
SEASON_TEMPLATES = [
    "{area} {cat} {year} 최신 정보 — 업데이트 완료",
    "{year} {area} {cat} 최신판 — 가격 변동 반영",
    "{area} {cat} {year} 업데이트 — 새롭게 바뀐 정보",
    "{area} 여행 {cat} — {year}년 최신 가격 ({month}월 기준)",
    "{area} {cat} 최신 가이드 — {year}년 {season} 추천",
    "{year}년 {area} {cat} — 달라진 점 총정리",
    "{area} {cat} {year} 버전 — 이전과 뭐가 다를까?",
    "{area} {cat} 최신 후기 — {year}년 {month}월 방문 ({year})",
]

# 7. Experience type: 체험 후기, 투어 후기, 하루 코스
EXPERIENCE_TEMPLATES = [
    "{area} {cat} 체험 후기 — 하루 코스 추천 ({year})",
    "{area} {cat} 투어 후기 — 가이드 투어 vs 자유 ({year})",
    "{area} {cat} 하루 코스 — 최적의 동선 추천",
    "{area} 여행 {cat} — {days}박 {days2}일 일정 ({year})",
    "{area} {cat} 체험 가이드 — 예약부터 완벽 정리",
    "{area} {cat} 투어 추천 — 가성비 BEST ({year})",
    "{area} {cat} 데이 코스 — 아침부터 저녁까지",
    "{area} {cat} 체험 리스트 — {year} 인기 액티비티",
]

ALL_TEMPLATE_GROUPS = [
    GUIDE_TEMPLATES, LIST_TEMPLATES, REVIEW_TEMPLATES,
    COMPARISON_TEMPLATES, TIP_TEMPLATES, SEASON_TEMPLATES,
    EXPERIENCE_TEMPLATES,
]

# ============================================================
# 지역별 SEO 키워드
# ============================================================

SEO_KEYWORDS = {
    "우붓": {
        "primary": ["우붓 맛집", "우붓 가볼만한곳", "우붓 숙소", "우붓 여행코스", "우붓 라이스테라스"],
        "secondary": ["우붓 원숭이숲", "우붓 카페", "우붓 마사지", "우붓 풀빌라", "우붓 자유여행"],
        "longtail": ["우붓 맛집 추천 2026", "우붓 1일 여행코스", "우붓 테갈랑 라이스테라스", "우붓 인스타 맛집", "우붓 가성비 숙소"],
    },
    "스미냑": {
        "primary": ["스미냑 맛집", "스미냑 비치클럽", "스미냑 숙소", "스미냑 쇼핑", "스미냑 해변"],
        "secondary": ["스미냑 선셋", "스미냑 카페", "스미냑 마사지", "스미냑 풀빌라", "스미냑 자유여행"],
        "longtail": ["스미냑 비치클럽 추천 2026", "스미냑 포테이토헤드", "스미냑 브런치 맛집", "스미냑 부티크 호텔", "스미냑 나이트라이프"],
    },
    "꾸따": {
        "primary": ["꾸따 맛집", "꾸따 해변", "꾸따 서핑", "꾸따 숙소", "꾸따 쇼핑몰"],
        "secondary": ["꾸따 비치워크", "꾸따 나이트라이프", "꾸따 마사지", "꾸따 자유여행", "꾸따 공항근처"],
        "longtail": ["꾸따 서핑 강습 가격", "꾸따 비치워크 맛집", "꾸따 가성비 숙소 2026", "꾸따 공항에서 가까운 호텔", "꾸따 워터밤"],
    },
    "사누르": {
        "primary": ["사누르 맛집", "사누르 해변", "사누르 숙소", "사누르 일출", "사누르 자전거"],
        "secondary": ["사누르 선셋", "사누르 카페", "사누르 마사지", "사누르 자유여행", "사누르 시장"],
        "longtail": ["사누르 일출 명소 2026", "사누르 자전거 코스", "사누르 가성비 리조트", "사누르 마크벵 맛집", "사누르 나이트마켓"],
    },
    "누사두아": {
        "primary": ["누사두아 맛집", "누사두아 리조트", "누사두아 해변", "누사두아 숙소", "누사두아 물놀이"],
        "secondary": ["누사두아 워터블로우", "누사두아 쇼핑", "누사두아 마사지", "누사두아 자유여행", "누사두아 풀빌라"],
        "longtail": ["누사두아 뮬리아 리조트 후기", "누사두아 워터블로우 가는법", "누사두아 가족 여행 2026", "누사두아 올인클루시브 리조트", "누사두아 발리컬렉션"],
    },
    "울루와뚜": {
        "primary": ["울루와뚜 맛집", "울루와뚜 사원", "울루와뚜 서핑", "울루와뚜 비치클럽", "울루와뚜 숙소"],
        "secondary": ["울루와뚜 케착춤", "울루와뚜 선셋", "울루와뚜 카페", "울루와뚜 자유여행", "울루와뚜 절벽"],
        "longtail": ["울루와뚜 사원 케착춤 시간 2026", "울루와뚜 싱글핀 비치클럽", "울루와뚜 록바 선셋", "울루와뚜 서핑 포인트", "울루와뚜 절벽 맛집"],
    },
    "짠디다사": {
        "primary": ["짠디다사 맛집", "짠디다사 해변", "짠디다사 숙소", "짠디다사 다이빙", "짠디다사 여행"],
        "secondary": ["짠디다사 스노클링", "짠디다사 카페", "짠디다사 자유여행", "짠디다사 베사키사원", "짠디다사 티르타강가"],
        "longtail": ["짠디다사 다이빙 포인트 2026", "짠디다사 조용한 해변", "짠디다사 가성비 숙소", "짠디다사 동부 발리 코스", "짠디다사 아메드 비치"],
    },
    "로비나": {
        "primary": ["로비나 맛집", "로비나 돌고래", "로비나 해변", "로비나 숙소", "로비나 온천"],
        "secondary": ["로비나 돌고래투어", "로비나 카페", "로비나 자유여행", "로비나 폭포", "로비나 스노클링"],
        "longtail": ["로비나 돌고래투어 가격 2026", "로비나 반자르 온천", "로비나 기트기트 폭포", "로비나 가성비 숙소", "로비나 북부 발리 코스"],
    },
    "킨타마니": {
        "primary": ["킨타마니 맛집", "킨타마니 화산", "킨타마니 일출", "킨타마니 트레킹", "킨타마니 숙소"],
        "secondary": ["킨타마니 바투르 화산", "킨타마니 카페", "킨타마니 자유여행", "킨타마니 뷔페", "킨타마니 호수"],
        "longtail": ["킨타마니 바투르 일출 트레킹 2026", "킨타마니 화산 등반 가격", "킨타마니 뷔페 추천", "킨타마니 가는법", "킨타마니 1일 투어"],
    },
    "타나롯": {
        "primary": ["타나롯 맛집", "타나롯 사원", "타나롯 일몰", "타나롯 숙소", "타나롯 여행"],
        "secondary": ["타나롯 선셋", "타나롯 카페", "타나롯 자유여행", "타나롯 입장료", "타나롯 포토스팟"],
        "longtail": ["타나롯 사원 일몰 시간 2026", "타나롯 가는법 입장료", "타나롯 근처 맛집", "타나롯 포토스팟 추천", "타나롯 반일 투어"],
    },
    "베두굴": {
        "primary": ["베두굴 맛집", "베두굴 사원", "베두굴 호수", "베두굴 숙소", "베두굴 식물원"],
        "secondary": ["베두굴 울룬다누사원", "베두굴 카페", "베두굴 자유여행", "베두굴 딸기농장", "베두굴 시장"],
        "longtail": ["베두굴 울룬다누 사원 2026", "베두굴 브라탄 호수", "베두굴 식물원 가는법", "베두굴 시장 쇼핑", "베두굴 고원 여행 코스"],
    },
}

# 카테고리별 대표 키워드
CATEGORY_KEYWORDS = {
    "food": ["맛집", "음식", "카페", "맛집 추천", "美食"],
    "culture": ["사원", "문화", "공연", "역사", "전통"],
    "beach": ["해변", "서핑", "비치클럽", "수영", "선셋"],
    "nature": ["자연", "폭포", "트레킹", "화산", "라이스테라스"],
    "shopping": ["쇼핑", "마사지", "스파", "기념품", "시장"],
    "transport": ["교통", "이동", "그랩", "스쿠터", "공항"],
}

# 카테고리별 한국어 이름
CAT_NAMES = {
    "food": "맛집",
    "culture": "사원/문화",
    "beach": "해변/서핑",
    "nature": "자연/모험",
    "shopping": "쇼핑/마사지",
    "transport": "교통/이동",
}


def generate_seo_title_v2(area: str, category: str, page_idx: int) -> str:
    """
    50+ 변형에서 고유한 SEO 제목 생성.
    해시값을 절대 포함하지 않음 (버그 수정).
    page_idx (0~13)에 따라 7가지 유형을 순환하며 선택.
    """
    # 유형 선택: 7가지를 순환
    group_idx = page_idx % len(ALL_TEMPLATE_GROUPS)
    templates = ALL_TEMPLATE_GROUPS[group_idx]
    # 그룹 내에서 지역+카테고리 조합으로 다른 템플릿 선택
    seed = hash(f"{area}_{category}_{page_idx}_title_v2")
    rng = random.Random(seed)
    template = templates[page_idx % len(templates)]

    kws = SEO_KEYWORDS.get(area, SEO_KEYWORDS["우붓"])
    cat_kw = CATEGORY_KEYWORDS.get(category, ["여행"])
    cat_name = CAT_NAMES.get(category, "여행")

    # 카테고리 키워드를 우선 사용 (제목-카테고리 일치 보장)
    if group_idx == 0:  # Guide
        kw = rng.choice([cat_name] + cat_kw[:2])
    elif group_idx == 1:  # List
        kw = rng.choice([cat_name] + cat_kw[:3])
    elif group_idx == 2:  # Review
        kw = rng.choice([cat_name] + cat_kw[:2])
    elif group_idx == 3:  # Comparison
        kw = rng.choice([cat_name] + cat_kw[:2])
    elif group_idx == 4:  # Tip
        kw = rng.choice(cat_kw[:3] + kws["longtail"][:2])
    elif group_idx == 5:  # Season
        kw = rng.choice([cat_name] + cat_kw[:2])
    else:  # Experience
        kw = rng.choice(cat_kw + [cat_name])

    # area가 이미 키워드에 포함되어 있으면 중복 제거
    if kw.startswith(area + " "):
        kw = kw[len(area) + 1:]

    title = template.format(
        area=area,
        cat=kw,
        cat_name=cat_name,
        N=rng.choice([3, 5, 7, 10]),
        year=YEAR,
        month=rng.choice(["1", "3", "5", "7", "9", "11"]),
        season=rng.choice(["건기", "우기", "봄", "여름"]),
        days=rng.choice(["1", "2", "3"]),
        days2=rng.choice(["2", "3", "4"]),
    )

    # 중복 공백 정리
    while "  " in title:
        title = title.replace("  ", " ")

    return title.strip()


def generate_meta_desc_v2(area: str, category: str, page_idx: int, data: dict = None) -> str:
    """고유 메타 설명 생성 (150자 이내)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_meta_v2"))
    cat_name = CAT_NAMES.get(category, "여행")

    spots = (data or {}).get("spots", [])
    food = (data or {}).get("food", [])
    hidden = (data or {}).get("hidden_gem", "")

    highlights = []
    if spots:
        highlights.append(f"{spots[0]} 추천")
    if food:
        highlights.append(f"{food[0].get('name', '')} 후기")
    if hidden:
        highlights.append("숨은 명소 공개")
    highlights.extend(["가격 비교", "실전 팁", "비용 절약"])

    h1 = rng.choice(highlights[:4])
    h2 = rng.choice(highlights[2:6])

    templates = [
        f"{area} {cat_name} 여행 정보. {h1}. {h2}. {YEAR}년 기준 최신 후기.",
        f"{area} {cat_name} 추천 가이드. {h1}, {h2}까지. 가격 비교와 실전 팁.",
        f"{area} 자유여행 {cat_name} 완벽 정리. {h1}. {YEAR}년 실제 후기 기반.",
        f"{area} {cat_name} — {h1}부터 {h2}까지. 현지인이 추천하는 진짜 정보.",
        f"{YEAR}년 {area} {cat_name} 최신 가이드. {h1}, {h2}. 비용 절약 팁 포함.",
        f"{area} 여행 {cat_name} 정보. {h1} 추천. {h2} 가격 비교.",
        f"{area} {cat_name} 베스트 추천. {h1}과 {h2} 비교. {YEAR} 최신.",
        f"{area} {cat_name} 완벽 가이드. {h1}, {h2}. 숨은 명소까지 공개.",
    ]

    desc = templates[page_idx % len(templates)]
    # 150자 제한
    if len(desc) > 150:
        desc = desc[:147] + "..."
    return desc


def generate_keywords_v2(area: str, category: str) -> str:
    """SEO 키워드 메타태그"""
    kws = SEO_KEYWORDS.get(area, SEO_KEYWORDS["우붓"])
    cat_name = CAT_NAMES.get(category, "여행")
    all_kws = kws["primary"][:3] + kws["secondary"][:2] + [area, "발리", "인도네시아", cat_name, "자유여행", f"{YEAR}"]
    return ", ".join(all_kws)


if __name__ == "__main__":
    print("=== SEO Title v2 Demo ===\n")
    areas = ["우붓", "타나롯", "꾸따"]
    cats = ["food", "culture", "beach"]
    for area in areas:
        for cat in cats:
            print(f"[{area}/{cat}]")
            for i in range(14):
                t = generate_seo_title_v2(area, cat, i)
                print(f"  p{i+1:02d}: {t}")
            print()
