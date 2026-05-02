#!/usr/bin/env python3
"""
실제 발리 이미지 다운로더 v2
- Openverse API + Flickr + Wikimedia
- 기존 Picsum 이미지에 추가 (덮어쓰기 아님)
- MD5 + pHash 중복 제거
- 11지역 × 6카테고리 × 목표 150장
"""
import os, sys, json, hashlib, time, requests
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
FILE_HASH_DB = BASE_DIR / "file_hashes.json"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
PROGRESS_FILE = BASE_DIR / "SCRAPER_PROGRESS.txt"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]

SEARCH_KEYWORDS = {
    "우붓": {
        "food": ["ubud bali food", "ubud restaurant", "babi guling ubud", "ubud warung", "ubud cafe bali", "bali cooking ubud", "nasi goreng ubud", "ubud smoothie bowl"],
        "culture": ["ubud temple bali", "monkey forest ubud", "ubud palace", "kecak dance ubud", "ubud art market", "taman saraswati ubud"],
        "beach": ["campuhan ridge ubud", "tibumana waterfall", "ubud river valley", "bali rice terrace ubud", "kanto lampo waterfall"],
        "nature": ["tegalalang rice terrace", "ubud monkey forest", "campuhan ridge walk", "ubud rice paddy", "ubud jungle bali"],
        "shopping": ["ubud art market bali", "ubud traditional market", "ubud craft market", "bali wood carving ubud"],
        "transport": ["ubud bali street", "bali motorbike ubud", "ubud road bali", "bali driver ubud"],
    },
    "스미냑": {
        "food": ["seminyak restaurant bali", "seminyak beach club", "potato head bali", "seminyak cafe", "bali seafood seminyak"],
        "culture": ["petitenget temple bali", "seminyak ceremony", "bali offering seminyak"],
        "beach": ["seminyak beach bali", "double six beach", "seminyak sunset", "seminyak surf"],
        "nature": ["seminyak rice field", "seminyak tropical garden", "bali nature seminyak"],
        "shopping": ["seminyak boutique bali", "seminyak spa", "bali fashion seminyak"],
        "transport": ["seminyak street bali", "seminyak road motorbike"],
    },
    "꾸따": {
        "food": ["kuta bali restaurant", "kuta beach food", "bali street food kuta", "kuta warung", "legian food bali"],
        "culture": ["kuta temple bali", "bali ceremony kuta", "kuta art"],
        "beach": ["kuta beach bali", "kuta surfing", "kuta sunset", "waterbom bali", "legian beach"],
        "nature": ["kuta beach nature", "kuta ocean wave", "bali sunset kuta"],
        "shopping": ["kuta market bali", "discovery mall bali", "kuta beachwalk", "bali souvenir kuta"],
        "transport": ["kuta street bali", "kuta traffic", "bali airport kuta"],
    },
    "사누르": {
        "food": ["sanur restaurant bali", "sanur seafood", "sanur cafe bali", "bali warung sanur"],
        "culture": ["sanur temple bali", "le mayeur museum", "sanur ceremony"],
        "beach": ["sanur beach bali", "sanur sunrise", "sanur boardwalk", "sanur harbor"],
        "nature": ["sanur mangrove bali", "sanur nature garden"],
        "shopping": ["sanur market bali", "sanur night market"],
        "transport": ["sanur cycling bali", "sanur harbor boat"],
    },
    "누사두아": {
        "food": ["nusa dua restaurant", "nusa dua resort dining", "bali seafood nusa dua"],
        "culture": ["nusa dua temple", "devdan show bali", "nusa dua ceremony"],
        "beach": ["nusa dua beach bali", "water blow nusa dua", "nusa dua snorkeling"],
        "nature": ["nusa dua tropical garden", "nusa dua marine bali"],
        "shopping": ["bali collection mall", "nusa dua shopping"],
        "transport": ["nusa dua road bali", "nusa dua taxi"],
    },
    "울루와뚜": {
        "food": ["uluwatu restaurant", "uluwatu beach club", "single fin uluwatu"],
        "culture": ["uluwatu temple bali", "kecak dance uluwatu", "uluwatu ceremony"],
        "beach": ["uluwatu beach bali", "uluwatu surf", "uluwatu cliff", "padang padang beach"],
        "nature": ["uluwatu cliff bali", "uluwatu ocean view", "uluwatu sunset"],
        "shopping": ["uluwatu souvenir bali"],
        "transport": ["uluwatu road bali"],
    },
    "짠디다사": {
        "food": ["candidasa restaurant bali", "candidasa seafood"],
        "culture": ["tirta gangga bali", "besakih temple bali", "candidasa temple"],
        "beach": ["candidasa beach bali", "amed beach bali", "padang bai bali"],
        "nature": ["candidasa nature bali", "east bali nature"],
        "shopping": ["candidasa market bali"],
        "transport": ["candidasa road bali"],
    },
    "로비나": {
        "food": ["lovina restaurant bali", "lovina seafood north bali"],
        "culture": ["lovina temple bali", "singaraja bali"],
        "beach": ["lovina beach bali", "lovina dolphin", "lovina sunrise"],
        "nature": ["gitgit waterfall bali", "banjar hot spring bali", "lovina nature"],
        "shopping": ["lovina market bali", "singaraja market"],
        "transport": ["lovina road bali", "north bali road"],
    },
    "킨타마니": {
        "food": ["kintamani restaurant bali", "kintamani coffee", "mount batur view"],
        "culture": ["kintamani temple bali", "batur temple", "trunyan bali"],
        "beach": ["batur lake bali", "kintamani crater lake"],
        "nature": ["mount batur volcano", "kintamani sunrise", "batur trekking"],
        "shopping": ["kintamani market bali", "bali highland market"],
        "transport": ["kintamani road bali", "mount batur trek"],
    },
    "타나롯": {
        "food": ["tanah lot restaurant", "tanah lot cafe bali"],
        "culture": ["tanah lot temple bali", "tanah lot ceremony", "batu bolong temple"],
        "beach": ["tanah lot beach bali", "tanah lot rock ocean", "tanah lot sunset"],
        "nature": ["tanah lot sunset bali", "tanah lot rice field"],
        "shopping": ["tanah lot souvenir bali"],
        "transport": ["tanah lot road bali"],
    },
    "베두굴": {
        "food": ["bedugul restaurant bali", "bedugul strawberry"],
        "culture": ["ulun danu bratan temple", "bedugul temple bali"],
        "beach": ["bratan lake bali", "bedugul lake"],
        "nature": ["bedugul botanical garden", "bali highland bedugul"],
        "shopping": ["candi kuning market", "bedugul fruit market"],
        "transport": ["bedugul road bali"],
    },
}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def md5(data):
    return hashlib.md5(data).hexdigest()

def phash(img):
    try:
        s = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        px = list(s.getdata())
        avg = sum(px) / len(px)
        return ''.join('1' if p > avg else '0' for p in px)
    except:
        return None

def hamming(a, b):
    if not a or not b or len(a) != len(b): return 999
    return sum(x != y for x, y in zip(a, b))

def search_images(query, page=1):
    """Openverse API 검색"""
    try:
        r = requests.get('https://api.openverse.org/v1/images/',
            params={'q': query, 'page_size': 30, 'page': page,
                    'license': 'by,by-sa,cc0,pdm'},
            headers={'User-Agent': 'JPTravel-Bali-Scraper/1.0'},
            timeout=25)
        if r.status_code == 200:
            return r.json().get('results', [])
        elif r.status_code == 429:
            log(f"  ⏳ Rate limited, waiting 10s...")
            time.sleep(10)
            return search_images(query, page)
    except Exception as e:
        log(f"  ⚠️ Search error: {e}")
    return []

def download(url):
    """이미지 다운로드"""
    try:
        r = requests.get(url, headers={'User-Agent': 'JPTravel-Bali-Scraper/1.0'}, timeout=20)
        if r.status_code == 200:
            return r.content
    except:
        pass
    return None

def to_webp(data, min_w=800, min_h=500):
    """WebP 변환"""
    try:
        img = Image.open(BytesIO(data))
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        w, h = img.size
        if w < min_w or h < min_h:
            return None, None
        if w > 2400 or h > 1600:
            ratio = min(2400/w, 1600/h)
            img = img.resize((int(w*ratio), int(h*ratio)), Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='WEBP', quality=85, method=4)
        return buf.getvalue(), img
    except:
        return None, None

def main():
    log("=" * 60)
    log("🚀 실제 발리 이미지 다운로더 v2 시작")
    log("=" * 60)

    # Load existing data
    all_hashes = json.loads(FILE_HASH_DB.read_text()) if FILE_HASH_DB.exists() else {}
    mapping = json.loads(MAPPING_FILE.read_text()) if MAPPING_FILE.exists() else {}
    existing_md5s = set(all_hashes.values())

    total_new = 0

    for area in AREAS:
        log(f"\n🌍 {area}")
        kws = SEARCH_KEYWORDS.get(area, SEARCH_KEYWORDS["우붓"])

        for cat in CATEGORIES:
            d = OUTPUT_DIR / area / cat
            d.mkdir(parents=True, exist_ok=True)
            cur = len(list(d.glob('*.webp')))
            target = 150
            needed = max(0, target - cur)

            if needed <= 0:
                log(f"  ⏭️ {area}/{cat}: {cur}장 OK")
                continue

            log(f"  🔍 {area}/{cat}: {needed}장 필요 (현재 {cur})")

            # 기존 pHashes
            eph = []
            for f in list(d.glob('*.webp'))[:80]:
                try:
                    h = phash(Image.open(f))
                    if h: eph.append(h)
                except: pass

            collected = 0
            seen = set()
            keywords = kws.get(cat, [f"bali {cat}"])

            for kw in keywords:
                if collected >= needed: break
                for pg in range(1, 5):
                    if collected >= needed: break
                    results = search_images(kw, pg)
                    time.sleep(2)
                    if not results: break

                    for item in results:
                        if collected >= needed: break
                        url = item.get('url', '')
                        if not url or url in seen: continue
                        seen.add(url)

                        raw = download(url)
                        if not raw: continue

                        webp, img = to_webp(raw)
                        if not webp: continue

                        h = md5(webp)
                        if h in existing_md5s: continue

                        p = phash(img)
                        dup = False
                        if p:
                            for ep in eph:
                                if hamming(p, ep) <= 5:
                                    dup = True; break
                        if dup: continue

                        # Save
                        num = len(list(d.glob('*.webp'))) + 1
                        fn = f"{area}_{cat}_{num:04d}.webp"
                        fp = d / fn
                        fp.write_bytes(webp)

                        all_hashes[str(fp)] = h
                        existing_md5s.add(h)
                        if p: eph.append(p)

                        if area not in mapping: mapping[area] = {}
                        if cat not in mapping[area]: mapping[area][cat] = []
                        mapping[area][cat].append(fn)

                        collected += 1
                        total_new += 1
                        src = item.get('source', '?')
                        ttl = (item.get('title') or '')[:35]
                        log(f"    ✅ {fn} [{src}] {ttl}")

                        if collected % 10 == 0:
                            FILE_HASH_DB.write_text(json.dumps(all_hashes, ensure_ascii=False, indent=2))
                            MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

                        time.sleep(0.5)

            FILE_HASH_DB.write_text(json.dumps(all_hashes, ensure_ascii=False, indent=2))
            MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
            log(f"  📊 {area}/{cat}: +{collected}장 (총 {cur + collected})")

    log("\n" + "=" * 60)
    log(f"✅ 완료! 신규 {total_new}장")
    total = sum(len(v) for cats in mapping.values() for v in cats.values())
    log(f"   총 이미지: {total}장")
    log("=" * 60)

if __name__ == '__main__':
    main()
