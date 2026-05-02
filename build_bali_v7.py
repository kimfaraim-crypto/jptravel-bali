#!/usr/bin/env python3
"""
발리 여행 블로그 빌드 시스템 v7 — Ultimate Edition
- 924 HTML 페이지 (11지역 × 6카테고리 × 14페이지)
- 해시값 제목 버그 완전 수정
- SEO 최적화: long-tail 키워드, 고유 메타 설명
- 고품질 콘텐츠: Hook, Q&A, 상세 장소, 가격 비교, 내부 링크
- 이미지: 10장/페이지, Fisher-Yates 셔플, contextual alt text
- Schema.org Article 마크업, canonical URL, og:image
- 읽기 진행률 표시기, lazy loading, 모바일 최적화
- 사이트맵/robots.txt 자동 생성
"""

import os, re, json, random, hashlib, html as html_mod
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent

# v2 SEO 타이틀 임포트 (해시 버그 없음)
try:
    from seo_titles_v2 import generate_seo_title_v2, generate_meta_desc_v2, generate_keywords_v2
    HAS_SEO_V2 = True
except ImportError:
    HAS_SEO_V2 = False
    print("⚠️  seo_titles_v2.py not found, using fallback titles")

# 기존 데이터 임포트
from build_bali import BALI_DATA, CATEGORY_EXTRA_CONTENT

# 고품질 콘텐츠 생성기 임포트
try:
    from content_generator_v7 import (
        generate_high_quality_intro,
        generate_high_quality_place_detail,
        generate_high_quality_budget_guide,
        generate_high_quality_local_tip,
    )
    HAS_HQ_CONTENT = True
except ImportError:
    HAS_HQ_CONTENT = False
    print("⚠️  content_generator_v7.py not found, using basic content")

OUTPUT_HTML = BASE_DIR / "output" / "html" / "bali"
OUTPUT_IMAGES = BASE_DIR / "output" / "images"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
COUPON_IMG = BASE_DIR / "mrt_coupon.jpg"

AFFILIATE_URL = "https://myrealt.rip/YuJbb5"
TOUR_URL = "https://myrealt.rip/YoEc1b"
HOTEL_URL = "https://www.myrealtrip.com/search?keyword=%EB%B0%9C%EB%A6%AC+%ED%98%B8%ED%85%94&mylink_id=1696108"
SITE_URL = "https://balitravel.blog"
AUTHOR = "발리 여행 10년차 블로거"
CURRENT_YEAR = datetime.now().year

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

AREA_SLUGS = {
    "우붓": "ubud", "스미냑": "seminyak", "꾸따": "kuta",
    "사누르": "sanur", "누사두아": "nusa-dua", "울루와뚜": "uluwatu",
    "짠디다사": "candidasa", "로비나": "lovina", "킨타마니": "kintamani",
    "타나롯": "tanah-lot", "베두굴": "bedugul",
}

CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "🍜", "desc": "맛집 탐방", "en": "food"},
    "culture": {"name": "문화/사원", "icon": "🛕", "desc": "문화 체험", "en": "culture"},
    "beach": {"name": "해변/서핑", "icon": "🏖️", "desc": "해변 액티비티", "en": "beach"},
    "nature": {"name": "자연/모험", "icon": "🌿", "desc": "자연 탐방", "en": "nature"},
    "shopping": {"name": "쇼핑/마사지", "icon": "🛍️", "desc": "쇼핑 & 힐링", "en": "shopping"},
    "transport": {"name": "여행/교통", "icon": "🚗", "desc": "이동 정보", "en": "transport"},
}

# 이미지 alt text 템플릿 (카테고리별)
IMAGE_ALT_TEMPLATES = {
    "food": [
        "{area} {place} 맛집 사진", "{area} 현지 음식 {dish} 사진",
        "{area} {place} 레스토랑 내부", "{area} 비치클럽 음료 사진",
        "{area} 로컬 와룽 식사 사진", "{area} 브런치 카페 분위기",
        "{area} 해산물 BBQ 사진", "{area} 전통 발리 요리 사진",
        "{area} 카페 인테리어 사진", "{area} 디저트 메뉴 사진",
    ],
    "culture": [
        "{area} 사원 전경 사진", "{area} 전통 공연 케착춤 사진",
        "{area} 사원 건축 양식 사진", "{area} 힌두교 의식 사진",
        "{area} 문화 체험 활동 사진", "{area} 미술관 전시 사진",
        "{area} 사원 조각상 사진", "{area} 전통 춤 공연 사진",
        "{area} 사원 입구 풍경", "{area} 예술 공방 사진",
    ],
    "beach": [
        "{area} 해변 전경 사진", "{area} 서핑 포인트 파도 사진",
        "{area} 비치클럽 선셋 사진", "{area} 스노클링 포인트 사진",
        "{area} 해변 산책로 사진", "{area} 수영장/비치 풍경",
        "{area} 해변 일몰 사진", "{area} 해변 액티비티 사진",
        "{area} 해변에서 즐기는 관광객", "{area} 해변 카페 사진",
    ],
    "nature": [
        "{area} 라이스 테라스 풍경", "{area} 폭포 전경 사진",
        "{area} 트레킹 코스 사진", "{area} 화산 일출 사진",
        "{area} 열대 우림 풍경", "{area} 원숭이 숲 사진",
        "{area} 자연 수영장 사진", "{area} 정원/식물원 사진",
        "{area} 강변 풍경 사진", "{area} 전망대 뷰 사진",
    ],
    "shopping": [
        "{area} 아트 마켓 풍경", "{area} 기념품 가게 사진",
        "{area} 마사지/스파 내부 사진", "{area} 쇼핑몰 전경",
        "{area} 전통 공예품 사진", "{area} 시장 풍경 사진",
        "{area} 라탄 가방/기념품 사진", "{area} 스파 트리트먼트 사진",
        "{area} 로컬 시장 쇼핑 사진", "{area} 부티크숍 내부 사진",
    ],
    "transport": [
        "{area} 공항 풍경 사진", "{area} 스쿠터 렌트 사진",
        "{area} 그랩 택시 이용 사진", "{area} 교통체증 풍경",
        "{area} 보트/페리 사진", "{area} 도로 풍경 사진",
        "{area} 주차장/차량 사진", "{area} 공항 셔틀 사진",
        "{area} 시내 이동 풍경", "{area} 교통 수단 비교 사진",
    ],
}

# ============================================================
# Fisher-Yates 시드 셔플 (이미지 배분용)
# ============================================================

def seeded_shuffle(lst, seed_str):
    """Deterministic Fisher-Yates shuffle"""
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    result = list(lst)
    rng = seed_val
    for i in range(len(result) - 1, 0, -1):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        j = rng % (i + 1)
        result[i], result[j] = result[j], result[i]
    return result


# ============================================================
# 이미지 로딩
# ============================================================

def load_image_mapping():
    """이미지 매핑 로드"""
    for f in [MAPPING_FILE, BASE_DIR / "image_mapping_v2.json", BASE_DIR / "image_mapping.json"]:
        if f.exists():
            try:
                return json.loads(f.read_text())
            except:
                continue
    return {}


def get_images_v7(area, category, page_idx, count=10):
    """페이지별 고유 이미지 10장 선택 (Fisher-Yates 셔플)"""
    mapping = load_image_mapping()

    # v3 매핑에서 이미지 가져오기
    area_imgs = mapping.get(area, {}).get(category, [])

    # 같은 지역 다른 카테고리에서 보충
    if len(area_imgs) < count:
        other_imgs = []
        for cat, cat_imgs in mapping.get(area, {}).items():
            if cat != category:
                other_imgs.extend(cat_imgs)
        area_imgs = area_imgs + other_imgs

    # 파일시스템에서 직접 검색
    if len(area_imgs) < count:
        for search_dir in [OUTPUT_IMAGES / area / category, OUTPUT_IMAGES / area]:
            if search_dir.exists():
                imgs = sorted([f.name for f in search_dir.iterdir()
                              if f.suffix.lower() in ('.jpg', '.png', '.webp')])
                if imgs:
                    area_imgs = area_imgs + imgs
                    break

    # 플레이스홀더 fallback
    if not area_imgs:
        area_imgs = [f"placeholder_{hashlib.md5(f'{area}_{category}_{i}'.encode()).hexdigest()[:8]}.webp"
                     for i in range(count)]

    # Fisher-Yates seeded shuffle → page_idx별 다른 10장
    shuffled = seeded_shuffle(area_imgs, f"{area}_{category}_{page_idx}_img_v7")

    if len(shuffled) < count:
        result = []
        for i in range(count):
            result.append(shuffled[i % len(shuffled)])
        return result

    return shuffled[:count]


def get_og_image(area, category):
    """OG 이미지 경로 (첫 번째 이미지)"""
    mapping = load_image_mapping()
    imgs = mapping.get(area, {}).get(category, [])
    if imgs:
        return f"/images/{area}/{category}/{imgs[0]}"
    search_dir = OUTPUT_IMAGES / area / category
    if search_dir.exists():
        files = sorted([f.name for f in search_dir.iterdir()
                       if f.suffix.lower() in ('.jpg', '.png', '.webp')])
        if files:
            return f"/images/{area}/{category}/{files[0]}"
    return f"/images/{area}/001.webp"


def generate_image_alt(area, category, img_idx, data):
    """이미지에 맞는 contextual alt text 생성"""
    templates = IMAGE_ALT_TEMPLATES.get(category, IMAGE_ALT_TEMPLATES["food"])
    rng = random.Random(hash(f"{area}_{category}_{img_idx}_alt"))

    spots = data.get("spots", [])
    food = data.get("food", [])

    template = templates[img_idx % len(templates)]

    place = rng.choice(spots) if spots else area
    dish = food[0].get("name", "현지 음식") if food else "현지 음식"

    alt = template.format(area=area, place=place, dish=dish)
    return alt


# ============================================================
# 콘텐츠 생성 엔진 (v7 고품질)
# ============================================================

WRITING_ANGLES = [
    "실전_후기", "가성비_최적화", "숨은_명소", "첫방문_가이드",
    "커플_가족", "사진_포토스팟", "혼자_여행", "맛집_투어",
    "액티비티", "힐링_휴양", "문화_역사", "일몰_일출",
    "비수기_여행", "로컬_체험",
]

INTRO_HOOKS = [
    "결론부터 말하면, {area}의 {cat_name}은(는) {conclusion}. {detail}",
    "{area}를 {visit_count}번 다녀온 경험으로 말하면, {cat_name}은(는) {conclusion}. {detail}",
    "많은 분들이 '{area} {cat_name} 어디가 좋나요?'라고 물어보시는데요, {conclusion}. {detail}",
    "{area} 자유여행에서 {cat_name}은(는) 빼놓을 수 없는 코스입니다. {conclusion}. {detail}",
    "10년간 {area}를 다니면서 느낀 건, {cat_name}은(는) {conclusion}이라는 거예요. {detail}",
    "{area} 여행 계획 중이신가요? {cat_name} 정보를 한눈에 정리했습니다. {conclusion}. {detail}",
    "실제로 {area}에서 {cat_desc}을(를) 즐겨본 결과, {conclusion}. {detail}",
    "{area} {cat_name} 추천 리스트입니다. {conclusion}. {detail}",
    "{area} {cat_name} 가이드 — {conclusion}. {detail}",
    "{area}에서 {cat_desc}을(를) 계획 중이신가요? {conclusion}. {detail}",
    "{area} {cat_name} 완벽 분석입니다. {conclusion}. {detail}",
    "{area} {cat_name} 숨은 꿀팁 대방출입니다. {conclusion}. {detail}",
    "{area} {cat_name} — 현지인이 알려주는 진짜 정보입니다. {conclusion}. {detail}",
    "{area}를 여행한다면 {cat_name}은(는) 필수입니다. {conclusion}. {detail}",
]

# Q&A 템플릿 (카테고리별)
QA_TEMPLATES = {
    "food": [
        ("{area} 맛집 중 가장 추천하는 곳은?", None),
        ("{area} 가성비 맛집은 어디인가요?", None),
        ("{area}에서 꼭 먹어봐야 할 음식은?", None),
        ("{area} 브런치 카페 추천해주세요", None),
        ("{area} 야시장 음식 추천은?", None),
        ("{area} 비건/채식 맛집이 있나요?", None),
        ("{area} 해산물 맛집 추천해주세요", None),
        ("{area} 카페 추천 (인스타 감성)", None),
        ("{area} 디저트 맛집은?", None),
        ("{area}에서 술 한잔 하기 좋은 곳은?", None),
    ],
    "culture": [
        ("{area} 사원 방문 시 복장 규정은?", None),
        ("{area}에서 꼭 봐야 할 전통 공연은?", None),
        ("{area} 사원 투어 추천 코스는?", None),
        ("{area} 문화 체험 프로그램이 있나요?", None),
        ("{area} 미술관/박물관 추천해주세요", None),
        ("{area} 전통 공예 체험은 어디서?", None),
        ("{area} 사원에서 사진 촬영 가능한가요?", None),
    ],
    "beach": [
        ("{area} 해변에서 서핑 강습 받으려면?", None),
        ("{area} 비치클럽 추천은?", None),
        ("{area} 스노클링 포인트는?", None),
        ("{area} 일몰 보기 좋은 해변은?", None),
        ("{area} 해변 근처 맛집 추천해주세요", None),
        ("{area} 수영하기 안전한 해변은?", None),
        ("{area} 해변 액티비티 추천은?", None),
    ],
    "nature": [
        ("{area} 라이스 테라스 방문 팁은?", None),
        ("{area} 폭포 추천 및 가는 방법은?", None),
        ("{area} 트레킹 코스 추천해주세요", None),
        ("{area} 원숭이 주의사항은?", None),
        ("{area} 자연 명소 하루 코스 추천", None),
        ("{area} 화산 트레킹 가격은?", None),
    ],
    "shopping": [
        ("{area} 기념품 쇼핑 추천 장소는?", None),
        ("{area} 마사지 가격과 추천 샵은?", None),
        ("{area} 아트 마켓에서 흥정 팁은?", None),
        ("{area} 스파 추천해주세요", None),
        ("{area} 로컬 브랜드 쇼핑몰은?", None),
        ("{area} 발리 커피/차 쇼핑 추천", None),
    ],
    "transport": [
        ("{area} 공항에서 가는 방법은?", None),
        ("{area} 시내 이동 수단 추천은?", None),
        ("{area} 스쿠터 렌트 시 주의사항은?", None),
        ("{area} 그랩 이용 팁은?", None),
        ("{area}에서 다른 지역 가는 방법은?", None),
        ("{area} 교통체증 피하는 방법은?", None),
    ],
}

# 팁 템플릿 (카테고리별)
TIP_TEMPLATES = {
    "food": [
        "현지 음식은 위생 상태를 꼭 확인하세요. 사람이 많은 곳이 신선합니다.",
        "발리 음식은 대부분 매운 편이에요. 못 먹으면 'tidak pedas'라고 말하세요.",
        "팁 문화는 필수는 아니지만, 서비스 좋으면 10,000~20,000루피아 남기면 좋아요.",
        "식수는 반드시 생수를 사서 마시세요. 수돗물은 마시면 안 됩니다.",
        "아침 식사는 호텔 조식이 가성비 최고예요. 대부분 포함이니 꼭 이용하세요.",
        "와룽(Warung)은 현지 로컬 식당이에요. 가격이 매우 저렴하고 맛도 좋습니다.",
        "야시장 음식은 가성비 최고! 꾸따/사누르 야시장에서 20,000루피아로 배부르게 먹을 수 있어요.",
        "해산물 BBQ는 짐바란 비치에서! 선셋과 함께 먹으면 분위기 최고예요.",
        "GoFood 배달 앱으로 호텔에서 시켜 먹으면 교통비 절약돼요.",
        "로컬 음식 가격: 나시고렝 20,000~35,000Rp, 미고렝 15,000~25,000Rp 수준입니다.",
        "생과일 주스가 매우 저렴해요. 아보카도, 망고, 파파야 추천. 15,000~25,000Rp.",
        "관광지 음식은 2~3배 비싸요. 1~2블록만 걸어가면 가성비 맛집이 있습니다.",
    ],
    "culture": [
        "사원 방문 시 사롱(긴 스카프) 착용 필수! 입구에서 빌려주는 곳도 있어요.",
        "사원 입장료는 보통 30,000~60,000루피아입니다.",
        "사진 촬영 전 허락을 구하세요. 특히 제사 중인 장면은 촬영 금지입니다.",
        "케착춤은 울루와뚜 사원에서 일몰 시간에 보는 게 가장 분위기 좋아요.",
        "사원 축제 기간(210일마다)에는 특별한 의식을 볼 수 있어요.",
        "사원에 들어갈 때는 신발을 벗어야 해요. 슬리퍼보다 운동화가 편합니다.",
        "사원 가이드를 고용하면 문화적 배경을 깊이 이해할 수 있어요. 100,000~200,000Rp.",
        "사원 방문은 오전이 좋아요. 오후에는 관광객이 많아지고 더워집니다.",
    ],
    "beach": [
        "서핑 강습은 꾸따/스미냑에서 가장 저렴해요. 150,000~250,000루피아/1회.",
        "일몰은 서쪽 해변(꾸따, 스미냑, 울루와뚜)에서, 일출은 동쪽(사누르)에서!",
        "파도가 강한 날에는 수영 금지! 빨간 깃발 표시를 꼭 확인하세요.",
        "비치클럽은 선셋 2시간 전 가야 좋은 자리를 잡을 수 있어요.",
        "자외선이 매우 강해요. 선크림 SPF50+ 필수, 모자도 추천합니다.",
        "스노클링 장비는 현지에서 대여 가능해요. 50,000~100,000루피아.",
        "서핑 초보자는 반드시 강사와 함께하세요. 혼자 가면 위험합니다.",
        "해변 근처 주차장은 스쿠터 5,000Rp, 차량 10,000~20,000Rp입니다.",
    ],
    "nature": [
        "트레킹은 새벽 출발이 필수! 낮에는 매우 덥고 습해요.",
        "모기 기피제 필수. 열대 지역이라 모기가 많습니다.",
        "편한 운동화 필수. 샌들로 트레킹하면 다칠 수 있어요.",
        "화산 트레킹은 가이드 필수! 혼자 가면 위험합니다.",
        "원숭이에게 소지품을 빼앗기지 않게 주의하세요. 가방은 앞으로 메세요.",
        "라이스 테라스는 이른 아침에 가야 안개 없이 깨끗한 뷰를 볼 수 있어요.",
        "열대 우림에서는 갑작스러운 소나기가 올 수 있어요. 우산 필수!",
        "화산 트레킹 시 마스크를 챙기세요. 유황 가스가 나올 수 있어요.",
    ],
    "shopping": [
        "기념품 가게에서는 흥정이 필수! 첫 가격의 30~50% 수준으로 흥정하세요.",
        "마사지는 관광지보다 로컬 가게가 50% 저렴해요.",
        "아트 마켓은 오전에 가야 선택 폭이 넓어요.",
        "발리 커피, 코코넛 오일, 라탄 가방이 대표 기념품이에요.",
        "면세점은 공항에만 있어요. 시내에서 미리 구매하세요.",
        "스파 패키지 예약은 Klook/마이리얼트립에서 하면 20~30% 저렴해요.",
        "기념품은 공항에서 사면 2~3배 비싸요. 시내에서 미리 사세요.",
        "대형 쇼핑몰(비치워크, 디스커버리)에서는 카드 결제 가능해요.",
    ],
    "transport": [
        "그랩(Grab)이 가장 편하고 저렴해요. 현금/카드 모두 가능.",
        "스쿠터 렌트는 국제운전면허증 필수! 없으면 벌금 500,000루피아.",
        "공항에서 호텔까지 사전 예약 드라이버가 그랩보다 안전해요.",
        "발리는 교통체증이 매우 심해요. 이동 시간을 넉넉하게 잡으세요.",
        "장거리 이동은 전용 드라이버를 고용하는 게 편해요. 8시간 기준 500,000~700,000루피아.",
        "공항 택시는 프리미엄이에요. 그랩이 30~50% 저렴합니다.",
        "공항 도착 시 유심칩을 사면 그랩 사용이 편해요. 100,000~200,000Rp.",
        "발리 공항은 출국 수속이 2~3시간 걸릴 수 있어요. 넉넉하게 가세요.",
    ],
}

# 에피소드 템플릿
ANECDOTE_TEMPLATES = [
    "실제로 {area}에서 {activity}을(를) 했을 때, {observation}.",
    "저는 {area}를 {visit_count}번째 방문했는데, {observation}.",
    "{area} 현지인 {local_name}씨가 알려준 바로는, {local_tip}.",
    "작년에 {area}를 방문했을 때, {observation}.",
    "{area}에서 만난 한국인 여행자들이 가장 많이 하는 말이 '{quote}'입니다.",
    "블로그 후기만 보고 {area}에 갔다가 실제로는 {observation}.",
    "10년간 {area}를 다니면서 느낀 건, {insight}.",
    "{area} 여행 첫날에는 {first_day_observation}. 둘째날부터는 {day2_recommendation}.",
]


# ============================================================
# HTML 조립 함수들
# ============================================================

def generate_intro(area, category, page_idx, data):
    """Hook 문단 (Q&A 스타일 - 검색 의도 즉시 충족)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_intro_v7"))
    cat_info = CATEGORIES[category]
    desc = data.get("description", "")
    spots = data.get("spots", [])
    hidden = data.get("hidden_gem", "")
    best_season = data.get("best_season", "4~10월")

    conclusions = [
        f"{desc}",
        f"{spots[0] if spots else '주요 명소'}부터 시작하는 것이 가장 효율적",
        f"예산형으로도 충분히 즐길 수 있는 곳",
        f"{best_season}이 최적 시기",
        f"하루 일정으로도 충분하지만 2박 3일이 이상적",
    ]

    details = [
        f"특히 {spots[0] if spots else '주요 명소'}는 꼭 방문해야 하고, {data.get('food', [{}])[0].get('name', '현지 맛집')}에서 식사하는 걸 추천합니다.",
        f"자세한 가격과 팁은 아래에서 정리했으니 끝까지 읽어보세요.",
        f"아래에서 가격 비교, 교통 정보, 숙소 추천까지 모두 정리했습니다.",
    ]

    hook = rng.choice(INTRO_HOOKS)
    result = hook.format(
        area=area,
        cat_name=cat_info["name"],
        cat_desc=cat_info["desc"],
        conclusion=rng.choice(conclusions),
        detail=rng.choice(details),
        visit_count=rng.choice(["3", "5", "7", "10"]),
    )
    return result


def generate_qa_section(area, category, page_idx, data):
    """Q&A 섹션 (4개 질문)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_qa_v7"))
    qa_list = QA_TEMPLATES.get(category, QA_TEMPLATES["food"])
    selected = rng.sample(qa_list, min(4, len(qa_list)))

    # 답변 풀 생성
    cat_data = data.get(category, [])
    answer_pool = []
    for item in cat_data[:6]:
        name = item.get("name", "")
        price = item.get("price", "")
        tip = item.get("tip", "")
        if name:
            answer_pool.append(f"{name} ({price}) — {tip}")
    if not answer_pool:
        answer_pool = [f"{area}의 {CATEGORIES[category]['name']} 정보는 본문을 참고하세요."]

    html = ""
    for q_tpl, _ in selected:
        q = q_tpl.format(area=area)
        a = rng.choice(answer_pool)
        html += f'''<div style="margin:16px 0;padding:16px;background:linear-gradient(135deg,#e8f5e9,#f1f8e9);border-radius:10px;border:1px solid #c8e6c9">
<p style="margin:0 0 6px;font-weight:700;color:#2e7d32;font-size:1em">❓ {q}</p>
<p style="margin:0;color:#333;line-height:1.7">{a}</p>
</div>\n'''
    return html


def generate_featured_places(area, category, page_idx, data):
    """4-5개 추천 장소 (상세 정보 포함)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_places_v7"))
    cat_data = data.get(category, [])

    if not cat_data:
        return f'<p style="margin:16px 0;line-height:1.7">{area}의 {CATEGORIES[category]["name"]} 정보를 준비 중입니다.</p>'

    # 페이지별 다른 시작점
    start = (page_idx * 2) % len(cat_data)
    count = min(5, len(cat_data))
    selected = []
    for i in range(count):
        selected.append(cat_data[(start + i) % len(cat_data)])

    html = ""
    for i, item in enumerate(selected):
        name = item.get("name", "장소")
        price = item.get("price", "-")
        price_krw = item.get("price_krw", "")
        tip = item.get("tip", "")
        area_loc = item.get("area", area)
        must_try = item.get("must_try", "")

        # 10년차 블로거 팁 추가
        blogger_tips = [
            "10년간 다니면서 느낀 건, 오전에 가면 사람이 적다는 거예요.",
            "현지인만 아는 꿀팁인데, 주말보다 평일이 훨씬 쾌적합니다.",
            "사진 찍기 좋은 시간대가 따로 있어요. 골든아워에 가세요.",
            "가성비를 중시한다면 로컬 가게를, 분위기를 중시한다면 리조트를 추천합니다.",
            "예약 필수입니다. 특히 성수기에는 2~3일 전에 예약하세요.",
        ]

        extra_tip = rng.choice(blogger_tips)

        html += f'''<div style="margin:16px 0;padding:18px;background:#fafafa;border-radius:10px;border-left:4px solid #FF6B35">
<h3 style="font-size:1.1em;font-weight:700;margin:0 0 12px;color:#333">{i+1}. {name}</h3>
<p style="margin:0 0 8px;line-height:1.7"><strong>💰 가격:</strong> {price} {f"({price_krw})" if price_krw else ""}</p>
<p style="margin:0 0 8px;line-height:1.7"><strong>📍 위치:</strong> {area_loc}</p>
<p style="margin:0 0 8px;line-height:1.7"><strong>💡 팁:</strong> {tip}</p>
{"<p style='margin:0 0 8px;line-height:1.7'><strong>🍽️ 추천 메뉴:</strong> " + must_try + "</p>" if must_try else ""}
<p style="margin:0;line-height:1.7;color:#555;font-style:italic"><strong>✍️ 블로거 팁:</strong> {extra_tip}</p>
</div>\n'''
    return html


def generate_price_table(data):
    """가격 비교 표 (로컬 vs 투어 vs 호텔)"""
    price_comp = data.get("price_comparison", [])
    if not price_comp:
        return ""

    html = '''<div style="overflow-x:auto">
<table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white">
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">💰 로컬</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">🎫 투어</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">🏨 호텔</th>
</tr></thead><tbody>'''
    for i, pc in enumerate(price_comp):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        html += f'''<tr style="background:{bg}">
<td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">{pc["item"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd;color:#2e7d32;font-weight:600">{pc["local"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd">{pc["tour"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd">{pc["hotel"]}</td>
</tr>'''
    html += '''</tbody></table></div>
<p style="margin:6px 0;font-size:.85em;color:#666">※ 로컬 = 직접 방문 시 / 투어 = 투어 포함 시 / 호텔 = 호텔 내 레스토랑 시</p>'''
    return html


def generate_transport_table(data):
    """교통 정보 표"""
    transport = data.get("transport", [])
    if not transport:
        return ""
    html = '''<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white">
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th>
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">정보</th>
</tr></thead><tbody>'''
    for i, t in enumerate(transport):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        html += f'<tr style="background:{bg}"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">{t["name"]}</td><td style="padding:10px 8px;border:1px solid #ddd">{t["price"]}</td></tr>\n'
    html += '</tbody></table></div>\n'
    return html


def generate_hotel_table(data):
    """숙소 추천 표 (예산/중급/고급)"""
    hotels = data.get("hotels", {})
    if not hotels:
        return ""
    return f'''<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#1565c0;color:white">
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">등급</th>
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">가격대</th>
</tr></thead><tbody>
<tr style="background:#f9f9f9"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰 예산형</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('budget', '-')}</td></tr>
<tr style="background:#ffffff"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰💰 중급</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('mid', '-')}</td></tr>
<tr style="background:#f9f9f9"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰💰💰 고급</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('high', '-')}</td></tr>
</tbody></table></div>\n'''


def generate_hidden_gem(data):
    """숨은 명소 박스"""
    hidden = data.get("hidden_gem", "")
    if not hidden:
        return ""
    return f'''<div style="margin:16px 0;padding:16px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2">
<p style="margin:0;font-weight:600;color:#e65100">💎 숨은 명소: {hidden}</p>
</div>\n'''


def generate_tips(area, category, page_idx):
    """실전 팁 섹션 (3-5개)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_tips_v7"))
    tips = TIP_TEMPLATES.get(category, TIP_TEMPLATES["food"])
    selected = rng.sample(tips, min(5, len(tips)))

    html = '<ul style="padding-left:20px;margin:12px 0">\n'
    for tip in selected:
        html += f'<li style="margin-bottom:8px;line-height:1.7">{tip}</li>\n'
    html += '</ul>\n'
    return html


def generate_anecdote(area, category, page_idx):
    """에피소드/명언"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_anecdote_v7"))
    tpl = rng.choice(ANECDOTE_TEMPLATES)
    result = tpl.format(
        area=area,
        activity=rng.choice(["트레킹", "서핑", "식사", "쇼핑", "산책", "다이빙", "마사지"]),
        observation=rng.choice([
            "예상보다 훨씬 아름다운 풍경에 감동했습니다",
            "현지인들의 친절함에 다시 오고 싶어졌어요",
            "가격 대비 만족도가 매우 높았습니다",
            "사진으로는 표현할 수 없는 분위기가 있었어요",
        ]),
        visit_count=rng.choice(["3", "5", "7", "10"]),
        local_name=rng.choice(["Wayan", "Made", "Ketut", "Nyoman", "Komang"]),
        local_tip=rng.choice([
            "오전에 가면 사람이 적다고 하더라고요",
            "현지인만 아는 숨은 메뉴가 있다고 알려줬어요",
            "비수기에 오면 가격이 30% 저렴하다고 합니다",
        ]),
        quote=rng.choice([
            "생각보다 저렴하다", "다시 오고 싶다", "여기가 진짜 발리다",
        ]),
        insight=rng.choice([
            "갈 때마다 새로운 명소가 생기고 있어요",
            "비수기가 오히려 여행하기 더 좋습니다",
            "로컬 맛집이 관광지 맛집보다 훨씬 낫습니다",
        ]),
        first_day_observation=rng.choice([
            "교통체증에 놀라고", "더위에 적응하느라 힘들고",
            "흥정 문화에 당황하고", "음식 맛에 감동하고",
        ]),
        day2_recommendation=rng.choice([
            "여유롭게 즐기는 게 포인트예요",
            "로컬 리듬에 맞춰 움직이면 훨씬 즐거워요",
            "아침 일찍 움직이면 하루를 알차게 보낼 수 있어요",
        ]),
    )
    return f'<div style="margin:16px 0;padding:14px;background:#f8f9fa;border-radius:8px;border-left:4px solid #6c757d;font-style:italic;color:#555">{result}</div>\n'


def generate_related_links(area, category, page_idx):
    """관련 지역 내부 링크 (지리적 근접성 기반)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_links_v7"))
    cat_info = CATEGORIES[category]

    area_groups = {
        "south": ["꾸따", "스미냑", "누사두아", "울루와뚜"],
        "central": ["우붓", "타나롯", "베두굴"],
        "east": ["사누르", "짠디다사", "킨타마니"],
        "north": ["로비나"],
    }

    current_group = None
    for g, areas_in_group in area_groups.items():
        if area in areas_in_group:
            current_group = g
            break

    related = []
    if current_group:
        same_group = [a for a in area_groups[current_group] if a != area]
        related.extend(same_group[:2])

    other_groups = [g for g in area_groups if g != current_group]
    for g in other_groups:
        candidates = [a for a in area_groups[g] if a != area and a not in related]
        if candidates:
            related.append(rng.choice(candidates))
            break

    if not related:
        related = rng.sample([a for a in AREAS if a != area], min(3, len(AREAS) - 1))

    html = '''<div style="display:flex;flex-wrap:wrap;gap:10px;margin:12px 0">\n'''
    for ra in related[:3]:
        rpage = rng.randint(1, 14)
        html += f'<a href="/{ra}/{category}/{rpage:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{ra} {cat_info["name"]}</a>\n'
    html += '</div>\n'
    return html


def generate_images_html(area, category, page_idx, data):
    """이미지 10장 HTML (contextual alt text)"""
    images = get_images_v7(area, category, page_idx, 10)
    html = ""
    for i, img in enumerate(images):
        img_path = f"../../images/{area}/{category}/{img}"
        alt_text = generate_image_alt(area, category, i, data)
        html += f'<figure style="margin:20px 0;text-align:center"><img src="{img_path}" alt="{alt_text}" loading="lazy" style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);background:#f0f0f0" /></figure>\n'
    return html


# ============================================================
# 메인 HTML 생성
# ============================================================

def generate_html_v7(area, category, page_idx):
    """단일 HTML 페이지 생성 (v7 Ultimate)"""
    data = BALI_DATA.get(area, {})
    cat_info = CATEGORIES[category]

    # === SEO 타이틀 (v2 - 해시 버그 없음) ===
    if HAS_SEO_V2:
        title = generate_seo_title_v2(area, category, page_idx)
        meta_desc = generate_meta_desc_v2(area, category, page_idx, data)
        meta_keywords = generate_keywords_v2(area, category)
    else:
        title = f"{area} {cat_info['name']} 여행 가이드 — {CURRENT_YEAR} 최신 #{page_idx+1}"
        meta_desc = f"{area} {cat_info['name']} 여행 후기. 실제 가격 비교와 실전 팁 포함. {CURRENT_YEAR} 기준."
        meta_keywords = f"{area}, 발리, 인도네시아, {cat_info['name']}, 여행, 자유여행"

    # 날짜
    base_date = datetime(2026, 4, 1)
    page_date = base_date + timedelta(days=page_idx % 30)
    date_str = page_date.strftime("%Y-%m-%d")

    # OG 이미지
    og_image = get_og_image(area, category)

    # === 콘텐츠 섹션 (고품질 콘텐츠 우선 적용) ===
    if HAS_HQ_CONTENT:
        intro = generate_high_quality_intro(area, category, page_idx, data)
    else:
        intro = generate_intro(area, category, page_idx, data)
    qa_html = generate_qa_section(area, category, page_idx, data)

    # 추천 장소 (고품질 상세 설명)
    if HAS_HQ_CONTENT:
        rng_places = random.Random(hash(f"{area}_{category}_{page_idx}_hq_places"))
        cat_data = data.get(category, [])
        if cat_data:
            start = (page_idx * 2) % len(cat_data)
            count = min(5, len(cat_data))
            places_html = ""
            for i in range(count):
                place_idx = (start + i) % len(cat_data)
                places_html += generate_high_quality_place_detail(area, category, page_idx, data, place_idx)
        else:
            places_html = f'<p style="margin:16px 0;line-height:1.7">{area}의 {CATEGORIES[category]["name"]} 정보를 준비 중입니다.</p>'
    else:
        places_html = generate_featured_places(area, category, page_idx, data)

    price_table = generate_price_table(data)
    transport_html = generate_transport_table(data)
    hotel_html = generate_hotel_table(data)
    hidden_html = generate_hidden_gem(data)
    tips_html = generate_tips(area, category, page_idx)
    anecdote_html = generate_anecdote(area, category, page_idx)
    related_html = generate_related_links(area, category, page_idx)
    images_html = generate_images_html(area, category, page_idx, data)

    # 예산 가이드 & 현지인 꿀팁 (고품질)
    if HAS_HQ_CONTENT:
        budget_guide_html = f'''<div style="margin:16px 0;padding:16px;background:linear-gradient(135deg,#e3f2fd,#bbdefb);border-radius:10px;border:1px solid #90caf9">
<p style="margin:0;font-weight:600;color:#1565c0">💰 {area} 예산 가이드</p>
<p style="margin:8px 0 0;line-height:1.7;color:#333">{generate_high_quality_budget_guide(area, category, data)}</p>
</div>\n'''
        local_tip_html = f'''<div style="margin:16px 0;padding:16px;background:linear-gradient(135deg,#fce4ec,#f8bbd0);border-radius:10px;border:1px solid #f48fb1">
<p style="margin:0;font-weight:600;color:#c2185b">🔑 현지인 꿀팁</p>
<p style="margin:8px 0 0;line-height:1.7;color:#333">{generate_high_quality_local_tip(area, category, data)}</p>
</div>\n'''
    else:
        budget_guide_html = ""
        local_tip_html = ""

    # 쿠폰 HTML
    coupon_html = f'''<div style="margin:24px 0;text-align:center">
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰" style="max-width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12)" loading="lazy" />
</a>
<p style="margin-top:10px;font-size:.85em;color:#666">마이리얼트립 할인쿠폰 — 투어/티켓/숙소 최대 30% 할인</p>
</div>\n'''

    # 명소 리스트
    spots = data.get("spots", [])
    spots_html = ""
    if spots:
        spots_html = '<ol style="padding-left:20px;margin:12px 0">\n'
        for s in spots:
            spots_html += f'<li style="margin-bottom:6px;line-height:1.7"><strong>{s}</strong></li>\n'
        spots_html += '</ol>\n'

    # 마무리
    rng_footer = random.Random(hash(f"{area}_{category}_{page_idx}_footer_v7"))
    footers = [
        f"이상으로 {area}의 {cat_info['name']} 정보를 정리했습니다. {CURRENT_YEAR}년 기준 최신 정보이니 참고하세요.",
        f"{area} 여행 계획에 도움이 되셨길 바랍니다. 추가 질문은 댓글로 남겨주세요!",
        f"{area} {cat_info['name']} 여행, 즐거운 시간 보내세요! 🌴",
        f"이 글이 {area} 여행 계획에 도움이 되길 바랍니다. {CURRENT_YEAR}년 기준 정보입니다.",
    ]
    footer_text = rng_footer.choice(footers)

    # === 최종 HTML ===
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{html_mod.escape(title)}</title>
<meta name="description" content="{html_mod.escape(meta_desc)}">
<meta name="keywords" content="{html_mod.escape(meta_keywords)}">
<link rel="canonical" href="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:title" content="{html_mod.escape(title)}">
<meta property="og:description" content="{html_mod.escape(meta_desc)}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE_URL}{og_image}">
<meta property="og:url" content="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:site_name" content="발리 여행 블로그">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "{title}", "description": "{meta_desc}", "image": ["{SITE_URL}{og_image}"], "datePublished": "{date_str}", "dateModified": "{date_str}", "author": {{"@type": "Person", "name": "{AUTHOR}"}}, "publisher": {{"@type": "Organization", "name": "발리 여행 블로그"}}, "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html"}}}}</script>
<style>
:root {{ --primary: #FF6B35; --bg: #FAFAFA; --text: #1A1A2E; --text-light: #666; --border: #E0E0E0; --card-bg: #FFFFFF; --shadow: 0 2px 8px rgba(0,0,0,0.08); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); line-height: 1.85; word-break: keep-all; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
header {{ background: linear-gradient(135deg, #FF6B35, #FF8C61); color: white; padding: 40px 20px; text-align: center; }}
header h1 {{ font-size: 1.8rem; margin-bottom: 10px; word-break: keep-all; }}
header .meta {{ opacity: 0.9; font-size: 0.9rem; }}
.breadcrumb {{ padding: 15px 0; font-size: 0.85rem; color: var(--text-light); }}
.breadcrumb a {{ color: var(--primary); text-decoration: none; }}
article {{ background: var(--card-bg); border-radius: 12px; padding: 30px; box-shadow: var(--shadow); margin: 20px 0; }}
article h2 {{ color: var(--primary); font-size: 1.4rem; margin: 30px 0 15px; padding-bottom: 8px; border-bottom: 2px solid var(--primary); }}
article h3 {{ color: #333; font-size: 1.15rem; margin: 20px 0 10px; }}
article table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
article th, article td {{ padding: 10px 8px; border: 1px solid #ddd; text-align: left; }}
article th {{ background: #FF6B35; color: white; }}
article tr:nth-child(even) {{ background: #f9f9f9; }}
article ul, article ol {{ padding-left: 20px; margin: 16px 0; }}
article li {{ margin-bottom: 8px; line-height: 1.7; }}
.content-intro {{ margin: 0 0 20px; padding: 16px 20px; background: linear-gradient(135deg, #fff7ed, #fff3e0); border-radius: 10px; border: 1px solid #ffe0b2; font-weight: 500; line-height: 1.8; }}
.content-footer {{ margin: 24px 0; padding: 12px; background: #f5f5f5; border-radius: 8px; font-size: 0.9em; color: #666; }}
.tags {{ margin: 20px 0; }}
.tag {{ display: inline-block; background: #F0F0F0; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 3px; color: var(--text-light); }}
footer {{ text-align: center; padding: 30px; color: var(--text-light); font-size: 0.85rem; }}

/* 읽기 진행률 표시기 */
#reading-progress {{ position: fixed; top: 0; left: 0; width: 0%; height: 3px; background: linear-gradient(90deg, #FF6B35, #FF8C61); z-index: 9999; transition: width 0.1s; }}

/* 이미지 플레이스홀더 */
figure img {{ background: #f0f0f0; min-height: 100px; }}

/* 모바일 최적화 */
@media (max-width: 600px) {{
    .container {{ padding: 10px; }}
    article {{ padding: 20px; }}
    header h1 {{ font-size: 1.4rem; }}
    table {{ font-size: .8em; }}
    article h2 {{ font-size: 1.2rem; }}
    .content-intro {{ padding: 12px 16px; }}
}}

/* 다크모드 대응 */
@media (prefers-color-scheme: dark) {{
    :root {{ --bg: #1a1a2e; --text: #e0e0e0; --text-light: #aaa; --card-bg: #16213e; --border: #333; }}
    body {{ background: var(--bg); color: var(--text); }}
    article {{ background: var(--card-bg); }}
    .content-intro {{ background: linear-gradient(135deg, #1a1a2e, #16213e); border-color: #333; }}
    article tr:nth-child(even) {{ background: #1a1a2e; }}
}}
</style>
</head>
<body>

<!-- 읽기 진행률 표시기 -->
<div id="reading-progress"></div>
<script>
window.addEventListener('scroll', function() {{
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = (winScroll / height) * 100;
    document.getElementById('reading-progress').style.width = scrolled + '%';
}});
</script>

<!-- 상단 파트너스 고지문 -->
<div style="background:#f5f5f5;padding:10px 15px;border-bottom:1px solid #e0e0e0;font-size:13px;color:#555;text-align:center;line-height:1.6">
📌 이 글은 <strong>마이리얼트립 파트너스 활동</strong>의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다. 
구매에 추가 비용이 발생하지 않습니다. | 
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored" style="color:#d84315;font-weight:600">🎫 마이리얼트립 할인쿠폰 받기</a>
</div>

<header>
<h1>{html_mod.escape(title)}</h1>
<div class="meta">{cat_info['icon']} {area} | {cat_info['name']} | 📅 {CURRENT_YEAR}년 기준 | ✍️ {AUTHOR}</div>
</header>

<div class="container">
<nav class="breadcrumb">
<a href="/">🏠 홈</a> &gt; 
<a href="/{area}/">{area}</a> &gt; 
<a href="/{area}/{category}/">{cat_info['name']}</a> &gt; 
<span>{html_mod.escape(title[:30])}...</span>
</nav>

<article>

<!-- 결론 요약 박스 -->
<div class="content-intro">{intro}</div>

<!-- 쿠폰 (상단) -->
{coupon_html}

<!-- 이미지 10장 -->
{images_html}

<!-- Q&A 섹션 -->
<h2>❓ 자주 묻는 질문</h2>
{qa_html}

<!-- 추천 장소 상세 -->
<h2>📍 {area} {cat_info['name']} 추천</h2>
{places_html}

<!-- 가격 비교 표 -->
<h2>💰 {area} 가격 비교 (로컬 vs 투어 vs 호텔)</h2>
{price_table}

<!-- 명소 리스트 -->
<h2>🗺️ {area} 추천 명소</h2>
{spots_html}

<!-- 숨은 명소 -->
<h2>💎 숨은 명소</h2>
{hidden_html}

<!-- 교통 정보 -->
<h2>🚗 {area} 교통 정보</h2>
{transport_html}

<!-- 숙소 추천 -->
<h2>🏨 {area} 숙소 추천</h2>
{hotel_html}

<!-- 예산 가이드 (고품질) -->
{budget_guide_html}

<!-- 현지인 꿀팁 (고품질) -->
{local_tip_html}

<!-- 실전 팁 -->
<h2>💡 실전 팁</h2>
{tips_html}

<!-- 에피소드 -->
<h2>📝 여행 에피소드</h2>
{anecdote_html}

<!-- 관련 지역 링크 -->
<h2>🔗 이런 지역도 함께 보면 좋아요</h2>
{related_html}

<!-- 태그 -->
<div class="tags">
<span class="tag">{area}</span>
<span class="tag">발리</span>
<span class="tag">{cat_info['name']}</span>
<span class="tag">자유여행</span>
<span class="tag">가격비교</span>
<span class="tag">{CURRENT_YEAR}</span>
</div>

<!-- 마무리 -->
<div class="content-footer">
<p>{footer_text}</p>
<p style="margin-top:6px;font-size:0.85em;color:#999">📅 {CURRENT_YEAR}년 {rng_footer.choice(["4월", "5월"])} 업데이트</p>
</div>

</article>

<footer>
<p>© {CURRENT_YEAR} 발리 여행 블로그 | {AUTHOR}</p>
<p style="margin-top:8px">이 글은 마이리얼트립 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>
</footer>
</div>
</body>
</html>'''
    return html


# ============================================================
# 사이트맵 & robots.txt 생성
# ============================================================

def generate_sitemap():
    """sitemap.xml 생성 (924 URLs)"""
    urls = []
    for area in AREAS:
        for category in CATEGORIES:
            for page_idx in range(14):
                url = f"{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html"
                base_date = datetime(2026, 4, 1)
                page_date = base_date + timedelta(days=page_idx % 30)
                date_str = page_date.strftime("%Y-%m-%d")
                urls.append(f'''<url>
<loc>{url}</loc>
<lastmod>{date_str}</lastmod>
<changefreq>weekly</changefreq>
<priority>0.8</priority>
</url>''')

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''
    return sitemap


def generate_robots():
    """robots.txt 생성"""
    return f'''User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml

User-agent: Googlebot
Allow: /

User-agent: NaverBot
Allow: /
'''


# ============================================================
# 메인 빌드
# ============================================================

def main():
    print("=" * 60)
    print("🏗️  발리 여행 블로그 빌드 시스템 v7 — Ultimate Edition")
    print("=" * 60)
    print(f"📅 연도: {CURRENT_YEAR}")
    print(f"📍 지역: {len(AREAS)}개")
    print(f"📂 카테고리: {len(CATEGORIES)}개")
    print(f"📄 페이지/조합: 14")
    print(f"📊 총 페이지: {len(AREAS) * len(CATEGORIES) * 14}")
    print()

    OUTPUT_HTML.mkdir(parents=True, exist_ok=True)

    total = 0
    errors = 0

    for area in AREAS:
        print(f"\n📍 {area}")
        for category in CATEGORIES:
            cat_info = CATEGORIES[category]
            for page_idx in range(14):
                try:
                    html = generate_html_v7(area, category, page_idx)

                    cat_dir = OUTPUT_HTML / area / category
                    cat_dir.mkdir(parents=True, exist_ok=True)

                    filename = f"{page_idx + 1:03d}.html"
                    filepath = cat_dir / filename
                    filepath.write_text(html, encoding='utf-8')
                    total += 1
                except Exception as e:
                    errors += 1
                    print(f"  ❌ {area}/{category}/{page_idx+1:03d}: {e}")

            print(f"  {cat_info['icon']} {category}: 14개 생성")

    # 사이트맵 생성
    print("\n📄 사이트맵 생성 중...")
    sitemap_path = OUTPUT_HTML / "sitemap.xml"
    sitemap_path.write_text(generate_sitemap(), encoding='utf-8')
    print(f"  ✅ {sitemap_path}")

    # robots.txt 생성
    robots_path = OUTPUT_HTML / "robots.txt"
    robots_path.write_text(generate_robots(), encoding='utf-8')
    print(f"  ✅ {robots_path}")

    # 쿠폰 이미지 복사
    coupon_dest = OUTPUT_HTML.parent / "images" / "mrt_coupon.jpg"
    coupon_dest.parent.mkdir(parents=True, exist_ok=True)
    if COUPON_IMG.exists() and not coupon_dest.exists():
        import shutil
        shutil.copy2(COUPON_IMG, coupon_dest)
        print(f"📷 쿠폰 이미지 복사: {coupon_dest}")

    print(f"\n{'=' * 60}")
    print(f"✅ 총 {total}개 HTML 페이지 생성 완료!")
    if errors:
        print(f"⚠️  {errors}개 에러 발생")
    print(f"📁 위치: {OUTPUT_HTML}")
    print(f"📄 sitemap.xml: {sitemap_path}")
    print(f"🤖 robots.txt: {robots_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
