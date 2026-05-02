#!/usr/bin/env python3
"""
Fill image shortages for area/category combos with < 14 images.
Uses Picsum photos as reliable fallback, with perceptual hash dedup.
"""
import json, hashlib, time, os
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
HASH_FILE = BASE_DIR / "image_hashes_v7.json"

TARGET = 20  # Target images per area/category (enough for 14 pages)

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]

HEADERS = {"User-Agent": "JPTravelBali/1.0"}

def load_hashes():
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text())
    return {}

def save_hashes(h):
    HASH_FILE.write_text(json.dumps(h, ensure_ascii=False, indent=2))

def perceptual_hash(img):
    try:
        s = img.resize((8,8)).convert('L')
        p = list(s.getdata())
        avg = sum(p)/len(p)
        return hex(int(''.join('1' if x>avg else '0' for x in p), 2))[2:].zfill(16)
    except:
        return None

def phash_dist(h1, h2):
    try:
        b1 = bin(int(h1,16))[2:].zfill(64)
        b2 = bin(int(h2,16))[2:].zfill(64)
        return sum(a!=b for a,b in zip(b1,b2))
    except:
        return 999

def is_dup(img, hashes):
    ph = perceptual_hash(img)
    if not ph: return True, None
    for v in hashes.values():
        if phash_dist(ph, v) <= 5:
            return True, None
    return False, ph

def download_picsum(path, hashes, seed):
    """Download from Picsum with dedup check"""
    url = f"https://picsum.photos/seed/{seed}/1200/800"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            return False
        c = r.content
        if len(c) < 3000:
            return False
        img = Image.open(BytesIO(c))
        if img.width < 150 or img.height < 150:
            return False
        dup, ph = is_dup(img, hashes)
        if dup:
            return False
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(str(path), 'WEBP', quality=85)
        hashes[path.name] = ph
        return True
    except Exception as e:
        return False

def main():
    print("=" * 60)
    print("🖼️  Filling Image Shortages")
    print("=" * 60)

    mapping = json.loads(MAPPING_FILE.read_text())
    hashes = load_hashes()
    total_new = 0

    for area in AREAS:
        if area not in mapping:
            mapping[area] = {}
        for cat in CATEGORIES:
            existing = mapping[area].get(cat, [])
            count = len(existing)
            if count >= TARGET:
                continue

            needed = TARGET - count
            print(f"\n📥 {area}/{cat}: {count}개 → {TARGET}개 필요 ({needed}개 부족)")

            out = OUTPUT_DIR / area / cat
            out.mkdir(parents=True, exist_ok=True)

            new = 0
            attempts = 0
            max_attempts = needed * 10

            while new < needed and attempts < max_attempts:
                attempts += 1
                seed = hashlib.md5(f"{area}_{cat}_{count + new}_{attempts}".encode()).hexdigest()[:12]
                idx = count + new + 1
                fname = f"{area}_{cat}_{idx:04d}.webp"
                sp = out / fname
                if sp.exists():
                    new += 1
                    continue
                if download_picsum(sp, hashes, seed):
                    new += 1
                    total_new += 1
                    print(f"  ✅ {fname}")
                time.sleep(0.3)

            # Update mapping
            imgs = sorted([f.name for f in out.glob("*.webp")])
            mapping[area][cat] = imgs
            print(f"  → 완료: +{new}개 (총 {len(imgs)}개)")

    # Save mapping and hashes
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    save_hashes(hashes)

    print(f"\n{'=' * 60}")
    print(f"✅ 이미지 보충 완료! 신규: {total_new}개")

    # Verify all combos have >= 14
    remaining = []
    for area in AREAS:
        for cat in CATEGORIES:
            count = len(mapping.get(area, {}).get(cat, []))
            if count < 14:
                remaining.append(f"  {area}/{cat}: {count}")
    if remaining:
        print(f"\n⚠️ 아직 부족 ({len(remaining)}개):")
        for r in remaining:
            print(r)
    else:
        print("\n✅ 모든 조합 14개 이상 확보!")

if __name__ == "__main__":
    main()
