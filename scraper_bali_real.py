#!/usr/bin/env python3
"""
Bali Real Image Scraper
Downloads REAL Bali-specific images from free APIs:
- Openverse API (no key needed)
- Wikimedia Commons API (no key needed)

For each of 11 areas × 6 categories, downloads 20+ relevant images.
Uses MD5 + simple pHash for deduplication.
Saves as WebP, quality 85, min 1200x800.
"""

import os, sys, json, hashlib, time, random, struct
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images_real"
PROGRESS_FILE = BASE_DIR / "SCRAPER_PROGRESS.txt"
MAPPING_FILE = BASE_DIR / "image_mapping_real.json"
GLOBAL_HASH_FILE = BASE_DIR / "global_hashes_real.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]

# Area-specific + category-specific search keywords
AREA_KEYWORDS = {
    "우붓": {
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

# Session for connection reuse
session = requests.Session()
session.headers.update({
    "User-Agent": "BaliTravelBlog/1.0 (Educational project; contact: admin@example.com)"
})

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def simple_phash(img, hash_size=8):
    """Simple perceptual hash using PIL - returns hex string."""
    try:
        img_small = img.convert("L").resize((hash_size, hash_size), Image.LANCZOS)
        pixels = list(img_small.getdata())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if p > avg else "0" for p in pixels)
        # Convert to hex
        return hex(int(bits, 2))[2:].zfill(hash_size * hash_size // 4)
    except:
        return None

def md5_hash(data):
    return hashlib.md5(data).hexdigest()

def check_min_size(img, min_w=1200, min_h=800):
    w, h = img.size
    return w >= min_w and h >= min_h

def download_and_convert(url, timeout=20):
    """Download image from URL, return (image_data, img) or None."""
    try:
        r = session.get(url, timeout=timeout, stream=True)
        if r.status_code != 200:
            return None
        data = r.content
        if len(data) < 5000:  # Too small, likely error page
            return None
        img = Image.open(BytesIO(data))
        img.load()
        # Convert RGBA to RGB
        if img.mode in ("RGBA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        return data, img
    except Exception as e:
        return None

def save_as_webp(img, path, quality=85):
    """Save image as WebP."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "WEBP", quality=quality)

def search_openverse(query, page_size=20, page=1):
    """Search Openverse API for images."""
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
                title = img.get("title", "")
                if url and w >= 600 and h >= 400:
                    results.append({"url": url, "width": w, "height": h, "title": title, "source": "openverse"})
            return results
        elif r.status_code == 429:
            log(f"  Rate limited on Openverse, sleeping 30s...")
            time.sleep(30)
            return []
    except Exception as e:
        log(f"  Openverse error: {e}")
    return []

def search_wikimedia(query, limit=20):
    """Search Wikimedia Commons for images."""
    try:
        r = session.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"filetype:bitmap {query}",
                "gsrnamespace": "6",
                "gsrlimit": limit,
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": 1400,
                "format": "json",
            },
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            results = []
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                iis = page.get("imageinfo", [])
                for ii in iis:
                    url = ii.get("thumburl") or ii.get("url", "")
                    w = ii.get("thumbwidth") or ii.get("width", 0)
                    h = ii.get("thumbheight") or ii.get("height", 0)
                    mime = ii.get("mime", "")
                    if url and "image" in mime and w >= 600 and h >= 400:
                        results.append({"url": url, "width": w, "height": h, "title": page.get("title", ""), "source": "wikimedia"})
            return results
    except Exception as e:
        log(f"  Wikimedia error: {e}")
    return []

def search_flickr(query, per_page=20, page=1):
    """Search Flickr public API (no key needed for basic search)."""
    try:
        r = session.get(
            "https://www.flickr.com/services/rest/",
            params={
                "method": "flickr.photos.search",
                "text": query,
                "per_page": per_page,
                "page": page,
                "format": "json",
                "nojsoncallback": "1",
                "license": "1,2,3,4,5,6,9,10",
                "sort": "relevance",
                "extras": "url_l,url_o,url_k,url_h,url_b",
                "media": "photos",
                "safe_search": "1",
                "content_type": "1",
            },
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            results = []
            for photo in data.get("photos", {}).get("photo", []):
                # Try to get largest available URL
                url = photo.get("url_o") or photo.get("url_k") or photo.get("url_h") or photo.get("url_b") or photo.get("url_l", "")
                if not url:
                    continue
                w = int(photo.get("width_o", 0) or photo.get("width_k", 0) or photo.get("width_h", 0) or photo.get("width_b", 0) or photo.get("width_l", 0) or 0)
                h = int(photo.get("height_o", 0) or photo.get("height_k", 0) or photo.get("height_h", 0) or photo.get("height_b", 0) or photo.get("height_l", 0) or 0)
                results.append({"url": url, "width": w, "height": h, "title": photo.get("title", ""), "source": "flickr"})
            return results
    except Exception as e:
        pass  # Flickr might not work without key
    return []

TARGET_PER_COMBO = 25  # Target images per area/category combo

def scrape_area_category(area, category, existing_hashes, mapping):
    """Scrape images for one area/category combination."""
    combo_key = f"{area}/{category}"
    output_dir = OUTPUT_DIR / area / category
    os.makedirs(output_dir, exist_ok=True)

    # Count existing
    existing_files = list(output_dir.glob("*.webp"))
    existing_count = len(existing_files)
    need = max(0, TARGET_PER_COMBO - existing_count)

    if need <= 0:
        log(f"  {combo_key}: Already have {existing_count} images, skipping")
        return 0

    log(f"  {combo_key}: Have {existing_count}, need {need} more")

    keywords = AREA_KEYWORDS.get(area, {}).get(category, [f"{area} bali {category}"])
    local_hashes = set()

    # Load existing local hashes
    for f in existing_files:
        try:
            with open(f, "rb") as fh:
                h = md5_hash(fh.read())
                local_hashes.add(h)
        except:
            pass

    downloaded = 0
    all_candidates = []

    # Search with multiple keyword variations
    for kw in keywords[:6]:  # Use top 6 keywords
        if downloaded >= need:
            break

        # Try Openverse first (largest free index)
        results = search_openverse(kw, page_size=15)
        all_candidates.extend(results)
        time.sleep(1)  # Rate limit

        # Try Wikimedia
        results = search_wikimedia(kw, limit=10)
        all_candidates.extend(results)
        time.sleep(1)

    # Shuffle to avoid always using same source first
    random.shuffle(all_candidates)

    # Deduplicate candidates by URL
    seen_urls = set()
    unique_candidates = []
    for c in all_candidates:
        if c["url"] not in seen_urls:
            seen_urls.add(c["url"])
            unique_candidates.append(c)

    log(f"  {combo_key}: Found {len(unique_candidates)} unique candidates")

    for candidate in unique_candidates:
        if downloaded >= need:
            break

        url = candidate["url"]
        result = download_and_convert(url)
        if result is None:
            continue

        data, img = result

        # Check minimum size
        if not check_min_size(img):
            # Try to upscale if close
            w, h = img.size
            if w >= 800 and h >= 500:
                ratio = max(1200 / w, 800 / h)
                new_w, new_h = int(w * ratio), int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
            else:
                continue

        # Check MD5
        file_md5 = md5_hash(data)
        if file_md5 in existing_hashes:
            continue
        if file_md5 in local_hashes:
            continue

        # Check pHash
        ph = simple_phash(img)
        if ph and ph in existing_hashes:
            continue

        # Save
        existing_count += 1
        filename = f"{area}_{category}_{existing_count:04d}.webp"
        filepath = output_dir / filename
        save_as_webp(img, filepath)

        # Track hashes
        existing_hashes.add(file_md5)
        if ph:
            existing_hashes.add(ph)
        local_hashes.add(file_md5)

        # Update mapping
        if area not in mapping:
            mapping[area] = {}
        if category not in mapping[area]:
            mapping[area][category] = []
        mapping[area][category].append(filename)

        downloaded += 1

        if downloaded % 5 == 0:
            log(f"  {combo_key}: Downloaded {downloaded}/{need}")

    log(f"  {combo_key}: Done! Downloaded {downloaded} new images")
    return downloaded

def main():
    log("=" * 60)
    log("Bali Real Image Scraper - Starting")
    log(f"Target: {TARGET_PER_COMBO} images per area/category")
    log(f"Total combos: {len(AREAS)} areas × {len(CATEGORIES)} cats = {len(AREAS)*len(CATEGORIES)}")
    log(f"Output: {OUTPUT_DIR}")
    log("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load existing mapping and hashes
    mapping = {}
    if MAPPING_FILE.exists():
        with open(MAPPING_FILE) as f:
            mapping = json.load(f)

    existing_hashes = set()
    if GLOBAL_HASH_FILE.exists():
        with open(GLOBAL_HASH_FILE) as f:
            existing_hashes = set(json.load(f))

    total_downloaded = 0

    # Process each area/category
    for area in AREAS:
        log(f"\n{'='*40}")
        log(f"Processing area: {area}")
        log(f"{'='*40}")

        for category in CATEGORIES:
            count = scrape_area_category(area, category, existing_hashes, mapping)
            total_downloaded += count

            # Save progress after each combo
            with open(MAPPING_FILE, "w", encoding="utf-8") as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            with open(GLOBAL_HASH_FILE, "w") as f:
                json.dump(list(existing_hashes), f)

    log(f"\n{'='*60}")
    log(f"SCRAPER COMPLETE!")
    log(f"Total new images downloaded: {total_downloaded}")
    log(f"Total hashes tracked: {len(existing_hashes)}")
    log(f"{'='*60}")

    # Print summary
    log("\nSummary by area:")
    for area in AREAS:
        area_total = 0
        for cat in CATEGORIES:
            cat_files = list((OUTPUT_DIR / area / cat).glob("*.webp")) if (OUTPUT_DIR / area / cat).exists() else []
            area_total += len(cat_files)
        log(f"  {area}: {area_total} images")

if __name__ == "__main__":
    main()
