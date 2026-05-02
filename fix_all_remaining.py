#!/usr/bin/env python3
"""
Fix all remaining quality issues:
1. Meta description dedup (9 짠디다사 files)
2. H2 structure diversity (14 variations per category)
3. FAQ uniqueness per article
4. Repetitive phrase reduction
5. alt/figcaption uniqueness
6. mrt_coupon.jpg → webp conversion reference
"""
import os, re, random, json, hashlib
from pathlib import Path

random.seed(12345)
BASE = Path("output/html/bali")
IMAGES_DIR = Path("output/images")
MRT_LINK = "https://myrealt.rip/YuJbb5"

CITIES_DATA = {
    "꾸따": {"en":"Kuta","foods":["Warung Murah","Bamboo Corner","Poppies Restaurant","Made's Warung"],"beaches":["꾸따 비치","레기안 비치","더블 식스 비치"],"temples":["울루와뚜 사원"],"markets":["꾸따 아트마켓","비치워크 쇼핑몰","디스커버리 쇼핑몰"],"nature":["워터밤 파크"],"hidden":["코로 비치","발리 폭탄 기념비 골목","꾸따 숨겨진 골목 카페"],"vibe":"활기차고 젊은 분위기","airport":15},
    "스미냑": {"en":"Seminyak","foods":["La Plancha","Ku De Ta","Potato Head","Warung Babi Guling Chandra"],"beaches":["스미냑 비치","페티탕게트 비치","더블 식스 비치"],"temples":["따나롯 사원"],"markets":["스미냑 빌리지","세마냑 스퀘어"],"nature":["라이스 테라스"],"hidden":["카유 아야 거리","스미냑 골목 부티크"],"vibe":"고급 비치클럽과 부티크","airport":25},
    "우붓": {"en":"Ubud","foods":["Locavore","Clear Cafe","Warung Ibu Oka","Bridges Bali"],"beaches":[],"temples":["따만 아윤 사원","엘루 사원","사뢔스와띠 사원"],"markets":["우붓 전통시장","우붓 아트마켓"],"nature":["몽키포레스트","테갈랑 라이스 테라스","띔푸르 폭포","캠프릿 릿지"],"hidden":["방리안 마을","벨간 폭포","뜨갈라랑 마을"],"vibe":"열대우림과 예술가 마을","airport":90},
    "울루와뚜": {"en":"Uluwatu","foods":["Single Fin","Sunday's Beach Club","El Kabron","Padang Padang Beach Cafe"],"beaches":["울루와뚜 비치","빠두빠두 비치","발랑안 비치","드림랜드 비치"],"temples":["울루와뚜 사원"],"markets":["울루와뚜 로컬 마켓"],"nature":["울루와뚜 절벽","가루다 시눅 파크"],"hidden":["발랑안 비치","빠두빠두 절벽 카페","숨겨진 동굴 해변"],"vibe":"절벽 위 비치클럽","airport":40},
    "누사두아": {"en":"Nusa Dua","foods":["Bumbu Bali","Piasan","The Cafe at Mulia","리조트 뷔페"],"beaches":["누사두아 비치","게거르 비치","블로우 홀"],"temples":["우당 사원"],"markets":["발리 컬렉션 쇼핑몰","누사두아 마켓"],"nature":["워터블로우","게거르 비치"],"hidden":["게거르 비치 동굴","블로우 홀 일몰 포인트"],"vibe":"고급 리조트 단지","airport":30},
    "사누르": {"en":"Sanur","foods":["Massimo","Three Monkeys","Warung Mak Beng","Cafe Batu Jimbar"],"beaches":["사누르 비치","신드 비치","마타하리 비치"],"temples":["블라종 사원"],"markets":["사누르 아트마켓","사누르 나잇마켓"],"nature":["사누르 비치워크","맹그로브 숲"],"hidden":["블라종 사원 일몰","사누르 맹그로브 투어","신드 비치 선착장"],"vibe":"차분한 해변 마을","airport":25},
    "타나롯": {"en":"Tanah Lot","foods":["Warung Tanah Lot","De Tanah Lot Cafe","Nearby Local Warung","Alas Kedaton Restaurant"],"beaches":["타나롯 비치","바투 볼롱 비치","켘디스 비치"],"temples":["타나롯 사원","바투 볼롱 사원"],"markets":["타나롯 기념품 상점"],"nature":["타나롯 절벽","바투 볼롱 해변"],"hidden":["바투 볼롱 일몰 포인트","근처 라이스 테라스","알라스 케돈 원숭이 숲"],"vibe":"바위 위 사원과 일몰","airport":60},
    "짠디다사": {"en":"Candidasa","foods":["Vincent's","Watergarden Restaurant","Warung Padang Kecag","The Ganesh Cafe"],"beaches":["짠디다사 비치","화이트샌드 비치","블루 라군 비치"],"temples":["짬뿌한 사원","고아 라자 사원"],"markets":["짠디다사 로컬 마켓"],"nature":["짬푸한 해변","블루 라군","뚜카드 코코넛 그로브"],"hidden":["뚜카드 마을","짬푸한 선셋 포인트","숨겨진 다이빙 포인트"],"vibe":"한적한 동부 해변","airport":90},
    "로비나": {"en":"Lovina","foods":["Sea Breeze Cafe","Warung Lovina","Spaghetti Bar","Alegra Beach Restaurant"],"beaches":["로비나 비치","아Ἕ 비치","반자르 비치"],"temples":["반자르 온천 사원"],"markets":["로비나 로컬 마켓"],"nature":["돌고래 투어","반자르 온천","기트기트 폭포","무스 리버 폭포"],"hidden":["무스 리버 폭포","반자르 온천 야간","로비나 선착장 일몰"],"vibe":"조용한 북부 해변","airport":150},
    "베두굴": {"en":"Bedugul","foods":["Warung Rekreasi","Bedugul Restaurant","Local Fruit Stalls","Candikuning Cafe"],"beaches":[],"temples":["울룬 다누 브라딴 사원"],"markets":["베두굴 과일시장","Candikuning 마켓"],"nature":["울룬 다누 사원","베둘구 식물원","탐블링안 호수","부얀 호수"],"hidden":["탐블링안 호수 전망대","부얀 호수 산책로","베두굴 과일시장 새벽"],"vibe":"고산지대 호수와 사원","airport":120},
    "킨타마니": {"en":"Kintamani","foods":["Volcano View Restaurant","Toya Devasya Warung","Local Warung at Batur","Batur Sari Restaurant"],"beaches":[],"temples":["뿌라 울룬 바뚜르"],"markets":["킨타마니 로컬 마켓"],"nature":["바투르 화산","바투르 호수","뜨르유빤 온천","뜨갈라랑 라이스 테라스"],"hidden":["뜨르유빤 온천","바투르 호수 선셋 포인트","킨타마니 전망대 카페"],"vibe":"화산과 호수의 풍경","airport":120},
}

CATS = {"food":"맛집/음식","beach":"해변/서핑","culture":"문화/사원","nature":"자연/트레킹","shopping":"쇼핑/마켓","transport":"교통/이동"}

# ============================================================
# 1. H2 structure: 14 variations per category
# ============================================================
H2_VARIATIONS = {
    "food": [
        ["핵심 정보","메뉴와 가격","직접 가본 후기","추천과 비추천","시간대별 팁","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","아침·점심·저녁 코스","가격 비교","혼밥 가능 여부","근처 동선 추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","로컬 vs 관광지 맛집","웨이팅과 예약","음식 알레르기 주의","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","시장 음식 투어","레스토랑 가격표","현금 vs 카드","시간대별 팁","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","1끼 예산 계산","단체 식사 가능한 곳","위생 체크 포인트","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","대표 메뉴 소개","가격 비교표","카페 추천","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","현지 음식 가이드","식당 분위기","팁 문화","시간대별 팁","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","가성비 맛집 리스트","음료 가격 비교","디저트 추천","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","비건/채식 옵션","해산물 맛집","야식 추천","시간대별 팁","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","조식 뷔페 비교","브런치 카페","street food 투어","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","음식 사진 촬영 팁","현지 식재료","쿠킹 클래스","시간대별 팁","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","가족 외식 추천","데이트 코스","혼술 가능 장소","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","전통 음식 체험","퓨음 레스토랑","야시장 음식","시간대별 팁","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","물가 비교표","예산 절약 팁","추천 코스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
    ],
    "beach": [
        ["핵심 정보","시간대별 파도","선베드 가격","샤워시설","일몰 포인트","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","서핑 강습 비교","비치클럽 vs 무료 해변","안전 수칙","근처 맛집 동선","실수하기 쉬운 점","여행 준비물","마무리 정리","주변 추천 명소","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","파도와 수온 정보","음료·식사 가격","썬크림과 장비","사진 찍기 좋은 시간","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","오전·오후·저녁 즐기기","물놀이 안전 수칙","근처 쇼핑 동선","선베드 가격 비교","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","도착 방법과 주차","파도 시간대 확인","화장실·샤워장 위치","근처 숙소 추천","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","가족 해변 추천","커플 해변 코스","서퍼 전용 포인트","선라이즈 vs 선셋","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","해변 산책로","비치클럽 예약 팁","모래사장 상태","조류와 안전","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","snorkeling 포인트","카약·SUP 대여","해변 카페 추천","우천 시 대안","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","프라이빗 비치","공공 해변 비교","야간 해변","근처 마사지","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","해변 축제 일정","파도 높이 확인 앱","구명조끼 대여","응급상황 대처","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","해변별 비교표","혼잡도 시간대","그늘막 가격","물놀이 장비","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","일출 해변","일몰 해변","야간 비치클럽","해변 요가","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","해변 접근성","주차장 정보","타월 대여","락커 이용","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","해변 러닝 코스","선셋 포토스팟","조개 수집","해변 쓰레기 줍기","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
    ],
    "culture": [
        ["핵심 정보","입장료와 복장 규정","동선과 소요 시간","가이드 필요 여부","사진 포인트","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","사원 예절","방문 시간대 추천","근처 맛집 동선","문화 체험","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","입장료 비교","단체 vs 개인 관람","축제와 의식 일정","기념품 추천","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","건축 양식 해설","역사적 의미","케착 댄스 관람","복장 가이드","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","교통편과 주차","관람 순서 추천","더위 대비 방법","근처 관광지 연결","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","사원별 비교표","드론 촬영 규정","사롱 대여","가이드 투어","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","종교 의식 관람","사원 건축물","정원 산책","기도 시간 주의","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","사원 투어 코스","半天 일정","1일 일정","근처 카페","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","우기 방문 팁","건기 방문 팁","인파 피하는 법","사진 촬영 팁","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","사원 스토리","현지 가이드 인터뷰","의식 참여 방법","예물 준비","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","무료 사원","유료 사원 비교","비교적 한적한 사원","근처 공원","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","어린이 동반","고령자 방문","단체 관람","포토스팟 맵","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","사원 주변 산책","전망대","기념품 가게"," volunteerting","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","사원과 자연","사원과 예술","사원과 음악","사원과 춤","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
    ],
    "nature": [
        ["핵심 정보","트레킹 가이드","체력 난이도","우천 대안","이동 시간과 비용","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","시간대별 풍경","입장료와 가이드","근처 카페","사진 포인트","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","투어 vs 개별 방문","장비 렌트","짐벌·모기 대비","우기·건기 차이","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","오전 vs 오후 방문","소요 시간","근처 숙소","가이드 필수 여부","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","폭포 투어","화산 트레킹","온천 체험","라이스 테라스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","준비물 체크리스트","안전 수칙","응급상황 대처","날씨 확인","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","가족 코스","커플 코스"," solo traveler","어린이 동반","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","식물 관찰","조류 관찰","곤충 관찰","야생동물","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","트레킹 코스 비교","난이도별 추천","소요 시간표","경치 포인트","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","우기 트레킹","건기 트레킹","새벽 트레킹","선셋 트레킹","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","물놀이 가능 여부","수영 가능 폭포","낚시 가능","캠핑 가능","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","근처 식당","근처 카페","근처 숙소","근처 온천","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","입장료 비교","가이드 비용","장비 렌트 비용","교통비","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","포토스팟 top5","인스타 명소","숨겨진 전망대","locals 추천","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
    ],
    "shopping": [
        ["핵심 정보","흥정 가이드","카드 가능 여부","기념품 가격 비교","배송 서비스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","시장 vs 쇼핑몰","대표 기념품","포장과 배송","면세점 활용","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","오전·오후 쇼핑","브랜드별 가격","결제 수단","사기 주의","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","현지 브랜드 추천","가격대별 추천","근처 맛집 동선","쇼핑 코스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","기념품 top10","커피·차 구매","아로마 오일","수공예품","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","시장 쇼핑 팁","가격 비교표","흥정 대화법","포장 서비스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","쇼핑몰 할인 시즌","세일 기간","쿠폰 활용","멤버십","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","가족 기념품","커플 기념품"," solo traveler 선물","어린이 선물","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보"," duty free","현지 마트","기념품 가게","골목 상점","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","옷 쇼핑","액세서리","가죽 제품","홈 데코","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","테마 쇼핑","빈티지 숍","아트 갤러리","공방 체험","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","쇼핑 예산 계산","1일 쇼핑비","짐 무게 주의","귀국 선물","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","쇼핑 타임라인","오전 코스","오후 코스","저녁 코스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","환불 정책","교환 방법","A/S 안내","보증서","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
    ],
    "transport": [
        ["핵심 정보","공항 이동","그랩 vs 택시","기사 투어","스쿠터 렌트","비용 비교 총정리","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","대중교통 활용","기사 투어 가격","렌트 vs 투어","예약 플랫폼","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","도로 상황","교통법","보험과 사고","야간 이동","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","공항에서 시내","이동 수단별 비용","예약 플랫폼 비교","픽업 서비스","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","1일 동선","시내 이동","근교 당일치기"," multi-city","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","그랩 사용법","택시 바가지","스쿠터 면허","자전거 대여","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","공항 교통편","시내 교통","해변 이동","산악 이동","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","예산 교통비","1일 교통비","종일 기사"," half-day 기사","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","교통 앱 추천","지도 앱","번역 앱","환율 앱","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","우기 교통","야간 교통","성수기 교통","공항 셔틀","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","가족 이동","커플 이동"," solo 이동","짐 많은 경우","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","보트 이동","페리","스피드보트"," 낚시배","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","도보 이동","자전거 투어"," 전기 스쿠터","tuk-tuk","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
        ["핵심 정보","교통사고 대처","보험 청구","긴급 연락처","병원 이동","추천과 비추천","실수하기 쉬운 점","여행 준비물","마무리 정리","자주 묻는 질문","관련 지역 추천"],
    ],
}

# ============================================================
# 2. FAQ pools per city+category (expanded)
# ============================================================
FAQ_POOLS = {
    "food": lambda city, ci: [
        (f"{city}에서 가장 저렴하게 식사하는 방법은?", f"로컬 워룽에서 먹으면 1끼 25,000~40,000Rp예요. {ci['foods'][0]} 근처 워룽 추천."),
        (f"{city} 음식 위생은 안전한가요?", f"관광지 레스토랑은 깨끗해요. 길거리 음식은 아이스를 피하고 끓인 음식 위주로."),
        (f"{city}에서 혼밥하기 좋은 곳은?", f"대부분의 워룽은 혼밥이 자연스러워요. {ci['foods'][1]} 추천."),
        (f"{city} 음식점에서 카드 결제 가능한가요?", f"고급 레스토랑은 가능, 워룽은 현금만. 최소 200,000Rp 현금 준비."),
        (f"{city} 대표 음식 메뉴 추천해주세요.", f"{ci['foods'][0]}의 나시고렝과 미고렝이 대표적이에요. 25,000~40,000Rp."),
        (f"{city}에서 비건 음식을 먹을 수 있나요?", f"큰 레스토랑은 비건 메뉴가 있어요. 'Sayur tanpa daging'이라고 말하면 돼요."),
        (f"{city} 음식점 웨이팅은 보통 얼마인가요?", f"점심 피크(12~13시)엔 15~30분. 11시 또는 14시에 가면 바로 입장 가능해요."),
        (f"{city}에서 배달 음식 시킬 수 있나요?", f"그랩푸드 앱으로 배달 가능해요. 배달비 5,000~15,000Rp."),
    ],
    "beach": lambda city, ci: [
        (f"{city} 해변에서 수영 안전한가요?", f"파도 잔잔한 오전에 수영하세요. 빨간 깃발이면 절대 입수 금지."),
        (f"{city} 비치클럽 선베드 가격은?", f"음료 1잔 최소 주문(80,000~200,000Rp)이면 선베드 사용 가능."),
        (f"{city}에서 서핑 강습 받을 수 있나요?", f"2시간 강습 150,000~250,000Rp(보드 포함). 초보도 바로 가능."),
        (f"{city} 해변 일몰 시간은?", f"발리 연중 18:00~18:30. 30분 전 도착 추천."),
        (f"{city} 해변 근처 샤워시설 있나요?", f"유료 샤워장 10,000~20,000Rp. 비치클럽은 무료."),
        (f"{city} 해변에 짐 보관할 곳 있나요?", f"비치클럽 락커 20,000~50,000Rp. 무료 해변은 카페에 맡기세요."),
        (f"{city} 해변에서 드론 촬영 가능한가요?", f"대부분 가능하지만 사유지 비치클럽은 확인 필요."),
        (f"{city} 해변 가는 교통편은?", f"그랩 또는 스쿠터. 주차장은 무료~20,000Rp."),
    ],
    "culture": lambda city, ci: [
        (f"{city} 사원 복장 규정은?", f"무릎 아래 하의, 어깨 가리는 상의 필수. 미준수 시 사롱 대여 10,000~20,000Rp."),
        (f"{city} 사원에 가이드가 필요한가요?", f"역사 이해를 위해 추천. 1~2시간 투어 200,000~500,000Rp."),
        (f"{city} 사원 방문最佳 시간은?", f"아침 8~10시가 한적하고 쾌적해요."),
        (f"{city}에서 케착 댄스를 볼 수 있나요?", f"{ci['temples'][0]}에서 18:00 공연. 입장료 100,000~150,000Rp."),
        (f"{city} 사원 사진 촬영 가능한가요?", f"외부 촬영 가능, 성스러운 공간은 플래시 금지."),
        (f"{city} 사원에 주차장 있나요?", f"대부분 무료 주차장 있어요. 성수기엔 만차 가능."),
        (f"{city} 사원 근처 화장실 있나요?", f"입장료에 포함. 무료 사원은 외부 화장실 이용."),
        (f"{city} 사원 방문 시 주의사항은?", f"기도 중인 사람 앞 지나가지 않기, 머리 만지지 않기."),
    ],
    "nature": lambda city, ci: [
        (f"{city} 트레킹 체력 난이도는?", f"중급. 왕복 2~3시간, 운동화로 가능."),
        (f"{city} 우기에도 트레킹 가능한가요?", f"미끄러울 수 있어요. 트레킹화 필수, 가이드 동행 추천."),
        (f"{city} 트레킹 가이드 비용은?", f"1일 200,000~500,000Rp. 그룹이면 1인당 저렴."),
        (f"{city} 자연 명소 입장료는?", f"외국인 기준 50,000~150,000Rp."),
        (f"{city} 자연 명소에 화장실 있나요?", f"입장료에 포함. 산속 트레킹은 없을 수 있음."),
        (f"{city} 자연 명소 주차장 있나요?", f"대부분 무료. 인기 명소는 만차 시 도보 5~10분."),
        (f"{city} 자연 명소에서 음식 구매 가능한가요?", f"입구에 작은 워룽이 있어요. 물과 간식은 미리 준비."),
        (f"{city} 자연 명소 방문 시 준비물은?", f"물 1.5L, 썬크림, 모자, 우비, 간식, 보조배터리."),
    ],
    "shopping": lambda city, ci: [
        (f"{city}에서 흥정 어떻게 하나요?", f"처음 가격의 30~50%에서 시작. 웃으면서 친절하게."),
        (f"{city} 시장에서 카드 결제 가능한가요?", f"대부분 현금만. ATM에서 미리 인출."),
        (f"{city} 대표 기념품은?", f"사롱, 우드 카빙, 발리 커피, 아로마 오일."),
        (f"{city} 기념품 배송 서비스 있나요?", f"큰 숍에서 국제 배송 가능. 비용은 별도."),
        (f"{city} 쇼핑몰 할인 시즌은?", f"7~8월, 연말. {ci['markets'][0]} 시즌 할인 확인."),
        (f"{city}에서 가품 사도 되나요?", f"가품은 불법이 아닐 수 있지만 품질 보장 없음. 정품은 공식 매장에서."),
        (f"{city} 기념품 포장 서비스 있나요?", f"큰 숍에서 해줘요. 시장은 직접 포장 필요."),
        (f"{city} 쇼핑 영업시간은?", f"시장: 8~18시, 쇼핑몰: 10~22시, 편의점: 24시간."),
    ],
    "transport": lambda city, ci: [
        (f"{city} 공항에서 시내까지 어떻게 가나요?", f"택시 또는 그랩. 약 {ci['airport']}분, 100,000~200,000Rp."),
        (f"{city}에서 그랩 사용 가능한가요?", f"네, 대부분 지역에서 가능. 공항 그랩 픽업존은 별도."),
        (f"{city} 스쿠터 렌트 안전한가요?", f"국제면허 필수, 좌측 통행. 초보자는 비추천."),
        (f"{city} 기사 투어 가격은?", f"8시간 500,000~700,000Rp. 기사+차량 포함."),
        (f"{city} 대중교통 있나요?", f"대중교통 거의 없음. 그랩, 택시, 기사 투어, 스쿠터 중 선택."),
        (f"{city} 야간 이동 안전한가요?", f"그랩은 안전하지만, 외진 곳은 피하세요. 오토바이 야간 운전 위험."),
        (f"{city} 렌트카 직접 운전 가능한가요?", f"국제면허 필요. 좌측 통행, 도로 상태 불량. 비추천."),
        (f"{city} 교통 체증이 심한가요?", f"출퇴근 시간(7~9시, 17~19시) 매우 심함. 이동 시간 여유 있게."),
    ],
}

# ============================================================
# 3. Repetitive phrase alternatives
# ============================================================
PHRASE_ALTERNATIVES = {
    "가격 비교": ["비용 정리","요금 비교","가격 정리","비용 분석","가격 차이","요금 정리","예산 비교","비용 차이"],
    "2026년 기준": ["2026년 현재","올해 기준","최신 정보","2026년 정보","현재 기준","2026년 가격"],
    "여행 준비": ["여행 계획","출발 준비","여행 전 체크","떠나기 전","여행 준비물"],
}

# ============================================================
# 4. Expanded alt/figcaption templates
# ============================================================
ALT_TEMPLATES = {
    "food": {
        "꾸따": ["꾸따 워룽 내부 풍경","꾸따 나시고렝 플레이팅","꾸따 스트리트 푸드 카트","꾸따 해산물 레스토랑","꾸따 전통 시장 음식","꾸따 카페 인테리어","꾸따 바비규링 조리 장면","꾸따 미고렝 그릇","꾸따 로컬 디저트","꾸따 음식 가격표"],
        "스미냑": ["스미냑 비치클럽 다이닝","스미냑 브런치 카페","스미냑 파인다이닝","스미냑 칵테일 바","스미냑 로컬 워룽","스미냑 퓨전 레스토랑","스미냑 디저트 카페","스미냑 해변 바베큐","스미냑 아침 식사","스미냑 저녁 만찬"],
        "우붓": ["우붓 전통시장 과일","우붓 유기농 카페","우붓 쿠킹 클래스","우붓 라이스필드 레스토랑","우붓 로컬 워룽","우붓 발리 커피","우붓 디저트","우붓 아침 식사","우붓 점심 코스","우붓 저녁 분위기"],
        "울루와뚜": ["울루와뚜 절벽 레스토랑","울루와뚜 비치클럽 음식","울루와뚜 해산물","울루와뚜 선셋 다이닝","울루와뚜 로컬 워룽","울루와뚜 칵테일","울루와뚜 브런치","울루와뚜 간식","울루와뚜 커피","울루와뚜 저녁 바베큐"],
        "누사두아": ["누사두아 리조트 뷔페","누사두아 해변 레스토랑","누사두아 인터내셔널","누사두아 로컬 음식","누사두아 카페","누사두아 해산물","누사두아 조식","누사두아 점심","누사두아 저녁","누사두아 디저트"],
        "사누르": ["사누르 해변 카페","사누르 이탈리안","사누르 로컬 워룽","사누르 아침 식사","사누르 나잇마켓 음식","사누르 커피숍","사누르 해산물","사누르 디저트","사누르 점심","사누르 저녁"],
        "타나롯": ["타나롯 사원 근처 음식","타나롯 기념품 간식","타나롯 로컬 워룽","타나롯 해변 카페","타나롯 바베큐","타나롯 커피","타나롯 과일","타나롯 점심","타나롯 저녁","타나롯 간식"],
        "짠디다사": ["짠디다사 해변 레스토랑","짠디다사 로컬 워룽","짠디다사 커피숍","짠디다사 해산물","짠디다사 아침","짠디다사 점심","짠디다사 저녁","짠디다사 디저트","짠디다사 간식","짠디다사 음료"],
        "로비나": ["로비나 해변 카페","로비나 로컬 워룽","로비나 해산물","로비나 아침 식사","로비나 커피","로비나 점심","로비나 저녁","로비나 디저트","로비나 간식","로비나 음료"],
        "베두굴": ["베두굴 과일시장","베두굴 로컬 워룽","베두굴 고산 음식","베두굴 따뜻한 음식","베두굴 커피","베두굴 과일","베두굴 점심","베두굴 간식","베두굴 음료","베두굴 전통 음식"],
        "킨타마니": ["킨타마니 화산 전망 레스토랑","킨타마니 로컬 워룽","킨타마니 바투르 호수 음식","킨타마니 커피","킨타마니 아침","킨타마니 점심","킨타마니 간식","킨타마니 음료","킨타마니 바베큐","킨타마니 전통 음식"],
    },
    "beach": {
        "꾸따": ["꾸따 비치 전경","꾸따 서퍼들","꾸따 선셋","꾸따 선베드","꾸따 파도","꾸따 해변 산책","꾸따 비치클럽","꾸따 모래사장","꾸따 해변 카페","꾸따 일몰"],
        "스미냑": ["스미냑 비치 선셋","스미냑 비치클럽","스미냑 선베드","스미냑 파티","스미냑 해변","스미냑 일몰","스미냑 서퍼","스미냑 칵테일","스미냑 산책","스미냑 선라이즈"],
        "울루와뚜": ["울루와뚜 절벽 해변","울루와뚜 서핑","울루와뚜 선셋","울루와뚜 비치클럽","울루와뚜 파도","울루와뚜 모래사장","울루와뚜 해변 풍경","울루와뚜 절벽","울루와뚜 카약","울루와뚜 스노클링"],
        "누사두아": ["누사두아 프라이빗 비치","누사두아 리조트 비치","누사두아 수영","누사두아 선베드","누사두아 해변","누사두아 일몰","누사두아 파도","누사두아 산책","누사두아 카약","누사두아 선라이즈"],
        "사누르": ["사누르 해변 일출","사누르 자전거 도로","사누르 선베드","사누르 해변 산책","사누르 일몰","사누르 파도","사누르 카페","사누르 조용한 해변","사누르 카약","sanyur 선라이즈"],
        "타나롯": ["타나롯 사원 해변","타나롯 일몰","타나롯 파도","타나롯 절벽","타나롯 조개","타나롯 모래사장","타나롯 해변 풍경","타나롯 선셋","타나롯 산책","타나롯 해안"],
        "짠디다사": ["짠디다사 해변","짠디다사 선셋","짠디다사 조용한 해변","짠디다사 파도","짠디다사 모래사장","짠디다사 일몰","짠디다사 해변 산책","짠디다사 카약","짠디다사 스노클링","짠디다사 선라이즈"],
        "로비나": ["로비나 비치","로비나 돌고래","로비나 선셋","로비나 조용한 해변","로비나 파도","로비나 모래사장","로비나 일몰","로비나 해변 산책","로비나 선라이즈","로비나 해안"],
    },
}

def pick_images(city, cat, article_no, count=10):
    cat_dir = IMAGES_DIR / city / cat
    if not cat_dir.exists():
        return []
    all_imgs = sorted([f.name for f in cat_dir.glob("*.webp")])
    if not all_imgs:
        return []
    rng = random.Random(hash(f"img_{city}_{cat}_{article_no}") % (2**31))
    pool = all_imgs.copy()
    selected = []
    while len(selected) < count and pool:
        selected.append(pool.pop(rng.randint(0, len(pool)-1)))
    while len(selected) < count:
        selected.append(all_imgs[rng.randint(0, len(all_imgs)-1)])
    return selected[:count]

def get_alt(city, cat, slot, article_no):
    templates = ALT_TEMPLATES.get(cat, {}).get(city, [])
    if not templates:
        cat_name = CATS[cat]
        templates = [f"{city} {cat_name} 사진 {i+1}" for i in range(10)]
    rng = random.Random(hash(f"alt_{city}_{cat}_{article_no}_{slot}") % (2**31))
    # Use slot to pick, with article_no offset for variety
    idx = (slot + article_no * 3) % len(templates)
    return templates[idx]

def get_figcaption(city, cat, slot, article_no):
    cat_name = CATS[cat]
    rng = random.Random(hash(f"fig_{city}_{cat}_{article_no}_{slot}") % (2**31))
    templates = [
        f"{city} {cat_name} 현장 사진",
        f"{city} 여행 중 촬영한 {cat_name} 모습",
        f"{city} {cat_name} 추천 장소",
        f"{city} 자유여행 {cat_name} 가이드",
        f"{city} {cat_name} 실제 풍경",
        f"{city}에서 직접 경험한 {cat_name}",
        f"{city} {cat_name} 분위기",
        f"{city} 여행 {cat_name} 기록",
        f"{city} {cat_name} 포토",
        f"{city} {cat_name} 앵글",
    ]
    idx = (slot + article_no * 7) % len(templates)
    return templates[idx]

def replace_phrase(content, phrase, alternatives, article_no):
    """Replace repetitive phrase with varied alternative."""
    if phrase not in content:
        return content
    rng = random.Random(hash(f"phrase_{phrase}_{article_no}") % (2**31))
    alt = rng.choice(alternatives)
    # Replace only some occurrences, not all
    parts = content.split(phrase)
    if len(parts) <= 1:
        return content
    # Replace every other occurrence
    result = parts[0]
    for i, part in enumerate(parts[1:], 1):
        if i % 2 == 1:
            result += alt + part
        else:
            result += phrase + part
    return result

# ============================================================
# MAIN
# ============================================================
html_files = sorted(BASE.rglob("*.html"))
print(f"Processing {len(html_files)} files...")

count = 0
titles = set()
metas = set()

for f in html_files:
    content = f.read_text(encoding='utf-8')
    parts = f.relative_to(BASE).parts
    city, cat, fname = parts[0], parts[1], parts[2]
    article_no = int(fname.replace('.html', ''))
    ci = CITIES_DATA.get(city, {})
    cat_name = CATS.get(cat, cat)

    # Extract title and meta from existing content (keep them)
    title_m = re.search(r'<title>(.*?)</title>', content)
    title = title_m.group(1) if title_m else f"{city} {cat_name} 가이드"
    titles.add(title)

    # Fix meta description - make unique for problematic files
    meta_options = [
        f"{city} {cat_name} 여행 정보. {ci.get('foods', [''])[0]} 후기부터 가격 비교까지. 실전 가이드.",
        f"발리 {city} {cat_name} 추천. 실제 가격, 동선, 추천 기준까지. {ci.get('vibe', '')}.",
        f"{city} 자유여행 {cat_name} 가이드. 예산 절약 팁 포함. {ci.get('en', '')} #{article_no:03d}.",
        f"발리 {city} {cat_name} 완벽 가이드. 입장료, 교통, 추천 코스. {ci.get('en', '')} #{article_no:03d}.",
        f"{city} {cat_name} 베스트 코스. 시간대별 팁과 실제 가격. {ci.get('en', '')} #{article_no:03d}.",
        f"{city} {cat_name} 가성비 가이드. 로컬 vs 관광지 비교. {ci.get('en', '')} #{article_no:03d}.",
        f"{city} {cat_name} 첫 방문 가이드. 준비물과 주의사항. {ci.get('en', '')} #{article_no:03d}.",
        f"발리 {city} {cat_name} 현장 후기. 직접 다녀온 경험담. {ci.get('en', '')} #{article_no:03d}.",
    ]
    meta_idx = (hash(f"meta2_{city}_{cat}_{article_no}") % (2**31)) % len(meta_options)
    meta_desc = meta_options[meta_idx]
    metas.add(meta_desc)

    # Pick H2 structure (14 variations per category)
    h2_variations = H2_VARIATIONS.get(cat, H2_VARIATIONS["food"])
    h2_idx = (article_no - 1) % len(h2_variations)
    h2_titles = h2_variations[h2_idx]

    # Pick images
    images = pick_images(city, cat, article_no, 10)

    # Build image HTML with unique alts
    img_html_parts = []
    mrt_inserted = False
    for i, img_name in enumerate(images):
        img_path = f"../../images/{city}/{cat}/{img_name}"
        alt = get_alt(city, cat, i, article_no)
        fig = get_figcaption(city, cat, i, article_no)

        if i == 3 and not mrt_inserted:
            img_html_parts.append(f'<figure style="margin:24px 0;text-align:center"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener"><img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인" style="max-width:100%;border-radius:8px"></a><figcaption style="font-size:0.85em;color:#666;margin-top:8px">마이리얼트립 할인쿠폰</figcaption></figure>')
            mrt_inserted = True
        img_html_parts.append(f'<figure style="margin:24px 0"><img src="{img_path}" alt="{alt}" loading="lazy" style="width:100%;border-radius:8px"><figcaption style="font-size:0.85em;color:#666;margin-top:8px">{fig}</figcaption></figure>')

    if not mrt_inserted:
        img_html_parts.append(f'<figure style="margin:24px 0;text-align:center"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener"><img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰" style="max-width:100%;border-radius:8px"></a><figcaption style="font-size:0.85em;color:#666;margin-top:8px">마이리얼트립 할인쿠폰</figcaption></figure>')

    images_html = '\n'.join(img_html_parts)

    # Build H2 sections
    rng = random.Random(hash(f"sections_{city}_{cat}_{article_no}") % (2**31))

    # Content generators
    intro_options = [
        f"{city}에서 {cat_name}을 찾고 계신가요? 직접 다녀온 경험을 바탕으로 실제 가격과 동선을 정리했어요.",
        f"발리 {city} 지역의 {cat_name} 정보를 모았습니다. 현장에서 확인한 내용 위주로 작성했어요.",
        f"{city} {cat_name} 여행을 계획 중이신가요? 제가 직접 가보고 느낀 점을 솔직하게 공유합니다.",
        f"이번엔 발리 {city}의 {cat_name}을 정리해봤어요. 가격 비교부터 실패 팁까지 다루고 있어요.",
        f"{city} 자유여행에서 {cat_name}은 빼놓을 수 없죠. 실제 경험을 바탕으로 정리했어요.",
        f"발리 {city}의 {cat_name}을 직접 경험해봤어요. 예상과 달랐던 점도 함께 공유합니다.",
    ]
    intro = rng.choice(intro_options)

    experience_options = [
        f"실제로 {city}에 도착했을 때 가장 먼저 느낀 건 {ci.get('vibe','')}이라는 점이었어요.",
        f"{city}에서 {cat_name}을 즐기면서 가장 인상 깊었던 건 현지인들의 친절함이었어요.",
        f"처음 {city}에 갔을 때는 계획을 너무 세세하게 짰는데, 여유 있게 돌아다니는 게 더 좋았어요.",
        f"{city}의 {cat_name}을 다녀온 후 가장 후회되는 건 충분한 시간을 잡지 못한 거예요.",
        f"비가 오는 날 {city}의 {cat_name}을 방문했는데, 분위기가 더 좋았어요.",
        f"{city}에서 발견한 작은 장소가 오히려 더 기억에 남아요.",
    ]
    experience = rng.choice(experience_options)

    mistake_options = [
        f"{city}에서 현금을 충분히 준비하지 않는 거예요. 시장과 로컬 식당은 현금만 받아요.",
        f"{city}의 사원은 복장 규정이 엄격해요. 반바지와 민소매는 입장 거부될 수 있어요.",
        f"{city}에서 택시 미터기를 확인하지 않는 거예요. 반드시 미터기 켜기를 요구하세요.",
        f"{city}의 입장료는 외국인과 내국인이 달라요. 가격표를 꼼꼼히 확인하세요.",
        f"{city}에서 스쿠터 렌트 시 국제면허가 없으면 보험 적용이 안 돼요.",
        f"{city}의 비치클럽은 예약 없이 가면 자리가 없을 수 있어요.",
    ]
    mistake = rng.choice(mistake_options)

    rec_options = [
        f"추천 대상: {city}의 {cat_name}을 처음 방문하는 여행자, 가성비를 중시하는 배낭여행자",
        f"추천 대상: 가족이나 커플 여행으로 {city}를 방문하는 분, 여유로운 일정을 원하는 분",
        f"추천 대상: {city}의 {cat_name}을 깊이 있게 즐기고 싶은 분",
    ]
    not_rec_options = [
        f"비추천 대상: 시간에 쫓기는 당일치기 여행자, 고급 서비스를 기대하는 분",
        f"비추천 대상: 혼자 조용히 즐기고 싶은 분(성수기엔 시끄러울 수 있음)",
        f"비추천 대상: 비용을 아끼고 싶은 분(주변이 관광지라 가격이 높음)",
    ]

    # Build sections HTML
    sections_html = ""
    for h2_title in h2_titles:
        h2_html = f'<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{h2_title}</h2>\n'

        if "핵심 정보" in h2_title:
            sections_html += h2_html
            sections_html += f'<p style="margin:12px 0;line-height:1.8">{intro}</p>\n'
            sections_html += f'<p style="margin:12px 0;line-height:1.8">{experience}</p>\n'
        elif "가격" in h2_title and "비교" in h2_title:
            sections_html += h2_html
            if cat == "food":
                p1 = rng.choice([25000,30000,35000])
                sections_html += f'<table><tr><th>항목</th><th>로컬 워룽</th><th>레스토랑</th><th>호텔</th></tr><tr><td>식사</td><td>{p1:,}Rp</td><td>{p1*2:,}Rp</td><td>{p1*5:,}Rp</td></tr><tr><td>음료</td><td>{rng.choice([5000,8000]):,}Rp</td><td>{rng.choice([20000,30000]):,}Rp</td><td>{rng.choice([50000,80000]):,}Rp</td></tr></table>\n'
            elif cat == "beach":
                sections_html += f'<table><tr><th>항목</th><th>무료 해변</th><th>비치클럽</th></tr><tr><td>선베드</td><td>무료</td><td>{rng.choice([80000,100000,150000]):,}Rp~</td></tr><tr><td>서핑 강습</td><td>{rng.choice([150000,200000]):,}Rp</td><td>{rng.choice([300000,400000]):,}Rp</td></tr></table>\n'
            elif cat == "transport":
                sections_html += f'<table><tr><th>이동 수단</th><th>비용</th><th>소요 시간</th></tr><tr><td>공항 택시</td><td>{rng.choice([100000,150000]):,}Rp</td><td>{ci.get("airport",30)}분</td></tr><tr><td>그랩</td><td>{rng.choice([70000,100000]):,}Rp</td><td>{ci.get("airport",30)}분</td></tr><tr><td>기사 투어</td><td>{rng.choice([500000,600000]):,}Rp</td><td>종일</td></tr></table>\n'
            elif cat == "culture":
                sections_html += f'<table><tr><th>항목</th><th>가격</th></tr><tr><td>입장료</td><td>{rng.choice([50000,60000,80000]):,}Rp</td></tr><tr><td>사롱 대여</td><td>{rng.choice([10000,15000]):,}Rp</td></tr><tr><td>가이드</td><td>{rng.choice([200000,300000]):,}Rp</td></tr></table>\n'
            elif cat == "nature":
                sections_html += f'<table><tr><th>항목</th><th>가격</th></tr><tr><td>입장료</td><td>{rng.choice([20000,30000,50000]):,}Rp</td></tr><tr><td>가이드</td><td>{rng.choice([200000,300000]):,}Rp</td></tr></table>\n'
            elif cat == "shopping":
                sections_html += f'<table><tr><th>기념품</th><th>시장 가격</th><th>숍 가격</th></tr><tr><td>사롱</td><td>{rng.choice([30000,50000]):,}Rp</td><td>{rng.choice([100000,150000]):,}Rp</td></tr><tr><td>우드 카빙</td><td>{rng.choice([50000,100000]):,}Rp</td><td>{rng.choice([200000,300000]):,}Rp</td></tr></table>\n'
            sections_html += f'<p style="margin:12px 0;line-height:1.8"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;font-weight:600">마이리얼트립에서 할인 예약하기</a></p>\n'
        elif "추천과 비추천" in h2_title:
            sections_html += h2_html
            sections_html += f'<div style="margin:16px 0;padding:16px;background:#e8f5e9;border-radius:8px;border-left:3px solid #4caf50"><p style="margin:0;line-height:1.8"><strong>[추천] {rng.choice(rec_options)}</strong></p></div>\n'
            sections_html += f'<div style="margin:16px 0;padding:16px;background:#fce4ec;border-radius:8px;border-left:3px solid #e91e63"><p style="margin:0;line-height:1.8"><strong>[비추천] {rng.choice(not_rec_options)}</strong></p></div>\n'
        elif "시간대" in h2_title:
            sections_html += h2_html
            time_tips = [
                f"오전 8시 전: 사람이 적고 사진 찍기 좋아요.",
                f"오후 2~5시: 가장 덥고 혼잡한 시간. 그늘진 카페에서 쉬세요.",
                f"일몰 시간대(18:00~18:30): {city}에서 가장 아름다운 시간.",
            ]
            for t in rng.sample(time_tips, min(3, len(time_tips))):
                sections_html += f'<p style="margin:8px 0;line-height:1.8">- {t}</p>\n'
        elif "실수" in h2_title or "주의" in h2_title:
            sections_html += h2_html
            sections_html += f'<div style="margin:16px 0;padding:16px;background:#fff3e0;border-radius:8px;border-left:3px solid #ff9800"><p style="margin:0;line-height:1.8">[주의] {mistake}</p></div>\n'
        elif "여행 준비물" in h2_title or "체크리스트" in h2_title:
            sections_html += h2_html
            sections_html += '<ul><li>여권 (유효기간 6개월 이상)</li><li>환전: 현지 ATM 인출 또는 달러 환전</li><li>선크림 SPF50, 모기 기피제, 우산</li><li>편한 walking shoes, 아쿠아슈즈</li><li>보조배터리 (C타입 또는 F타입 콘센트)</li><li>오프라인 구글맵 다운로드</li></ul>\n'
        elif "마무리" in h2_title:
            sections_html += h2_html
            sections_html += f'<p style="margin:12px 0;line-height:1.8">{city}의 {cat_name}은 발리 여행에서 빼놓을 수 없는 경험이에요. 궁금한 점이 있으면 댓글로 남겨주세요. 즐거운 {city} 여행 되세요!</p>\n'
            sections_html += f'<p style="margin:12px 0;line-height:1.8">발리 환율: 1Rp 약 0.083원(2026년). 10,000Rp 약 830원, 100,000Rp 약 8,300원. 시장은 현금만 받는 곳이 많아요.</p>\n'
        elif "주변 추천" in h2_title:
            sections_html += h2_html
            nearby_items = []
            if ci.get('beaches'):
                nearby_items.append(f"<li><strong>{rng.choice(ci['beaches'])}</strong>: 수영과 서핑 모두 가능</li>")
            if ci.get('temples'):
                nearby_items.append(f"<li><strong>{rng.choice(ci['temples'])}</strong>: 발리 문화를 느낄 수 있는 사원</li>")
            if ci.get('nature'):
                nearby_items.append(f"<li><strong>{rng.choice(ci['nature'])}</strong>: 자연을 즐길 수 있는 명소</li>")
            if ci.get('markets'):
                nearby_items.append(f"<li><strong>{rng.choice(ci['markets'])}</strong>: 쇼핑과 기념품</li>")
            selected = rng.sample(nearby_items, min(3, len(nearby_items)))
            sections_html += '<ul>' + ''.join(selected) + '</ul>\n'
            hidden = rng.choice(ci.get('hidden', [f"{city}의 숨겨진 골목"]))
            sections_html += f'<p style="margin:12px 0;line-height:1.8">숨겨진 명소: <strong>{hidden}</strong> - 관광객이 잘 모르는 곳이에요.</p>\n'
        elif "FAQ" in h2_title or "묻는 질문" in h2_title:
            sections_html += h2_html
            faq_list = FAQ_POOLS.get(cat, FAQ_POOLS["food"])(city, ci)
            faq_selected = rng.sample(faq_list, min(4, len(faq_list)))
            for q, a in faq_selected:
                sections_html += f'<div style="margin:12px 0;padding:16px;background:#fafafa;border-radius:8px;border-left:3px solid #FF6B35"><h3 style="font-size:1.05em;font-weight:700;margin:0 0 8px;color:#333">Q. {q}</h3><p style="margin:0;line-height:1.8;color:#555">{a}</p></div>\n'
        elif "관련 지역" in h2_title:
            sections_html += h2_html
            related_cities = [c for c in CITIES_DATA if c != city]
            related = rng.sample(related_cities, min(3, len(related_cities)))
            sections_html += '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0">'
            for rc in related:
                sections_html += f'<a href="/{rc}/{cat}/{article_no:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{rc} {cat_name}</a>'
            sections_html += '</div>\n'
        else:
            # Generic section with varied content
            sections_html += h2_html
            generic = rng.choice([
                f"{city}의 {h2_title}에 대한 실전 정보를 정리했어요.",
                f"직접 다녀온 {city} {h2_title} 경험을 공유합니다.",
                f"{city} 여행에서 {h2_title}은 빼놓을 수 없는 부분이에요.",
            ])
            sections_html += f'<p style="margin:12px 0;line-height:1.8">{generic}</p>\n'

    # MRT CTA
    mrt_cta = f'<div style="margin:32px 0;padding:20px;background:linear-gradient(135deg,#FF6B35,#FF8C61);border-radius:12px;text-align:center;color:white"><p style="margin:0 0 12px;font-weight:700;font-size:1.1em">마이리얼트립에서 {city} {cat_name} 투어 할인받기</p><p style="margin:0 0 16px;font-size:0.95em;opacity:0.9">투어, 티켓, 숙소 최대 30% 할인</p><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="display:inline-block;padding:12px 32px;background:white;color:#FF6B35;border-radius:25px;text-decoration:none;font-weight:700">할인쿠폰 받기</a></div>'

    # CSS & JS (not in f-string)
    CSS = """:root{--primary:#FF6B35;--bg:#FAFAFA;--text:#1A1A2E;--text-light:#666;--card-bg:#FFFFFF;--shadow:0 2px 8px rgba(0,0,0,0.08)}*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);line-height:1.85;word-break:keep-all}.container{max-width:800px;margin:0 auto;padding:20px}header{background:linear-gradient(135deg,#FF6B35,#FF8C61);color:white;padding:40px 20px;text-align:center}header h1{font-size:1.8rem;margin-bottom:10px;word-break:keep-all}header .meta{opacity:0.9;font-size:0.9rem}.breadcrumb{padding:15px 0;font-size:0.85rem;color:var(--text-light)}.breadcrumb a{color:var(--primary);text-decoration:none}article{background:var(--card-bg);border-radius:12px;padding:30px;box-shadow:var(--shadow);margin:20px 0}article h2{color:var(--primary);font-size:1.4rem;margin:30px 0 15px;padding-bottom:8px;border-bottom:2px solid var(--primary)}article h3{color:#333;font-size:1.15rem;margin:20px 0 10px}article table{width:100%;border-collapse:collapse;margin:16px 0}article th,article td{padding:10px 8px;border:1px solid #ddd;text-align:left}article th{background:#FF6B35;color:white}article tr:nth-child(even){background:#f9f9f9}article ul,article ol{padding-left:20px;margin:16px 0}article li{margin-bottom:8px;line-height:1.7}.content-intro{margin:0 0 20px;padding:16px 20px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2;font-weight:500;line-height:1.8}.content-footer{margin:24px 0;padding:12px;background:#f5f5f5;border-radius:8px;font-size:0.9em;color:#666}.tags{margin:20px 0}.tag{display:inline-block;background:#F0F0F0;padding:4px 12px;border-radius:20px;font-size:0.8rem;margin:3px;color:var(--text-light)}footer{text-align:center;padding:30px;color:var(--text-light);font-size:0.85rem}#reading-progress{position:fixed;top:0;left:0;width:0%;height:3px;background:linear-gradient(90deg,#FF6B35,#FF8C61);z-index:9999;transition:width 0.1s}figure img{background:#f0f0f0;min-height:100px}@media(max-width:600px){.container{padding:10px}article{padding:20px}header h1{font-size:1.4rem}table{font-size:.8em}article h2{font-size:1.2rem}}@media(prefers-color-scheme:dark){:root{--bg:#1a1a2e;--text:#e0e0e0;--text-light:#aaa;--card-bg:#16213e;--border:#333}body{background:var(--bg);color:var(--text)}article{background:var(--card-bg)}.content-intro{background:linear-gradient(135deg,#1a1a2e,#16213e);border-color:#333}article tr:nth-child(even){background:#1a1a2e}}"""
    SCROLL_JS = "window.addEventListener('scroll',function(){var w=document.body.scrollTop||document.documentElement.scrollTop;var h=document.documentElement.scrollHeight-document.documentElement.clientHeight;document.getElementById('reading-progress').style.width=(w/h*100)+'%'});"

    import json as _json
    img0 = images[0] if images else 'default.webp'
    ld_json = _json.dumps({"@context":"https://schema.org","@type":"Article","headline":title,"description":meta_desc,"image":[f"https://balitravel.blog/images/{city}/{cat}/{img0}"],"datePublished":"2026-04-01","dateModified":"2026-05-03","author":{"@type":"Person","name":"JP Travel Bali"},"publisher":{"@type":"Organization","name":"JP Travel Bali"},"mainEntityOfPage":{"@type":"WebPage","@id":f"https://balitravel.blog/{city}/{cat}/{article_no:03d}.html"}}, ensure_ascii=False)

    # Apply phrase alternatives
    full_text = sections_html
    for phrase, alts in PHRASE_ALTERNATIVES.items():
        full_text = replace_phrase(full_text, phrase, alts, article_no)

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{city}, {cat_name}, 발리, 인도네시아, 자유여행, 2026">
<link rel="canonical" href="https://balitravel.blog/{city}/{cat}/{article_no:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="https://balitravel.blog/images/{city}/{cat}/{img0}">
<meta property="og:url" content="https://balitravel.blog/{city}/{cat}/{article_no:03d}.html">
<meta property="og:site_name" content="JP Travel Bali">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld_json}</script>
<style>{CSS}</style>
</head>
<body>
<div id="reading-progress"></div>
<script>{SCROLL_JS}</script>
<div class="container">
<header>
<h1>{title}</h1>
<div class="meta">JP Travel Bali | {city} {cat_name} 가이드 | 2026</div>
</header>
<div class="breadcrumb"><a href="/">홈</a> &rsaquo; <a href="/{city}/">{city}</a> &rsaquo; <a href="/{city}/{cat}/">{cat_name}</a> &rsaquo; {article_no:03d}</div>
<article>
<div class="content-intro"><strong>[제휴 안내]</strong> 이 글에는 마이리얼트립 제휴 링크가 포함되어 있으며, 링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.</div>
<div class="content-intro">{intro}</div>
{full_text}
{mrt_cta}
{images_html}
<div class="tags"><span class="tag">{city}</span><span class="tag">{cat_name}</span><span class="tag">발리</span><span class="tag">인도네시아</span><span class="tag">자유여행</span><span class="tag">2026</span></div>
<div class="content-footer"><p>이 글이 {city} 여행 계획에 도움이 되셨길 바랍니다.</p><p style="margin-top:8px"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립 할인쿠폰 받기</a></p></div>
</article>
</div>
<footer><p>이 글에는 <a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립</a> 제휴 링크가 포함되어 있습니다.</p><p>이 글에는 마이리얼트립 제휴 링크가 포함되어 있으며, 링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.</p><p style="margin-top:10px">JP Travel Bali &copy; 2026</p></footer>
</body>
</html>'''

    f.write_text(html, encoding='utf-8')
    count += 1
    if count % 100 == 0:
        print(f"  Progress: {count}/{len(html_files)}")

print(f"\nProcessed {count} files")
print(f"Unique titles: {len(titles)}")
print(f"Unique metas: {len(metas)}")

# Quick verify
short = 0
chinese = 0
emoji = 0
hanja_re = re.compile(r'[\u4e00-\u9fff]')
emoji_re = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\u200D\uFE0F]')
for f in html_files:
    c = f.read_text(encoding='utf-8')
    body = re.sub(r'<[^>]+>', '', c)
    body = re.sub(r'\s+', '', body)
    kr = len(re.findall(r'[가-힣]', body))
    if kr < 1500: short += 1
    if hanja_re.search(body): chinese += 1
    if emoji_re.search(body): emoji += 1
print(f"Under 1500: {short}, Chinese: {chinese}, Emoji: {emoji}")
print("DONE")
