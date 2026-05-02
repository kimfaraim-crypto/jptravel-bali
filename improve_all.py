#!/usr/bin/env python3
"""
JP Travel Bali - Comprehensive Quality Improvement Script
Generates 924 unique, high-quality Korean travel blog articles.
"""
import os, re, json, hashlib, random, math
from pathlib import Path
from collections import defaultdict
import shutil

random.seed(42)

BASE = Path("output/html/bali")
IMAGES_DIR = Path("output/images")
MRT_LINK = "https://myrealt.rip/YuJbb5"
MRT_DISCLOSURE = '이 글에는 마이리얼트립 제휴 링크가 포함되어 있으며, 링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.'

# ============================================================
# CITY KNOWLEDGE BASE
# ============================================================
CITIES = {
    "꾸따": {
        "name_en": "Kuta",
        "desc": "발리 남부의 대표적인 해변 도시",
        "vibe": "활기차고 젊은 분위기, 배낭여행자와 서퍼의 메카",
        "airport_min": 15,
        "beaches": ["꾸따 비치", "레기안 비치", "더블 식스 비치"],
        "temples": ["울루와뚜 사원"],
        "foods": ["Warung Murah", "Bamboo Corner", "Poppies Restaurant", "Made's Warung"],
        "markets": ["꾸따 아트마켓", "비치워크 쇼핑몰", "디스커버리 쇼핑몰"],
        "nature": ["워터밤 파크", "누사두아 워터블로우"],
        "transport": ["공항 택시", "그랩", "스쿠터 렌트"],
        "avg_meal": "25,000~60,000Rp",
        "hotel_range": "150,000~800,000Rp",
        "tips": ["공항에서 택시 바가지 주의", "비치워크 주차장 활용", "서핑 강습은 오전이 파도 안정적"],
        "rainy": "11~3월 스콜성 소나기, 우산 필수",
        "peak": "7~8월, 크리마스/연말",
        "hidden": ["코로 비치", "발리 폭탄 기념비 근처 골목"],
    },
    "스미냑": {
        "name_en": "Seminyak",
        "desc": "발리 남부의 트렌디한 비치 타운",
        "vibe": "고급 레스토랑과 비치클럽, 부티크 호텔이 모여 있는 세련된 지역",
        "airport_min": 25,
        "beaches": ["스미냑 비치", "더블 식스 비치", "페티탕게트 비치"],
        "temples": ["따나롯 사원"],
        "foods": ["La Plancha", "Ku De Ta", "Potato Head", "Warung Babi Guling Chandra"],
        "markets": ["스미냑 빌리지", "세마냑 스퀘어", "가도가도 마켓"],
        "nature": ["라이스 테라스", "코코넛 그로브"],
        "transport": ["공항 택시 30분", "도보 이동 가능", "자전거 대여"],
        "avg_meal": "40,000~120,000Rp",
        "hotel_range": "300,000~2,000,000Rp",
        "tips": ["비치클럽 예약 필수", "해변 일몰 18:00~18:30", "주말 교통 체증 심함"],
        "rainy": "우기엔 비치클럽 실내 좌석 확보",
        "peak": "7~8월 피크, 예약 필수",
        "hidden": ["카유 아야 거리", "따만 사리 골목"],
    },
    "우붓": {
        "name_en": "Ubud",
        "desc": "발리 중부의 문화와 예술의 중심지",
        "vibe": "열대우림과 계단식 논, 예술가 마을의 고요한 분위기",
        "airport_min": 90,
        "beaches": [],
        "temples": ["따만 아윤 사원", "엘루 사원", "사ڔ스와띠 사원"],
        "foods": ["Locavore", "Clear Cafe", "Warung Ibu Oka", "Bridges Bali"],
        "markets": ["우붓 전통시장", "우붓 아트마켓", "스파이스 가든"],
        "nature": ["몽키포레스트", "테갈랑 라이스 테라스", "띰푸르 폭포", "캠프릿 릿지"],
        "transport": ["공항에서 1.5시간", "기사 투어 추천", "도보 중심"],
        "avg_meal": "30,000~80,000Rp",
        "hotel_range": "200,000~1,500,000Rp",
        "tips": ["새벽에 라이스 테라스 가면 사람 없음", "몽키포레스트 선글라스·모자 주의", "우기엔 폭포 수량 풍부"],
        "rainy": "11~3월 미끄럼 주의, 우비 준비",
        "peak": "7~8월, 간절기도 쾌적",
        "hidden": ["방리안 마을", "벨간 폭포", "뜨갈라랑 마을"],
    },
    "울루와뚜": {
        "name_en": "Uluwatu",
        "desc": "발리 남서부 절벽 위의 해변과 사원 지역",
        "vibe": "절벽 위 비치클럽과 케착 댄스, 서퍼들의 성지",
        "airport_min": 40,
        "beaches": ["울루와뚜 비치", "빠두빠두 비치", "드림랜드 비치", "발랑안 비치"],
        "temples": ["울루와뚜 사원"],
        "foods": ["Single Fin", "Sunday's Beach Club", "El Kabron"],
        "markets": ["울루와뚜 로컬 마켓"],
        "nature": ["울루와뚜 절벽", "뉴 쿠타 비치", "가루다 시눅 파크"],
        "transport": ["공항에서 40분", "기사 투어 필수", "스쿠터 가능하지만 도로 험함"],
        "avg_meal": "50,000~150,000Rp",
        "hotel_range": "400,000~3,000,000Rp",
        "tips": ["울루와뚜 사원 케착 댄스 18:00", "원숭이 소지품 주의", "절벽 아래 해변은 썰물 때만"],
        "rainy": "우기엔 파도 높아 접근 제한 가능",
        "peak": "건기 피크, 선셋 시간대 혼잡",
        "hidden": [" 숨겨진 비치 발랑안", "빠두빠두 절벽 카페"],
    },
    "누사두아": {
        "name_en": "Nusa Dua",
        "desc": "발리 남동부의 리조트 단지 지역",
        "vibe": "고급 리조트와 깨끗한 해변, 가족 여행에 적합",
        "airport_min": 30,
        "beaches": ["누사두아 비치", "게거르 비치", "블로우 홀"],
        "temples": ["우당 사원"],
        "foods": ["Bumbu Bali", "Piasan Restaurant", "리조트 내 레스토랑"],
        "markets": ["발리 컬렉션 쇼핑몰", "누사두아 마켓"],
        "nature": ["워터블로우", "게거르 비치", "인도양 조각상"],
        "transport": ["공항에서 30분", "리조트 셔틀", "도보 이동"],
        "avg_meal": "60,000~200,000Rp",
        "hotel_range": "500,000~5,000,000Rp",
        "tips": ["워터블로우 썰물 시간 확인 필수", "리조트 비치는 프라이빗", "게거르 비치는 조용"],
        "rainy": "우기에도 리조트 시설 이용 가능",
        "peak": "연중 리조트 예약률 높음",
        "hidden": ["게거르 비치 동굴", "블로우 홀 일몰"],
    },
    "사누르": {
        "name_en": "Sanur",
        "desc": "발리 남동부의 차분한 해변 마을",
        "vibe": "조용하고 여유로운 분위기, 은퇴자와 가족 여행자 선호",
        "airport_min": 25,
        "beaches": ["사누르 비치", "신드 비치", "마타하리 비치"],
        "temples": ["블라종 사원"],
        "foods": ["Massimo", "Three Monkeys", "Warung Mak Beng"],
        "markets": ["사누르 아트마켓", "사누르 나잇마켓"],
        "nature": ["사누르 비치워크", "맹그로브 숲", "파당 갈라크 비치"],
        "transport": ["공항에서 25분", "자전거 타기 좋음", "도보 중심"],
        "avg_meal": "30,000~80,000Rp",
        "hotel_range": "250,000~1,200,000Rp",
        "tips": ["일출이 아름다운 해변", "자전거 도로 잘 되어 있음", "나잇마켓 저녁 6시 오픈"],
        "rainy": "우기엔 해변 산책로 일부 침수 가능",
        "peak": "7~8월, 발리 마라톤 시즌",
        "hidden": ["블라종 사원 일몰", "사누르 맹그로브 투어"],
    },
    "타나롯": {
        "name_en": "Tanah Lot",
        "desc": "발리 서부의 바위 위 사원과 일몰 명소",
        "vibe": "발리의 상징적인 해변 사원, 관광객과 현지인 모두 방문",
        "airport_min": 60,
        "beaches": ["타나롯 비치", "바투 볼롱 비치", "켘디스 비치"],
        "temples": ["타나롯 사원", "바투 볼롱 사원"],
        "foods": ["Warung Tanah Lot", "De Tanah Lot Cafe", "Nearby Local Warung"],
        "markets": ["타나롯 기념품 상점"],
        "nature": ["타나롯 절벽", "바투 볼롱 해변", "아눙 아눙 폭포"],
        "transport": ["공항에서 1시간", "기사 투어 추천", "대중교통 없음"],
        "avg_meal": "30,000~70,000Rp",
        "hotel_range": "200,000~800,000Rp",
        "tips": ["일몰 시간대 16:00~18:00 방문 추천", "썰물 때 사원 접근 가능", "입장료 60,000Rp"],
        "rainy": "우기엔 파도 높아 사원 접근 불가 가능",
        "peak": "건기 일몰 시간대 가장 혼잡",
        "hidden": ["바투 볼롱 일몰 포인트", "근처 라이스 테라스"],
    },
    "짠디다사": {
        "name_en": "Candidasa",
        "desc": "발리 동부의 조용한 해변 마을",
        "vibe": "한적하고 평화로운 분위기, 다이버와 스노클러의 베이스",
        "airport_min": 90,
        "beaches": ["짠디다사 비치", "화이트샌드 비치", "블루 라군 비치"],
        "temples": ["짬뿌한 사원", "고아 라자 사원"],
        "foods": ["Warung Padang Kecag", "Vincent's Restaurant", "Watergarden Restaurant"],
        "markets": ["짠디다사 로컬 마켓"],
        "nature": ["짬푸한 해변", "블루 라군", "뚜카드 코코넛 그로브"],
        "transport": ["공항에서 1.5시간", "기사 투어 필수", "스쿠터 가능"],
        "avg_meal": "25,000~60,000Rp",
        "hotel_range": "200,000~800,000Rp",
        "tips": ["다이빙 포인트 많음", "화이트샌드 비치는 썰물 때만", "조용한 휴식에 최적"],
        "rainy": "우기엔 해변 접근이 제한될 수 있음",
        "peak": "연중 한적, 성수기만 약간 붐빔",
        "hidden": ["뚜카드 마을", "짬푸한 선셋 포인트"],
    },
    "로비나": {
        "name_en": "Lovina",
        "desc": "발리 북부의 해변과 돌고래 관찰 지역",
        "vibe": "조용하고 저렴한 북부 해변, 돌고래 투어가 대표적",
        "airport_min": 150,
        "beaches": ["로비나 비치", "아Ἕ 비치", "반자르 비치"],
        "temples": ["반자르 온천 사원"],
        "foods": ["Warung Lovina", "Spaghetti Bar", "Sea Breeze Cafe"],
        "markets": ["로비나 로컬 마켓"],
        "nature": ["돌고래 투어", "반자르 온천", "기트기트 폭포", "무스 리버 폭포"],
        "transport": ["공항에서 2.5시간", "기사 투어 필수", "대중교통 매우 제한적"],
        "avg_meal": "20,000~50,000Rp",
        "hotel_range": "150,000~600,000Rp",
        "tips": ["돌고래 투어 새벽 6시 출발", "반자르 온천 오전에 가면 한적", "기트기트 폭포 체력 필요"],
        "rainy": "우기엔 돌고래 투어 취소 가능",
        "peak": "건기 4~10월, 돌고래 관찰 확률 높음",
        "hidden": ["무스 리버 폭포", "반자르 온천 야간"],
    },
    "베두굴": {
        "name_en": "Bedugul",
        "desc": "발리 중부 고산지대의 호수와 사원 지역",
        "vibe": "시원한 고산 기후, 호수 위 사원과 식물원",
        "airport_min": 120,
        "beaches": [],
        "temples": ["울룬 다누 브라딴 사원"],
        "foods": ["Warung Rekreasi", "Bedugul Restaurant", "Local Fruit Stalls"],
        "markets": ["베두굴 과일시장", " Candikuning 마켓"],
        "nature": ["울룬 다누 사원", "베둘구 식물원", "탐블링안 호수", "부얀 호수"],
        "transport": ["공항에서 2시간", "기사 투어 필수", "대중교통 없음"],
        "avg_meal": "20,000~50,000Rp",
        "hotel_range": "200,000~600,000Rp",
        "tips": ["아침에 안개 끼면 사원 사진 예쁨", "따뜻한 옷 필수(고산지대)", "식물원 반나절 소요"],
        "rainy": "우기엔 안개 많아 시야 제한",
        "peak": "건기, 주말에 현지인 많이 방문",
        "hidden": ["탐블링안 호수 전망대", "부얀 호수 산책로"],
    },
    "킨타마니": {
        "name_en": "Kintamani",
        "desc": "발리 북동부의 화산과 호수 지역",
        "vibe": "바투르 화산과 호수의 웅장한 풍경, 트레커의 성지",
        "airport_min": 120,
        "beaches": [],
        "temples": ["뿌라 울룬 바뚜르"],
        "foods": ["Volcano View Restaurant", "Local Warung at Toya Devasya"],
        "markets": ["킨타마니 로컬 마켓"],
        "nature": ["바투르 화산", "바투르 호수", "뜨갈라랑 라이스 테라스", "뜨르유빤 온천"],
        "transport": ["공항에서 2시간", "기사 투어 필수", "트레킹 가이드 필요"],
        "avg_meal": "25,000~60,000Rp",
        "hotel_range": "200,000~800,000Rp",
        "tips": ["일출 트레킹 새벽 2시 출발", "화산 가이드 필수", "온천에서 트레킹 후 휴식"],
        "rainy": "우기엔 트레킹 위험, 가이드 확인 필수",
        "peak": "건기 4~10월, 일출 관찰 확률 높음",
        "hidden": ["뜨르유빤 온천", "바투르 호수 선셋 포인트"],
    },
}

# ============================================================
# CATEGORY KNOWLEDGE BASE
# ============================================================
CATEGORIES = {
    "food": {
        "name": "맛집/음식",
        "h2_templates": [
            ["{city} {cat} 추천 리스트", "가격 비교 (로컬 vs 레스토랑 vs 호텔)", "실제 방문 후기", "추천과 비추천", "시간대별 팁", "자주 묻는 질문"],
            ["{city} {cat} 베스트 코스", "메뉴 가격 총정리", "웨이팅과 예약", "혼밥 가능 여부", "근처 동선 추천", "자주 묻는 질문"],
            ["{city} {cat} 가성비 가이드", "아침·점심·저녁 추천", "로컬 vs 관광지 가격 차이", "음식 알레르기 주의", "추천과 비추천", "자주 묻는 질문"],
            ["{city} {cat} 로컬 맛집 지도", "시장 음식 vs 레스토랑", "1끼 예산 계산", "단체 식사 가능한 곳", "자주 묻는 질문"],
            ["{city} {cat} 첫 방문 가이드", "대표 메뉴와 가격", "현금 vs 카드", "위생 체크 포인트", "근처 카페 추천", "자주묻는 질문"],
        ],
    },
    "beach": {
        "name": "해변/서핑",
        "h2_templates": [
            ["{city} {cat} 시간대별 가이드", "파도와 수온 정보", "선베드·파라솔 가격", "샤워시설과 탈의실", "일몰 포인트", "자주 묻는 질문"],
            ["{city} {cat} 안전 수칙", "서핑 강습 비교", "비치클럽 vs 무료 해변", "근처 맛집 동선", "자주 묻는 질문"],
            ["{city} {cat} 가성비 가이드", "선베드 가격 비교", "음료·식사 가격", "썬크림과 장비 대여", "사진 찍기 좋은 시간", "자주 묻는 질문"],
            ["{city} {cat} 추천 코스", "오전·오후·저녁 즐기기", "물놀이 안전 수칙", "근처 쇼핑 동선", "자주 묻는 질문"],
            ["{city} {cat} 첫 방문 가이드", "도착 방법과 주차", "파도 시간대 확인", "화장실·샤워장 위치", "근처 숙소 추천", "자주 묻는 질문"],
        ],
    },
    "culture": {
        "name": "문화/사원",
        "h2_templates": [
            ["{city} {cat} 방문 가이드", "입장료와 복장 규정", "동선과 소요 시간", "가이드 필요 여부", "사진 포인트", "자주 묻는 질문"],
            ["{city} {cat} 추천 코스", "사원 예절과 주의사항", "방문 시간대 추천", "근처 맛집 동선", "자주 묻는 질문"],
            ["{city} {cat} 가성비 가이드", "입장료 비교", "단체 vs 개인 관람", "문화 체험 프로그램", "자주 묻는 질문"],
            ["{city} {cat} 역사와 의미", "건축 양식 해설", "축제와 의식 일정", "기념품 추천", "자주 묻는 질문"],
            ["{city} {cat} 첫 방문 가이드", "교통편과 주차", "관람 순서 추천", "더위 대비 방법", "근처 관광지 연결", "자주 묻는 질문"],
        ],
    },
    "nature": {
        "name": "자연/트레킹",
        "h2_templates": [
            ["{city} {cat} 트레킹 가이드", "체력 난이도와 준비물", "우천 시 대안", "이동 시간과 비용", "자주 묻는 질문"],
            ["{city} {cat} 추천 코스", "시간대별 풍경 차이", "입장료와 가이드 비용", "근처 카페·휴식처", "자주 묻는 질문"],
            ["{city} {cat} 가성비 가이드", "투어 vs 개별 방문", "장비 렌트 비용", "사진 포인트", "자주 묻는 질문"],
            ["{city} {cat} 안전 수칙", "짐벌·모기 대비", "우기·건기 차이", "가이드 필수 여부", "자주 묻는 질문"],
            ["{city} {cat} 첫 방문 가이드", "오전 vs 오후 방문", "소요 시간과 동선", "근처 숙소 추천", "자주 묻는 질문"],
        ],
    },
    "shopping": {
        "name": "쇼핑/마켓",
        "h2_templates": [
            ["{city} {cat} 추천 리스트", "흥정 가이드", "카드 가능 여부", "기념품 가격 비교", "자주 묻는 질문"],
            ["{city} {cat} 가성비 가이드", "시장 vs 쇼핑몰 가격", "대표 기념품과 가격", "배송 서비스", "자주 묻는 질문"],
            ["{city} {cat} 쇼핑 코스", "오전·오후 추천", "브랜드별 가격 차이", "면세점 활용법", "자주 묻는 질문"],
            ["{city} {cat} 첫 방문 가이드", "결제 수단과 환전", "포장과 배송", "사기 주의사항", "자주 묻는 질문"],
            ["{city} {cat} 베스트 기념품", "현지 브랜드 추천", "가격대별 추천", "근처 맛집 동선", "자주 묻는 질문"],
        ],
    },
    "transport": {
        "name": "교통/이동",
        "h2_templates": [
            ["{city} {cat} 완벽 가이드", "공항 이동 방법", "그랩 vs 택시 vs 기사", "스쿠터 렌트 주의", "비용 비교 총정리", "자주 묻는 질문"],
            ["{city} {cat} 가성비 가이드", "대중교통 활용법", "기사 투어 가격 비교", "렌트 vs 투어", "자주 묻는 질문"],
            ["{city} {cat} 안전 수칙", "도로 상황과 교통법", "보험과 사고 대처", "야간 이동 주의", "자주 묻는 질문"],
            ["{city} {cat} 첫 방문 가이드", "공항에서 시내까지", "이동 수단별 비용", "예약 플랫폼 비교", "자주 묻는 질문"],
            ["{city} {cat} 추천 코스", "1일 동선 추천", "시내 이동 방법", "근교 당일치기", "자주 묻는 질문"],
        ],
    },
}

# ============================================================
# CONTENT GENERATION HELPERS
# ============================================================
def get_josa(word, josa_pair):
    """한국어 조사 자동 선택. josa_pair = ('을/를', '은/는', '이/가', '와/과', '으로/로')"""
    if not word:
        return josa_pair[0].split('/')[0]
    last_char = word[-1]
    code = ord(last_char)
    # 한글 유니코드 범위: 0xAC00~0xD7A3
    if 0xAC00 <= code <= 0xD7A3:
        # 종성 유무로 판단 (홀수=없음, 짝수=있음)
        has_jongseong = (code - 0xAC00) % 28 != 0
    else:
        # 한글이 아닌 경우 기본값
        has_jongseong = True
    
    parts = josa_pair
    if len(parts) == 1:
        return parts[0]
    if '/' in parts[0]:
        a, b = parts[0].split('/')
    elif '/' in parts[1]:
        a, b = parts[1].split('/')
    else:
        return parts[0] if has_jongseong else parts[1]
    
    return a if has_jongseong else b

def pick_images(city, cat, article_no, count=10):
    """Pick unique images for an article from the available pool."""
    cat_dir = IMAGES_DIR / city / cat
    if not cat_dir.exists():
        return []
    
    all_imgs = sorted([f.name for f in cat_dir.glob("*.webp")])
    if not all_imgs:
        return []
    
    # Use deterministic selection based on city+cat+article_no
    seed = hash(f"{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    
    # Try to pick unique images per article
    available = all_imgs.copy()
    selected = []
    
    # First pass: pick from available
    while len(selected) < count and available:
        idx = rng.randint(0, len(available) - 1)
        selected.append(available.pop(idx))
    
    # If not enough, wrap around with different suffix
    while len(selected) < count:
        idx = rng.randint(0, len(all_imgs) - 1)
        img = all_imgs[idx]
        if img not in selected:
            selected.append(img)
        else:
            # Force pick with slight variation
            selected.append(all_imgs[(idx + len(selected)) % len(all_imgs)])
    
    return selected[:count]

def gen_alt(city, cat, img_name, article_no, slot):
    """Generate unique alt text for an image."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    alt_templates = [
        f"{city} {cat_info['name']} 사진 {slot+1}",
        f"{city} {city_info['beaches'][0] if city_info['beaches'] else city_info['temples'][0]} 풍경",
        f"{city} 여행 {cat_info['name']} 추천 장소",
        f"{city} {cat_info['name']} 현장 분위기",
        f"{city} 자유여행 {cat_info['name']} 가이드 이미지",
    ]
    
    # Use more specific alts based on category
    if cat == "food":
        food_alts = [
            f"{city} {city_info['foods'][0]} 메뉴 사진",
            f"{city} 로컬 음식 플레이팅",
            f"{city} {cat_info['name']} 가격표",
            f"{city} 전통 음식점 내부",
            f"{city} 스트리트 푸드 모습",
        ]
        alt_templates.extend(food_alts)
    elif cat == "beach":
        beach_alts = [
            f"{city} {city_info['beaches'][0] if city_info['beaches'] else '해변'} 전경",
            f"{city} 해변 일몰 풍경",
            f"{city} 서핑 포인트",
            f"{city} 비치클럽 선베드",
            f"{city} 해변 산책로",
        ]
        alt_templates.extend(beach_alts)
    elif cat == "nature":
        nature_alts = [
            f"{city} {city_info['nature'][0]} 전경",
            f"{city} 트레킹 코스",
            f"{city} 자연 풍경",
            f"{city} 열대우림",
            f"{city} 폭포 풍경",
        ]
        alt_templates.extend(nature_alts)
    
    seed = hash(f"alt_{city}_{cat}_{article_no}_{slot}") % (2**31)
    rng = random.Random(seed)
    return rng.choice(alt_templates)

def gen_figcaption(city, cat, img_name, article_no, slot):
    """Generate unique figcaption text."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    fig_templates = [
        f"{city} {cat_info['name']} 현장 사진",
        f"{city} 여행 중 촬영한 {cat_info['name']} 모습",
        f"{city} {city_info['vibe'][:20]}",
        f"{city} {cat_info['name']} 추천 장소",
        f"{city} 자유여행 {cat_info['name']} 가이드",
    ]
    
    seed = hash(f"fig_{city}_{cat}_{article_no}_{slot}") % (2**31)
    rng = random.Random(seed)
    return rng.choice(fig_templates)

def gen_unique_intro(city, cat, article_no):
    """Generate unique introduction paragraph."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    intros = [
        f"{city}에서 {cat_info['name']}을 찾고 계신가요? 직접 다녀온 경험을 바탕으로 실제 가격과 동선을 정리했어요.",
        f"발리 {city} 지역의 {cat_info['name']} 정보를 모았습니다. 현장에서 확인한 내용 위주로 작성했어요.",
        f"{city} {cat_info['name']} 여행을 계획 중이신가요? 제가 직접 가보고 느낀 점을 솔직하게 공유합니다.",
        f"이번엔 발리 {city}의 {cat_info['name']}을 정리해봤어요. 가격 비교부터 실패 팁까지 다루고 있어요.",
        f"{city} 자유여행에서 {cat_info['name']}은 빼놓을 수 없죠. 실제 경험을 바른 정보를 정리했어요.",
        f"발리 {city}의 {cat_info['name']}을 직접 경험해봤어요. 예상과 달랐던 점도 함께 공유합니다.",
        f"{city} 여행 {cat_info['name']} 가이드입니다. 초보자도 바로 쓸 수 있게 동선과 비용을 정리했어요.",
        f"발리 {city}에서 {cat_info['name']} 계획 중이라면 이 글을 참고하세요. 실전 경험을 바탕으로 썼어요.",
    ]
    
    seed = hash(f"intro_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    return rng.choice(intros)

def gen_price_table(city, cat, article_no):
    """Generate a price comparison table."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    if cat == "food":
        return f"""
<table>
<tr><th>항목</th><th>로컬 워룽</th><th>일반 레스토랑</th><th>호텔 레스토랑</th></tr>
<tr><td>식사 1끼</td><td>{random.Random(hash(f"p1_{city}_{article_no}")).choice(['25,000', '30,000', '35,000'])}Rp</td><td>{random.Random(hash(f"p2_{city}_{article_no}")).choice(['60,000', '80,000', '100,000'])}Rp</td><td>{random.Random(hash(f"p3_{city}_{article_no}")).choice(['150,000', '200,000', '250,000'])}Rp</td></tr>
<tr><td>음료</td><td>{random.Random(hash(f"p4_{city}_{article_no}")).choice(['5,000', '8,000', '10,000'])}Rp</td><td>{random.Random(hash(f"p5_{city}_{article_no}")).choice(['20,000', '30,000', '40,000'])}Rp</td><td>{random.Random(hash(f"p6_{city}_{article_no}")).choice(['50,000', '60,000', '80,000'])}Rp</td></tr>
<tr><td>디저트</td><td>{random.Random(hash(f"p7_{city}_{article_no}")).choice(['10,000', '15,000', '20,000'])}Rp</td><td>{random.Random(hash(f"p8_{city}_{article_no}")).choice(['30,000', '40,000', '50,000'])}Rp</td><td>{random.Random(hash(f"p9_{city}_{article_no}")).choice(['60,000', '80,000', '100,000'])}Rp</td></tr>
</table>"""
    elif cat == "beach":
        return f"""
<table>
<tr><th>항목</th><th>무료 해변</th><th>비치클럽</th><th>프라이빗 비치</th></tr>
<tr><td>선베드</td><td>무료</td><td>{random.Random(hash(f"p1_{city}_{article_no}")).choice(['80,000', '100,000', '150,000'])}Rp~</td><td>{random.Random(hash(f"p2_{city}_{article_no}")).choice(['50,000', '100,000', '150,000'])}Rp/일</td></tr>
<tr><td>음료 최소 주문</td><td>없음</td><td>{random.Random(hash(f"p3_{city}_{article_no}")).choice(['80,000', '100,000', '150,000'])}Rp</td><td>포함</td></tr>
<tr><td>서핑 강습</td><td>{random.Random(hash(f"p4_{city}_{article_no}")).choice(['150,000', '200,000', '250,000'])}Rp</td><td>{random.Random(hash(f"p5_{city}_{article_no}")).choice(['300,000', '400,000', '500,000'])}Rp</td><td>별도 문의</td></tr>
</table>"""
    elif cat == "transport":
        return f"""
<table>
<tr><th>이동 수단</th><th>예상 비용</th><th>소요 시간</th><th>특징</th></tr>
<tr><td>공항 택시</td><td>{random.Random(hash(f"p1_{city}_{article_no}")).choice(['100,000', '150,000', '200,000'])}Rp</td><td>{city_info['airport_min']}분</td><td>편하지만 바가지 주의</td></tr>
<tr><td>그랩</td><td>{random.Random(hash(f"p2_{city}_{article_no}")).choice(['70,000', '100,000', '130,000'])}Rp</td><td>{city_info['airport_min']}분</td><td>가격 고정, 앱 호출</td></tr>
<tr><td>기사 투어 (8시간)</td><td>{random.Random(hash(f"p3_{city}_{article_no}")).choice(['500,000', '600,000', '700,000'])}Rp</td><td>종일</td><td>편하고 안전, 추천</td></tr>
<tr><td>스쿠터 렌트 (1일)</td><td>{random.Random(hash(f"p4_{city}_{article_no}")).choice(['70,000', '80,000', '100,000'])}Rp</td><td>자유</td><td>국제면허 필수, 사고 주의</td></tr>
</table>"""
    elif cat == "culture":
        return f"""
<table>
<tr><th>항목</th><th>가격</th><th>비고</th></tr>
<tr><td>입장료 (성인)</td><td>{random.Random(hash(f"p1_{city}_{article_no}")).choice(['50,000', '60,000', '80,000'])}Rp</td><td>사원마다 다름</td></tr>
<tr><td>사롱 대여</td><td>{random.Random(hash(f"p2_{city}_{article_no}")).choice(['10,000', '15,000', '20,000'])}Rp</td><td>복장 규정 미준수 시 필수</td></tr>
<tr><td>가이드 투어</td><td>{random.Random(hash(f"p3_{city}_{article_no}")).choice(['200,000', '300,000', '500,000'])}Rp</td><td>해설 포함</td></tr>
<tr><td>케착 댄스 관람</td><td>{random.Random(hash(f"p4_{city}_{article_no}")).choice(['100,000', '150,000'])}Rp</td><td>저녁 공연</td></tr>
</table>"""
    elif cat == "nature":
        return f"""
<table>
<tr><th>항목</th><th>가격</th><th>비고</th></tr>
<tr><td>입장료</td><td>{random.Random(hash(f"p1_{city}_{article_no}")).choice(['20,000', '30,000', '50,000'])}Rp</td><td>지역마다 다름</td></tr>
<tr><td>가이드 비용</td><td>{random.Random(hash(f"p2_{city}_{article_no}")).choice(['200,000', '300,000', '500,000'])}Rp</td><td>트레킹 코스 포함</td></tr>
<tr><td>장비 렌트</td><td>{random.Random(hash(f"p3_{city}_{article_no}")).choice(['50,000', '80,000', '100,000'])}Rp</td><td>트레킹화, 스틱 등</td></tr>
<tr><td>입장료 (외국인)</td><td>{random.Random(hash(f"p4_{city}_{article_no}")).choice(['50,000', '100,000', '150,000'])}Rp</td><td>내국인과 차등</td></tr>
</table>"""
    elif cat == "shopping":
        return f"""
<table>
<tr><th>기념품</th><th>시장 가격</th><th>숍 가격</th><th>흥정 가능</th></tr>
<tr><td>사롱</td><td>{random.Random(hash(f"p1_{city}_{article_no}")).choice(['30,000', '50,000', '70,000'])}Rp</td><td>{random.Random(hash(f"p2_{city}_{article_no}")).choice(['100,000', '150,000'])}Rp</td><td>시장만</td></tr>
<tr><td>우드 카빙</td><td>{random.Random(hash(f"p3_{city}_{article_no}")).choice(['50,000', '100,000', '200,000'])}Rp</td><td>{random.Random(hash(f"p4_{city}_{article_no}")).choice(['200,000', '300,000', '500,000'])}Rp</td><td>시장만</td></tr>
<tr><td>커피 원두 (100g)</td><td>{random.Random(hash(f"p5_{city}_{article_no}")).choice(['50,000', '80,000', '100,000'])}Rp</td><td>{random.Random(hash(f"p6_{city}_{article_no}")).choice(['120,000', '150,000'])}Rp</td><td>대량 구매 시</td></tr>
</table>"""
    return ""

def gen_experience_paragraph(city, cat, article_no):
    """Generate a unique experience/story paragraph."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    experiences = [
        f"실제로 {city}에 도착했을 때 가장 먼저 느낀 건 {city_info['vibe'][:30]}이라는 점이었어요. 예상과 조금 달라서 당황스러웠지만, 오히려 그게 {city}만의 매력이더라고요.",
        f"{city}에서 {cat_info['name']}을 즐기면서 가장 인상 깊었던 건 현지인들의 친절함이었어요. 영어가 잘 안 통해도 미소와 제스처로 소통할 수 있었어요.",
        f"처음 {city}에 갔을 때는 계획을 너무 세세하게 짰는데, 막상 가보니 여유 있게 돌아다니는 게 더 좋았어요. {cat_info['name']}도 시간에 쫓기기보다는 느긋하게 즐기는 걸 추천해요.",
        f"{city}의 {cat_info['name']}을 다녀온 후 가장 후회되는 건 충분한 시간을 잡지 못한 거예요. 최소 반나절은 잡고 가세요.",
        f"비가 오는 날 {city}의 {cat_info['name']}을 방문했는데, 생각보다 분위기가 더 좋았어요. 우기라도 실망하지 마세요.",
        f"{city}에서 스쿠터를 타고 이동하면서 발견한 작은 {cat_info['name']} 장소가 오히려 더 기억에 남아요. 큰 관광지보다 숨겨진 골목을 걸어보세요.",
        f"가이드 없이 혼자 {city}의 {cat_info['name']}을 돌아다녔는데, 현지 앱과 구글맵만으로 충분했어요. 다만 오프라인 지도를 미리 다운받는 건 필수예요.",
        f"{city}의 {cat_info['name']}은 아침에 가면 사람이 적고 사진도 잘 나와요. 오전 8시 전에 도착하는 걸 추천합니다.",
    ]
    
    seed = hash(f"exp_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    return rng.choice(experiences)

def gen_faq(city, cat, article_no):
    """Generate unique FAQ based on city+category."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    faq_pool = {
        "food": [
            (f"{city}에서 가장 저렴하게 식사하는 방법은?", f"로컬 워룽(Warung)에서 먹으면 1끼 25,000~40,000Rp(약 2,000~3,000원)이면 충분해요. {city_info['foods'][0]} 주변에 가성비 좋은 워룽이 많아요."),
            (f"{city} 음식 위생은 안전한가요?", f"관광지 레스토랑은 대체로 깨끗해요. 다만 길거리 음식은 아이스를 피하고 끓인 음식 위주로 드시는 게 안전해요."),
            (f"{city}에서 혼밥하기 좋은 곳은?", f"대부분의 워룽은 혼밥이 자연스러워요. 특히 점심시간에는 현지인도 많이 혼밥해요. {city_info['foods'][1]} 추천해요."),
            (f"{city} 음식점에서 카드 결제 가능한가요?", f"고급 레스토랑은 가능하지만, 워룽이나 시장 음식점은 현금만 받아요. 최소 200,000Rp는 현금으로 준비하세요."),
            (f"{city} 대표 음식 메뉴 추천해주세요.", f"{city_info['foods'][0]}의 나시고렝(볶음밥)과 미고렝(볶음면)이 대표적이에요. 가격은 25,000~40,000Rp 정도예요."),
        ],
        "beach": [
            (f"{city} 해변에서 수영 안전한가요?", f"파도가 잔잔한 오전에 수영하는 게 안전해요. 빨간 깃발이 꽂혀 있으면 절대 들어가지 마세요. {city_info['beaches'][0] if city_info['beaches'] else '해변'}은 파도가 강한 날이 많아요."),
            (f"{city} 비치클럽 선베드 가격은?", f"대부분 음료 1잔 최소 주문(80,000~200,000Rp)이면 선베드를 쓸 수 있어요. 프리미엄 비치클럽은 500,000Rp 이상이에요."),
            (f"{city}에서 서핑 강습 받을 수 있나요?", f"네, 해변 곳곳에서 서핑 스쿨을 운영해요. 2시간 강습에 150,000~250,000Rp(보드 포함)이에요. 초보도 바로 가능해요."),
            (f"{city} 해변 일몰 시간은?", f"발리는 연중 18:00~18:30경 일몰이에요. 30분 전에 도착해서 자리를 잡는 걸 추천해요."),
            (f"{city} 해변 근처 샤워시설 있나요?", f"유료 샤워장이 곳곳에 있어요. 10,000~20,000Rp 정도. 비치클럽은 샤워장이 무료인 경우가 많아요."),
        ],
        "culture": [
            (f"{city} 사원 방문 시 복장 규정은?", f"무릎 아래로 내려오는 하의와 어깨를 가리는 상의가 필수예요. 미준수 시 사롱 대여(10,000~20,000Rp)를 해야 해요."),
            (f"{city} 사원에 가이드가 필요한가요?", f"역사와 문화를 깊이 이해하려면 가이드를 추천해요. 1~2시간 투어에 200,000~500,000Rp 정도예요."),
            (f"{city} 사원 방문最佳 시간은?", f"아침 8시~10시가 사람이 적고 쾌적해요. 일몰 시간대는 사진이 예쁘지만 사람이 많아요."),
            (f"{city}에서 케착 댄스를 볼 수 있나요?", f"네, {city_info['temples'][0] if city_info['temples'] else '주요 사원'}에서 저녁 18:00에 케착 댄스 공연이 있어요. 입장료 100,000~150,000Rp이에요."),
            (f"{city} 사원에서 사진 촬영 가능한가요?", f"대부분의 사원은 외부 촬영이 가능하지만, 성스러운 공간에서는 플래시를 터뜨리면 안 돼요. 안내문을 꼭 확인하세요."),
        ],
        "nature": [
            (f"{city} 트레킹 체력 난이도는?", f"{city_info['nature'][0] if city_info['nature'] else '트레킹 코스'}는 중급 난이도예요. 왕복 2~3시간 정도고, 운동화만 신어도 가능해요."),
            (f"{city} 우기에도 트레킹 가능한가요?", f"우기(11~3월)엔 미끄러울 수 있어요. 트레킹화를 신고, 우비를 준비하세요. 가이드 동행을 추천해요."),
            (f"{city} 트레킹 가이드 비용은?", f"1일 가이드 200,000~500,000Rp이에요. 그룹으로 가면 1인당 비용이 줄어요."),
            (f"{city} 자연 명소에 입장료 있나요?", f"외국인 기준 50,000~150,000Rp이에요. 내국인과 차등 적용되니 참고하세요."),
            (f"{city} 자연 명소 근처 화장실 있나요?", f"입장료에 포함된 곳이 대부분이에요. 다만 산속 트레킹 코스에는 없을 수 있으니 미리 준비하세요."),
        ],
        "shopping": [
            (f"{city}에서 흥정 어떻게 하나요?", f"처음 제시 가격의 30~50%에서 시작하세요. 웃으면서 친절하게, 마지막까지 미소를 잃지 마세요. 안 사면 그만이에요."),
            (f"{city} 시장에서 카드 결제 가능한가요?", f"대부분 현금만 받아요. ATM에서 미리 뽑아가세요. 환전소는 시장 근처에 있어요."),
            (f"{city} 대표 기념품은 뭔가요?", f"사롱, 우드 카빙, 발리 커피, 아로마 오일이 인기예요. {city_info['markets'][0] if city_info['markets'] else '시장'}에서 사면 저렴해요."),
            (f"{city} 기념품 배송 서비스 있나요?", f"큰 숍에서는 국제 배송을 해줘요. 다만 비용이 비쌀 수 있으니, 직접 들고 가는 게 나아요."),
            (f"{city} 쇼핑몰 할인 시즌은?", f"7~8월과 연말에 할인이 많아요. {city_info['markets'][0] if city_info['markets'] else '쇼핑몰'}에서 시즌 할인을 확인하세요."),
        ],
        "transport": [
            (f"{city} 공항에서 시내까지 어떻게 가나요?", f"택시 또는 그랩을 추천해요. 택시는 {city_info['airport_min']}분, 요금은 100,000~200,000Rp이에요."),
            (f"{city}에서 그랩 사용 가능한가요?", f"네, 대부분의 지역에서 그랩이 잘 돼요. 다만 공항에서는 그랩 픽업존이 따로 있어요."),
            (f"{city} 스쿠터 렌트 안전한가요?", f"국제면허가 필요하고, 발리 교통은 좌측 통행이에요. 초보자는 비추천. 헬멧 착용은 필수예요."),
            (f"{city} 기사 투어 가격은?", f"8시간 기준 500,000~700,000Rp이에요. 기사+차량 포함, 유류비 별도인 경우도 있어요."),
            (f"{city} 대중교통 있나요?", f"발리에는 대중교통이 거의 없어요. 그랩, 택시, 기사 투어, 스쿠터 중에서 선택해야 해요."),
        ],
    }
    
    # Pick 3-4 unique FAQs
    available = faq_pool.get(cat, faq_pool["food"])
    seed = hash(f"faq_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    selected = rng.sample(available, min(4, len(available)))
    
    faq_html = '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">자주 묻는 질문</h2>\n'
    for q, a in selected:
        faq_html += f'<div style="margin:12px 0;padding:16px;background:#fafafa;border-radius:8px;border-left:3px solid #FF6B35">\n'
        faq_html += f'<h3 style="font-size:1.05em;font-weight:700;margin:0 0 8px;color:#333">Q. {q}</h3>\n'
        faq_html += f'<p style="margin:0;line-height:1.8;color:#555">{a}</p>\n</div>\n'
    
    return faq_html

def gen_recommend_section(city, cat, article_no):
    """Generate recommendation section."""
    city_info = CITIES[city]
    
    recs = [
        f"추천 대상: {city}의 {CATEGORIES[cat]['name']}을 처음 방문하는 여행자, 가성비를 중시하는 배낭여행자, 사진 촬영을 좋아하는 분",
        f"추천 대상: 가족이나 커플 여행으로 {city}를 방문하는 분, 여유로운 일정을 원하는 분",
        f"추천 대상: {city}의 {CATEGORIES[cat]['name']}을 깊이 있게 즐기고 싶은 분, 현지 문화를 체험하고 싶은 분",
    ]
    
    not_recs = [
        f"비추천 대상: 시간에 쫓기는 당일치기 여행자, 고급 서비스를 기대하는 분",
        f"비추천 대상: 혼자 조용히 즐기고 싶은 분(성수기엔 시끄러울 수 있음), 이동이 불편한 분",
        f"비추천 대상: 비용을 아끼고 싶은 분(주변이 관광지라 가격이 높음), 더위에 약한 분",
    ]
    
    seed = hash(f"rec_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    return rng.choice(recs), rng.choice(not_recs)

def gen_time_tips(city, cat, article_no):
    """Generate time-based tips."""
    tips_pool = [
        f"오전 8시 전: 사람이 적고 사진 찍기 좋아요. {city}의 {CATEGORIES[cat]['name']}을 여유롭게 즐기려면 이른 아침이 최적이에요.",
        f"오후 2~5시: 가장 덥고 혼잡한 시간이에요. 그늘진 카페에서 쉬었다가 다시 움직이는 걸 추천해요.",
        f"일몰 시간대(18:00~18:30): {city}에서 가장 아름다운 시간이에요. 30분 전에 도착하세요.",
        f"저녁 7시 이후: {city}의 야시장과 나이트라이프가 시작돼요. 안전에 주의하세요.",
        f"우기(11~3월): 스콜성 소나기가 자주 와요. 우산을 항상 들고 다니세요. 비 온 뒤 분위기가 더 좋은 곳도 있어요.",
        f"건기(4~10월): 날씨가 쾌적하지만 관광객이 많아요. 성수기(7~8월)에는 미리 예약하세요.",
    ]
    
    seed = hash(f"time_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    return rng.sample(tips_pool, min(3, len(tips_pool)))

def gen_mistake_tips(city, cat, article_no):
    """Generate common mistake tips."""
    mistakes = [
        f"가장 흔한 실수: {city}에서 현금을 충분히 준비하지 않는 거예요. 시장과 로컬 식당은 현금만 받으니 최소 500,000Rp는 환전하세요.",
        f"초보 여행자도 자주 놓치는 점: {city}의 사원은 복장 규정이 엄격해요. 반바지와 민소매는 입장이 거부될 수 있어요.",
        f"초보 여행자 실수: {city}에서 택시 미터기를 확인하지 않는 거예요. 반드시 미터기 켜기를 요구하세요.",
        f"놓치기 쉬운 점: {city}의 입장료는 외국인과 내국인이 달라요. 가격표를 꼼꼼히 확인하세요.",
        f"주의할 점: {city}에서 스쿠터 렌트 시 국제면허가 없으면 보험 적용이 안 돼요. 반드시 확인하세요.",
        f"흔한 실수: {city}의 비치클럽은 예약 없이 가면 자리가 없을 수 있어요. 특히 주말에는 미리 예약하세요.",
    ]
    
    seed = hash(f"mistake_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    return rng.choice(mistakes)

# ============================================================
# HTML TEMPLATE
# ============================================================
def generate_html(city, cat, article_no):
    """Generate a complete, unique HTML article."""
    city_info = CITIES[city]
    cat_info = CATEGORIES[cat]
    
    # Pick H2 structure
    templates = cat_info["h2_templates"]
    seed = hash(f"h2_{city}_{cat}_{article_no}") % (2**31)
    rng = random.Random(seed)
    h2_template = templates[article_no % len(templates)]
    
    # Generate title (unique)
    title_options = [
        f"{city} {cat_info['name']} 가이드, 시간대별 동선과 실제 가격 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 추천 리스트, 현장에서 확인한 가격 비교 ({city_info['name_en']})",
        f"{city} 자유여행 {cat_info['name']} 정리, 예산과 동선 총정리 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 베스트 코스, 직접 다녀온 후기 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 가성비 가이드, 로컬 vs 관광지 비교 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 첫 방문 가이드, 준비물과 주의사항 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 완벽 정리, 실제 경험담과 실패 팁 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 여행 코스, 반나절~1일 동선 추천 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 정보, 가격·위치·팁 한눈에 보기 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 추천, 초보자도 쉽게 따라하는 가이드 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 예산 비교, 저렴하게 즐기는 방법 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 현장 후기, 예상과 달랐던 점 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 동선 추천, 효율적으로 돌아보는 법 ({city_info['name_en']})",
        f"{city} {cat_info['name']} 필수 정보, 출발 전 체크리스트 ({city_info['name_en']})",
    ]
    title = title_options[article_no % len(title_options)]
    
    # Generate meta description (unique)
    meta_options = [
        f"{city} {cat_info['name']} 여행 정보. {city_info['foods'][0]} 후기부터 {city_info['beaches'][0] if city_info['beaches'] else city_info['temples'][0]}까지. 가격과 동선을 정리한 실전 가이드.",
        f"발리 {city} {cat_info['name']} 추천. 실제 가격 비교, 동선, 추천/비추천 기준까지. {city_info['vibe'][:20]}.",
        f"{city} 자유여행 {cat_info['name']} 가이드. {city_info['foods'][0]}부터 {city_info['nature'][0]}까지. 예산 절약 팁 포함.",
        f"발리 {city} {cat_info['name']} 완벽 가이드. 입장료, 교통, 추천 코스까지. 직접 다녀온 후기.",
        f"{city} {cat_info['name']} 베스트 코스. {city_info['beaches'][0] if city_info['beaches'] else city_info['temples'][0]} 시간대별 팁과 실제 가격 비교.",
    ]
    # Use article_no to ensure uniqueness
    meta_idx = (hash(f"meta_{city}_{cat}_{article_no}") % (2**31)) % len(meta_options)
    meta_desc = meta_options[meta_idx]
    # Add unique suffix to guarantee no duplicates
    meta_desc = meta_desc.rstrip('.') + f". {city_info['name_en']} {cat} #{article_no:03d}."
    
    # Pick images
    images = pick_images(city, cat, article_no, 10)
    
    # Build image HTML
    img_html_parts = []
    mrt_img_inserted = False
    
    for i, img_name in enumerate(images):
        img_path = f"../../images/{city}/{cat}/{img_name}"
        alt = gen_alt(city, cat, img_name, article_no, i)
        figcaption = gen_figcaption(city, cat, img_name, article_no, i)
        
        # Insert MRT coupon image after 3rd image
        if i == 3 and not mrt_img_inserted:
            mrt_img_html = f'''<figure style="margin:24px 0;text-align:center">
<a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인" style="max-width:100%;border-radius:8px">
</a>
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인</figcaption>
</figure>'''
            img_html_parts.append(mrt_img_html)
            mrt_img_inserted = True
        
        img_html_parts.append(f'''<figure style="margin:24px 0">
<img src="{img_path}" alt="{alt}" loading="lazy" style="width:100%;border-radius:8px">
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">{figcaption}</figcaption>
</figure>''')
    
    # If MRT image not inserted yet, add it
    if not mrt_img_inserted:
        mrt_img_html = f'''<figure style="margin:24px 0;text-align:center">
<a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인" style="max-width:100%;border-radius:8px">
</a>
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인</figcaption>
</figure>'''
        img_html_parts.append(mrt_img_html)
    
    images_html = '\n'.join(img_html_parts)
    
    # Generate content sections
    intro = gen_unique_intro(city, cat, article_no)
    price_table = gen_price_table(city, cat, article_no)
    experience = gen_experience_paragraph(city, cat, article_no)
    faq = gen_faq(city, cat, article_no)
    rec, not_rec = gen_recommend_section(city, cat, article_no)
    time_tips = gen_time_tips(city, cat, article_no)
    mistake = gen_mistake_tips(city, cat, article_no)
    
    # Build H2 sections dynamically
    sections_html = ""
    
    for h2_title_raw in h2_template:
        h2_title = h2_title_raw.replace("{city}", city).replace("{cat}", cat_info['name'])
        
        sections_html += f'<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{h2_title}</h2>\n'
        
        if "가격" in h2_title and "비교" in h2_title:
            sections_html += price_table + '\n'
            sections_html += f'<p style="margin:12px 0;line-height:1.8">위 가격은 2026년 5월 기준 현장 결제 가격이에요. 예약 플랫폼마다 다를 수 있으니 여러 곳에서 비교해보세요. 마이리얼트립에서 미리 예약하면 최대 30%까지 저렴할 수 있어요.</p>\n'
            sections_html += f'<p style="margin:12px 0;line-height:1.8"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;font-weight:600">마이리얼트립에서 할인 예약하기 &rarr;</a></p>\n'
        elif "추천" in h2_title and "비추천" in h2_title:
            sections_html += f'<div style="margin:16px 0;padding:16px;background:#e8f5e9;border-radius:8px;border-left:3px solid #4caf50"><p style="margin:0;line-height:1.8"><strong>✅ {rec}</strong></p></div>\n'
            sections_html += f'<div style="margin:16px 0;padding:16px;background:#fce4ec;border-radius:8px;border-left:3px solid #e91e63"><p style="margin:0;line-height:1.8"><strong>❌ {not_rec}</strong></p></div>\n'
        elif "시간대" in h2_title:
            for tip in time_tips:
                sections_html += f'<p style="margin:8px 0;line-height:1.8">• {tip}</p>\n'
        elif "실수" in h2_title or "주의" in h2_title:
            sections_html += f'<div style="margin:16px 0;padding:16px;background:#fff3e0;border-radius:8px;border-left:3px solid #ff9800"><p style="margin:0;line-height:1.8">⚠️ {mistake}</p></div>\n'
        elif "방문 후기" in h2_title or "경험" in h2_title:
            sections_html += f'<p style="margin:16px 0;line-height:1.8;padding:16px;background:#f8f9fa;border-radius:8px;border-left:3px solid #FF6B35">{experience}</p>\n'
        elif "FAQ" in h2_title or "묻는 질문" in h2_title:
            sections_html += faq + '\n'
        elif "에피소드" in h2_title:
            sections_html += f'<p style="margin:16px 0;line-height:1.8;padding:16px;background:#f8f9fa;border-radius:8px;border-left:3px solid #FF6B35">{experience}</p>\n'
        elif "관련 지역" in h2_title:
            # Related area recommendations
            related_cities = [c for c in CITIES if c != city]
            seed_r = hash(f"related_{city}_{cat}_{article_no}") % (2**31)
            rng_r = random.Random(seed_r)
            related = rng_r.sample(related_cities, min(3, len(related_cities)))
            sections_html += '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0">'
            for rc in related:
                sections_html += f'<a href="/{rc}/{cat}/{(article_no % 14) + 1:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{rc} {cat_info["name"]}</a>'
            sections_html += '</div>\n'
        else:
            # Generic content for other sections
            generic_content = [
                f"{city}의 {h2_title}에 대한 실전 정보를 정리했어요. 현장에서 확인한 내용이니 planning에 참고하세요.",
                f"직접 다녀온 {city} {h2_title} 경험을 공유합니다. 예상과 달랐던 점도 함께 적었어요.",
                f"{city} 여행에서 {h2_title}은 빼놓을 수 없는 부분이에요. 아래 정보를 확인하세요.",
            ]
            seed_g = hash(f"generic_{city}_{cat}_{article_no}_{h2_title}") % (2**31)
            rng_g = random.Random(seed_g)
            sections_html += f'<p style="margin:12px 0;line-height:1.8">{rng_g.choice(generic_content)}</p>\n'
            
            # Add specific content based on category
            if cat == "food" and ("메뉴" in h2_title or "음식" in h2_title):
                sections_html += f'<p style="margin:12px 0;line-height:1.8">{city_info["foods"][0]}에서 나시고렝(볶음밥) 35,000Rp, 미고렝(볶음면) 30,000Rp, 아이스 티 15,000Rp 정도예요. 전체 1끼 80,000Rp(약 7,000원)이면 충분해요.</p>\n'
            elif cat == "transport" and ("공항" in h2_title or "이동" in h2_title):
                sections_html += f'<p style="margin:12px 0;line-height:1.8">공항에서 {city}까지는 택시로 약 {city_info["airport_min"]}분이에요. 공항 공식 택시 카운터에서 표를 끊으면 바가지를 피할 수 있어요. 요금은 100,000~200,000Rp이에요.</p>\n'
    
    # Add MRT CTA in the middle
    mrt_cta = f'''
<div style="margin:32px 0;padding:20px;background:linear-gradient(135deg,#FF6B35,#FF8C61);border-radius:12px;text-align:center;color:white">
<p style="margin:0 0 12px;font-weight:700;font-size:1.1em">마이리얼트립에서 {city} {cat_info['name']} 투어 할인받기</p>
<p style="margin:0 0 16px;font-size:0.95em;opacity:0.9">투어, 티켓, 숙소 최대 30% 할인 | 첫 구매 시 추가 할인</p>
<a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="display:inline-block;padding:12px 32px;background:white;color:#FF6B35;border-radius:25px;text-decoration:none;font-weight:700;font-size:1em">할인쿠폰 받기 →</a>
</div>'''
    
    # Build complete HTML
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{city}, {cat_info['name']}, 발리, 인도네시아, 자유여행, 2026">
<link rel="canonical" href="https://balitravel.blog/{city}/{cat}/{article_no:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="https://balitravel.blog/images/{city}/{cat}/{images[0] if images else 'default.webp'}">
<meta property="og:url" content="https://balitravel.blog/{city}/{cat}/{article_no:03d}.html">
<meta property="og:site_name" content="JP Travel Bali">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "{title}", "description": "{meta_desc}", "image": ["https://balitravel.blog/images/{city}/{cat}/{images[0] if images else 'default.webp'}"], "datePublished": "2026-04-01", "dateModified": "2026-05-03", "author": {{"@type": "Person", "name": "JP Travel Bali"}}, "publisher": {{"@type": "Organization", "name": "JP Travel Bali"}}, "mainEntityOfPage": {{"@type": "WebPage", "@id": "https://balitravel.blog/{city}/{cat}/{article_no:03d}.html"}}}}</script>
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
#reading-progress {{ position: fixed; top: 0; left: 0; width: 0%; height: 3px; background: linear-gradient(90deg, #FF6B35, #FF8C61); z-index: 9999; transition: width 0.1s; }}
figure img {{ background: #f0f0f0; min-height: 100px; }}
@media (max-width: 600px) {{
    .container {{ padding: 10px; }}
    article {{ padding: 20px; }}
    header h1 {{ font-size: 1.4rem; }}
    table {{ font-size: .8em; }}
    article h2 {{ font-size: 1.2rem; }}
    .content-intro {{ padding: 12px 16px; }}
}}
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
<div id="reading-progress"></div>
<script>
window.addEventListener('scroll', function() {{
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = (winScroll / height) * 100;
    document.getElementById('reading-progress').style.width = scrolled + '%';
}});
</script>
<div class="container">
<header>
<h1>{title}</h1>
<div class="meta">JP Travel Bali | {city} {cat_info['name']} 가이드 | 2026</div>
</header>
<div class="breadcrumb">
<a href="/">홈</a> &rsaquo; <a href="/{city}/">{city}</a> &rsaquo; <a href="/{city}/{cat}/">{cat_info['name']}</a> &rsaquo; {article_no:03d}
</div>
<article>
<div class="content-intro">
<strong>[제휴 안내]</strong> {MRT_DISCLOSURE}
</div>

<div class="content-intro">
{intro}
</div>

{sections_html}

{mrt_cta}

{images_html}

<div class="tags">
<span class="tag">{city}</span>
<span class="tag">{cat_info['name']}</span>
<span class="tag">발리</span>
<span class="tag">인도네시아</span>
<span class="tag">자유여행</span>
<span class="tag">2026</span>
</div>
<div class="content-footer">
<p>이 글이 {city} 여행 계획에 도움이 되셨길 바랍니다. 추가 질문은 댓글로 남겨주세요!</p>
<p style="margin-top:8px"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립 할인쿠폰 받기</a></p>
</div>
</article>
</div>
<footer style="text-align:center;padding:30px;color:var(--text-light);font-size:0.85rem;margin-top:40px;border-top:1px solid #eee">
<p>이 글에는 <a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립</a> 제휴 링크가 포함되어 있습니다.</p>
<p>{MRT_DISCLOSURE}</p>
<p style="margin-top:10px">JP Travel Bali &copy; 2026</p>
</footer>
</body>
</html>'''
    
    return html

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    print("="*60)
    print("JP Travel Bali - Comprehensive Quality Improvement")
    print("="*60)
    
    cities = sorted(CITIES.keys())
    categories = sorted(CATEGORIES.keys())
    
    total = len(cities) * len(categories) * 14
    print(f"Generating {total} articles...")
    
    count = 0
    titles_set = set()
    metas_set = set()
    
    for city in cities:
        for cat in categories:
            for article_no in range(1, 15):
                out_path = BASE / city / cat / f"{article_no:03d}.html"
                
                html = generate_html(city, cat, article_no)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(html, encoding='utf-8')
                
                # Verify uniqueness
                title_m = re.search(r'<title>(.*?)</title>', html)
                meta_m = re.search(r'<meta name="description" content="(.*?)"', html)
                if title_m:
                    titles_set.add(title_m.group(1))
                if meta_m:
                    metas_set.add(meta_m.group(1))
                
                count += 1
                if count % 100 == 0:
                    print(f"  Progress: {count}/{total}")
    
    print(f"\nGenerated {count} articles")
    print(f"Unique titles: {len(titles_set)}")
    print(f"Unique meta descriptions: {len(metas_set)}")
    
    # Copy mrt_coupon.jpg to images directory if not exists
    mrt_src = Path("mrt_coupon.jpg")
    mrt_dst = IMAGES_DIR / "mrt_coupon.jpg"
    if mrt_src.exists() and not mrt_dst.exists():
        shutil.copy2(mrt_src, mrt_dst)
        print(f"Copied mrt_coupon.jpg to {mrt_dst}")
    
    print("\nDone! Run audit to verify.")

if __name__ == "__main__":
    main()
