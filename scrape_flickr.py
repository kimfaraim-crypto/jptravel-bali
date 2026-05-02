#!/usr/bin/env python3
"""
Flickr 공개 피드 기반 발리 이미지 스크래퍼
- API 키 불필요
- 태그 기반 검색
- 다운로드 → WebP 변환 → 중복 제거
"""
import os, json, hashlib, time, requests, re
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime

BASE = Path(__file__).parent
IMG_DIR = BASE / "output" / "images"
HASH_DB = BASE / "file_hashes.json"
MAP_FILE = BASE / "image_mapping_v3.json"
LOG_FILE = BASE / "SCRAPER_PROGRESS.txt"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

# Flickr 태그 조합 (지역 + 카테고리)
FLICKR_TAGS = {
    "우붓": {
        "food": ["ubud,bali,food", "ubud,bali,restaurant", "ubud,bali,warung", "ubud,bali,coffee", "bali,babi guling", "ubud,smoothie", "bali,nasi goreng", "ubud,dining"],
        "culture": ["ubud,bali,temple", "ubud,bali,monkey", "ubud,bali,dance", "ubud,bali,art", "ubud,bali,ceremony", "ubud,bali,offering", "bali,kecak,ubud"],
        "beach": ["ubud,bali,river", "ubud,bali,waterfall", "ubud,bali,ridge", "ubud,bali,rice", "bali,campuhan", "ubud,jungle"],
        "nature": ["ubud,bali,rice terrace", "tegalalang,bali", "ubud,bali,nature", "ubud,bali,monkey forest", "ubud,bali,field", "bali,rice paddy,ubud"],
        "shopping": ["ubud,bali,market", "ubud,bali,craft", "ubud,bali,art market", "bali,souvenir,ubud", "ubud,shopping"],
        "transport": ["ubud,bali,street", "ubud,bali,road", "bali,motorbike,ubud", "bali,scooter,ubud"],
    },
    "스미냑": {
        "food": ["seminyak,bali,restaurant", "seminyak,bali,food", "seminyak,bali,cafe", "potato head,bali", "seminyak,seafood"],
        "culture": ["seminyak,bali,temple", "petitenget,bali", "bali,ceremony,seminyak"],
        "beach": ["seminyak,bali,beach", "double six beach,bali", "seminyak,bali,sunset", "seminyak,surf"],
        "nature": ["seminyak,bali,nature", "seminyak,bali,garden"],
        "shopping": ["seminyak,bali,boutique", "seminyak,bali,spa", "seminyak,shopping"],
        "transport": ["seminyak,bali,street", "seminyak,bali,road"],
    },
    "꾸따": {
        "food": ["kuta,bali,food", "kuta,bali,restaurant", "bali,street food,kuta", "kuta,bali,warung"],
        "culture": ["kuta,bali,temple", "bali,ceremony,kuta"],
        "beach": ["kuta,bali,beach", "kuta,bali,surf", "kuta,bali,sunset", "waterbom,bali", "legian,beach"],
        "nature": ["kuta,bali,ocean", "kuta,bali,wave"],
        "shopping": ["kuta,bali,market", "discovery mall,bali", "kuta,beachwalk"],
        "transport": ["kuta,bali,street", "kuta,bali,airport"],
    },
    "사누르": {
        "food": ["sanur,bali,food", "sanur,bali,seafood", "sanur,bali,cafe"],
        "culture": ["sanur,bali,temple", "sanur,bali,museum"],
        "beach": ["sanur,bali,beach", "sanur,bali,sunrise", "sanur,boardwalk"],
        "nature": ["sanur,bali,mangrove", "sanur,bali,nature"],
        "shopping": ["sanur,bali,market", "sanur,night market"],
        "transport": ["sanur,bali,cycling", "sanur,bali,harbor"],
    },
    "누사두아": {
        "food": ["nusa dua,bali,food", "nusa dua,bali,restaurant"],
        "culture": ["nusa dua,bali,temple", "nusa dua,bali,show"],
        "beach": ["nusa dua,bali,beach", "nusa dua,bali,snorkeling", "water blow,bali"],
        "nature": ["nusa dua,bali,garden", "nusa dua,bali,marine"],
        "shopping": ["nusa dua,bali,shopping", "bali collection"],
        "transport": ["nusa dua,bali,road"],
    },
    "울루와뚜": {
        "food": ["uluwatu,bali,restaurant", "uluwatu,bali,cafe", "single fin,uluwatu"],
        "culture": ["uluwatu,bali,temple", "uluwatu,kecak", "uluwatu,bali,ceremony"],
        "beach": ["uluwatu,bali,beach", "uluwatu,bali,surf", "uluwatu,bali,cliff", "padang padang,bali"],
        "nature": ["uluwatu,bali,cliff", "uluwatu,bali,ocean", "uluwatu,bali,sunset"],
        "shopping": ["uluwatu,bali,souvenir"],
        "transport": ["uluwatu,bali,road"],
    },
    "짠디다사": {
        "food": ["candidasa,bali,food", "candidasa,bali,seafood"],
        "culture": ["tirta gangga,bali", "besakih,bali,temple", "candidasa,bali,temple"],
        "beach": ["candidasa,bali,beach", "amed,bali,beach", "padang bai,bali"],
        "nature": ["candidasa,bali,nature", "east bali,nature"],
        "shopping": ["candidasa,bali,market"],
        "transport": ["candidasa,bali,road"],
    },
    "로비나": {
        "food": ["lovina,bali,food", "lovina,bali,seafood"],
        "culture": ["lovina,bali,temple", "singaraja,bali"],
        "beach": ["lovina,bali,beach", "lovina,bali,dolphin", "lovina,bali,sunrise"],
        "nature": ["gitgit,bali,waterfall", "banjar,bali,hot spring", "lovina,bali,nature"],
        "shopping": ["lovina,bali,market"],
        "transport": ["lovina,bali,road"],
    },
    "킨타마니": {
        "food": ["kintamani,bali,food", "kintamani,bali,coffee", "mount batur,view"],
        "culture": ["kintamani,bali,temple", "batur,temple,bali"],
        "beach": ["batur lake,bali", "kintamani,crater"],
        "nature": ["mount batur,bali", "kintamani,bali,volcano", "batur,sunrise", "kintamani,trekking"],
        "shopping": ["kintamani,bali,market"],
        "transport": ["kintamani,bali,road"],
    },
    "타나롯": {
        "food": ["tanah lot,bali,food", "tanah lot,bali,restaurant"],
        "culture": ["tanah lot,bali,temple", "tanah lot,ceremony", "batu bolong,bali"],
        "beach": ["tanah lot,bali,beach", "tanah lot,bali,rock", "tanah lot,bali,sunset"],
        "nature": ["tanah lot,bali,sunset", "tanah lot,bali,rice"],
        "shopping": ["tanah lot,bali,souvenir"],
        "transport": ["tanah lot,bali,road"],
    },
    "베두굴": {
        "food": ["bedugul,bali,food", "bedugul,bali,strawberry"],
        "culture": ["ulun danu,bali", "bedugul,bali,temple", "bratan lake,temple"],
        "beach": ["bratan lake,bali", "bedugul,bali,lake"],
        "nature": ["bedugul,botanical garden", "bedugul,bali,nature", "bali,highland"],
        "shopping": ["candi kuning market", "bedugul,bali,market"],
        "transport": ["bedugul,bali,road"],
    },
}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
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

def flickr_feed(tags, max_retries=2):
    """Flickr 공개 피드에서 이미지 URL 가져오기"""
    for attempt in range(max_retries):
        try:
            r = requests.get('https://api.flickr.com/services/feeds/photos_public.gne',
                params={'tags': tags, 'tagmode': 'all', 'format': 'json', 'nojsoncallback': 1},
                headers={'User-Agent': 'Mozilla/5.0 (Bali Blog)'},
                timeout=15)
            if r.status_code == 200:
                items = r.json().get('items', [])
                urls = []
                for item in items:
                    media = item.get('media', {}).get('m', '')
                    # _m = small, _b = large (1024), _c = medium (800), _z = 640
                    large = media.replace('_m.', '_b.')
                    if large:
                        urls.append({'url': large, 'title': item.get('title', ''), 'source': 'flickr'})
                return urls
        except:
            time.sleep(2)
    return []

def download(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Bali Blog)'}, timeout=20)
        if r.status_code == 200:
            return r.content
    except:
        pass
    return None

def to_webp(data, min_w=800, min_h=500):
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
    log("🚀 Flickr 피드 기반 발리 이미지 스크래퍼")
    log("=" * 60)

    hashes = json.loads(HASH_DB.read_text()) if HASH_DB.exists() else {}
    mapping = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}
    existing_md5s = set(hashes.values())
    total_new = 0

    for area in AREAS:
        log(f"\n🌍 {area}")
        tags_by_cat = FLICKR_TAGS.get(area, {})

        for cat in ["food", "culture", "beach", "nature", "shopping", "transport"]:
            d = IMG_DIR / area / cat
            d.mkdir(parents=True, exist_ok=True)
            cur = len(list(d.glob('*.webp')))
            target = 150
            needed = max(0, target - cur)

            if needed <= 0:
                log(f"  ⏭️ {area}/{cat}: {cur}장 OK")
                continue

            log(f"  🔍 {area}/{cat}: +{needed}장 필요")

            # 기존 pHashes
            eph = []
            for f in list(d.glob('*.webp'))[:100]:
                try:
                    h = phash(Image.open(f))
                    if h: eph.append(h)
                except: pass

            collected = 0
            seen_urls = set()
            tag_list = tags_by_cat.get(cat, [f"bali,{cat}"])

            for tags in tag_list:
                if collected >= needed: break

                items = flickr_feed(tags)
                time.sleep(1)

                for item in items:
                    if collected >= needed: break
                    url = item['url']
                    if url in seen_urls: continue
                    seen_urls.add(url)

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

                    num = len(list(d.glob('*.webp'))) + 1
                    fn = f"{area}_{cat}_{num:04d}.webp"
                    fp = d / fn
                    fp.write_bytes(webp)

                    hashes[str(fp)] = h
                    existing_md5s.add(h)
                    if p: eph.append(p)

                    if area not in mapping: mapping[area] = {}
                    if cat not in mapping[area]: mapping[area][cat] = []
                    mapping[area][cat].append(fn)

                    collected += 1
                    total_new += 1
                    ttl = item.get('title', '')[:35]
                    log(f"    ✅ {fn} [{ttl}]")

                    time.sleep(0.3)

            # Save periodically
            HASH_DB.write_text(json.dumps(hashes, ensure_ascii=False, indent=2))
            MAP_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
            log(f"  📊 {area}/{cat}: +{collected} → {cur + collected}장")

    log("\n" + "=" * 60)
    log(f"✅ 완료! 신규 {total_new}장")
    total = sum(len(v) for cats in mapping.values() for v in cats.values())
    log(f"   총 이미지: {total}장")
    log("=" * 60)

if __name__ == '__main__':
    main()
