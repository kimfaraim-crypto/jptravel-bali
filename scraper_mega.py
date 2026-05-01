#!/usr/bin/env python3
"""
메가 이미지 스크래퍼 v7
목표: 9,000+ 고유 이미지 (지역×카테고리당 ~136장)
소스: Openverse + Flickr + Wikimedia + Picsum(fallback)
중복 제거: perceptual hash 기반
다운로드: ThreadPoolExecutor 병렬 처리
"""
import os, sys, json, hashlib, time, random, requests, threading
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images"
HASH_DB = BASE_DIR / "image_hashes_v7.json"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
STATE_FILE = BASE_DIR / "scraper_state_v7.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

AREA_KW = {
    "우붓": ["ubud", "ubud bali", "monkey forest ubud", "tegalalang", "rice terrace ubud"],
    "스미냑": ["seminyak", "seminyak bali", "double six beach", "potato head bali"],
    "꾸따": ["kuta", "kuta bali", "kuta beach", "waterbom bali"],
    "사누르": ["sanur", "sanur bali", "sanur beach", "sanur sunrise"],
    "누사두아": ["nusa dua", "nusa dua bali", "nusa dua beach", "mulia resort bali"],
    "울루와뚜": ["uluwatu", "uluwatu bali", "uluwatu temple", "uluwatu surf"],
    "짠디다사": ["candidasa", "candidasa bali", "candidasa beach"],
    "로비나": ["lovina", "lovina bali", "lovina beach", "lovina dolphin"],
    "킨타마니": ["kintamani", "kintamani bali", "mount batur", "batur lake"],
    "타나롯": ["tanah lot", "tanah lot bali", "tanah lot temple"],
    "베두굴": ["bedugul", "bedugul bali", "ulun danu", "bratan lake"],
}

CATEGORIES = {
    "food": {
        "openverse": [
            "bali food", "bali restaurant", "bali warung", "nasi goreng bali", "babi guling",
            "bali cafe", "bali cuisine", "indonesian food bali", "bali street food", "bali seafood",
            "bali coffee", "bali dessert", "bali breakfast", "bali brunch", "bali dining",
            "bali smoothie bowl", "bali vegan food", "bali bbq", "bali market food", "bali fruit",
        ],
        "flickr": [
            "bali,food", "bali,restaurant", "bali,warung", "bali,cafe", "bali,seafood",
            "bali,nasi", "bali,cooking", "bali,eating", "bali,dining", "bali,cuisine",
            "bali,coffee", "bali,dessert", "bali,breakfast", "bali,smoothie", "bali,vegan",
        ],
        "wikimedia": [
            "bali food", "bali cuisine", "nasi goreng", "babi guling", "bali restaurant",
            "indonesian cuisine", "bali warung", "bali cafe", "bali coffee", "bali street food",
            "bali market food", "bali seafood", "bali cooking", "indonesian food", "bali dining",
        ],
    },
    "culture": {
        "openverse": [
            "bali temple", "bali ceremony", "bali dance", "bali culture", "bali art",
            "bali offering", "bali ritual", "bali hindu", "bali shrine", "bali gamelan",
            "bali barong", "bali kecak", "bali sculpture", "bali painting", "bali traditional",
            "bali ceremony flower", "bali incense", "bali prayer", "bali festival", "bali puppet",
        ],
        "flickr": [
            "bali,temple", "bali,ceremony", "bali,dance", "bali,culture", "bali,art",
            "bali,offering", "bali,ritual", "bali,shrines", "bali,gamelan", "bali,barong",
            "bali,kecak", "bali,sculpture", "bali,painting", "bali,hindu", "bali,traditional",
        ],
        "wikimedia": [
            "bali temple", "pura bali", "bali ceremony", "kecak dance", "bali culture",
            "bali art", "bali offering", "hindu temple bali", "bali dance", "bali barong",
            "bali sculpture", "bali painting", "bali ritual", "bali gamelan", "bali shrine",
        ],
    },
    "beach": {
        "openverse": [
            "bali beach", "bali surfing", "bali ocean", "bali sunset", "bali waves",
            "bali snorkeling", "bali coast", "bali sand", "bali sea", "bali island",
            "bali surf board", "bali beach club", "bali coral", "bali tropical beach", "bali palm tree",
            "bali cliff beach", "bali diving", "bali paddle", "bali kayak", "bali jet ski",
        ],
        "flickr": [
            "bali,beach", "bali,surfing", "bali,ocean", "bali,sunset", "bali,waves",
            "bali,snorkeling", "bali,coast", "bali,sea", "bali,island", "bali,surf",
            "bali,beach club", "bali,diving", "bali,tropical", "bali,palm", "bali,cliff",
        ],
        "wikimedia": [
            "bali beach", "kuta beach bali", "bali surfing", "bali coast", "bali ocean",
            "sanur beach", "nusa dua beach", "bali sunset", "bali sea", "bali island",
            "uluwatu beach", "bali snorkeling", "bali diving", "bali waves", "bali sand",
        ],
    },
    "nature": {
        "openverse": [
            "bali rice terrace", "bali waterfall", "bali volcano", "bali jungle",
            "bali monkey", "bali nature", "bali mountain", "bali lake", "bali forest", "bali trekking",
            "bali swing", "bali canyon", "bali hot spring", "bali crater", "bali bamboo",
            "bali tropical", "bali garden", "bali flower", "bali dragon fruit", "bali rice field",
        ],
        "flickr": [
            "bali,rice,terrace", "bali,waterfall", "bali,volcano", "bali,jungle",
            "bali,monkey", "bali,nature", "bali,mountain", "bali,lake", "bali,forest", "bali,trek",
            "bali,swing", "bali,canyon", "bali,hot spring", "bali,crater", "bali,bamboo",
        ],
        "wikimedia": [
            "bali rice terrace", "tegalalang", "bali waterfall", "mount batur", "bali nature",
            "bali monkey forest", "bali volcano", "bali lake", "bali jungle", "bali forest",
            "bali mountain", "bali crater", "bali hot spring", "bali garden", "bali tropical",
        ],
    },
    "shopping": {
        "openverse": [
            "bali market", "bali shopping", "bali spa", "bali massage", "bali craft",
            "bali souvenir", "bali art market", "bali boutique", "bali handicraft", "bali textile",
            "bali jewelry", "bali wood carving", "bali batik", "bali leather", "bali ceramics",
            "bali fabric", "bali basket", "bali pottery", "bali silver", "bali painting market",
        ],
        "flickr": [
            "bali,market", "bali,shopping", "bali,spa", "bali,massage", "bali,craft",
            "bali,souvenir", "bali,market", "bali,boutique", "bali,handicraft", "bali,textile",
            "bali,jewelry", "bali,carving", "bali,batik", "bali,leather", "bali,ceramics",
        ],
        "wikimedia": [
            "bali market", "ubud market", "bali shopping", "bali craft", "bali souvenir",
            "bali art market", "bali spa", "traditional market bali", "bali textile", "bali batik",
            "bali handicraft", "bali jewelry", "bali wood carving", "bali silver", "bali pottery",
        ],
    },
    "transport": {
        "openverse": [
            "bali scooter", "bali airport", "bali transport", "bali taxi", "bali road",
            "bali travel", "bali traffic", "bali bus", "bali boat", "bali motorbike",
            "bali bicycle", "bali car rental", "bali driver", "bali bridge", "bali harbor",
            "bali ferry", "bali parking", "bali street", "bali highway", "bali roundabout",
        ],
        "flickr": [
            "bali,scooter", "bali,airport", "bali,transport", "bali,taxi", "bali,road",
            "bali,travel", "bali,traffic", "bali,bus", "bali,boat", "bali,motorbike",
            "bali,bicycle", "bali,car", "bali,driver", "bali,bridge", "bali,harbor",
        ],
        "wikimedia": [
            "bali airport", "ngurah rai", "bali transport", "bali scooter", "bali road",
            "bali traffic", "bali boat", "indonesia transport", "bali bus", "bali motorbike",
            "bali bicycle", "bali ferry", "bali harbor", "bali car", "bali taxi",
        ],
    },
}

TARGET_PER_COMBO = 137  # 11*6*137 ≈ 9,022
HEADERS = {"User-Agent": "JPTravelBali/2.0 (https://balitravel.blog; scraper)"}
lock = threading.Lock()
flush_lock = threading.Lock()

def flush_print(msg):
    with flush_lock:
        print(msg, flush=True)

def load_hashes():
    if HASH_DB.exists():
        try:
            return json.loads(HASH_DB.read_text())
        except:
            return {}
    return {}

def save_hashes(h):
    with lock:
        HASH_DB.write_text(json.dumps(h, ensure_ascii=False))

def perceptual_hash(img):
    try:
        s = img.resize((8, 8)).convert('L')
        p = list(s.getdata())
        avg = sum(p) / len(p)
        return hex(int(''.join('1' if x > avg else '0' for x in p), 2))[2:].zfill(16)
    except:
        return None

def phash_dist(h1, h2):
    try:
        b1 = bin(int(h1, 16))[2:].zfill(64)
        b2 = bin(int(h2, 16))[2:].zfill(64)
        return sum(a != b for a, b in zip(b1, b2))
    except:
        return 999

def is_dup(img, hashes):
    ph = perceptual_hash(img)
    if not ph:
        return True, None
    for v in hashes.values():
        if phash_dist(ph, v) <= 5:
            return True, None
    return False, ph

def download(url, path, hashes):
    """단일 이미지 다운로드 + 중복 체크"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        if r.status_code != 200:
            return False
        c = r.content
        if len(c) < 3000:
            return False
        img = Image.open(BytesIO(c))
        if img.width < 150 or img.height < 150:
            return False
        with lock:
            dup, ph = is_dup(img, hashes)
        if dup:
            return False
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(path, 'WEBP', quality=85)
        with lock:
            hashes[path.name] = ph
        return True
    except:
        return False


# ============================================================
# 소스별 스크래핑 함수
# ============================================================

def scrape_openverse(area, cat):
    """Openverse API — 키워드 10개 × 3페이지 = 최대 1,500 후보"""
    results = []
    area_kws = AREA_KW.get(area, [area])
    cat_kws = CATEGORIES[cat]["openverse"]
    
    for ak in area_kws[:3]:
        for kw in cat_kws[:8]:
            q = f"{ak} {kw.split(' ', 1)[-1]}"
            for page in range(1, 4):
                try:
                    r = requests.get(
                        "https://api.openverse.org/v1/images/",
                        params={"q": q, "page_size": 50, "page": page},
                        headers=HEADERS, timeout=20
                    )
                    if r.status_code == 200:
                        data = r.json()
                        items = data.get("results", [])
                        if not items:
                            break
                        for item in items:
                            url = item.get("url")
                            if url and url.startswith("http"):
                                results.append(url)
                    elif r.status_code == 429:
                        time.sleep(8)
                        continue
                    else:
                        break
                    time.sleep(1.5)
                except Exception as e:
                    break
    return results

def scrape_flickr(area, cat):
    """Flickr public feed — 키워드 10개 × 20개 = 최대 200 후보"""
    results = []
    area_kws = AREA_KW.get(area, [area])
    cat_kws = CATEGORIES[cat]["flickr"]
    
    for ak in area_kws[:3]:
        for kw in cat_kws[:8]:
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
                            big = m.replace("_m.jpg", "_b.jpg")
                            results.append(big)
                time.sleep(0.3)
            except:
                pass
    return results

def scrape_wikimedia(area, cat):
    """Wikimedia Commons — 키워드 10개 × 20개 = 최대 200 후보"""
    results = []
    area_kws = AREA_KW.get(area, [area])
    cat_kws = CATEGORIES[cat]["wikimedia"]
    
    for ak in area_kws[:3]:
        for kw in cat_kws[:8]:
            q = f"{ak} {kw}"
            try:
                r = requests.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={
                        "action": "query", "list": "search", "srsearch": q,
                        "srnamespace": "6", "srlimit": "20", "format": "json"
                    },
                    headers={**HEADERS, "User-Agent": "JPTravelBali/2.0 (https://balitravel.blog)"},
                    timeout=20
                )
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("query", {}).get("search", []):
                        fn = item["title"].replace("File:", "").replace(" ", "_")
                        h = hashlib.md5(fn.encode()).hexdigest()
                        thumb_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{fn}/800px-{fn}"
                        results.append(thumb_url)
                time.sleep(1.5)
            except:
                pass
    return results

def generate_picsum_urls(area, cat, count=50):
    """Picsum 랜덤 이미지 (fallback)"""
    urls = []
    base_seed = hash(f"{area}_{cat}_{datetime.now().strftime('%Y%m%d')}")
    for i in range(count):
        seed = hashlib.md5(f"{base_seed}_{i}".encode()).hexdigest()[:10]
        urls.append(f"https://picsum.photos/seed/{seed}/1200/800")
    return urls


def download_batch(candidates, out_dir, hashes, needed, area, cat):
    """배치 다운로드 (병렬)"""
    new = 0
    fail = 0
    existing_count = len(list(out_dir.glob("*.webp")))
    
    # 중복 URL 제거
    seen_urls = set()
    unique_candidates = []
    for url in candidates:
        if url not in seen_urls:
            seen_urls.add(url)
            unique_candidates.append(url)
    
    flush_print(f"    후보: {len(unique_candidates)}개 (중복제거 후)")
    
    def dl_one(args):
        url, idx = args
        fname = f"{area}_{cat}_{idx:04d}.webp"
        sp = out_dir / fname
        if sp.exists():
            return False
        return download(url, sp, hashes)
    
    # 병렬 다운로드 (5 workers)
    tasks = []
    for i, url in enumerate(unique_candidates):
        if len(tasks) >= needed * 3:  # 3배수 후보
            break
        idx = existing_count + i + 1
        tasks.append((url, idx))
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(dl_one, t): t for t in tasks}
        for future in as_completed(futures):
            if new >= needed:
                # 나머지 취소
                for f in futures:
                    f.cancel()
                break
            try:
                if future.result():
                    new += 1
                else:
                    fail += 1
            except:
                fail += 1
            
            # 주기적 저장
            if (new + fail) % 100 == 0 and (new + fail) > 0:
                save_hashes(hashes)
                flush_print(f"    → 진행: +{new} 성공 / {fail} 실패")
    
    save_hashes(hashes)
    return new, fail


def main():
    flush_print("=" * 60)
    flush_print("🖼️ 메가 이미지 스크래퍼 v7")
    flush_print(f"   목표: 지역×카테고리당 {TARGET_PER_COMBO}장+ (총 ~9,000장)")
    flush_print("=" * 60)

    hashes = load_hashes()
    total_new = 0
    total_fail = 0
    stats = {}

    for area in AREAS:
        flush_print(f"\n📍 {area}")
        stats[area] = {}

        for cat in CATEGORIES:
            out = OUTPUT_DIR / area / cat
            out.mkdir(parents=True, exist_ok=True)
            existing = list(out.glob("*.webp"))
            current_count = len(existing)
            needed = TARGET_PER_COMBO - current_count

            if needed <= 0:
                flush_print(f"  ✅ {cat}: {current_count}개 (충분)")
                stats[area][cat] = {"existing": current_count, "new": 0}
                continue

            flush_print(f"  📥 {cat}: {current_count}개 → 목표 {TARGET_PER_COMBO} ({needed}개 부족)")

            # 소스별 후보 수집
            candidates = []
            
            for name, fn in [("openverse", scrape_openverse), ("flickr", scrape_flickr), ("wikimedia", scrape_wikimedia)]:
                try:
                    r = fn(area, cat)
                    candidates.extend(r)
                    flush_print(f"    {name}: {len(r)}개 수집")
                except Exception as e:
                    flush_print(f"    {name}: 오류 {e}")

            # Picsum fallback (부족분 보충)
            picsum_count = max(0, needed - len(candidates) + 50)
            if picsum_count > 0:
                picsum = generate_picsum_urls(area, cat, picsum_count)
                candidates.extend(picsum)
                flush_print(f"    picsum: {len(picsum)}개 추가 (fallback)")

            random.shuffle(candidates)

            # 배치 다운로드
            new, fail = download_batch(candidates, out, hashes, needed, area, cat)
            
            total_new += new
            total_fail += fail
            final_count = current_count + new
            stats[area][cat] = {"existing": final_count, "new": new, "fail": fail}
            flush_print(f"    → 완료: +{new}개 (총 {final_count}개)")

    # 매핑 재생성
    flush_print("\n📋 매핑 재생성...")
    mapping = {}
    for ad in OUTPUT_DIR.iterdir():
        if not ad.is_dir():
            continue
        mapping[ad.name] = {}
        for cd in ad.iterdir():
            if not cd.is_dir():
                continue
            imgs = sorted([f.name for f in cd.glob("*.webp")])
            mapping[ad.name][cd.name] = imgs
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

    # 상태 저장
    STATE_FILE.write_text(json.dumps({
        "last_run": datetime.now().isoformat(),
        "stats": stats,
        "total_new": total_new,
        "total_fail": total_fail,
    }, ensure_ascii=False, indent=2))

    # 결과 요약
    total_imgs = sum(len(v) for cats in mapping.values() for v in cats.values())
    flush_print(f"\n{'='*60}")
    flush_print(f"✅ 완료!")
    flush_print(f"   신규 다운로드: {total_new}")
    flush_print(f"   실패: {total_fail}")
    flush_print(f"   총 이미지: {total_imgs}")
    flush_print(f"   목표: {len(AREAS) * len(CATEGORIES) * TARGET_PER_COMBO}")
    
    # 부족분 확인
    shortage = []
    for area in AREAS:
        for cat in CATEGORIES:
            count = len(mapping.get(area, {}).get(cat, []))
            if count < TARGET_PER_COMBO - 10:
                shortage.append(f"  {area}/{cat}: {count}개 ({TARGET_PER_COMBO} 필요)")
    if shortage:
        flush_print(f"\n⚠️ 부족분 ({len(shortage)}개 조합):")
        for s in shortage[:30]:
            flush_print(s)
    else:
        flush_print(f"\n🎉 모든 조합이 목표 달성!")

if __name__ == "__main__":
    main()
