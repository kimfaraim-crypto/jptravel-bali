#!/usr/bin/env python3
"""
실제 발리 이미지 종합 스크래퍼 v1
- Openverse API (무료, 키 불필요)
- Wikimedia Commons API (무료)
- 지역×카테고리별 맞춤 키워드
- MD5 + pHash 중복 제거
- WebP 변환 (품질 85, 1200x800 이상)
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
PROGRESS_FILE = BASE_DIR / "SCRAPER_PROGRESS.txt"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

# 지역별 + 카테고리별 검색 키워드 (Openverse 쿼리)
AREA_CAT_KEYWORDS = {
    "우붓": {
        "food": ["ubud bali food", "ubud restaurant bali", "babi guling ubud", "ubud warung food", "ubud cafe smoothie bowl", "ubud rice terrace dining", "bali traditional food ubud", "ubud cooking class"],
        "culture": ["ubud temple bali", "ubud palace", "monkey forest ubud", "ubud dance kecak", "ubud art market", "taman saraswati temple", "ubud bali ceremony", "ubud hindu temple"],
        "beach": ["ubud river valley", "ubud campuhan ridge", "bali rice terrace ubud", "ubud jungle", "tibumana waterfall bali", "kanto lampo waterfall", "ubud nature walk"],
        "nature": ["tegalalang rice terrace", "ubud monkey forest", "campuhan ridge walk", "ubud rice paddy", "bali jungle ubud", "ubud waterfall", "ubud botanical"],
        "shopping": ["ubud art market bali", "ubud traditional market", "ubud craft market", "bali art shop ubud", "ubud souvenir shop", "ubud textile market"],
        "transport": ["ubud bali street", "ubud road bali", "bali motorbike ubud", "ubud shuttle bus", "bali driver ubud", "ubud walking tour"],
    },
    "스미냑": {
        "food": ["seminyak restaurant bali", "seminyak beach club food", "seminyak cafe bali", "bali seafood seminyak", "seminyak brunch", "seminyak fine dining", "potato head bali food"],
        "culture": ["seminyak temple bali", "seminyak ceremony", "bali offering seminyak", "seminyak petitenget temple", "bali culture seminyak"],
        "beach": ["seminyak beach bali", "double six beach", "seminyak sunset beach", "seminyak surf", "petitenget beach bali", "seminyak beach club"],
        "nature": ["seminyak rice field bali", "seminyak garden", "bali nature seminyak", "seminyak tropical", "seminyak palm tree"],
        "shopping": ["seminyak boutique bali", "seminyak shopping street", "seminyak spa massage", "bali fashion seminyak", "seminyak villa shopping"],
        "transport": ["seminyak street bali", "seminyak road", "bali scooter seminyak", "seminyak taxi", "seminyak walking"],
    },
    "꾸따": {
        "food": ["kuta bali restaurant", "kuta beach food", "kuta warung", "bali street food kuta", "kuta cafe", "kuta seafood", "legian food bali"],
        "culture": ["kuta temple bali", "bali ceremony kuta", "kuta art", "bali culture kuta", "kuta mosque"],
        "beach": ["kuta beach bali", "kuta surfing", "kuta sunset", "kuta wave", "legian beach bali", "kuta beach sunset", "waterbom bali kuta"],
        "nature": ["kuta beach nature", "bali sunset kuta", "kuta ocean", "kuta palm tree", "kuta tropical"],
        "shopping": ["kuta market bali", "discovery mall bali", "kuta square shopping", "bali souvenir kuta", "kuta beachwalk mall", "kuta art market"],
        "transport": ["kuta street bali", "kuta traffic", "bali airport kuta", "kuta road", "kuta walking street"],
    },
    "사누르": {
        "food": ["sanur restaurant bali", "sanur seafood", "sanur cafe", "bali food sanur", "sanur warung", "sanur breakfast"],
        "culture": ["sanur temple bali", "sanur ceremony", "le mayeur museum", "bali culture sanur", "sanur art"],
        "beach": ["sanur beach bali", "sanur sunrise", "sanur boardwalk", "sanur calm water", "sanur harbor", "sanur beach morning"],
        "nature": ["sanur mangrove bali", "sanur nature", "bali bird sanur", "sanur garden", "sanur tropical"],
        "shopping": ["sanur market bali", "sanur night market", "sanur craft", "bali souvenir sanur", "sanur art shop"],
        "transport": ["sanur cycling bali", "sanur boardwalk bike", "sanur road", "bali boat sanur", "sanur harbor fast boat"],
    },
    "누사두아": {
        "food": ["nusa dua restaurant", "nusa dua resort dining", "bali food nusa dua", "nusa dua seafood", "nusa dua buffet"],
        "culture": ["nusa dua temple", "bali culture nusa dua", "nusa dua ceremony", "devdan show bali", "nusa dua art"],
        "beach": ["nusa dua beach bali", "nusa dua water blow", "nusa dua snorkeling", "nusa dua peninsula", "nusa dua white sand", "nusa dua ocean"],
        "nature": ["nusa dua nature bali", "nusa dua tropical garden", "bali marine nusa dua", "nusa dua coral reef"],
        "shopping": ["bali collection mall nusa dua", "nusa dua shopping", "nusa dua resort shop", "bali souvenir nusa dua"],
        "transport": ["nusa dua road bali", "nusa dua resort area", "bali taxi nusa dua", "nusa dua shuttle"],
    },
    "울루와뚜": {
        "food": ["uluwatu restaurant", "uluwatu beach club", "uluwatu cafe bali", "bali food uluwatu", "single fin uluwatu"],
        "culture": ["uluwatu temple bali", "kecak dance uluwatu", "uluwatu ceremony", "bali hindu uluwatu", "uluwatu cliff temple"],
        "beach": ["uluwatu beach bali", "uluwatu surf", "uluwatu cliff", "blue point beach", "uluwatu cave beach", "padang padang beach"],
        "nature": ["uluwatu cliff bali", "uluwatu ocean view", "bali cliff uluwatu", "uluwatu sunset", "uluwatu tropical"],
        "shopping": ["uluwatu market bali", "uluwatu souvenir", "bali craft uluwatu"],
        "transport": ["uluwatu road bali", "uluwatu cliff road", "bali scooter uluwatu"],
    },
    "짠디다사": {
        "food": ["candidasa restaurant bali", "candidasa seafood", "bali food candidasa", "candidasa warung"],
        "culture": ["candidasa temple bali", "tirta gangga", "besakih temple bali", "candidasa ceremony", "bali culture candidasa"],
        "beach": ["candidasa beach bali", "candidasa coast", "amed beach bali", "padang bai", "candidasa ocean"],
        "nature": ["candidasa nature bali", "east bali nature", "candidasa rice field", "bali east coast", "candidasa mountain"],
        "shopping": ["candidasa market bali", "candidasa craft", "bali souvenir candidasa"],
        "transport": ["candidasa road bali", "bali east road", "candidasa to amed"],
    },
    "로비나": {
        "food": ["lovina restaurant bali", "lovina seafood", "bali food lovina", "lovina warung"],
        "culture": ["lovina temple bali", "singaraja bali", "lovina ceremony", "bali north culture"],
        "beach": ["lovina beach bali", "lovina dolphin", "lovina sunrise", "lovina calm sea", "north bali beach"],
        "nature": ["lovina waterfall bali", "gitgit waterfall", "banjar hot spring", "lovina nature", "north bali nature"],
        "shopping": ["lovina market bali", "singaraja market", "bali north shopping"],
        "transport": ["lovina road bali", "north bali road", "lovina to singaraja"],
    },
    "킨타마니": {
        "food": ["kintamani restaurant bali", "kintamani coffee", "bali food kintamani", "mount batur view restaurant"],
        "culture": ["kintamani temple bali", "batur temple", "trunyan bali", "kintamani ceremony"],
        "beach": ["batur lake bali", "kintamani lake", "bali volcanic lake", "kintamani crater"],
        "nature": ["mount batur bali", "kintamani volcano", "batur sunrise trek", "kintamani caldera", "bali volcano", "kintamani trekking"],
        "shopping": ["kintamani market bali", "kintamani fruit market", "bali highland market"],
        "transport": ["kintamani road bali", "mount batur trek", "bali highland road"],
    },
    "타나롯": {
        "food": ["tanah lot restaurant", "tanah lot cafe", "bali food tanah lot", "tanah lot sunset dining"],
        "culture": ["tanah lot temple bali", "tanah lot ceremony", "tanah lot sunset temple", "bali sea temple", "batu bolong temple"],
        "beach": ["tanah lot beach bali", "tanah lot rock", "tanah lot ocean", "tanah lot wave", "tabanan beach bali"],
        "nature": ["tanah lot sunset bali", "tanah lot rice field", "bali nature tanah lot", "tanah lot cliff"],
        "shopping": ["tanah lot market bali", "tanah lot souvenir", "bali craft tanah lot"],
        "transport": ["tanah lot road bali", "tabanan road", "bali to tanah lot"],
    },
    "베두굴": {
        "food": ["bedugul restaurant bali", "bedugul strawberry", "bali highland food", "bedugul market food"],
        "culture": ["ulun danu bratan temple", "bedugul temple bali", "bratan lake temple", "bali highland temple"],
        "beach": ["bratan lake bali", "bedugul lake", "bali lake bedugul", "ulun danu lake"],
        "nature": ["bedugul botanical garden", "bali highland nature", "bedugul rainforest", "bali mountain bedugul", "bratan lake nature"],
        "shopping": ["bedugul market bali", "candi kuning market", "bedugul fruit market", "bali highland market"],
        "transport": ["bedugul road bali", "bali highland road", "bedugul to singaraja"],
    },
}

# 라이선스 필터 (자유 사용 가능)
LICENSES = "by,by-sa,cc0,pdm"

lock = threading.Lock()
download_count = 0
skip_count = 0
error_count = 0

def load_hashes():
    """기존 해시 DB 로드"""
    if FILE_HASH_DB.exists():
        return json.loads(FILE_HASH_DB.read_text())
    return {}

def save_hashes(hashes):
    """해시 DB 저장"""
    FILE_HASH_DB.write_text(json.dumps(hashes, ensure_ascii=False, indent=2))

def load_mapping():
    """기존 이미지 매핑 로드"""
    if MAPPING_FILE.exists():
        return json.loads(MAPPING_FILE.read_text())
    return {}

def save_mapping(mapping):
    """이미지 매핑 저장"""
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

def compute_md5(data):
    return hashlib.md5(data).hexdigest()

def compute_phash(img):
    """perceptual hash 계산 (8x8 그레이스케일)"""
    try:
        small = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        pixels = list(small.getdata())
        avg = sum(pixels) / len(pixels)
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        return bits
    except:
        return None

def hamming_distance(h1, h2):
    """해밍 거리 계산"""
    if not h1 or not h2 or len(h1) != len(h2):
        return 999
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))

def is_duplicate(data, img, existing_hashes, existing_phashes):
    """중복 여부 확인 (MD5 + pHash)"""
    md5 = compute_md5(data)
    if md5 in existing_hashes:
        return True, md5, None
    
    phash = compute_phash(img)
    if phash:
        for existing in existing_phashes:
            if hamming_distance(phash, existing) <= 5:
                return True, md5, phash
    
    return False, md5, phash

def download_image(url, timeout=15):
    """이미지 다운로드"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.google.com/',
        }
        r = requests.get(url, headers=headers, timeout=timeout, stream=True)
        if r.status_code == 200:
            return r.content
    except:
        pass
    return None

def convert_to_webp(data, min_width=1200, min_height=800):
    """WebP 변환 + 크기 체크"""
    try:
        img = Image.open(BytesIO(data))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        w, h = img.size
        if w < min_width or h < min_height:
            return None, None
        
        # 크기 조정 (너무 크면 리사이즈)
        if w > 2000 or h > 1400:
            ratio = min(2000/w, 1400/h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        buf = BytesIO()
        img.save(buf, format='WEBP', quality=85, method=4)
        return buf.getvalue(), img
    except:
        return None, None

def search_openverse(query, page_size=20, page=1):
    """Openverse API 검색"""
    try:
        r = requests.get('https://api.openverse.org/v1/images/', 
            params={
                'q': query,
                'page_size': page_size,
                'page': page,
                'license': LICENSES,
                'source': 'flickr,wikimedia,stocksnap',
            },
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=20)
        if r.status_code == 200:
            data = r.json()
            return data.get('results', [])
        elif r.status_code == 429:
            time.sleep(5)
            return search_openverse(query, page_size, page)
    except:
        pass
    return []

def search_wikimedia(query, limit=20):
    """Wikimedia Commons 검색"""
    try:
        r = requests.get('https://commons.wikimedia.org/w/api.php', params={
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srnamespace': '6',
            'srlimit': limit,
            'format': 'json',
        }, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        if r.status_code == 200:
            results = r.json().get('query', {}).get('search', [])
            image_urls = []
            for item in results:
                title = item.get('title', '')
                # Get actual image URL
                try:
                    r2 = requests.get('https://commons.wikimedia.org/w/api.php', params={
                        'action': 'query',
                        'titles': title,
                        'prop': 'imageinfo',
                        'iiprop': 'url',
                        'iiurlwidth': 1400,
                        'format': 'json',
                    }, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    pages = r2.json().get('query', {}).get('pages', {})
                    for page in pages.values():
                        for ii in page.get('imageinfo', []):
                            url = ii.get('thumburl') or ii.get('url')
                            if url:
                                image_urls.append({'url': url, 'title': title, 'source': 'wikimedia'})
                except:
                    pass
            return image_urls
    except:
        pass
    return []

def log_progress(msg):
    """진행 상황 로그"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def scrape_area_category(area, cat, keywords, target_count=50):
    """지역+카테고리별 이미지 스크래핑"""
    global download_count, skip_count, error_count
    
    area_dir = OUTPUT_DIR / area / cat
    area_dir.mkdir(parents=True, exist_ok=True)
    
    # 기존 이미지 수 확인
    existing = list(area_dir.glob('*.webp'))
    if len(existing) >= target_count:
        log_progress(f"⏭️ {area}/{cat}: 이미 {len(existing)}장 보유, 건너뜀")
        return 0
    
    needed = target_count - len(existing)
    log_progress(f"🔍 {area}/{cat}: {needed}장 필요 (현재 {len(existing)}장)")
    
    # 기존 해시 로드
    with lock:
        all_hashes = load_hashes()
        mapping = load_mapping()
    
    existing_hashes = set(all_hashes.values())
    existing_phashes = []
    
    # 기존 이미지의 pHash 수집
    for img_path in area_dir.glob('*.webp'):
        try:
            img = Image.open(img_path)
            ph = compute_phash(img)
            if ph:
                existing_phashes.append(ph)
        except:
            pass
    
    collected = 0
    tried_urls = set()
    
    # Openverse에서 검색 (1차 + 2차 키워드)
    all_keywords = keywords + [kw + " indonesia" for kw in keywords] + [kw + " travel" for kw in keywords[:3]]
    for kw in all_keywords:
        if collected >= needed:
            break
        
        # 여러 페이지 검색
        for pg in range(1, 4):
            if collected >= needed:
                break
            results = search_openverse(kw, page_size=30, page=pg)
            time.sleep(1.5)  # Rate limit
            if not results:
                break
            
            for item in results:
                if collected >= needed:
                    break
                
                url = item.get('url', '')
                if not url or url in tried_urls:
                    continue
                tried_urls.add(url)
                
                # 다운로드
                data = download_image(url)
                if not data:
                    error_count += 1
                    continue
                
                # WebP 변환
                webp_data, img = convert_to_webp(data)
                if not webp_data:
                    skip_count += 1
                    continue
                
                # 중복 체크
                is_dup, md5, phash = is_duplicate(webp_data, img, existing_hashes, existing_phashes)
                if is_dup:
                    skip_count += 1
                    continue
                
                # 저장
                with lock:
                    existing_num = len(list(area_dir.glob('*.webp')))
                    filename = f"{area}_{cat}_{existing_num+1:04d}.webp"
                    filepath = area_dir / filename
                    
                    filepath.write_bytes(webp_data)
                    
                    all_hashes[str(filepath)] = md5
                    existing_hashes.add(md5)
                    if phash:
                        existing_phashes.append(phash)
                    
                    # 매핑 업데이트
                    if area not in mapping:
                        mapping[area] = {}
                    if cat not in mapping[area]:
                        mapping[area][cat] = []
                    mapping[area][cat].append(filename)
                    
                    save_hashes(all_hashes)
                    save_mapping(mapping)
                
                collected += 1
                download_count += 1
                
                source = item.get('source', 'unknown')
                creator = item.get('creator', 'unknown')
                log_progress(f"  ✅ {area}/{cat}/{filename} (from {source} by {creator})")
                
                time.sleep(0.5)  # Rate limit
    
    # Wikimedia에서 추가 검색 (Openverse로 부족한 경우)
    if collected < needed:
        log_progress(f"  📚 {area}/{cat}: Wikimedia에서 추가 검색...")
        for kw in keywords[:3]:
            if collected >= needed:
                break
            results = search_wikimedia(kw + " bali")
            time.sleep(1)
            for item in results:
                if collected >= needed:
                    break
                url = item.get('url', '')
                if not url or url in tried_urls:
                    continue
                tried_urls.add(url)
                
                data = download_image(url)
                if not data:
                    continue
                webp_data, img = convert_to_webp(data, min_width=800, min_height=600)
                if not webp_data:
                    continue
                
                is_dup, md5, phash = is_duplicate(webp_data, img, existing_hashes, existing_phashes)
                if is_dup:
                    continue
                
                with lock:
                    existing_num = len(list(area_dir.glob('*.webp')))
                    filename = f"{area}_{cat}_{existing_num+1:04d}.webp"
                    filepath = area_dir / filename
                    filepath.write_bytes(webp_data)
                    all_hashes[str(filepath)] = md5
                    existing_hashes.add(md5)
                    if phash:
                        existing_phashes.append(phash)
                    if area not in mapping:
                        mapping[area] = {}
                    if cat not in mapping[area]:
                        mapping[area][cat] = []
                    mapping[area][cat].append(filename)
                    save_hashes(all_hashes)
                    save_mapping(mapping)
                
                collected += 1
                download_count += 1
                log_progress(f"  ✅ {area}/{cat}/{filename} (wikimedia)")
                time.sleep(0.5)
    
    log_progress(f"📊 {area}/{cat}: {collected}장 신규 다운로드 완료")
    return collected

def main():
    global download_count, skip_count, error_count
    
    log_progress("=" * 60)
    log_progress("🚀 실제 발리 이미지 스크래퍼 시작")
    log_progress(f"   대상: {len(AREAS)} 지역 × {len(AREA_CAT_KEYWORDS['우붓'])} 카테고리")
    log_progress("=" * 60)
    
    total_start = time.time()
    total_collected = 0
    
    # 지역별 순차 실행 (API rate limit 때문)
    for area in AREAS:
        log_progress(f"\n🌍 지역: {area}")
        keywords_by_cat = AREA_CAT_KEYWORDS.get(area, AREA_CAT_KEYWORDS["우붓"])
        
        for cat, keywords in keywords_by_cat.items():
            count = scrape_area_category(area, cat, keywords, target_count=25)
            total_collected += count
            time.sleep(1)  # 카테고리 간 대기
    
    elapsed = time.time() - total_start
    
    log_progress("\n" + "=" * 60)
    log_progress(f"✅ 스크래핑 완료!")
    log_progress(f"   신규 다운로드: {download_count}장")
    log_progress(f"   중복 스킵: {skip_count}장")
    log_progress(f"   에러: {error_count}건")
    log_progress(f"   소요 시간: {elapsed:.0f}초")
    log_progress("=" * 60)
    
    # 최종 매핑 통계
    mapping = load_mapping()
    total_images = sum(len(imgs) for cats in mapping.values() for imgs in cats.values())
    log_progress(f"\n📊 최종 이미지 통계:")
    for area in AREAS:
        if area in mapping:
            cats = mapping[area]
            total = sum(len(imgs) for imgs in cats.values())
            log_progress(f"   {area}: {total}장")

if __name__ == '__main__':
    main()
