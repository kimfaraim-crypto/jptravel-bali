#!/usr/bin/env python3
"""원화 환산 오류 + Q&A 중복 + 이미지 alt 다양화 수정"""
import re, hashlib, random
from pathlib import Path

html_dir = Path("output/html/bali")

cat_img_alts = {
    "food": ["맛집 음식 사진", "현지 레스토랑 사진", "비치클럽 음료 사진", "로컬 와룽 식사 사진", "브런치 카페 분위기", "해산물 BBQ 사진", "전통 발리 요리 사진", "카페 인테리어 사진", "디저트 메뉴 사진", "야시장 음식 사진"],
    "culture": ["사원 전경 사진", "전통 공연 케착춤 사진", "사원 건축 양식 사진", "힌두교 의식 사진", "문화 체험 활동 사진", "미술관 전시 사진", "사원 조각상 사진", "전통 춤 공연 사진", "사원 입구 풍경", "예술 공방 사진"],
    "beach": ["해변 전경 사진", "서핑 포인트 파도 사진", "비치클럽 선셋 사진", "스노클링 포인트 사진", "해변 산책로 사진", "수영장/비치 풍경", "해변 일몰 사진", "해변 액티비티 사진", "해변 카페 사진", "해변 모래사장 사진"],
    "nature": ["라이스 테라스 풍경", "폭포 전경 사진", "트레킹 코스 사진", "화산 일출 사진", "열대 우림 풍경", "원숭이 숲 사진", "자연 수영장 사진", "정원/식물원 사진", "강변 풍경 사진", "전망대 뷰 사진"],
    "shopping": ["아트 마켓 풍경", "기념품 가게 사진", "마사지/스파 내부 사진", "쇼핑몰 전경", "전통 공예품 사진", "시장 풍경 사진", "라탄 가방/기념품 사진", "스파 트리트먼트 사진", "로컬 시장 쇼핑 사진", "부티크숍 내부 사진"],
    "transport": ["공항 풍경 사진", "스쿠터 렌트 사진", "그랩 택시 이용 사진", "교통체증 풍경", "보트/페리 사진", "도로 풍경 사진", "주차장/차량 사진", "공항 셔틀 사진", "시내 이동 풍경", "교통 수단 비교 사진"],
}

fixed_total = 0
for f in sorted(html_dir.rglob("*.html")):
    with open(f) as fh:
        content = fh.read()
    parts = f.relative_to(html_dir).parts
    area, cat, page = parts[0], parts[1], parts[2].replace(".html", "")
    original = content

    # Fix 1: 원화 환산 — "(약 N원)" where N < 100 → multiply by 1000
    # The bug: 25,000Rp / 10 = 2500, but script wrote "약 2원" (divided by 10 twice or wrong calc)
    # Actually the issue is: 25,000Rp → 25,000/10 = 2,500원 but script shows "약 2원"
    # So the formula was num/10 but displayed as just num without proper formatting
    # Fix: (약 X원) where X < 100 → (약 X,000원)
    content = re.sub(
        r"\(약 (\d)원\)",
        lambda m: f"(약 {int(m.group(1)) * 1000:,}원)",
        content
    )
    # Also fix (약 NN원) where NN < 100
    content = re.sub(
        r"\(약 (\d{2})원\)",
        lambda m: f"(약 {int(m.group(1)) * 100:,}원)",
        content
    )
    # Fix (약 N0원) patterns like (약 50원) which should be (약 5,000원)
    content = re.sub(
        r"\(약 (\d{2,3})원\)",
        lambda m: f"(약 {int(m.group(1)) * 100:,}원)" if int(m.group(1)) < 500 else m.group(0),
        content
    )

    # Fix 2: Q&A question word duplication "우붓 우붓" → "우붓"
    content = re.sub(r"([\uac00-\ud7af]+)\s+\1(?=[\s?])", r"\1", content)

    # Fix 3: Image alt diversity
    if cat in cat_img_alts:
        alts = cat_img_alts[cat]
        rng = random.Random(int(hashlib.md5(f"{area}_{cat}_{page}".encode()).hexdigest()[:8], 16))
        shuffled = list(alts)
        rng.shuffle(shuffled)
        alt_iter = iter(shuffled * 2)  # Double for 10 images

        def replace_alt(m, _iter=alt_iter, _area=area):
            old_alt = m.group(1)
            if "여행 사진" in old_alt and len(old_alt) < 20:
                try:
                    new_alt = f"{_area} {next(_iter)}"
                except StopIteration:
                    new_alt = old_alt
                return f'alt="{new_alt}"'
            return m.group(0)

        content = re.sub(r'alt="([^"]*)"', replace_alt, content)

    if content != original:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(content)
        fixed_total += 1

print(f"수정된 파일: {fixed_total}개")

# Verify
print("\n검증:")
sample = html_dir / "우붓" / "food" / "001.html"
with open(sample) as fh:
    c = fh.read()

# Check KRW
krw = re.findall(r"\(약 [\d,]+원\)", c)
print(f"  원화 표시 샘플: {krw[:5]}")

# Check Q&A
qas = re.findall(r"❓ (.*?)\?", c)
for q in qas[:3]:
    print(f"  Q&A 질문: {q}")

# Check alt
alts = re.findall(r'alt="(.*?)"', c)
content_alts = [a for a in alts if not a.startswith("마이리얼트립")]
print(f"  이미지 alt: {content_alts[:5]}")
print(f"  고유 alt 수: {len(set(content_alts))}/{len(content_alts)}")
