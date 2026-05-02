#!/usr/bin/env python3
"""
Fast image expansion v2 - aggressive parallel download
Sources: Unsplash Source (diverse, fast) + Picsum by ID
"""
import json, hashlib, time, sys, random
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

TARGET_PER_COMBO = 60

# Category-specific Unsplash search terms
CAT_QUERIES = {
    "food": ["bali-food", "indonesian-cuisine", "bali-restaurant", "nasi-goreng", "bali-warung", "bali-seafood", "bali-cafe", "bali-coffee", "bali-street-food", "bali-fruit"],
    "culture": ["bali-temple", "bali-ceremony", "bali-dance", "bali-hindu", "bali-offering", "bali-ritual", "bali-shrine", "bali-gamelan", "bali-barong", "bali-art"],
    "beach": ["bali-beach", "bali-surfing", "bali-sunset", "bali-ocean", "bali-wave", "bali-snorkeling", "bali-coast", "bali-sand", "bali-sea", "bali-island"],
    "nature": ["bali-rice-terrace", "bali-waterfall", "bali-volcano", "bali-jungle", "bali-monkey", "bali-mountain", "bali-lake", "bali-forest", "bali-nature", "bali-trekking"],
    "shopping": ["bali-market", "bali-shopping", "bali-spa", "bali-massage", "bali-craft", "bali-souvenir", "bali-art-market", "bali-boutique", "bali-handicraft", "bali-textile"],
    "transport": ["bali-scooter", "bali-airport", "bali-transport", "bali-taxi", "bali-road", "bali-travel", "bali-traffic", "bali-boat", "bali-motorbike", "bali-bus"],
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "JPTravelBali/2.0"})

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
            dist = sum(a!=b for a,b in zip(b1,b2))
            if dist <= 4:  # Stricter threshold for more variety
                return True, None
        except:
            pass
    return False, ph

def dl(args):
    url, path = args
    try:
        r = SESSION.get(url, timeout=10, allow_redirects=True)
        if r.status_code != 200: return False, path, None
        c = r.content
        if len(c) < 1500: return False, path, None
        img = Image.open(BytesIO(c))
        if img.width < 80 or img.height < 80: return False, path, None
        dup, ph = is_dup(img)
        if dup: return False, path, None
        if img.mode in ('RGBA','P'): img = img.convert('RGB')
        img.save(str(path), 'WEBP', quality=80)
        return True, path, ph
    except:
        return False, path, None

def gen_urls(area, cat, start, count):
    """Generate diverse URLs from multiple sources"""
    urls = []
    queries = CAT_QUERIES.get(cat, [cat])
    area_en = area  # Will be mapped
    
    # Source 1: Unsplash Source (diverse, keyword-based)
    for i in range(count):
        q = queries[i % len(queries)]
        seed = hashlib.md5(f"{area}_{cat}_{start+i}_{time.time()}".encode()).hexdigest()[:8]
        url = f"https://source.unsplash.com/1200x800/?{q},{area_en}&sig={seed}"
        urls.append(url)
    
    # Source 2: Picsum by specific IDs (no seed collision)
    picsum_start = (hashlib.md5(f"{area}{cat}".encode()).hexdigest()[:4])
    picsum_base = int(picsum_start, 16) % 1000
    for i in range(count // 2):
        pid = (picsum_base + start + i) % 1084 + 1  # Picsum has ~1084 images
        url = f"https://picsum.photos/id/{pid}/1200/800"
        urls.append(url)
    
    random.shuffle(urls)
    return urls

def process_combo(area, cat, existing, needed):
    out = OUTPUT_DIR / area / cat
    out.mkdir(parents=True, exist_ok=True)
    
    urls = gen_urls(area, cat, existing, needed * 4)
    tasks = []
    for i, url in enumerate(urls):
        idx = existing + i + 1
        fname = f"{area}_{cat}_{idx:04d}.webp"
        sp = out / fname
        if sp.exists(): continue
        tasks.append((url, sp))
    
    success = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(dl, t): t for t in tasks[:needed*3]}
        for f in as_completed(futs):
            if success >= needed: break
            ok, path, ph = f.result()
            if ok:
                success += 1
                hash_db[path.name] = ph
    return success

def main():
    start = time.time()
    print("=" * 60)
    print("🚀 Fast Expansion v2 - 3000 images")
    print("=" * 60)
    sys.stdout.flush()

    mapping = json.loads(MAPPING_FILE.read_text())
    total_new = 0
    
    tasks = []
    for area in AREAS:
        if area not in mapping: mapping[area] = {}
        for cat in CATEGORIES:
            existing = len(mapping[area].get(cat, []))
            if existing < TARGET_PER_COMBO:
                tasks.append((area, cat, existing, TARGET_PER_COMBO - existing))
    
    tasks.sort(key=lambda x: -x[3])
    print(f"📋 {len(tasks)}개 조합, 총 {sum(t[3] for t in tasks)}개 필요")
    sys.stdout.flush()
    
    # Process ALL combos concurrently (not one-by-one)
    with ThreadPoolExecutor(max_workers=48) as executor:
        futures = {}
        for area, cat, existing, needed in tasks:
            f = executor.submit(process_combo, area, cat, existing, needed)
            futures[f] = (area, cat, needed)
        
        for f in as_completed(futures):
            area, cat, needed = futures[f]
            try:
                r = f.result()
                total_new += r
                elapsed = time.time() - start
                print(f"  ✅ {area}/{cat}: +{r}개 ({elapsed:.0f}s)")
                sys.stdout.flush()
            except Exception as e:
                print(f"  ❌ {area}/{cat}: {e}")
                sys.stdout.flush()
            
            if time.time() - start > 540:  # 9 min cutoff
                print("  ⏰ 시간 제한 도달")
                break
    
    # Update mapping
    print("\n📋 매핑 업데이트...")
    for area in AREAS:
        for cat in CATEGORIES:
            out = OUTPUT_DIR / area / cat
            if out.exists():
                mapping[area][cat] = sorted([f.name for f in out.glob("*.webp")])
    
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    HASH_FILE.write_text(json.dumps(hash_db, ensure_ascii=False, indent=2))
    
    elapsed = time.time() - start
    total = sum(len(v) for cats in mapping.values() for v in cats.values())
    print(f"\n{'='*60}")
    print(f"✅ 완료! +{total_new}개 (총 {total}개) / {elapsed:.0f}초")
    print(f"{'='*60}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
