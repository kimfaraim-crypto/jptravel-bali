#!/usr/bin/env python3
"""
이미지 스크래퍼 v4 - 안정성 강화
Openverse + Flickr + Wikimedia + Picsum
"""
import os, sys, json, hashlib, time, requests
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
HASH_DB = BASE_DIR / "image_hashes.json"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
STATE_FILE = BASE_DIR / "scraper_state.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

CATEGORIES = {
    "food": ["bali food", "bali restaurant", "bali warung", "nasi goreng", "babi guling", "bali cafe"],
    "culture": ["bali temple", "bali ceremony", "bali dance", "bali culture", "bali art", "bali offering"],
    "beach": ["bali beach", "bali surfing", "bali ocean", "bali sunset", "bali waves", "bali snorkeling"],
    "nature": ["bali rice terrace", "bali waterfall", "bali volcano", "bali jungle", "bali monkey", "bali nature"],
    "shopping": ["bali market", "bali shopping", "bali spa", "bali massage", "bali craft", "bali souvenir"],
    "transport": ["bali scooter", "bali airport", "bali transport", "bali taxi", "bali road", "bali travel"],
}

AREA_KW = {
    "우붓": "ubud", "스미냑": "seminyak", "꾸따": "kuta",
    "사누르": "sanur", "누사두아": "nusa dua", "울루와뚜": "uluwatu",
    "짠디다사": "candidasa", "로비나": "lovina", "킨타마니": "kintamani",
    "타나롯": "tanah lot", "베두굴": "bedugul",
}

TARGET = 10  # 지역×카테고리당 목표
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}

def flush_print(msg):
    print(msg, flush=True)

def load_hashes():
    if HASH_DB.exists():
        return json.loads(HASH_DB.read_text())
    return {}

def save_hashes(h):
    HASH_DB.write_text(json.dumps(h, ensure_ascii=False))

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

def download(url, path, hashes):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, stream=True)
        if r.status_code != 200: return False
        c = r.content
        if len(c) < 3000: return False
        img = Image.open(BytesIO(c))
        if img.width < 150 or img.height < 150: return False
        dup, ph = is_dup(img, hashes)
        if dup: return False
        if img.mode in ('RGBA','P'): img = img.convert('RGB')
        img.save(path, 'WEBP', quality=85)
        hashes[path.name] = ph
        return True
    except:
        return False

def scrape_openverse(area, cat):
    results = []
    ak = AREA_KW.get(area, area)
    for kw in CATEGORIES[cat][:2]:
        q = f"{ak} {kw.split(' ',1)[-1]}"
        try:
            r = requests.get(f"https://api.openverse.org/v1/images/?q={requests.utils.quote(q)}&page_size=15", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                for item in r.json().get("results", []):
                    if item.get("url"):
                        results.append(item["url"])
            time.sleep(1.5)
        except: pass
    return results

def scrape_wikimedia(area, cat):
    results = []
    ak = AREA_KW.get(area, area)
    for kw in CATEGORIES[cat][:2]:
        q = f"{ak} {kw.split(' ',1)[-1]}"
        try:
            r = requests.get("https://commons.wikimedia.org/w/api.php", params={
                "action":"query","list":"search","srsearch":q,"srnamespace":"6","srlimit":"10","format":"json"
            }, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                for item in r.json().get("query",{}).get("search",[]):
                    fn = item["title"].replace("File:","").replace(" ","_")
                    h = hashlib.md5(fn.encode()).hexdigest()
                    results.append(f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{fn}/800px-{fn}")
            time.sleep(2)
        except: pass
    return results

def scrape_flickr(area, cat):
    results = []
    ak = AREA_KW.get(area, area)
    for kw in CATEGORIES[cat][:2]:
        q = f"{ak} {kw.split(' ',1)[-1]}"
        try:
            r = requests.get(f"https://www.flickr.com/services/feeds/photos_public.gne?format=json&nojsoncallback=1&tags={requests.utils.quote(q.replace(' ',','))}&tagmode=all", headers=HEADERS, timeout=10)
            if r.status_code == 200:
                txt = r.text
                if txt.startswith('jsonFlickrFeed('): txt = txt[15:-1]
                data = json.loads(txt)
                for item in data.get("items",[]):
                    m = item.get("media",{}).get("m","")
                    if m: results.append(m.replace("_m.jpg","_b.jpg"))
            time.sleep(0.5)
        except: pass
    return results

def main():
    flush_print("=" * 50)
    flush_print("🖼️ 이미지 스크래퍼 v4")
    flush_print("=" * 50)

    hashes = load_hashes()
    total_new = 0
    total_skip = 0

    for area in AREAS:
        flush_print(f"\n📍 {area}")
        ak = AREA_KW.get(area, area)
        for cat in CATEGORIES:
            out = OUTPUT_DIR / area / cat
            out.mkdir(parents=True, exist_ok=True)
            existing = list(out.glob("*.webp"))
            needed = TARGET - len(existing)
            if needed <= 0:
                flush_print(f"  ✅ {cat}: {len(existing)}개 (충분)")
                continue

            flush_print(f"  📥 {cat}: {len(existing)}개, {needed}개 필요")

            # 모든 소스에서 후보 수집
            candidates = []
            for name, fn in [("openverse", scrape_openverse), ("flickr", scrape_flickr), ("wikimedia", scrape_wikimedia)]:
                try:
                    r = fn(area, cat)
                    candidates.extend(r)
                    flush_print(f"    {name}: {len(r)}개")
                except Exception as e:
                    flush_print(f"    {name}: 오류 {e}")

            # Picsum fallback
            if len(candidates) < needed:
                for i in range(needed * 2):
                    seed = hashlib.md5(f"{area}_{cat}_{i}".encode()).hexdigest()[:8]
                    candidates.append(f"https://picsum.photos/seed/{seed}/1200/800")

            # 다운로드
            new = 0
            for url in candidates:
                if new >= needed: break
                idx = len(existing) + new + 1
                fname = f"{area}_{cat}_{idx:04d}.webp"
                sp = out / fname
                if sp.exists(): continue
                if download(url, sp, hashes):
                    new += 1
                    total_new += 1
                    if new % 5 == 0:
                        flush_print(f"    → {new}개 다운로드")
                else:
                    total_skip += 1
                if (new + total_skip) % 20 == 0:
                    save_hashes(hashes)
                time.sleep(0.2)

            flush_print(f"    → 완료: {new}개 신규")
            save_hashes(hashes)

    # 매핑 생성
    flush_print("\n📋 매핑 생성...")
    mapping = {}
    for ad in OUTPUT_DIR.iterdir():
        if not ad.is_dir(): continue
        mapping[ad.name] = {}
        for cd in ad.iterdir():
            if not cd.is_dir(): continue
            mapping[ad.name][cd.name] = sorted([f.name for f in cd.glob("*.webp")])
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

    total_imgs = sum(len(v) for cats in mapping.values() for v in cats.values())
    flush_print(f"\n✅ 완료! 신규: {total_new}, 스킵: {total_skip}, 총 이미지: {total_imgs}")

if __name__ == "__main__":
    main()
