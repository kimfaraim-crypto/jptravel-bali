#!/usr/bin/env python3
"""
발리 여행 블로그 v8 대개선 스크립트
- 한국어 조사 자동 처리 (을/를, 은/는, 이/가, 와/과)
- 반복 구문 제거 및 다양화
- 이미지 ALT 구체화
- Figcaption 구체화
- 도입부 패턴 다양화 (20개+)
- robots.txt, sitemap.xml 생성
- 경험 중심 콘텐츠 전환
"""

import os, re, json, hashlib, random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
HTML_DIR = BASE_DIR / "output" / "html" / "bali"
YEAR = datetime.now().year

# ============================================================
# 한국어 조사 처리
# ============================================================

def has_batchim(word):
    """한국어 단어의 마지막 글자에 받침이 있는지 확인"""
    if not word:
        return False
    last_char = word[-1]
    code = ord(last_char) - 0xAC00
    if 0 <= code <= 0x278C:  # 한글 유니코드 범위
        return (code % 28) != 0
    return False

def josa(word, pair):
    """
    pair: (받침 있을 때, 받침 없을 때)
    예: josa("우붓", ("을", "를")) → "를"
    """
    if not word:
        return pair[1]
    return pair[0] if has_batchim(word) else pair[1]

def fix_josa(text, area=""):
    """텍스트 내 미처리 조사를 자동 수정"""
    # 을/를
    text = re.sub(r'을\(를\)', lambda m: josa(area, ("을", "를")) if area else "를", text)
    text = re.sub(r'\(를\)', lambda m: josa(area, ("을", "를")) if area else "를", text)
    # 은/는
    text = re.sub(r'은\(는\)', lambda m: josa(area, ("은", "는")) if area else "는", text)
    text = re.sub(r'\(는\)', lambda m: josa(area, ("은", "는")) if area else "는", text)
    # 이/가
    text = re.sub(r'이\(가\)', lambda m: josa(area, ("이", "가")) if area else "가", text)
    text = re.sub(r'\(가\)', lambda m: josa(area, ("이", "가")) if area else "가", text)
    # 와/과
    text = re.sub(r'와\(과\)', lambda m: josa(area, ("과", "와")) if area else "와", text)
    text = re.sub(r'\(과\)', lambda m: josa(area, ("과", "와")) if area else "와", text)
    # 으로/로
    text = re.sub(r'으로\(로\)', lambda m: josa(area, ("으로", "로")) if area else "로", text)
    text = re.sub(r'\(로\)', lambda m: josa(area, ("으로", "로")) if area else "로", text)
    # 아/야
    text = re.sub(r'아\(야\)', lambda m: josa(area, ("아", "야")) if area else "야", text)
    text = re.sub(r'\(야\)', lambda m: josa(area, ("아", "야")) if area else "야", text)
    # 이/ — (명사+이/가 생략 패턴)
    text = re.sub(r'는\(은\)', lambda m: josa(area, ("은", "는")) if area else "는", text)
    # 남아있는 패턴도 정리
    text = re.sub(r'을/를', lambda m: josa(area, ("을", "를")) if area else "를", text)
    text = re.sub(r'은/는', lambda m: josa(area, ("은", "는")) if area else "는", text)
    text = re.sub(r'이/가', lambda m: josa(area, ("이", "가")) if area else "가", text)
    return text

def fix_josa_in_html(html, area):
    """HTML 전체에서 조사 미처리 패턴 수정"""
    return fix_josa(html, area)

# ============================================================
# 이미지 ALT/Figcaption 구체화
# ============================================================

AREA_IMAGE_CONTEXT = {
    "우붓": {
        "food": [
            "우붓 와룽에서 나시고렝을 기다리는 모습",
            "베벵길 오리구이 크리스피덕 세트",
            "우붓 아트 마켓 근처 로컬 음식 노점",
            "클리어 카페 강변 뷰 스무디볼",
            "우붓 전통 발리 요리 와룽 내부",
            "우붓 비건 카페 브런치 메뉴",
            "우붓 로컬 시장 열대 과일 가게",
            "우붓 레스토랑 발리니스 정식 코스",
            "우붓 카페 인테리어 소품과 식물",
            "우붓 디저트 카페 케이크 진열대",
        ],
        "culture": [
            "타만 사라스와티 사원 연못 위 건축물",
            "우붓 원숭이 숲 입구 조각상",
            "우붓 왕궁 전통 공연 케착춤 장면",
            "아궁 라이 미술관 발리 전통 회화",
            "우붓 사원 힌두교 의식 중인 현지인",
            "우붓 거리 발리 전통 장식품",
            "우붓 왕궁 야간 공연 무대 조명",
            "우붓 사원 석조 조각 디테일",
            "우붓 미술관 내부 전시 공간",
            "우붓 전통 공예품 제작 시연",
        ],
        "beach": [
            "아융강 래프팅 보트를 타고 협곡 통과",
            "우붓 근처 천연 수영장 폭포 풍경",
            "우붓 강변 카약 체험 장면",
            "우붓 외곽 계곡 절벽 풍경",
            "우붓 리조트 수영장 라운지",
            "우붓 근처 온천 풍경",
            "우붓 강변 레스토랑 야경",
            "우붓 자연 수영장 주변 열대 식물",
            "우붓 외곽 강변 산책로",
            "우붓 근처 폭포 입구 계단",
        ],
        "nature": [
            "테갈랑 라이스 테라스 안개 낀 아침 풍경",
            "알링킹 폭포 아래 천연 수영장",
            "뜨갈라랑 스윙에서 내려다본 계곡",
            "캄포한 리지 절벽 위 산책로",
            "우붓 논밭 사이 작은 사원",
            "우붓 열대 우림 트레킹 코스",
            "우붓 근처 화산 일출 풍경",
            "우붓 강변 일몰 골든아워",
            "우붓 외곽 코코넛 농장 풍경",
            "우붓 자연 보호구역 원숭이 서식지",
        ],
        "shopping": [
            "우붓 아트 마켓 기념품 진열대",
            "우붓 은세공 공방 장인 작업 모습",
            "우붓 라탄 가방 숍 입구",
            "우붓 마사지숍 내부 침대와 오일",
            "우붓 아트 마켓 흥정하는 관광객",
            "우붓 기념품 가게 발리 직물 사롱",
            "우붓 몽키 포레스트 로드 부티크숍",
            "우붓 전통 직물 염색 시연",
            "우붓 시장 열대 향신료 가게",
            "우붓 카페 거리 야경 쇼핑 풍경",
        ],
        "transport": [
            "공항에서 우붓 가는 길 풍경",
            "우붓 스쿠터 렌트 숍 입구",
            "우붓 그랩 택시 호출 화면",
            "우붓 도로 교통체증 풍경",
            "우붓 시내 도보 이동 관광객",
            "우붓 호텔 셔틀 차량",
            "우붓 근처 도로 논밭 풍경",
            "우붓 시내 교차로 풍경",
            "우붓 주차장 스쿠터 줄",
            "우붓 드라이버와 함께하는 투어",
        ],
    },
    "스미냑": {
        "food": [
            "포테이토 헤드 비치클럽 선셋 칵테일",
            "스미냑 해변 이탈리안 레스토랑 파스타",
            "와룽니아 로컬 음식 나시캄푸르",
            "시스터필즈 카페 브런치 에그베네딕트",
            "모텔 멕시콜라 바 타코와 마가리타",
            "스미냑 비치클럽 선베드 음료",
            "스미냑 로컬 와룽 내부 풍경",
            "스미냑 카페 라떼 아트",
            "스미냑 레스토랑 해산물 플래터",
            "스미냑 야시장 음식 노점",
        ],
        "culture": [
            "페티탕겟 해변 사원 일몰 풍경",
            "스미냑 빌리지 전통 마을 입구",
            "스미냑 사원 입구 조각상",
            "스미냑 거리 발리 전통 장식",
            "스미냑 비치 근처 소규모 사원",
            "스미냑 예술가 공방 내부",
            "스미냑 전통 춤 공연 모습",
            "스미냑 사원 제단 꽃 장식",
            "스미냑 마을 주민 일상 풍경",
            "스미냑 사원 야경 조명",
        ],
        "beach": [
            "더블식스 비치 선셋 포토스팟",
            "스미냑 비치 서핑 강습 장면",
            "쿠데타 비치클럽 선베드 풍경",
            "스미냑 해변 산책로 조깅하는 사람들",
            "스미냑 비치 일몰 실루엣 사진",
            "스미냑 해변 카페 야외 좌석",
            "스미냑 비치 서핑 보드 대여점",
            "스미냑 해변 모래사장 아침 풍경",
            "스미냑 비치클럽 풀 파티",
            "스미냑 해변 야자수 일몰",
        ],
        "nature": [
            "스미냑 해변 산책로 아침 산책",
            "스미냑 비치 일출 풍경",
            "스미냑 해변 야자수 열대 식물",
            "스미냑 근처 논밭 풍경",
            "스미냑 해변 조류 관찰",
            "스미냑 비치 파도 소리 풍경",
            "스미냑 해변 일몰 구름 색채",
            "스미냑 열대 정원 리조트",
            "스미냑 해변 모래사장 발자국",
            "스미냑 비치 아침 안개",
        ],
        "shopping": [
            "스미냑 빌리지 부티크숍 내부",
            "스미냑 디자이너숍 의류 진열",
            "스미냑 스파 내부 마사지 침대",
            "스미냑 세일 시즌 쇼핑백",
            "스미냑 기념품숍 라탄 가방",
            "스미냑 패션숍 거울과 조명",
            "스미냑 스파 오일과 타월",
            "스미냑 쇼핑몰 입구 간판",
            "스미냑 기념품 가게 발리 직물",
            "스미냑 부티크숍 주얼리 진열",
        ],
        "transport": [
            "공항에서 스미냑 가는 그랩 택시",
            "스미냑 스쿠터 렌트 숍",
            "스미냑 도로 교통체증 풍경",
            "스미냑 해변 도보 이동",
            "스미냑 골목 스쿠터 주차",
            "스미냑 호텔 셔틀 차량",
            "스미냑 시내 교차로 풍경",
            "스미냑 비치 근처 주차장",
            "스미냑 드라이버 투어",
            "스미냑 골목 도보 산책",
        ],
    },
    "꾸따": {
        "food": [
            "꾸따 와룽무라 나시고реги 한 상",
            "마데스 와룽 1969년부터 내려오는 맛집",
            "하드락 카페 발리 버거와 맥주",
            "팝피스 레스토랑 정원 테이블",
            "대나무 코너 로컬 음식점",
            "꾸따 비치워크 푸드코트",
            "꾸따 해변 음식 노점",
            "꾸따 로컬 와룽 내부 풍경",
            "꾸따 카페 아메리카노",
            "꾸따 해산물 레스토랑",
        ],
        "culture": [
            "꾸따 아트 마켓 기념품 진열",
            "워터밤 파크 워터슬라이드",
            "꾸따 사원 건축 양식",
            "꾸따 전통 공예품 가게",
            "꾸따 문화 체험 활동",
            "꾸따 힌두교 의식 장면",
            "꾸따 사원 조각상 디테일",
            "꾸따 미술관 전시 공간",
            "꾸따 전통 공연 모습",
            "꾸따 예술 공방 내부",
        ],
        "beach": [
            "꾸따 비치 서핑 강습 장면",
            "꾸따 해변 일몰 서퍼 실루엣",
            "레기안 비치 한적한 아침 풍경",
            "꾸따 비치 서핑 보드 대여",
            "꾸따 해변 산책로 조깅",
            "꾸따 비치 파도 치는 모습",
            "꾸따 해변 야자수 풍경",
            "꾸따 비치 일몰 골든아워",
            "꾸따 해변 모래사장 놀이",
            "꾸따 비치 서핑 대회 장면",
        ],
        "nature": [
            "레기안 비치 아침 산책로",
            "꾸따 해변 일출 풍경",
            "꾸따 근처 열대 정원",
            "꾸따 해변 조류 관찰",
            "꾸따 비치 파도 소리 풍경",
            "꾸따 해변 일몰 구름",
            "꾸따 열대 식물원",
            "꾸따 해변 모래사장",
            "꾸따 비치 아침 안개",
            "꾸따 근처 논밭 풍경",
        ],
        "shopping": [
            "비치워크 쇼핑몰 외관",
            "디스커버리 몰 내부 풍경",
            "꾸따 마사지숍 입구",
            "꾸따 기념품 가게",
            "꾸따 아트 마켓 흥정",
            "꾸따 쇼핑몰 푸드코트",
            "꾸따 마사지 침대와 오일",
            "꾸따 기념품 진열대",
            "꾸따 시장 열대 과일",
            "꾸따 쇼핑몰 브랜드숍",
        ],
        "transport": [
            "공항에서 꾸따 가는 길",
            "꾸따 도보 이동 관광객",
            "꾸따 스쿠터 렌트",
            "꾸따 그랩 택시",
            "꾸따 도로 풍경",
            "꾸따 주차장",
            "꾸따 시내 교차로",
            "꾸따 해변 가는 길",
            "꾸따 골목 산책",
            "꾸따 호텔 셔틀",
        ],
    },
}

# 공통 fallback ALT 패턴
def get_specific_alt(area, category, idx):
    """지역+카테고리+인덱스별 구체적 ALT 텍스트 생성"""
    context = AREA_IMAGE_CONTEXT.get(area, {}).get(category, [])
    if context and idx < len(context):
        return context[idx]
    # fallback: 구체적 패턴 생성
    cat_names = {
        "food": ["현지 음식", "맛집 내부", "전통 요리", "카페 분위기", "로컬 음식점"],
        "culture": ["사원 건축물", "전통 공연", "문화 체험", "역사 유적", "종교 의식"],
        "beach": ["해변 풍경", "서핑 장면", "일몰 포인트", "비치클럽", "수상 스포츠"],
        "nature": ["자연 경관", "폭포 풍경", "트레킹 코스", "열대 식물", "전망대 뷰"],
        "shopping": ["쇼핑몰 내부", "기념품 가게", "마사지숍", "시장 풍경", "부티크숍"],
        "transport": ["이동 수단", "도로 풍경", "공항 풍경", "교통 수단", "이동 경로"],
    }
    cats = cat_names.get(category, cat_names["food"])
    return f"{area} {cats[idx % len(cats)]}"

# ============================================================
# 도입부 패턴 다양화 (20개+)
# ============================================================

INTRO_TEMPLATES = [
    # 1. 경험담 스타일
    "{area}에서 {cat_desc} 즐기고 왔어요. {tip}. 솔직하게 장단점 다 정리할게요.",
    # 2. 질문형
    "'{area} {cat_name} 어디가 좋나요?' 저도 같은 고민했거든요. {tip}. 자세히 알려드릴게요.",
    # 3. 결론先行
    "결론부터 말하면, {area}의 {cat_name}은 {best_season}이 가장 좋아요. {tip}.",
    # 4. 비교형
    "{area} {cat_name}, 직접 가보니 생각이 좀 달랐어요. {tip}. 후기 시작합니다.",
    # 5. 추천형
    "{area} 여행 계획 중이신가요? {cat_name}은 꼭 넣으세요. {tip}.",
    # 6. 시간순 스토리
    "지난 {month}월에 {area}에 다녀왔어요. {cat_name} 위주로 돌아봤는데, {tip}.",
    # 7. 비용 중심
    "{area} {cat_name} 예산이 궁금하셨죠? {tip}. 가격 비교표도 준비했어요.",
    # 8. 실용 가이드
    "{area} {cat_name} 정보를 모아봤어요. {tip}. 아래에서 확인하세요.",
    # 9. 감성형
    "{area}의 {cat_name}, 사진으로만 보다가 직접 가니까 정말 달랐어요. {tip}.",
    # 10. 리스트형
    "{area} {cat_name} 핵심만 정리하면: ①{spot1} ②{spot2} ③{tip_short}.",
    # 11. 현지인 관점
    "발리 현지인 친구가 추천한 {area} {cat_name} 코스예요. {tip}.",
    # 12. 재방문 후기
    "{area}에 {visit_count}번째 방문이에요. 이번에 새로 알게 된 {cat_name} 정보를 공유해요. {tip}.",
    # 13. 시즌 추천
    "{area} {cat_name}은 {best_season}에 가면 가장 좋아요. {tip}.",
    # 14. 하루 코스
    "{area}에서 {cat_name} 하루 코스를 짜봤어요. {tip}. 일정표도 아래에 있어요.",
    # 15. 가성비형
    "예산형으로 {area} {cat_name} 즐기는 법을 알려드릴게요. {tip}.",
    # 16. 포토 가이드
    "{area} {cat_name} 포토스팟을 정리했어요. {tip}. 인생샷 건지세요!",
    # 17. 팁 공유형
    "10년간 발리 다니면서 알게 된 {area} {cat_name} 꿀팁이에요. {tip}.",
    # 18. 문제 해결형
    "{area} {cat_name} 어디서부터 시작해야 할지 모르겠다면? {tip}. 이 글 하나면 돼요.",
    # 19. 감성+실용
    "{area}에서 보낸 시간 중 가장 좋았던 {cat_name} 순간을 정리했어요. {tip}.",
    # 20. 비교 분석형
    "{area} {cat_name} 여러 곳을 비교해봤어요. {tip}. 최종 추천은 아래에서.",
]

def generate_diverse_intro(area, category, page_idx, data):
    """다양한 도입부 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_intro_v8"))

    cat_info = {
        "food": {"name": "맛집", "desc": "맛집 탐방"},
        "culture": {"name": "사원/문화", "desc": "문화 체험"},
        "beach": {"name": "해변/서핑", "desc": "해변 액티비티"},
        "nature": {"name": "자연/모험", "desc": "자연 탐방"},
        "shopping": {"name": "쇼핑/마사지", "desc": "쇼핑 & 힐링"},
        "transport": {"name": "교통/이동", "desc": "이동 정보"},
    }.get(category, {"name": "여행", "desc": "여행"})

    spots = data.get("spots", [])
    food = data.get("food", [])
    hidden = data.get("hidden_gem", "")
    best_season = data.get("best_season", "4~10월")

    spot1 = spots[0] if spots else "주요 명소"
    spot2 = spots[1] if len(spots) > 1 else "숨은 명소"
    first_food = food[0].get("name", "현지 맛집") if food else "현지 맛집"

    tips_pool = [
        f"{spot1}부터 시작하면 동선이 좋아요",
        f"{first_food}에서 식사 추천이에요",
        f"숨은 명소({hidden})도 놓치지 마세요" if hidden else f"{spot2}도 꼭 가보세요",
        f"가격 비교와 실전 팁을 정리했어요",
        f"비용 절약 꿀팁도 포함했어요",
        f"오전에 가면 사람이 적어요",
        f"사진이 정말 잘 나와요",
        f"현지인 추천 코스예요",
    ]

    tip = rng.choice(tips_pool)
    tip_short = tip.split(".")[0] if "." in tip else tip

    template = INTRO_TEMPLATES[page_idx % len(INTRO_TEMPLATES)]
    intro = template.format(
        area=area,
        cat_name=cat_info["name"],
        cat_desc=cat_info["desc"],
        tip=tip,
        tip_short=tip_short,
        spot1=spot1,
        spot2=spot2,
        best_season=best_season,
        month=rng.choice(["3", "4", "5", "7", "8", "9", "10"]),
        visit_count=rng.choice(["2", "3", "5", "7"]),
    )

    # 조사 처리
    intro = fix_josa(intro, area)
    return intro


# ============================================================
# 반복 구문 제거 및 다양화
# ============================================================

def diversify_phrases(text, area, page_idx):
    """반복 구문을 페이지별로 다양하게 변형"""
    rng = random.Random(hash(f"{area}_{page_idx}_phrase_v8"))

    replacements = {
        "10년차 블로거": rng.choice([
            "여행 블로거", "발리 마니아", "여행 작가", "발리 전문가",
            "자유여행 전문가", "발리 가이드", "여행 큐레이터",
        ]),
        "숨은 명소": rng.choice([
            "로컬 스팟", "비밀 장소", "알짜 장소", "숨겨진 보석",
            "관광객 모르는 곳", "현지인 추천 장소", "조용한 명소",
        ]),
        "모든 정보를 정리했어요": rng.choice([
            "핵심만 모았어요", "알짜 정보만 추렸어요", "실전 정보를 정리했어요",
            "필요한 정보를 다 담았어요", "이 글 하나면 충분해요",
            "놓치면 후회할 정보를 모았어요",
        ]),
        "끝까지 읽어보세요": rng.choice([
            "끝까지 읽어보시면 도움이 될 거예요",
            "아래에서 자세히 확인하세요",
            "밑에서 상세히 알려드릴게요",
            "하나씩 살펴볼게요",
            "실전 팁도 있으니 끝까지 읽어보세요",
        ]),
        "솔직 후기입니다": rng.choice([
            "직접 다녀온 후기예요", "현장에서 느낀 그대로예요",
            "가감 없이 정리했어요", "좋은 점만 말하지 않을게요",
            "장단점 솔직하게 썼어요",
        ]),
        "한눈에 정리했습니다": rng.choice([
            "핵심만 추렸어요", "알짜만 모았어요", "한번에 파악할 수 있게 정리했어요",
            "시간 절약해드릴게요", "이 표 하나면 끝이에요",
        ]),
        "필수입니다": rng.choice([
            "꼭 가보세요", "빼놓으면 아쉬워요", "반드시 포함하세요",
            "안 가면 후회해요", "추천드려요",
        ]),
        "추천이에요": rng.choice([
            "추천드려요", "좋아요", "괜찮아요", "만족스러웠어요",
            "가볼 만해요", "值得一 방문이에요",
        ]),
        "2026년 기준": rng.choice([
            f"{YEAR}년 최신", f"{YEAR} 업데이트", f"{YEAR} 방문 기준",
            f"올해({YEAR}) 정보", f"{YEAR} 현재",
        ]),
        "실전 팁": rng.choice([
            "현장 꿀팁", "알짜 팁", "실용 정보", "현지 꿀팁",
            "시간 절약 팁", "비용 절약 팁",
        ]),
        "가격 비교": rng.choice([
            "비용 비교", "가격 정리", "예산 비교", "가격 분석",
            "로컬 vs 투어 가격",
        ]),
        "비용 절약": rng.choice([
            "예산 절약", "돈 아끼는 법", "가성비 UP", "저렴하게 즐기는 법",
            "알뜰 여행 팁",
        ]),
    }

    for old, new in replacements.items():
        # 같은 구문이 반복되면 첫 번째만 변형, 나머지는 다른 변형 적용
        count = text.count(old)
        if count > 0:
            # 확률적으로 변형 (너무 급격한 변경 방지)
            if rng.random() < 0.8:
                text = text.replace(old, new, 1)
                # 나머지는 다른 변형으로
                alts = [v for v in replacements[old].split(", ") if v != new] if isinstance(replacements[old], str) else []
                if not alts:
                    continue
                remaining = count - 1
                for _ in range(remaining):
                    alt = rng.choice(alts) if alts else new
                    text = text.replace(old, alt, 1)

    return text


# ============================================================
# 여행 에피소드 다양화
# ============================================================

EPISODE_TEMPLATES = [
    "{area}에서의 마지막 날, {spot}에서 일몰을 보면서 '아, 다시 오고 싶다'는 생각이 들었어요. {food}에서 먹은 마지막 저녁 식사도 잊을 수 없고요.",
    "비가 갑자기 와서 {spot} 근처 카페에서 2시간을 기다렸는데, 오히려 그 시간이 더 좋았어요. 빗소리 들으며 마신 {area} 커피 맛이 아직도 기억나요.",
    "{area}에서 스쿠터를 빌려서 돌아다녔는데, 길을 잘못 들어서 발견한 숨겨진 해변이 정말 예뻤어요. 여행은 역시 예상치 못한 곳에서 추억이 생기더라고요.",
    "{spot}에서 만난 현지인이 추천해준 맛집이 있었는데, 관광객은 저 하나였어요. {food} 맛이 정말 독특했어요.",
    "{area}에 도착하자마자 비가 쏟아져서 첫날은 호텔에서만 있었는데, 오히려 쉬니까 다음 날부터 더 잘 즐겼어요. 여행도 쉼이 필요해요.",
    "{spot}에서 사진을 찍고 있는데 현지 아이들이 같이 찍자고 다가왔어요. 소통은 영어+몸짓이었는데, 그 미소가 아직도 기억에 남아요.",
    "{area}에서 마지막 밤, 해변에 앉아서 파도 소리를 들었어요. 내일 다시 일상으로 돌아간다고 생각하니 좀 그랬어요.",
    "{food}에서 주문 실수로 다른 메뉴가 나왔는데, 오히려 그게 더 맛있었어요. 여행에서의 실패는 때로는 행운이에요.",
    "{spot} 가는 길이 생각보다 험해서 힘들었는데, 도착해서 보는 풍경에 다 잊혀졌어요. 노력한 만큼 보상받는 느낌이었어요.",
    "{area}에서 혼자 여행했는데, 오히려 혼자여서 더 자유롭게 즐길 수 있었어요. 원하는 곳에서 원하는 시간만큼 있을 수 있다는 게 최고예요.",
]

def generate_episode(area, page_idx, data):
    """다양한 여행 에피소드 생성"""
    rng = random.Random(hash(f"{area}_{page_idx}_episode_v8"))

    spots = data.get("spots", [])
    food_items = data.get("food", [])

    spot = rng.choice(spots) if spots else "해변"
    food = rng.choice([f.get("name", "현지 음식") for f in food_items]) if food_items else "현지 음식"

    template = EPISODE_TEMPLATES[page_idx % len(EPISODE_TEMPLATES)]
    episode = template.format(area=area, spot=spot, food=food)
    return episode


# ============================================================
# 메인 HTML 처리 함수
# ============================================================

def process_html_file(filepath, area, category, page_idx):
    """단일 HTML 파일 처리"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 조사 처리
    html = fix_josa_in_html(html, area)

    # 2. 반복 구문 다양화
    html = diversify_phrases(html, area, page_idx)

    # 3. 이미지 ALT 구체화
    def replace_alt(match):
        idx = int(match.group(1)) if match.group(1) else 0
        specific = get_specific_alt(area, category, idx)
        return f'alt="{specific}"'

    # Replace generic alt texts
    alt_pattern = r'alt="' + re.escape(area) + r'[^"]*사진[^"]*"'
    alt_counter = [0]
    def replace_alt_counter(match):
        idx = alt_counter[0]
        alt_counter[0] += 1
        specific = get_specific_alt(area, category, idx)
        return f'alt="{specific}"'
    html = re.sub(alt_pattern, replace_alt_counter, html)

    # 4. figcaption 구체화
    figcap_pattern = r'<figcaption[^>]*>' + re.escape(area) + r'[^<]*</figcaption>'
    figcap_counter = [0]
    def replace_figcap(match):
        idx = figcap_counter[0]
        figcap_counter[0] += 1
        specific = get_specific_alt(area, category, idx)
        return f'<figcaption style="margin-top:8px;font-size:.85em;color:#666">{specific}</figcaption>'
    html = re.sub(figcap_pattern, replace_figcap, html)

    # 5. 메타 설명 중복 제거 (같은 area+cat 내에서)
    # 이건 별도 패스에서 처리

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return True


# ============================================================
# robots.txt / sitemap.xml 생성
# ============================================================

def generate_robots_txt():
    robots = f"""User-agent: *
Allow: /
Disallow: /output/images_real/

Sitemap: https://balitravel.blog/sitemap.xml

# JP Travel Bali - 발리 여행 블로그
# {YEAR}년 업데이트
"""
    robots_path = BASE_DIR / "output" / "html" / "robots.txt"
    robots_path.write_text(robots)
    print(f"✅ robots.txt 생성: {robots_path}")


def generate_sitemap():
    urls = []
    for area_dir in sorted(HTML_DIR.iterdir()):
        if not area_dir.is_dir():
            continue
        for cat_dir in sorted(area_dir.iterdir()):
            if not cat_dir.is_dir():
                continue
            for html_file in sorted(cat_dir.iterdir()):
                if html_file.suffix == '.html':
                    rel = f"{area_dir.name}/{cat_dir.name}/{html_file.name}"
                    urls.append(f"""<url>
<loc>https://balitravel.blog/{rel}</loc>
<lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
<changefreq>weekly</changefreq>
<priority>0.8</priority>
</url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""

    sitemap_path = BASE_DIR / "output" / "html" / "sitemap.xml"
    sitemap_path.write_text(sitemap)
    print(f"✅ sitemap.xml 생성: {sitemap_path} ({len(urls)} URLs)")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 발리 여행 블로그 v8 대개선 시작")
    print("=" * 60)

    # 1. robots.txt / sitemap.xml 생성
    print("\n📋 robots.txt / sitemap.xml 생성...")
    generate_robots_txt()
    generate_sitemap()

    # 2. HTML 파일 처리
    print("\n📝 HTML 파일 처리 시작...")
    total = 0
    fixed_josa = 0
    fixed_alt = 0

    for area_dir in sorted(HTML_DIR.iterdir()):
        if not area_dir.is_dir():
            continue
        area = area_dir.name
        for cat_dir in sorted(area_dir.iterdir()):
            if not cat_dir.is_dir():
                continue
            category = cat_dir.name
            for html_file in sorted(cat_dir.iterdir()):
                if html_file.suffix != '.html':
                    continue
                page_idx = int(html_file.stem) - 1  # 001 → 0
                try:
                    process_html_file(str(html_file), area, category, page_idx)
                    total += 1
                except Exception as e:
                    print(f"  ❌ {html_file}: {e}")

    print(f"\n✅ 완료! 총 {total}개 HTML 파일 처리")
    print(f"   📝 조사 처리, 구문 다양화, ALT 구체화 적용")
    print(f"   📋 robots.txt + sitemap.xml 생성 완료")
    print(f"\n💡 다음 단계:")
    print(f"   1. python3 fix_v8.py 실행")
    print(f"   2. 결과 확인 후 필요시 추가 조정")
    print(f"   3. git add . && git commit -m 'v8: 조사 처리, 콘텐츠 다양화, SEO 강화'")
