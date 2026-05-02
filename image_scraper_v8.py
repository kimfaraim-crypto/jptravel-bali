#!/usr/bin/env python3
"""
발리 이미지 스크래퍼 v8 — Openverse API 활용
- 지역별+카테고리별 검색어로 이미지 다운로드
- WebP 변환 및 중복 제거
- 이미지당 고유 alt text 생성
"""

import os, sys, json, hashlib, time, requests
from pathlib import Path
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
HASH_DB = BASE_DIR / "image_hashes_v8.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

AREA_EN = {
    "우붓": "ubud", "스미냑": "seminyak", "꾸따": "kuta",
    "사누르": "sanur", "누사두아": "nusa dua", "울루와뚜": "uluwatu",
    "짠디다사": "candidasa", "로비나": "lovina", "킨타마니": "kintamani",
    "타나롯": "tanah lot", "베두굴": "bedugul",
}

# 지역별+카테고리별 검색 키워드 (Openverse 검색용)
SEARCH_QUERIES = {
    "우붓": {
        "food": ["ubud bali food", "ubud restaurant bali", "bali warung ubud", "ubud cafe bali", "babi guling ubud"],
        "culture": ["ubud temple bali", "ubud palace bali", "monkey forest ubud", "bali dance ubud", "ubud art museum"],
        "beach": ["ubud rice terrace", "ubud jungle bali", "bali nature ubud", "campuhan ridge ubud"],
        "nature": ["tegalalang rice terrace", "ubud waterfall bali", "bali rice field ubud", "alas harum bali", "ubud swing"],
        "shopping": ["ubud art market bali", "ubud market", "bali craft ubud", "ubud souvenir", "ubud spa bali"],
        "transport": ["bali scooter ubud", "bali road ubud", "grab bali ubud", "ubud traffic bali"],
    },
    "타나롯": {
        "food": ["tanah lot bali food", "tanah lot restaurant", "bali warung tanah lot"],
        "culture": ["tanah lot temple bali", "tanah lot sunset", "bali sea temple", "pura tanah lot"],
        "beach": ["tanah lot beach bali", "bali coast tanah lot", "bali sunset tanah lot"],
        "nature": ["tanah lot bali", "bali temple coast", "rice terrace tanah lot"],
        "shopping": ["tanah lot market bali", "bali souvenir tanah lot"],
        "transport": ["bali transport tanah lot", "bali road tanah lot"],
    },
    "꾸따": {
        "food": ["kuta bali food", "kuta restaurant bali", "bali warung kuta", "kuta beach cafe"],
        "culture": ["kuta bali art", "bali market kuta", "waterbom bali kuta"],
        "beach": ["kuta beach bali", "bali surfing kuta", "kuta sunset bali", "bali waves kuta", "legian beach bali"],
        "nature": ["bali beach kuta", "kuta coast bali", "bali ocean kuta"],
        "shopping": ["beachwalk mall kuta", "discovery mall bali", "kuta shopping bali", "bali market kuta"],
        "transport": ["bali airport kuta", "kuta traffic bali", "bali taxi kuta"],
    },
    "스미냑": {
        "food": ["seminyak bali food", "seminyak restaurant", "potato head bali", "bali cafe seminyak", "seminyak beach club"],
        "culture": ["seminyak temple bali", "bali art seminyak", "petitenget temple"],
        "beach": ["seminyak beach bali", "double six beach", "bali sunset seminyak", "seminyak surf"],
        "nature": ["seminyak beach walk", "bali coast seminyak", "seminyak sunset"],
        "shopping": ["seminyak shopping bali", "seminyak boutique", "bali spa seminyak", "seminyak market"],
        "transport": ["bali transport seminyak", "seminyak scooter bali"],
    },
    "사누르": {
        "food": ["sanur bali food", "sanur restaurant", "warung mak beng", "bali cafe sanur"],
        "culture": ["sanur bali art", "bali museum sanur", "le mayeur museum"],
        "beach": ["sanur beach bali", "bali sunrise sanur", "sanur coast", "bali cycling sanur"],
        "nature": ["sanur beach sunrise", "bali nature sanur", "sanur coastal path"],
        "shopping": ["sanur market bali", "sanur night market", "bali craft sanur"],
        "transport": ["bali transport sanur", "sanur bike bali"],
    },
    "누사두아": {
        "food": ["nusa dua bali food", "nusa dua restaurant", "bali resort food nusa dua"],
        "culture": ["nusa dua bali", "bali theater nusa dua", "devdan show bali"],
        "beach": ["nusa dua beach bali", "bali blowhole nusa dua", "nusa dua coast", "bali water sport nusa dua"],
        "nature": ["nusa dua bali nature", "bali coast nusa dua", "waterblow nusa dua"],
        "shopping": ["bali collection nusa dua", "nusa dua shopping", "bali spa nusa dua"],
        "transport": ["bali transport nusa dua", "nusa dua resort shuttle"],
    },
    "울루와뚜": {
        "food": ["uluwatu bali food", "uluwatu restaurant", "single fin bali", "rock bar bali"],
        "culture": ["uluwatu temple bali", "kecak dance uluwatu", "bali cliff temple"],
        "beach": ["uluwatu beach bali", "bali surf uluwatu", "blue point beach bali", "pandawa beach bali", "jimbaran beach bali"],
        "nature": ["uluwatu cliff bali", "bali coast uluwatu", "uluwatu sunset"],
        "shopping": ["uluwatu souvenir bali", "bali craft uluwatu"],
        "transport": ["bali transport uluwatu", "uluwatu scooter bali"],
    },
    "짠디다사": {
        "food": ["candidasa bali food", "candidasa restaurant", "bali warung candidasa"],
        "culture": ["besakih temple bali", "bali temple candidasa", "tirta gangga bali"],
        "beach": ["candidasa beach bali", "amed beach bali", "bali east coast", "bali diving candidasa"],
        "nature": ["bali volcano candidasa", "amed bali", "bali east nature"],
        "shopping": ["candidasa market bali", "bali craft candidasa"],
        "transport": ["bali transport candidasa", "bali east road"],
    },
    "로비나": {
        "food": ["lovina bali food", "lovina restaurant", "bali warung lovina"],
        "culture": ["lovina bali", "bali north temple", "budhul temple lovina"],
        "beach": ["lovina beach bali", "bali dolphin lovina", "lovina coast", "bali north beach"],
        "nature": ["lovina dolphin bali", "banjar hot spring", "gitgit waterfall bali", "bali north nature"],
        "shopping": ["lovina market bali", "bali souvenir lovina"],
        "transport": ["bali transport lovina", "bali north road"],
    },
    "킨타마니": {
        "food": ["kintamani bali food", "batur restaurant bali", "kintamani buffet"],
        "culture": ["kintamani temple bali", "bali temple kintamani", "triti empul"],
        "beach": [],
        "nature": ["mount batur bali", "kintamani volcano", "batur lake bali", "bali sunrise trek", "kintamani bali"],
        "shopping": ["kintamani market bali"],
        "transport": ["bali transport kintamani", "bali mountain road"],
    },
    "베두굴": {
        "food": ["bedugul bali food", "bedugul restaurant", "bali highland food"],
        "culture": ["ulun danu temple bali", "bedugul temple", "bali lake temple"],
        "beach": [],
        "nature": ["bratan lake bali", "bedugul bali", "bali botanic garden", "bali highland nature", "bedugul market"],
        "shopping": ["bedugul market bali", "bali strawberry farm", "bedugul traditional market"],
        "transport": ["bali transport bedugul", "bali highland road"],
    },
}

# 카테고리별 보조 키워드
CATEGORY_EXTRA_KW = {
    "food": ["food", "restaurant", "warung", "cafe", "cuisine", "dining", "seafood"],
    "culture": ["temple", "ceremony", "dance", "culture", "art", "shrine", "ritual"],
    "beach": ["beach", "surf", "ocean", "coast", "sea", "waves", "sunset"],
    "nature": ["nature", "rice terrace", "waterfall", "volcano", "jungle", "forest", "lake"],
    "shopping": ["market", "shopping", "souvenir", "craft", "spa", "boutique"],
    "transport": ["transport", "road", "scooter", "taxi", "airport", "traffic"],
}


def load_existing_hashes():
    """기존 이미지 해시 로드 (중복 방지)"""
    if HASH_DB.exists():
        try:
            return json.loads(HASH_DB.read_text())
        except:
            pass
    return {}


def save_hashes(hashes):
    """이미지 해시 저장"""
    HASH_DB.write_text(json.dumps(hashes, indent=2), encoding='utf-8')


def compute_image_hash(img_bytes):
    """이미지 perceptual hash 계산"""
    try:
        img = Image.open(BytesIO(img_bytes)).convert('RGB').resize((8, 8))
        pixels = list(img.getdata())
        avg = sum(p[0] + p[1] + p[2] for p in pixels) / len(pixels)
        bits = ''.join('1' if (p[0] + p[1] + p[2]) > avg else '0' for p in pixels)
        return hex(int(bits, 2))[2:].zfill(16)
    except:
        return None


def search_openverse(query, page_size=20):
    """Openverse API로 이미지 검색"""
    url = f"https://api.openverse.org/v1/images/?q={query}&license_type=commercial&page_size={page_size}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json().get("results", [])
    except Exception as e:
        print(f"  ⚠️ Openverse 검색 실패: {e}")
    return []


def download_image(img_url, timeout=15):
    """이미지 다운로드"""
    try:
        r = requests.get(img_url, timeout=timeout, stream=True)
        if r.status_code == 200 and len(r.content) > 5000:  # 최소 5KB
            return r.content
    except:
        pass
    return None


def convert_to_webp(img_bytes, max_size=(1200, 800)):
    """이미지를 WebP로 변환"""
    try:
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        img.thumbnail(max_size, Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='WEBP', quality=85)
        return buf.getvalue()
    except:
        return None


def scrape_area_category(area, category, target_count=30):
    """지역+카테고리 이미지 스크래핑"""
    area_en = AREA_EN.get(area, area)
    queries = SEARCH_QUERIES.get(area, {}).get(category, [])

    # 쿼리가 없으면 보조 키워드로 생성
    if not queries:
        cat_kw = CATEGORY_EXTRA_KW.get(category, ["travel"])
        queries = [f"{area_en} {kw}" for kw in cat_kw[:3]]

    # 기존 이미지 확인
    existing_dir = OUTPUT_DIR / area / category
    existing_count = len(list(existing_dir.glob("*.webp"))) if existing_dir.exists() else 0

    if existing_count >= target_count:
        print(f"  ✅ {area}/{category}: 이미 {existing_count}장 존재")
        return 0

    need = target_count - existing_count
    print(f"  🔍 {area}/{category}: {need}장 추가 필요 (기존 {existing_count}장)")

    # 기존 해시 로드
    hashes = load_existing_hashes()

    # 이미지 번호 계산
    existing_files = sorted(existing_dir.glob("*.webp")) if existing_dir.exists() else []
    next_num = len(existing_files) + 1

    downloaded = 0
    seen_hashes = set(hashes.values())

    for query in queries:
        if downloaded >= need:
            break

        results = search_openverse(query, page_size=30)
        print(f"    검색 '{query}': {len(results)}개 결과")

        for img_data in results:
            if downloaded >= need:
                break

            img_url = img_data.get("url", "")
            if not img_url:
                continue

            # 다운로드
            img_bytes = download_image(img_url)
            if not img_bytes:
                continue

            # 해시 계산 (중복 방지)
            img_hash = compute_image_hash(img_bytes)
            if not img_hash or img_hash in seen_hashes:
                continue

            # WebP 변환
            webp_bytes = convert_to_webp(img_bytes)
            if not webp_bytes:
                continue

            # 저장
            filename = f"{area}_{category}_{next_num:04d}.webp"
            filepath = existing_dir / filename
            existing_dir.mkdir(parents=True, exist_ok=True)
            filepath.write_bytes(webp_bytes)

            # 해시 저장
            hashes[filename] = img_hash
            seen_hashes.add(img_hash)

            downloaded += 1
            next_num += 1

            # API 부하 방지
            time.sleep(0.3)

    save_hashes(hashes)
    return downloaded


def main():
    print("=" * 60)
    print("🖼️  발리 이미지 스크래퍼 v8 — Openverse API")
    print("=" * 60)

    total_downloaded = 0

    for area in AREAS:
        print(f"\n📍 {area}")
        for category in SEARCH_QUERIES.get(area, {}).keys():
            count = scrape_area_category(area, category, target_count=30)
            total_downloaded += count

    print(f"\n{'=' * 60}")
    print(f"✅ 총 {total_downloaded}장 이미지 다운로드 완료!")
    print(f"📁 위치: {OUTPUT_DIR}")

    # 이미지 매핑 업데이트
    print("\n📋 이미지 매핑 업데이트 중...")
    mapping = {}
    for area in AREAS:
        mapping[area] = {}
        for cat_dir in (OUTPUT_DIR / area).iterdir():
            if cat_dir.is_dir():
                files = sorted([f.name for f in cat_dir.glob("*.webp")])
                mapping[area][cat_dir.name] = files

    MAPPING_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ 매핑 저장: {MAPPING_FILE}")


if __name__ == "__main__":
    main()
