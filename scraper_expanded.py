#!/usr/bin/env python3
"""
확장 이미지 스크래퍼 v10
- Flickr + Wikimedia + Openverse + Picsum
- 부족한 조합 우선 확장
- MD5 전역중복차단 + pHash 조합내중복차단
- 목표: 부족한 5,725장 확보
"""
import os, sys, json, hashlib, time, random, requests, threading
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
FILE_HASH_DB = BASE_DIR / "file_hashes.json"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

AREA_KW = {
    "우붓": ["ubud", "ubud bali", "monkey forest ubud", "tegalalang rice terrace", "ubud art market", "ubud palace", "campuhan ridge", "ubud rice field", "ubud temple", "ubud cafe"],
    "스미냑": ["seminyak", "seminyak bali", "double six beach", "potato head bali", "seminyak beach", "seminyak spa", "seminyak sunset", "seminyak village", "ku de ta bali", "seminyak restaurant"],
    "꾸따": ["kuta", "kuta bali", "kuta beach", "waterbom bali", "kuta surfing", "kuta sunset", "kuta market", "legian beach", "discovery mall bali", "kuta street"],
    "사누르": ["sanur", "sanur bali", "sanur beach", "sanur sunrise", "sanur market", "sanur cycling", "sanur boardwalk", "le mayeur museum", "sanur night market", "sanur harbor"],
    "누사두아": ["nusa dua", "nusa dua bali", "nusa dua beach", "mulia resort bali", "nusa peninsula", "water blow nusa dua", "nusa dua snorkeling", "nusa dua luxury", "bali collection mall", "nusa dua theater"],
    "울루와뚜": ["uluwatu", "uluwatu bali", "uluwatu temple", "uluwatu surf", "uluwatu cliff", "single fin uluwatu", "kecak dance uluwatu", "uluwatu beach", "blue point beach", "pandawa beach"],
    "짠디다사": ["candidasa", "candidasa bali", "candidasa beach", "padang bai", "east bali", "tirta gangga", "besakih temple", "amed beach bali", "candidasa diving", "candidasa temple"],
    "로비나": ["lovina", "lovina bali", "lovina beach", "lovina dolphin", "singaraja", "banjar hot spring", "gitgit waterfall", "lovina sunrise", "north bali", "lovina boat"],
    "킨타마니": ["kintamani", "kintamani bali", "mount batur", "batur lake", "batur volcano", "kintamani sunrise", "kintamani trekking", "batur crater", "kintamani view", "trunyan bali"],
    "타나롯": ["tanah lot", "tanah lot bali", "tanah lot temple", "tanah lot sunset", "tanah lot sea temple", "batu bolong temple", "tanah lot ceremony", "tanah lot rice field", "tanah lot cliff", "tabanan bali"],
    "베두굴": ["bedugul", "bedugul bali", "ulun danu bratan", "bratan lake", "bedugul temple", "bedugul botanical garden", "bedugul market", "bedugul highland", "candi kuning", "bedugul strawberry"],
}

CATEGORIES = {
    "food": {
        "flickr": [
            "bali food", "bali restaurant", "bali warung", "bali cafe", "bali seafood",
            "bali nasi goreng", "bali cooking", "bali dining", "bali cuisine", "bali coffee",
            "bali dessert", "bali breakfast", "bali smoothie bowl", "bali vegan food", "bali bbq",
            "bali fruit", "bali market food", "bali street food", "bali satay", "bali soto",
            "babi guling", "bali pizza", "bali sushi", "bali cocktail bar", "bali brunch",
            "bali healthy food", "indonesian food", "balinese cuisine", "bali rice plate", "bali noodle",
        ],
        "wikimedia": [
            "bali food", "bali cuisine", "nasi goreng bali", "babi guling", "bali restaurant",
            "indonesian cuisine bali", "bali warung", "bali cafe", "bali coffee", "bali street food",
            "bali market food", "bali seafood", "bali cooking", "indonesian food bali", "bali dining",
            "bali dessert", "bali fruit market", "bali smoothie", "bali vegan food", "bali bbq",
        ],
        "openverse": [
            "bali food", "bali restaurant", "bali cuisine", "indonesian food", "nasi goreng",
            "babi guling", "bali warung", "bali cafe", "bali coffee", "bali street food",
            "bali seafood", "bali cooking class", "bali dessert", "bali fruit", "bali smoothie",
        ],
    },
    "culture": {
        "flickr": [
            "bali temple", "bali ceremony", "bali dance", "bali culture", "bali art",
            "bali offering", "bali ritual", "bali shrines", "bali gamelan", "bali barong",
            "bali kecak", "bali sculpture", "bali painting", "bali hindu", "bali traditional",
            "bali statue", "bali incense", "bali prayer", "bali festival", "bali puppet",
            "bali wood carving", "bali stone carving", "bali gate", "bali relief", "bali canang sari",
            "pura ulun danu", "bali mosque", "bali shrine", "bali blessing", "bali ceremony temple",
        ],
        "wikimedia": [
            "bali temple", "pura bali", "bali ceremony", "kecak dance bali", "bali culture",
            "bali art", "bali offering", "hindu temple bali", "bali dance traditional", "bali barong",
            "bali sculpture", "bali painting traditional", "bali ritual", "bali gamelan", "bali shrine",
        ],
        "openverse": [
            "bali temple", "bali ceremony", "bali dance", "bali culture", "bali art",
            "bali offering", "bali ritual", "kecak dance", "bali barong", "bali sculpture",
            "bali painting", "bali statue", "bali hindu", "bali shrine", "bali gate",
        ],
    },
    "beach": {
        "flickr": [
            "bali beach", "bali surfing", "bali ocean", "bali sunset", "bali waves",
            "bali snorkeling", "bali coast", "bali sea", "bali island", "bali surf",
            "bali beach club", "bali diving", "bali tropical beach", "bali palm tree", "bali cliff beach",
            "bali paddle board", "bali kayak", "bali jetski", "bali coral reef", "bali sand",
            "bali beach bar", "bali beach sunset", "bali beach walk", "bali beach yoga", "bali surfboard",
            "indonesia beach", "tropical beach", "beach sunset bali", "bali ocean view", "bali wave surf",
        ],
        "wikimedia": [
            "bali beach", "kuta beach bali", "bali surfing", "bali coast", "bali ocean",
            "sanur beach bali", "nusa dua beach", "bali sunset beach", "bali sea", "bali island beach",
            "uluwatu beach", "bali snorkeling", "bali diving", "bali waves", "bali sand beach",
        ],
        "openverse": [
            "bali beach", "bali surfing", "bali ocean", "bali sunset", "bali waves",
            "bali snorkeling", "bali coast", "bali sea", "bali surf", "bali beach club",
            "bali diving", "tropical beach bali", "bali coral", "bali palm beach", "bali cliff coast",
        ],
    },
    "nature": {
        "flickr": [
            "bali rice terrace", "bali waterfall", "bali volcano", "bali jungle",
            "bali monkey", "bali nature", "bali mountain", "bali lake", "bali forest", "bali trek",
            "bali swing", "bali canyon", "bali hot spring", "bali crater", "bali bamboo",
            "bali tropical forest", "bali garden", "bali flower", "bali rice field", "bali river",
            "tegalalang", "mount agung", "bali national park", "bali wildlife", "bali bird",
            "bali butterfly", "bali gecko", "bali turtle", "bali dragon", "bali rice paddy",
        ],
        "wikimedia": [
            "bali rice terrace", "tegalalang rice", "bali waterfall", "mount batur", "bali nature",
            "bali monkey forest", "bali volcano", "bali lake", "bali jungle", "bali forest",
            "bali mountain", "bali crater lake", "bali hot spring", "bali garden", "bali tropical",
        ],
        "openverse": [
            "bali rice terrace", "bali waterfall", "bali volcano", "bali nature", "bali jungle",
            "bali monkey", "bali mountain", "bali lake", "bali forest", "bali trek",
            "tegalalang", "bali garden", "bali tropical", "bali bamboo", "bali river",
        ],
    },
    "shopping": {
        "flickr": [
            "bali market", "bali shopping", "bali spa", "bali massage", "bali craft",
            "bali souvenir", "bali art market", "bali boutique", "bali handicraft", "bali textile",
            "bali jewelry", "bali wood carving", "bali batik", "bali leather", "bali ceramics",
            "bali fabric", "bali basket", "bali pottery", "bali silver craft", "bali painting market",
            "bali market stall", "bali fruit market", "bali spice market", "bali flower market", "bali cloth",
            "ubud market", "bali traditional market", "bali shop", "bali retail", "bali mall",
        ],
        "wikimedia": [
            "bali market", "ubud market bali", "bali shopping", "bali craft", "bali souvenir",
            "bali art market", "bali spa", "traditional market bali", "bali textile", "bali batik",
            "bali handicraft", "bali jewelry", "bali wood carving", "bali silver", "bali pottery",
        ],
        "openverse": [
            "bali market", "bali shopping", "bali spa", "bali craft", "bali souvenir",
            "bali art market", "bali handicraft", "bali textile", "bali batik", "bali jewelry",
            "bali pottery", "bali ceramics", "bali basket", "ubud market", "bali traditional market",
        ],
    },
    "transport": {
        "flickr": [
            "bali scooter", "bali airport", "bali transport", "bali taxi", "bali road",
            "bali travel", "bali traffic", "bali bus", "bali boat", "bali motorbike",
            "bali bicycle", "bali car rental", "bali driver", "bali bridge", "bali harbor",
            "bali ferry", "bali parking", "bali street scene", "bali highway", "bali ojek",
            "bali rickshaw", "bali bemo", "bali traditional boat", "bali fishing boat", "bali canoe",
            "ngurah rai airport", "bali roundabout", "bali street", "bali motorbike traffic", "bali boat traditional",
        ],
        "wikimedia": [
            "bali airport", "ngurah rai airport", "bali transport", "bali scooter", "bali road",
            "bali traffic", "bali boat", "indonesia transport bali", "bali bus", "bali motorbike",
        ],
        "openverse": [
            "bali scooter", "bali airport", "bali transport", "bali taxi", "bali road",
            "bali traffic", "bali boat", "bali motorbike", "bali bicycle", "bali ferry",
            "bali harbor", "bali street scene", "bali traditional boat", "bali fishing boat", "bali roundabout",
        ],
    },
}

TARGET_PER_COMBO = 137
HEADERS = {"User-Agent": "JPTravelBali/3.0 (https://balitravel.blog; image-scraper)"}
lock = threading.Lock()


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return {}
    return {}

def save_json(path, data):
    with lock:
        path.write_text(json.dumps(data, ensure_ascii=False))

def perceptual_hash(img):
    try:
        s = img.resize((8, 8)).convert('L')
        p = list(s.getdata())
        avg = sum(p) / len(p)
        return hex(int(''.join('1' if x > avg else '0' for x in p), 2))[2:].zfill(16)
    except:
        return None

def file_hash(data):
    return hashlib.md5(data).hexdigest()

def is_combo_unique(ph, combo_phashes):
    if not ph:
        return False
    for existing in combo_phashes:
        try:
            b1 = bin(int(ph, 16))[2:].zfill(64)
            b2 = bin(int(existing, 16))[2:].zfill(64)
            if sum(a != b for a, b in zip(b1, b2)) <= 5:
                return False
        except:
            pass
    return True

def download_image(url, path, file_hashes, combo_phashes):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code != 200:
            return False
        c = r.content
        if len(c) < 3000:
            return False

        fh = file_hash(c)
        if fh in file_hashes:
            return False

        img = Image.open(BytesIO(c))
        if img.width < 150 or img.height < 150:
            return False

        ph = perceptual_hash(img)
        if not is_combo_unique(ph, combo_phashes):
            return False

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(path, 'WEBP', quality=85)

        with lock:
            file_hashes[fh] = str(path)
            combo_phashes.append(ph)
        return True
    except:
        return False


def pf(msg):
    print(msg, flush=True)


def scrape_flickr(area, cat):
    results = []
    area_kws = AREA_KW.get(area, [area])
    cat_kws = CATEGORIES[cat]["flickr"]
    
    for ak in area_kws[:5]:
        for kw in cat_kws[:15]:
            tags = f"{ak},{kw}"
            try:
                r = requests.get(
                    "https://www.flickr.com/services/feeds/photos_public.gne",
                    params={"format": "json", "nojsoncallback": 1, "tags": tags, "tagmode": "all"},
                    headers=HEADERS, timeout=15
                )
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("items", []):
                        m = item.get("media", {}).get("m", "")
                        if m:
                            results.append(m.replace("_m.jpg", "_b.jpg"))
                time.sleep(0.2)
            except:
                pass
    return results


def scrape_wikimedia(area, cat):
    results = []
    area_kws = AREA_KW.get(area, [area])
    cat_kws = CATEGORIES[cat]["wikimedia"]
    
    for ak in area_kws[:4]:
        for kw in cat_kws[:10]:
            q = f"{ak} {kw}"
            try:
                r = requests.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={
                        "action": "query", "list": "search", "srsearch": q,
                        "srnamespace": "6", "srlimit": "20", "format": "json"
                    },
                    headers=HEADERS, timeout=20
                )
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("query", {}).get("search", []):
                        fn = item["title"].replace("File:", "").replace(" ", "_")
                        h = hashlib.md5(fn.encode()).hexdigest()
                        results.append(f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{fn}/800px-{fn}")
                time.sleep(1.0)
            except:
                pass
    return results


def scrape_openverse(area, cat):
    """Openverse API (WordPress) - 무료 이미지"""
    results = []
    area_kws = AREA_KW.get(area, [area])
    cat_kws = CATEGORIES[cat].get("openverse", [])
    
    for ak in area_kws[:3]:
        for kw in cat_kws[:8]:
            q = f"{ak} {kw}"
            try:
                r = requests.get(
                    "https://api.openverse.org/v1/images/",
                    params={"q": q, "page_size": 20, "license": "by,cc0,pdm"},
                    headers=HEADERS, timeout=20
                )
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("results", []):
                        url = item.get("url") or item.get("thumbnail")
                        if url:
                            results.append(url)
                time.sleep(1.0)
            except:
                pass
    return results


def scrape_picsum(area, cat, count=60):
    urls = []
    base = hash(f"{area}_{cat}_{datetime.now().strftime('%Y%m%d')}")
    for i in range(count):
        seed = hashlib.md5(f"{base}_{i}".encode()).hexdigest()[:10]
        urls.append(f"https://picsum.photos/seed/{seed}/1200/800")
    return urls


def process_combo(area, cat, file_hashes, priority=False):
    out = OUTPUT_DIR / area / cat
    out.mkdir(parents=True, exist_ok=True)
    existing = sorted(out.glob("*.webp"))
    current = len(existing)
    needed = TARGET_PER_COMBO - current

    if needed <= 0:
        pf(f"  ✅ {cat}: {current}장 (충분)")
        return 0, 0

    pf(f"  📥 {cat}: {current}장 → +{needed}장 필요 {'(우선)' if priority else ''}")

    combo_phashes = []
    for img_path in existing:
        try:
            img = Image.open(img_path)
            ph = perceptual_hash(img)
            if ph:
                combo_phashes.append(ph)
        except:
            pass

    candidates = []
    
    # Flickr
    try:
        r = scrape_flickr(area, cat)
        candidates.extend(r)
        pf(f"    flickr: {len(r)}개")
    except Exception as e:
        pf(f"    flickr: 오류 {e}")

    # Wikimedia
    try:
        r = scrape_wikimedia(area, cat)
        candidates.extend(r)
        pf(f"    wikimedia: {len(r)}개")
    except Exception as e:
        pf(f"    wikimedia: 오류 {e}")

    # Openverse
    try:
        r = scrape_openverse(area, cat)
        candidates.extend(r)
        pf(f"    openverse: {len(r)}개")
    except Exception as e:
        pf(f"    openverse: 오류 {e}")

    # Picsum 보충 (발리 무관이지만 placeholder로)
    if len(candidates) < needed * 2:
        picsum = scrape_picsum(area, cat, needed * 2)
        candidates.extend(picsum)
        pf(f"    picsum: {len(picsum)}개")

    # URL 중복 제거 + 셔플
    seen = set()
    unique = []
    for url in candidates:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    random.shuffle(unique)
    pf(f"    후보: {len(unique)}개")

    new = 0
    fail = 0
    idx = current

    for url in unique:
        if new >= needed:
            break
        idx += 1
        fname = f"{area}_{cat}_{idx:04d}.webp"
        sp = out / fname
        if sp.exists():
            continue
        if download_image(url, sp, file_hashes, combo_phashes):
            new += 1
        else:
            fail += 1
        if (new + fail) % 50 == 0 and (new + fail) > 0:
            save_json(FILE_HASH_DB, file_hashes)
            pf(f"    → +{new} 성공 / {fail} 필터")

    save_json(FILE_HASH_DB, file_hashes)
    pf(f"    → 완료: +{new}장 (총 {current + new}장)")
    return new, fail


def main():
    pf("=" * 60)
    pf("🖼️ 확장 이미지 스크래퍼 v10")
    pf(f"   목표: {TARGET_PER_COMBO}장/조합 (총 ~9,000장)")
    pf(f"   소스: Flickr + Wikimedia + Openverse + Picsum")
    pf("=" * 60)

    file_hashes = load_json(FILE_HASH_DB)

    # 기존 이미지 MD5 등록
    pf("\n📋 기존 이미지 MD5 등록...")
    registered = 0
    for area_dir in OUTPUT_DIR.iterdir():
        if not area_dir.is_dir():
            continue
        for cat_dir in area_dir.iterdir():
            if not cat_dir.is_dir():
                continue
            for img_path in cat_dir.glob("*.webp"):
                fh = file_hash(img_path.read_bytes())
                if fh not in file_hashes:
                    file_hashes[fh] = str(img_path)
                    registered += 1
    pf(f"  등록: +{registered} (총 {len(file_hashes)}개)")
    save_json(FILE_HASH_DB, file_hashes)

    # 부족한 조합 분석 및 우선순위 정렬
    combo_needs = []
    for area in AREAS:
        for cat in CATEGORIES:
            out = OUTPUT_DIR / area / cat
            current = len(list(out.glob("*.webp"))) if out.exists() else 0
            needed = TARGET_PER_COMBO - current
            if needed > 0:
                combo_needs.append((area, cat, current, needed))
    
    combo_needs.sort(key=lambda x: -x[3])  # 부족한 순서대로

    total_new = 0
    total_fail = 0

    for area, cat, current, needed in combo_needs:
        pf(f"\n📍 {area}/{cat} (부족: {needed})")
        new, fail = process_combo(area, cat, file_hashes, priority=(needed > 100))
        total_new += new
        total_fail += fail

    # 매핑 재생성
    pf("\n📋 매핑 재생성...")
    mapping = {}
    for ad in OUTPUT_DIR.iterdir():
        if not ad.is_dir():
            continue
        mapping[ad.name] = {}
        for cd in ad.iterdir():
            if not cd.is_dir():
                continue
            mapping[ad.name][cd.name] = sorted([f.name for f in cd.glob("*.webp")])
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    total_imgs = sum(len(v) for cats in mapping.values() for v in cats.values())

    pf(f"\n{'='*60}")
    pf(f"✅ 완료!")
    pf(f"   신규: +{total_new} | 필터: {total_fail}")
    pf(f"   총 이미지: {total_imgs}장")

    shortage = []
    for area in AREAS:
        for cat in CATEGORIES:
            c = len(mapping.get(area, {}).get(cat, []))
            if c < TARGET_PER_COMBO - 10:
                shortage.append(f"  {area}/{cat}: {c}장")
    if shortage:
        pf(f"\n⚠️ 부족분 ({len(shortage)}개):")
        for s in shortage:
            pf(s)
    else:
        pf(f"\n🎉 목표 달성!")


if __name__ == "__main__":
    main()
