#!/usr/bin/env python3
"""
924개 HTML 전면 개선 스크립트
- 각 글 고유 도입부
- 도시별 맞춤 팁
- 카테고리별 전문 정보
- 중복 제거
- 품질 향상
"""

import os, re, random, json
from pathlib import Path

BASE = Path(__file__).parent / "output" / "html" / "bali"

# ============================================================
# 도시별 고유 데이터 (12개 도시)
# ============================================================
CITIES = {
    "꾸따": {
        "vibe": "활기찬 해변 도시",
        "best_for": "서핑 초보자, 파티, 쇼핑",
        "avoid_if": "조용한 휴식을 원한다면",
        "best_time": "일몰 시간대 (18:00~18:30)",
        "budget": "1일 720,000Rp (약 6만원)",
        "transport": "공항에서 10분, 그랩 100,000Rp",
        "food_highlight": "비치 로드 뒷골목 워룽의 나시 캄푸르 20,000Rp",
        "hidden_spot": "Poppies Lane의 로컬 바",
        "local_tip": "비치 로드에서 2블록만 들어가면 가격이 절반",
        "weather": "건기(4~10월) 최적, 우기에도 오후 스콜 후 그침",
        "exchange": "비치 로드 공식 환전소 이용. 길거리 환전소 사기 주의",
        "food_tip": "나시 캄푸르(혼합 밥) 20,000Rp면 배불리 먹을 수 있어요",
        "hours": "워룽 보통 오전 8시~밤 10시. 비치 로드는 밤늦게까지",
    },
    "우붓": {
        "vibe": "영적·예술적 중심지",
        "best_for": "문화 체험, 요가, 유기농 음식",
        "avoid_if": "나이트라이프를 원한다면",
        "best_time": "오전 9시 전 (라이스 테라스 방문)",
        "budget": "1일 500,000Rp (약 4.2만원)",
        "transport": "공항에서 1.5시간, 그랩 200,000Rp",
        "food_highlight": "로카보어 파인 다이닝 코스 1,200,000Rp",
        "hidden_spot": "Jatiluwih 라이스 테라스 (UNESCO)",
        "local_tip": "테갈랑보다 Jatiluwih가 10배 더 진짜",
        "weather": "고산지대라 해안보다 2~3도 낮음",
        "exchange": "ATM 있지만 시골이라 카드 결제 안 되는 곳 많음",
        "food_tip": "유기농 카페가 많아요. 클리어 카페나 세이드 추천",
        "hours": "마켓 새벽 5시부터. 오전에 신선한 과일 구매 가능",
    },
    "스미냑": {
        "vibe": "세련된 비치 클럽 도시",
        "best_for": "파인 다이닝, 비치 클럽, 부티크 쇼핑",
        "avoid_if": "예산이 빠듯하다면",
        "best_time": "선셋 시간대 (17:30~18:30)",
        "budget": "1일 1,500,000Rp (약 12.5만원)",
        "transport": "공항에서 30분, 그랩 150,000Rp",
        "food_highlight": "사롱 레스토랑 아시안 퓨전 2인 800,000Rp",
        "hidden_spot": "Jalan Kayu Aya 뒷골목 로컬 워룽",
        "local_tip": "Eat Street에서 1블록만 들어가면 가격 절반",
        "weather": "건기에 비치 클럽 최적",
        "exchange": "대부분 카드 결제 가능. 팁은 현금으로",
        "food_tip": "Jalan Kayu Aya(먹자골목)에 다양한 세계 음식",
        "hours": "레스토랑 오전 10시~밤 11시. 비치 클럽 예약 필수",
    },
    "사누르": {
        "vibe": "조용한 가족 해변 도시",
        "best_for": "가족 여행, 자전거, 아침 산책",
        "avoid_if": "나이트라이프를 원한다면",
        "best_time": "오전 6시 (해변 산책)",
        "budget": "1일 600,000Rp (약 5만원)",
        "transport": "공항에서 30분, 그랩 150,000Rp",
        "food_highlight": "신두 야시장 나시 고랭 15,000Rp",
        "hidden_spot": "워룽 마크벵 생선 튀김 (아침 7시 오픈)",
        "local_tip": "해변 산책로 5km 자전거 코스",
        "weather": "리프 보호로 우기에도 해변 이용 가능",
        "exchange": "환전소 적음. 미리 꾸따에서 환전",
        "food_tip": "신두 야시장 나시 고랭 15,000Rp. 현지인 맛집",
        "hours": "해변 산책로 24시간. 워룽 오전 7시~",
    },
    "누사두아": {
        "vibe": "5성급 리조트 단지",
        "best_for": "럭셔리 휴가, 신혼여행, 가족 리조트",
        "avoid_if": "배낭여행, 예산 여행",
        "best_time": "리조트 수영장 오전 시간",
        "budget": "1일 3,000,000Rp (약 25만원)",
        "transport": "공항에서 30분, 그랩 200,000Rp",
        "food_highlight": "리조트 뷔페 300,000~800,000Rp",
        "hidden_spot": "BTDC 단지 밖 로컬 워룽",
        "local_tip": "단지 밖으로 나가면 같은 음식 절반 가격",
        "weather": "리조트 수영장은 우기에도 OK",
        "exchange": "리조트에서 카드 결제 가능",
        "food_tip": "리조트 뷔페 비싸지만 품질 좋음",
        "hours": "리조트 레스토랑 오전 6시~자정",
    },
    "울루와뚜": {
        "vibe": "절벽 위 서핑·사원 도시",
        "best_for": "중급 서핑, 케akış 불춤, 절경",
        "avoid_if": "초보 서핑, 이동 불편 싫다면",
        "best_time": "케akış 공연 시간 (18:00)",
        "budget": "1일 800,000Rp (약 6.7만원)",
        "transport": "공항에서 40분, 전용차 600,000Rp/일",
        "food_highlight": "절벽 아래 워룽 나시 고랭 25,000Rp",
        "hidden_spot": "Bingin Beach 절벽 아래 비밀 워룽",
        "local_tip": "절벽 도로 야간 운전 위험. 교통편 확보 필수",
        "weather": "절벽 위 바람 매우 강함",
        "exchange": "ATM 없을 수 있음. 현금 충분히 준비",
        "food_tip": "절벽 아래 워룽에서 인도양 전망 나시 고랭",
        "hours": "워룽 오전 9시~. 서핑 후 방문 추천",
    },
    "덴파사르": {
        "vibe": "발리 수도, 로컬 도시",
        "best_for": "전통시장, 로컬 음식, 박물관",
        "avoid_if": "해변, 리조트를 원한다면",
        "best_time": "새벽 5~7시 (시장 방문)",
        "budget": "1일 400,000Rp (약 3.3만원)",
        "transport": "공항에서 15분, 그랩 50,000Rp",
        "food_highlight": "파사르 바둥 2층 바비 꿀링 25,000Rp",
        "hidden_spot": "케레넹 야시장",
        "local_tip": "시장은 새벽이 가장 활기참",
        "weather": "도시 열섬 효과로 해안보다 1~2도 더움",
        "exchange": "환전소 가장 많음. 공식 환전소 이용",
        "food_tip": "파사르 바둥 2층 바비 꿀링 25,000Rp",
        "hours": "시장 새벽 5시~오후 5시",
    },
    "베두굴": {
        "vibe": "산속 호수 도시",
        "best_for": "사원 방문, 식물원, 딸기 농장",
        "avoid_if": "해변, 나이트라이프를 원한다면",
        "best_time": "오전 (안개 없을 때)",
        "budget": "1일 500,000Rp (약 4.2만원)",
        "transport": "우붓에서 1.5시간, 전용차 500,000Rp",
        "food_highlight": "캔디쿠닝 마켓 딸기 주스 10,000Rp",
        "hidden_spot": "발리 식물원 (입장료 20,000Rp)",
        "local_tip": "밤에는 매우 춥다. 얇은 겉옷 필수",
        "weather": "고산지대 15~22도. 항상 서늘",
        "exchange": "환전소 없음. 미리 환전",
        "food_tip": "캔디쿠닝 마켓 딸기 주스 10,000Rp",
        "hours": "워룽 오전 8시~오후 5시",
    },
    "타바난": {
        "vibe": "논밭 농촌 지역",
        "best_for": "라이스 테라스, 자전거, 사진",
        "avoid_if": "나이트라이프, 쇼핑을 원한다면",
        "best_time": "우기(11~3월) 벼 가장 푸를 때",
        "budget": "1일 350,000Rp (약 2.9만원)",
        "transport": "우붓에서 1시간, 스쿠터 70,000Rp/일",
        "food_highlight": "마을 워룽 나시 캄푸르 15,000Rp",
        "hidden_spot": "Jatiluwih UNESCO 라이스 테라스",
        "local_tip": "메인 도로보다 마을 안쪽이 더 진짜",
        "weather": "우기에는 논이 가장 푸름",
        "exchange": "환전소 없음. 우붓에서 미리 환전",
        "food_tip": "농부가 직접 만든 나시 캄푸르 15,000Rp",
        "hours": "워룽 오전 7시~오후 5시",
    },
    "로비나": {
        "vibe": "조용한 북부 해안",
        "best_for": "돌고래 투어, 스노클링, 조용한 휴식",
        "avoid_if": "쇼핑, 나이트라이프를 원한다면",
        "best_time": "새벽 6시 (돌고래 투어)",
        "budget": "1일 400,000Rp (약 3.3만원)",
        "transport": "공항에서 3시간, 전용차 500,000Rp",
        "food_highlight": "해변 생선구이 30,000Rp",
        "hidden_spot": "반자르 온천 (무료)",
        "local_tip": "1박 이상 추천. 당일치기 너무 멀다",
        "weather": "동부 해안이라 우기 영향 적음",
        "exchange": "환전소 적음. 싱가라자에서 미리 환전",
        "food_tip": "해변에서 신선한 생선구이 30,000Rp",
        "hours": "워룽 오전 7시~오후 8시",
    },
    "킨타마니": {
        "vibe": "화산 전망 고산 지역",
        "best_for": "화산 트레킹, 일출, 온천",
        "avoid_if": "쇼핑, 해변을 원한다면",
        "best_time": "새벽 2시 (일출 트레킹 출발)",
        "budget": "1일 600,000Rp (약 5만원)",
        "transport": "우붓에서 2시간, 전용차 400,000Rp",
        "food_highlight": "뷔페 레스토랑 화산 전망 식사",
        "hidden_spot": "뜨갈랄랑 온천",
        "local_tip": "새벽 출발 필수. 오전에 안개 끼면 화산 안 보임",
        "weather": "고산지대 매우 추움. 두꺼운 겉옷 필수",
        "exchange": "환전소 없음. 우붓에서 미리 환전",
        "food_tip": "뷔페에서 바투르 화산 전망 보며 식사",
        "hours": "레스토랑 오전 10시~오후 5시",
    },
    "타나롯": {
        "vibe": "해양 사원 도시",
        "best_for": "사원 방문, 일몰 사진, 문화 체험",
        "avoid_if": "장기 체류를 원한다면",
        "best_time": "일몰 시간대 (17:30~18:30)",
        "budget": "1일 500,000Rp (약 4.2만원)",
        "transport": "공항에서 90분, 그랩 250,000Rp",
        "food_highlight": "사원 근처 발리 커피와 전통 과자",
        "hidden_spot": "근처 바투 볼롱 사원 (한적)",
        "local_tip": "조수 시간 확인. 만조 때 사원이 섬처럼 보임",
        "weather": "해안가라 바람 항상 붐",
        "exchange": "환전소 있음. 관광지라 가격 비쌈",
        "food_tip": "사원 근처 발리 커피와 전통 과자",
        "hours": "사원 오전 7시~오후 5시",
    },
    "짠디다사": {
        "vibe": "동부 해안 조용한 휴양지",
        "best_for": "다이빙, 스노클링, 조용한 휴식",
        "avoid_if": "쇼핑, 나이트라이프를 원한다면",
        "best_time": "오전 (다이빙 visibility 좋을 때)",
        "budget": "1일 500,000Rp (약 4.2만원)",
        "transport": "공항에서 2시간, 전용차 400,000Rp",
        "food_highlight": "해변 레스토랑 신선한 해산물",
        "hidden_spot": "블루 라군 비치 (스노클링)",
        "local_tip": "1박 이상 추천. 다이빙 투어 포함",
        "weather": "동부 해안이라 우기 영향 적음",
        "exchange": "환전소 적음. 미리 환전",
        "food_tip": "해변 레스토랑 신선한 해산물",
        "hours": "워룽 오전 7시~오후 8시",
    },
}

# ============================================================
# 카테고리별 전문 팁
# ============================================================
CATEGORY_TIPS = {
    "food": {
        "general": "발리 음식은 향신료가 강해요. 처음엔 덜 맵게 주문하세요.",
        "budget": "로컬 워룽 20,000~40,000Rp, 레스토랑 80,000~200,000Rp",
        "safety": "현지인이 많이 찾는 곳이 가장 안전해요.",
        "must_know": "'Tidak pedas'(안 맵게), 'Tanpa gula'(설탕 없이) 표현 알아두면 편해요.",
    },
    "beach": {
        "general": "자외선이 매우 강해요. 선크림 필수.",
        "budget": "선베드 50,000~100,000Rp, 음료 25,000~50,000Rp",
        "safety": "파도가 강한 날에는 수영하지 마세요.",
        "must_know": "만조 시간을 미리 확인하세요.",
    },
    "culture": {
        "general": "사원 방문 시 긴 바지와 스카프 필수.",
        "budget": "입장료 20,000~100,000Rp, 기부금 10,000~20,000Rp",
        "safety": "사원 내에서는 조용히 해주세요.",
        "must_know": "사원 앞에서 기도하는 사람을 방해하지 마세요.",
    },
    "nature": {
        "general": "편한 신발 필수. 미끄러울 수 있어요.",
        "budget": "입장료 20,000~100,000Rp, 가이드 200,000~500,000Rp",
        "safety": "우기에는 트레킹 코스가 미끄러워요.",
        "must_know": "충분한 물과 간식을 준비하세요.",
    },
    "shopping": {
        "general": "첫 가격의 30~50%에서 흥정 시작하세요.",
        "budget": "기념품 10,000~100,000Rp, 의류 50,000~300,000Rp",
        "safety": "가짜 브랜드 제품 주의.",
        "must_know": "시장은 오전에 가야 좋은 가격.",
    },
    "transport": {
        "general": "그랩이 택시보다 저렴하고 안전해요.",
        "budget": "시내 이동 15,000~50,000Rp, 공항 이동 100,000~500,000Rp",
        "safety": "스쿠터 렌탈 시 국제면허 필수.",
        "must_know": "러시아워(17~19시) 이동 피하세요.",
    },
}

def get_city_name_from_path(filepath):
    """파일 경로에서 도시명 추출"""
    parts = filepath.parts
    for part in parts:
        if part in CITIES:
            return part
    return None

def get_category_from_path(filepath):
    """파일 경로에서 카테고리 추출"""
    parts = filepath.parts
    for part in parts:
        if part in CATEGORY_TIPS:
            return part
    return None

def get_article_number(filepath):
    """파일 경로에서 아티클 번호 추출"""
    name = filepath.stem
    if name.isdigit():
        return int(name)
    return 0

def generate_unique_intro(city, category, article_num):
    """도시+카테고리+번호별 고유 도입부 생성"""
    city_info = CITIES[city]
    cat_info = CATEGORY_TIPS[category]
    rng = random.Random(hash(f"{city}_{category}_{article_num}"))
    
    templates = [
        f"{city}의 {category} 정보를 찾다가 직접 가보니, 검색해서 알게 된 것과 실제가 좀 달랐어요. {city_info['food_highlight']}부터 시작해서 솔직하게 장단점 다 쓸게요.",
        f"{city} {category} 계획 중이신가요? 저도 같은 고민했거든요. 직접 가본 결과, {city_info['hidden_spot']}부터 시작하는 코스가 가장 효율적이었어요.",
        f"결론부터 말하면, {city}의 {category}은 {city_info['best_time']}이 가장 좋아요. {city_info['food_highlight']} 추천이고, {city_info['hidden_spot']}도 놓치지 마시고요.",
        f"{city} {category} 핵심만 추리면: 1) {city_info['food_highlight']} 2) {city_info['hidden_spot']}. 이 두 가지만 기억하세요.",
        f"'{city} {category} 어디가 좋나요?' 저도 출발 전에 같은 질문을 했어요. 막상 가보니 {city_info['vibe']} 분위기가 정말 다르더라고요.",
        f"{city}에 도착한 첫째 날, {category} 계획을 짰어요. {city_info['best_time']}에 {city_info['hidden_spot']} 방문이 가장 좋았어요.",
        f"{city}에서 보낸 시간 중 가장 좋았던 건 {category}이었어요. {city_info['best_time']}에 도착했을 때의 그 분위기가 아직도 기억나요.",
        f"{city} {category} 완벽 가이드입니다. 직접 가본 기준으로 정리했어요. {city_info['food_highlight']} 추천부터 {city_info['hidden_spot']} 후기까지 다뤘어요.",
    ]
    
    return rng.choice(templates)

def generate_city_specific_tip(city, category):
    """도시별 맞춤 팁 생성"""
    city_info = CITIES[city]
    cat_info = CATEGORY_TIPS[category]
    
    tips = []
    tips.append(f"💡 {city} 팁: {city_info['local_tip']}")
    tips.append(f"💰 예산: {city_info['budget']}")
    tips.append(f"🚗 교통: {city_info['transport']}")
    tips.append(f"🌤️ 날씨: {city_info['weather']}")
    
    return tips

def improve_html_file(filepath):
    """단일 HTML 파일 개선"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    city = get_city_name_from_path(filepath)
    category = get_category_from_path(filepath)
    article_num = get_article_number(filepath)
    
    if not city or not category:
        return False
    
    city_info = CITIES[city]
    cat_info = CATEGORY_TIPS[category]
    modified = False
    
    # 1. 고유 도입부 생성 (기존 도입부가 템플릿인 경우)
    if "직접 가보고 느낀 점을 솔직하게" in content:
        new_intro = generate_unique_intro(city, category, article_num)
        old_intro_pattern = r'<div class="content-intro">.*?직접 가보고 느낀 점을 솔직하게 공유합니다.*?</div>'
        if re.search(old_intro_pattern, content, re.DOTALL):
            content = re.sub(old_intro_pattern, f'<div class="content-intro">{new_intro}</div>', content, count=1, flags=re.DOTALL)
            modified = True
    
    # 2. 도시별 맞춤 팁 추가 (마무리 정리 섹션 앞)
    if "마무리 정리" in content and city_info["local_tip"]:
        tips = generate_city_specific_tip(city, category)
        tips_html = "\n".join([f'<p style="margin:8px 0;line-height:1.8">{tip}</p>' for tip in tips])
        
        # 마무리 정리 H2 앞에 팁 추가
        if f'💡 {city} 팁' not in content:
            content = content.replace(
                '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">마무리 정리</h2>',
                f'\n{tips_html}\n<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">마무리 정리</h2>'
            )
            modified = True
    
    # 3. 카테고리별 전문 팁 추가
    if cat_info["must_know"] and cat_info["must_know"] not in content:
        # 핵심 정보 섹션 끝에 추가
        must_know_html = f'<p style="margin:12px 0;line-height:1.8;background:#fff3e0;padding:12px;border-radius:8px;border-left:3px solid #ff9800"><strong>꼭 알아두세요:</strong> {cat_info["must_know"]}</p>'
        
        # 핵심 정보 H2 다음에 추가
        if "핵심 정보" in content and "꼭 알아두세요" not in content:
            content = content.replace(
                '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">핵심 정보</h2>',
                f'<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">핵심 정보</h2>\n{must_know_html}'
            )
            modified = True
    
    # 4. 도시별 숨겨진 장소 강조
    if city_info["hidden_spot"] and city_info["hidden_spot"] not in content:
        hidden_html = f'<div style="margin:16px 0;padding:16px;background:#e3f2fd;border-radius:8px;border-left:3px solid #2196f3"><p style="margin:0;line-height:1.8"><strong>🔍 숨겨진 장소:</strong> {city_info["hidden_spot"]} — {city_info["local_tip"]}</p></div>'
        
        # 주변 추천 명소 앞에 추가
        if "주변 추천 명소" in content and "숨겨진 장소" not in content:
            content = content.replace(
                '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">주변 추천 명소</h2>',
                f'{hidden_html}\n<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">주변 추천 명소</h2>'
            )
            modified = True
    
    # 5. 중복 제휴 안내 문장 정리 (한 번만 표시)
    affiliate_count = content.count("마이리얼트립 제휴 링크가 포함되어 있으며")
    if affiliate_count > 1:
        # 첫 번째만 남기고 나머지 제거
        first_found = False
        def replace_affiliate(match):
            nonlocal first_found
            if not first_found:
                first_found = True
                return match.group(0)
            return ""
        content = re.sub(
            r'<p>이 글에는 마이리얼트립 제휴 링크가 포함되어 있으며.*?</p>',
            replace_affiliate,
            content
        )
        modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """메인 실행"""
    print("=== 924개 HTML 전면 개선 시작 ===\n")
    
    html_files = list(BASE.rglob("*.html"))
    print(f"총 HTML 파일: {len(html_files)}개\n")
    
    improved = 0
    for i, filepath in enumerate(html_files):
        if improve_html_file(filepath):
            improved += 1
        if (i + 1) % 100 == 0:
            print(f"  진행: {i+1}/{len(html_files)} 처리 완료...")
    
    print(f"\n✅ 개선 완료: {improved}/{len(html_files)}개 파일")
    
    # 검증
    print("\n=== 개선 후 검증 ===")
    checks = {
        "도시별 고유 팁 포함": 0,
        "카테고리 전문 팁 포함": 0,
        "숨겨진 장소 포함": 0,
        "중복 제휴 정리": 0,
    }
    
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        city = get_city_name_from_path(filepath)
        if city and f"💡 {city} 팁" in content:
            checks["도시별 고유 팁 포함"] += 1
        if "꼭 알아두세요" in content:
            checks["카테고리 전문 팁 포함"] += 1
        if "숨겨진 장소" in content:
            checks["숨겨진 장소 포함"] += 1
    
    for key, count in checks.items():
        print(f"  {key}: {count}/{len(html_files)}")

if __name__ == "__main__":
    main()
