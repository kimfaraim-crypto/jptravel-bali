#!/usr/bin/env python3
"""
Bali Real Image Scraper v3 - MEGA EXPANDED
Downloads enough REAL Bali images to cover ALL mapped filenames.
Uses Openverse + Wikimedia (no API key needed).
MD5 + pHash dedup. WebP output.

Strategy per area/category:
- Use 15+ keyword variations
- Search multiple pages
- Target: match the count in image_mapping_v3.json
"""

import os, sys, json, hashlib, time, random
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "images_real"
PROGRESS_FILE = BASE_DIR / "SCRAPER_PROGRESS_V3.txt"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
GLOBAL_HASH_FILE = BASE_DIR / "global_hashes_real.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]

# Expanded keywords - 15+ per combo for maximum coverage
AREA_KEYWORDS = {
    "우ữu": {
        "food": [
            "ubud bali food", "ubud restaurant", "ubud warung", "ubud smoothie bowl",
            "babi guling ubud", "ubud cafe bali", "ubud healthy food", "ubud vegan restaurant",
            "ubud cooking class", "ubud rice terrace cafe", "ubud organic food", "ubud brunch",
            "ubud fine dining", "ubud local food", "ubud nasi goreng", "ubud sate",
            "ubud indonesian food", "bali ubud meal", "ubud traditional food", "ubud coffee shop",
        ],
        "culture": [
            "ubud temple", "monkey forest ubud", "ubud palace bali", "ubud art market",
            "ubud dance kecak", "ubud painting", "ubud traditional", "campuhan ridge ubud",
            "ubud bali ceremony", "ubud hindu temple", "ubud wood carving", "ubud barong dance",
            "ubud galeri seni", "ubud saraswati temple", "ubud tirta empul", "ubud goa gajah",
            "ubud bali ritual", "ubud offering canang", "ubud gamelan music", "ubud batik",
        ],
        "beach": [
            "ubud river valley", "ubud waterfall", "ubud nature", "campuhan ridge walk",
            "ubud rice field", "tegalalang rice terrace", "ubud jungle", "ubud valley view",
            "bali rice terrace", "ubud green landscape", "ubud tukad cepung waterfall",
            "ubud tibumana waterfall", "ubud kanto lampo waterfall", "ubud sungai",
            "ubud ayung river", "ubud jungle trek", "ubud ridge", "ubud valley",
        ],
        "nature": [
            "tegalalang rice terrace", "monkey forest ubud", "campuhan ridge ubud",
            "ubud waterfall", "ubud rice paddy", "ubud jungle bali", "ubud botanical",
            "bali rice field ubud", "ubud tropical garden", "ubud nature walk",
            "ubud butterfly park", "ubud bali flora", "ubud tropical forest",
            "ubud green valley", "ubud palm tree", "ubud terraced landscape",
        ],
        "shopping": [
            "ubud art market", "ubud craft market", "ubud shopping", "ubud silver jewelry",
            "ubud batik shop", "ubud souvenir", "ubud traditional market", "ubud artisan",
            "ubud wood carving shop", "ubud gallery", "ubud textile", "ubud handmade craft",
            "ubud painting shop", "ubud local market", "ubud boutique", "ubud spa products",
        ],
        "transport": [
            "ubud bali road", "ubud scooter", "bali motorbike ubud", "ubud street",
            "ubud bridge", "ubud walking", "bali transport ubud", "ubud village road",
            "ubud path", "ubud pathway", "ubud bike cycling", "ubud bali traffic",
            "ubud shuttle bus", "ubud taxi", "ubud bali alley", "ubud rice field path",
        ],
    },
    "스미냑": {
        "food": [
            "seminyak restaurant", "seminyak bali food", "potato head bali food",
            "seminyak beach club dining", "seminyak cafe", "seminyak brunch",
            "seminyak seafood", "ku de ta bali", "seminyak fine dining", "seminyak smoothie bowl",
            "seminyak warung", "seminyak vegan", "seminyak coffee", "seminyak sunset dinner",
            "seminyak cocktail bar", "seminyak italian food", "seminyak japanese food",
            "seminyak healthy food", "seminyak bakery", "seminyak brunch spot",
        ],
        "culture": [
            "seminyak temple bali", "seminyak ceremony", "seminyak bali culture",
            "petitenget temple", "seminyak art gallery", "seminyak bali tradition",
            "seminyak offering", "seminyak bali dance", "seminyak hindu", "petitenget ceremony",
            "seminyak canang sari", "seminyak bali shrine", "seminyak traditional",
            "seminyak pura", "seminyak bali ritual", "seminyak incense offering",
        ],
        "beach": [
            "seminyak beach", "double six beach bali", "seminyak beach sunset",
            "seminyak surfing", "seminyak beach club", "petitenget beach", "seminyak ocean",
            "seminyak coast", "seminyak waves", "seminyak sand", "seminyak beach bar",
            "seminyak beach walk", "seminyak surfboard", "seminyak tide", "seminyak shore",
            "seminyak beach volleyball", "seminyak ocean view", "seminyak seaside",
        ],
        "nature": [
            "seminyak garden", "seminyak tropical", "seminyak palm tree", "seminyak nature",
            "seminyak rice field", "petitenget park", "seminyak green", "bali nature seminyak",
            "seminyak flower", "seminyak landscape", "seminyak tropical plants", "seminyak villa garden",
            "seminyak pool garden", "seminyak bali greenery", "seminyak frangipani",
        ],
        "shopping": [
            "seminyak shopping", "seminyak boutique", "seminyak fashion bali", "seminyak craft",
            "seminyak souvenir", "seminyak designer", "seminyak market", "seminyak art shop",
            "seminyak villa decor", "seminyak jewelry", "seminyak homeware", "seminyak spa",
            "seminyak textiles", "seminyak gallery shop", "seminyak concept store",
        ],
        "transport": [
            "seminyak street", "seminyak road bali", "seminyak motorbike", "seminyak traffic",
            "seminyak walking", "bali transport seminyak", "seminyak taxi", "seminyak scooter",
            "seminyak lane", "seminyak pathway", "seminyak bali alley", "seminyak main road",
        ],
    },
    "꾸따": {
        "food": [
            "kuta bali food", "kuta restaurant", "kuta beach dining", "kuta seafood",
            "kuta cafe", "kuta street food", "kuta warung", "kuta nasi goreng", "kuta smoothie",
            "waterbom bali food", "kuta bali brunch", "kuta beach club food", "kuta local food",
            "kuta fast food bali", "kuta bbq", "kuta indonesian food", "kuta dessert",
            "kuta coffee shop", "kuta legian food", "kuta night food",
        ],
        "culture": [
            "kuta temple bali", "kuta bali ceremony", "kuta art", "kuta traditional",
            "kuta bali culture", "kuta monument", "kuta heritage", "legian temple",
            "kuta bali offering", "kuta hindu shrine", "kuta bali dance", "kuta pura",
            "kuta traditional market", "kuta bali ritual", "kuta memorial",
        ],
        "beach": [
            "kuta beach", "kuta beach sunset", "kuta surfing", "kuta waves",
            "kuta beach bali", "legian beach", "kuta ocean", "kuta coast",
            "kuta beach walk", "kuta sand surf", "kuta beach vendor", "kuta beach bar",
            "kuta surf lesson", "kuta beach sunrise", "kuta tide", "kuta shore",
        ],
        "nature": [
            "kuta park bali", "kuta garden", "kuta tropical", "kuta nature",
            "bali nature kuta", "kuta palm", "kuta green", "kuta landscape",
            "kuta flower", "kuta sunrise nature", "kuta bali trees", "kuta tropical garden",
        ],
        "shopping": [
            "kuta shopping", "discovery mall bali", "kuta market", "kuta art market",
            "kuta souvenir shop", "kuta beachwalk mall", "kuta craft", "kuta bargain",
            "kuta fashion", "kuta bali shopping street", "kuta spa shop", "kuta krisna",
            "kuta surf shop", "kuta duty free", "kuta local craft",
        ],
        "transport": [
            "kuta street", "kuta road bali", "kuta traffic", "kuta motorbike",
            "kuta taxi", "bali transport kuta", "kuta airport", "kuta scooter",
            "kuta walking street", "kuta lane", "kuta bali trans", "kuta bali bus",
        ],
    },
    "사누르": {
        "food": [
            "sanur restaurant bali", "sanur food", "sanur beach cafe", "sanur seafood",
            "sanur brunch", "sanur warung", "sanur breakfast", "sanur dining",
            "sanur coffee", "sanur night market food", "sanur bali food", "sanur smoothie",
            "sanur beach bar food", "sanur healthy food", "sanur local cuisine",
        ],
        "culture": [
            "sanur temple bali", "sanur ceremony", "sanur bali culture", "le mayeur museum",
            "sanur art", "sanur traditional", "sanur bali dance", "sanur offering",
            "sanur hindu", "sanur heritage", "sanur blanjong temple", "sanur pura",
            "sanur bali ritual", "sanur traditional craft", "sanur painting",
        ],
        "beach": [
            "sanur beach", "sanur beach sunrise", "sanur boardwalk", "sanur coast",
            "sanur ocean", "sanur reef", "sanur sand", "sanur sea", "sanur harbor",
            "sanur beach bali", "sanur mangrove beach", "sanur calm sea", "sanur paddle board",
            "sanur kite surfing", "sanur beach path",
        ],
        "nature": [
            "sanur garden", "sanur nature", "sanur mangrove", "sanur tropical",
            "sanur green", "bali nature sanur", "sanur park", "sanur palm",
            "sanur flower", "sanur mangrove forest", "sanur bali trees", "sanur botanical",
        ],
        "shopping": [
            "sanur market", "sanur shopping", "sanur art market", "sanur craft",
            "sanur souvenir", "sanur night market", "sanur boutique", "sanur gallery",
            "sanur traditional market", "sanur shop", "sanur local craft", "sanur batik",
        ],
        "transport": [
            "sanur road", "sanur cycling bali", "sanur bike", "sanur boardwalk",
            "sanur street", "sanur ferry", "sanur harbor boat", "bali transport sanur",
            "sanur scooter", "sanur walking path", "sanur bali road", "sanur bali alley",
        ],
    },
    "누사두아": {
        "food": [
            "nusa dua restaurant", "nusa dua food", "nusa dua resort dining", "nusa dua seafood",
            "nusa dua beach club", "nusa dua cafe", "nusa dua fine dining", "nusa dua breakfast",
            "nusa dua bali food", "nusa dua luxury dining", "nusa dua buffet", "nusa dua international food",
            "nusa dua beach bar", "nusa dua indonesian food", "nusa dua cocktail",
        ],
        "culture": [
            "nusa dua temple", "nusa dua bali culture", "nusa dua ceremony", "nusa dua art",
            "nusa dua traditional", "nusa dua heritage", "nusa dua balinese", "nusa dua hindu",
            "nusa dua offering", "nusa dua dance", "nusa dua pura", "nusa dua bali ritual",
            "nusa dua kecak", "nusa dua traditional craft",
        ],
        "beach": [
            "nusa dua beach", "nusa dua water blow", "nusa dua snorkeling", "nusa dua ocean",
            "nusa dua coast", "nusa dua reef", "nusa dua sand", "nusa dua sea",
            "nusa dua peninsula", "nusa dua beach bali", "nusa dua clear water", "nusa dua coral",
            "nusa dua diving", "nusa dua paddle board", "nusa dua beach walk",
        ],
        "nature": [
            "nusa dua garden", "nusa dua tropical", "nusa dua nature", "nusa dua green",
            "nusa dua landscape", "bali nature nusa dua", "nusa dua park", "nusa dua palm",
            "nusa dua flower", "nusa dua botanical", "nusa dua tropical garden", "nusa dua resort garden",
        ],
        "shopping": [
            "bali collection mall", "nusa dua shopping", "nusa dua market", "nusa dua craft",
            "nusa dua souvenir", "nusa dua boutique", "nusa dua gallery", "nusa dua shop",
            "nusa dua art", "nusa dua luxury shop", "nusa dua local craft", "nusa dua spa shop",
        ],
        "transport": [
            "nusa dua road", "nusa dua street", "nusa dua transport", "nusa dua taxi",
            "nusa dua motorbike", "nusa dua walking", "nusa dua resort shuttle",
            "bali transport nusa dua", "nusa dua scooter", "nusa dua pathway",
        ],
    },
    "울루와뚜": {
        "food": [
            "uluwatu restaurant", "uluwatu food", "uluwatu cliff dining", "uluwatu beach club food",
            "uluwatu cafe", "uluwatu seafood", "uluwatu sunset dining", "single fin uluwatu food",
            "uluwatu warung", "uluwatu bali food", "uluwatu smoothie", "uluwatu brunch",
            "uluwatu cliff bar", "uluwatu local food", "uluwatu coffee",
        ],
        "culture": [
            "uluwatu temple", "uluwatu kecak dance", "uluwatu ceremony", "uluwatu bali culture",
            "uluwatu hindu temple", "uluwatu traditional", "uluwatu offering", "uluwatu ritual",
            "uluwatu cliff temple", "uluwatu bali tradition", "uluwatu pura", "uluwatu dance",
            "uluwatu stone carving", "uluwatu bali shrine",
        ],
        "beach": [
            "uluwatu beach", "uluwatu surf", "uluwatu cliff", "uluwatu ocean",
            "uluwatu wave", "blue point beach uluwatu", "uluwatu coast", "uluwatu cave beach",
            "uluwatu sand", "uluwatu sea cliff", "uluwatu surf break", "uluwatu secret beach",
            "uluwatu padang padang", "uluwatu bingin beach", "uluwatu dreamland beach",
        ],
        "nature": [
            "uluwatu cliff nature", "uluwatu tropical", "uluwatu garden", "uluwatu green",
            "uluwatu landscape", "bali nature uluwatu", "uluwatu palm", "uluwatu sunset nature",
            "uluwatu ocean view", "uluwatu rocky coast", "uluwatu cliff garden", "uluwatu bali nature",
        ],
        "shopping": [
            "uluwatu market", "uluwatu shopping", "uluwatu craft", "uluwatu souvenir",
            "uluwatu art", "uluwatu boutique", "uluwatu gallery", "uluwatu shop",
            "uluwatu bali market", "uluwatu traditional craft", "uluwatu surf shop",
        ],
        "transport": [
            "uluwatu road", "uluwatu street", "uluwatu motorbike", "uluwatu cliff road",
            "uluwatu transport", "uluwatu scooter", "uluwatu pathway", "bali transport uluwatu",
            "uluwatu coastal road", "uluwatu walking", "uluwatu bali alley",
        ],
    },
    "짠디다사": {
        "food": [
            "candidasa restaurant", "candidasa food", "candidasa bali dining", "candidasa seafood",
            "candidasa cafe", "candidasa warung", "east bali food", "candidasa beach dining",
            "candidasa coffee", "candidasa bali food", "candidasa local food", "candidasa indonesian",
        ],
        "culture": [
            "candidasa temple", "tirta gangga", "besakih temple", "candidasa bali culture",
            "candidasa ceremony", "east bali temple", "candidasa traditional", "candidasa hindu",
            "candidasa offering", "candidasa art", "candidasa pura", "candidasa bali ritual",
        ],
        "beach": [
            "candidasa beach", "candidasa coast", "candidasa ocean", "candidasa reef",
            "candidasa sea", "amed beach", "padang bai beach", "candidasa sand",
            "east bali beach", "candidasa waterfront", "candidasa snorkeling", "candidasa diving",
        ],
        "nature": [
            "candidasa nature", "candidasa tropical", "candidasa garden", "tirta gangga garden",
            "candidasa rice field", "east bali nature", "candidasa green", "candidasa landscape",
            "candidasa mountain", "candidasa waterfall", "candidasa lotus pond", "candidasa palm",
        ],
        "shopping": [
            "candidasa market", "candidasa shopping", "candidasa craft", "candidasa souvenir",
            "candidasa art", "east bali market", "candidasa gallery", "candidasa shop",
            "candidasa traditional market", "candidasa bali shopping", "candidasa local craft",
        ],
        "transport": [
            "candidasa road", "candidasa street", "candidasa motorbike", "candidasa transport",
            "east bali road", "candidasa scooter", "padang bai harbor", "candidasa boat",
            "candidasa pathway", "bali transport candidasa", "candidasa bali alley",
        ],
    },
    "로비나": {
        "food": [
            "lovina restaurant", "lovina food", "lovina bali dining", "lovina seafood",
            "lovina cafe", "lovina warung", "north bali food", "lovina beach dining",
            "lovina coffee", "singaraja food", "lovina local food", "lovina indonesian food",
        ],
        "culture": [
            "lovina temple", "lovina ceremony", "lovina bali culture", "singaraja temple",
            "lovina traditional", "north bali temple", "lovina hindu", "lovina offering",
            "lovina art", "lovina heritage", "lovina pura", "lovina bali ritual",
        ],
        "beach": [
            "lovina beach", "lovina dolphin", "lovina sunrise", "lovina coast",
            "lovina black sand", "lovina ocean", "lovina sea", "north bali beach",
            "lovina boat", "lovina calm sea", "lovina snorkeling", "lovina coral",
        ],
        "nature": [
            "lovina nature", "gitgit waterfall", "banjar hot spring", "lovina tropical",
            "lovina garden", "north bali nature", "lovina green", "lovina landscape",
            "lovina mountain", "lovina botanical", "lovina rice field", "lovina jungle",
        ],
        "shopping": [
            "lovina market", "lovina shopping", "lovina craft", "lovina souvenir",
            "singaraja market", "north bali market", "lovina art", "lovina gallery",
            "lovina shop", "lovina traditional market", "lovina local craft",
        ],
        "transport": [
            "lovina road", "lovina street", "lovina motorbike", "lovina boat",
            "lovina transport", "north bali road", "lovina scooter", "singaraja road",
            "lovina pathway", "bali transport lovina", "lovina bali alley",
        ],
    },
    "킨타마니": {
        "food": [
            "kintamani restaurant", "kintamani food", "kintamani bali dining", "kintamani coffee",
            "kintamani view restaurant", "mount batur food", "kintamani warung", "kintamani cafe",
            "batur lake food", "kintamani breakfast", "kintamani local food", "kintamani indonesian",
        ],
        "culture": [
            "kintamani temple", "kintamani ceremony", "kintamani bali culture", "mount batur temple",
            "trunyan village", "kintamani traditional", "kintamani hindu", "kintamani offering",
            "kintamani art", "batur temple", "kintamani pura", "kintamani bali ritual",
        ],
        "beach": [
            "batur lake", "kintamani lake", "kintamani crater", "batur crater lake",
            "kintamani water", "kintamani volcanic", "batur caldera", "kintamani island",
            "trunyan lake", "kintamani shore", "kintamani hot spring", "batur lake view",
        ],
        "nature": [
            "mount batur", "kintamani volcano", "batur sunrise", "kintamani trekking",
            "kintamani crater", "batur landscape", "kintamani mountain", "kintamani caldera",
            "batur lava field", "kintamani nature", "kintamani volcanic rock", "batur geological",
            "kintamani misty mountain", "batur sunrise trek", "kintamani highland",
        ],
        "shopping": [
            "kintamani market", "kintamani shopping", "kintamani craft", "kintamani souvenir",
            "kintamani art", "batur market", "kintamani coffee shop", "kintamani gallery",
            "kintamani traditional market", "kintamani bali shopping", "kintamani local craft",
        ],
        "transport": [
            "kintamani road", "kintamani mountain road", "kintamani motorbike", "kintamani transport",
            "batur road", "kintamani scooter", "kintamani trekking path", "kintamani pathway",
            "bali transport kintamani", "kintamani winding road", "kintamani bali alley",
        ],
    },
    "타나롯": {
        "food": [
            "tanah lot restaurant", "tanah lot food", "tanah lot dining", "tanah lot cafe",
            "tanah lot bali food", "tanah lot sunset dining", "tanah lot warung", "tabanan food",
            "tanah lot seafood", "tanah lot bali restaurant", "tanah lot local food", "tanah lot coffee",
        ],
        "culture": [
            "tanah lot temple", "tanah lot ceremony", "tanah lot sunset temple", "tanah lot bali culture",
            "tanah lot ritual", "tanah lot hindu", "tanah lot offering", "batu bolong temple",
            "tanah lot traditional", "tanah lot kecak", "tanah lot pura", "tanah lot bali dance",
            "tanah lot ceremony sunset", "tanah lot shrine",
        ],
        "beach": [
            "tanah lot beach", "tanah lot cliff", "tanah lot ocean", "tanah lot coast",
            "tanah lot sea temple", "tanah lot rock", "tanah lot wave", "tanah lot sand",
            "tanah lot tide", "tabanan beach", "tanah lot rocky shore", "tanah lot ocean waves",
        ],
        "nature": [
            "tanah lot rice field", "tanah lot sunset", "tanah lot tropical", "tanah lot nature",
            "tanah lot landscape", "tanah lot green", "tabanan rice terrace", "tanah lot garden",
            "tanah lot palm", "tanah lot cliff nature", "tanah lot bali sunset", "tanah lot scenic",
        ],
        "shopping": [
            "tanah lot market", "tanah lot shopping", "tanah lot craft", "tanah lot souvenir",
            "tanah lot art", "tabanan market", "tanah lot gallery", "tanah lot shop",
            "tanah lot traditional market", "tanah lot bali shopping", "tanah lot local craft",
        ],
        "transport": [
            "tanah lot road", "tanah lot path", "tanah lot motorbike", "tanah lot transport",
            "tanah lot walking", "tabanan road", "tanah lot scooter", "tanah lot pathway",
            "bali transport tanah lot", "tanah lot coastal road", "tanah lot bali alley",
        ],
    },
    "베두굴": {
        "food": [
            "bedugul restaurant", "bedugul food", "bedugul bali dining", "bedugul strawberry",
            "bedugul cafe", "bedugul warung", "bedugul coffee", "bedugul market food",
            "bedugul highland food", "candi kuning food", "bedugul local food", "bedugul indonesian",
        ],
        "culture": [
            "ulun danu bratan", "bedugul temple", "bedugul ceremony", "bedugul bali culture",
            "bratan lake temple", "bedugul hindu", "bedugul offering", "bedugul traditional",
            "bedugul art", "candi kuning temple", "bedugul pura", "bedugul bali ritual",
        ],
        "beach": [
            "bratan lake", "bedugul lake", "bedugul water", "bratan lake bali",
            "bedugul lake temple", "bedugul reservoir", "bedugul calm water", "bedugul pond",
            "bedugul reflection", "bedugul lake view", "bedugul misty lake", "bratan lake reflection",
        ],
        "nature": [
            "bedugul botanical garden", "bedugul highland", "bedugul nature", "bedugul mountain",
            "bedugul tropical garden", "bedugul forest", "bedugul green", "bedugul landscape",
            "bedugul misty", "bedugul cool climate", "bedugul mossy forest", "bedugul fern",
            "bedugul orchid garden", "bedugul rainforest", "bedugul highland plants",
        ],
        "shopping": [
            "candi kuning market", "bedugul market", "bedugul shopping", "bedugul fruit market",
            "bedugul strawberry market", "bedugul craft", "bedugul souvenir", "bedugul flower market",
            "bedugul vegetable market", "bedugul art", "bedugul local craft", "bedugul spice market",
        ],
        "transport": [
            "bedugul road", "bedugul mountain road", "bedugul motorbike", "bedugul transport",
            "bedugul scooter", "bedugul winding road", "bedugul pathway", "bali transport bedugul",
            "bedugul highland road", "bedugul street", "bedugul bali alley",
        ],
    },
}
if "우ữu" in AREA_KEYWORDS:
    AREA_KEYWORDS["우붓"] = AREA_KEYWORDS.pop("우ữu")

session = requests.Session()
session.headers.update({"User-Agent": "BaliTravelBlog/1.0 (Educational; admin@example.com)"})

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
            if img.mode == "P": img = img.convert("RGBA")
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
                w, h = img.get("width", 0) or 0, img.get("height", 0) or 0
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
            for pid, page in data.get("query", {}).get("pages", {}).items():
                for ii in page.get("imageinfo", []):
                    url = ii.get("thumburl") or ii.get("url", "")
                    w = ii.get("thumbwidth") or ii.get("width", 0)
                    h = ii.get("thumbheight") or ii.get("height", 0)
                    if url and "image" in ii.get("mime", "") and w >= 600 and h >= 400:
                        results.append({"url": url, "width": w, "height": h})
            return results
    except:
        pass
    return []

def get_target_count(area, category):
    """Get target count from image_mapping_v3.json."""
    try:
        with open(MAPPING_FILE) as f:
            mapping = json.load(f)
        return len(mapping.get(area, {}).get(category, []))
    except:
        return 60  # fallback

def scrape_combo(area, category, global_hashes):
    output_dir = OUTPUT_DIR / area / category
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = len(list(output_dir.glob("*.webp")))
    target = get_target_count(area, category)
    need = max(0, target - existing)

    if need <= 0:
        return 0

    combo = f"{area}/{category}"
    log(f"  {combo}: {existing}/{target} → need {need}")

    keywords = AREA_KEYWORDS.get(area, {}).get(category, [f"{area} bali {category}"])
    candidates = []

    # Search ALL keywords, multiple pages
    for i, kw in enumerate(keywords):
        # Openverse page 1
        results = search_openverse(kw, page_size=20, page=1)
        candidates.extend(results)
        time.sleep(1.2)

        # Openverse page 2 for more variety
        if i < 8:
            results = search_openverse(kw, page_size=20, page=2)
            candidates.extend(results)
            time.sleep(1.2)

        # Wikimedia
        results = search_wikimedia(kw, limit=15)
        candidates.extend(results)
        time.sleep(1.2)

    # Deduplicate URLs
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

    # Find next filename number
    existing_nums = []
    for f in output_dir.glob("*.webp"):
        try:
            existing_nums.append(int(f.stem.split("_")[-1]))
        except:
            pass
    next_num = max(existing_nums) + 1 if existing_nums else 1

    downloaded = 0
    for candidate in unique:
        if downloaded >= need:
            break

        img = download_image(candidate["url"])
        if img is None:
            continue

        w, h = img.size
        if w < 1200 or h < 800:
            if w >= 600 and h >= 400:
                ratio = max(1200 / w, 800 / h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            else:
                continue

        buf = BytesIO()
        img.save(buf, "WEBP", quality=85)
        webp_data = buf.getvalue()
        file_md5 = md5_hash(webp_data)

        if file_md5 in global_hashes or file_md5 in local_hashes:
            continue

        ph = simple_phash(img)
        if ph and ph in global_hashes:
            continue

        filename = f"{area}_{category}_{next_num:04d}.webp"
        filepath = output_dir / filename
        with open(filepath, "wb") as f:
            f.write(webp_data)

        global_hashes.add(file_md5)
        if ph: global_hashes.add(ph)
        local_hashes.add(file_md5)

        next_num += 1
        downloaded += 1

        if downloaded % 20 == 0:
            log(f"  {combo}: {downloaded}/{need}")

    log(f"  {combo}: +{downloaded} → {existing + downloaded}/{target}")
    return downloaded

def main():
    with open(PROGRESS_FILE, "w") as f:
        f.write("")

    # Load target counts
    with open(MAPPING_FILE) as f:
        mapping = json.load(f)

    total_target = sum(len(files) for area in mapping.values() for files in area.values())
    log("=" * 60)
    log(f"Bali Real Image Scraper v3 - MEGA EXPANDED")
    log(f"Target: {total_target} images (from mapping)")
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
            with open(GLOBAL_HASH_FILE, "w") as f:
                json.dump(list(global_hashes), f)

    log(f"\n{'='*60}")
    log(f"✅ DONE! New images: {total}")
    log(f"{'='*60}")

    log("\n📊 Final count:")
    for area in AREAS:
        cnt = 0
        for cat in CATEGORIES:
            d = OUTPUT_DIR / area / cat
            if d.exists():
                cnt += len(list(d.glob("*.webp")))
        target = sum(len(mapping.get(area, {}).get(cat, [])) for cat in CATEGORIES)
        log(f"  {area}: {cnt}/{target}")

if __name__ == "__main__":
    main()
