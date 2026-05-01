#!/usr/bin/env python3
"""
발리 여행 블로그 빌드 시스템 v5 — 고유 콘텐츠 강화판
- 924개 HTML 페이지 (11지역 × 6카테고리 × 14페이지)
- 각 페이지별 고유한 글 내용 (AI 없이 템플릿 변형)
- 네이버 Cue: 최적화 구조 (표, 리스트, 결론박스, Q&A)
- 4소스 이미지 시스템 (Openverse + Flickr + Wikimedia + Picsum)
- 마이리얼트립 제휴 링크
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
    "food": {"name": "음식/맛집", "icon": "🍜", "desc": "맛집 탐방", "en": "food"},
    "culture": {"name": "문화/사원", "icon": "🛕", "desc": "문화 체험", "en": "culture"},
    "beach": {"name": "해변/서핑", "icon": "🏖️", "desc": "해변 액티비티", "en": "beach"},
    "nature": {"name": "자연/모험", "icon": "🌿", "desc": "자연 탐방", "en": "nature"},
    "shopping": {"name": "쇼핑/마사지", "icon": "🛍️", "desc": "쇼핑 & 힐링", "en": "shopping"},
    "transport": {"name": "여행/교통", "icon": "🚗", "desc": "이동 정보", "en": "transport"},
}

# ============================================================
# 발리 지역별 상세 데이터 (기존 build_bali.py에서 import)
# ============================================================
from build_bali import BALI_DATA, CATEGORY_EXTRA_CONTENT

# ============================================================
# 고유 콘텐츠 생성 엔진
# ============================================================

# 글 작성 앵글 (14가지 변형)
WRITING_ANGLES = [
    "실전_후기",      # 0: 실제 다녀온 후기 기반
    "가성비_최적화",   # 1: 예산 절약 중심
    "숨은_명소",      # 2: 관광객이 잘 모르는 곳
    "첫방문_가이드",   # 3: 처음 가는 사람을 위해
    "커플_가족",      # 4: 동반자별 추천
    "사진_포토스팟",   # 5: 인스타/사진 명소
    "혼자_여행",      # 6: 혼행족 가이드
    "맛집_투어",      # 7: 음식 중심 코스
    "액티비티",       # 8: 체험/활동 중심
    "힐링_휴양",      # 9: 휴식 중심
    "문화_역사",      # 10: 문화적 배경
    "일몰_일출",      # 11: 시간대별 명소
    "비수기_여행",    # 12: 비수기 장점
    "로컬_체험",      # 13: 현지인처럼 즐기기
]

# 첫 문단 결론 템플릿 (30가지)
INTRO_TEMPLATES = [
    "{area}에서 {cat_desc}을(를) 즐기려면 {conclusion}입니다. 특히 {condition}이라면 {var1}, {var2}, {var3}을 함께 고려해야 {goal} 달성이 쉽습니다.",
    "{area} {cat_name} 여행의 핵심은 {conclusion}. {var1}부터 {var2}까지, {condition} 기준으로 정리했습니다.",
    "결론부터 말하면, {area}의 {cat_name}은 {conclusion}. {var1}과 {var2}를 비교하면 {var3}이(가) 더 {advantage}합니다.",
    "{area}를 {visit_count}번 다녀온 경험으로 말하면, {cat_name}은 {conclusion}. {condition}이라면 {var1}을 추천합니다.",
    "{area} {cat_name} 완벽 가이드입니다. {var1}부터 {var3}까지, {conclusion}이 핵심입니다.",
    "많은 분들이 {area} {cat_name}을(를) 물어보시는데요, {conclusion}. 특히 {condition}이라면 {var1}이(가) 가장 좋습니다.",
    "{area} 여행에서 {cat_name}은(는) 빼놓을 수 없는 코스입니다. {conclusion}. {var1}과 {var2}를 비교해보세요.",
    "{area} {cat_name} 추천 리스트입니다. {conclusion}. {condition} 기준으로 {var1}, {var2}, {var3} 순서로 정리했습니다.",
    "{area}에서 {cat_desc}을(를) 제대로 즐기려면 {conclusion}. {var1}부터 시작해서 {var2}까지 코스를 짜보세요.",
    "{area} {cat_name} 정보를 한눈에 정리했습니다. {conclusion}. {var1}과 {var2}의 가격 차이는 {var3} 수준입니다.",
    "실제로 {area}에서 {cat_desc}을(를) 즐겨본 결과, {conclusion}. {condition}이라면 {var1}을(를) 꼭 방문하세요.",
    "{area} {cat_name} 가이드 — {conclusion}. {var1}, {var2}, {var3} 중에서 {condition}에 맞는 것을 선택하세요.",
    "{area} 자유여행에서 {cat_name}은(는) {conclusion}. {var1}부터 {var2}까지 예산별로 정리했습니다.",
    "{area} {cat_name} 베스트 추천입니다. {conclusion}. {condition}이라면 {var1}이(가) 최고의 선택입니다.",
    "{area} 여행 10년차가 추천하는 {cat_name}은 {conclusion}. {var1}과 {var2}를 비교하면 확실히 차이가 있습니다.",
    "{area} {cat_name} 완벽 정리 — {conclusion}. {var1}, {var2}, {var3} 각각의 장단점을 비교했습니다.",
    "{area}에서 {cat_desc}을(를) 계획 중이신가요? {conclusion}. {condition} 기준으로 추천드립니다.",
    "{area} {cat_name} 실제 후기입니다. {conclusion}. {var1}은(는) {var2}보다 {advantage}합니다.",
    "{area} {cat_name} 총정리 — {conclusion}. {var1}부터 {var3}까지 모두 다녀본 결과입니다.",
    "{area} 여행 필수 정보, {cat_name}입니다. {conclusion}. {condition}이라면 이 글이 도움될 거예요.",
    "{area} {cat_name} 추천 TOP리스트입니다. {conclusion}. {var1}, {var2}, {var3} 순으로 정리했습니다.",
    "{area}에서 {cat_desc}을(를) 즐기는 방법은 여러 가지가 있지만, {conclusion}. 특히 {var1}이(가) 인기입니다.",
    "{area} {cat_name} 가이드북에 없는 진짜 정보입니다. {conclusion}. {condition}이라면 주목하세요.",
    "{area} {cat_name} — {conclusion}. {var1}과 {var2}의 가격을 비교하면 {var3} 정도 차이가 납니다.",
    "{area}를 여행한다면 {cat_name}은(는) 필수입니다. {conclusion}. {condition} 기준으로 추천합니다.",
    "{area} {cat_name} 숨은 꿀팁 대방출입니다. {conclusion}. {var1}부터 {var2}까지 모두 정리했습니다.",
    "{area} {cat_name} 완벽 분석입니다. {conclusion}. {var1}, {var2}, {var3} 각각의 특징을 비교했습니다.",
    "{area}에서 {cat_desc}을(를) 찾고 계신가요? {conclusion}. {condition}이라면 {var1}을(를) 추천합니다.",
    "{area} {cat_name} 2026년 최신 정보입니다. {conclusion}. {var1}부터 {var3}까지 업데이트했습니다.",
    "{area} {cat_name} — 현지인이 알려주는 진짜 정보입니다. {conclusion}. {condition} 기준으로 정리했습니다.",
]

# Q&A 템플릿 (카테고리별)
QA_TEMPLATES = {
    "food": [
        ("{area} 맛집 중 가장 추천하는 곳은?", "{answer}"),
        ("{area} 가성비 맛집은 어디인가요?", "{answer}"),
        ("{area}에서 꼭 먹어봐야 할 음식은?", "{answer}"),
        ("{area} 브런치 카페 추천해주세요", "{answer}"),
        ("{area} 야시장 음식 추천은?", "{answer}"),
        ("{area} 비건/채식 맛집이 있나요?", "{answer}"),
        ("{area} 해산물 맛집 추천해주세요", "{answer}"),
        ("{area} 카페 추천 (인스타 감성)", "{answer}"),
        ("{area} 디저트 맛집은?", "{answer}"),
        ("{area}에서 술 한잔 하기 좋은 곳은?", "{answer}"),
    ],
    "culture": [
        ("{area} 사원 방문 시 복장 규정은?", "{answer}"),
        ("{area}에서 꼭 봐야 할 전통 공연은?", "{answer}"),
        ("{area} 사원 투어 추천 코스는?", "{answer}"),
        ("{area} 문화 체험 프로그램이 있나요?", "{answer}"),
        ("{area} 미술관/박물관 추천해주세요", "{answer}"),
        ("{area} 전통 공예 체험은 어디서?", "{answer}"),
        ("{area} 사원에서 사진 촬영 가능한가요?", "{answer}"),
        ("{area} 힌두교 문화에 대해 알려주세요", "{answer}"),
    ],
    "beach": [
        ("{area} 해변에서 서핑 강습 받으려면?", "{answer}"),
        ("{area} 비치클럽 추천은?", "{answer}"),
        ("{area} 스노클링 포인트는?", "{answer}"),
        ("{area} 일몰 보기 좋은 해변은?", "{answer}"),
        ("{area} 해변 근처 맛집 추천해주세요", "{answer}"),
        ("{area} 해변에서 주의할 점은?", "{answer}"),
        ("{area} 수영하기 안전한 해변은?", "{answer}"),
        ("{area} 해변 액티비티 추천은?", "{answer}"),
    ],
    "nature": [
        ("{area} 라이스 테라스 방문 팁은?", "{answer}"),
        ("{area} 폭포 추천 및 가는 방법은?", "{answer}"),
        ("{area} 트레킹 코스 추천해주세요", "{answer}"),
        ("{area} 원숭이 주의사항은?", "{answer}"),
        ("{area} 자연 명소 하루 코스 추천", "{answer}"),
        ("{area} 화산 트레킹 가격은?", "{answer}"),
        ("{area} 우기 vs 건기 어느 시기가 좋나요?", "{answer}"),
        ("{area} 자연 사진 찍기 좋은 곳은?", "{answer}"),
    ],
    "shopping": [
        ("{area} 기념품 쇼핑 추천 장소는?", "{answer}"),
        ("{area} 마사지 가격과 추천 샵은?", "{answer}"),
        ("{area} 아트 마켓에서 흥정 팁은?", "{answer}"),
        ("{area} 스파 추천해주세요", "{answer}"),
        ("{area} 로컬 브랜드 쇼핑몰은?", "{answer}"),
        ("{area} 발리 커피/차 쇼핑 추천", "{answer}"),
        ("{area} 세일 시즌은 언제인가요?", "{answer}"),
        ("{area} 면세점 쇼핑 팁은?", "{answer}"),
    ],
    "transport": [
        ("{area} 공항에서 가는 방법은?", "{answer}"),
        ("{area} 시내 이동 수단 추천은?", "{answer}"),
        ("{area} 스쿠터 렌트 시 주의사항은?", "{answer}"),
        ("{area} 그랩 이용 팁은?", "{answer}"),
        ("{area}에서 다른 지역 가는 방법은?", "{answer}"),
        ("{area} 교통체증 피하는 방법은?", "{answer}"),
        ("{area} 전용 드라이버 고용 가격은?", "{answer}"),
        ("{area} 주차 정보는?", "{answer}"),
    ],
}

# 팁 템플릿 (카테고리별 × 20개씩)
TIP_TEMPLATES = {
    "food": [
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
        "GoFood 배달 앱으로 호텔에서 시켜 먹으면 교통비 절약돼요.",
        "나시고렝은 어디서든 먹을 수 있지만, 집마다 맛이 달라요. 여러 곳 시도해보세요.",
        "발리 맥주는 빈탕(Bintang)이 대표적이에요. 생맥주가 병맥주보다 저렴합니다.",
        "디저트 카페가 우붓/스미냑에 많아요. 젤라토, 케이크 전문점 추천합니다.",
        "조식 뷔페가 포함된 숙소를 선택하면 하루 1끼 비용을 절약할 수 있어요.",
        "로컬 음식 가격: 나시고렝 20,000~35,000Rp, 미고렝 15,000~25,000Rp 수준입니다.",
        "생과일 주스가 매우 저렴해요. 아보카도, 망고, 파파야 추천. 15,000~25,000Rp.",
        "발리에서는 아이스커피가 인기예요. 카페마다 시그니처 메뉴가 있으니 물어보세요.",
        "식사 시간은 한국보다 1~2시간 빨라요. 점심 11시, 저녁 6시가 피크입니다.",
        "관광지 음식은 2~3배 비싸요. 1~2블록만 걸어가면 가성비 맛집이 있습니다.",
    ],
    "culture": [
        "사원 방문 시 사롱(긴 스카프) 착용 필수! 입구에서 빌려주는 곳도 있어요.",
        "사원 입장료는 보통 30,000~60,000루피아입니다.",
        "발리는 힌두교 국가라 일요일이 아닌 '갈룽안'에 공연이 많아요.",
        "사진 촬영 전 허락을 구하세요. 특히 제사 중인 장면은 촬영 금지입니다.",
        "케착춤은 울루와뚜 사원에서 일몰 시간에 보는 게 가장 분위기 좋아요.",
        "바롱 댄스는 선악의 대결을 묘사한 발리 전통 공연이에요.",
        "사원 축제 기간(210일마다)에는 특별한 의식을 볼 수 있어요.",
        "발리 예술은 회화, 조각, 은세공, 직물 등 다양해요.",
        "사원에 들어갈 때는 신발을 벗어야 해요. 슬리퍼보다 운동화가 편합니다.",
        "우붓 왕궁 저녁 공연(7시)은 발리 전통춤을 볼 수 있는 좋은 기회예요.",
        "사원마다 입장 시간이 달라요. 오전 8시~오후 5시가 일반적입니다.",
        "발리 달력은 210일 주기예요. 갈룽안과 쿠닝안 축제가 특히 화려합니다.",
        "사원 가이드를 고용하면 문화적 배경을 깊이 이해할 수 있어요. 100,000~200,000Rp.",
        "힌두교 의식 중에는 절대 앞을 지나가지 마세요. 뒤로 돌아가세요.",
        "발리 전통 공연 시간표는 숙소 리셉션에서 확인할 수 있어요.",
        "사원에서 받는 축복(떤또트)은 무료이지만 기부금 10,000~20,000Rp를 놓는 게 예의입니다.",
        "우붓 아트 마켓에서 전통 직물(사롱)을 구매하면 좋은 기념품이에요.",
        "발리 조각상은 지역마다 스타일이 달라요. 우붓은 섬세, 마스는 대담한 스타일입니다.",
        "사원 건축 양식은 자바 힌두교와 발리 토속 신앙이 혼합된 독특한 형태입니다.",
        "사원 방문은 오전이 좋아요. 오후에는 관광객이 많아지고 더워집니다.",
    ],
    "beach": [
        "서핑 강습은 꾸따/스미냑에서 가장 저렴해요. 150,000~250,000루피아/1회.",
        "일몰은 서쪽 해변(꾸따, 스미냑, 울루와뚜)에서, 일출은 동쪽(사누르)에서!",
        "파도가 강한 날에는 수영 금지! 빨간 깃발 표시를 꼭 확인하세요.",
        "비치클럽은 선셋 2시간 전 가야 좋은 자리를 잡을 수 있어요.",
        "자외선이 매우 강해요. 선크림 SPF50+ 필수, 모자도 추천합니다.",
        "해변에서 물건 파는 사람에게는 단호하게 '아니요'라고 하면 됩니다.",
        "스노클링 장비는 현지에서 대여 가능해요. 50,000~100,000루피아.",
        "우기는 파도가 매우 강해요. 서핑은 건기(4~10월)가 가장 좋습니다.",
        "해변 의자(선베드)는 대여 비용이 50,000~100,000루피아예요.",
        "해변에서 수영 후 담수 샤워 시설이 있는 곳을 이용하세요. 10,000~20,000Rp.",
        "서핑 보드 대여는 50,000~100,000루피아/시간. 하루 종일이면 200,000~300,000Rp.",
        "해변가 레스토랑은 내륙보다 2~3배 비싸요. 해변에서 놀고 내륙에서 식사하세요.",
        "일몰 시간은 계절에 따라 다르지만, 보통 오후 6시 전후예요.",
        "해변에서 밤에는 조류가 강해져요. 일몰 후 수영은 피하세요.",
        "물놀이 후 선크림을 꼭 다시 바르세요. 2시간마다 덧발라야 합니다.",
        "해변 근처에는 화장실/샤워실이 10,000~20,000루피아예요.",
        "비치타월은 호텔에서 가져가면 비용을 절약할 수 있어요.",
        "해변에서 코코넛 음료를 파는 가게가 많아요. 15,000~25,000Rp.",
        "서핑 초보자는 반드시 강사와 함께하세요. 혼자 가면 위험합니다.",
        "해변 근처 주차장은 스쿠터 5,000Rp, 차량 10,000~20,000Rp입니다.",
    ],
    "nature": [
        "트레킹은 새벽 출발이 필수! 낮에는 매우 덥고 습해요.",
        "모기 기피제 필수. 열대 지역이라 모기가 많습니다.",
        "편한 운동화 필수. 샌들로 트레킹하면 다칠 수 있어요.",
        "우기(11~3월)에는 폭포 수량이 풍부하지만 길이 미끄러워요.",
        "화산 트레킹은 가이드 필수! 혼자 가면 위험합니다.",
        "원숭이에게 소지품을 빼앗기지 않게 주의하세요. 가방은 앞으로 메세요.",
        "라이스 테라스는 이른 아침에 가야 안개 없이 깨끗한 뷰를 볼 수 있어요.",
        "열대 우림에서는 갑작스러운 소나기가 올 수 있어요. 우산 필수!",
        "폭포 근처는 바닥이 미끄러워요. 아쿠아슈즈를 신으세요.",
        "야간 트레킹은 반드시 가이드와 함께하세요. 야생동물 주의.",
        "화산 트레킹 시 마스크를 챙기세요. 유황 가스가 나올 수 있어요.",
        "라이스 테라스에서 사진 찍을 때는 농부에게 방해되지 않게 주의하세요.",
        "자연 명소에는 쓰레기통이 없을 수 있어요. 봉지를 가져가세요.",
        "트레킹 중간에 휴식을 충분히 취하세요. 탈수 위험이 있습니다.",
        "열대 과일 농장 체험도 추천이에요. 두리안, 망고, 람부탄 시즌이 달라요.",
        "정글 트레킹은 장화를 대여해주는 곳이 있어요. 20,000~30,000Rp.",
        "폭포 입구에서 가이드를 제안하는 경우가 많아요. 50,000~100,000Rp.",
        "라이스 테라스는 우기(11~3월)가 가장 푸르고 아름답습니다.",
        "화산 일출 트레킹은 새벽 2시 출발이에요. 전날 일찍 자세요.",
        "자연 명소에는 모바일 신호가 약할 수 있어요. 오프라인 지도를 준비하세요.",
    ],
    "shopping": [
        "기념품 가게에서는 흥정이 필수! 첫 가격의 30~50% 수준으로 흥정하세요.",
        "마사지는 관광지보다 로컬 가게가 50% 저렴해요.",
        "아트 마켓은 오전에 가야 선택 폭이 넓어요.",
        "발리 커피, 코코넛 오일, 라탄 가방이 대표 기념품이에요.",
        "사롱(전통 직물)은 고품질 기념품으로 좋아요.",
        "은세공은 우붓에서! 세밀한 공예품이 많아요.",
        "면세점은 공항에만 있어요. 시내에서 미리 구매하세요.",
        "스파 패키지 예약은 Klook/마이리얼트립에서 하면 20~30% 저렴해요.",
        "쇼핑몰에서는 흥정이 안 돼요. 로컬 시장에서만 흥정하세요.",
        "발리 원목 가구는 국제 배송이 가능해요. 2~3개월 소요.",
        "기념품은 공항에서 사면 2~3배 비싸요. 시내에서 미리 사세요.",
        "마사지 샵은 1시간 기준 60,000~150,000루피아. 프리미엄은 300,000Rp~.",
        "발리 섬유(바틱)는 지역마다 패턴이 달라요. 고유한 선물로 좋아요.",
        "은세공품은 우붓 마스(Mas) 마을에서 공방을 직접 방문하면 저렴해요.",
        "스파 예약은 하루 전에 하면 10~20% 할인되는 곳이 있어요.",
        "로드샵 화장품은 한국보다 저렴하지 않아요. 다른 기념품을 추천합니다.",
        "발리 전통 마사지(Boreh)는 따뜻한 허브를 사용해요. 추천합니다.",
        "아트 마켓에서 그림을 구매하면 액자 포장도 해줘요. 비행기 수화물 주의.",
        "발리 와인은 맛이 독특해요. 선물용으로 좋은 Hatten, Two Islands 브랜드.",
        "대형 쇼핑몰(비치워크, 디스커버리)에서는 카드 결제 가능해요.",
    ],
    "transport": [
        "그랩(Grab)이 가장 편하고 저렴해요. 현금/카드 모두 가능.",
        "스쿠터 렌트는 국제운전면허증 필수! 없으면 벌금 500,000루피아.",
        "공항에서 호텔까지 사전 예약 드라이버가 그랩보다 안전해요.",
        "발리는 교통체증이 매우 심해요. 이동 시간을 넉넉하게 잡으세요.",
        "고젝(Gojek)은 그랩 대안이에요. 오토바이 택시도 가능합니다.",
        "우붓→꾸까지 약 1시간, 꾸따→누사두아 약 40분이에요.",
        "장거리 이동은 전용 드라이버를 고용하는 게 편해요. 8시간 기준 500,000~700,000루피아.",
        "보트 투어는 사전 예약 필수! 날씨에 따라 취소될 수 있어요.",
        "공항 택시는 프리미엄이에요. 그랩이 30~50% 저렴합니다.",
        "스쿠터 렌트 시 헬멧 착용 필수! 안 걸리더라도 안전을 위해.",
        "우붓은 일방통행이 많아요. 내비게이션을 꼭 확인하세요.",
        "그랩 드라이버에게 별점 5개를 주면 다음에 더 빨리 매칭돼요.",
        "비수기(11~3월)에는 교통체증이 적어요. 이동 시간이 30% 단축됩니다.",
        "장거리 이동 시 휴게소에서 발리 커피를 마시는 것도 여행의 묘미예요.",
        "공항 도착 시 유심칩을 사면 그랩 사용이 편해요. 100,000~200,000Rp.",
        "보트 예약은 Bali Ferry 또는 Klook에서 하면 편해요.",
        "우붓→킨타마니는 산길이 많아요. 면허가 자신 없으면 드라이버를 고용하세요.",
        "택시 미터기 확인 필수! 미터가 없는 택시는 타지 마세요.",
        "스쿠터 반납 시 주유 상태를 확인하세요. 가득 채워서 반납이 일반적이에요.",
        "발리 공항은 출국 수속이 2~3시간 걸릴 수 있어요. 넉넉하게 가세요.",
    ],
}

# 명언/에피소드 템플릿
ANECDOTE_TEMPLATES = [
    "실제로 {area}에서 {activity}을(를) 했을 때, {observation}.",
    "저는 {area}를 {visit_count}번째 방문했는데, {observation}.",
    "{area} 현지인 {local_name}씨가 알려준 바로는, {local_tip}.",
    "작년 {month}월에 {area}를 방문했을 때, {observation}.",
    "{area}에서 만난 한국인 여행자들이 가장 많이 하는 말이 '{quote}'입니다.",
    "블로그 후기만 보고 {area}에 갔다가 실제로는 {observation}.",
    "{area}에서 {activity} 중에 깜짝 놀란 사실은, {surprising_fact}.",
    "10년간 {area}를 다니면서 느낀 건, {insight}.",
    "{area} 여행 첫날에는 {first_day_observation}. 둘째날부터는 {day2_recommendation}.",
    "현지 가이드 {local_name}씨에게 '{question}'이라고 물었더니, '{answer}'라고 하더라고요.",
]

# ============================================================
# 콘텐츠 생성 함수
# ============================================================

def get_images(area, category, count=10, page_offset=0):
    """페이지별 고유 이미지 선택 (셔플 기반으로 매번 다른 세트)"""
    mapping = {}
    for f in [MAPPING_FILE, BASE_DIR / "image_mapping_v2.json", BASE_DIR / "image_mapping.json"]:
        if f.exists():
            try:
                mapping = json.loads(f.read_text())
                break
            except:
                continue
    
    imgs = mapping.get(area, {}).get(category, [])
    if not imgs:
        # 파일시스템 fallback
        search_dir = OUTPUT_IMAGES / area / category
        if search_dir.exists():
            imgs = sorted([f.name for f in search_dir.iterdir() if f.suffix.lower() in ('.jpg', '.png', '.webp')])
    
    if not imgs:
        return [f"placeholder_{hashlib.md5(f'{area}_{category}_{i}_{page_offset}'.encode()).hexdigest()[:8]}.webp" for i in range(count)]
    
    # 페이지별 시드로 셔플 → 매번 다른 순서와 조합
    rng = random.Random(hash(f"{area}_{category}_{page_offset}_img"))
    shuffled = list(imgs)
    rng.shuffle(shuffled)
    
    # 이미지가 10개 미만이면 반복 사용하되 순서를 바꿔서
    if len(shuffled) < count:
        result = []
        for i in range(count):
            result.append(shuffled[i % len(shuffled)])
        return result
    
    return shuffled[:count]

def generate_unique_intro(area, category, page_idx, data):
    """고유한 첫 문단 생성"""
    cat_info = CATEGORIES[category]
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_intro"))
    
    # 결론/조건/변수 추출
    desc = data.get("description", "")
    spots = data.get("spots", [])
    qa = data.get("intro_qa", [])
    hidden = data.get("hidden_gem", "")
    best_season = data.get("best_season", "4~10월")
    
    conclusions = [
        f"{desc}",
        f"{spots[0] if spots else '주요 명소'}부터 시작하는 것이 가장 효율적",
        f"예산형 {data.get('hotels', {}).get('budget', '100,000~200,000루피아')}으로도 충분히 즐길 수 있는 곳",
        f"{best_season}이 최적 시기",
        f"{hidden.split('은')[0] if hidden else '숨은 명소'}까지 포함하면 완벽한 코스",
        f"하루 일정으로도 충분하지만 2박 3일이 이상적",
    ]
    
    conditions = [
        f"첫 방문이라면",
        f"가성비를 중시한다면",
        f"사진을 많이 찍고 싶다면",
        f"가족과 함께라면",
        f"혼자 여행한다면",
        f"비수기에 방문한다면",
        f"로컬 음식을 즐기고 싶다면",
        f"역사와 문화에 관심이 있다면",
    ]
    
    vars_pool = [
        spots[0] if spots else "주요 명소",
        spots[1] if len(spots) > 1 else "추천 코스",
        data.get("food", [{}])[0].get("name", "현지 맛집") if data.get("food") else "현지 맛집",
        f"{best_season} 방문",
        data.get("hotels", {}).get("mid", "중급 숙소"),
        "그랩/고젝 이용",
    ]
    
    template = rng.choice(INTRO_TEMPLATES)
    result = template.format(
        area=area,
        cat_name=cat_info["name"],
        cat_desc=cat_info["desc"],
        conclusion=rng.choice(conclusions),
        condition=rng.choice(conditions),
        var1=rng.choice(vars_pool),
        var2=rng.choice(vars_pool),
        var3=rng.choice(vars_pool),
        advantage=rng.choice(["저렴", "좋", "편리", "아름답", "인기 있"]),
        visit_count=rng.choice(["3", "5", "7", "10"]),
        goal=rng.choice(["여행", "방문", "체험", "탐방"]),
    )
    return result

def generate_unique_qa(area, category, page_idx, data):
    """고유한 Q&A 섹션 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_qa"))
    qa_templates = QA_TEMPLATES.get(category, QA_TEMPLATES["food"])
    
    # 3~4개 Q&A 선택
    selected = rng.sample(qa_templates, min(4, len(qa_templates)))
    
    # 답변 풀
    answer_pool = []
    cat_data = data.get(category, [])
    for item in cat_data[:6]:
        name = item.get("name", "")
        price = item.get("price", "")
        tip = item.get("tip", "")
        if name:
            answer_pool.append(f"{name} ({price}) — {tip}")
    
    if not answer_pool:
        answer_pool = [f"{area}의 {CATEGORIES[category]['name']} 정보는 본문을 참고하세요."]
    
    html = ""
    for q_template, _ in selected:
        q = q_template.format(area=area)
        a = rng.choice(answer_pool)
        html += f'''<div style="margin:16px 0;padding:16px;background:linear-gradient(135deg,#e8f5e9,#f1f8e9);border-radius:10px;border:1px solid #c8e6c9">
<p style="margin:0 0 6px;font-weight:700;color:#2e7d32;font-size:1em">❓ {q}</p>
<p style="margin:0;color:#333;line-height:1.7">{a}</p>
</div>\n'''
    return html

def generate_unique_content_body(area, category, page_idx, data):
    """고유한 본문 콘텐츠 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_body"))
    cat_info = CATEGORIES[category]
    cat_data = data.get(category, [])
    
    angle_idx = page_idx % len(WRITING_ANGLES)
    angle = WRITING_ANGLES[angle_idx]
    
    html = ""
    
    # 앵글별 소제목과 내용
    if angle == "실전_후기":
        html += f'<h2>📋 {area} {cat_info["name"]} 실전 후기</h2>\n'
        html += f'<p>직접 다녀온 기준으로 {area}의 {cat_info["name"]} 정보를 정리했습니다. 가격, 위치, 팁까지 모두 실제 경험담입니다.</p>\n'
    elif angle == "가성비_최적화":
        html += f'<h2>💰 {area} {cat_info["name"]} 가성비 최적화 가이드</h2>\n'
        html += f'<p>예산을 아끼면서도 {area}의 {cat_info["name"]}을(를) 제대로 즐기는 방법을 정리했습니다.</p>\n'
    elif angle == "숨은_명소":
        html += f'<h2>💎 {area} {cat_info["name"]} 숨은 명소</h2>\n'
        html += f'<p>관광객이 잘 모르는 {area}의 {cat_info["name"]} 명소를 공개합니다.</p>\n'
    elif angle == "첫방문_가이드":
        html += f'<h2>🔰 {area} {cat_info["name"]} 첫 방문 가이드</h2>\n'
        html += f'<p>처음 {area}를 방문하시는 분들을 위해 {cat_info["name"]} 정보를 쉽게 정리했습니다.</p>\n'
    elif angle == "커플_가족":
        html += f'<h2>💑 {area} {cat_info["name"]} — 커플/가족 추천</h2>\n'
        html += f'<p>커플 여행, 가족 여행에 맞는 {area}의 {cat_info["name"]} 추천 코스입니다.</p>\n'
    elif angle == "사진_포토스팟":
        html += f'<h2>📸 {area} {cat_info["name"]} 포토스팟 가이드</h2>\n'
        html += f'<p>인스타 감성 사진을 찍을 수 있는 {area}의 {cat_info["name"]} 명소를 정리했습니다.</p>\n'
    elif angle == "혼자_여행":
        html += f'<h2>🎒 {area} 혼자 여행 — {cat_info["name"]} 가이드</h2>\n'
        html += f'<p>혼자서도 안전하고 즐겁게 {area}의 {cat_info["name"]}을(를) 즐기는 방법입니다.</p>\n'
    elif angle == "맛집_투어":
        html += f'<h2>🍽️ {area} 맛집 투어 코스</h2>\n'
        html += f'<p>하루 3끼를 {area}의 맛집에서 해결하는 투어 코스를 추천합니다.</p>\n'
    elif angle == "액티비티":
        html += f'<h2>🎯 {area} {cat_info["name"]} 액티비티 추천</h2>\n'
        html += f'<p>체험과 활동 중심으로 {area}의 {cat_info["name"]}을(를) 즐기는 방법입니다.</p>\n'
    elif angle == "힐링_휴양":
        html += f'<h2>🧘 {area} 힐링 여행 — {cat_info["name"]}</h2>\n'
        html += f'<p>휴식과 힐링 중심으로 {area}의 {cat_info["name"]}을(를) 즐기는 코스입니다.</p>\n'
    elif angle == "문화_역사":
        html += f'<h2>🏛️ {area} 문화와 역사 — {cat_info["name"]}</h2>\n'
        html += f'<p>{area}의 문화적 배경과 역사를 이해하면서 {cat_info["name"]}을(를) 즐기는 방법입니다.</p>\n'
    elif angle == "일몰_일출":
        html += f'<h2>🌅 {area} 시간대별 명소 — {cat_info["name"]}</h2>\n'
        html += f'<p>일몰, 일출, 골든아워에 {area}의 {cat_info["name"]}을(를) 제대로 즐기는 방법입니다.</p>\n'
    elif angle == "비수기_여행":
        html += f'<h2>🌧️ {area} 비수기 여행의 장점 — {cat_info["name"]}</h2>\n'
        html += f'<p>비수기(11~3월)에 {area}의 {cat_info["name"]}을(를) 즐기면 좋은 이유를 정리했습니다.</p>\n'
    else:  # 로컬_체험
        html += f'<h2>🏠 {area} 로컬 체험 — {cat_info["name"]}</h2>\n'
        html += f'<p>현지인처럼 {area}의 {cat_info["name"]}을(를) 즐기는 방법을 알려드립니다.</p>\n'
    
    # 카테고리별 상세 내용
    if category == "food" and cat_data:
        start = (page_idx * 2) % len(cat_data)
        for i in range(min(5, len(cat_data))):
            fd = cat_data[(start + i) % len(cat_data)]
            html += f'''<div style="margin:14px 0;padding:14px;background:#fafafa;border-radius:8px;border-left:4px solid #FF6B35">
<h3 style="font-size:1.05em;font-weight:700;margin:0 0 8px;color:#333">{i+1}. {fd["name"]}</h3>
<p style="margin:0 0 6px;line-height:1.6"><strong>💰 가격:</strong> {fd["price"]} ({fd.get("price_krw", "")})</p>
<p style="margin:0 0 6px;line-height:1.6"><strong>📍 위치:</strong> {fd["area"]}</p>
<p style="margin:0 0 6px;line-height:1.6"><strong>💡 팁:</strong> {fd["tip"]}</p>
<p style="margin:0;line-height:1.6"><strong>🍽️ 추천 메뉴:</strong> {fd.get("must_try", "-")}</p>
</div>\n'''
    elif cat_data:
        start = (page_idx * 2) % len(cat_data)
        for i in range(min(5, len(cat_data))):
            item = cat_data[(start + i) % len(cat_data)]
            html += f'''<div style="margin:14px 0;padding:14px;background:#fafafa;border-radius:8px;border-left:4px solid #FF6B35">
<h3 style="font-size:1.05em;font-weight:700;margin:0 0 8px;color:#333">{i+1}. {item["name"]}</h3>
<p style="margin:0 0 6px;line-height:1.6"><strong>💰 가격:</strong> {item.get("price", "-")}</p>
<p style="margin:0;line-height:1.6"><strong>💡 팁:</strong> {item.get("tip", "-")}</p>
</div>\n'''
    
    return html

def generate_unique_tips(area, category, page_idx):
    """고유한 팁 섹션 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_tips"))
    tips = TIP_TEMPLATES.get(category, TIP_TEMPLATES["food"])
    
    selected = rng.sample(tips, min(5, len(tips)))
    
    html = f'<h2>💡 {area} {CATEGORIES[category]["name"]} 실전 팁</h2>\n<ul style="padding-left:20px;margin:12px 0">\n'
    for tip in selected:
        html += f'<li style="margin-bottom:8px;line-height:1.7">{tip}</li>\n'
    html += '</ul>\n'
    return html

def generate_unique_anecdote(area, category, page_idx, data):
    """고유한 에피소드/명언 생성"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_anecdote"))
    
    spots = data.get("spots", [])
    food = data.get("food", [])
    
    template = rng.choice(ANECDOTE_TEMPLATES)
    result = template.format(
        area=area,
        activity=rng.choice(["트레킹", "서핑", "식사", "쇼핑", "산책", "다이빙", "마사지"]),
        observation=rng.choice([
            f"예상보다 훨씬 아름다운 풍경에 감동했습니다",
            f"현지인들의 친절함에 다시 오고 싶어졌어요",
            f"가격 대비 만족도가 매우 높았습니다",
            f"사진으로는 표현할 수 없는 분위기가 있었어요",
            f"한국인 여행자가 아직 많지 않아 조용하게 즐길 수 있었습니다",
        ]),
        visit_count=rng.choice(["3", "5", "7", "10"]),
        local_name=rng.choice(["Wayan", "Made", "Ketut", "Nyoman", "Komang"]),
        local_tip=rng.choice([
            f"오전에 가면 사람이 적다고 하더라고요",
            f"현지인만 아는 숨은 메뉴가 있다고 알려줬어요",
            f"비수기에 오면 가격이 30% 저렴하다고 합니다",
            f"사진 찍기 좋은 시간대가 따로 있다고 하더라고요",
        ]),
        month=rng.choice(["1", "3", "5", "7", "9", "11"]),
        quote=rng.choice([
            "생각보다 저렴하다", "다시 오고 싶다", "여기가 진짜 발리다",
            "한국에서는 이 가격에 못 먹는다", "사진이 실물을 못 담는다",
        ]),
        surprising_fact=rng.choice([
            f"입장료가 무료인 곳이 많다는 것",
            f"로컬 음식 가격이 한국의 1/5 수준이라는 것",
            f"자연 명소가 관광지화되지 않고 보존되어 있다는 것",
            f"현지인들이 한국 문화에 관심이 많다는 것",
        ]),
        insight=rng.choice([
            f"갈 때마다 새로운 명소가 생기고 있어요",
            f"비수기가 오히려 여행하기 더 좋습니다",
            f"로컬 맛집이 관광지 맛집보다 훨씬 낫습니다",
            f"10년 전과 비교하면 인프라가 크게 발전했어요",
        ]),
        first_day_observation=rng.choice([
            "교통체증에 놀라고",
            "더위에 적응하느라 힘들고",
            "흥정 문화에 당황하고",
            "음식 맛에 감동하고",
        ]),
        day2_recommendation=rng.choice([
            "여유롭게 즐기는 게 포인트예요",
            "로컬 리듬에 맞춰 움직이면 훨씬 즐거워요",
            "아침 일찍 움직이면 하루를 알차게 보낼 수 있어요",
            "숙소 주변만 탐방해도 충분히 즐거워요",
        ]),
        question=rng.choice([
            "여기서 가장 맛있는 집이 어디예요?",
            "사진 찍기 좋은 곳은요?",
            "비수기에 오면 사람이 적나요?",
            "가성비 숙소 추천해주세요",
        ]),
        answer=rng.choice([
            "로컬 와룽이 최고예요",
            "일몰 시간에 오세요",
            "비수기가 훨씬 좋아요",
            "게스트하우스도 충분합니다",
        ]),
    )
    return f'<div style="margin:16px 0;padding:14px;background:#f8f9fa;border-radius:8px;border-left:4px solid #6c757d;font-style:italic;color:#555">{result}</div>\n'

def generate_unique_footer(area, category, page_idx):
    """고유한 마무리"""
    rng = random.Random(hash(f"{area}_{category}_{page_idx}_footer"))
    
    footers = [
        f"이상으로 {area}의 {CATEGORIES[category]['name']} 정보를 정리했습니다. {CURRENT_YEAR}년 기준 최신 정보이니 참고하세요.",
        f"{area} 여행 계획에 도움이 되셨길 바랍니다. 추가 질문은 댓글로 남겨주세요!",
        f"다음 글에서는 {rng.choice(AREAS)}의 {rng.choice(list(CATEGORIES.values()))['name']} 정보를 정리할 예정입니다.",
        f"{area} {CATEGORIES[category]['name']} 여행, 즐거운 시간 보내세요! 🌴",
        f"이 글이 {area} 여행 계획에 도움이 되길 바랍니다. {CURRENT_YEAR}년 {rng.choice(['4월', '5월', '6월'])} 기준 정보입니다.",
        f"{area}에서의 {CATEGORIES[category]['name']} 경험이 저처럼 좋은 추억이 되길 바랍니다.",
    ]
    
    return f'<div class="content-footer"><p>{rng.choice(footers)}</p><p style="margin-top:6px;font-size:0.85em;color:#999">📅 {CURRENT_YEAR}년 {rng.choice(["4월", "5월"])} 업데이트</p></div>\n'

def generate_html(area, category, page_idx):
    """단일 HTML 페이지 생성 (고유 콘텐츠)"""
    data = BALI_DATA.get(area, {})
    cat_info = CATEGORIES[category]
    
    # SEO 제목 (14가지 변형)
    title_seeds = [
        f"{area} {cat_info['name']} 추천 — {CURRENT_YEAR} 최신 가이드",
        f"{area} {cat_info['name']} 완벽 정리 — 가격·팁·후기",
        f"{area} 여행 {cat_info['name']} — 현지인이 추천하는 진짜 정보",
        f"{area} {cat_info['name']} 베스트 — {CURRENT_YEAR} 실제 후기",
        f"{area} 자유여행 {cat_info['name']} — 놓치면 후회하는 꿀팁",
        f"{area} {cat_info['name']} 가이드 — 10년차 블로거 추천",
        f"{area} {cat_info['name']} 총정리 — 비용·위치·팁 비교",
        f"{area} {cat_info['name']} 탐방기 — 직접 다녀온 솔직 리뷰",
        f"{area} {cat_info['name']} 추천 리스트 — 예산별 BEST",
        f"{area} {cat_info['name']} 숨은 명소 — 현지인만 아는 곳",
        f"{area} {cat_info['name']} 맛있는 코스 — 하루 일정 추천",
        f"{area} {cat_info['name']} 포토스팟 — 인생샷 찍는 법",
        f"{area} {cat_info['name']} 비용 절약 — 가성비 최적화 팁",
        f"{area} {cat_info['name']} 초보 가이드 — 처음 방문자를 위해",
    ]
    title = title_seeds[page_idx % len(title_seeds)]
    meta_desc = f"{area} {cat_info['name']} 여행 정보. 가격 비교, 숨은 명소, 실전 팁까지. {CURRENT_YEAR}년 기준 최신 후기."
    
    # 날짜 (페이지별 고유)
    base_date = datetime(2026, 4, 1)
    page_date = base_date + timedelta(days=page_idx % 30)
    date_str = page_date.strftime("%Y-%m-%d")
    
    # 이미지 (페이지별 고유 세트)
    images = get_images(area, category, 10, page_idx)
    images_html = ""
    for i, img in enumerate(images):
        img_path = f"../../images/{area}/{category}/{img}"
        alt_text = f"{area} {cat_info['name']} 여행 사진 {i+1}"
        images_html += f'<figure style="margin:20px 0;text-align:center"><img src="{img_path}" alt="{alt_text}" loading="lazy" style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)" /></figure>\n'
    
    # 고유 콘텐츠 섹션
    intro_html = generate_unique_intro(area, category, page_idx, data)
    qa_html = generate_unique_qa(area, category, page_idx, data)
    body_html = generate_unique_content_body(area, category, page_idx, data)
    tips_html = generate_unique_tips(area, category, page_idx)
    anecdote_html = generate_unique_anecdote(area, category, page_idx, data)
    footer_content_html = generate_unique_footer(area, category, page_idx)
    
    # 가격비교 표
    price_comp = data.get("price_comparison", [])
    price_table = ""
    if price_comp:
        price_table = f'''<h2>💰 {area} 가격 비교 (로컬 vs 투어 vs 호텔)</h2>
<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white">
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">💰 로컬</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">🎫 투어</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">🏨 호텔</th>
</tr></thead><tbody>'''
        for i, pc in enumerate(price_comp):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            price_table += f'''<tr style="background:{bg}">
<td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">{pc["item"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd;color:#2e7d32;font-weight:600">{pc["local"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd">{pc["tour"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd">{pc["hotel"]}</td>
</tr>'''
        price_table += '''</tbody></table></div>
<p style="margin:6px 0;font-size:.85em;color:#666">※ 로컬 = 직접 방문 시 / 투어 = 투어 포함 시 / 호텔 = 호텔 내 레스토랑 시</p>'''
    
    # 숨은 명소
    hidden = data.get("hidden_gem", "")
    hidden_html = ""
    if hidden:
        hidden_html = f'''<h2>💎 숨은 명소</h2>
<div style="margin:12px 0;padding:14px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:8px;border:1px solid #ffe0b2">
<p style="margin:0;font-weight:600;color:#e65100">{hidden}</p>
</div>'''
    
    # 명소 리스트
    spots = data.get("spots", [])
    spots_html = ""
    if spots:
        spots_html = f'<h2>📍 {area} 추천 명소</h2>\n<ol style="padding-left:20px;margin:12px 0">\n'
        for i, s in enumerate(spots):
            spots_html += f'<li style="margin-bottom:6px;line-height:1.7"><strong>{s}</strong></li>\n'
        spots_html += '</ol>\n'
    
    # 교통 정보
    transport = data.get("transport", [])
    transport_html = ""
    if transport:
        transport_html = f'''<h2>🚗 {area} 교통 정보</h2>
<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white"><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">정보</th></tr></thead>
<tbody>'''
        for i, t in enumerate(transport):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            transport_html += f'<tr style="background:{bg}"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">{t["name"]}</td><td style="padding:10px 8px;border:1px solid #ddd">{t["price"]}</td></tr>\n'
        transport_html += '</tbody></table></div>\n'
    
    # 숙소 정보
    hotels = data.get("hotels", {})
    hotel_html = ""
    if hotels:
        hotel_html = f'''<h2>🏨 {area} 숙소 추천</h2>
<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#1565c0;color:white"><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">등급</th><th style="padding:10px 8px;text-align:left;border:1px solid #ddd">가격대</th></tr></thead>
<tbody>
<tr style="background:#f9f9f9"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰 예산형</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('budget', '-')}</td></tr>
<tr style="background:#ffffff"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰💰 중급</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('mid', '-')}</td></tr>
<tr style="background:#f9f9f9"><td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">💰💰💰 고급</td><td style="padding:10px 8px;border:1px solid #ddd">{hotels.get('high', '-')}</td></tr>
</tbody></table></div>\n'''
    
    # 관련 지역 링크
    other_areas = [a for a in AREAS if a != area]
    rng_link = random.Random(hash(f"{area}_{category}_{page_idx}_links"))
    related = rng_link.sample(other_areas, min(3, len(other_areas)))
    related_html = f'<h2>🔗 관련 지역 추천</h2>\n<div style="display:flex;flex-wrap:wrap;gap:10px;margin:12px 0">\n'
    for ra in related:
        rpage = (page_idx + 1) % 14 + 1
        related_html += f'<a href="/{ra}/{category}/{rpage:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{ra} {cat_info["name"]}</a>\n'
    related_html += '</div>\n'
    
    # 쿠폰 HTML
    coupon_html = f'''<div style="margin:24px 0;text-align:center">
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰" style="max-width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12)" loading="lazy" />
</a>
<p style="margin-top:10px;font-size:.85em;color:#666">마이리얼트립 할인쿠폰 — 투어/티켓/숙소 최대 30% 할인</p>
</div>'''
    
    # 최종 HTML 조립
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{area}, 발리, 인도네시아, {cat_info['name']}, 여행, 자유여행, 가격비교, {CURRENT_YEAR}">
<link rel="canonical" href="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE_URL}/images/{area}/001.webp">
<meta property="og:url" content="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:site_name" content="발리 여행 블로그">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "{title}", "description": "{meta_desc}", "image": ["{SITE_URL}/images/{area}/001.webp"], "datePublished": "{date_str}", "dateModified": "{date_str}", "author": {{"@type": "Person", "name": "{AUTHOR}"}}, "publisher": {{"@type": "Organization", "name": "발리 여행 블로그"}}, "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html"}}}}</script>
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
article h3 {{ color: #333; font-size: 1.15rem; margin: 20px 0 10px; }}
article table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
article th, article td {{ padding: 10px 8px; border: 1px solid #ddd; text-align: left; }}
article th {{ background: #FF6B35; color: white; }}
article tr:nth-child(even) {{ background: #f9f9f9; }}
article ul, article ol {{ padding-left: 20px; margin: 16px 0; }}
article li {{ margin-bottom: 8px; line-height: 1.7; }}
.content-intro {{ margin: 0 0 20px; padding: 16px 20px; background: linear-gradient(135deg, #fff7ed, #fff3e0); border-radius: 10px; border: 1px solid #ffe0b2; font-weight: 500; }}
.content-footer {{ margin: 24px 0; padding: 12px; background: #f5f5f5; border-radius: 8px; font-size: 0.9em; color: #666; }}
.tags {{ margin: 20px 0; }}
.tag {{ display: inline-block; background: #F0F0F0; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 3px; color: var(--text-light); }}
footer {{ text-align: center; padding: 30px; color: var(--text-light); font-size: 0.85rem; }}
@media (max-width: 600px) {{ .container {{ padding: 10px; }} article {{ padding: 20px; }} header h1 {{ font-size: 1.4rem; }} table {{ font-size: .8em; }} }}
</style>
</head>
<body>

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

<!-- 결론 요약 박스 -->
<div class="content-intro">{intro_html}</div>

<!-- 쿠폰 (상단) -->
{coupon_html}

<!-- 이미지 10장 -->
{images_html}

<!-- Q&A 섹션 -->
<h2>❓ 자주 묻는 질문</h2>
{qa_html}

<!-- 카테고리별 상세 콘텐츠 -->
{body_html}

<!-- 에피소드/명언 -->
{anecdote_html}

<!-- 가격비교 표 -->
{price_table}

<!-- 명소 -->
{spots_html}

<!-- 숨은 명소 -->
{hidden_html}

<!-- 교통 -->
{transport_html}

<!-- 숙소 -->
{hotel_html}

<!-- 실전 팁 -->
{tips_html}

<!-- 관련 지역 링크 -->
{related_html}

<!-- 쿠폰 (하단) -->
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

<!-- 마무리 -->
{footer_content_html}

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
    print("🏗️  발리 여행 블로그 빌드 시스템 v5 (고유 콘텐츠)")
    print("=" * 60)
    
    OUTPUT_HTML.mkdir(parents=True, exist_ok=True)
    
    total = 0
    pages_per_combo = 14  # 11 areas × 6 cats × 14 = 924
    
    for area in AREAS:
        print(f"\n📍 {area}")
        for category in CATEGORIES:
            for page_idx in range(pages_per_combo):
                html = generate_html(area, category, page_idx)
                
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
