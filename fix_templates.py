#!/usr/bin/env python3
"""
중복 템플릿 문장을 도시별 고유 내용으로 교체
"""

import os, re
from pathlib import Path

BASE = Path(__file__).parent / "output" / "html" / "bali"

# 도시별 고유 음식 팁 (Tidak pedas 대체)
FOOD_TIPS = {
    "꾸따": "꾸따의 로컬 워룽에서는 나시 캄푸르를 주문할 때 'Nasi Campur satu'라고 하면 됩니다. 한 접에 20,000Rp 정도.",
    "우붓": "우붓의 유기농 카페에서는 채식 메뉴가 다양합니다. 'Vegetarian'이라고 말하면 맞춰줘요.",
    "스미냑": "스미냑 레스토랑은 예약이 필수입니다. 'Mau reservasi'라고 하면 예약할 수 있어요.",
    "사누르": "사누르의 신두 야시장에서는 바비 꼬치를 'Sate satu'라고 주문하세요. 10개에 15,000Rp.",
    "누사두아": "누사두아 리조트 레스토랑은 대부분 영어 메뉴가 있습니다. 알레르기는 'Alergi'라고 말하세요.",
    "울루와뚜": "울루와뚜 절벽 아래 warung에서는 현금만 가능합니다. 충분히 환전해가세요.",
    "짠디다사": "짠디다사의 해변 warung에서는 신선한 생선을 'Ikan bakar satu'라고 주문하세요.",
    "로비나": "로비나의 해변 레스토랑에서는 아침 일찍 가면 갓 잡은 생선을 먹을 수 있어요.",
    "킨타마니": "킨타마니 뷔페는 화산 전망이 포함된 가격입니다. 자리 선택이 중요해요.",
    "타나롯": "타나롯 사원 근처 카페에서는 발리 커피를 'Kopi Bali satu'라고 주문하세요.",
    "베두굴": "베두굴 캔디쿠닝 마켓에서는 딸기를 'Stroberi satu kilo'라고 주문하면 1kg 단위로 살 수 있어요.",
    "타바난": "타바난 마을 warung에서는 농부가 직접 만든 음식을 먹을 수 있어요. 'Nasi Campur'라고 하면 됩니다.",
}

# 도시별 고유 알레르기 팁 (땅콩 알레르기 대체)
ALLERGY_TIPS = {
    "꾸따": "꾸따 레스토랑은 외국인이 많아서 영어 메뉴가 대부분 있어요. 알레르기가 있다면 'Alergi'라고 미리 말하세요.",
    "우붓": "우붓의 전통 음식은 향신료가 강해요. 처음엔 덜 맵게 주문하는 걸 추천해요.",
}

def fix_duplicates(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    city = None
    for part in filepath.parts:
        if part in FOOD_TIPS:
            city = part
    
    if not city:
        return False
    
    modified = False
    
    # 1. "꼭 알아두세요" 박스의 Tidak pedas 문장 교체
    old_tip = """<strong>꼭 알아두세요:</strong> 'Tidak pedas'(안 맵게), 'Tanpa gula'(설탕 없이) 표현 알아두면 편해요."""
    new_tip = f"""<strong>꼭 알아두세요:</strong> {FOOD_TIPS[city]}"""
    if old_tip in content:
        content = content.replace(old_tip, new_tip)
        modified = True
    
    # 2. "Tidak pedas" 남은 문장 교체
    old_tidak = """'Tidak pedas'(안 맵게)라고 하면 맞춰줘요."""
    new_tidak = FOOD_TIPS[city]
    if old_tidak in content:
        content = content.replace(old_tidak, new_tidak)
        modified = True
    
    # 3. 땅콩 알레르기 문장 교체 (꾸따, 우붓만)
    old_peanut = """꾸따 레스토랑은 외국인이 많아서 영어 메뉴가 대부분 있어요. 하지만 알레르기가 있다면 'Alergi kacang'(땅콩 알레르기)이라고 미리 말하세요."""
    new_peanut = ALLERGY_TIPS.get(city, FOOD_TIPS[city])
    if old_peanut in content:
        content = content.replace(old_peanut, new_peanut)
        modified = True
    
    old_peanut2 = """우붓의 전통 음식은 땅콩 소스가 많이 들어가요. 알레르기가 있다면 'Alergi kacang'이라고 말하세요."""
    new_peanut2 = ALLERGY_TIPS.get(city, FOOD_TIPS[city])
    if old_peanut2 in content:
        content = content.replace(old_peanut2, new_peanut2)
        modified = True
    
    # 4. "오전 7시" 문장 교체
    old_hours = """워룽은 보통 오전 7시에 열어요."""
    if old_hours in content:
        hours_tips = {
            "사누르": "사누르 워룽은 오전 6시부터 열어요. 해변 산책 후 아침 식사하기 좋습니다.",
            "짠디다사": "짠디다사 워룽은 오전 7시에 열어요. 해변 레스토랑은 오후까지 영업해요.",
            "로비나": "로비나 워룽은 오전 6시에 열어요. 새벽에 생선을 잡아와서 신선해요.",
            "타나롯": "타나롯 사원은 오전 7시에 열어요. 오후 5시까지 관람 가능.",
        }
        new_hours = hours_tips.get(city, "워룽은 보통 오전 8시에 열어요.")
        content = content.replace(old_hours, new_hours)
        modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return modified

def main():
    html_files = list(BASE.rglob("*.html"))
    fixed = 0
    for f in html_files:
        if fix_duplicates(f):
            fixed += 1
    print(f"수정 완료: {fixed}/{len(html_files)} 파일")
    
    # 검증
    for phrase in ["Tidak pedas", "땅콩 알레르기", "Alergi kacang", "오전 7시에 열어요"]:
        count = sum(1 for f in html_files if phrase in f.read_text(encoding='utf-8'))
        print(f"  '{phrase}': {count}/{len(html_files)}")

if __name__ == "__main__":
    main()
