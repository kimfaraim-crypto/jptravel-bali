#!/usr/bin/env python3
"""
중국 여행 사이트 발리 이미지 스크래퍼
- Mafengwo, Qyer, Ctrip, Qunar 등
- 모바일 UA 우회
- 카테고리별 맞춤 이미지
- MD5 + pHash 중복 제거
"""
import os, json, hashlib, time, re, requests, random
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime
from urllib.parse import quote

BASE = Path(__file__).parent
IMG_DIR = BASE / "output" / "images"
HASH_DB = BASE / "file_hashes.json"
MAP_FILE = BASE / "image_mapping_v3.json"
LOG_FILE = BASE / "SCRAPER_PROGRESS.txt"

MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
DESKTOP_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATS = ["food", "culture", "beach", "nature", "shopping", "transport"]

# 중국어 검색 키워드 (지역별)
ZH_KEYWORDS = {
    "우ữu": {"food": ["乌布美食", "乌布餐厅", "乌布猪肋排"], "culture": ["乌布皇宫", "乌布寺庙", "乌布市场"], "beach": ["乌布梯田", "乌布丛林"], "nature": ["乌布梯田", "乌布猴子森林", "乌布瀑布"], "shopping": ["乌布市场", "乌布手工艺"], "transport": ["乌布交通"]},
    "스미냑": {"food": ["水明漾美食", "水明漾餐厅", "水明漾咖啡"], "culture": ["水明漾寺庙"], "beach": ["水明漾海滩", "水明漾冲浪", "双六海滩"], "nature": ["水明漾花园"], "shopping": ["水明漾购物", "水明漾SPA"], "transport": ["水明漾交通"]},
    "꾸따": {"food": ["库塔美食", "库塔餐厅", "库塔小吃"], "culture": ["库塔寺庙"], "beach": ["库塔海滩", "库塔冲浪", "库塔日落"], "nature": ["库塔海洋"], "shopping": ["库塔购物", "库塔市场", "discovery mall"], "transport": ["库塔交通", "库塔机场"]},
    "사누르": {"food": ["沙努尔美食", "沙努尔海鲜"], "culture": ["沙努尔寺庙"], "beach": ["沙努尔海滩", "沙努尔日出"], "nature": ["沙努尔红树林"], "shopping": ["沙努尔市场"], "transport": ["沙努尔骑行"]},
    "누사두아": {"food": ["努沙杜瓦美食", "努沙杜瓦自助餐"], "culture": ["努沙杜瓦寺庙"], "beach": ["努沙杜瓦海滩", "努沙杜瓦浮潜"], "nature": ["努沙杜瓦花园"], "shopping": ["bali collection"], "transport": ["努沙杜瓦交通"]},
    "울루와뚜": {"food": ["乌鲁瓦图美食", "乌鲁瓦图餐厅"], "culture": ["乌鲁瓦图寺庙", "kecak舞"], "beach": ["乌鲁瓦图海滩", "乌鲁瓦图冲浪", "padang padang"], "nature": ["乌鲁瓦图悬崖"], "shopping": ["乌鲁瓦图纪念品"], "transport": ["乌鲁瓦图交通"]},
    "짠디다사": {"food": ["赞迪达萨美食"], "culture": ["水之宫殿", "百沙基庙"], "beach": ["赞迪达萨海滩", "阿美德海滩"], "nature": ["东巴厘自然"], "shopping": ["赞迪达萨市场"], "transport": ["赞迪达萨交通"]},
    "로비나": {"food": ["罗威纳美食", "罗威纳海鲜"], "culture": ["罗威纳寺庙"], "beach": ["罗威纳海滩", "罗威纳海豚"], "nature": ["吉吉特瀑布", "班嘉温泉"], "shopping": ["罗威纳市场"], "transport": ["罗威纳交通"]},
    "킨타마니": {"food": ["金塔马尼美食", "金塔马尼咖啡"], "culture": ["金塔马尼寺庙"], "beach": ["巴图尔湖"], "nature": ["巴图尔火山", "金塔马尼日出"], "shopping": ["金塔马尼市场"], "transport": ["金塔马尼交通"]},
    "타나롯": {"food": ["海神庙美食"], "culture": ["海神庙", "海神庙仪式"], "beach": ["海神庙海滩", "海神庙日落"], "nature": ["海神庙稻田"], "shopping": ["海神庙纪念品"], "transport": ["海神庙交通"]},
    "베두굴": {"food": ["百度库美食", "百度库草莓"], "culture": ["水神庙", "百度库寺庙"], "beach": ["布拉坦湖"], "nature": ["百度库植物园", "百度库高原"], "shopping": ["百度库市场"], "transport": ["百度库交通"]},
}

# 영어 키워드 (백업)
EN_KEYWORDS = {
    "우붓": {"food": ["ubud bali food", "ubud restaurant", "babi guling ubud"], "culture": ["ubud temple", "monkey forest ubud"], "beach": ["ubud rice terrace", "campuhan ridge"], "nature": ["tegalalang rice", "ubud waterfall"], "shopping": ["ubud art market"], "transport": ["ubud bali street"]},
    "스미냑": {"food": ["seminyak food", "seminyak beach club"], "culture": ["seminyak temple"], "beach": ["seminyak beach", "double six beach"], "nature": ["seminyak garden"], "shopping": ["seminyak boutique"], "transport": ["seminyak road"]},
    "꾸따": {"food": ["kuta bali food", "kuta restaurant"], "culture": ["kuta temple"], "beach": ["kuta beach surfing", "kuta sunset"], "nature": ["kuta ocean"], "shopping": ["kuta market bali"], "transport": ["kuta airport"]},
    "사누르": {"food": ["sanur food", "sanur seafood"], "culture": ["sanur temple"], "beach": ["sanur beach sunrise"], "nature": ["sanur mangrove"], "shopping": ["sanur night market"], "transport": ["sanur cycling"]},
    "누사두아": {"food": ["nusa dua food"], "culture": ["nusa dua temple"], "beach": ["nusa dua beach", "water blow bali"], "nature": ["nusa dua garden"], "shopping": ["bali collection mall"], "transport": ["nusa dua road"]},
    "울루와뚜": {"food": ["uluwatu restaurant", "single fin uluwatu"], "culture": ["uluwatu temple", "kecak dance"], "beach": ["uluwatu beach", "padang padang beach"], "nature": ["uluwatu cliff"], "shopping": ["uluwatu souvenir"], "transport": ["uluwatu road"]},
    "짠디다사": {"food": ["candidasa food"], "culture": ["tirta gangga", "besakih temple"], "beach": ["candidasa beach", "amed beach"], "nature": ["east bali nature"], "shopping": ["candidasa market"], "transport": ["candidasa road"]},
    "로비나": {"food": ["lovina food"], "culture": ["lovina temple"], "beach": ["lovina dolphin", "lovina beach"], "nature": ["gitgit waterfall", "banjar hot spring"], "shopping": ["lovina market"], "transport": ["lovina road"]},
    "킨타마니": {"food": ["kintamani food", "kintamani coffee"], "culture": ["kintamani temple"], "beach": ["batur lake"], "nature": ["mount batur volcano", "kintamani sunrise"], "shopping": ["kintamani market"], "transport": ["kintamani road"]},
    "타나롯": {"food": ["tanah lot food"], "culture": ["tanah lot temple"], "beach": ["tanah lot sunset", "tanah lot beach"], "nature": ["tanah lot rice field"], "shopping": ["tanah lot souvenir"], "transport": ["tanah lot road"]},
    "베두굴": {"food": ["bedugul food", "bedugul strawberry"], "culture": ["ulun danu temple", "bedugul temple"], "beach": ["bratan lake"], "nature": ["bedugul botanical garden"], "shopping": ["candi kuning market"], "transport": ["bedugul road"]},
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

def fetch_page(url, ua=MOBILE_UA, timeout=15):
    """페이지 가져오기"""
    try:
        r = requests.get(url, headers={'User-Agent': ua, 'Accept': 'text/html,application/xhtml+xml', 'Accept-Language': 'zh-CN,zh;q=0.9'}, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def extract_image_urls(html):
    """HTML에서 이미지 URL 추출"""
    if not html:
        return []
    # 다양한 이미지 URL 패턴
    patterns = [
        r'https?://[^\s\"\'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"\'<>]*)?',
        r'//([^\s\"\'<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"\'<>]*)?)',
        r'data-src=["\']([^"\']+\.(?:jpg|jpeg|png|webp))["\']',
        r'src=["\']([^"\']+\.(?:jpg|jpeg|png|webp))["\']',
        r'"url"\s*:\s*"([^"]+\.(?:jpg|jpeg|png|webp))"',
        r'original["\']?\s*[:=]\s*["\']([^"\']+\.(?:jpg|jpeg|png|webp))',
    ]
    urls = set()
    for p in patterns:
        for m in re.findall(p, html, re.IGNORECASE):
            url = m if m.startswith('http') else ('https:' + m if m.startswith('//') else m)
            # 필터: 아이콘, 로고, 광고 제외
            skip = ['logo', 'icon', 'avatar', 'banner', 'ad_', 'sprite', 'button', 'loading', 'placeholder', '1x1', 'blank']
            if any(s in url.lower() for s in skip):
                continue
            if len(url) > 30:
                urls.add(url)
    return list(urls)

def download_image(url, timeout=15):
    """이미지 다운로드"""
    try:
        r = requests.get(url, headers={'User-Agent': MOBILE_UA, 'Referer': 'https://www.google.com/'}, timeout=timeout, stream=True)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except:
        pass
    return None

def to_webp(data, min_w=600, min_h=400):
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

def scrape_mafengwo(query, limit=30):
    """마펑우 이미지 스크래핑"""
    urls = []
    # 마펑우 검색 API
    search_urls = [
        f'https://www.mafengwo.cn/search/q.php?q={quote(query)}&t=notes',
        f'https://www.mafengwo.cn/search/q.php?q={quote(query)}&t=photo',
        f'https://www.mafengwo.cn/photo/search.php?q={quote(query)}',
    ]
    for surl in search_urls:
        html = fetch_page(surl)
        if html:
            found = extract_image_urls(html)
            # 마펑우 CDN 필터
            found = [u for u in found if 'mafengwo' in u or 'mfw' in u or 'qunar' in u]
            urls.extend(found)
        time.sleep(0.5)
    return urls[:limit]

def scrape_qyer(query, limit=30):
    """큐이얼 이미지 스크래핑"""
    urls = []
    search_urls = [
        f'https://search.qyer.com/word/{quote(query)}',
        f'https://www.qyer.com/search.php?q={quote(query)}&type=photo',
    ]
    for surl in search_urls:
        html = fetch_page(surl)
        if html:
            found = extract_image_urls(html)
            found = [u for u in found if 'qyer' in u or 'qyerimg' in u]
            urls.extend(found)
        time.sleep(0.5)
    return urls[:limit]

def scrape_generic_travel(query, limit=30):
    """일반 여행 사이트 이미지 스크래핑"""
    urls = []
    # 다양한 여행 사이트 검색
    search_urls = [
        f'https://www.mafengwo.cn/search/q.php?q={quote(query)}&t=photo',
        f'https://search.qyer.com/word/{quote(query)}',
        f'https://www.qunar.com/search?query={quote(query)}',
    ]
    for surl in search_urls:
        html = fetch_page(surl)
        if html:
            found = extract_image_urls(html)
            urls.extend(found)
        time.sleep(0.5)
    return urls[:limit]

def scrape_ctrip_images(query, limit=30):
    """씨트립 이미지 스크래핑"""
    urls = []
    # 씨트립 모바일 API 시도
    search_urls = [
        f'https://m.ctrip.com/webapp/you/article/search?keyword={quote(query)}',
        f'https://you.ctrip.com/searchsite/notes/?query={quote(query)}',
    ]
    for surl in search_urls:
        html = fetch_page(surl)
        if html:
            found = extract_image_urls(html)
            found = [u for u in found if 'ctrip' in u or 'dimg' in u]
            urls.extend(found)
        time.sleep(0.5)
    return urls[:limit]

def main():
    log("=" * 60)
    log("🚀 중국 여행 사이트 발리 이미지 스크래퍼")
    log("=" * 60)

    hashes = json.loads(HASH_DB.read_text()) if HASH_DB.exists() else {}
    mapping = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}
    existing_md5s = set(hashes.values())

    total_new = 0
    start_time = time.time()
    time_limit = 8 * 60  # 8분 제한

    for area in AREAS:
        if time.time() - start_time > time_limit:
            log("⏰ 시간 제한 도달, 중단")
            break

        log(f"\n🌍 {area}")
        zh_kw = ZH_KEYWORDS.get(area, ZH_KEYWORDS["우ữu"])
        en_kw = EN_KEYWORDS.get(area, EN_KEYWORDS["우붓"])

        for cat in CATS:
            if time.time() - start_time > time_limit:
                break

            d = IMG_DIR / area / cat
            d.mkdir(parents=True, exist_ok=True)
            cur = len(mapping.get(area, {}).get(cat, []))
            needed = max(0, 150 - cur)

            if needed <= 0:
                continue

            log(f"  🔍 {area}/{cat}: +{needed}장")

            # 기존 pHashes
            eph = []
            for f in list(d.glob('*.webp'))[:60]:
                try:
                    h = phash(Image.open(f))
                    if h: eph.append(h)
                except: pass

            collected = 0
            all_urls = []

            # 1차: 중국어 키워드로 마펑우/큐이얼 검색
            zh_keywords = zh_kw.get(cat, [f"巴厘岛{cat}"])
            for kw in zh_keywords[:3]:
                if collected >= needed: break
                if time.time() - start_time > time_limit: break

                urls = scrape_mafengwo(kw, 20)
                all_urls.extend(urls)
                time.sleep(0.3)

                urls = scrape_qyer(kw, 15)
                all_urls.extend(urls)
                time.sleep(0.3)

                urls = scrape_ctrip_images(kw, 15)
                all_urls.extend(urls)
                time.sleep(0.3)

            # 2차: 영어 키워드 (백업)
            en_keywords = en_kw.get(cat, [f"bali {cat}"])
            for kw in en_keywords[:2]:
                if collected >= needed: break
                if time.time() - start_time > time_limit: break

                urls = scrape_generic_travel(kw, 15)
                all_urls.extend(urls)
                time.sleep(0.3)

            # 중복 URL 제거
            unique_urls = list(dict.fromkeys(all_urls))
            log(f"    📋 후보 URL: {len(unique_urls)}개")

            # 다운로드 및 저장
            for url in unique_urls:
                if collected >= needed: break
                if time.time() - start_time > time_limit: break

                raw = download_image(url)
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

            # 주기적 저장
            HASH_DB.write_text(json.dumps(hashes, ensure_ascii=False, indent=2))
            MAP_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

            if collected > 0:
                log(f"    ✅ +{collected} → {cur + collected}장")

    elapsed = time.time() - start_time
    log(f"\n{'='*60}")
    log(f"✅ 완료! 신규 {total_new}장 ({elapsed:.0f}초)")
    total = sum(len(v) for cats in mapping.values() for v in cats.values())
    log(f"   총 이미지: {total}장")
    log(f"{'='*60}")

if __name__ == '__main__':
    main()
