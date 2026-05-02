#!/usr/bin/env python3
"""
Bali Real Image Scraper v2
Downloads REAL Bali-specific images from free APIs:
- Openverse API (no key needed)
- Wikimedia Commons API (no key needed)

Resumable: detects existing files and only downloads what's needed.
Uses MD5 + simple pHash for deduplication.
Saves as WebP, quality 85, min 1200x800.
"""

import os, sys, json, hashlib, time, random
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images_real"
PROGRESS_FILE = BASE_DIR / "SCRAPER_PROGRESS_V2.txt"
MAPPING_FILE = BASE_DIR / "image_mapping_real.json"
GLOBAL_HASH_FILE = BASE_DIR / "global_hashes_real.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]
TARGET_PER_COMBO = 25

AREA_KEYWORDS = {
    "우ữu": {
        "food": ["ubud bali food", "ubud restaurant", "ubud warung", "ubud smoothie bowl", "babi guling ubud", "ubud cafe bali", "ubud healthy food", "ubud vegan restaurant", "ubud cooking class", "ubud rice terrace cafe"],
        "culture": ["ubud temple", "monkey forest ubud", "ubud palace bali", "ubud art market", "ubud dance kecak", "ubud painting", "ubud traditional", "campuhan ridge ubud", "ubud bali ceremony", "ubud hindu temple"],
        "beach": ["ubud river valley", "ubud waterfall", "ubud nature", "campuhan ridge walk", "ubud rice field", "tegalalang rice terrace", "ubud jungle", "ubud valley view", "bali rice terrace", "ubud green landscape"],
        "nature": ["tegalalang rice terrace", "monkey forest ubud", "campuhan ridge ubud", "ubud waterfall", "ubud rice paddy", "ubud jungle bali", "ubud botanical", "bali rice field ubud", "ubud tropical garden", "ubud nature walk"],
        "shopping": ["ubud art market", "ubud craft market", "ubud shopping", "ubud silver jewelry", "ubud batik shop", "ubud souvenir", "ubud traditional market", "ubud artisan", "ubud wood carving shop", "ubud gallery"],
        "transport": ["ubud bali road", "ubud scooter", "bali motorbike ubud", "ubud street", "ubud bridge", "ubud walking", "bali transport ubud", "ubud village road", "ubud path", "ubud pathway"],
    },
    "스미냑": {
        "food": ["seminyak restaurant", "seminyak bali food", "potato head bali food", "seminyak beach club dining", "seminyak cafe", "seminyak brunch", "seminyak seafood", "ku de ta bali", "seminyak fine dining", "seminyak smoothie bowl"],
        "culture": ["seminyak temple bali", "seminyak ceremony", "seminyak bali culture", "petitenget temple", "seminyak art gallery", "seminyak bali tradition", "seminyak offering", "seminyak bali dance", "seminyak hindu", "petitenget ceremony"],
        "beach": ["seminyak beach", "double six beach bali", "seminyak beach sunset", "seminyak surfing", "seminyak beach club", "petitenget beach", "seminyak ocean", "seminyak coast", "seminyak waves", "seminyak sand"],
        "nature": ["seminyak garden", "seminyak tropical", "seminyak palm tree", "seminyak nature", "seminyak rice field", "petitenget park", "seminyak green", "bali nature seminyak", "seminyak flower", "seminyak landscape"],
        "shopping": ["seminyak shopping", "seminyak boutique", "seminyak fashion bali", "seminyak craft", "seminyak souvenir", "seminyak designer", "seminyak market", "seminyak art shop", "seminyak villa decor", "seminyak jewelry"],
        "transport": ["seminyak street", "seminyak road bali", "seminyak motorbike", "seminyak traffic", "seminyak walking", "bali transport seminyak", "seminyak taxi", "seminyak scooter", "seminyak lane", "seminyak pathway"],
    },
    "꾸따": {
        "food": ["kuta bali food", "kuta restaurant", "kuta beach dining", "kuta seafood", "kuta cafe", "kuta street food", "kuta warung", "kuta nasi goreng", "kuta smoothie", "waterbom bali food"],
        "culture": ["kuta temple bali", "kuta bali ceremony", "kuta art", "kuta traditional", "kuta bali culture", "kuta monument", "kuta heritage", "legian temple", "kuta bali offering", "kuta hindu shrine"],
        "beach": ["kuta beach", "kuta beach sunset", "kuta surfing", "kuta waves", "kuta beach bali", "legian beach", "kuta ocean", "kuta coast", "kuta beach walk", "kuta sand surf"],
        "nature": ["kuta park bali", "kuta garden", "kuta tropical", "kuta nature", "bali nature kuta", "kuta palm", "kuta green", "kuta landscape", "kuta flower", "kuta sunrise nature"],
        "shopping": ["kuta shopping", "discovery mall bali", "kuta market", "kuta art market", "kuta souvenir shop", "kuta beachwalk mall", "kuta craft", "kuta bargain", "kuta fashion", "kuta bali shopping street"],
        "transport": ["kuta street", "kuta road bali", "kuta traffic", "kuta motorbike", "kuta taxi", "bali transport kuta", "kuta airport", "kuta scooter", "kuta walking street", "kuta lane"],
    },
    "사누르": {
        "food": ["sanur restaurant bali", "sanur food", "sanur beach cafe", "sanur seafood", "sanur brunch", "sanur warung", "sanur breakfast", "sanur dining", "sanur coffee", "sanur night market food"],
        "culture": ["sanur temple bali", "sanur ceremony", "sanur bali culture", "le mayeur museum", "sanur art", "sanur traditional", "sanur bali dance", "sanur offering", "sanur hindu", "sanur heritage"],
        "beach": ["sanur beach", "sanur beach sunrise", "sanur boardwalk", "sanur coast", "sanur ocean", "sanur reef", "sanur sand", "sanur sea", "sanur harbor", "sanur beach bali"],
        "nature": ["sanur garden", "sanur nature", "sanur mangrove", "sanur tropical", "sanur green", "bali nature sanur", "sanur park", "sanur palm", "sanur flower", "sanur mangrove forest"],
        "shopping": ["sanur market", "sanur shopping", "sanur art market", "sanur craft", "sanur souvenir", "sanur night market", "sanur boutique", "sanur gallery", "sanur traditional market", "sanur shop"],
        "transport": ["sanur road", "sanur cycling bali", "sanur bike", "sanur boardwalk", "sanur street", "sanur ferry", "sanur harbor boat", "bali transport sanur", "sanur scooter", "sanur walking path"],
    },
    "누사두아": {
        "food": ["nusa dua restaurant", "nusa dua food", "nusa dua resort dining", "nusa dua seafood", "nusa dua beach club", "nusa dua cafe", "nusa dua fine dining", "nusa dua breakfast", "nusa dua bali food", "nusa dua luxury dining"],
        "culture": ["nusa dua temple", "nusa dua bali culture", "nusa dua ceremony", "nusa dua art", "nusa dua traditional", "nusa dua heritage", "nusa dua balinese", "nusa dua hindu", "nusa dua offering", "nusa dua dance"],
        "beach": ["nusa dua beach", "nusa dua water blow", "nusa dua snorkeling", "nusa dua ocean", "nusa dua coast", "nusa dua reef", "nusa dua sand", "nusa dua sea", "nusa dua peninsula", "nusa dua beach bali"],
        "nature": ["nusa dua garden", "nusa dua tropical", "nusa dua nature", "nusa dua green", "nusa dua landscape", "bali nature nusa dua", "nusa dua park", "nusa dua palm", "nusa dua flower", "nusa dua botanical"],
        "shopping": ["bali collection mall", "nusa dua shopping", "nusa dua market", "nusa dua craft", "nusa dua souvenir", "nusa dua boutique", "nusa dua gallery", "nusa dua shop", "nusa dua art", "nusa dua luxury shop"],
        "transport": ["nusa dua road", "nusa dua street", "nusa dua transport", "nusa dua taxi", "nusa dua motorbike", "nusa dua walking", "nusa dua resort shuttle", "bali transport nusa dua", "nusa dua scooter", "nusa dua pathway"],
    },
    "울루와뚜": {
        "food": ["uluwatu restaurant", "uluwatu food", "uluwatu cliff dining", "uluwatu beach club food", "uluwatu cafe", "uluwatu seafood", "uluwatu sunset dining", "single fin uluwatu food", "uluwatu warung", "uluwatu bali food"],
        "culture": ["uluwatu temple", "uluwatu kecak dance", "uluwatu ceremony", "uluwatu bali culture", "uluwatu hindu temple", "uluwatu traditional", "uluwatu offering", "uluwatu ritual", "uluwatu cliff temple", "uluwatu bali tradition"],
        "beach": ["uluwatu beach", "uluwatu surf", "uluwatu cliff", "uluwatu ocean", "uluwatu wave", "blue point beach uluwatu", "uluwatu coast", "uluwatu cave beach", "uluwatu sand", "uluwatu sea cliff"],
        "nature": ["uluwatu cliff nature", "uluwatu tropical", "uluwatu garden", "uluwatu green", "uluwatu landscape", "bali nature uluwatu", "uluwatu palm", "uluwatu sunset nature", "uluwatu ocean view", "uluwatu rocky coast"],
        "shopping": ["uluwatu market", "uluwatu shopping", "uluwatu craft", "uluwatu souvenir", "uluwatu art", "uluwatu boutique", "uluwatu gallery", "uluwatu shop", "uluwatu bali market", "uluwatu traditional craft"],
        "transport": ["uluwatu road", "uluwatu street", "uluwatu motorbike", "uluwatu cliff road", "uluwatu transport", "uluwatu scooter", "uluwatu pathway", "bali transport uluwatu", "uluwatu coastal road", "uluwatu walking"],
    },
    "짠디다사": {
        "food": ["candidasa restaurant", "candidasa food", "candidasa bali dining", "candidasa seafood", "candidasa cafe", "candidasa warung", "east bali food", "candidasa beach dining", "candidasa coffee", "candidasa bali food"],
        "culture": ["candidasa temple", "tirta gangga", "besakih temple", "candidasa bali culture", "candidasa ceremony", "east bali temple", "candidasa traditional", "candidasa hindu", "candidasa offering", "candidasa art"],
        "beach": ["candidasa beach", "candidasa coast", "candidasa ocean", "candidasa reef", "candidasa sea", "amed beach", "padang bai beach", "candidasa sand", "east bali beach", "candidasa waterfront"],
        "nature": ["candidasa nature", "candidasa tropical", "candidasa garden", "tirta gangga garden", "candidasa rice field", "east bali nature", "candidasa green", "candidasa landscape", "candidasa mountain", "candidasa waterfall"],
        "shopping": ["candidasa market", "candidasa shopping", "candidasa craft", "candidasa souvenir", "candidasa art", "east bali market", "candidasa gallery", "candidasa shop", "candidasa traditional market", "candidasa bali shopping"],
        "transport": ["candidasa road", "candidasa street", "candidasa motorbike", "candidasa transport", "east bali road", "candidasa scooter", "padang bai harbor", "candidasa boat", "candidasa pathway", "bali transport candidasa"],
    },
    "로비나": {
        "food": ["lovina restaurant", "lovina food", "lovina bali dining", "lovina seafood", "lovina cafe", "lovina warung", "north bali food", "lovina beach dining", "lovina coffee", "singaraja food"],
        "culture": ["lovina temple", "lovina ceremony", "lovina bali culture", "singaraja temple", "lovina traditional", "north bali temple", "lovina hindu", "lovina offering", "lovina art", "lovina heritage"],
        "beach": ["lovina beach", "lovina dolphin", "lovina sunrise", "lovina coast", "lovina black sand", "lovina ocean", "lovina sea", "north bali beach", "lovina boat", "lovina calm sea"],
        "nature": ["lovina nature", "gitgit waterfall", "banjar hot spring", "lovina tropical", "lovina garden", "north bali nature", "lovina green", "lovina landscape", "lovina mountain", "lovina botanical"],
        "shopping": ["lovina market", "lovina shopping", "lovina craft", "lovina souvenir", "singaraja market", "north bali market", "lovina art", "lovina gallery", "lovina shop", "lovina traditional market"],
        "transport": ["lovina road", "lovina street", "lovina motorbike", "lovina boat", "lovina transport", "north bali road", "lovina scooter", "singaraja road", "lovina pathway", "bali transport lovina"],
    },
    "킨타마니": {
        "food": ["kintamani restaurant", "kintamani food", "kintamani bali dining", "kintamani coffee", "kintamani view restaurant", "mount batur food", "kintamani warung", "kintamani cafe", "batur lake food", "kintamani breakfast"],
        "culture": ["kintamani temple", "kintamani ceremony", "kintamani bali culture", "mount batur temple", "trunyan village", "kintamani traditional", "kintamani hindu", "kintamani offering", "kintamani art", "batur temple"],
        "beach": ["batur lake", "kintamani lake", "kintamani crater", "batur crater lake", "kintamani water", "kintamani volcanic", "batur caldera", "kintamani island", "trunyan lake", "kintamani shore"],
        "nature": ["mount batur", "kintamani volcano", "batur sunrise", "kintamani trekking", "kintamani crater", "batur landscape", "kintamani mountain", "kintamani caldera", "batur lava field", "kintamani nature"],
        "shopping": ["kintamani market", "kintamani shopping", "kintamani craft", "kintamani souvenir", "kintamani art", "batur market", "kintamani coffee shop", "kintamani gallery", "kintamani traditional market", "kintamani bali shopping"],
        "transport": ["kintamani road", "kintamani mountain road", "kintamani motorbike", "kintamani transport", "batur road", "kintamani scooter", "kintamani trekking path", "kintamani pathway", "bali transport kintamani", "kintamani winding road"],
    },
    "타나롯": {
        "food": ["tanah lot restaurant", "tanah lot food", "tanah lot dining", "tanah lot cafe", "tanah lot bali food", "tanah lot sunset dining", "tanah lot warung", "tabanan food", "tanah lot seafood", "tanah lot bali restaurant"],
        "culture": ["tanah lot temple", "tanah lot ceremony", "tanah lot sunset temple", "tanah lot bali culture", "tanah lot ritual", "tanah lot hindu", "tanah lot offering", "batu bolong temple", "tanah lot traditional", "tanah lot kecak"],
        "beach": ["tanah lot beach", "tanah lot cliff", "tanah lot ocean", "tanah lot coast", "tanah lot sea temple", "tanah lot rock", "tanah lot wave", "tanah lot sand", "tanah lot tide", "tabanan beach"],
        "nature": ["tanah lot rice field", "tanah lot sunset", "tanah lot tropical", "tanah lot nature", "tanah lot landscape", "tanah lot green", "tabanan rice terrace", "tanah lot garden", "tanah lot palm", "tanah lot cliff nature"],
        "shopping": ["tanah lot market", "tanah lot shopping", "tanah lot craft", "tanah lot souvenir", "tanah lot art", "tabanan market", "tanah lot gallery", "tanah lot shop", "tanah lot traditional market", "tanah lot bali shopping"],
        "transport": ["tanah lot road", "tanah lot path", "tanah lot motorbike", "tanah lot transport", "tanah lot walking", "tabanan road", "tanah lot scooter", "tanah lot pathway", "bali transport tanah lot", "tanah lot coastal road"],
    },
    "베두굴": {
        "food": ["bedugul restaurant", "bedugul food", "bedugul bali dining", "bedugul strawberry", "bedugul cafe", "bedugul warung", "bedugul coffee", "bedugul market food", "bedugul highland food", "candi kuning food"],
        "culture": ["ulun danu bratan", "bedugul temple", "bedugul ceremony", "bedugul bali culture", "bratan lake temple", "bedugul hindu", "bedugul offering", "bedugul traditional", "bedugul art", "candi kuning temple"],
        "beach": ["bratan lake", "bedugul lake", "bedugul water", "bratan lake bali", "bedugul lake temple", "bedugul reservoir", "bedugul calm water", "bedugul pond", "bedugul reflection", "bedugul lake view"],
        "nature": ["bedugul botanical garden", "bedugul highland", "bedugul nature", "bedugul mountain", "bedugul tropical garden", "bedugul forest", "bedugul green", "bedugul landscape", "bedugul misty", "bedugul cool climate"],
        "shopping": ["candi kuning market", "bedugul market", "bedugul shopping", "bedugul fruit market", "bedugul strawberry market", "bedugul craft", "bedugul souvenir", "bedugul flower market", "bedugul vegetable market", "bedugul art"],
        "transport": ["bedugul road", "bedugul mountain road", "bedugul motorbike", "bedugul transport", "bedugul scooter", "bedugul winding road", "bedugul pathway", "bali transport bedugul", "bedugul highland road", "bedugul street"],
    },
}
# Fix the key if wrong
if "우ữu" in AREA_KEYWORDS:
    AREA_KEYWORDS["우붓"] = AREA_KEYWORDS.pop("우ữu")

session = requests.Session()
session.headers.update({
    "User-Agent": "BaliTravelBlog/1.0 (Educational; admin@example.com)"
})

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def simple_phash(img, hash_size=8):
    try:
        img_small = img.convert("L").resize((hash_size, hash_size), Image.LANCZOS)
        pixels = list(img_small.getdata())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if p > avg else "0" for p in pixels)
        return hex(int(bits, 2))[2:].zfill(hash_size * hash_size // 4)
    except:
        return None

def md5_hash(data):
    return hashlib.md5(data).hexdigest()

def download_image(url, timeout=20):
    try:
        r = session.get(url, timeout=timeout, stream=True)
        if r.status_code != 200:
            return None
        data = r.content
        if len(data) < 5000:
            return None
        img = Image.open(BytesIO(data))
        img.load()
        if img.mode in ("RGBA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        return img
    except:
        return None

def search_openverse(query, page_size=20, page=1):
    try:
        r = session.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "page_size": page_size, "page": page, "license": "cc0,by,by-sa"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            results = []
            for img in data.get("results", []):
                url = img.get("url", "")
                w = img.get("width", 0) or 0
                h = img.get("height", 0) or 0
                if url and w >= 600 and h >= 400:
                    results.append({"url": url, "width": w, "height": h})
            return results
        elif r.status_code == 429:
            time.sleep(30)
    except:
        pass
    return []

def search_wikimedia(query, limit=20):
    try:
        r = session.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "generator": "search",
                "gsrsearch": f"filetype:bitmap {query}",
                "gsrnamespace": "6", "gsrlimit": limit,
                "prop": "imageinfo",
                "iiprop": "url|size|mime", "iiurlwidth": 1400,
                "format": "json",
            },
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            results = []
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                for ii in page.get("imageinfo", []):
                    url = ii.get("thumburl") or ii.get("url", "")
                    w = ii.get("thumbwidth") or ii.get("width", 0)
                    h = ii.get("thumbheight") or ii.get("height", 0)
                    mime = ii.get("mime", "")
                    if url and "image" in mime and w >= 600 and h >= 400:
                        results.append({"url": url, "width": w, "height": h})
            return results
    except:
        pass
    return []

def get_next_filename(output_dir, area, category):
    """Find the next available filename number."""
    existing = sorted(output_dir.glob(f"{area}_{category}_*.webp"))
    if not existing:
        return 1
    max_num = 0
    for f in existing:
        try:
            num = int(f.stem.split("_")[-1])
            max_num = max(max_num, num)
        except:
            pass
    return max_num + 1

def scrape_combo(area, category, global_hashes):
    """Download images for one area/category combo."""
    output_dir = OUTPUT_DIR / area / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    existing_count = len(list(output_dir.glob("*.webp")))
    need = max(0, TARGET_PER_COMBO - existing_count)
    
    if need <= 0:
        return 0
    
    combo = f"{area}/{category}"
    log(f"  {combo}: {existing_count} existing, need {need} more")
    
    keywords = AREA_KEYWORDS.get(area, {}).get(category, [f"{area} bali {category}"])
    candidates = []
    
    # Search with multiple keywords
    for kw in keywords[:5]:
        results = search_openverse(kw, page_size=15)
        candidates.extend(results)
        time.sleep(1.5)  # Respect rate limits
        
        results = search_wikimedia(kw, limit=10)
        candidates.extend(results)
        time.sleep(1.5)
    
    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for c in candidates:
        if c["url"] not in seen_urls:
            seen_urls.add(c["url"])
            unique.append(c)
    
    random.shuffle(unique)
    log(f"  {combo}: {len(unique)} unique candidates")
    
    # Load existing local hashes
    local_hashes = set()
    for f in output_dir.glob("*.webp"):
        try:
            with open(f, "rb") as fh:
                local_hashes.add(md5_hash(fh.read()))
        except:
            pass
    
    next_num = get_next_filename(output_dir, area, category)
    downloaded = 0
    
    for candidate in unique:
        if downloaded >= need:
            break
        
        img = download_image(candidate["url"])
        if img is None:
            continue
        
        # Upscale if needed
        w, h = img.size
        if w < 1200 or h < 800:
            if w >= 600 and h >= 400:
                ratio = max(1200 / w, 800 / h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            else:
                continue
        
        # Check hashes
        buf = BytesIO()
        img.save(buf, "WEBP", quality=85)
        webp_data = buf.getvalue()
        file_md5 = md5_hash(webp_data)
        
        if file_md5 in global_hashes or file_md5 in local_hashes:
            continue
        
        ph = simple_phash(img)
        if ph and ph in global_hashes:
            continue
        
        # Save
        filename = f"{area}_{category}_{next_num:04d}.webp"
        filepath = output_dir / filename
        with open(filepath, "wb") as f:
            f.write(webp_data)
        
        global_hashes.add(file_md5)
        if ph:
            global_hashes.add(ph)
        local_hashes.add(file_md5)
        
        next_num += 1
        downloaded += 1
    
    log(f"  {combo}: +{downloaded} downloaded (total: {existing_count + downloaded})")
    return downloaded

def main():
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write("")
    
    log("=" * 60)
    log("Bali Real Image Scraper v2")
    log(f"Target: {TARGET_PER_COMBO} per combo × {len(AREAS)*len(CATEGORIES)} combos")
    log("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    global_hashes = set()
    if GLOBAL_HASH_FILE.exists():
        try:
            with open(GLOBAL_HASH_FILE) as f:
                global_hashes = set(json.load(f))
        except:
            pass
    
    total = 0
    for area in AREAS:
        log(f"\n🌍 {area}")
        for cat in CATEGORIES:
            n = scrape_combo(area, cat, global_hashes)
            total += n
            
            # Save hashes periodically
            with open(GLOBAL_HASH_FILE, "w") as f:
                json.dump(list(global_hashes), f)
    
    log(f"\n{'='*60}")
    log(f"✅ DONE! Total new images: {total}")
    log(f"{'='*60}")
    
    # Summary
    log("\n📊 Summary:")
    for area in AREAS:
        cnt = 0
        for cat in CATEGORIES:
            d = OUTPUT_DIR / area / cat
            if d.exists():
                cnt += len(list(d.glob("*.webp")))
        log(f"  {area}: {cnt}")

if __name__ == "__main__":
    main()
