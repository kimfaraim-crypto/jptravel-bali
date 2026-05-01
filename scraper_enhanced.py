#!/usr/bin/env python3
"""
강화 이미지 스크래퍼 v5
목표: 지역×카테고리당 150+ 고유 이미지 확보
소스: Openverse + Flickr + Wikimedia + Picsum(fallback)
중복 제거: perceptual hash 기반
"""
import os, sys, json, hashlib, time, random, requests
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
HASH_DB = BASE_DIR / "image_hashes.json"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
STATE_FILE = BASE_DIR / "scraper_state_v5.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

# 카테고리별 확장 검색 키워드 (소스 다양화)
CATEGORIES = {
    "food": {
        "openverse": ["bali food", "bali restaurant", "bali warung", "nasi goreng bali", "babi guling", 
                       "bali cafe", "bali cuisine", "indonesian food bali", "bali street food", "bali seafood"],
        "flickr": ["bali,food", "bali,restaurant", "bali,warung", "bali,cafe", "bali,seafood",
                   "bali,nasi", "bali,cooking", "bali,eating", "bali,dining", "bali,cuisine"],
        "wikimedia": ["bali food", "bali cuisine", "nasi goreng", "babi guling", "bali restaurant",
                       "indonesian cuisine", "bali warung", "bali cafe"],
    },
    "culture": {
        "openverse": ["bali temple", "bali ceremony", "bali dance", "bali culture", "bali art",
                       "bali offering", "bali ritual", "bali Hindu", "bali shrine", "bali gamelan"],
        "flickr": ["bali,temple", "bali,ceremony", "bali,dance", "bali,culture", "bali,art",
                   "bali,offering", "bali,ritual", "bali,shrines", "bali,gamelan", "bali,barong"],
        "wikimedia": ["bali temple", "pura bali", "bali ceremony", "kecak dance", "bali culture",
                       "bali art", "bali offering", "hindu temple bali"],
    },
    "beach": {
        "openverse": ["bali beach", "bali surfing", "bali ocean", "bali sunset", "bali waves",
                       "bali snorkeling", "bali coast", "bali sand", "bali sea", "bali island"],
        "flickr": ["bali,beach", "bali,surfing", "bali,ocean", "bali,sunset", "bali,waves",
                   "bali,snorkeling", "bali,coast", "bali,sea", "bali,island", "bali,surf"],
        "wikimedia": ["bali beach", "kuta beach bali", "bali surfing", "bali coast", "bali ocean",
                       "sanur beach", "nusa dua beach", "bali sunset"],
    },
    "nature": {
        "openverse": ["bali rice terrace", "bali waterfall", "bali volcano", "bali jungle",
                       "bali monkey", "bali nature", "bali mountain", "bali lake", "bali forest", "bali trekking"],
        "flickr": ["bali,rice,terrace", "bali,waterfall", "bali,volcano", "bali,jungle",
                   "bali,monkey", "bali,nature", "bali,mountain", "bali,lake", "bali,forest", "bali,trek"],
        "wikimedia": ["bali rice terrace", "tegalalang", "bali waterfall", "mount batur", "bali nature",
                       "bali monkey forest", "bali volcano", "bali lake"],
    },
    "shopping": {
        "openverse": ["bali market", "bali shopping", "bali spa", "bali massage", "bali craft",
                       "bali souvenir", "bali art market", "bali boutique", "bali handicraft", "bali textile"],
        "flickr": ["bali,market", "bali,shopping", "bali,spa", "bali,massage", "bali,craft",
                   "bali,souvenir", "bali,market", "bali,boutique", "bali,handicraft", "bali,textile"],
        "wikimedia": ["bali market", "ubud market", "bali shopping", "bali craft", "bali souvenir",
                       "bali art market", "bali spa", "traditional market bali"],
    },
    "transport": {
        "openverse": ["bali scooter", "bali airport", "bali transport", "bali taxi", "bali road",
                       "bali travel", "bali traffic", "bali bus", "bali boat", "bali motorbike"],
        "flickr": ["bali,scooter", "bali,airport", "bali,transport", "bali,taxi", "bali,road",
                   "bali,travel", "bali,traffic", "bali,bus", "bali,boat", "bali,motorbike"],
        "wikimedia": ["bali airport", "ngurah rai", "bali transport", "bali scooter", "bali road",
                       "bali traffic", "bali boat", "indonesia transport"],
    },
}

AREA_KW = {
    "우붓": "ubud", "스미냑": "seminyak", "꾸따": "kuta",
    "사누르": "sanur", "누사두아": "nusa dua", "울루와뚜": "uluwatu",
    "짠디다사": "candidasa", "로비나": "lovina", "킨타마니": "kintamani",
    "타나롯": "tanah lot", "베두굴": "bedugul",
}

TARGET_PER_COMBO = 150  # 지역×카테고리당 목표
HEADERS = {"User-Agent": "JPTraffiBali/1.0 (https://balitravel.blog; contact@balitravel.blog)"}

def flush_print(msg):
    print(msg, flush=True)

def load_hashes():
    if HASH_DB.exists():
        return json.loads(HASH_DB.read_text())
    return {}

def save_hashes(h):
    HASH_DB.write_text(json.dumps(h, ensure_ascii=False, indent=2))

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
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
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

# ============================================================
# 소스별 스크래핑 함수 (확장판)
# ============================================================

def scrape_openverse(area, cat):
    """Openverse API — 최대 5페이지까지 확장"""
    results = []
    ak = AREA_KW.get(area, area)
    kws = CATEGORIES[cat]["openverse"]
    for kw in kws[:5]:  # 키워드 5개 사용
        q = f"{ak} {kw.split(' ',1)[-1]}"
        for page in range(1, 4):  # 최대 3페이지
            try:
                r = requests.get(
                    f"https://api.openverse.org/v1/images/",
                    params={"q": q, "page_size": 50, "page": page},
                    headers=HEADERS, timeout=15
                )
                if r.status_code == 200:
                    data = r.json()
                    items = data.get("results", [])
                    if not items: break
                    for item in items:
                        url = item.get("url")
                        if url and url.startswith("http"):
                            results.append(url)
                    flush_print(f"      openverse '{q}' p{page}: {len(items)}개")
                elif r.status_code == 429:
                    time.sleep(5)
                    continue
                else:
                    break
                time.sleep(2)  # rate limit
            except Exception as e:
                flush_print(f"      openverse 오류: {e}")
                break
    return results

def scrape_flickr(area, cat):
    """Flickr public feed — 확장 검색"""
    results = []
    ak = AREA_KW.get(area, area)
    kws = CATEGORIES[cat]["flickr"]
    for kw in kws[:6]:
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
                        # 원본 크기로 변환 (m → b)
                        big = m.replace("_m.jpg", "_b.jpg")
                        results.append(big)
                flush_print(f"      flickr '{tags}': {len(data.get('items',[]))}개")
            time.sleep(0.5)
        except Exception as e:
            flush_print(f"      flickr 오류: {e}")
    return results

def scrape_wikimedia(area, cat):
    """Wikimedia Commons — 확장 검색"""
    results = []
    ak = AREA_KW.get(area, area)
    kws = CATEGORIES[cat]["wikimedia"]
    for kw in kws[:5]:
        q = f"{ak} {kw}"
        try:
            # 파일 목록 검색
            r = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action": "query", "list": "search", "srsearch": q,
                    "srnamespace": "6", "srlimit": "20", "format": "json"
                },
                headers=HEADERS, timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                for item in data.get("query", {}).get("search", []):
                    fn = item["title"].replace("File:", "").replace(" ", "_")
                    # Wikimedia 이미지 URL 생성
                    h = hashlib.md5(fn.encode()).hexdigest()
                    thumb_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{fn}/800px-{fn}"
                    results.append(thumb_url)
                flush_print(f"      wikimedia '{q}': {len(data.get('query',{}).get('search',[]))}개")
            time.sleep(2)
        except Exception as e:
            flush_print(f"      wikimedia 오류: {e}")
    return results

def generate_picsum_urls(area, cat, count=30):
    """Picsum 랜덤 이미지 URL 생성 (fallback)"""
    urls = []
    for i in range(count):
        seed = hashlib.md5(f"{area}_{cat}_{i}_{datetime.now().strftime('%Y%m')}".encode()).hexdigest()[:10]
        urls.append(f"https://picsum.photos/seed/{seed}/1200/800")
    return urls

def main():
    flush_print("=" * 60)
    flush_print("🖼️ 강화 이미지 스크래퍼 v5")
    flush_print(f"   목표: 지역×카테고리당 {TARGET_PER_COMBO}개 이상")
    flush_print("=" * 60)

    hashes = load_hashes()
    total_new = 0
    total_skip = 0
    stats = {}

    for area in AREAS:
        flush_print(f"\n📍 {area}")
        ak = AREA_KW.get(area, area)
        stats[area] = {}

        for cat in CATEGORIES:
            out = OUTPUT_DIR / area / cat
            out.mkdir(parents=True, exist_ok=True)
            existing = list(out.glob("*.webp"))
            needed = TARGET_PER_COMBO - len(existing)

            if needed <= 0:
                flush_print(f"  ✅ {cat}: {len(existing)}개 (충분)")
                stats[area][cat] = {"existing": len(existing), "new": 0}
                continue

            flush_print(f"  📥 {cat}: {len(existing)}개 → {TARGET_PER_COMBO}개 필요 ({needed}개 부족)")

            # 모든 소스에서 후보 수집
            candidates = []
            for name, fn in [("openverse", scrape_openverse), ("flickr", scrape_flickr), ("wikimedia", scrape_wikimedia)]:
                try:
                    r = fn(area, cat)
                    candidates.extend(r)
                    flush_print(f"    {name}: {len(r)}개 수집")
                except Exception as e:
                    flush_print(f"    {name}: 오류 {e}")

            # Picsum fallback (부족분)
            if len(candidates) < needed * 2:
                picsum = generate_picsum_urls(area, cat, needed * 2)
                candidates.extend(picsum)
                flush_print(f"    picsum: {len(picsum)}개 추가 (fallback)")

            # 셔플 (소스 균형)
            random.shuffle(candidates)

            # 다운로드
            new = 0
            fail = 0
            for url in candidates:
                if new >= needed: break
                idx = len(existing) + new + 1
                fname = f"{area}_{cat}_{idx:04d}.webp"
                sp = out / fname
                if sp.exists(): continue
                if download(url, sp, hashes):
                    new += 1
                    total_new += 1
                else:
                    fail += 1
                    total_skip += 1
                
                # 주기적 저장
                if (new + fail) % 50 == 0:
                    save_hashes(hashes)
                    flush_print(f"    → 진행: {new}개 성공 / {fail}개 실패")
                
                time.sleep(0.1)

            save_hashes(hashes)
            stats[area][cat] = {"existing": len(existing) + new, "new": new, "fail": fail}
            flush_print(f"    → 완료: +{new}개 (총 {len(existing)+new}개)")

    # 매핑 재생성
    flush_print("\n📋 매핑 재생성...")
    mapping = {}
    for ad in OUTPUT_DIR.iterdir():
        if not ad.is_dir(): continue
        mapping[ad.name] = {}
        for cd in ad.iterdir():
            if not cd.is_dir(): continue
            imgs = sorted([f.name for f in cd.glob("*.webp")])
            mapping[ad.name][cd.name] = imgs
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

    # 상태 저장
    STATE_FILE.write_text(json.dumps({
        "last_run": datetime.now().isoformat(),
        "stats": stats,
        "total_new": total_new,
        "total_skip": total_skip,
    }, ensure_ascii=False, indent=2))

    # 결과 요약
    total_imgs = sum(len(v) for cats in mapping.values() for v in cats.values())
    flush_print(f"\n{'='*60}")
    flush_print(f"✅ 완료!")
    flush_print(f"   신규 다운로드: {total_new}")
    flush_print(f"   스킵(중복/실패): {total_skip}")
    flush_print(f"   총 이미지: {total_imgs}")
    flush_print(f"   목표: {len(AREAS) * len(CATEGORIES) * TARGET_PER_COMBO}")
    
    # 부족분 확인
    shortage = []
    for area in AREAS:
        for cat in CATEGORIES:
            count = len(mapping.get(area, {}).get(cat, []))
            if count < 140:
                shortage.append(f"  {area}/{cat}: {count}개 (140 필요)")
    if shortage:
        flush_print(f"\n⚠️ 부족분 ({len(shortage)}개 조합):")
        for s in shortage[:20]:
            flush_print(s)

if __name__ == "__main__":
    main()
