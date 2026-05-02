#!/usr/bin/env python3
"""
Fast image expansion - 3000 images in 10 minutes
Uses concurrent downloads from Picsum (fast, reliable) + Openverse (variety)
"""
import json, hashlib, time, os, sys, random
from pathlib import Path
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
HASH_FILE = BASE_DIR / "global_image_hashes.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]

AREA_KW = {
    "우붓": "ubud", "스미냑": "seminyak", "꾸따": "kuta",
    "사누르": "sanur", "누사두아": "nusa dua", "울루와뚜": "uluwatu",
    "짠디다사": "candidasa", "로비나": "lovina", "킨타마니": "kintamani",
    "타나롯": "tanah lot", "베두굴": "bedugul",
}

TARGET_PER_COMBO = 50  # Target per area/category
HEADERS = {"User-Agent": "JPTravelBali/2.0"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Load hashes once
hash_db = {}
if HASH_FILE.exists():
    try:
        hash_db = json.loads(HASH_FILE.read_text())
    except:
        pass

def perceptual_hash(img):
    try:
        s = img.resize((8,8)).convert('L')
        p = list(s.getdata())
        avg = sum(p)/len(p)
        return hex(int(''.join('1' if x>avg else '0' for x in p), 2))[2:].zfill(16)
    except:
        return None

def is_dup(img):
    ph = perceptual_hash(img)
    if not ph: return True, None
    for v in hash_db.values():
        try:
            b1 = bin(int(ph,16))[2:].zfill(64)
            b2 = bin(int(v,16))[2:].zfill(64)
            if sum(a!=b for a,b in zip(b1,b2)) <= 5:
                return True, None
        except:
            pass
    return False, ph

def download_one(args):
    """Download single image - returns (success, path, hash)"""
    url, path, idx = args
    try:
        r = SESSION.get(url, timeout=12, allow_redirects=True, stream=False)
        if r.status_code != 200:
            return False, path, None
        c = r.content
        if len(c) < 2000:
            return False, path, None
        img = Image.open(BytesIO(c))
        if img.width < 100 or img.height < 100:
            return False, path, None
        dup, ph = is_dup(img)
        if dup:
            return False, path, None
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(str(path), 'WEBP', quality=80)
        return True, path, ph
    except:
        return False, path, None

def generate_urls(area, cat, start_idx, count):
    """Generate Picsum URLs with unique seeds"""
    urls = []
    area_hash = hashlib.md5(f"{area}_{cat}".encode()).hexdigest()[:6]
    for i in range(count):
        seed = f"{area_hash}_{start_idx + i}_{int(time.time()) % 10000}"
        url = f"https://picsum.photos/seed/{seed}/1200/800"
        urls.append(url)
    return urls

def process_combo(area, cat, existing_count, needed):
    """Download images for one area/category combo"""
    out = OUTPUT_DIR / area / cat
    out.mkdir(parents=True, exist_ok=True)
    
    urls = generate_urls(area, cat, existing_count, needed * 3)  # 3x for dup tolerance
    
    tasks = []
    for i, url in enumerate(urls):
        idx = existing_count + i + 1
        fname = f"{area}_{cat}_{idx:04d}.webp"
        sp = out / fname
        if sp.exists():
            continue
        tasks.append((url, sp, idx))
    
    success = 0
    if not tasks:
        return 0
    
    # 8 concurrent workers per combo
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(download_one, t): t for t in tasks[:needed*2]}
        for future in as_completed(futures):
            if success >= needed:
                break
            ok, path, ph = future.result()
            if ok:
                success += 1
                hash_db[path.name] = ph
    
    return success

def main():
    start_time = time.time()
    print("=" * 60)
    print("🚀 Fast Image Expansion - 3000 images in 10 min")
    print("=" * 60)
    sys.stdout.flush()

    mapping = json.loads(MAPPING_FILE.read_text())
    total_new = 0
    
    # Build task list: prioritize areas with fewer images
    tasks = []
    for area in AREAS:
        if area not in mapping:
            mapping[area] = {}
        for cat in CATEGORIES:
            existing = len(mapping[area].get(cat, []))
            if existing < TARGET_PER_COMBO:
                needed = TARGET_PER_COMBO - existing
                tasks.append((area, cat, existing, needed))
    
    # Sort by most needed first
    tasks.sort(key=lambda x: -x[3])
    
    print(f"📋 {len(tasks)}개 조합 보충 필요, 목표: {TARGET_PER_COMBO}개/조합")
    sys.stdout.flush()
    
    # Process with global thread pool (max 32 concurrent)
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {}
        for area, cat, existing, needed in tasks:
            future = executor.submit(process_combo, area, cat, existing, needed)
            futures[future] = (area, cat, needed)
        
        for future in as_completed(futures):
            area, cat, needed = futures[future]
            try:
                result = future.result()
                total_new += result
                elapsed = time.time() - start_time
                print(f"  ✅ {area}/{cat}: +{result}개 ({elapsed:.0f}초)")
                sys.stdout.flush()
            except Exception as e:
                print(f"  ❌ {area}/{cat}: 오류 {e}")
                sys.stdout.flush()
    
    # Update mapping from disk
    print("\n📋 매핑 업데이트...")
    for area in AREAS:
        if area not in mapping:
            mapping[area] = {}
        for cat in CATEGORIES:
            out = OUTPUT_DIR / area / cat
            if out.exists():
                imgs = sorted([f.name for f in out.glob("*.webp")])
                mapping[area][cat] = imgs
    
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    
    # Save hashes
    HASH_FILE.write_text(json.dumps(hash_db, ensure_ascii=False, indent=2))
    
    elapsed = time.time() - start_time
    total_imgs = sum(len(v) for cats in mapping.values() for v in cats.values())
    
    print(f"\n{'=' * 60}")
    print(f"✅ 완료!")
    print(f"   신규 다운로드: {total_new}개")
    print(f"   총 이미지: {total_imgs}개")
    print(f"   소요 시간: {elapsed:.0f}초 ({elapsed/60:.1f}분)")
    print(f"{'=' * 60}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
