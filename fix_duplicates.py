#!/usr/bin/env python3
"""
924개 HTML 파일의 중복 템플릿 문장을 고유 콘텐츠로 교체
Google Helpful Content Update 대응
"""

import os, re, random
from pathlib import Path

BASE = Path(__file__).parent / "output" / "html" / "bali"

# 도시별 고유 데이터
CITY_DATA = {
    "꾸따": {
        "exchange": "꾸따는 관광객이 많아서 환전소가 많아요. 비치 로드의 공식 환전소를 이용하세요. 길거리 환전소는 사기 위험이 있어요.",
        "food_tip": "꾸따의 로컬 워룽에서는 나시 캄푸르(혼합 밥)를 추천해요. 20,000Rp면 배불리 먹을 수 있어요.",
        "peanut": "꾸따 레스토랑은 외국인이 많아서 영어 메뉴가 대부분 있어요. 하지만 알레르기가 있다면 'Alergi kacang'(땅콩 알레르기)이라고 미리 말하세요.",
        "spice": "꾸따 음식은 관광객 입맛에 맞게 조절해주는 곳이 많아요. 'Tidak pedas'(안 맵게)라고 하면 맞춰줘요.",
        "hours": "꾸따 워룽은 보통 오전 8시에 열어서 밤 10시까지 영업해요. 비치 로드 근처는 밤늦게까지 하는 곳도 있어요.",
    },
    "우붓": {
        "exchange": "우붓에는 ATM이 있지만 시골 지역이라 카드 결제가 안 되는 곳이 많아요. 현금을 충분히 환전해가세요.",
        "food_tip": "우붓은 유기농 카페가 많아요. 클리어 카페나 세이드에서 건강식을 즐길 수 있어요.",
        "peanut": "우붓의 전통 발리 음식은 땅콩 소스가 많이 들어가요. 알레르기가 있다면 'Alergi kacang'이라고 말하세요.",
        "spice": "우붓 음식은 전통적이라 향신료가 강해요. 'Tidak pedas'(안 맵게)라고 하면_Adjust 해줘요.",
        "hours": "우붓 마켓은 새벽 5시부터 열어요. 오전에 가면 신선한 과일과 전통 과자를 살 수 있어요.",
    },
    "스미냑": {
        "exchange": "스미냑은 고급 지역이라 대부분 카드 결제가 돼요. 하지만 팁은 현금으로 준비하세요.",
        "food_tip": "스미냑의 Jalan Kayu Aya(먹자골목)에는 다양한 세계 음식이 있어요. 이탈리안, 일본식, 멕시칸까지.",
        "peanut": "스미냑 레스토랑은 영어 메뉴와 알레르기 표시가 잘 되어 있어요. 그래도 'Alergi kacang'이라고 말하면 확실해요.",
        "spice": "스미냑 음식은 인터내셔널이라 향신료가 조절돼요. 'No spicy'라고 해도 통해요.",
        "hours": "스미냑 레스토랑은 보통 오전 10시에 열어서 밤 11시까지 영업해요. 비치 클럽은 예약 필수.",
    },
    "사누르": {
        "exchange": "사누르는 조용한 지역이라 환전소가 적어요. 미리 꾸따나 덴파사르에서 환전하세요.",
        "food_tip": "사누르의 신두 야시장에서 나시 고랭을 15,000Rp에 먹을 수 있어요. 현지인들이 많이 찾는 곳이에요.",
        "peanut": "사누르 워룽은 로컬이라 영어가 안 통할 수 있어요. 알레르기 카드를 인쇄해가면 편해요.",
        "spice": "사누르 음식은 전통 발리 스타일이라 매워요. 'Tidak pedas'라고 하면 덜 맵게 해줘요.",
        "hours": "사누르 해변은 오전 6시부터 산책할 수 있어요. 워룽은 오전 7시에 열어요.",
    },
    "누사두아": {
        "exchange": "누사두아는 리조트 지역이라 대부분 카드 결제가 돼요. 팁은 현금으로.",
        "food_tip": "누사두아 리조트 뷔페는 비싸지만 품질이 좋아요. 단지 밖으로 나가면 절반 가격.",
        "peanut": "누사두아 리조트 레스토랑은 알레르기 표시가 철저해요. 안심하고 주문하세요.",
        "spice": "누사두아 음식은 인터내셔널이라 향신료가 약해요. 걱정 마세요.",
        "hours": "누사두아 리조트 레스토랑은 오전 6시~자정까지 영업해요.",
    },
    "울루와뚜": {
        "exchange": "울루와뚜는 시골 지역이라 ATM이 없을 수 있어요. 현금을 충분히 준비하세요.",
        "food_tip": "울루와뚜 절벽 아래 warung에서 나시 고랭을 25,000Rp에 먹을 수 있어요. 인도양 전망이 무료.",
        "peanut": "울루와뚜 워룽은 로컬이에요. 알레르기 카드를 보여주세요.",
        "spice": "울루와뚜 음식은 전통적이라 매워요. 'Tidak pedas'라고 하면_Adjust 해줘요.",
        "hours": "울루와뚜 워룽은 오전 9시에 열어요. 서핑 후에 가기 좋아요.",
    },
    "덴파사르": {
        "exchange": "덴파사르는 발리 수도라 환전소가 가장 많아요. 공식 환전소를 이용하세요.",
        "food_tip": "덴파사르 파사르 바둥 2층에서 바비 꿀링을 25,000Rp에 먹을 수 있어요.",
        "peanut": "덴파사르 시장 음식은 영어 표시가 없어요. 알레르기 카드를 준비하세요.",
        "spice": "덴파사르 음식은 가장 전통적이에요. 향신료가very 강할 수 있어요.",
        "hours": "덴파사르 시장은 새벽 5시부터 열어요. 오전이 가장 활기차요.",
    },
    "베두굴": {
        "exchange": "베두굴은 산속이라 환전소가 없어요. 미리 환전하세요.",
        "food_tip": "베두굴 캔디쿠닝 마켓에서 신선한 딸기 주스를 10,000Rp에 마실 수 있어요.",
        "peanut": "베두굴 워룽은very 로컬이에요. 알레르기 카드를 준비하세요.",
        "spice": "베두굴 음식은 산속 스타일이라 덜 매워요.",
        "hours": "베두굴 워룽은 오전 8시에 열어요. 오후 5시면 닫는 곳이 많아요.",
    },
    "타바난": {
        "exchange": "타바난은 농촌 지역이라 환전소가 없어요. 우붓에서 미리 환전하세요.",
        "food_tip": "타바난 마을 warung에서 농부가 직접 만든 나시 캄푸르를 15,000Rp에 먹을 수 있어요.",
        "peanut": "타바난 음식은 전통 발리 가정식이에요. 알레르기 카드를 보여주세요.",
        "spice": "타바난 음식은 가정식이라 향신료가 조절돼요.",
        "hours": "타바난 워룽은 오전 7시에 열어요. 농부들이 아침 식사하러 와요.",
    },
    "로비나": {
        "exchange": "로비나는 북부 해안이라 환전소가 적어요. 싱가라자에서 미리 환전하세요.",
        "food_tip": "로비나 해변에서 신선한 생선구이를 30,000Rp에 먹을 수 있어요.",
        "peanut": "로비나 워룽은very 로컬이에요. 알레르기 카드를 준비하세요.",
        "spice": "로비나 음식은 북부 스타일이라 덜 매워요.",
        "hours": "로비나 워룽은 오전 7시에 열어요. 새벽에 생선을 잡아와서 신선해요.",
    },
    "킨타마니": {
        "exchange": "킨타마니는 화산 지역이라 환전소가 없어요. 우붓에서 미리 환전하세요.",
        "food_tip": "킨타마니 뷔페 레스토랑에서 바투르 화산 전망을 보며 식사할 수 있어요.",
        "peanut": "킨타마니 레스토랑은 관광객 대상이라 알레르기 표시가 있어요.",
        "spice": "킨타마니 음식은 뷔페 스타일이라 향신료가 약해요.",
        "hours": "킨타마니 레스토랑은 오전 10시에 열어요. 일출 보고 아침 식사하기 좋아요.",
    },
    "타나롯": {
        "exchange": "타나롯은 관광지라 환전소가 있어요. 하지만 가격이 비쌀 수 있어요.",
        "food_tip": "타나롯 사원 근처에서 발리 커피와 전통 과자를 즐길 수 있어요.",
        "peanut": "타나롯 레스토랑은 관광객 대상이라 영어 메뉴가 있어요.",
        "spice": "타나롯 음식은 관광객 입맛에 맞게 조절돼요.",
        "hours": "타나롯 사원은 오전 7시에 열어요. 오후 5시까지 관람 가능.",
    },
    "짠디다사": {
        "exchange": "짠디다사는 동부 해안이라 환전소가 적어요. 칸디다사에서 미리 환전하세요.",
        "food_tip": "짠디다사 해변 레스토랑에서 신선한 해산물을 즐길 수 있어요.",
        "peanut": "짠디다사 워룽은 로컬이에요. 알레르기 카드를 준비하세요.",
        "spice": "짠디다사 음식은 전통 발리 스타일이에요. 'Tidak pedas'라고 하면 덜 맵게 해줘요.",
        "hours": "짠디다사 워룽은 오전 7시에 열어요. 해변 레스토랑은 오후까지 영업해요.",
    },
}

# 카테고리별 고유 데이터
CATEGORY_DATA = {
    "food": {
        "peanut_key": "peanut",
        "spice_key": "spice",
        "hours_key": "hours",
    },
    "beach": {
        "peanut_key": None,
        "spice_key": None,
        "hours_key": "hours",
    },
    "culture": {
        "peanut_key": None,
        "spice_key": None,
        "hours_key": "hours",
    },
    "nature": {
        "peanut_key": None,
        "spice_key": None,
        "hours_key": "hours",
    },
    "shopping": {
        "peanut_key": None,
        "spice_key": None,
        "hours_key": "hours",
    },
    "transport": {
        "peanut_key": None,
        "spice_key": None,
        "hours_key": None,
    },
}

def fix_file(filepath):
    """단일 HTML 파일의 중복 문장을 수정"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 도시와 카테고리 추출
    parts = filepath.parts
    city = None
    category = None
    for part in parts:
        if part in CITY_DATA:
            city = part
        if part in CATEGORY_DATA:
            category = part
    
    if not city or not category:
        return False
    
    city_info = CITY_DATA[city]
    cat_info = CATEGORY_DATA[category]
    modified = False
    
    # 1. 환율 문장 → 도시별 고유 환율 정보
    old_exchange = r'발리 환율은 1Rp 약 0\.083원.*?환전해가세요\.'
    new_exchange = city_info["exchange"]
    if re.search(old_exchange, content, re.DOTALL):
        content = re.sub(old_exchange, new_exchange, content, count=1, flags=re.DOTALL)
        modified = True
    
    # 2. 땅콩 알레르기 문장 → 도시별 고유 (food 카테고리만)
    if cat_info["peanut_key"]:
        old_peanut = r'발리 음식의 특징은 향신료가 강하다.*?Alergi kacang.*?돼요\.'
        new_peanut = city_info[cat_info["peanut_key"]]
        if re.search(old_peanut, content, re.DOTALL):
            content = re.sub(old_peanut, new_peanut, content, count=1, flags=re.DOTALL)
            modified = True
    
    # 3. Tidak pedas 문장 → 도시별 고유 (food 카테고리만)
    if cat_info["spice_key"]:
        old_spice = r'현지 음식을 주문할 때 알아두면 좋은.*?Tidak pedas.*?대해줘요\.'
        new_spice = city_info[cat_info["spice_key"]]
        if re.search(old_spice, content, re.DOTALL):
            content = re.sub(old_spice, new_spice, content, count=1, flags=re.DOTALL)
            modified = True
    
    # 4. 오전 7시 문장 → 도시별 고유
    if cat_info["hours_key"]:
        old_hours = r'발리의 워룽은 보통 오전 7시에 열어서.*?식사할 수 있어요\.'
        new_hours = city_info[cat_info["hours_key"]]
        if re.search(old_hours, content, re.DOTALL):
            content = re.sub(old_hours, new_hours, content, count=1, flags=re.DOTALL)
            modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """메인 실행"""
    print("=== 924개 HTML 중복 문장 수정 시작 ===\n")
    
    html_files = list(BASE.rglob("*.html"))
    print(f"총 HTML 파일: {len(html_files)}개\n")
    
    fixed = 0
    for filepath in html_files:
        if fix_file(filepath):
            fixed += 1
    
    print(f"\n✅ 수정 완료: {fixed}/{len(html_files)}개 파일")
    
    # 검증
    print("\n=== 수정 후 검증 ===")
    remaining = {"환율": 0, "땅콩": 0, "Tidak pedas": 0, "0.083원": 0}
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for key in remaining:
            if key in content:
                remaining[key] += 1
    
    for key, count in remaining.items():
        status = "✅" if count == 0 else "🔴"
        print(f"  {status} '{key}': {count}/924 파일")

if __name__ == "__main__":
    main()
