#!/usr/bin/env python3
"""
SEO 최적화 제목 생성기 v2
- 네이버/구글 트렌드 키워드 기반
- 카테고리별 고유 제목 템플릿
- 지역별 검색 의도 반영
- 클릭률(CTR) 최적화
"""

import random, hashlib
from datetime import datetime

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

TITLE_TEMPLATES = {
    "food": [
        "{area} {keyword} TOP{num} — 현지인이 추천하는 진짜 맛집 ({year})",
        "{area} {keyword} 완벽 가이드 — 가격·위치·팁 총정리",
        "{area} {keyword} 추천 — 10년차 블로거가 다녀온 후기",
        "{area} {keyword} 순위 — {year} 최신 가격 비교",
        "{area} 자유여행 {keyword} — 놓치면 후회하는 맛집 리스트",
        "{area} {keyword} 추천 — 가성비 vs 분위기 비교 ({year})",
        "{area} 여행 필수 {keyword} — 현지인만 아는 숨은 맛집",
        "{area} {keyword} 가이드 — 위치·가격·예약 tip 총정리",
        "{area} {keyword} 베스트 — {year} 실제 후기 기반",
        "{area} {keyword} 총정리 — 로컬 vs 관광지 비교",
        "{area} {keyword} 추천 리스트 — 예산별 BEST ({year})",
        "{area} {keyword} 탐방기 — 직접 가본 솔직 리뷰",
        "{area} {keyword} 맛있는 코스 — 하루 3끼 추천 ({year})",
        "{area} {keyword} 숨은 명소 — 현지인만 아는 곳",
    ],
    "culture": [
        "{area} {keyword} 완벽 가이드 — 입장료·팁·포토스팟 ({year})",
        "{area} {keyword} 추천 — 반드시 가봐야 할 곳 TOP{num}",
        "{area} {keyword} 투어 — 실제 경험 기준 후기",
        "{area} 자유여행 {keyword} — 시간·비용 절약 팁",
        "{area} {keyword} 가이드 — 복장 규정·사진 명소 총정리",
        "{area} {keyword} 추천 — {year} 최신 입장료 비교",
        "{area} 여행 {keyword} — 현지 가이드가 알려주는 비법",
        "{area} {keyword} 코스 — 반일/1일 일정 추천 ({year})",
        "{area} {keyword} 역사 이야기 — 문화적 배경까지 이해",
        "{area} {keyword} 포토스팟 — 인생샷 찍는 법 ({year})",
        "{area} {keyword} 방문 팁 — 현지인이 알려주는 꿀팁",
        "{area} {keyword} 코스 추천 — 가족/커플별 BEST ({year})",
        "{area} {keyword} 체험 가이드 — 예약부터 완벽 정리",
        "{area} {keyword} 숨은 이야기 — 모르면 손해인 정보",
    ],
    "beach": [
        "{area} {keyword} 완벽 가이드 — 서핑·수영·선셋 ({year})",
        "{area} {keyword} 추천 — 물놀이하기 좋은 곳 TOP{num}",
        "{area} {keyword} 후기 — 실제 다녀온 솔직 리뷰",
        "{area} 자유여행 {keyword} — 파도·안전·장비 tip",
        "{area} {keyword} 가이드 — 가는법·주차·탈의실 정보",
        "{area} {keyword} 추천 — 인생샷 포토스팟 ({year})",
        "{area} 여행 {keyword} — 선셋 타임 BEST 명소",
        "{area} {keyword} 코스 — 해변 따라 1일 여행 ({year})",
        "{area} {keyword} 서핑 가이드 — 초보자도 즐기는 법",
        "{area} {keyword} 안전 수칙 — 물놀이 전 체크리스트 ({year})",
        "{area} {keyword} 비치클럽 — 선셋 명소 추천",
        "{area} {keyword} 수영 명소 — 가족-friendly ({year})",
        "{area} {keyword} 스노클링 포인트 — 물고기 관찰 명소",
        "{area} {keyword} 해변 산책로 — 걸어다니기 좋은 코스 ({year})",
    ],
    "nature": [
        "{area} {keyword} 완벽 가이드 — 코스·난이도·비용 ({year})",
        "{area} {keyword} 추천 — 자연 만끽하는 BEST 코스 TOP{num}",
        "{area} {keyword} 후기 — 실제 트레킹/투어 리뷰",
        "{area} 자유여행 {keyword} — 준비물·안전 수칙 총정리",
        "{area} {keyword} 가이드 — 소요시간·Difficulty·팁",
        "{area} {keyword} 추천 — {year} 입장료 비교",
        "{area} 여행 {keyword} — 새벽/오전 타임 추천",
        "{area} {keyword} 코스 — 가족/커플/혼자 여행별 추천 ({year})",
        "{area} {keyword} 트레킹 가이드 — 준비물부터 난이도까지",
        "{area} {keyword} 포토스팟 — 사진 잘 찍는 법 ({year})",
        "{area} {keyword} 안전 가이드 — 주의사항 총정리",
        "{area} {keyword} 숨은 코스 — 관광객 모르는 명소 ({year})",
        "{area} {keyword} 가족 여행 — 아이와 함께하기 좋은 코스",
        "{area} {keyword} 1일 코스 — 효율적인 동선 추천 ({year})",
    ],
    "shopping": [
        "{area} {keyword} 완벽 가이드 — 가격·흥정·추천 ({year})",
        "{area} {keyword} 추천 — 꼭 사야 할 BEST 아이템 TOP{num}",
        "{area} {keyword} 후기 — 실제 이용/구매 리뷰",
        "{area} 자유여행 {keyword} — 시간·비용 절약 팁",
        "{area} {keyword} 가이드 — 영업시간·위치·가격 비교",
        "{area} {keyword} 추천 — {year} 최신 가격 정보",
        "{area} 여행 {keyword} — 현지인 추천 BEST 숍",
        "{area} {keyword} 코스 — 쇼핑+마사지 1일 코스 ({year})",
        "{area} {keyword} 흥정 팁 — 현지인처럼 사는 법",
        "{area} {keyword} 가성비 추천 — 예산별 BEST ({year})",
        "{area} {keyword} 마사지 추천 — 진짜 좋은 곳만 골라",
        "{area} {keyword} 기념품 리스트 — 꼭 사가야 할 것들 ({year})",
        "{area} {keyword} 시장 가이드 — 로컬 시장 탐방기",
        "{area} {keyword} 스파 추천 — 힐링 코스 총정리 ({year})",
    ],
    "transport": [
        "{area} {keyword} 완벽 가이드 — 비용·시간·tip ({year})",
        "{area} {keyword} 추천 — 가장 저렴하고 편한 방법 TOP{num}",
        "{area} {keyword} 후기 — 실제 이동 경험 리뷰",
        "{area} 자유여행 {keyword} — 그랩 vs 스쿠터 vs 렌트 비교",
        "{area} {keyword} 가이드 — 공항에서 {area} 최저가 방법",
        "{area} {keyword} 추천 — {year} 최신 가격 비교",
        "{area} 여행 {keyword} — 초보자도 쉽게 따라하는 법",
        "{area} {keyword} 코스 — {area} 내 이동 BEST 경로 ({year})",
        "{area} {keyword} 절약 팁 — 교통비 50% 줄이는 법",
        "{area} {keyword} 안전 가이드 — 스쿠터/차량 이용 시 주의 ({year})",
        "{area} {keyword} 공항 이동 — 택시 vs 그랩 vs 셔틀 비교",
        "{area} {keyword} 코스 추천 — 효율적인 동선 ({year})",
        "{area} {keyword} 초보 가이드 — 처음 가는 사람을 위한 팁",
        "{area} {keyword} 예약 가이드 — 사전 예약 vs 현장 ({year})",
    ],
}

def generate_seo_title(area, category, index):
    """SEO 최적화 제목 생성"""
    keywords = SEO_KEYWORDS.get(area, SEO_KEYWORDS["우붓"])
    templates = TITLE_TEMPLATES.get(category, TITLE_TEMPLATES["food"])

    if index % 3 == 0:
        kw_pool = keywords["primary"]
    elif index % 3 == 1:
        kw_pool = keywords["secondary"]
    else:
        kw_pool = keywords["longtail"]

    keyword = kw_pool[index % len(kw_pool)]

    if keyword.startswith(area + " "):
        keyword = keyword[len(area) + 1:]

    template = templates[index % len(templates)]
    year = datetime.now().year

    title = template.format(
        area=area,
        keyword=keyword,
        num=random.choice([3, 5, 7, 10]),
        year=year,
    )
    # 중복 방지: area+category+index 조합으로 완전 고유 ID 생성
    unique_id = hashlib.md5(f"{area}_{category}_{index}".encode()).hexdigest()[:4]
    title = title.rstrip(")")
    if title.endswith("("):
        title = title[:-1].rstrip()
    title = title + f" ({unique_id})"
    return title

def generate_meta_description(area, category, index):
    """SEO 메타 설명 생성"""
    keywords = SEO_KEYWORDS.get(area, SEO_KEYWORDS["우붓"])
    keyword = keywords["primary"][index % len(keywords["primary"])]

    templates = [
        f"{area} {keyword} 추천! 실제 가격 비교와 할인쿠폰까지. {datetime.now().year}년 최신 정보. 마이리얼트립 할인쿠폰으로 추가 절약하세요.",
        f"{area} 자유여행 필수 {keyword} 가이드. 현지인이 추천하는 진짜 맛집·명소·숙소 총정리. {datetime.now().year}년 기준.",
        f"{area} {keyword} 완벽 가이드 — 가격·위치·팁까지 한 번에. 10년차 블로거의 솔직 후기. 할인쿠폰 포함.",
        f"{area} 여행 {keyword} 추천 TOP. 가성비부터 프리미엄까지 비교. {datetime.now().year}년 최신 가격 정보.",
    ]
    return templates[index % len(templates)]

def generate_keywords(area, category):
    """SEO 키워드 메타태그 생성"""
    kws = SEO_KEYWORDS.get(area, SEO_KEYWORDS["우붓"])
    all_kws = (
        kws["primary"][:3] +
        kws["secondary"][:2] +
        [area, "발리", "인도네시아", "여행", "자유여행", "가격비교"]
    )
    return ", ".join(all_kws)

if __name__ == "__main__":
    for area in list(SEO_KEYWORDS.keys())[:3]:
        for cat in ["food", "culture", "beach"]:
            title = generate_seo_title(area, cat, 0)
            desc = generate_meta_description(area, cat, 0)
            kws = generate_keywords(area, cat)
            print(f"\n[{area}/{cat}]")
            print(f"  제목: {title}")
            print(f"  설명: {desc[:80]}...")
            print(f"  키워드: {kws[:60]}...")
