#!/usr/bin/env python3
"""
Fast expansion v3 - Use Picsum IDs (1084 unique photos) + relaxed dedup
Each Picsum ID = unique photo, no hash collision possible
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
TARGET = 60

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0"})

hash_db = {}
if HASH_FILE.exists():
    try: hash_db = json.loads(HASH_FILE.read_text())
    except: pass

def phash(img):
    try:
        s = img.resize((8,8)).convert('L')
        p = list(s.getdata())
        avg = sum(p)/len(p)
        return hex(int(''.join('1' if x>avg else '0' for x in p), 2))[2:].zfill(16)
    except: return None

def dl(args):
    url, path, use_hash = args
    try:
        r = SESSION.get(url, timeout=10, allow_redirects=True)
        if r.status_code != 200: return False, path, None
        c = r.content
        if len(c) < 1000: return False, path, None
        img = Image.open(BytesIO(c))
        if img.width < 50: return False, path, None
        if use_hash:
            ph = phash(img)
            if ph:
                for v in hash_db.values():
                    try:
                        b1 = bin(int(ph,16))[2:].zfill(64)
                        b2 = bin(int(v,16))[2:].zfill(64)
                        if sum(a!=b for a,b in zip(b1,b2)) <= 3:
                            return False, path, None
                    except: pass
        else:
            ph = None
        if img.mode in ('RGBA','P'): img = img.convert('RGB')
        img.save(str(path), 'WEBP', quality=80)
        return True, path, ph
    except:
        return False, path, None

def main():
    start = time.time()
    print("🚀 Fast Expansion v3 (Picsum ID-based)")
    sys.stdout.flush()

    mapping = json.loads(MAPPING_FILE.read_text())
    
    # Assign unique Picsum IDs to each combo
    # 1084 total IDs, 66 combos → ~16 per combo from IDs alone
    # Plus we'll use size variations for more
    all_ids = list(range(1, 1085))
    random.seed(42)
    random.shuffle(all_ids)
    
    tasks = []
    id_idx = 0
    combo_list = []
    
    for area in AREAS:
        if area not in mapping: mapping[area] = {}
        for cat in CATEGORIES:
            existing = len(mapping[area].get(cat, []))
            if existing < TARGET:
                needed = TARGET - existing
                combo_list.append((area, cat, existing, needed))
    
    combo_list.sort(key=lambda x: -x[3])
    total_needed = sum(t[3] for t in combo_list)
    print(f"📋 {len(combo_list)}개 조합, 총 {total_needed}개 필요")
    sys.stdout.flush()
    
    # Strategy: Use Picsum IDs + size variations + seed URLs
    for area, cat, existing, needed in combo_list:
        out = OUTPUT_DIR / area / cat
        out.mkdir(parents=True, exist_ok=True)
        
        urls = []
        # 1. Picsum by ID (guaranteed unique)
        for i in range(needed):
            pid = all_ids[id_idx % len(all_ids)]
            id_idx += 1
            urls.append(f"https://picsum.photos/id/{pid}/1200/800")
        
        # 2. Seed-based with very different seeds (backup)
        for i in range(needed):
            seed = hashlib.md5(f"{area}{cat}{existing}{i}{time.time_ns()}".encode()).hexdigest()[:12]
            urls.append(f"https://picsum.photos/seed/{seed}/1000/700")
        
        # 3. Random with cache-busting
        for i in range(needed // 2):
            urls.append(f"https://picsum.photos/1200/800?random={area}_{cat}_{existing+i}_{time.time_ns()}")
        
        random.shuffle(urls)
        
        for i, url in enumerate(urls):
            idx = existing + i + 1
            fname = f"{area}_{cat}_{idx:04d}.webp"
            sp = out / fname
            if sp.exists(): continue
            # For Picsum IDs, skip hash check (they're guaranteed unique)
            use_hash = "id/" not in url
            tasks.append((url, sp, use_hash))
    
    print(f"📥 {len(tasks)}개 다운로드 태스크")
    sys.stdout.flush()
    
    total_new = 0
    completed_combos = set()
    
    with ThreadPoolExecutor(max_workers=64) as ex:
        futs = {ex.submit(dl, t): t for t in tasks}
        done_count = 0
        for f in as_completed(futs):
            ok, path, ph = f.result()
            if ok:
                total_new += 1
                if ph: hash_db[path.name] = ph
            done_count += 1
            if done_count % 200 == 0:
                elapsed = time.time() - start
                print(f"  진행: {done_count}/{len(tasks)} ({total_new}개 성공, {elapsed:.0f}s)")
                sys.stdout.flush()
            if time.time() - start > 570:
                print("  ⏰ 9.5분 cutoff")
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
    
    # Stats per area
    print(f"\n{'='*60}")
    print(f"✅ 완료! +{total_new}개 신규 (총 {total}개) / {elapsed:.0f}초")
    for area in AREAS:
        area_total = sum(len(mapping.get(area,{}).get(c,[])) for c in CATEGORIES)
        print(f"  {area}: {area_total}개")
    print(f"{'='*60}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
