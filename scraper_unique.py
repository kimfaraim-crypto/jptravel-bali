#!/usr/bin/env python3
"""
고유 이미지 스크래퍼 v9 — 실용적 전략
- 정확한 파일 해시(MD5)로 카테고리 간 중복 차단
- perceptual hash는 같은 조합 내에서만 중복 체크
- 목표: 9,000+ 고유 이미지
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
PHASH_DB = BASE_DIR / "phash_per_combo.json"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

AREA_KW = {
    "우붓": ["ubud", "ubud bali", "monkey forest ubud", "tegalalang rice", "ubud art"],
    "스미냑": ["seminyak", "seminyak bali", "double six beach", "potato head bali", "seminyak village"],
    "꾸따": ["kuta", "kuta bali", "kuta beach", "waterbom bali", "kuta surfing"],
    "사누르": ["sanur", "sanur bali", "sanur beach", "sanur sunrise", "sanur market"],
    "누사두아": ["nusa dua", "nusa dua bali", "nusa dua beach", "mulia resort", "nusa peninsula"],
    "울루와뚜": ["uluwatu", "uluwatu bali", "uluwatu temple", "uluwatu surf", "uluwatu cliff"],
    "짠디다사": ["candidasa", "candidasa bali", "candidasa beach", "padang bai", "east bali"],
    "로비나": ["lovina", "lovina bali", "lovina beach", "lovina dolphin", "singaraja"],
    "킨타마니": ["kintamani", "kintamani bali", "mount batur", "batur lake", "batur volcano"],
    "타나롯": ["tanah lot", "tanah lot bali", "tanah lot temple", "tanah lot sunset"],
    "베두굴": ["bedugul", "bedugul bali", "ulun danu", "bratan lake", "bedugul temple"],
}

CATEGORIES = {
    "food": {
        "flickr": [
            "bali,food", "bali,restaurant", "bali,warung", "bali,cafe", "bali,seafood",
            "bali,nasi goreng", "bali,cooking", "bali,eating", "bali,dining", "bali,cuisine",
            "bali,coffee", "bali,dessert", "bali,breakfast", "bali,smoothie bowl", "bali,vegan",
            "bali,bbq", "bali,fruit", "bali,market food", "bali,street food", "bali,satay",
            "bali,soto", "bali,rendang", "bali,gado gado", "bali,tempeh", "bali,tofu",
        ],
        "wikimedia": [
            "bali food", "bali cuisine", "nasi goreng bali", "babi guling", "bali restaurant",
            "indonesian cuisine bali", "bali warung", "bali cafe", "bali coffee", "bali street food",
            "bali market food", "bali seafood", "bali cooking", "indonesian food bali", "bali dining",
            "bali dessert", "bali fruit market", "bali smoothie", "bali vegan food", "bali bbq",
            "bali soto", "bali rendang", "bali tempeh", "bali tofu", "bali gado gado",
        ],
    },
    "culture": {
        "flickr": [
            "bali,temple", "bali,ceremony", "bali,dance", "bali,culture", "bali,art",
            "bali,offering", "bali,ritual", "bali,shrines", "bali,gamelan", "bali,barong",
            "bali,kecak", "bali,sculpture", "bali,painting", "bali,hindu", "bali,traditional",
            "bali,statue", "bali,incense", "bali,prayer", "bali,festival", "bali,puppet",
            "bali,wood carving", "bali,stone carving", "bali,mosaic", "bali,balinese dress", "bali,offering basket",
        ],
        "wikimedia": [
            "bali temple", "pura bali", "bali ceremony", "kecak dance bali", "bali culture",
            "bali art", "bali offering", "hindu temple bali", "bali dance traditional", "bali barong",
            "bali sculpture", "bali painting traditional", "bali ritual", "bali gamelan", "bali shrine",
            "bali statue", "bali incense", "bali prayer", "bali festival", "bali puppet",
            "bali wood carving", "bali stone carving", "bali gate", "bali relief", "bali offering canang",
        ],
    },
    "beach": {
        "flickr": [
            "bali,beach", "bali,surfing", "bali,ocean", "bali,sunset", "bali,waves",
            "bali,snorkeling", "bali,coast", "bali,sea", "bali,island", "bali,surf",
            "bali,beach club", "bali,diving", "bali,tropical beach", "bali,palm tree", "bali,cliff beach",
            "bali,paddle board", "bali,kayak", "bali,jetski", "bali,coral reef", "bali,sand",
            "bali,beach bar", "bali,beach sunset", "bali,beach walk", "bali,beach yoga", "bali,beach horse",
        ],
        "wikimedia": [
            "bali beach", "kuta beach bali", "bali surfing", "bali coast", "bali ocean",
            "sanur beach bali", "nusa dua beach", "bali sunset beach", "bali sea", "bali island beach",
            "uluwatu beach", "bali snorkeling", "bali diving", "bali waves", "bali sand beach",
            "bali tropical beach", "bali coral", "bali palm beach", "bali cliff coast", "bali surf board",
            "bali beach club", "bali beach bar", "bali beach walk", "bali beach sunset", "bali beach yoga",
        ],
    },
    "nature": {
        "flickr": [
            "bali,rice terrace", "bali,waterfall", "bali,volcano", "bali,jungle",
            "bali,monkey", "bali,nature", "bali,mountain", "bali,lake", "bali,forest", "bali,trek",
            "bali,swing", "bali,canyon", "bali,hot spring", "bali,crater", "bali,bamboo",
            "bali,tropical forest", "bali,garden", "bali,flower", "bali,rice field", "bali,river",
            "bali,dragon fly", "bali,butterfly", "bali,gecko", "bali,turtle", "bali,bird",
        ],
        "wikimedia": [
            "bali rice terrace", "tegalalang rice", "bali waterfall", "mount batur", "bali nature",
            "bali monkey forest", "bali volcano", "bali lake", "bali jungle", "bali forest",
            "bali mountain", "bali crater lake", "bali hot spring", "bali garden", "bali tropical",
            "bali rice field", "bali river", "bali bamboo forest", "bali flower tropical", "bali canyon",
            "bali turtle", "bali bird", "bali butterfly", "bali gecko", "bali dragon",
        ],
    },
    "shopping": {
        "flickr": [
            "bali,market", "bali,shopping", "bali,spa", "bali,massage", "bali,craft",
            "bali,souvenir", "bali,art market", "bali,boutique", "bali,handicraft", "bali,textile",
            "bali,jewelry", "bali,wood carving", "bali,batik", "bali,leather", "bali,ceramics",
            "bali,fabric", "bali,basket", "bali,pottery", "bali,silver craft", "bali,painting market",
            "bali,market stall", "bali,market fruit", "bali,market spice", "bali,market flower", "bali,market cloth",
        ],
        "wikimedia": [
            "bali market", "ubud market bali", "bali shopping", "bali craft", "bali souvenir",
            "bali art market", "bali spa", "traditional market bali", "bali textile", "bali batik",
            "bali handicraft", "bali jewelry", "bali wood carving", "bali silver", "bali pottery",
            "bali ceramics", "bali basket", "bali fabric", "bali leather goods", "bali boutique",
            "bali market fruit", "bali market spice", "bali market flower", "bali market cloth", "bali market food stall",
        ],
    },
    "transport": {
        "flickr": [
            "bali,scooter", "bali,airport", "bali,transport", "bali,taxi", "bali,road",
            "bali,travel", "bali,traffic", "bali,bus", "bali,boat", "bali,motorbike",
            "bali,bicycle", "bali,car rental", "bali,driver", "bali,bridge", "bali,harbor",
            "bali,ferry", "bali,parking", "bali,street scene", "bali,highway", "bali,ojek",
            "bali,rickshaw", "bali,bemo", "bali,boat traditional", "bali,fishing boat", "bali,canoe",
        ],
        "wikimedia": [
            "bali airport", "ngurah rai airport", "bali transport", "bali scooter", "bali road",
            "bali traffic", "bali boat", "indonesia transport bali", "bali bus", "bali motorbike",
            "bali bicycle", "bali ferry", "bali harbor", "bali car", "bali taxi",
            "bali street scene", "bali bridge", "bali parking", "bali ojek", "bali traditional boat",
            "bali fishing boat", "bali canoe", "bali rickshaw", "bali bemo", "bali roundabout",
        ],
    },
}

TARGET_PER_COMBO = 137
HEADERS = {"User-Agent": "JPTravelBali/2.0 (https://balitravel.blog; image-scraper)"}
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
    """같은 조합 내에서 perceptual 중복 체크 (해밍거리 <=5)"""
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
    """다운로드: MD5 전역중복 + pHash 조합내중복 체크"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code != 200:
            return False
        c = r.content
        if len(c) < 3000:
            return False

        # MD5 전역 중복 체크 (같은 파일이 다른 카테고리에 있으면 스킵)
        fh = file_hash(c)
        if fh in file_hashes:
            return False

        img = Image.open(BytesIO(c))
        if img.width < 150 or img.height < 150:
            return False

        # perceptual hash 조합 내 중복 체크
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
    for ak in area_kws[:3]:
        for kw in CATEGORIES[cat]["flickr"][:12]:
            tags = f"{ak},{kw}" if "," not in kw else f"{ak},{kw}"
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
                time.sleep(0.3)
            except:
                pass
    return results


def scrape_wikimedia(area, cat):
    results = []
    area_kws = AREA_KW.get(area, [area])
    for ak in area_kws[:3]:
        for kw in CATEGORIES[cat]["wikimedia"][:12]:
            q = f"{ak} {kw}"
            try:
                r = requests.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={"action": "query", "list": "search", "srsearch": q,
                            "srnamespace": "6", "srlimit": "20", "format": "json"},
                    headers={**HEADERS, "User-Agent": "JPTravelBali/2.0 (https://balitravel.blog)"},
                    timeout=20
                )
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("query", {}).get("search", []):
                        fn = item["title"].replace("File:", "").replace(" ", "_")
                        h = hashlib.md5(fn.encode()).hexdigest()
                        results.append(f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{fn}/800px-{fn}")
                time.sleep(1.5)
            except:
                pass
    return results


def scrape_picsum(area, cat, count=80):
    urls = []
    base = hash(f"{area}_{cat}_{datetime.now().strftime('%Y%m%d')}")
    for i in range(count):
        seed = hashlib.md5(f"{base}_{i}".encode()).hexdigest()[:10]
        urls.append(f"https://picsum.photos/seed/{seed}/1200/800")
    return urls


def process_combo(area, cat, file_hashes):
    out = OUTPUT_DIR / area / cat
    out.mkdir(parents=True, exist_ok=True)
    existing = sorted(out.glob("*.webp"))
    current = len(existing)
    needed = TARGET_PER_COMBO - current

    if needed <= 0:
        pf(f"  ✅ {cat}: {current}장 (충분)")
        return 0, 0

    pf(f"  📥 {cat}: {current}장 → +{needed}장 필요")

    # 이 조합의 기존 perceptual hash 로드
    combo_phashes = []
    for img_path in existing:
        try:
            img = Image.open(img_path)
            ph = perceptual_hash(img)
            if ph:
                combo_phashes.append(ph)
        except:
            pass

    # 후보 수집
    candidates = []
    for name, fn in [("flickr", scrape_flickr), ("wikimedia", scrape_wikimedia)]:
        try:
            r = fn(area, cat)
            candidates.extend(r)
            pf(f"    {name}: {len(r)}개")
        except Exception as e:
            pf(f"    {name}: 오류 {e}")

    # Picsum 보충
    if len(candidates) < needed * 3:
        picsum = scrape_picsum(area, cat, needed * 3)
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

    # 다운로드
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
        if (new + fail) % 80 == 0 and (new + fail) > 0:
            save_json(FILE_HASH_DB, file_hashes)
            pf(f"    → +{new} 성공 / {fail} 필터")

    save_json(FILE_HASH_DB, file_hashes)
    pf(f"    → 완료: +{new}장 (총 {current + new}장)")
    return new, fail


def main():
    pf("=" * 60)
    pf("🖼️ 고유 이미지 스크래퍼 v9")
    pf(f"   목표: {TARGET_PER_COMBO}장/조합 (총 ~9,000장)")
    pf(f"   전략: MD5 전역중복차단 + pHash 조합내중복차단")
    pf("=" * 60)

    file_hashes = load_json(FILE_HASH_DB)

    # 기존 이미지 MD5 등록
    pf("\n📋 기존 이미지 MD5 등록...")
    registered = 0
    for area_dir in OUTPUT_DIR.iterdir():
        if not area_dir.is_dir(): continue
        for cat_dir in area_dir.iterdir():
            if not cat_dir.is_dir(): continue
            for img_path in cat_dir.glob("*.webp"):
                fh = file_hash(img_path.read_bytes())
                if fh not in file_hashes:
                    file_hashes[fh] = str(img_path)
                    registered += 1
    pf(f"  등록: +{registered} (총 {len(file_hashes)}개)")
    save_json(FILE_HASH_DB, file_hashes)

    total_new = 0
    total_fail = 0

    for area in AREAS:
        pf(f"\n📍 {area}")
        for cat in CATEGORIES:
            new, fail = process_combo(area, cat, file_hashes)
            total_new += new
            total_fail += fail

    # 매핑 재생성
    pf("\n📋 매핑 재생성...")
    mapping = {}
    for ad in OUTPUT_DIR.iterdir():
        if not ad.is_dir(): continue
        mapping[ad.name] = {}
        for cd in ad.iterdir():
            if not cd.is_dir(): continue
            mapping[ad.name][cd.name] = sorted([f.name for f in cd.glob("*.webp")])
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    total_imgs = sum(len(v) for cats in mapping.values() for v in cats.values())

    pf(f"\n{'='*60}")
    pf(f"✅ 완료!")
    pf(f"   신규: +{total_new} | 필터: {total_fail}")
    pf(f"   총 이미지: {total_imgs}장")
    pf(f"   전역 MD5 DB: {len(file_hashes)}개")

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
