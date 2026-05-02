#!/usr/bin/env python3
"""
JP Travel Bali — v9 전면 재빌드
924개 HTML을 고품질 여행 블로그로 전면 재생성

핵심 목표:
- 한국어 본문 2500자 이상
- 이모지/한자 제거
- 조사 자동 처리
- 경험 중심 콘텐츠
- 고유 ALT/Figcaption
- SEO 롱테일 제목
- MRT 제휴 링크 정상 배치
"""

import os, re, json, random, hashlib, math
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_HTML = BASE_DIR / "output" / "html" / "bali"
OUTPUT_IMAGES = BASE_DIR / "output" / "images"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
COUPON_IMG = BASE_DIR / "mrt_coupon.jpg"

AFFILIATE_URL = "https://myrealt.rip/YuJbb5"
TOUR_URL = "https://myrealt.rip/YoEc1b"
SITE_URL = "https://balitravel.blog"
CURRENT_YEAR = datetime.now().year

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "-", "desc": "맛집 탐방"},
    "culture": {"name": "문화/사원", "icon": "-", "desc": "문화 체험"},
    "beach": {"name": "해변/서핑", "icon": "-", "desc": "해변 액티비티"},
    "nature": {"name": "자연/모험", "icon": "-", "desc": "자연 탐방"},
    "shopping": {"name": "쇼핑/마사지", "icon": "-", "desc": "쇼핑 & 힐링"},
    "transport": {"name": "여행/교통", "icon": "-", "desc": "이동 정보"},
}

# ============================================================
# 한국어 조사 처리
# ============================================================
def has_batchim(word):
    if not word:
        return False
    code = ord(word[-1]) - 0xAC00
    return 0 <= code <= 0x278C and (code % 28) != 0

def josa(word, pair):
    return pair[0] if has_batchim(word) else pair[1]

def j(word, pair):
    """단축 조사 함수"""
    return josa(word, pair)

# ============================================================
# BALI_DATA (11개 지역 상세 데이터)
# ============================================================
BALI_DATA = {
    "우붓": {
        "desc": "발리 문화예술의 중심지",
        "vibe": "예술가 마을",
        "spots": ["테갈랑 라이스 테라스", "원숭이 숲", "우붓 아트 마켓", "타만 사라스와티 사원", "캄포한 리지"],
        "hidden": "캄포한 리지 절벽 위 산책로는 우붓 시내에서 도보 15분인데 관광객이 거의 없어요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 90분, 그랩 300,000Rp. 우붓 시내는 스쿠터 80,000Rp/일",
        "best_time": "오전 8시~11시",
        "food": [
            {"name": "Bebek Bengil", "price": "95,000Rp", "krw": "약 9,500원", "tip": "우붓 대표 오리구이. 예약 필수. 크리스피덕이 시그니처", "area": "우붓 시내", "must": "크리스피덕 세트"},
            {"name": "Warung Babi Guling Ibu Oka", "price": "50,000Rp", "krw": "약 5,000원", "tip": "새끼돼지구이. 오전에 가야 sold out 안됨", "area": "우붓 궁전 근처", "must": "바비굴링 스페셜"},
            {"name": "Clear Cafe", "price": "음료 40,000~80,000Rp", "krw": "약 4,000~8,000원", "tip": "강변 뷰 카페. 비건 메뉴도 있음", "area": "캠프한 리지", "must": "스무디볼"},
            {"name": "Locavore", "price": "점심 350,000Rp~", "krw": "약 35,000원~", "tip": "발리 최고 파인다이닝. 2개월 전 예약 필요", "area": "우붓 시내", "must": "코스 요리"},
            {"name": "Room 4 Dessert", "price": "디저트 120,000~200,000Rp", "krw": "약 12,000~20,000원", "tip": "디저트 바. 예약 추천", "area": "우붓 시내", "must": "코스 디저트"},
            {"name": "Sayuri Healing Food", "price": "브런치 60,000~120,000Rp", "krw": "약 6,000~12,000원", "tip": "비건 전문. 건강식 선호자에게 추천", "area": "우붓 시내", "must": "스무디볼"},
        ],
        "culture": [
            {"name": "타만 사라스와티 사원", "price": "무료 (기부금 10,000~20,000Rp)", "tip": "연못 위 사원. 일몰 시간대 방문 추천", "area": "우붓 시내"},
            {"name": "우붓 원숭이 숲", "price": "80,000Rp", "tip": "소지품 주의. 오전에 한적", "area": "우붓 시내"},
            {"name": "우붓 왕궁", "price": "무료", "tip": "저녁 전통 공연 7시. 입장료 100,000Rp", "area": "우붓 시내"},
            {"name": "아궁 라이 미술관", "price": "50,000Rp", "tip": "발리 전통 미술 컬렉션", "area": "우붓 시내"},
        ],
        "beach": [
            {"name": "아융강 래프팅", "price": "250,000~400,000Rp", "tip": "2시간 코스. 초보 가능", "area": "우붓 외곽"},
            {"name": "천연 수영장", "price": "50,000~100,000Rp", "tip": "알링킹 폭포 근처", "area": "우붓 외곽"},
        ],
        "nature": [
            {"name": "테갈랑 라이스 테라스", "price": "15,000Rp", "tip": "새벽/오전 방문 추천. 안개 없이 깨끗한 뷰", "area": "우붓 북쪽"},
            {"name": "알링킹 폭포", "price": "20,000Rp", "tip": "차로 30분. 계단 많으니 편한 신발 필수", "area": "우붓 외곽"},
            {"name": "뜨갈라랑 스윙", "price": "150,000~250,000Rp", "tip": "인생샷 명소. 오전에 웨이팅 짧음", "area": "우붓 북쪽"},
            {"name": "캄포한 리지 산책", "price": "무료", "tip": "시내에서 도보 15분. 강변 절벽 코스", "area": "우붓 시내"},
        ],
        "shopping": [
            {"name": "우붓 아트 마켓", "price": "흥정 필수", "tip": "첫 가격의 30~50%. 오전에 선택 폭 넓음", "area": "우붓 시내"},
            {"name": "마스 마을 은세공", "price": "다양", "tip": "시내보다 30~40% 저렴. 공방 직접 방문", "area": "마스 마을"},
            {"name": "우붓 전통 마사지", "price": "80,000~150,000Rp/1시간", "tip": "Boreh 전통 마사지 추천", "area": "우붓 시내"},
        ],
        "transport": [
            {"name": "공항-우붓", "price": "300,000Rp (90분)", "tip": "그랩 또는 사전 예약 드라이버"},
            {"name": "우붓 시내", "price": "스쿠터 80,000Rp/일", "tip": "교통체증 심하므로 오전 이동 추천"},
            {"name": "우붓-꾸따", "price": "그랩 150,000~200,000Rp (1시간)", "tip": "오후 피크 시간 피하세요"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000Rp/1박", "mid": "풀빌라 500,000~1,500,000Rp/1박", "high": "알리라 우붓 3,000,000Rp~/1박"},
        "price_comp": [
            {"item": "베벵길 오리구이", "local": "95,000Rp", "tour": "120,000Rp", "hotel": "180,000Rp"},
            {"item": "나시고렝", "local": "25,000Rp", "tour": "45,000Rp", "hotel": "80,000Rp"},
            {"item": "마사지 1시간", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "250,000Rp"},
            {"item": "생맥주", "local": "35,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
        ],
    },
    "스미냑": {
        "desc": "트렌디한 비치 타운",
        "vibe": "비치클럽과 부티크",
        "spots": ["더블식스 비치", "포테이토 헤드", "스미냑 빌리지", "페티탕겟 사원", "쿠데타 비치클럽"],
        "hidden": "더블식스 비치 끝자락은 관광객 적고 선셋 포토스팟으로 최고",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 30분, 그랩 150,000Rp. 스미냑은 교통체증 심하므로 도보/스쿠터 추천",
        "best_time": "오후 4시~7시",
        "food": [
            {"name": "Potato Head Beach Club", "price": "음료 100,000~200,000Rp", "krw": "약 10,000~20,000원", "tip": "선셋 2시간 전 도착 추천", "area": "스미냑 비치", "must": "칵테일 + 선셋"},
            {"name": "La Lucciola", "price": "파스타 150,000~250,000Rp", "krw": "약 15,000~25,000원", "tip": "해변 이탈리안. 분위기 최고", "area": "스미냑 비치", "must": "해산물 파스타"},
            {"name": "Warung Nia", "price": "30,000~60,000Rp", "krw": "약 3,000~6,000원", "tip": "가성비 로컬 맛집", "area": "스미냑 시내", "must": "나시캄푸르"},
            {"name": "Sisterfields", "price": "브런치 80,000~150,000Rp", "krw": "약 8,000~15,000원", "tip": "호주식 브런치. 주말 웨이팅", "area": "스미냑 시내", "must": "에그 베네딕트"},
            {"name": "Motel Mexicola", "price": "칵테일 80,000~150,000Rp", "krw": "약 8,000~15,000원", "tip": "멕시칸 바. 밤에는 파티 분위기", "area": "스미냑 시내", "must": "타코 + 마가리타"},
            {"name": "Sarong", "price": "메인 150,000~300,000Rp", "krw": "약 15,000~30,000원", "tip": "아시안 퓨전 파인다이닝", "area": "스미냑 시내", "must": "아시안 타파스"},
        ],
        "culture": [
            {"name": "페티탕겟 사원", "price": "무료 (기부금)", "tip": "해변 사원. 선셋 시간대 추천", "area": "스미냑 비치"},
            {"name": "스미냑 빌리지", "price": "무료", "tip": "전통 마을 산책. 예술가 공방 방문", "area": "스미냑 시내"},
        ],
        "beach": [
            {"name": "더블식스 비치", "price": "무료", "tip": "선셋 포토스팟. 비치클럽 다수", "area": "스미냑"},
            {"name": "스미냑 비치 서핑", "price": "150,000~250,000Rp/1회", "tip": "초보 강습 가능", "area": "스미냑"},
            {"name": "쿠데타 비치클럽", "price": "음료 80,000~150,000Rp", "tip": "선베드 무료. 최소 음료 1잔", "area": "스미냑 비치"},
        ],
        "nature": [
            {"name": "해변 산책로", "price": "무료", "tip": "더블식스~포테이토 헤드 약 2km", "area": "스미냑"},
        ],
        "shopping": [
            {"name": "스미냑 빌리지 쇼핑", "price": "다양", "tip": "부티크숍 밀집. 세일 11~12월", "area": "스미냑 시내"},
            {"name": "스미냑 스파", "price": "150,000~400,000Rp/1시간", "tip": "Spring Spa, Bodyworks 추천", "area": "스미냑 시내"},
        ],
        "transport": [
            {"name": "공항-스미냑", "price": "150,000Rp (30분)", "tip": "그랩 추천"},
            {"name": "스미냑 시내", "price": "도보 가능", "tip": "교통체증 심하므로 도보/스쿠터"},
        ],
        "hotels": {"budget": "게스트하우스 150,000~300,000Rp/1박", "mid": "부티크 호텔 500,000~1,500,000Rp/1박", "high": "위 발리 5,000,000Rp~/1박"},
        "price_comp": [
            {"item": "비치클럽 음료", "local": "100,000Rp", "tour": "150,000Rp", "hotel": "200,000Rp"},
            {"item": "파스타", "local": "150,000Rp", "tour": "180,000Rp", "hotel": "250,000Rp"},
            {"item": "마사지 1시간", "local": "80,000Rp", "tour": "150,000Rp", "hotel": "300,000Rp"},
        ],
    },
    "꾸따": {
        "desc": "발리 최초의 관광지, 서핑의 성지",
        "vibe": "서핑과 나이트라이프",
        "spots": ["꾸따 비치", "비치워크 쇼핑몰", "워터밤 파크", "꾸따 아트 마켓", "레기안 비치"],
        "hidden": "꾸따 북쪽 레기안 비치는 꾸보다 한적하고 서핑 포인트도 좋아요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 15분, 그랩 100,000Rp. 공항에서 가장 가까운 관광지",
        "best_time": "오후 4시~6시",
        "food": [
            {"name": "Warung Murah", "price": "나시고렝 20,000~35,000Rp", "krw": "약 2,000~3,500원", "tip": "대표 저렴한 로컬. 점심 웨이팅", "area": "꾸따 시내", "must": "나시고렝 스페셜"},
            {"name": "Made's Warung", "price": "40,000~80,000Rp", "krw": "약 4,000~8,000원", "tip": "1969년부터 운영된 전통 맛집", "area": "꾸따 시내", "must": "나시짬뿌르"},
            {"name": "Hard Rock Cafe", "price": "버거 120,000~180,000Rp", "krw": "약 12,000~18,000원", "tip": "비치 앞. 라이브 음악", "area": "꾸따 비치", "must": "레전더리 버거"},
            {"name": "Poppies Restaurant", "price": "파스타 80,000~150,000Rp", "krw": "약 8,000~15,000원", "tip": "정원 분위기", "area": "팝피스 레인", "must": "해산물 파스타"},
            {"name": "Bamboo Corner", "price": "25,000~50,000Rp", "krw": "약 2,500~5,000원", "tip": "가성비 로컬. 대나무 인테리어", "area": "꾸따 시내", "must": "나시캄푸르"},
        ],
        "culture": [
            {"name": "꾸따 아트 마켓", "price": "무료", "tip": "기념품 쇼핑. 흥정 필수", "area": "꾸따 시내"},
            {"name": "워터밤 파크", "price": "535,000Rp", "tip": "최대 워터파크. 가족 추천", "area": "꾸따"},
        ],
        "beach": [
            {"name": "꾸따 비치", "price": "무료", "tip": "서핑 강습 가능. 선셋 포토스팟", "area": "꾸따"},
            {"name": "레기안 비치", "price": "무료", "tip": "꾸보다 한적한 서핑 포인트", "area": "레기안"},
            {"name": "서핑 강습", "price": "150,000~250,000Rp/1회", "tip": "보드 포함. 2시간. 초보 가능", "area": "꾸따 비치"},
        ],
        "nature": [],
        "shopping": [
            {"name": "비치워크 쇼핑몰", "price": "다양", "tip": "최대 쇼핑몰. 브랜드+로컬", "area": "꾸따 비치"},
            {"name": "Discovery Mall", "price": "다양", "tip": "로컬 브랜드 위주", "area": "꾸따"},
            {"name": "꾸따 마사지", "price": "60,000~100,000Rp/1시간", "tip": "해변 근처가 가장 저렴", "area": "꾸따 비치"},
        ],
        "transport": [
            {"name": "공항-꾸따", "price": "100,000Rp (15분)", "tip": "공항에서 가장 가까운 관광지"},
            {"name": "꾸따 시내", "price": "도보 가능", "tip": "도보 이동 가능"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000Rp/1박", "mid": "비치 호텔 300,000~800,000Rp/1박", "high": "하드락 호텔 1,500,000Rp~/1박"},
        "price_comp": [
            {"item": "서핑 강습", "local": "150,000Rp", "tour": "250,000Rp", "hotel": "350,000Rp"},
            {"item": "나시고렝", "local": "20,000Rp", "tour": "40,000Rp", "hotel": "70,000Rp"},
            {"item": "마사지 1시간", "local": "60,000Rp", "tour": "100,000Rp", "hotel": "200,000Rp"},
        ],
    },
    "사누르": {
        "desc": "조용한 해변 휴양지",
        "vibe": "일출과 자전거",
        "spots": ["사누르 비치", "아트 마켓", "르 마유르 박물관", "나이트 마켓", "블랑크 미술관"],
        "hidden": "사누르 나이트 마켓은 저녁 6시부터 로컬 음식을 20,000Rp대로 즐길 수 있어요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 30분, 그랩 150,000Rp. 자전거 50,000Rp/일",
        "best_time": "오전 5시30분 (일출)",
        "food": [
            {"name": "Warung Mak Beng", "price": "생선튀김 세트 35,000Rp", "krw": "약 3,500원", "tip": "줄 서서 먹는 집. 대표 맛집", "area": "사누르 시내", "must": "생선튀김 세트"},
            {"name": "Massimo", "price": "파스타 80,000~150,000Rp", "krw": "약 8,000~15,000원", "tip": "이탈리안. 예약 추천", "area": "사누르 비치", "must": "트러플 파스타"},
            {"name": "The Glass House", "price": "브런치 60,000~120,000Rp", "krw": "약 6,000~12,000원", "tip": "정원 분위기 카페", "area": "사누르 시내", "must": "아보카도 토스트"},
        ],
        "culture": [
            {"name": "르 마유르 박물관", "price": "50,000Rp", "tip": "발리 현대 미술", "area": "사누르"},
            {"name": "블랑크 미술관", "price": "100,000Rp", "tip": "아르카 블랑크 작품 전시", "area": "사누르"},
        ],
        "beach": [
            {"name": "사누르 비치", "price": "무료", "tip": "일출 명소. 자전거 코스 5km", "area": "사누르"},
        ],
        "nature": [],
        "shopping": [
            {"name": "사누르 아트 마켓", "price": "다양", "tip": "기념품. 흥정 필수", "area": "사누르"},
            {"name": "사누르 나이트 마켓", "price": "20,000~50,000Rp", "tip": "저녁 6시부터 로컬 음식", "area": "사누르"},
        ],
        "transport": [
            {"name": "공항-사누르", "price": "150,000Rp (30분)", "tip": "그랩 추천"},
            {"name": "사누르 시내", "price": "자전거 50,000Rp/일", "tip": "자전거로 이동 좋음"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000Rp/1박", "mid": "비치 리조트 500,000~1,500,000Rp/1박", "high": "그랜드 하얏트 3,000,000Rp~/1박"},
        "price_comp": [
            {"item": "생선튀김 세트", "local": "35,000Rp", "tour": "55,000Rp", "hotel": "90,000Rp"},
            {"item": "파스타", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "180,000Rp"},
            {"item": "마사지 1시간", "local": "70,000Rp", "tour": "120,000Rp", "hotel": "250,000Rp"},
        ],
    },
    "누사두아": {
        "desc": "프리미엄 리조트 지구",
        "vibe": "리조트와 가족 여행",
        "spots": ["누사두아 비치", "워터블로우", "발리 컬렉션 쇼핑몰", "파라다이스 극장", "워터밤 파크"],
        "hidden": "누사두아 비치 동쪽 끝은 스노클링 포인트로 관광객이 거의 없어요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 40분, 그랩 200,000Rp. 리조트 셔틀 무료",
        "best_time": "오후 3시~6시",
        "food": [
            {"name": "Bumbu Bali", "price": "80,000~150,000Rp", "krw": "약 8,000~15,000원", "tip": "발리 전통 요리 전문. 쿠킹클래스 운영", "area": "누사두아", "must": "발리 정식 코스"},
            {"name": "Warung Dobiel", "price": "나시고렝 25,000~40,000Rp", "krw": "약 2,500~4,000원", "tip": "누사두아 근처 로컬", "area": "누사두아", "must": "나시고렝"},
            {"name": "The Cafe at Mulia", "price": "뷔페 500,000Rp~", "krw": "약 50,000원~", "tip": "최고급 뷔페", "area": "뮬리아 리조트", "must": "디너 뷔페"},
        ],
        "culture": [
            {"name": "파라다이스 극장", "price": "150,000~300,000Rp", "tip": "발리 전통 공연. 예약 추천", "area": "누사두아"},
        ],
        "beach": [
            {"name": "누사두아 비치", "price": "무료", "tip": "깨끗한 백사장. 리조트 프라이빗 비치", "area": "누사두아"},
            {"name": "워터블로우", "price": "20,000Rp", "tip": "파도 칠 때 물기둥 장관. 일몰 추천", "area": "누사두아"},
        ],
        "nature": [],
        "shopping": [
            {"name": "발리 컬렉션 쇼핑몰", "price": "다양", "tip": "누사두아 유일의 쇼핑몰", "area": "누사두아"},
        ],
        "transport": [
            {"name": "공항-누사두아", "price": "200,000Rp (40분)", "tip": "리조트 셔틀 또는 그랩"},
        ],
        "hotels": {"budget": "게스트하우스 150,000~300,000Rp/1박", "mid": "리조트 800,000~2,000,000Rp/1박", "high": "뮬리아 리조트 5,000,000Rp~/1박"},
        "price_comp": [
            {"item": "발리 정식", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "200,000Rp"},
            {"item": "뷔페 디너", "local": "500,000Rp", "tour": "600,000Rp", "hotel": "800,000Rp"},
        ],
    },
    "울루와뚜": {
        "desc": "절벽 위의 서핑과 사원",
        "vibe": "절벽과 케착춤",
        "spots": ["울루와뚜 사원", "싱글핀 비치클럽", "판다와 비치", "블루포인트 비치", "짐바란 비치"],
        "hidden": "판다와 비치는 절벽 아래 숨겨진 비치로 관광객 적고 물 맑아요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 45분, 그랩 200,000Rp. 절벽 지역이라 스쿠터 주의",
        "best_time": "오후 5시~6시30분",
        "food": [
            {"name": "Single Fin", "price": "음료 80,000~150,000Rp", "krw": "약 8,000~15,000원", "tip": "절벽 위 비치클럽. 선셋 명소", "area": "울루와뚜 절벽", "must": "칵테일 + 선셋"},
            {"name": "Warung Sego Njamoer", "price": "25,000~40,000Rp", "krw": "약 2,500~4,000원", "tip": "로컬 맛집", "area": "울루와뚜", "must": "나시고렝"},
            {"name": "Rock Bar", "price": "칵테일 150,000~250,000Rp", "krw": "약 15,000~25,000원", "tip": "절벽 위 바. 발리 최고 야경", "area": "짐바란", "must": "시그니처 칵테일"},
        ],
        "culture": [
            {"name": "울루와뚜 사원", "price": "50,000Rp", "tip": "절벽 위 해양 사원. 케착춤 필수 관람", "area": "울루와뚜"},
            {"name": "케착춤 공연", "price": "입장료에 포함", "tip": "오후 6시. 일몰과 함께", "area": "울루와뚜 사원"},
        ],
        "beach": [
            {"name": "울루와뚜 비치", "price": "무료", "tip": "절벽 아래 숨겨진 비치. 계단 내려가야 함", "area": "울루와뚜"},
            {"name": "판다와 비치", "price": "10,000Rp", "tip": "절벽 아래. 관광객 적고 물 맑음", "area": "울루와뚜"},
            {"name": "짐바란 비치", "price": "무료", "tip": "해산물 BBQ. 선셋 추천", "area": "짐바란"},
        ],
        "nature": [],
        "shopping": [
            {"name": "사원 입구 기념품", "price": "다양", "tip": "흥정 필수", "area": "울루와뚜"},
        ],
        "transport": [
            {"name": "공항-울루와뚜", "price": "200,000Rp (45분)", "tip": "절벽 지역 스쿠터 주의"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000Rp/1박", "mid": "클리프 리조트 500,000~1,500,000Rp/1박", "high": "아야나 리조트 4,000,000Rp~/1박"},
        "price_comp": [
            {"item": "비치클럽 음료", "local": "80,000Rp", "tour": "120,000Rp", "hotel": "200,000Rp"},
            {"item": "서핑 강습", "local": "200,000Rp", "tour": "300,000Rp", "hotel": "450,000Rp"},
        ],
    },
    "짠디다사": {
        "desc": "발리 동부의 조용한 해변 마을",
        "vibe": "다이빙과 한적함",
        "spots": ["짠디다사 비치", "베사키 사원", "티르타강가", "아메드 비치", "아꿍 화산"],
        "hidden": "티르타강가 '정화의 샘'은 현지인만 아는 숨겨진 성지",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 90분, 그랩 350,000Rp. 동부 발리 코스로 연결",
        "best_time": "오전 8시~11시",
        "food": [
            {"name": "Warung Padang Kecag", "price": "나시파당 20,000~35,000Rp", "krw": "약 2,000~3,500원", "tip": "로컬 파당 맛집", "area": "짠디다사", "must": "나시파당"},
            {"name": "Villa Puri Purnama", "price": "해산물 60,000~120,000Rp", "krw": "약 6,000~12,000원", "tip": "해변 해산물", "area": "짠디다사 비치", "must": "그릴 피쉬"},
        ],
        "culture": [
            {"name": "베사키 사원", "price": "60,000Rp", "tip": "발리 어머니 사원. 아꿍 화산 근처", "area": "짠디다사"},
            {"name": "티르타강가", "price": "30,000Rp", "tip": "정화의 샘. 현지인 성지", "area": "짠디다사"},
        ],
        "beach": [
            {"name": "짠디다사 비치", "price": "무료", "tip": "한적한 해변. 관광객 10% 수준", "area": "짠디다사"},
            {"name": "아메드 비치", "price": "무료", "tip": "다이빙/스노클링 포인트", "area": "아메드"},
        ],
        "nature": [
            {"name": "아꿍 화산", "price": "30,000Rp", "tip": "트레킹 코스. 가이드 추천", "area": "짠디다사"},
        ],
        "shopping": [],
        "transport": [
            {"name": "공항-짠디다사", "price": "350,000Rp (90분)", "tip": "동부 발리 코스 연결"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000Rp/1박", "mid": "비치 방갈로 300,000~800,000Rp/1박", "high": "아메드 리조트 1,500,000Rp~/1박"},
        "price_comp": [
            {"item": "나시파당", "local": "20,000Rp", "tour": "40,000Rp", "hotel": "70,000Rp"},
            {"item": "다이빙 1회", "local": "500,000Rp", "tour": "700,000Rp", "hotel": "900,000Rp"},
        ],
    },
    "로비나": {
        "desc": "발리 북부의 조용한 해변, 돌고래 관찰",
        "vibe": "돌고래와 온천",
        "spots": ["로비나 비치", "반자르 온천", "기트기트 폭포", "브둘루 사원", "발리 국립공원"],
        "hidden": "반자르 온천은 관광객 거의 없고 천연 온천수로 무료 족욕 가능",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 3시간, 그랩 500,000Rp. 1박 추천",
        "best_time": "새벽 6시 (돌고래 투어)",
        "food": [
            {"name": "Warung Orange", "price": "해산물 40,000~80,000Rp", "krw": "약 4,000~8,000원", "tip": "대표 해산물 맛집", "area": "로비나 비치", "must": "그릴 피쉬"},
            {"name": "Spaghetti Bar", "price": "파스타 50,000~80,000Rp", "krw": "약 5,000~8,000원", "tip": "이탈리안 맛집", "area": "로비나", "must": "해산물 파스타"},
        ],
        "culture": [
            {"name": "브둘루 사원", "price": "20,000Rp", "tip": "근처 고대 사원", "area": "로비나"},
        ],
        "beach": [
            {"name": "로비나 비치", "price": "무료", "tip": "돌고래 관찰 포인트. 새벽 투어", "area": "로비나"},
            {"name": "돌고래 투어", "price": "150,000~200,000Rp", "tip": "새벽 6시 출발. 보트 포함", "area": "로비나"},
        ],
        "nature": [
            {"name": "반자르 온천", "price": "20,000Rp", "tip": "천연 온천수. 관광객 적음", "area": "반자르"},
            {"name": "기트기트 폭포", "price": "20,000Rp", "tip": "차로 30분", "area": "로비나 외곽"},
        ],
        "shopping": [],
        "transport": [
            {"name": "공항-로비나", "price": "500,000Rp (3시간)", "tip": "1박 추천"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000Rp/1박", "mid": "비치 방갈로 200,000~500,000Rp/1박", "high": "로비나 리조트 1,000,000Rp~/1박"},
        "price_comp": [
            {"item": "돌고래투어", "local": "150,000Rp", "tour": "250,000Rp", "hotel": "350,000Rp"},
            {"item": "해산물", "local": "40,000Rp", "tour": "70,000Rp", "hotel": "120,000Rp"},
        ],
    },
    "킨타마니": {
        "desc": "발리 북부의 화산 지대",
        "vibe": "화산과 일출",
        "spots": ["바투르 화산", "바투르 호수", "킨타마니 전망대", "뜨리뜨 에פק 사원", "뜨갈라랑 라이스 테라스"],
        "hidden": "바투르 호수 남쪽은 관광객 없고 카약 타기 좋은 포인트",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 2시간, 그랩 400,000Rp. 새벽 출발 추천",
        "best_time": "새벽 2시~6시",
        "food": [
            {"name": "Batur Sari Restaurant", "price": "뷔페 100,000~150,000Rp", "krw": "약 10,000~15,000원", "tip": "화산 뷰 뷔페", "area": "킨타마니", "must": "발리 정식 뷔페"},
        ],
        "culture": [
            {"name": "뜨리뜨 에פק 사원", "price": "60,000Rp", "tip": "킨타마니 대표 사원", "area": "킨타마니"},
        ],
        "beach": [],
        "nature": [
            {"name": "바투르 화산 일출 트레킹", "price": "350,000~500,000Rp", "tip": "새벽 2시 출발. 가이드 포함", "area": "킨타마니"},
            {"name": "바투르 호수", "price": "무료", "tip": "화산 칼데라 호수. 카약 투어", "area": "킨타마니"},
        ],
        "shopping": [],
        "transport": [
            {"name": "공항-킨타마니", "price": "400,000Rp (2시간)", "tip": "새벽 출발 추천"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000Rp/1박", "mid": "화산 뷰 리조트 400,000~1,000,000Rp/1박", "high": "킨타마니 리조트 2,000,000Rp~/1박"},
        "price_comp": [
            {"item": "뷔페", "local": "100,000Rp", "tour": "150,000Rp", "hotel": "200,000Rp"},
            {"item": "일출 트레킹", "local": "350,000Rp", "tour": "500,000Rp", "hotel": "700,000Rp"},
        ],
    },
    "타나롯": {
        "desc": "바다 위 사원의 도시",
        "vibe": "일몰과 해양사원",
        "spots": ["타나롯 사원", "일몰 포인트", "바투 볼롱 사원", "잘란 라이스 테라스", "타나롯 시장"],
        "hidden": "바투 볼롱 사원은 타나롯보다 한적하고 일몰 뷰가 더 좋아요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 90분, 그랩 250,000Rp. 우붓에서 40분",
        "best_time": "오후 4시~6시",
        "food": [
            {"name": "Warung Tegak", "price": "나시캄푸르 30,000~50,000Rp", "krw": "약 3,000~5,000원", "tip": "근처 로컬 맛집", "area": "타나롯", "must": "나시캄푸르"},
            {"name": "Tanah Lot Restaurant", "price": "60,000~120,000Rp", "krw": "약 6,000~12,000원", "tip": "사원 뷰 레스토랑", "area": "타나롯", "must": "발리 정식"},
        ],
        "culture": [
            {"name": "타나롯 사원", "price": "60,000Rp", "tip": "바다 위 해양 사원. 일몰 추천", "area": "타나롯"},
            {"name": "바투 볼롱 사원", "price": "포함", "tip": "타나롯보다 한적. 일몰 뷰 더 좋음", "area": "타나롯"},
        ],
        "beach": [
            {"name": "타나롯 해변", "price": "무료", "tip": "사원 주변 산책", "area": "타나롯"},
        ],
        "nature": [
            {"name": "잘란 라이스 테라스", "price": "무료", "tip": "근처 아름다운 논밭", "area": "타나롯"},
        ],
        "shopping": [
            {"name": "타나롯 시장", "price": "다양", "tip": "사원 입구 기념품", "area": "타나롯"},
        ],
        "transport": [
            {"name": "공항-타나롯", "price": "250,000Rp (90분)", "tip": "일몰 시간대 방문 추천"},
        ],
        "hotels": {"budget": "게스트하우스 100,000~200,000Rp/1박", "mid": "리조트 500,000~1,500,000Rp/1박", "high": "아야나 리조트 4,000,000Rp~/1박"},
        "price_comp": [
            {"item": "사원 입장료", "local": "60,000Rp", "tour": "80,000Rp", "hotel": "100,000Rp"},
            {"item": "나시캄푸르", "local": "30,000Rp", "tour": "50,000Rp", "hotel": "80,000Rp"},
        ],
    },
    "베두굴": {
        "desc": "발리 중부의 고원 도시",
        "vibe": "고원과 사원",
        "spots": ["울룬 다누 브라탄 사원", "브라탄 호수", "발리 보타닉 가든", "몽키 포레스트", "베두굴 전통 시장"],
        "hidden": "발리 보타닉 가든은 관광객 거의 없고 열대 식물원 산책 코스가 좋아요",
        "best_season": "4~10월 건기",
        "transport_tip": "공항에서 2시간, 그랩 350,000Rp. 고원이라 서늘함",
        "best_time": "오전 9시~12시",
        "food": [
            {"name": "Lakeview Restaurant", "price": "50,000~100,000Rp", "krw": "약 5,000~10,000원", "tip": "브라탄 호수 뷰", "area": "브라탄 호수", "must": "발리 정식"},
            {"name": "Warung Classic", "price": "25,000~45,000Rp", "krw": "약 2,500~4,500원", "tip": "대표 로컬 맛집", "area": "베두굴", "must": "나시고렝"},
        ],
        "culture": [
            {"name": "울룬 다누 브라탄 사원", "price": "50,000Rp", "tip": "호수 위 사원. 오전 9시 이후 방문", "area": "베두굴"},
        ],
        "beach": [],
        "nature": [
            {"name": "브라탄 호수", "price": "무료", "tip": "고원 호수. 보트 투어 가능", "area": "베두굴"},
            {"name": "발리 보타닉 가든", "price": "20,000Rp", "tip": "열대 식물원. 관광객 거의 없음", "area": "베두굴"},
        ],
        "shopping": [
            {"name": "베두굴 전통 시장", "price": "다양", "tip": "딸기, 채소, 기념품", "area": "베두굴"},
            {"name": "딸기 농장 체험", "price": "50,000~100,000Rp", "tip": "딸기 따기 + 시식", "area": "베두굴"},
        ],
        "transport": [
            {"name": "공항-베두굴", "price": "350,000Rp (2시간)", "tip": "고원 지대 서늘함"},
        ],
        "hotels": {"budget": "게스트하우스 80,000~150,000Rp/1박", "mid": "고원 리조트 300,000~800,000Rp/1박", "high": "문 레이크 호텔 1,500,000Rp~/1박"},
        "price_comp": [
            {"item": "사원 입장료", "local": "50,000Rp", "tour": "70,000Rp", "hotel": "100,000Rp"},
            {"item": "로컬 음식", "local": "25,000Rp", "tour": "45,000Rp", "hotel": "80,000Rp"},
        ],
    },
}

# ============================================================
# 이미지 매핑 로드
# ============================================================
def load_image_mapping():
    for f in [MAPPING_FILE, BASE_DIR / "image_mapping_v2.json"]:
        if f.exists():
            try:
                return json.loads(f.read_text())
            except:
                continue
    return {}

def get_images(area, category, page_index, count=10):
    mapping = load_image_mapping()
    area_imgs = mapping.get(area, {}).get(category, [])
    if not area_imgs:
        return []

    total = len(area_imgs)
    if total <= count:
        return list(area_imgs)

    seed_str = f"{area}_{category}_{page_index}_v9"
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    shuffled = list(area_imgs)
    rng = seed_val
    for i in range(len(shuffled) - 1, 0, -1):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        j_idx = rng % (i + 1)
        shuffled[i], shuffled[j_idx] = shuffled[j_idx], shuffled[i]
    return shuffled[:count]


# ============================================================
# 콘텐츠 생성 엔진
# ============================================================

# 카테고리별 H2 구조 변형
H2_STRUCTURES = {
    "food": [
        ["intro_qa", "places", "price_table", "budget_tips", "related"],
        ["intro_qa", "places", "local_vs_tourist", "must_avoid", "related"],
        ["intro_qa", "morning_lunch_dinner", "price_table", "tips", "related"],
        ["intro_qa", "best_of", "price_table", "seasonal", "related"],
        ["intro_qa", "places", "budget_tips", "review", "related"],
        ["intro_qa", "course", "price_table", "fail_tips", "related"],
        ["intro_qa", "places", "compare", "tips", "related"],
        ["intro_qa", "hidden_restaurants", "price_table", "budget_tips", "related"],
        ["intro_qa", "places", "local_vs_tourist", "tips", "related"],
        ["intro_qa", "morning_lunch_dinner", "price_table", "review", "related"],
        ["intro_qa", "best_of", "compare", "fail_tips", "related"],
        ["intro_qa", "course", "local_vs_tourist", "tips", "related"],
        ["intro_qa", "hidden_restaurants", "compare", "budget_tips", "related"],
        ["intro_qa", "places", "price_table", "seasonal", "related"],
    ],
    "culture": [
        ["intro_qa", "places", "dress_code", "route", "related"],
        ["intro_qa", "places", "tips", "photo_spots", "related"],
        ["intro_qa", "places", "entrance_fee", "guide_needed", "related"],
        ["intro_qa", "best_temples", "dress_code", "tips", "related"],
        ["intro_qa", "places", "route", "fail_tips", "related"],
        ["intro_qa", "places", "tips", "time_needed", "related"],
        ["intro_qa", "hidden_temples", "dress_code", "route", "related"],
        ["intro_qa", "places", "entrance_fee", "photo_spots", "related"],
        ["intro_qa", "best_temples", "tips", "guide_needed", "related"],
        ["intro_qa", "places", "route", "tips", "related"],
        ["intro_qa", "hidden_temples", "entrance_fee", "dress_code", "related"],
        ["intro_qa", "places", "photo_spots", "fail_tips", "related"],
        ["intro_qa", "best_temples", "route", "tips", "related"],
        ["intro_qa", "places", "dress_code", "time_needed", "related"],
    ],
    "beach": [
        ["intro_qa", "places", "time_slot", "wave_safety", "related"],
        ["intro_qa", "places", "sunset_spots", "sunbed_price", "related"],
        ["intro_qa", "best_beaches", "surf_info", "tips", "related"],
        ["intro_qa", "places", "snorkel_info", "shower_facility", "related"],
        ["intro_qa", "places", "time_slot", "food_nearby", "related"],
        ["intro_qa", "hidden_beaches", "wave_safety", "tips", "related"],
        ["intro_qa", "places", "sunset_spots", "tips", "related"],
        ["intro_qa", "best_beaches", "time_slot", "sunbed_price", "related"],
        ["intro_qa", "places", "surf_info", "snorkel_info", "related"],
        ["intro_qa", "hidden_beaches", "sunset_spots", "food_nearby", "related"],
        ["intro_qa", "places", "wave_safety", "tips", "related"],
        ["intro_qa", "best_beaches", "shower_facility", "tips", "related"],
        ["intro_qa", "places", "time_slot", "sunbed_price", "related"],
        ["intro_qa", "hidden_beaches", "surf_info", "tips", "related"],
    ],
    "nature": [
        ["intro_qa", "places", "difficulty", "preparation", "related"],
        ["intro_qa", "places", "best_time", "rainy_day_alt", "related"],
        ["intro_qa", "places", "transport_time", "tips", "related"],
        ["intro_qa", "best_spots", "difficulty", "preparation", "related"],
        ["intro_qa", "places", "best_time", "tips", "related"],
        ["intro_qa", "hidden_spots", "difficulty", "rainy_day_alt", "related"],
        ["intro_qa", "places", "transport_time", "preparation", "related"],
        ["intro_qa", "best_spots", "best_time", "tips", "related"],
        ["intro_qa", "hidden_spots", "transport_time", "difficulty", "related"],
        ["intro_qa", "places", "rainy_day_alt", "tips", "related"],
        ["intro_qa", "best_spots", "difficulty", "tips", "related"],
        ["intro_qa", "hidden_spots", "best_time", "preparation", "related"],
        ["intro_qa", "places", "transport_time", "rainy_day_alt", "related"],
        ["intro_qa", "best_spots", "hidden_spots", "tips", "related"],
    ],
    "shopping": [
        ["intro_qa", "places", "bargaining", "card_payment", "related"],
        ["intro_qa", "places", "price_list", "market_diff", "related"],
        ["intro_qa", "best_shops", "bargaining", "tips", "related"],
        ["intro_qa", "places", "souvenir_guide", "card_payment", "related"],
        ["intro_qa", "hidden_shops", "price_list", "bargaining", "related"],
        ["intro_qa", "places", "market_diff", "tips", "related"],
        ["intro_qa", "best_shops", "souvenir_guide", "card_payment", "related"],
        ["intro_qa", "hidden_shops", "bargaining", "price_list", "related"],
        ["intro_qa", "places", "card_payment", "tips", "related"],
        ["intro_qa", "best_shops", "market_diff", "tips", "related"],
        ["intro_qa", "hidden_shops", "souvenir_guide", "tips", "related"],
        ["intro_qa", "places", "bargaining", "souvenir_guide", "related"],
        ["intro_qa", "best_shops", "price_list", "tips", "related"],
        ["intro_qa", "hidden_shops", "card_payment", "market_diff", "related"],
    ],
    "transport": [
        ["intro_qa", "airport", "grab_info", "scooter_info", "related"],
        ["intro_qa", "routes", "cost_table", "tips", "related"],
        ["intro_qa", "airport", "driver_tour", "grab_info", "related"],
        ["intro_qa", "routes", "scooter_info", "cost_table", "related"],
        ["intro_qa", "airport", "cost_table", "tips", "related"],
        ["intro_qa", "routes", "grab_info", "fail_tips", "related"],
        ["intro_qa", "airport", "driver_tour", "cost_table", "related"],
        ["intro_qa", "routes", "scooter_info", "tips", "related"],
        ["intro_qa", "airport", "grab_info", "fail_tips", "related"],
        ["intro_qa", "routes", "driver_tour", "tips", "related"],
        ["intro_qa", "airport", "scooter_info", "cost_table", "related"],
        ["intro_qa", "routes", "grab_info", "tips", "related"],
        ["intro_qa", "airport", "cost_table", "fail_tips", "related"],
        ["intro_qa", "routes", "driver_tour", "scooter_info", "related"],
    ],
}


def generate_intro(area, category, page_idx, data):
    """경험 중심 도입부 생성 (2500자+ 확보)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_intro_v9"))
    cat_info = CATEGORIES[category]
    spots = data.get("spots", [])
    food = data.get("food", [])
    hidden = data.get("hidden", "")
    best_season = data.get("best_season", "4~10월")
    vibe = data.get("vibe", "")
    desc = data.get("desc", "")

    spot1 = spots[0] if spots else "주요 명소"
    spot2 = spots[1] if len(spots) > 1 else ""
    first_food = food[0]["name"] if food else ""
    food_price = food[0]["price"] if food else ""
    transport_tip = data.get("transport_tip", "")
    best_time = data.get("best_time", "")

    # 30개 도입부 패턴
    templates = [
        # 경험담
        f"{area}{j(area,('을','를'))} 다녀온 후기를 솔직하게 쓸게요. {cat_info['name']} 위주로 돌아봤는데, {spot1}{j(spot1,('에서','에서'))} 시작하면 동선이 좋아요. {transport_tip.split('.')[0] if transport_tip else ''}. 가격 비교와 실패 팁까지 정리했으니 끝까지 읽어보시면 도움이 될 거예요.",
        f"지난달에 {area}{j(area,('에','에'))} 다녀왔어요. {cat_info['name']} 정보를 찾다가 직접 가보니 검색해서 알게 된 것과 실제가 좀 달랐어요. {first_food}{j(first_food,('은','는'))} 생각보다 괜찮았고, {spot1}{j(spot1,('은','는'))} 기대 이상이었어요. 솔직하게 장단점 다 쓸게요.",
        f"{area} {cat_info['name']} 계획 중이신가요? 저도 같은 고민했거든요. 직접 가본 결과, {spot1}{j(spot1,('부터','부터'))} 시작하고 {first_food}{j(first_food,('에서','에서'))} 점심 먹는 코스가 가장 효율적이었어요. 예산별 추천도 아래에 정리했어요.",

        # 결론先行
        f"결론부터 말하면, {area}의 {cat_info['name']}은 {best_season.split(' ')[0]}이 가장 좋아요. {spot1} 추천이고, {first_food}에서 식사하세요. {hidden if hidden else spot2}도 놓치지 마시고요. 가격 비교표도 준비했어요.",
        f"{area} {cat_info['name']} 핵심만 추리면: 1) {spot1} 2) {first_food} 3) {hidden if hidden else spot2}. 이 세 가지만 기억하세요. 아래에서 동선, 가격, 시간대별 팁을 상세히 정리할게요.",

        # 질문형
        f"'{area} {cat_info['name']} 어디가 좋나요?' 저도 출발 전에 같은 질문을 했어요. 막상 가보니 생각보다 선택지가 많더라고요. {spot1}부터 {hidden if hidden else spot2}까지 직접 가본 기준으로 추천과 비추천을 정리할게요.",

        # 시간순
        f"{area}에 도착한 첫째 날, {cat_info['name']} 계획을 짰어요. 오전에 {spot1} 방문, 점심에 {first_food}, 오후에 {hidden if hidden else spot2} 코스로 잡았는데, 실제 가보니 이 동선이 가장 효율적이었어요. 다만 한 가지 실수가 있었는데, 아래에서 알려드릴게요.",

        # 비교형
        f"검색해서 알게 된 {area} {cat_info['name']} 정보 vs 실제 가본 후기. 솔직하게 비교하면, 가격 정보는 대부분 맞았는데 동선 정보는 좀 달랐어요. {transport_tip.split('.')[0] if transport_tip else ''}. 자세한 비교는 아래에서 할게요.",

        # 감성형
        f"{area}에서 보낸 시간 중 가장 좋았던 건 {cat_info['name']}이었어요. {best_time}에 {spot1}에 도착했을 때의 그 분위기가 아직도 기억나요. 사진으로만 보다가 직접 가니까 정말 달랐어요. 이 글에서 그 느낌을 전달해드릴게요.",

        # 비용 중심
        f"{area} {cat_info['name']} 예산이 궁금하셨죠? 로컬 기준 하루 500,000Rp(약 50,000원)이면 충분해요. {first_food}에서 {food_price}에 식사하고, {spot1} 입장료 포함하면 이 정도 나와요. 예산별 상세 비교는 본문에서 확인하세요.",

        # 실용 가이드
        f"{area} {cat_info['name']} 완벽 가이드입니다. 직접 가본 기준으로 정리했어요. {spot1} 추천부터 {first_food} 후기까지, 가격과 위치와 팁 모두 다뤘어요. 특히 {hidden if hidden else '숨겨진 장소'}도 놓치지 마세요.",

        # 현지인 관점
        f"현지인 친구가 추천한 {area} {cat_info['name']} 코스예요. 관광객이 잘 모르는 곳도 있어서 좋았어요. {first_food}는 현지 가격으로 먹을 수 있고, {spot1}도 사람이 적은 시간대에 가면 더 좋아요.",

        # 재방문
        f"{area}에 두 번째 방문이에요. 첫 번째에는 놓쳤던 {cat_info['name']} 스팟들을 이번에 다녀왔어요. {spot1}은 처음 갔을 때보다 더 좋았고, {hidden if hidden else spot2}는 새로 발견한 곳이에요.",

        # 팁 공유
        f"발리 여러 번 다니면서 알게 된 {area} {cat_info['name']} 꿀팁이에요. {spot1}은 {best_time}에 가면 사람이 적고, {first_food}는 예약하면 기다리지 않아요. 시간과 비용을 절약하는 팁을 정리했어요.",

        # 문제 해결
        f"{area} {cat_info['name']} 어디서부터 시작해야 할지 모르겠다면 이 글 하나면 돼요. {spot1}부터 {first_food}까지 추천 코스를 정리했고, 가격 비교표와 시간대별 팁도 포함했어요. {transport_tip.split('.')[0] if transport_tip else ''}.",
    ]

    intro = templates[page_idx % len(templates)]
    return intro


def generate_places_html(area, category, page_idx, data):
    """추천 장소 HTML 생성 (상세 설명 포함)"""
    cat_data = data.get(category, [])
    if not cat_data:
        return ""

    rng = random.Random(hash(f"{area}_{category}_{page_idx}_places_v9"))
    start = (page_idx * 2) % len(cat_data)
    selected = []
    for i in range(min(5, len(cat_data))):
        selected.append(cat_data[(start + i) % len(cat_data)])

    cat_info = CATEGORIES[category]
    html = ""

    # 장소별 상세 설명 풀
    detail_pool = {
        "food": [
            f"{area}에서 이 집을 추천하는 이유는 가격 대비 퀄리티가 확실히 다르기 때문이에요. 비슷한 가격대의 다른 집과 비교했을 때, 여기는 재료가 신선하고 양도 충분해요. 다만 점심시간(12시~13시)에는 웨이팅이 있을 수 있으니 11시 30분쯤 도착하거나, 14시 이후에 가면 기다리지 않고 먹을 수 있어요. 주문은 메뉴판의 1번이나 2번이 대표 메뉴인데, 현지인들은 보통 3번을 많이 시켜요.",
            f"이 집의 장점은 분위기예요. 실내 좌석과 야외 좌석이 있는데, 날씨가 좋으면 야외 좌석을 추천해요. 다만 우기철(11~3월)에는 갑자기 비가 올 수 있으니 실내 좌석이 안전해요. 음료는 생맥주(35,000Rp)가 가성비 좋고, 칵테일은 80,000~120,000Rp 정도예요. 직원들이 친절하고 영어도 잘 통해서 주문이 편해요.",
            f"가격 대비 만족도가 높은 곳이에요. 2인 기준으로 150,000~250,000Rp(약 15,000~25,000원)이면 충분히 배부르게 먹을 수 있어요. 다만 카드 결제가 안 되는 곳이 있으니 현금을 미리 준비하세요. 가장 가까운 ATM은 도보 5분 거리에 있어요.",
            f"이 집은 예약이 필수는 아니지만, 성수기(7~8월)에는 현장 예약이 안 될 수도 있어요. 미리 전화하거나 인스타그램 DM으로 예약하면 기다리지 않아요. 주차 공간은 제한적이어서 스쿠터나 그랩으로 이동하는 게 좋아요.",
            f"근처에 다른 맛집도 있어서 코스로 묶으면 좋아요. 이 집에서 식사 후 도보 5분 거리에 있는 카페에서 디저트를 먹는 코스를 추천해요. 오후 3시~5시는 비교적 한가해서 여유롭게 즐길 수 있어요.",
        ],
        "culture": [
            f"이 사원은 {area}에서 가장 오래된 사원 중 하나예요. 건축 양식이 독특해서 사진이 정말 잘 나오는데, 특히 동쪽에서 서쪽을 바라보는 각도가 가장 예뻐요. 일몰 시간대에 가면 황금빛 조명이 사원을 비춰서 분위기가 최고예요. 다만 제사 중인 장면은 촬영 금지이니 현지인에게 허락을 구하세요.",
            f"입장료는 포함이지만, 기부금 형식으로 10,000~20,000Rp를 내는 게 예의예요. 사롱(긴 스카프) 착용 필수인데, 입구에서 무료 대여 가능하지만 직접 가져가는 게 위생적이에요. 신발은 벗어야 하니 슬리퍼보다 운동화가 편해요.",
            f"가이드 투어를 하면 사원의 역사와 의미를 더 잘 알 수 있어요. 비용은 200,000~400,000Rp 정도인데, 1~2시간 코스예요. 자유여행이면 사원 입구에서 안내판을 읽는 것만으로도 충분해요. 다만 영어 안내판이 없는 곳도 있어서 미리 검색하고 가는 게 좋아요.",
            f"사원 주변에는 기념품 가게가 많아요. 여기서 사면 다른 곳보다 20~30% 비싸니, 기념품은 우붓이나 시내에서 미리 사는 게 좋아요. 대신 사원에서만 구할 수 있는 특별한 기념품이 있으면 여기서 사는 것도 괜찮아요.",
            f"사원 방문 후 근처 카페에서 쉬는 코스를 추천해요. 도보 5분 거리에 분위기 좋은 카페가 있어서, 사원 구경 후 커피 한 잔 하면서 사진을 정리하기 좋아요.",
        ],
        "beach": [
            f"이 해변은 {area}에서 가장 인기 있는 해변이에요. 선셋 시간대(오후 5시~6시 30분)에 가면 가장 아름다운 풍경을 볼 수 있어요. 비치클럽 선베드는 무료인 곳도 있지만 최소 음료 1잔(80,000~200,000Rp) 주문이에요. 프라이빗 비치 선베드는 50,000~100,000Rp/일이에요.",
            f"서핑 초보자도 강습 받으면 2시간이면 설 수 있어요. 강습비 150,000~250,000Rp에 보드 포함이에요. 강사는 대부분 영어를 잘해서 소통이 편해요. 다만 파도가 강한 날(우기)에는 초보자에게 위험할 수 있으니, 강사에게 안전 여부를 꼭 확인하세요.",
            f"해변에서 물건 파는 사람이 다가올 수 있어요. 단호하게 '아니요'라고 하면 됩니다. 가격을 물어보면 사는 분위기로 몰아가니까, 관심 없으면 아예 눈을 마주치지 않는 게 좋아요.",
            f"샤워시설은 해변 근처에 있어요. 10,000~20,000Rp 정도인데, 수압이 약한 곳도 있어요. 타월은 미리 챙기세요. 해변에서 나올 때 모래를 털고 나오면 주변 상점에서 눈치를 줄 수 있어요.",
            f"해변 근처에 맛집이 많아요. 선셋 후 저녁 식사를 하려면 미리 예약하세요. 성수기에는 현장 예약이 안 될 수 있어요. 가격은 1인 100,000~300,000Rp 정도예요.",
        ],
        "nature": [
            f"이 명소는 {area}에서 가장 인기 있는 자연 명소예요. 새벽에 가면 안개 없이 깨끗한 뷰를 볼 수 있어요. 오전 8시~10시가 가장 좋고, 오후에는 관광객이 많아져요. 우기(11~3월)에는 폭포 수량이 풍부하지만 길이 미끄러워요.",
            f"편한 운동화 필수예요. 샌들로 트레킹하면 다칠 수 있어요. 모기 기피제도 챙기세요. 열대 지역이라 모기가 많아요. 생수는 미리 사두세요. 중간에 파는 곳이 없거나 가격이 2~3배 비싸요.",
            f"가이드 투어를 하면 안전하고 정보도 많이 알 수 있어요. 비용은 200,000~400,000Rp 정도인데, 2~3시간 코스예요. 자유여행이면 입구에서 안내판을 읽는 것만으로도 충분해요.",
            f"사진 포인트가 따로 있어요. 입구에서 왼쪽으로 가면 뷰가 더 좋아요. 대부분의 관광객은 오른쪽으로 가는데, 왼쪽이 한적하고 사진이 잘 나와요.",
            f"우천 시 대안으로 근처 카페나 온천을 추천해요. 우기철에는 갑작스러운 소나기가 올 수 있으니 우산 필수예요.",
        ],
        "shopping": [
            f"이 곳은 {area}에서 가장 큰 쇼핑몰/시장이에요. 가격은 로컬 기준으로 저렴하지만, 관광객 가격과 현지인 가격이 다른 곳이 있어요. 흥정이 필수예요. 첫 가격의 30~50% 수준으로 시작하세요.",
            f"카드 결제가 가능한 곳도 있지만, 로컬 시장과 기념품 가게는 현금만 받는 곳이 많아요. 현금 충분히 챙기세요. ATM은 편의점에 있어요.",
            f"기념품으로 발리 커피, 코코넛 오일, 라탄 가방, 사롱(전통 직물)이 대표적이에요. 은세공은 우붓에서 사는 게 저렴해요. 면세점은 공항에만 있어요.",
            f"마사지는 관광지보다 로컬 가게가 50% 저렴해요. 1시간 60,000~100,000Rp면 충분해요. 프리미엄 스파는 150,000~400,000Rp/1시간이에요.",
            f"쇼핑몰 내부에는 푸드코트도 있어서 쇼핑 중간에 식사하기 좋아요. 가격은 20,000~50,000Rp로 저렴해요.",
        ],
        "transport": [
            f"이 교통수단은 {area}에서 가장 편하고 저렴한 방법이에요. 그랩은 현금/카드 모두 가능하고, 미터기로 자동 계산돼요. 다만 피크 시간(오전 7~9시, 오후 5~7시)에는 할증이 붙어요.",
            f"스쿠터 렌트는 국제운전면허증 필수예요. 없으면 벌금 500,000Rp. 헬멧 착용 필수이고, 보험 확인하세요. 좌측 통행이에요. 밤에는 스쿠터보다 그랩이 안전해요.",
            f"전용 드라이버 8시간 기준 500,000~700,000Rp(약 50,000~70,000원)이에요. 여러 명이면 그랩보다 가성비 좋아요. 점심은 기사와 함께 먹으면 식대를 챙겨주는 게 예의예요.",
            f"고젝(Gojek)은 그랩 대안이에요. 오토바이 택시도 가능해서 교통체증이 심한 시간대에 유용해요. 다만 안전을 위해 헬멧을 꼭 착용하세요.",
            f"장거리 이동은 전용 드라이버를 고용하는 게 편해요. 8시간 기준 500,000~700,000Rp. 여러 명이면 1인당 100,000~200,000Rp 정도예요.",
        ],
    }

    for i, place in enumerate(selected):
        name = place.get("name", "")
        price = place.get("price", "")
        krw = place.get("krw", "")
        tip = place.get("tip", "")
        place_area = place.get("area", area)
        must = place.get("must", "")

        details = detail_pool.get(category, detail_pool["food"])
        detail = details[(page_idx + i) % len(details)]

        html += f'''<div style="margin:16px 0;padding:18px;background:#fafafa;border-radius:10px;border-left:4px solid #FF6B35">
<h3 style="font-size:1.1em;font-weight:700;margin:0 0 12px;color:#333">{i+1}. {name}</h3>
<p style="margin:0 0 8px;line-height:1.8"><strong>가격:</strong> {price} {f"({krw})" if krw else ""}</p>
<p style="margin:0 0 8px;line-height:1.8"><strong>위치:</strong> {place_area}</p>
<p style="margin:0 0 8px;line-height:1.8"><strong>팁:</strong> {tip}</p>
{f'<p style="margin:0 0 8px;line-height:1.8"><strong>추천 메뉴:</strong> {must}</p>' if must else ''}
<p style="margin:0;line-height:1.7;color:#555;font-size:0.95em">{detail}</p>
</div>'''

    return html


def generate_price_table_html(price_comp):
    """가격 비교표 HTML"""
    if not price_comp:
        return ""
    html = '''<div style="margin:20px 0;overflow-x:auto">
<table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white">
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">로컬 직접</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">투어 포함</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">호텔 내</th>
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
<p style="margin:8px 0;font-size:.85em;color:#666">로컬 = 직접 방문 / 투어 = 투어 예약 시 / 호텔 = 호텔 내 이용 시</p>'''
    return html


def generate_qa_html(area, category, page_idx, data):
    """고유 Q&A 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_qa_v9"))
    spots = data.get("spots", [])
    food = data.get("food", [])
    transport_tip = data.get("transport_tip", "")
    best_time = data.get("best_time", "")
    hidden = data.get("hidden", "")
    hotels = data.get("hotels", {})
    price_comp = data.get("price_comp", [])

    spot1 = spots[0] if spots else ""
    first_food = food[0] if food else {}

    # 지역+카테고리별 고유 Q&A 풀
    qa_pool = []

    if category == "food":
        qa_pool = [
            (f"{area} 가성비 맛집은 어디인가요?",
             f"{first_food.get('name', '현지 와룽')}에서 {first_food.get('price', '30,000~50,000Rp')}면 든든하게 먹을 수 있어요. {first_food.get('tip', '')}"),
            (f"{area}에서 혼밥 가능한가요?",
             f"대부분의 와룽은 혼밥 가능해요. 특히 로컬 와룽은 1인석이 있어서 편하게 먹을 수 있어요. 비치클럽은 2인 이상을 권하는 곳도 있어요."),
            (f"{area} 음점 주의사항이 있나요?",
             f"생수는 반드시 사서 마시고, 길거리 음식은 사람이 많은 곳에서 먹는 게 안전해요. 매운 걸 못 먹으면 'tidak pedas'라고 말하세요."),
            (f"{area} 브런치 카페 추천해주세요",
             f"아침은 호텔 조식이 가성비 최고예요. 별도로 카페를 가고 싶다면 오전 10시 전에 가면 웨이팅이 짧아요."),
        ]
    elif category == "culture":
        qa_pool = [
            (f"{area} 사원 방문 시 복장 규정은?",
             f"사롱(긴 스카프) 착용 필수예요. 입구에서 무료 대여 가능한 곳도 있지만, 직접 가져가는 게 위생적이에요."),
            (f"{area} 사원에서 사진 촬영 가능한가요?",
             f"대부분의 사원에서 사진 촬영 가능하지만, 제사 중인 장면은 촬영 금지예요. 촬영 전 현지인에게 허락을 구하세요."),
            (f"{area} 사원 방문 추천 시간대는?",
             f"{best_time}에 방문하는 게 좋아요. 오후에는 관광객이 많아지고 더워져요."),
            (f"{area} 가이드 투어 vs 자유여행?",
             f"사원의 역사와 의미를 알고 싶다면 가이드 투어 추천이에요. 비용은 200,000~400,000Rp 정도예요."),
        ]
    elif category == "beach":
        qa_pool = [
            (f"{area} 일몰 보기 좋은 해변은?",
             f"{spot1}이 대표적이에요. 선셋 시간대에 비치클럽 좌석을 잡으면 분위기 최고예요."),
            (f"{area} 서핑 초보자도 할 수 있나요?",
             f"네, 강습 받으면 2시간이면 설 수 있어요. 강습비 150,000~250,000Rp에 보드 포함이에요."),
            (f"{area} 해변에서 수영 가능한가요?",
             f"파도가 강한 날에는 수영 금지예요. 빨간 깃발 표시를 꼭 확인하세요. 안전한 곳만 수영하세요."),
            (f"{area} 비치클럽 가격은?",
             f"음료 80,000~200,000Rp 정도예요. 선베드 무료인 곳도 있지만 최소 음료 1잔 주문이에요."),
        ]
    elif category == "nature":
        qa_pool = [
            (f"{area} 트레킹 난이도는?",
             f"대부분 중간 난이도예요. 편한 운동화 필수고, 모기 기피제도 챙기세요. 새벽 출발이 필수예요."),
            (f"{area} 우기에도 방문 가능한가요?",
             f"우기(11~3월)에는 폭포 수량이 풍부하지만 길이 미끄러워요. 우산 필수, 트레킹은 가이드 추천이에요."),
            (f"{area} 준비물은 뭐가 필요한가요?",
             f"편한 운동화, 모기 기피제, 생수, 우산, 선크림 SPF50+. 화산 트레킹이면 겉옷도 챙기세요."),
            (f"{area} 가는 방법과 이동 시간은?",
             f"{transport_tip}"),
        ]
    elif category == "shopping":
        qa_pool = [
            (f"{area}에서 흥정 어떻게 하나요?",
             f"첫 가격의 30~50% 수준으로 시작하세요. 단호하게 '아니요'라고 하면 더 내려가요. 카드보다 현금이 흥정에 유리해요."),
            (f"{area}에서 카드 결제 가능한가요?",
             f"대형 쇼핑몰은 가능하지만 로컬 시장과 기념품 가게는 현금만 받는 곳이 많아요. 현금 충분히 챙기세요."),
            (f"{area} 기념품 추천은?",
             f"발리 커피, 코코넛 오일, 라탄 가방, 사롱(전통 직물)이 대표적이에요. 은세공은 우붓에서 사는 게 저렴해요."),
            (f"{area} 면세점은 어디에 있나요?",
             f"공항에만 있어요. 시내에서 미리 구매하세요. 시내 가격이 면세점보다 저렴한 경우도 많아요."),
        ]
    elif category == "transport":
        qa_pool = [
            (f"{area} 그랩 이용 팁은?",
             f"그랩이 가장 편하고 저렴해요. 현금/카드 모두 가능. 다만 피크 시간에는 할증이 붙어요."),
            (f"{area} 스쿠터 렌트 조건은?",
             f"국제운전면허증 필수! 없으면 벌금 500,000Rp. 헬멧 착용 필수이고, 보험 확인하세요."),
            (f"{area} 공항에서 가는 가장 저렴한 방법은?",
             f"그랩이 가장 저렴해요. 사전 예약 드라이버는 약간 비싸지만 안전하고 편해요."),
            (f"{area} 교통체증 피하는 방법은?",
             f"오전 10시 전, 오후 2시~4시가 비교적 한가해요. 오전 7~9시, 오후 5~7시는 피하세요."),
        ]

    # 페이지별로 다른 Q&A 선택
    if not qa_pool:
        return ""
    q, a = qa_pool[page_idx % len(qa_pool)]

    return f'''<div style="margin:20px 0;padding:20px;background:linear-gradient(135deg,#e8f5e9,#f1f8e9);border-radius:12px;border:1px solid #c8e6c9">
<p style="margin:0 0 8px;font-weight:700;color:#2e7d32;font-size:1.05em">Q. {q}</p>
<p style="margin:0;color:#333;line-height:1.7">{a}</p>
</div>'''


def generate_budget_tips_html(area, category, data):
    """예산 팁 HTML"""
    hotels = data.get("hotels", {})
    rng = random.Random(hash(f"{area}_{category}_budget_v9"))

    budget = hotels.get("budget", "100,000~200,000Rp/1박")
    mid = hotels.get("mid", "500,000~1,500,000Rp/1박")

    tips = [
        f"숙소는 예산형({budget})으로 잡고, 음식은 로컬 와룽에서 해결하면 하루 300,000~500,000Rp(약 30,000~50,000원)이면 충분해요.",
        f"중급 숙소({mid})를 원하시면 비수기에 예약하면 20~30% 저렴해요. 11~3월이 비수기예요.",
        f"그랩 할인 코드를 미리 확인하세요. 첫 이용 시 할인되는 경우가 많아요.",
        f"생수는 편의점에서 사면 5,000Rp인데 관광지에서는 15,000Rp예요. 미리 사두세요.",
        f"호텔 조식이 포함이면 꼭 이용하세요. 아침 식사 비용을 따로 쓸 필요가 없어요.",
        f"마이리얼트립에서 투어/티켓을 미리 예약하면 현장 구매보다 20~30% 저렴해요.",
    ]

    selected = []
    for i in range(3):
        selected.append(tips[(page_idx_hash := hash(f"{area}_{category}_{i}_tip_v9")) % len(tips)])

    html = '<ul style="padding-left:20px;margin:16px 0">'
    for tip in selected:
        html += f'<li style="margin-bottom:8px;line-height:1.7">{tip}</li>'
    html += '</ul>'
    return html


def generate_related_links_html(area, category, page_idx):
    """관련 지역 링크"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_related_v9"))
    other_areas = [a for a in AREAS if a != area]
    selected = rng.sample(other_areas, min(3, len(other_areas)))
    cat_info = CATEGORIES[category]

    html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0">'
    for sa in selected:
        p = (page_idx + 1) % 14 + 1
        html += f'<a href="/{sa}/{category}/{p:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{sa} {cat_info["name"]}</a>'
    html += '</div>'
    return html


def generate_coupon_html():
    """쿠폰 + CTA HTML"""
    return f'''<div style="margin:24px 0;text-align:center">
<a href="{AFFILIATE_URL}" target="_blank" rel="sponsored nofollow noopener">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인" style="max-width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12)" loading="lazy" />
</a>
<p style="margin-top:10px;font-size:.85em;color:#666">마이리얼트립 할인쿠폰 - 투어/티켓/숙소 최대 30% 할인</p>
</div>'''


def generate_images_html(area, category, page_idx):
    """이미지 10장 HTML (고유 ALT)"""
    images = get_images(area, category, page_idx, 10)
    if not images:
        return ""

    # 이미지별 고유 ALT 생성
    alt_descriptions = generate_image_alts(area, category, page_idx, len(images))

    html = ""
    for i, img in enumerate(images):
        img_path = f"../../images/{area}/{category}/{img}"
        alt = alt_descriptions[i] if i < len(alt_descriptions) else f"{area} 여행 사진"
        html += f'''<figure style="margin:20px 0;text-align:center">
<img src="{img_path}" alt="{alt}" loading="lazy" style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)" />
<figcaption style="margin-top:8px;font-size:.85em;color:#666">{alt}</figcaption>
</figure>
'''
    return html


def generate_image_alts(area, category, page_idx, count):
    """이미지별 고유 ALT 텍스트 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_alt_v9"))
    data = BALI_DATA.get(area, {})
    spots = data.get("spots", [])
    food = data.get("food", [])

    alts = []
    for i in range(count):
        if i == 0:
            # 첫 번째 이미지는 항상 쿠폰
            alts.append("마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인")
            continue

        # 지역+카테고리+인덱스별 고유 ALT
        alt_pool = get_alt_pool(area, category, data)
        idx = (i - 1 + page_idx * 3) % len(alt_pool)
        alts.append(alt_pool[idx])

    return alts


def get_alt_pool(area, category, data):
    """지역+카테고리별 ALT 풀 생성"""
    spots = data.get("spots", [])
    food = data.get("food", [])
    desc = data.get("desc", "")

    cat_alts = {
        "food": [f"{area} {f['name']} {f.get('area', '')} 사진" for f in food[:6]] +
                [f"{area} 로컬 와룽 내부 분위기", f"{area} 전통 시장 음식 진열대",
                 f"{area} 카페 브런치 메뉴", f"{area} 해산물 레스토랑 그릴"],
        "culture": [f"{s} 입구 전경" for s in spots[:3]] +
                   [f"{area} 사원 힌두 건축 양식 디테일", f"{area} 전통 공연 무대 장면",
                    f"{area} 사원 제단 꽃 공물", f"{area} 예술 공방 작업 모습",
                    f"{area} 사원 수호신 석조상", f"{area} 마을 주민 일상 풍경"],
        "beach": [f"{s} 전경" for s in spots[:3]] +
                 [f"{area} 해변 일몰 골든아워", f"{area} 서핑 강습 장면",
                  f"{area} 비치클럽 선베드 풍경", f"{area} 해변 산책로 아침 풍경",
                  f"{area} 해변 모래사장 일몰 실루엣", f"{area} 스노클링 포인트 수중"],
        "nature": [f"{s} 전경" for s in spots[:3]] +
                  [f"{area} 열대 우림 트레킹 코스", f"{area} 폭포 아래 천연 수영장",
                   f"{area} 라이스 테라스 새벽 안개", f"{area} 화산 일출 실루엣",
                   f"{area} 강변 골든아워 풍경", f"{area} 열대 식물원 전경"],
        "shopping": [f"{area} 아트 마켓 기념품 진열대", f"{area} 부티크숍 쇼윈도",
                     f"{area} 마사지숍 아로마 오일 선반", f"{area} 기념품숍 흥정 장면",
                     f"{area} 시장 열대 과일 가게", f"{area} 스파 내부 마사지 침대",
                     f"{area} 전통 직물 염색 시연", f"{area} 은세공 공방 장인 작업"],
        "transport": [f"{area} 공항 이동 차량 창밖 풍경", f"{area} 스쿠터 렌트숍 주차장",
                      f"{area} 그랩 택시 호출 화면", f"{area} 도로 교통체증 풍경",
                      f"{area} 시내 도보 이동 관광객", f"{area} 호텔 셔틀 차량",
                      f"{area} 시내 교차로 현지인 통근", f"{area} 골목 산책 풍경"],
    }

    pool = cat_alts.get(category, [f"{area} {CATEGORIES[category]['name']} 여행 사진"])
    return pool if pool else [f"{area} 여행 사진"]


def generate_extra_sections(area, category, page_idx, data):
    """카테고리별 추가 섹션 (H2 구조 다양화)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_extra_v9"))
    sections = []
    spots = data.get("spots", [])

    # 비추천/실패 팁
    fail_tips = [
        f"{area}에서 가장 많이 하는 실수는 성수기(7~8월)에 예약 없이 가는 거예요. 최소 2주 전에 미리 예약하세요.",
        f"관광지 바로 앞 음식점은 가격이 2~3배 비싸요. 1~2블록만 걸어가면 가성비 맛집이 있어요.",
        f"우기(11~3월)에 {area}를 방문하면 갑작스러운 소나기를 만날 수 있어요. 우산은 필수로 챙기세요.",
        f"택시 미터기를 안 켜는 기사가 있어요. 탑승 전에 미터기 또는 그랩 사용을 확인하세요.",
        f"사원에서 짧은 반바지나 민소매는 입장이 거부될 수 있어요. 사롱을 미리 준비하세요.",
    ]

    # 시간대별 팁
    time_tips = [
        f"오전 7~9시: {area}에서 가장 한가한 시간. 사진 찍기 좋아요.",
        f"오전 10시~오후 2시: 관광객 피크. 그늘에서 쉬는 게 좋아요.",
        f"오후 3~5시: 다시 관광 시작. 선셋 전 시간대가 분위기 좋아요.",
        f"오후 5~7시: 선셋 타임. 서쪽 해변에서는 꼭 이 시간에 가세요.",
        f"저녁 7~9시: 레스토랑 피크 시간. 예약했으면 기다리지 않아요.",
    ]

    # 우천/성수기 팁
    weather_tips = [
        f"우기({area}는 11~3월)에는 실내 장소 위주로 코스를 짜세요. 사원, 카페, 쇼핑몰 추천이에요.",
        f"성수기(7~8월)에는 숙소 가격이 30~50% 올라요. 비수기(2~3월, 11월)가 가성비 최고예요.",
        f"열대 소나기는 보통 30분~1시간이에요. 비가 그치면 다시 맑아지니 잠시 카페에서 기다리세요.",
    ]

    # 추천/비추천 대상
    recommend_tips = [
        f"추천: 혼자 여행하는 분, 커플 여행, 사진 찍기 좋아하는 분",
        f"비추천: 어린 아이 동반 가족(이동이 많음), 야간 활동을 원하는 분",
        f"추천: 예산형 여행자, 로컬 음식을 좋아하는 분",
        f"비추천: 고급 리조트만 원하는 분, 이동 시간에 민감한 분",
    ]

    # 카테고리별 맞춤 섹션
    if category == "food":
        sections.append(("추천과 비추천", rng.choice(recommend_tips)))
        sections.append(("시간대별 팁", f"아침은 호텔 조식이 가성비 최고예요. 점심은 로컬 와룽(11시~13시), 저녁은 레스토랑 예약(18시~20시) 추천이에요. {area}의 피크 시간은 12시~13시이니 이 시간은 피하세요."))
    elif category == "culture":
        sections.append(("복장 규정", "사롱(긴 스카프) 착용 필수. 입구에서 무료 대여 가능하지만 직접 가져가는 게 위생적이에요. 신발은 벗어야 하니 슬리퍼보다 운동화가 편해요."))
        sections.append(("사진 포인트", f"{spots[0] if spots else area} 사원에서는 동쪽에서 서쪽을 바라보는 각도가 가장 사진이 잘 나와요. 일몰 시간대면 황금빛 조명이 사원을 비춰요."))
    elif category == "beach":
        sections.append(("파도 안전 정보", "파도가 강한 날에는 수영 금지. 빨간 깃발 표시를 꼭 확인하세요. 서핑은 건기(4~10월)가 가장 좋아요. 파도 높이는 Windguru 앱으로 미리 확인하세요."))
        sections.append(("선베드 가격", f"비치클럽 선베드는 무료인 곳도 있지만 최소 음료 1잔(80,000~200,000Rp) 주문이에요. 프라이빗 비치 선베드는 50,000~100,000Rp/일이에요."))
    elif category == "nature":
        sections.append(("체력 난이도", f"대부분 중간 난이도예요. 편한 운동화 필수, 모기 기피제도 챙기세요. 새벽 출발이 필수예요. 화산 트레킹이면 겉옷도 챙기세요. {area}는 해발이 높은 곳이 있어요."))
        sections.append(("우천 대안", "우기에는 폭포 수량이 풍부하지만 길이 미끄러워요. 우산 필수, 트레킹은 가이드 추천이에요. 실내 카페나 온천으로 대체할 수 있어요."))
    elif category == "shopping":
        sections.append(("흥정 가이드", "첫 가격의 30~50% 수준으로 시작하세요. 단호하게 '아니요'라고 하면 더 내려가요. 카드보다 현금이 흥정에 유리해요. 2개 이상 사면 추가 할인을 요청하세요."))
        sections.append(("카드 가능 여부", "대형 쇼핑몰은 카드 가능하지만 로컬 시장과 기념품 가게는 현금만 받는 곳이 많아요. 현금 충분히 챙기세요. ATM은 편의점에 있어요."))
    elif category == "transport":
        sections.append(("기사 투어 비용", f"전용 드라이버 8시간 기준 500,000~700,000Rp(약 50,000~70,000원)이에요. 여러 명이면 그랩보다 가성비 좋아요. 점심은 기사와 함께 먹으면 식대를 챙겨주는 게 예의예요."))
        sections.append(("스쿠터 주의사항", "국제운전면허증 필수! 없으면 벌금 500,000Rp. 헬멧 착용 필수, 보험 확인하세요. 좌측 통행이에요. 밤에는 스쿠터보다 그랩이 안전해요."))

    html = ""
    for title, content in sections:
        html += f'''<h3 style="font-size:1.1em;font-weight:700;margin:20px 0 10px;color:#333">{title}</h3>
<p style="margin:0 0 12px;line-height:1.8">{content}</p>
'''

    return html


def generate_episode_html(area, page_idx, data):
    """여행 에피소드"""
    rng = random.Random(hash(f"{area}_{page_idx}_episode_v9"))
    spots = data.get("spots", [])
    food = data.get("food", [])

    spot = rng.choice(spots) if spots else "해변"
    food_name = rng.choice([f["name"] for f in food]) if food else "현지 음식"

    episodes = [
        f"{area}에서의 마지막 날, {spot}에서 일몰을 보면서 '다시 오고 싶다'는 생각이 들었어요. {food_name}에서 먹은 마지막 저녁 식사도 잊을 수 없고요.",
        f"비가 갑자 와서 {spot} 근처 카페에서 2시간을 기다렸는데, 오히려 그 시간이 더 좋았어요. 빗소리 들며 마신 {area} 커피 맛이 아직도 기억나요.",
        f"{area}에서 스쿠터를 빌려서 돌아다녔는데, 길을 잘못 들어서 발견한 숨겨진 해변이 정말 예뻤어요. 여행은 역시 예상치 못한 곳에서 추억이 생기더라고요.",
        f"{spot}에서 사진을 찍고 있는데 현지 아이들이 같이 찍자고 다가왔어요. 소통은 영어+몸짓이었는데, 그 미소가 아직도 기억에 남아요.",
        f"{food_name}에서 주문 실수로 다른 메뉴가 나왔는데, 오히려 그게 더 맛있었어요. 여행에서의 실패는 때로는 행운이에요.",
        f"{area}에서 혼자 여행했는데, 오히려 혼자여서 더 자유롭게 즐길 수 있었어요. 원하는 곳에서 원하는 시간만큼 있을 수 있다는 게 최고예요.",
    ]

    return f'<p style="margin:16px 0;line-height:1.8;padding:16px;background:#f8f9fa;border-radius:8px;border-left:3px solid #FF6B35">{rng.choice(episodes)}</p>'


def generate_footer_html():
    """하단 푸터"""
    return f'''<footer style="text-align:center;padding:30px;color:var(--text-light);font-size:0.85rem;margin-top:40px;border-top:1px solid #eee">
<p>이 글에는 <a href="{AFFILIATE_URL}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립</a> 제휴 링크가 포함되어 있습니다.</p>
<p>링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.</p>
<p style="margin-top:10px">JP Travel Bali &copy; {CURRENT_YEAR}</p>
</footer>'''


def generate_html(area, category, page_idx):
    """단일 HTML 페이지 전체 생성"""
    data = BALI_DATA.get(area, {})
    cat_info = CATEGORIES[category]

    # SEO 제목 생성
    title = generate_seo_title(area, category, page_idx, data)
    meta_desc = generate_meta_desc(area, category, page_idx, data)
    meta_keywords = generate_keywords(area, category, data)

    # 읽기 시간 (평균 2500자 기준 6분)
    read_time = "약 6분"

    # 도입부
    intro = generate_intro(area, category, page_idx, data)

    # H2 구조 선택
    structures = H2_STRUCTURES.get(category, H2_STRUCTURES["food"])
    structure = structures[page_idx % len(structures)]

    # 콘텐츠 섹션들 생성
    content_sections = []

    for section_type in structure:
        if section_type == "intro_qa":
            content_sections.append(("자주 묻는 질문", generate_qa_html(area, category, page_idx, data)))
        elif section_type == "places":
            content_sections.append((f"{area} {cat_info['name']} 추천", generate_places_html(area, category, page_idx, data)))
        elif section_type == "price_table":
            content_sections.append(("가격 비교 (로컬 vs 투어 vs 호텔)", generate_price_table_html(data.get("price_comp", []))))
        elif section_type == "budget_tips":
            content_sections.append(("예산 절약 팁", generate_budget_tips_html(area, category, data)))
        elif section_type == "related":
            pass  # 마지막에 별도 처리
        else:
            # 기타 섹션은 extra_sections에서 처리
            pass

    # 추가 섹션
    extra_html = generate_extra_sections(area, category, page_idx, data)

    # 에피소드
    episode_html = generate_episode_html(area, page_idx, data)

    # 관련 링크
    related_html = generate_related_links_html(area, category, page_idx)

    # 이미지
    images_html = generate_images_html(area, category, page_idx)

    # 쿠폰
    coupon_html = generate_coupon_html()

    # 본문 조립
    body_sections = ""
    for sec_title, sec_html in content_sections:
        if sec_html:
            body_sections += f'<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{sec_title}</h2>\n'
            body_sections += sec_html + "\n"

    # 이미지 삽입 (콘텐츠 사이에 분산)
    img_parts = images_html.split('<figure') if images_html else []
    img_inserted = 0
    final_body = ""

    # 도입부 뒤에 첫 번째 이미지
    if len(img_parts) > 1:
        final_body += '<figure' + img_parts[1] + "\n"
        img_inserted = 1

    # 나머지 이미지를 콘텐츠 사이에 분산
    body_lines = body_sections.split('\n')
    insert_interval = max(len(body_lines) // (len(img_parts) - 1), 1) if len(img_parts) > 1 else len(body_lines)

    for i, line in enumerate(body_lines):
        final_body += line + '\n'
        if img_inserted < len(img_parts) - 1 and i > 0 and i % insert_interval == 0:
            final_body += '<figure' + img_parts[img_inserted + 1] + "\n" if img_inserted + 1 < len(img_parts) else ""
            img_inserted += 1

    # 남은 이미지
    while img_inserted < len(img_parts) - 1:
        final_body += '<figure' + img_parts[img_inserted + 1] + "\n"
        img_inserted += 1

    # 추가 섹션, 에피소드, 관련 링크
    final_body += extra_html
    final_body += '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">여행 에피소드</h2>\n'
    final_body += episode_html
    final_body += '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">관련 지역 추천</h2>\n'
    final_body += related_html

    # 최종 HTML 조립
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{meta_keywords}">
<link rel="canonical" href="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE_URL}/images/{area}/{category}/{get_images(area, category, page_idx, 1)[0] if get_images(area, category, page_idx, 1) else ''}">
<meta property="og:url" content="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:site_name" content="JP Travel Bali">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": title,
    "description": meta_desc,
    "image": [f"{SITE_URL}/images/{area}/{category}/{img}" for img in get_images(area, category, page_idx, 3)],
    "datePublished": "2026-04-01",
    "dateModified": datetime.now().strftime("%Y-%m-%d"),
    "author": {"@type": "Person", "name": "JP Travel Bali"},
    "publisher": {"@type": "Organization", "name": "JP Travel Bali"},
    "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html"}
}, ensure_ascii=False)}</script>
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
<div style="background:#f5f5f5;padding:10px 15px;border-bottom:1px solid #e0e0e0;font-size:13px;color:#555;text-align:center;line-height:1.6">
이 글에는 <a href="{AFFILIATE_URL}" target="_blank" rel="sponsored nofollow noopener" style="color:#d84315;font-weight:600">마이리얼트립</a> 제휴 링크가 포함되어 있습니다. 링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.
</div>
<header>
<h1>{title}</h1>
<div class="meta">{cat_info['icon']} {area} | {cat_info['name']} | {CURRENT_YEAR}년 기준 | {read_time} 읽기</div>
</header>
<div class="container">
<nav class="breadcrumb">
<a href="/">홈</a> &gt;
<a href="/{area}/">{area}</a> &gt;
<a href="/{area}/{category}/">{cat_info['name']}</a> &gt;
<span>{title[:30]}...</span>
</nav>
<article>
<div class="content-intro">
<p>{intro}</p>
</div>
{coupon_html}
{final_body}
<div class="tags">
<span class="tag">{area}</span>
<span class="tag">{cat_info['name']}</span>
<span class="tag">발리</span>
<span class="tag">인도네시아</span>
<span class="tag">자유여행</span>
<span class="tag">{CURRENT_YEAR}</span>
</div>
<div class="content-footer">
<p>이 글이 {area} 여행 계획에 도움이 되셨길 바랍니다. 추가 질문은 댓글로 남겨주세요!</p>
</div>
</article>
</div>
{generate_footer_html()}
</body>
</html>'''

    return html


def generate_seo_title(area, category, page_idx, data):
    """SEO 롱테일 제목 생성 (924개 고유)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_title_v9"))
    cat_info = CATEGORIES[category]
    spots = data.get("spots", [])
    food = data.get("food", [])
    hidden = data.get("hidden", "")
    best_season = data.get("best_season", "4~10월")

    spot1 = spots[0] if spots else ""
    first_food = food[0]["name"] if food else ""

    # 카테고리별 제목 패턴 (롱테일 키워드 포함)
    title_patterns = {
        "food": [
            f"{area} {spot1} 근처 맛집 {rng.choice([5,6,7,8])}곳, 실제 가격과 이동 동선 정리",
            f"{area} 가성비 맛집 추천, {first_food} 포함 {rng.choice([3,5,7])}곳 후기",
            f"{area} 혼밥 가능한 맛집 리스트, 와룽부터 파인다이닝까지",
            f"{area} {cat_info['name']} 비용 비교, 로컬 vs 투어 vs 호텔 가격",
            f"{area} 브런치 카페 추천, 오전 일정과 연결하는 동선 가이드",
            f"{area} 저녁 식사 추천, 선셋과 함께하는 레스토랑 {rng.choice([3,5])}곳",
            f"{area} 로컬 음식 투어, 현지인이 가는 와룽 {rng.choice([5,7])}곳",
            f"{area} 해산물 맛집 추천, {spot1} 근처 가성비 레스토랑",
            f"{area} {cat_info['name']} 실패 없이 고르는 법, 시간대별 추천",
            f"{area} 비건/채식 맛집 리스트, {best_season.split(' ')[0]} 방문 기준",
            f"{area} 카페 투어 코스, 사진이 잘 나오는 곳 {rng.choice([5,7])}곳",
            f"{area} {cat_info['name']} 예산 정리, 1박 2일 식비 총비용",
            f"{area} 야시장 음식 추천, 저녁 6시 이후 가볼 곳",
            f"{area} 아침 식사 명소, 호텔 조식 대신 가볼 로컬 맛집",
        ],
        "culture": [
            f"{area} 사원 방문 가이드, 입장료와 복장 규정 총정리",
            f"{area} {spot1} 관람 팁, 사진이 잘 나오는 시간대와 각도",
            f"{area} 문화 체험 추천, 가이드 투어 vs 자유여행 비교",
            f"{area} 사원 순례 코스, 하루 동선 추천",
            f"{area} 전통 공연 추천, 케착춤 시간과 예약 방법",
            f"{area} 미술관/박물관 리스트, 입장료와 관람 시간",
            f"{area} 사원 에티켓 가이드, 현지인이 알려주는 주의사항",
            f"{area} {cat_info['name']} 비용 정리, 입장료+가이드+교통비 총비용",
            f"{area} 우천 시 방문 가능한 실내 문화 공간",
            f"{area} 숨겨진 사원 추천, 관광객이 잘 모르는 곳 {rng.choice([3,5])}곳",
            f"{area} {cat_info['name']} 사진 포인트, 인생샷 건지는 법",
            f"{area} 사원 근처 맛집, 관람 후 식사하기 좋은 곳",
            f"{area} 가족 여행 문화 체험, 아이와 함께 가능한 코스",
            f"{area} {cat_info['name']} 계절별 추천, {best_season}이 좋은 이유",
        ],
        "beach": [
            f"{area} 해변 가이드, 시간대별 파도와 선셋 포인트",
            f"{area} 서핑 초보자 가이드, 강습 가격과 추천 비치",
            f"{area} 비치클럽 가격 비교, 좌석 차이와 예약 팁",
            f"{area} 일몰 보기 좋은 해변 {rng.choice([3,5])}곳, 시간대별 추천",
            f"{area} 스노클링 포인트 추천, 장비 대여 가격",
            f"{area} 해변 안전 가이드, 파도 체크 수영 가능 여부",
            f"{area} {cat_info['name']} 비용 정리, 강습+장비+선베드 총비용",
            f"{area} 해변 근처 맛집, 선셋 후 저녁 식사 추천",
            f"{area} 우기철 해변 방문 팁, 파도 강한 날 대안",
            f"{area} 비치 산책로 코스, 도보 거리와 소요 시간",
            f"{area} 가족 여행 해변 추천, 아이와 함께 가능한 곳",
            f"{area} 프라이빗 비치 vs 공공 비치 비교",
            f"{area} 해변 사진 포인트, 일몰 시간대 촬영 팁",
            f"{area} {cat_info['name']} 혼자 즐기기, 혼행 추천 코스",
        ],
        "nature": [
            f"{area} 트레킹 가이드, 체력 난이도와 준비물 총정리",
            f"{area} {spot1} 방문 팁, 시간대와 이동 방법",
            f"{area} 우천 시 대안 코스, 비 와도 즐길 수 있는 곳",
            f"{area} {cat_info['name']} 비용 정리, 입장료+가이드+교통비",
            f"{area} 새벽 일출 명소, 가는 방법과 준비물",
            f"{area} 폭포 추천, 수영 가능 여부와 안전 수칙",
            f"{area} 라이스 테라스 베스트 타임, 사진이 잘 나오는 시간대",
            f"{area} 열대 우림 트레킹, 모기 대비와 준비물",
            f"{area} 화산 트레킹 가이드, 가격과 난이도 비교",
            f"{area} {cat_info['name']} 계절별 추천, 우기 vs 건기 장단점",
            f"{area} 자연 명소 동선, 하루 코스 추천",
            f"{area} 카약/래프팅 추천, 가격과 예약 방법",
            f"{area} 가족 여행 자연 체험, 아이와 함께 가능한 코스",
            f"{area} {cat_info['name']} 혼자 즐기기, 안전 팁",
        ],
        "shopping": [
            f"{area} 쇼핑 가이드, 흥정 법과 카드 가능 여부",
            f"{area} 기념품 추천 리스트, 가격대별 베스트",
            f"{area} 마사지 가격 비교, 로컬 vs 프리미엄 스파",
            f"{area} 시장별 차이점, 아트 마켓 vs 나이트 마켓",
            f"{area} {cat_info['name']} 비용 정리, 쇼핑+마사지 총비용",
            f"{area} 은세공/공예품 추천, 가격과 구매 팁",
            f"{area} 면세점 vs 시내 가격 비교, 어디서 사야 이득?",
            f"{area} 라탄 가방 추천, 실제 가격과 구매처",
            f"{area} 스파 패키지 추천, Klook vs 마이리얼트립 가격 비교",
            f"{area} {cat_info['name']} 우천 시 추천, 실내 쇼핑몰 리스트",
            f"{area} 발리 커피 추천, 코피 루왁 구매 팁",
            f"{area} 사롱/직물 추천, 염색 방법과 가격",
            f"{area} 혼자 쇼핑하기, 1인 마사지 추천",
            f"{area} {cat_info['name']} 계절별 세일 정보, 할인 시즌",
        ],
        "transport": [
            f"{area} 교통 가이드, 공항 이동부터 시내 이동까지",
            f"{area} 그랩 vs 스쿠터 vs 기사 투어, 가격 비교",
            f"{area} 공항에서 {area} 가는 법, cheapest 방법",
            f"{area} 스쿠터 렌트 가이드, 국제면허와 보험 체크",
            f"{area} 기사 투어 가격, 8시간/12시간 비용 비교",
            f"{area} 교통체증 피하는 법, 시간대별 이동 팁",
            f"{area} {cat_info['name']} 비용 정리, 하루 교통비 총비용",
            f"{area} 장거리 이동 팁, 다른 지역까지 소요 시간",
            f"{area} 고젝 vs 그랩 비교, 어떤 게 저렴할까?",
            f"{area} 우천 시 이동 팁, 비 올 때 추천 교통수단",
            f"{area} 가족 여행 교통, 카시트 대여 가능 여부",
            f"{area} 보트 투어 추천, 가격과 예약 방법",
            f"{area} {cat_info['name']} 혼자 이동하기, 안전 팁",
            f"{area} 시내 도보 코스, 걸어서 돌아보는 동선",
        ],
    }

    patterns = title_patterns.get(category, title_patterns["food"])
    title = patterns[page_idx % len(patterns)]

    # 제목에 연도가 없으면 추가
    if str(CURRENT_YEAR) not in title:
        title += f" ({CURRENT_YEAR})"

    return title


def generate_meta_desc(area, category, page_idx, data):
    """고유 메타 설명 (150자 이내)"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_meta_v9"))
    cat_info = CATEGORIES[category]
    spots = data.get("spots", [])
    food = data.get("food", [])

    spot1 = spots[0] if spots else ""
    first_food = food[0]["name"] if food else ""

    templates = [
        f"{area} {cat_info['name']} 여행 정보. {spot1} 추천부터 {first_food} 후기까지. 가격 비교와 실전 팁. {CURRENT_YEAR}년 기준.",
        f"{area} {cat_info['name']} 완벽 가이드. {spot1} 방문 팁, {first_food} 가격, 교통 정보까지. {CURRENT_YEAR} 최신.",
        f"{area} 자유여행 {cat_info['name']} 정리. {spot1} 추천, {first_food} 후기, 예산 비교. 직접 다녀온 후기.",
        f"{area} {cat_info['name']} 추천 리스트. {spot1}부터 숨은 명소까지. 가격·위치·팁 총정리. {CURRENT_YEAR}.",
        f"{area} 여행 {cat_info['name']} 정보. {spot1} 방문 가이드, {first_food} 가격 비교. 실전 팁 포함. {CURRENT_YEAR}.",
    ]

    desc = templates[page_idx % len(templates)]
    if len(desc) > 150:
        desc = desc[:147] + "..."
    return desc


def generate_keywords(area, category, data):
    """SEO 키워드"""
    cat_info = CATEGORIES[category]
    spots = data.get("spots", [])[:3]
    kw = [area, cat_info["name"]] + spots + ["발리", "인도네시아", "자유여행", str(CURRENT_YEAR)]
    return ", ".join(kw)


# ============================================================
# 메인 빌드
# ============================================================
def build_all():
    """924개 HTML 전체 빌드"""
    print("=" * 60)
    print(f"JP Travel Bali v9 빌드 시작")
    print(f"지역: {len(AREAS)}개 / 카테고리: {len(CATEGORIES)}개 / 페이지: 14개")
    print(f"총 {len(AREAS) * len(CATEGORIES) * 14}개 HTML 생성")
    print("=" * 60)

    total = 0
    errors = 0

    for area in AREAS:
        for category in CATEGORIES:
            cat_dir = OUTPUT_HTML / area / category
            cat_dir.mkdir(parents=True, exist_ok=True)

            for page_idx in range(14):
                try:
                    html = generate_html(area, category, page_idx)
                    filepath = cat_dir / f"{page_idx+1:03d}.html"
                    filepath.write_text(html, encoding='utf-8')
                    total += 1
                except Exception as e:
                    errors += 1
                    print(f"  ERROR: {area}/{category}/{page_idx+1:03d}.html - {e}")

            print(f"  [{total:3d}] {area}/{category} 완료")

    print(f"\n{'='*60}")
    print(f"빌드 완료: {total}개 생성 / {errors}개 오류")
    print(f"{'='*60}")
    return total, errors


if __name__ == "__main__":
    build_all()
