#!/usr/bin/env python3
"""
발리 여행 블로그 빌드 시스템 v3
- 900개 HTML 페이지 생성 (11지역 × 6카테고리 × ~14페이지)
- 네이버 AI 검색(Cue:) 최적화
- 고유 콘텐츠 + 고유 제목
- 카테고리별 매핑 이미지 10장
- 마이리얼트립 쿠폰 하이퍼링크
- SEO 타이틀 + 메타 설명 중복 제거
"""

import os, re, json, random, hashlib
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent

try:
    from seo_titles import generate_seo_title, generate_meta_description, generate_keywords
    HAS_SEO = True
except ImportError:
    HAS_SEO = False

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

CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "🍜", "desc": "맛집 탐방"},
    "culture": {"name": "문화/사원", "icon": "🛕", "desc": "문화 체험"},
    "beach": {"name": "해변/서핑", "icon": "🏖️", "desc": "해변 액티비티"},
    "nature": {"name": "자연/모험", "icon": "🌿", "desc": "자연 탐방"},
    "shopping": {"name": "쇼핑/마사지", "icon": "🛍️", "desc": "쇼핑 & 힐링"},
    "transport": {"name": "여행/교통", "icon": "🚗", "desc": "이동 정보"},
}

# ============================================================
# 발리 지역별 상세 데이터 (11개 지역)
# ============================================================
BALI_DATA = {
    "우붓": {
        "description": "발리의 문화와 예술의 중심지",
        "intro_qa": [
            ("우붓 맛집 중 가장 추천하는 곳은?", "베벵길 오리구이(95,000루피아~)가 가성비 최고입니다. 예약 필수이고, 워르마 바비굴링(50,000루피아~)은 현지인도 줄서서 먹는 집이에요."),
            ("우붓 1일 예산은 얼마나 잡아야 하나요?", "예산형 260,000~500,000루피아(약 25,000~50,000원), 중급 950,000~2,500,000루피아(약 95,000~250,000원)입니다."),
            ("우붓에서 꼭 해야 할 체험은?", "테갈랑 라이스 테라스 산책 + 원숭이 숲 방문 + 우붓 아트 마켓 쇼핑이 필수 코스입니다."),
        ],
        "food": [
            {"name": "Bebek Bengil (Dirty Duck Diner)", "price": "95,000루피아~", "price_krw": "약 9,500원~", "tip": "우붓 대표 오리구이, 바삭한 크리스피덕이 시그니처. 예약 필수", "area": "우붓 시내", "must_try": "크리스피덕 세트"},
            {"name": "Locavore", "price": "점심 350,000루피아~", "price_krw": "약 35,000원~", "tip": "발리 최고의 파인다이닝, 2개월 전 예약 필요", "area": "우붓 시내", "must_try": "코스 요리"},
            {"name": "Warung Babi Guling Ibu Oka", "price": "50,000루피아~", "price_krw": "약 5,000원~", "tip": "우붓 대표 새끼돼지구이, 오전에 가야 sold out 안됨", "area": "우붓 궁전 근처", "must_try": "바비굴링 스페셜"},
            {"name": "Clear Cafe", "price": "음료 40,000~80,000루피아", "price_krw": "약 4,000~8,000원", "tip": "우붓 대표 카페, 강변 뷰가 환상적", "area": "캠프한 리지", "must_try": "스무디볼"},
            {"name": "Room 4 Dessert", "price": "디저트 120,000~200,000루피아", "price_krw": "약 12,000~20,000원", "tip": "발리 최고의 디저트 바, 예약 필수", "area": "우붓 시내", "must_try": "코스 디저트"},
            {"name": "Sayuri Healing Food", "price": "브런치 60,000~120,000루피아", "price_krw": "약 6,000~12,000원", "tip": "비건/채식 전문, 건강식 선호자에게 추천", "area": "우붓 시내", "must_try": "스무디볼"},
        ],
        "culture": [
            {"name": "타만 사라스와티 사원", "price": "무료 (기부금 10,000~20,000루피아)", "tip": "연못 위의 사원, 일몰 시간대 방문 추천", "area": "우붓 시내"},
            {"name": "우붓 원숭이 숲", "price": "입장료 80,000루피아", "tip": "원숭이가 많으니 소지품 주의. 오전에 가면 한적", "area": "우붓 시내"},
            {"name": "우붓 왕궁", "price": "무료", "tip": "저녁 전통 공연(7시) 추천, 입장료 100,000루피아", "area": "우붓 시내"},
            {"name": "아궁 라이 미술관", "price": "입장료 50,000루피아", "tip": "발리 전통 미술 컬렉션, 르마유르 미술관과 연계", "area": "우붓 시내"},
        ],
        "beach": [
            {"name": "우붓 강변 래프팅", "price": "250,000~400,000루피아", "tip": "아융강 래프팅, 2시간 코스. 초보자 가능", "area": "우붓 외곽"},
            {"name": "우붓 자연 수영장", "price": "50,000~100,000루피아", "tip": "알링킹 폭포 근처 천연 수영장", "area": "우붓 외곽"},
        ],
        "nature": [
            {"name": "테갈랑 라이스 테라스", "price": "입장료 15,000루피아", "tip": "새벽이나 오전에 가야 안개 없이 깨끗한 뷰", "area": "우붓 북쪽"},
            {"name": "알링킹 폭포", "price": "입장료 20,000루피아", "tip": "우붓에서 차로 30분, 계단 많으니 편한 신발 필수", "area": "우붓 외곽"},
            {"name": "뜨갈라랑 스윙", "price": "스윙 150,000~250,000루피아", "tip": "인생샷 명소, 오전에 가면 웨이팅 짧음", "area": "우붓 북쪽"},
            {"name": "캄포한 리지 산책", "price": "무료", "tip": "우붓 시내에서 도보 15분, 강변 절벽 코스", "area": "우붓 시내"},
        ],
        "shopping": [
            {"name": "우붓 아트 마켓", "price": "흥정 필수", "tip": "첫 가격의 30~50% 수준으로 흥정 가능. 오전에 가면 선택 폭 넓음", "area": "우붓 시내"},
            {"name": "우붓 몽키 포레스트 로드", "price": "다양", "tip": "기념품 숍 밀집 지역, 가격 비교 후 구매", "area": "우붓 시내"},
            {"name": "우붓 전통 마사지", "price": "80,000~150,000루피아/1시간", "tip": "발리 전통 마사지(Boreh) 추천", "area": "우붓 시내"},
        ],
        "transport": [
            {"name": "공항→우붓", "price": "300,000루피아 (차량 90분)", "tip": "그랩 또는 사전 예약 드라이버 추천"},
            {"name": "우붓 시내 이동", "price": "스쿠터 80,000루피아/일", "tip": "우붓은 교통체증 심하므로 오전 이동 추천"},
            {"name": "우붓→다른 지역", "price": "그랩 150,000~300,000루피아", "tip": "꾸까지 1시간, 스미냑까지 1시간 30분"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000루피아/1박", "mid": "풀빌라 500,000~1,500,000루피아/1박", "high": "알리라 우붓 3,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "우붓 외곽 락사강 협곡은 관광객이 거의 없어 인생샷 가능",
        "price_comparison": [
            {"item": "베벵길 오리구이", "local": "95,000Rp", "tour": "120,000Rp", "hotel": "180,000Rp"},
            {"item": "나시고렝", "local": "25,000Rp", "tour": "45,000Rp", "hotel": "80,000Rp"},
            {"item": "생맥주", "local": "35,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
            {"item": "마사지 (1시간)", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "250,000Rp"},
        ],
        "spots": ["우붓 원숭이 숲", "테갈랑 라이스 테라스", "우붓 아트 마켓", "타만 사라스와티 사원", "캄포한 리지"],
    },
    "스미냑": {
        "description": "발리의 트렌디한 비치 타운",
        "intro_qa": [
            ("스미냑 비치클럽 중 가장 추천하는 곳은?", "포테이토 헤드가 대표적이지만, 선셋 시간대는 2시간 전 가야 자리 잡아요. 음료 100,000~200,000루피아."),
            ("스미냑 가성비 맛집은?", "와룽니아(Warung Nia)에서 현지 음식 30,000~60,000루피아로 든든하게 먹을 수 있어요."),
            ("스미냑에서 교통비 절약하려면?", "그랩/고젝 추천. 스쿠터 렌트 80,000루피아/일이 가장 저렴하지만, 스미냑은 교통체증이 심해요."),
        ],
        "food": [
            {"name": "Potato Head Beach Club", "price": "음료 100,000~200,000루피아", "price_krw": "약 10,000~20,000원", "tip": "발리 대표 비치클럽, 선셋 시간대 2시간 전 도착 추천", "area": "스미냑 비치", "must_try": "칵테일 + 선셋"},
            {"name": "La Lucciola", "price": "파스타 150,000~250,000루피아", "price_krw": "약 15,000~25,000원", "tip": "해변 이탈리안 레스토랑, 분위기 최고", "area": "스미냑 비치", "must_try": "해산물 파스타"},
            {"name": "Warung Nia", "price": "현지 음식 30,000~60,000루피아", "price_krw": "약 3,000~6,000원", "tip": "가성비 최고의 로컬 맛집", "area": "스미냑 시내", "must_try": "나시캄푸르"},
            {"name": "Sisterfields", "price": "브런치 80,000~150,000루피아", "price_krw": "약 8,000~15,000원", "tip": "호주식 브런치 카페, 주말 웨이팅 있음", "area": "스미냑 시내", "must_try": "에그 베네딕트"},
            {"name": "Motel Mexicola", "price": "칵테일 80,000~150,000루피아", "price_krw": "약 8,000~15,000원", "tip": "멕시칸 분위기 바, 밤에는 파티 분위기", "area": "스미냑 시내", "must_try": "타코 + 마가리타"},
            {"name": "Sarong", "price": "메인 150,000~300,000루피아", "price_krw": "약 15,000~30,000원", "tip": "아시안 퓨전 파인다이닝, 예약 추천", "area": "스미냑 시내", "must_try": "아시안 타파스"},
        ],
        "culture": [
            {"name": "페티탕겟 사원", "price": "무료 (기부금)", "tip": "스미냑 비치 근처 해변 사원, 선셋 시간대 추천", "area": "스미냑 비치"},
            {"name": "스미냑 빌리지", "price": "무료", "tip": "전통 발리 마을 산책, 현지 예술가 공방 방문", "area": "스미냑 시내"},
        ],
        "beach": [
            {"name": "더블식스 비치", "price": "무료", "tip": "스미냑 대표 해변, 선셋 포토스팟. 비치클럽 많음", "area": "스미냑"},
            {"name": "스미냑 비치", "price": "무료", "tip": "서핑 초보자 강습 가능, 150,000~250,000루피아", "area": "스미냑"},
            {"name": "쿠데타 비치클럽", "price": "음료 80,000~150,000루피아", "tip": "선베드 무료, 최소 음료 1잔 주문", "area": "스미냑 비치"},
        ],
        "nature": [
            {"name": "스미냑 해변 산책로", "price": "무료", "tip": "더블식스에서 포테이토 헤드까지 해변 산책, 약 2km", "area": "스미냑"},
        ],
        "shopping": [
            {"name": "스미냑 빌리지 쇼핑", "price": "다양", "tip": "부티크숍, 디자이너숍 밀집. 세일 시즌 11~12월", "area": "스미냑 시내"},
            {"name": "스미냑 스파", "price": "150,000~400,000루피아/1시간", "tip": "프리미엄 스파 추천: Spring Spa, Bodyworks", "area": "스미냑 시내"},
            {"name": "Seminyak Square", "price": "다양", "tip": "쇼핑몰 + 레스토랑 복합 공간", "area": "스미냑 시내"},
        ],
        "transport": [
            {"name": "공항→스미냑", "price": "150,000루피아 (차량 30분)", "tip": "그랩 추천, 미터 택시도 가능"},
            {"name": "스미냑 시내 이동", "price": "도보 가능", "tip": "스미냑은 교통체증 심하므로 도보 또는 스쿠터 추천"},
        ],
        "hotels": {"budget": "게스트하우스 150,000~300,000루피아/1박", "mid": "부티크 호텔 500,000~1,500,000루피아/1박", "high": "위 발리 5,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "더블식스 비치 끝자락은 관광객 적고 선셋 포토스팟으로 최고",
        "price_comparison": [
            {"item": "비치클럽 음료", "local": "100,000Rp", "tour": "150,000Rp", "hotel": "200,000Rp"},
            {"item": "파스타", "local": "150,000Rp", "tour": "180,000Rp", "hotel": "250,000Rp"},
            {"item": "로컬 음식", "local": "30,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
            {"item": "마사지 (1시간)", "local": "80,000Rp", "tour": "150,000Rp", "hotel": "300,000Rp"},
        ],
        "spots": ["스미냑 비치", "Potato Head", "스미냑 빌리지", "페티탕겟 사원", "더블식스 비치"],
    },
    "꾸따": {
        "description": "발리 최초의 관광지, 서핑의 성지",
        "intro_qa": [
            ("꾸따에서 서핑 강습 받으려면?", "꾸따 비치에서 1회 강습 150,000~250,000루피아(약 15,000~25,000원). 보드 포함 가격이에요."),
            ("꾸따 공항에서 가까운 맛집은?", "와룽무라(Warung Murah)에서 나시고렝 20,000~35,000루피아. 공항에서 차로 15분이에요."),
            ("꾸따 쇼핑몰 추천은?", "비치워크 쇼핑몰이 가장 크고, Discovery Mall은 로컬 브랜드 위주예요."),
        ],
        "food": [
            {"name": "Warung Murah", "price": "나시고렝 20,000~35,000루피아", "price_krw": "약 2,000~3,500원", "tip": "꾸따 대표 저렴한 로컬 맛집, 점심시간 웨이팅", "area": "꾸따 시내", "must_try": "나시고렝 스페셜"},
            {"name": "Made's Warung", "price": "현지 음식 40,000~80,000루피아", "price_krw": "약 4,000~8,000원", "tip": "1969년부터 운영된 전통 맛집", "area": "꾸따 시내", "must_try": "나시짬뿌르"},
            {"name": "Hard Rock Cafe Bali", "price": "버거 120,000~180,000루피아", "price_krw": "약 12,000~18,000원", "tip": "꾸따 비치 앞, 라이브 음악", "area": "꾸따 비치", "must_try": "레전더리 버거"},
            {"name": "Poppies Restaurant", "price": "파스타 80,000~150,000루피아", "price_krw": "약 8,000~15,000원", "tip": "정원 분위기의 레스토랑", "area": "팝피스 레인", "must_try": "해산물 파스타"},
            {"name": "Bamboo Corner", "price": "현지 음식 25,000~50,000루피아", "price_krw": "약 2,500~5,000원", "tip": "가성비 로컬 맛집, 대나무 인테리어", "area": "꾸따 시내", "must_try": "나시캄푸르"},
        ],
        "culture": [
            {"name": "꾸따 아트 마켓", "price": "무료 입장", "tip": "기념품 쇼핑 명소, 흥정 필수", "area": "꾸따 시내"},
            {"name": " Waterbomb Bali", "price": "입장료 535,000루피아", "tip": "발리 최대 워터파크, 가족 여행객에게 추천", "area": "꾸따"},
        ],
        "beach": [
            {"name": "꾸따 비치", "price": "무료", "tip": "서핑 강습 가능, 선셋 포토스팟", "area": "꾸따"},
            {"name": "레기안 비치", "price": "무료", "tip": "꾸보다 한적한 해변, 서핑 포인트", "area": "레기안"},
            {"name": "꾸따 서핑 강습", "price": "150,000~250,000루피아/1회", "tip": "보드 포함, 2시간 강습. 초보자 가능", "area": "꾸따 비치"},
        ],
        "nature": [],
        "shopping": [
            {"name": "비치워크 쇼핑몰", "price": "다양", "tip": "꾸따 최대 쇼핑몰, 브랜드숍+로컬숍", "area": "꾸따 비치"},
            {"name": "Discovery Mall", "price": "다양", "tip": "로컬 브랜드 위주, 가격 적절", "area": "꾸따"},
            {"name": "꾸따 마사지", "price": "60,000~100,000루피아/1시간", "tip": "해변 마사지 가게가 가장 저렴", "area": "꾸따 비치"},
        ],
        "transport": [
            {"name": "공항→꾸따", "price": "100,000루피아 (차량 15분)", "tip": "공항에서 가장 가까운 관광지"},
            {"name": "꾸따 시내 이동", "price": "도보 가능", "tip": "꾸따는 도보 이동 가능"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000루피아/1박", "mid": "비치 호텔 300,000~800,000루피아/1박", "high": "하드락 호텔 1,500,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "꾸따 북쪽 레기안 비치는 꾸보다 한적하고 서핑 포인트도 좋아요",
        "price_comparison": [
            {"item": "서핑 강습 (1회)", "local": "150,000Rp", "tour": "250,000Rp", "hotel": "350,000Rp"},
            {"item": "나시고렝", "local": "20,000Rp", "tour": "40,000Rp", "hotel": "70,000Rp"},
            {"item": "맥주", "local": "35,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
            {"item": "마사지 (1시간)", "local": "60,000Rp", "tour": "100,000Rp", "hotel": "200,000Rp"},
        ],
        "spots": ["꾸따 비치", "워터밤 파크", "비치워크 쇼핑몰", "꾸따 아트 마켓", "서핑 포인트"],
    },
    "사누르": {
        "description": "발리의 조용한 해변 휴양지",
        "intro_qa": [
            ("사누르 일출 명소는?", "사누르 비치 동쪽 끝자락이 일출 포인트. 오전 5:30까지 가야 해요."),
            ("사누르 가성비 맛집은?", "와룽막벵(Warung Mak Beng) 생선튀김 세트 35,000루피아. 줄 서서 먹는 집이에요."),
            ("사누르에서 자전거 대여 가능한가요?", "네, 50,000루피아/일. 해변 따라 자전거 코스가 5km 정도 이어져 있어요."),
        ],
        "food": [
            {"name": "Massimo", "price": "파스타 80,000~150,000루피아", "price_krw": "약 8,000~15,000원", "tip": "사누르 대표 이탈리안, 예약 추천", "area": "사누르 비치", "must_try": "트러플 파스타"},
            {"name": "Warung Mak Beng", "price": "생선튀김 세트 35,000루피아", "price_krw": "약 3,500원", "tip": "사누르 대표 로컬 맛집, 줄 서서 먹는 집", "area": "사누르 시내", "must_try": "생선튀김 세트"},
            {"name": "The Glass House", "price": "브런치 60,000~120,000루피아", "price_krw": "약 6,000~12,000원", "tip": "정원 분위기 카페", "area": "사누르 시내", "must_try": "아보카도 토스트"},
            {"name": "Kayuputih Restaurant", "price": "해산물 100,000~200,000루피아", "price_krw": "약 10,000~20,000원", "tip": "해변 해산물 레스토랑", "area": "사누르 비치", "must_try": "그릴 피쉬"},
        ],
        "culture": [
            {"name": "르 마유르 박물관", "price": "입장료 50,000루피아", "tip": "발리 현대 미술, 블랑크 미술관과 연계", "area": "사누르"},
            {"name": "블랑크 미술관", "price": "입장료 100,000루피아", "tip": "아르카 블랑크 작품 전시", "area": "사누르"},
        ],
        "beach": [
            {"name": "사누르 비치", "price": "무료", "tip": "일출 명소, 자전거 코스", "area": "사누르"},
            {"name": "사누르 자전거 코스", "price": "자전거 대여 50,000루피아/일", "tip": "해변 따라 5km, 평탄한 코스", "area": "사누르"},
        ],
        "nature": [],
        "shopping": [
            {"name": "사누르 아트 마켓", "price": "다양", "tip": "기념품 쇼핑, 흥정 필수", "area": "사누르"},
            {"name": "사누르 나이트 마켓", "price": "20,000~50,000루피아", "tip": "저녁 6시부터 로컬 음식 저렴하게", "area": "사누르"},
        ],
        "transport": [
            {"name": "공항→사누르", "price": "150,000루피아 (차량 30분)", "tip": "그랩 추천"},
            {"name": "사누르 시내 이동", "price": "자전거 50,000루피아/일", "tip": "자전거로 이동하기 좋음"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000루피아/1박", "mid": "비치 리조트 500,000~1,500,000루피아/1박", "high": "그랜드 하얏트 3,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "사누르 나이트 마켓은 저녁 6시부터 로컬 음식을 20,000루피아대로 즐길 수 있어요",
        "price_comparison": [
            {"item": "생선튀김 세트", "local": "35,000Rp", "tour": "55,000Rp", "hotel": "90,000Rp"},
            {"item": "파스타", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "180,000Rp"},
            {"item": "자전거 대여 (1일)", "local": "50,000Rp", "tour": "80,000Rp", "hotel": "120,000Rp"},
            {"item": "마사지 (1시간)", "local": "70,000Rp", "tour": "120,000Rp", "hotel": "250,000Rp"},
        ],
        "spots": ["사누르 비치", "사누르 아트 마켓", "발리 비치 골프 코스", "르 마유르 박물관", "사누르 나이트 마켓"],
    },
    "누사두아": {
        "description": "발리의 프리미엄 리조트 지구",
        "intro_qa": [
            ("누사두아 리조트 추천은?", "뮬리아 리조트가 럭셔리 끝판왕이지만, 그랜드하얏트가 가성비 최고예요."),
            ("누사두아 블로우홀 가는법?", "누사두아 비치에서 도보 10분. 입장료 20,000루피아. 파도 칠 때 물기둥이 장관이에요."),
            ("누사두아 가족 여행 추천 코스는?", "워터밤 파크(오전) → 리조트 수영장(오후) → 블로우홀(일몰) 코스 추천."),
        ],
        "food": [
            {"name": "Bumbu Bali", "price": "발리 전통 요리 80,000~150,000루피아", "price_krw": "약 8,000~15,000원", "tip": "발리 전통 요리 전문점, 쿠킹클래스도 운영", "area": "누사두아", "must_try": "발리 정식 코스"},
            {"name": "Kayuputih at Grand Hyatt", "price": "해산물 200,000~400,000루피아", "price_krw": "약 20,000~40,000원", "tip": "고급 해산물 레스토랑", "area": "누사두아", "must_try": "시푸드 플래터"},
            {"name": "Warung Dobiel", "price": "나시고렝 25,000~40,000루피아", "price_krw": "약 2,500~4,000원", "tip": "누사두아 근처 로컬 맛집", "area": "누사두아", "must_try": "나시고렝"},
            {"name": "The Cafe at Mulia", "price": "뷔페 500,000루피아~", "price_krw": "약 50,000원~", "tip": "발리 최고급 뷔페", "area": "뮬리아 리조트", "must_try": "디너 뷔페"},
        ],
        "culture": [
            {"name": "파라다이스 극장", "price": "공연 150,000~300,000루피아", "tip": "발리 전통 공연, 예약 추천", "area": "누사두아"},
        ],
        "beach": [
            {"name": "누사두아 비치", "price": "무료", "tip": "깨끗한 백사장, 리조트 프라이빗 비치", "area": "누사두아"},
            {"name": "워터블로우", "price": "입장료 20,000루피아", "tip": "파도 칠 때 물기둥 장관, 일몰 시간대 추천", "area": "누사두아"},
            {"name": "누사두아 스노클링", "price": "100,000~200,000루피아", "tip": "누사두아 비치 동쪽 끝 포인트", "area": "누사두아"},
        ],
        "nature": [],
        "shopping": [
            {"name": "발리 컬렉션 쇼핑몰", "price": "다양", "tip": "누사두아 유일의 쇼핑몰, 로컬 브랜드 위주", "area": "누사두아"},
            {"name": "누사두아 스파", "price": "200,000~500,000루피아/1시간", "tip": "리조트 내 스파 추천", "area": "누사두아"},
        ],
        "transport": [
            {"name": "공항→누사두아", "price": "200,000루피아 (차량 40분)", "tip": "리조트 셔틀 또는 그랩"},
            {"name": "누사두아 시내 이동", "price": "리조트 셔틀 무료", "tip": "리조트 내에서 대부분 해결 가능"},
        ],
        "hotels": {"budget": "게스트하우스 150,000~300,000루피아/1박", "mid": "리조트 800,000~2,000,000루피아/1박", "high": "뮬리아 리조트 5,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "누사두아 비치 동쪽 끝은 스노클링 포인트로 관광객이 거의 없어요",
        "price_comparison": [
            {"item": "발리 정식", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "200,000Rp"},
            {"item": "나시고렝", "local": "25,000Rp", "tour": "45,000Rp", "hotel": "80,000Rp"},
            {"item": "뷔페 디너", "local": "500,000Rp", "tour": "600,000Rp", "hotel": "800,000Rp"},
            {"item": "마사지 (1시간)", "local": "100,000Rp", "tour": "180,000Rp", "hotel": "350,000Rp"},
        ],
        "spots": ["누사두아 비치", "발리 컬렉션 쇼핑몰", "워터밤 파크", "블로우 홀", "파라다이스 극장"],
    },
    "울루와뚜": {
        "description": "절벽 위의 서핑과 사원의 도시",
        "intro_qa": [
            ("울루와뚜 사원 케착춤 시간은?", "오후 6시부터 1시간. 입장료 50,000루피아. 일몰 시간대라 분위기 최고예요."),
            ("울루와뚜 비치클럽 추천은?", "싱글핀(Single Fin)이 대표적. 음료 80,000~150,000루피아. 절벽 위 선셋 뷰가 환상적이에요."),
            ("울루와뚜 서핑 포인트는?", "울루와뚜 비치와 블루포인트 비치. 중급자 이상 추천. 강습 200,000~300,000루피아."),
        ],
        "food": [
            {"name": "Single Fin", "price": "음료 80,000~150,000루피아", "price_krw": "약 8,000~15,000원", "tip": "울루와뚜 대표 비치클럽, 선셋 명소", "area": "울루와뚜 절벽", "must_try": "칵테일 + 선셋"},
            {"name": "Warung Sego Njamoer", "price": "나시고렝 25,000~40,000루피아", "price_krw": "약 2,500~4,000원", "tip": "로컬 맛집", "area": "울루와뚜", "must_try": "나시고렝"},
            {"name": "Sundara Beach Club", "price": "칵테일 120,000~200,000루피아", "price_krw": "약 12,000~20,000원", "tip": "포시즌스 리조트 내 비치클럽", "area": "짐바란", "must_try": "시그니처 칵테일"},
            {"name": "Rock Bar", "price": "칵테일 150,000~250,000루피아", "price_krw": "약 15,000~25,000원", "tip": "절벽 위 바, 발리 최고의 야경", "area": "짐바란", "must_try": "록바 시그니처"},
        ],
        "culture": [
            {"name": "울루와뚜 사원", "price": "입장료 50,000루피아", "tip": "절벽 위 해양 사원, 케착춤 공연 필수 관람", "area": "울루와뚜"},
            {"name": "케착춤 공연", "price": "입장료에 포함", "tip": "오후 6시, 일몰과 함께 보는 케착춤", "area": "울루와뚜 사원"},
        ],
        "beach": [
            {"name": "울루와뚜 비치", "price": "무료", "tip": "절벽 아래 숨겨진 비치, 계단 내려가야 함", "area": "울루와뚜"},
            {"name": "블루포인트 비치", "price": "무료", "tip": "서핑 포인트, 중급자 이상", "area": "울루와뚜"},
            {"name": "판다와 비치", "price": "입장료 10,000루피아", "tip": "절벽 아래 숨겨진 비치, 관광객 적고 물 맑아요", "area": "울루와뚜"},
            {"name": "짐바란 비치", "price": "무료", "tip": "해산물 BBQ 명소, 선셋 시간대 추천", "area": "짐바란"},
        ],
        "nature": [],
        "shopping": [
            {"name": "울루와두 기념품 가게", "price": "다양", "tip": "사원 입구 기념품 숍, 흥정 필수", "area": "울루와뚜"},
        ],
        "transport": [
            {"name": "공항→울루와뚜", "price": "200,000루피아 (차량 45분)", "tip": "절벽 지역이라 스쿠터 주의"},
            {"name": "울루와뚜 시내 이동", "price": "스쿠터 80,000루피아/일", "tip": "그랩 80,000~130,000루피아"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000루피아/1박", "mid": "클리프 리조트 500,000~1,500,000루피아/1박", "high": "아야나 리조트 4,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "판다와 비치는 절벽 아래 숨겨진 비치로 관광객 적고 물 맑아요",
        "price_comparison": [
            {"item": "비치클럽 음료", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "200,000Rp"},
            {"item": "나시고렝", "local": "25,000Rp", "tour": "45,000Rp", "hotel": "80,000Rp"},
            {"item": "서핑 강습", "local": "200,000Rp", "tour": "300,000Rp", "hotel": "450,000Rp"},
            {"item": "마사지 (1시간)", "local": "80,000Rp", "tour": "130,000Rp", "hotel": "250,000Rp"},
        ],
        "spots": ["울루와뚜 사원", "울루와뚜 비치", "짐바란 비치", "블루포인트 비치", "판다와 비치"],
    },
    "짠디다사": {
        "description": "발리 동부의 조용한 해변 마을",
        "intro_qa": [
            ("짠디다사 다이빙 포인트는?", "아메드 비치와 빌리멜루크. 오픈워터 기준 500,000~800,000루피아."),
            ("짠디다사 조용한 해변 추천?", "짠디다사 비치 자체가 한적해요. 스미냑/꾸따 대비 관광객 10% 수준."),
            ("짠디다사 가는법?", "공항에서 차량 90분, 350,000루피아. 동부 발리 코스로 연결하면 좋아요."),
        ],
        "food": [
            {"name": "Warung Padang Kecag", "price": "나시파당 20,000~35,000루피아", "price_krw": "약 2,000~3,500원", "tip": "로컬 파당 맛집", "area": "짠디다사", "must_try": "나시파당"},
            {"name": "Villa Puri Purnama", "price": "해산물 60,000~120,000루피아", "price_krw": "약 6,000~12,000원", "tip": "해변 해산물 레스토랑", "area": "짠디다사 비치", "must_try": "그릴 피쉬"},
            {"name": "Warung Subak", "price": "발리 전통 요리 30,000~60,000루피아", "price_krw": "약 3,000~6,000원", "tip": "논 뷰 맛집", "area": "짠디다사", "must_try": "발리 정식"},
        ],
        "culture": [
            {"name": "베사키 사원", "price": "입장료 60,000루피아", "tip": "발리 어머니 사원, 아궁 화산 근처", "area": "짠디다사"},
            {"name": "티르타강가", "price": "입장료 30,000루피아", "tip": "정화의 샘, 현지인 성지", "area": "짠디다사"},
        ],
        "beach": [
            {"name": "짠디다사 비치", "price": "무료", "tip": "한적한 해변, 관광객 적음", "area": "짠디다사"},
            {"name": "아메드 비치", "price": "무료", "tip": "다이빙/스노클링 포인트", "area": "아메드"},
        ],
        "nature": [
            {"name": "아꿍 화산", "price": "입장료 30,000루피아", "tip": "트레킹 코스, 가이드 추천", "area": "짠디다사"},
        ],
        "shopping": [
            {"name": "짠디다사 로컬 마켓", "price": "다양", "tip": "소규모 로컬 마켓", "area": "짠디다사"},
        ],
        "transport": [
            {"name": "공항→짠디다사", "price": "350,000루피아 (차량 90분)", "tip": "동부 발리 코스로 연결"},
            {"name": "짠디다사 시내 이동", "price": "스쿠터 70,000루피아/일", "tip": "발리 동부는 관광객 적어 조용"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000루피아/1박", "mid": "비치 방갈로 300,000~800,000루피아/1박", "high": "아메드 비치 리조트 1,500,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "티르타강가 '정화의 샘'은 현지인만 아는 숨겨진 성지",
        "price_comparison": [
            {"item": "나시파당", "local": "20,000Rp", "tour": "40,000Rp", "hotel": "70,000Rp"},
            {"item": "해산물", "local": "60,000Rp", "tour": "100,000Rp", "hotel": "160,000Rp"},
            {"item": "다이빙 (1회)", "local": "500,000Rp", "tour": "700,000Rp", "hotel": "900,000Rp"},
            {"item": "마사지 (1시간)", "local": "60,000Rp", "tour": "100,000Rp", "hotel": "180,000Rp"},
        ],
        "spots": ["짠디다사 비치", "아꿍 화산", "베사키 사원", "티르타강가", "아메드 비치"],
    },
    "로비나": {
        "description": "발리 북부의 조용한 해변, 돌고래 관찰",
        "intro_qa": [
            ("로비나 돌고래투어 가격은?", "새벽 6시 출발, 150,000~200,000루피아(약 15,000~20,000원). 보트 포함 가격이에요."),
            ("로비나 가는법?", "공항에서 차량 3시간, 500,000루피아. 1박 추천. 반자르 온천과 연계하면 좋아요."),
            ("로비나 숙소 추천?", "게스트하우스 80,000~150,000루피아. 해변 바로 앞 방갈로가 분위기 최고예요."),
        ],
        "food": [
            {"name": "Warung Orange", "price": "해산물 40,000~80,000루피아", "price_krw": "약 4,000~8,000원", "tip": "로비나 대표 해산물 맛집", "area": "로비나 비치", "must_try": "그릴 피쉬"},
            {"name": "Warung Bambu Pemaron", "price": "발리 요리 30,000~60,000루피아", "price_krw": "약 3,000~6,000원", "tip": "대나무 통발 요리", "area": "로비나", "must_try": "발리 정식"},
            {"name": "Spaghetti Bar", "price": "파스타 50,000~80,000루피아", "price_krw": "약 5,000~8,000원", "tip": "이탈리안 맛집", "area": "로비나", "must_try": "해산물 파스타"},
        ],
        "culture": [
            {"name": "브둘루 사원", "price": "입장료 20,000루피아", "tip": "로비나 근처 고대 사원", "area": "로비나"},
        ],
        "beach": [
            {"name": "로비나 비치", "price": "무료", "tip": "돌고래 관찰 포인트, 새벽 투어 추천", "area": "로비나"},
            {"name": "돌고래 투어", "price": "150,000~200,000루피아", "tip": "새벽 6시 출발, 보트 포함", "area": "로비나"},
        ],
        "nature": [
            {"name": "반자르 온천", "price": "입장료 20,000루피아", "tip": "천연 온천수, 관광객 적음", "area": "반자르"},
            {"name": "기트기트 폭포", "price": "입장료 20,000루피아", "tip": "로비나에서 차로 30분", "area": "로비나 외곽"},
        ],
        "shopping": [],
        "transport": [
            {"name": "공항→로비나", "price": "500,000루피아 (차량 3시간)", "tip": "발리 북부는 거리가 멀므로 1박 추천"},
            {"name": "로비나 시내 이동", "price": "스쿠터 70,000루피아/일", "tip": "그랩 200,000~300,000루피아"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000루피아/1박", "mid": "비치 방갈로 200,000~500,000루피아/1박", "high": "로비나 비치 리조트 1,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "반자르 온천은 관광객 적고 천연 온천수로 무료 족욕 가능",
        "price_comparison": [
            {"item": "돌고래투어", "local": "150,000Rp", "tour": "250,000Rp", "hotel": "350,000Rp"},
            {"item": "해산물", "local": "40,000Rp", "tour": "70,000Rp", "hotel": "120,000Rp"},
            {"item": "반자르 온천", "local": "20,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
            {"item": "마사지 (1시간)", "local": "60,000Rp", "tour": "100,000Rp", "hotel": "180,000Rp"},
        ],
        "spots": ["로비나 비치 (돌고래 투어)", "반자르 온천", "기트기트 폭포", "발리 국립공원", "브둘루 사원"],
    },
    "킨타마니": {
        "description": "발리 북부의 화산 지대",
        "intro_qa": [
            ("킨타마니 바투르 일출 트레킹 가격은?", "새벽 2시 출발, 350,000~500,000루피아(약 35,000~50,000원). 가이드 포함."),
            ("킨타마니 뷔페 추천은?", "바투르 사리 레스토랑 뷔페 100,000~150,000루피아. 화산 뷰가 환상적이에요."),
            ("킨타마니 가는법?", "공항에서 차량 2시간, 400,000루피아. 새벽 출발 추천(일출 포인트)."),
        ],
        "food": [
            {"name": "Batur Sari Restaurant", "price": "뷔페 100,000~150,000루피아", "price_krw": "약 10,000~15,000원", "tip": "바투르 화산 뷰 뷔페", "area": "킨타마니", "must_try": "발리 정식 뷔페"},
            {"name": "Warung Crispy", "price": "현지 음식 30,000~50,000루피아", "price_krw": "약 3,000~5,000원", "tip": "화산 뷰 로컬 맛집", "area": "킨타마니", "must_try": "크리스피 덕"},
        ],
        "culture": [
            {"name": "뜨리뜨 에מפק 사원", "price": "입장료 60,000루피아", "tip": "킨타마니 대표 사원", "area": "킨타마니"},
        ],
        "beach": [],
        "nature": [
            {"name": "바투르 화산 일출 트레킹", "price": "350,000~500,000루피아", "tip": "새벽 2시 출발, 가이드 포함. 난이도 중간", "area": "킨타마니"},
            {"name": "바투르 호수", "price": "무료", "tip": "화산 칼데라 호수, 카약 투어 가능", "area": "킨타마니"},
            {"name": "킨타마니 전망대", "price": "무료", "tip": "화산+호수 동시 조망 포인트", "area": "킨타마니"},
        ],
        "shopping": [],
        "transport": [
            {"name": "공항→킨타마니", "price": "400,000루피아 (차량 2시간)", "tip": "새벽 출발 추천 (일출 포인트)"},
            {"name": "킨타마니 시내 이동", "price": "차량 이동 필수", "tip": "그랩 150,000~250,000루피아"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000루피아/1박", "mid": "화산 뷰 리조트 400,000~1,000,000루피아/1박", "high": "킨타마니 리조트 2,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "바투르 호수 남쪽은 관광객 없고 카약 타기 좋은 포인트",
        "price_comparison": [
            {"item": "뷔페", "local": "100,000Rp", "tour": "150,000Rp", "hotel": "200,000Rp"},
            {"item": "일출 트레킹", "local": "350,000Rp", "tour": "500,000Rp", "hotel": "700,000Rp"},
            {"item": "로컬 음식", "local": "30,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
        ],
        "spots": ["바투르 화산", "바투르 호수", "킨타마니 전망대", "뜨걀라랑 라이스 테라스", "뜨리뜨 에פק 사원"],
    },
    "타나롯": {
        "description": "바다 위 사원으로 유명한 발리의 상징",
        "intro_qa": [
            ("타나롯 사원 입장료는?", "성인 60,000루피아(약 6,000원). 일몰 시간대 방문 추천."),
            ("타나롯 가는법?", "공항에서 차량 90분, 250,000루피아. 우붓에서 40분이에요."),
            ("타나롯 근처 맛집은?", "와루테닥에서 나시캄푸르 30,000~50,000루피아. 사원 뷰 레스토랑도 있어요."),
        ],
        "food": [
            {"name": "Warung Tegak", "price": "나시 캄푸르 30,000~50,000루피아", "price_krw": "약 3,000~5,000원", "tip": "타나롯 근처 로컬 맛집", "area": "타나롯", "must_try": "나시캄푸르"},
            {"name": "Tanah Lot Restaurant", "price": "발리 요리 60,000~120,000루피아", "price_krw": "약 6,000~12,000원", "tip": "타나롯 사원 뷰 레스토랑", "area": "타나롯", "must_try": "발리 정식"},
        ],
        "culture": [
            {"name": "타나롯 사원", "price": "입장료 60,000루피아", "tip": "바다 위 해양 사원, 일몰 시간대 추천", "area": "타나롯"},
            {"name": "바투 볼롱 사원", "price": "입장료 포함", "tip": "타나롯보다 한적, 일몰 뷰 더 좋음", "area": "타나롯"},
        ],
        "beach": [
            {"name": "타나롯 해변", "price": "무료", "tip": "사원 주변 해변 산책", "area": "타나롯"},
        ],
        "nature": [
            {"name": "잘란 라이스 테라스", "price": "무료", "tip": "타나롯 근처 아름다운 논밭", "area": "타나롯"},
        ],
        "shopping": [
            {"name": "타나롯 시장", "price": "다양", "tip": "사원 입구 기념품 시장", "area": "타나롯"},
        ],
        "transport": [
            {"name": "공항→타나롯", "price": "250,000루피아 (차량 90분)", "tip": "일몰 시간대 방문 추천"},
            {"name": "타나롯 시내 이동", "price": "차량 이동 추천", "tip": "그랩 100,000~150,000루피아"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000루피아/1박", "mid": "리조트 500,000~1,500,000루피아/1박", "high": "아야나 리조트 4,000,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "바투 볼롱 사원은 타나롯보다 한적하고 일몰 뷰가 더 좋아요",
        "price_comparison": [
            {"item": "사원 입장료", "local": "60,000Rp", "tour": "80,000Rp", "hotel": "100,000Rp"},
            {"item": "나시캄푸르", "local": "30,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
            {"item": "발리 정식", "local": "60,000Rp", "tour": "90,000Rp", "hotel": "150,000Rp"},
        ],
        "spots": ["타나롯 사원", "일몰 포인트", "바투 볼롱 사원", "잘란 라이스 테라스", "타나롯 시장"],
    },
    "베두굴": {
        "description": "발리 중부의 고원 도시",
        "intro_qa": [
            ("베두굴 울룬다누 사원 입장료는?", "성인 50,000루피아(약 5,000원). 오전 안개가 걷히는 9시 이후 방문 추천."),
            ("베두굴 고원 날씨는?", "해발 1,500m라 연평균 20도. 우기엔 15도까지 내려가니 겉옷 필수예요."),
            ("베두굴 가는법?", "공항에서 차량 2시간, 350,000루피아. 우붓에서 1시간 30분이에요."),
        ],
        "food": [
            {"name": "Warung Classic", "price": "현지 음식 25,000~45,000루피아", "price_krw": "약 2,500~4,500원", "tip": "베두굴 대표 로컬 맛집", "area": "베두굴", "must_try": "나시고렝"},
            {"name": "Lakeview Restaurant", "price": "발리 요리 50,000~100,000루피아", "price_krw": "약 5,000~10,000원", "tip": "브라탄 호수 뷰", "area": "브라탄 호수", "must_try": "발리 정식"},
        ],
        "culture": [
            {"name": "울룬 다누 브라탄 사원", "price": "입장료 50,000루피아", "tip": "호수 위 사원, 오전 9시 이후 방문 추천", "area": "베두굴"},
        ],
        "beach": [],
        "nature": [
            {"name": "브라탄 호수", "price": "무료", "tip": "고원 호수, 보트 투어 가능", "area": "베두굴"},
            {"name": "발리 보타닉 가든", "price": "입장료 20,000루피아", "tip": "열대 식물원, 관광객 거의 없음", "area": "베두굴"},
            {"name": "베두굴 전통 시장", "price": "무료", "tip": "딸기 농장 + 전통 시장", "area": "베두굴"},
        ],
        "shopping": [
            {"name": "베두굴 전통 시장", "price": "다양", "tip": "딸기, 채소, 기념품", "area": "베두굴"},
            {"name": "딸기 농장 체험", "price": "50,000~100,000루피아", "tip": "딸기 따기 체험 + 시식", "area": "베두굴"},
        ],
        "transport": [
            {"name": "공항→베두굴", "price": "350,000루피아 (차량 2시간)", "tip": "고원 지대라 서늘함"},
            {"name": "베두굴 시내 이동", "price": "차량 이동 추천", "tip": "그랩 130,000~200,000루피아"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000루피아/1박", "mid": "고원 리조트 300,000~800,000루피아/1박", "high": "문 레이크 호텔 1,500,000루피아~/1박"},
        "best_season": "4~10월 (건기)",
        "hidden_gem": "발리 보타닉 가든은 관광객 거의 없고 열대 식물원 산책 코스가 좋아요",
        "price_comparison": [
            {"item": "사원 입장료", "local": "50,000Rp", "tour": "70,000Rp", "hotel": "100,000Rp"},
            {"item": "로컬 음식", "local": "25,000Rp", "tour": "45,000Rp", "hotel": "80,000Rp"},
            {"item": "식물원 입장료", "local": "20,000Rp", "tour": "30,000Rp", "hotel": "50,000Rp"},
        ],
        "spots": ["울룬 다누 브라탄 사원", "브라탄 호수", "발리 보타닉 가든", "몽키 포레스트", "베두굴 전통 시장"],
    },
}

# 카테고리별 추가 콘텐츠 템플릿 (페이지 변형용)
CATEGORY_EXTRA_CONTENT = {
    "food": {
        "tips": [
            "현지 음식은 위생 상태를 꼭 확인하세요. 사람이 많은 곳이 신선합니다.",
            "발리 음식은 대부분 매운 편이에요. 못 먹으면 'tidak pedas'라고 말하세요.",
            "팁 문화는 필수는 아니지만, 서비스 좋으면 10,000~20,000루피아 남기면 좋아요.",
            "식수는 반드시 생수를 사서 마시세요. 수돗물은 마시면 안 됩니다.",
            "아침 식사는 호텔 조식이 가성비 최고예요. 대부분 포함이니 꼭 이용하세요.",
            "와룽(Warung)은 현지 로컬 식당이에요. 가격이 매우 저렴하고 맛도 좋습니다.",
            "발리 커피는 세계적으로 유명해요. 코피 루왁 체험 추천합니다.",
            "야시장 음식은 가성비 최고! 꾸따/사누르 야시장에서 20,000루피아로 배부르게 먹을 수 있어요.",
            "비건/채식 레스토랑이 많아요. 우붓에 특히 많으니 채식러도 걱정 마세요.",
            "해산물 BBQ는 짐바란 비치에서! 선셋과 함께 먹으면 분위기 최고예요.",
        ],
        "budget_tips": [
            "로컬 와룽에서 식사하면 1끼 20,000~40,000루피아(약 2,000~4,000원)입니다.",
            "편점(GoFood) 배달 앱으로 호텔에서 시켜 먹으면 교통비 절약돼요.",
            "생수는 편의점에서 사면 5,000루피아, 관광지에서는 15,000루피아예요.",
        ],
    },
    "culture": {
        "tips": [
            "사원 방문 시 사롱(긴 스카프) 착용 필수! 입구에서 빌려주는 곳도 있어요.",
            "사원 입장료는 보통 30,000~60,000루피아입니다.",
            "발리는 힌두교 국가라 일요일이 아닌 '南海网의 날'(갈룽안)에 공연이 많아요.",
            "사진 촬영 전 허락을 구하세요. 특히 제사 중인 장면은 촬영 금지입니다.",
            "케착춤은 울루와뚜 사원에서 일몰 시간에 보는 게 가장 분위기 좋아요.",
            "바롱 댄스는 선악의 대결을 묘사한 발리 전통 공연이에요.",
            "사원 축제 기간(每 210일마다)에는 특별한 의식을 볼 수 있어요.",
            "발리 예술은 회화, 조각, 은세공, 직물 등 다양해요. 우붓 아트 마켓에서 구매 가능합니다.",
        ],
    },
    "beach": {
        "tips": [
            "서핑 강습은 꾸따/스미냑에서 가장 저렴해요. 150,000~250,000루피아/1회.",
            "일몰은 서쪽 해변(꾸따, 스미냑, 울루와뚜)에서, 일출은 동쪽(사누르)에서!",
            "파도가 강한 날에는 수영 금지! 빨간 깃발 표시를 꼭 확인하세요.",
            "비치클럽은 선셋 2시간 전 가야 좋은 자리를 잡을 수 있어요.",
            "자외선이 매우 강해요. 선크림 SPF50+ 필수, 모자도 추천합니다.",
            "해변에서 물건 파는 사람에게는 단호하게 '아니요'라고 하면 됩니다.",
            "스노클링 장비는 현지에서 대여 가능해요. 50,000~100,000루피아.",
            "우기는 파도가 매우 강해요. 서핑은 건기(4~10월)가 가장 좋습니다.",
        ],
    },
    "nature": {
        "tips": [
            "트레킹은 새벽 출발이 필수! 낮에는 매우 덥고 습해요.",
            "모기 기피제 필수. 열대 지역이라 모기가 많습니다.",
            "편한 운동화 필수. 샌들로 트레킹하면 다칠 수 있어요.",
            "우기(11~3월)에는 폭포水量이 풍부하지만 길이 미끄러워요.",
            "화산 트레킹은 가이드 필수! 혼자 가면 위험합니다.",
            "원숭이에게 소지품을 빼앗기지 않게 주의하세요. 가방은 앞으로 메세요.",
            "라이스 테라스는 이른 아침에 가야 안개 없이 깨끗한 뷰를 볼 수 있어요.",
            "열대 우림에서는 갑작스러운 소나기가 올 수 있어요. 우산 필수!",
        ],
    },
    "shopping": {
        "tips": [
            "기념품 가게에서는 흥정이 필수! 첫 가격의 30~50% 수준으로 흥정하세요.",
            "마사지는 관광지보다 로컬 가게가 50% 저렴해요.",
            "아트 마켓은 오전에 가야 선택 폭이 넓어요.",
            "발리 커피, 코코넛 오일, 라탄 가방이 대표 기념품이에요.",
            "사루ongs(전통 직물)은 고품질 기념품으로 좋아요.",
            "은세공은 우붓에서! 세밀한 공예품이 많아요.",
            "면세점은 공항에만 있어요. 시내에서 미리 구매하세요.",
            "스파 패키지 예약은 Klook/마이리얼트립에서 하면 20~30% 저렴해요.",
        ],
    },
    "transport": {
        "tips": [
            "그랩(Grab)이 가장 편하고 저렴해요. 현금/카드 모두 가능.",
            "스쿠터 렌트는 국제운전면허증 필수! 없으면 벌금 500,000루피아.",
            "공항에서 호텔까지 사전 예약 드라이버가 그랩보다 안전해요.",
            "발리는 교통체증이 매우 심해요. 이동 시간을 넉넉하게 잡으세요.",
            "고젝(Gojek)은 그랩 대안이에요. 오토바이 택시도 가능합니다.",
            "우붓→꾸까지 약 1시간, 꾸따→누사두아 약 40분이에요.",
            "장거리 이동은 전용 드라이버를 고용하는 게 편해요. 8시간 기준 500,000~700,000루피아.",
            "보트 투어는 사전 예약 필수! 날씨에 따라 취소될 수 있어요.",
        ],
    },
}


def load_image_mapping():
    """이미지 매핑 로드"""
    for f in [MAPPING_FILE, BASE_DIR / "image_mapping_v2.json", BASE_DIR / "image_mapping.json"]:
        if f.exists():
            try:
                return json.loads(f.read_text())
            except:
                continue
    return {}

def get_images(area, category, page_index=0, count=10):
    """지역+카테고리별 이미지 가져오기 (페이지별 고유 배분 - 중복 방지)"""
    mapping = load_image_mapping()
    
    def rotate_images(img_list, pidx, cnt):
        """페이지별 고유 이미지 세트 생성 (시드 셔플 방식)"""
        total = len(img_list)
        if total <= cnt:
            return list(img_list)
        # 페이지별 고유 시드로 셔플 → 앞에서 cnt개 선택
        seed_str = f"{area}_{category}_{pidx}"
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        shuffled = list(img_list)
        # Fisher-Yates 셔플 (시드 고정)
        rng = seed_val
        for i in range(len(shuffled) - 1, 0, -1):
            rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
            j = rng % (i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        return shuffled[:cnt]
    
    # v3 매핑 시도
    area_imgs = mapping.get(area, {}).get(category, [])
    if len(area_imgs) >= count:
        return rotate_images(area_imgs, page_index, count)
    
    # 같은 지역 다른 카테고리에서 보충 (해당 카테고리 이미지 우선)
    own_imgs = list(area_imgs)
    other_imgs = []
    for cat, cat_imgs in mapping.get(area, {}).items():
        if cat != category:
            other_imgs.extend(cat_imgs)
    combined = own_imgs + other_imgs
    if len(combined) >= count:
        return rotate_images(combined, page_index, count)
    
    # 파일시스템에서 직접 검색
    for search_dir in [OUTPUT_IMAGES / area / category, OUTPUT_IMAGES / area]:
        if search_dir.exists():
            imgs = sorted([f.name for f in search_dir.iterdir() if f.suffix.lower() in ('.jpg', '.png', '.webp')])
            if len(imgs) >= count:
                return rotate_images(imgs, page_index, count)
    
    # Picsum fallback
    return [f"placeholder_{hashlib.md5(f'{area}_{category}_{page_index}_{i}'.encode()).hexdigest()[:8]}.webp" for i in range(count)]

def generate_qa_html(area, data, index):
    """Q&A 서론 생성 (페이지별 변형)"""
    qa = data.get("intro_qa", [])
    if not qa:
        return ""
    q, a = qa[index % len(qa)]
    return f'''<div style="margin:20px 0;padding:20px;background:linear-gradient(135deg,#e8f5e9,#f1f8e9);border-radius:12px;border:1px solid #c8e6c9">
<p style="margin:0 0 8px;font-weight:700;color:#2e7d32;font-size:1.05em">❓ {q}</p>
<p style="margin:0;color:#333;line-height:1.7">{a}</p>
</div>'''

def generate_food_html(foods, index):
    """음식 섹션 생성 (페이지별 변형)"""
    if not foods:
        return ""
    start = (index * 2) % len(foods)
    selected = []
    for i in range(min(4, len(foods))):
        fd = foods[(start + i) % len(foods)]
        selected.append(fd)
    
    html = ""
    for i, fd in enumerate(selected):
        html += f'''<div style="margin:16px 0;padding:16px;background:#fafafa;border-radius:10px;border-left:4px solid #FF6B35">
<h3 style="font-size:1.1em;font-weight:700;margin:0 0 10px;color:#333">{i+1}. {fd["name"]}</h3>
<p style="margin:0 0 8px;line-height:1.7"><strong>💰 가격:</strong> {fd["price"]} ({fd.get("price_krw", "")})</p>
<p style="margin:0 0 8px;line-height:1.7"><strong>📍 위치:</strong> {fd["area"]}</p>
<p style="margin:0 0 8px;line-height:1.7"><strong>💡 팁:</strong> {fd["tip"]}</p>
<p style="margin:0;line-height:1.7"><strong>🍽️ 추천 메뉴:</strong> {fd.get("must_try", "-")}</p>
</div>'''
    return html

def generate_price_table(price_comp):
    """가격비교 표 생성"""
    if not price_comp:
        return ""
    html = '''<div style="margin:20px 0;overflow-x:auto">
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
<p style="margin:8px 0;font-size:.85em;color:#666">※ 로컬 = 직접 방문 시 / 투어 = 투어 포함 시 / 호텔 = 호텔 내 레스토랑 시</p>'''
    return html

def generate_transport_html(transport):
    """교통 정보 표 생성"""
    if not transport:
        return ""
    html = '''<div style="margin:16px 0;overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white"><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">정보</th></tr></thead>
<tbody>'''
    for i, t in enumerate(transport):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        html += f'''<tr style="background:{bg}"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">{t["name"]}</td><td style="padding:10px 8px;border:1px solid #ddd">{t["price"]}</td></tr>'''
    html += '''</tbody></table></div>'''
    return html

def generate_hotel_table(hotels):
    """숙소 가격비교 표"""
    if not hotels:
        return ""
    return f'''<div style="margin:16px 0;overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#1565c0;color:white"><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">등급</th><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">가격대</th></tr></thead>
<tbody>
<tr style="background:#f9f9f9"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰 예산형</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('budget', '-')}</td></tr>
<tr style="background:#ffffff"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰💰 중급</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('mid', '-')}</td></tr>
<tr style="background:#f9f9f9"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰💰💰 고급</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('high', '-')}</td></tr>
</tbody></table></div>'''

def generate_extra_tips(category, index):
    """카테고리별 추가 팁 (페이지 변형용)"""
    extra = CATEGORY_EXTRA_CONTENT.get(category, {})
    tips = extra.get("tips", [])
    if not tips:
        return ""
    
    start = (index * 2) % len(tips)
    selected = []
    for i in range(min(3, len(tips))):
        selected.append(tips[(start + i) % len(tips)])
    
    html = '''<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">💡 실전 팁</h2>
<ul style="padding-left:20px;margin:16px 0">'''
    for tip in selected:
        html += f'<li style="margin-bottom:8px;line-height:1.7">{tip}</li>'
    html += '</ul>'
    return html

def generate_coupon_html():
    """쿠폰 이미지 + 하이퍼링크 HTML"""
    return f'''<div style="margin:24px 0;text-align:center">
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰" style="max-width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12)" loading="lazy" />
</a>
<p style="margin-top:10px;font-size:.85em;color:#666">마이리얼트립 할인쿠폰 — 투어/티켓/숙소 최대 30% 할인</p>
</div>'''

def generate_images_html(area, category, index):
    """이미지 10장 HTML 생성"""
    images = get_images(area, category, index, 10)
    cat_info = CATEGORIES.get(category, CATEGORIES["food"])
    html = ""
    for i, img in enumerate(images):
        img_path = f"../../images/{area}/{category}/{img}"
        alt_text = f"{area} {cat_info['name']} 여행 사진 {i+1}"
        html += f'<figure style="margin:20px 0;text-align:center"><img src="{img_path}" alt="{alt_text}" loading="lazy" style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)" /></figure>\n'
    return html

def generate_related_links(area, category, index):
    """관련 지역 링크 (내부 링크 시스템)"""
    other_areas = [a for a in AREAS if a != area]
    random.seed(f"{area}_{category}_{index}")
    selected = random.sample(other_areas, min(3, len(other_areas)))
    
    cat_info = CATEGORIES.get(category, CATEGORIES["food"])
    html = '''<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">🔗 관련 지역 추천</h2>
<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0">'''
    for sa in selected:
        page_idx = (index + 1) % 14 + 1
        html += f'<a href="/{sa}/{category}/{page_idx:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{sa} {cat_info["name"]}</a>'
    html += '</div>'
    return html

def generate_html(area, category, index):
    """단일 HTML 페이지 생성"""
    data = BALI_DATA.get(area, list(BALI_DATA.values())[0])
    cat_info = CATEGORIES.get(category, CATEGORIES["food"])
    
    # SEO 제목
    if HAS_SEO:
        title = generate_seo_title(area, category, index)
        meta_desc = generate_meta_description(area, category, index)
        meta_keywords = generate_keywords(area, category)
    else:
        title = f"{area} {cat_info['name']} 여행 가이드 — {CURRENT_YEAR} 최신 #{index+1}"
        meta_desc = f"{area} {cat_info['name']} 여행 후기. 실제 가격 비교, 할인쿠폰, 실전 팁 포함. {CURRENT_YEAR} 기준."
        meta_keywords = f"{area}, 발리, 인도네시아, {cat_info['name']}, 여행, 자유여행, 가격비교"
    
    # 메타 설명 중복 제거
    if meta_desc.startswith(area + " " + area):
        meta_desc = meta_desc.replace(area + " " + area, area, 1)
    
    # 날짜 생성 (페이지별 고유)
    base_date = datetime(2026, 4, 1)
    page_date = base_date + timedelta(days=index % 30)
    date_str = page_date.strftime("%Y-%m-%d")
    
    # 섹션 생성
    qa_html = generate_qa_html(area, data, index)
    
    # 카테고리별 콘텐츠
    cat_data = data.get(category, [])
    if category == "food":
        content_html = generate_food_html(cat_data, index)
    else:
        content_html = ""
        for item in cat_data:
            content_html += f'''<div style="margin:16px 0;padding:16px;background:#fafafa;border-radius:10px;border-left:4px solid #FF6B35">
<h3 style="font-size:1.1em;font-weight:700;margin:0 0 10px;color:#333">{item["name"]}</h3>
<p style="margin:0 0 8px;line-height:1.7"><strong>💰 가격:</strong> {item.get("price", "-")}</p>
<p style="margin:0 0 8px;line-height:1.7"><strong>💡 팁:</strong> {item.get("tip", "-")}</p>
</div>'''
    
    price_table = generate_price_table(data.get("price_comparison", []))
    transport_html = generate_transport_html(data.get("transport", []))
    hotel_table = generate_hotel_table(data.get("hotels", {}))
    extra_tips = generate_extra_tips(category, index)
    images_html = generate_images_html(area, category, index)
    related_html = generate_related_links(area, category, index)
    coupon_html = generate_coupon_html()
    
    # 명소 HTML
    spots = data.get("spots", [])
    spots_html = ""
    if spots:
        spots_html = '''<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">📍 추천 명소</h2>
<ol style="padding-left:20px;margin:16px 0">'''
        for i, s in enumerate(spots):
            spots_html += f'<li style="margin-bottom:8px;line-height:1.7"><strong>{i+1}. {s}</strong></li>'
        spots_html += '</ol>'
    
    # 숨은 gems
    hidden = data.get("hidden_gem", "")
    hidden_html = ""
    if hidden:
        hidden_html = f'''<div style="margin:20px 0;padding:16px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2">
<p style="margin:0;font-weight:600;color:#e65100">💎 숨은 명소: {hidden}</p>
</div>'''
    
    # 최종 HTML
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{meta_keywords}">
<link rel="canonical" href="{SITE_URL}/{area}/{category}/{index+1:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE_URL}/images/{area}/001.webp">
<meta property="og:url" content="{SITE_URL}/{area}/{category}/{index+1:03d}.html">
<meta property="og:site_name" content="발리 여행 블로그">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "{title}", "description": "{meta_desc}", "image": ["{SITE_URL}/images/{area}/001.webp"], "datePublished": "{date_str}", "dateModified": "{date_str}", "author": {{"@type": "Person", "name": "{AUTHOR}"}}, "publisher": {{"@type": "Organization", "name": "발리 여행 블로그"}}, "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE_URL}/{area}/{category}/{index+1:03d}.html"}}}}</script>
<style>
:root {{ --primary: #FF6B35; --bg: #FAFAFA; --text: #1A1A2E; --text-light: #666; --border: #E0E0E0; --card-bg: #FFFFFF; --shadow: 0 2px 8px rgba(0,0,0,0.08); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
header {{ background: linear-gradient(135deg, #FF6B35, #FF8C61); color: white; padding: 40px 20px; text-align: center; }}
header h1 {{ font-size: 1.8rem; margin-bottom: 10px; }}
header .meta {{ opacity: 0.9; font-size: 0.9rem; }}
.breadcrumb {{ padding: 15px 0; font-size: 0.85rem; color: var(--text-light); }}
.breadcrumb a {{ color: var(--primary); text-decoration: none; }}
article {{ background: var(--card-bg); border-radius: 12px; padding: 30px; box-shadow: var(--shadow); margin: 20px 0; }}
article h2 {{ color: var(--primary); font-size: 1.4rem; margin: 30px 0 15px; padding-bottom: 8px; border-bottom: 2px solid var(--primary); }}
.tags {{ margin: 20px 0; }}
.tag {{ display: inline-block; background: #F0F0F0; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 3px; color: var(--text-light); }}
footer {{ text-align: center; padding: 30px; color: var(--text-light); font-size: 0.85rem; }}
@media (max-width: 600px) {{ .container {{ padding: 10px; }} article {{ padding: 20px; }} header h1 {{ font-size: 1.4rem; }} table {{ font-size: .8em; }} }}
</style>
</head>
<body>

<!-- 상단 파트너스 고지문 -->
<div style="background:#f5f5f5;padding:10px 15px;border-bottom:1px solid #e0e0e0;font-size:13px;color:#555;text-align:center;line-height:1.6">
📌 이 글은 <strong>마이리얼트립 파트너스 활동</strong>의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다. 
구매에 추가 비용이 발생하지 않습니다. | 
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored" style="color:#d84315;font-weight:600">🎫 마이리얼트립 할인쿠폰 받기</a>
</div>

<header>
<h1>{title}</h1>
<div class="meta">{cat_info['icon']} {area} | {cat_info['name']} | 📅 {CURRENT_YEAR}년 기준 | ✍️ {AUTHOR}</div>
</header>

<div class="container">
<nav class="breadcrumb">
<a href="/">🏠 홈</a> &gt; 
<a href="/{area}/">{area}</a> &gt; 
<a href="/{area}/{category}/">{cat_info['name']}</a> &gt; 
<span>{title[:30]}...</span>
</nav>

<article>

{qa_html}

<!-- 핵심 팁 요약 박스 -->
<div style="margin:0 0 20px 0;padding:16px 20px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2">
<p style="margin:0;font-size:1em;color:#1a1a2e;line-height:1.7;font-weight:500">
<strong>{area} {cat_info['name']}</strong> 핵심 팁: 
{data.get('description', '')}. 
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored" style="color:#d84315;font-weight:600">할인쿠폰 받기</a>로 추가 할인 가능.
</p>
</div>

<!-- 쿠폰 이미지 + 하이퍼링크 (상단) -->
{coupon_html}

<!-- 이미지 배치 (10장) -->
{images_html}

<!-- 카테고리별 콘텐츠 -->
<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{area}에서 꼭 {cat_info['desc']}</h2>
<p style="margin-bottom:18px;line-height:2.0;word-break:keep-all">{area} 여행에서 {cat_info['name']}은 빼놓을 수 없는 즐거움이에요. 제가 직접 다녀본 기준으로, 가격과 팁을 정리했어요.</p>
{content_html}

<!-- 가격비교 표 -->
<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{area} 가격 비교 (로컬 vs 투어 vs 호텔)</h2>
{price_table}

<!-- 명소 -->
{spots_html}

<!-- 숨은 명소 -->
{hidden_html}

<!-- 교통 정보 -->
<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{area} 교통 정보</h2>
{transport_html}

<!-- 숙소 -->
<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{area} 숙소 추천</h2>
{hotel_table}

<!-- 추가 팁 -->
{extra_tips}

<!-- 관련 지역 링크 -->
{related_html}

<!-- 쿠폰 이미지 + 하이퍼링크 (하단) -->
{coupon_html}

<!-- 태그 -->
<div class="tags">
<span class="tag">{area}</span>
<span class="tag">발리</span>
<span class="tag">{cat_info['name']}</span>
<span class="tag">자유여행</span>
<span class="tag">가격비교</span>
<span class="tag">{CURRENT_YEAR}</span>
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


def main():
    print("=" * 60)
    print("🏗️  발리 여행 블로그 빌드 시스템 v3")
    print("=" * 60)
    
    OUTPUT_HTML.mkdir(parents=True, exist_ok=True)
    
    total = 0
    pages_per_combo = 14  # 11 areas × 6 cats × 14 = 924 pages
    
    for area in AREAS:
        print(f"\n📍 {area}")
        for category in CATEGORIES:
            for page_idx in range(pages_per_combo):
                html = generate_html(area, category, page_idx)
                
                # 파일명: area/category/001.html
                cat_dir = OUTPUT_HTML / area / category
                cat_dir.mkdir(parents=True, exist_ok=True)
                
                filename = f"{page_idx + 1:03d}.html"
                filepath = cat_dir / filename
                filepath.write_text(html, encoding='utf-8')
                total += 1
            
            print(f"  {CATEGORIES[category]['icon']} {category}: {pages_per_combo}개 생성")
    
    print(f"\n{'=' * 60}")
    print(f"✅ 총 {total}개 HTML 페이지 생성 완료!")
    print(f"📁 위치: {OUTPUT_HTML}")
    
    # 쿠폰 이미지 복사
    coupon_dest = OUTPUT_HTML.parent / "images" / "mrt_coupon.jpg"
    coupon_dest.parent.mkdir(parents=True, exist_ok=True)
    if COUPON_IMG.exists() and not coupon_dest.exists():
        import shutil
        shutil.copy2(COUPON_IMG, coupon_dest)
        print(f"📷 쿠폰 이미지 복사: {coupon_dest}")

if __name__ == "__main__":
    main()
