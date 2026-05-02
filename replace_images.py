#!/usr/bin/env python3
"""
Replace Picsum images with real Bali images.
1. Copy real images to output/images/ using mapping filenames
2. Update image_mapping_v3.json
3. Verify all HTML references resolve correctly
"""

import os, sys, json, shutil, hashlib
from pathlib import Path
from PIL import Image
from io import BytesIO

BASE_DIR = Path(__file__).parent
REAL_DIR = BASE_DIR / "output" / "images_real"
IMAGES_DIR = BASE_DIR / "output" / "images"
HTML_DIR = BASE_DIR / "output" / "html"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
PROGRESS_FILE = BASE_DIR / "REPLACE_PROGRESS.txt"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]
CATEGORIES = ["food", "culture", "beach", "nature", "shopping", "transport"]

def log(msg):
    line = f"[{__import__('datetime').datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def file_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    with open(PROGRESS_FILE, "w") as f:
        f.write("")

    log("=" * 60)
    log("Replace Picsum → Real Bali Images")
    log("=" * 60)

    # Load mapping
    with open(MAPPING_FILE) as f:
        mapping = json.load(f)

    # Build pool of real images per area/category
    real_pool = {}
    for area in AREAS:
        real_pool[area] = {}
        for cat in CATEGORIES:
            src_dir = REAL_DIR / area / cat
            if src_dir.exists():
                files = sorted(src_dir.glob("*.webp"))
                real_pool[area][cat] = files
            else:
                real_pool[area][cat] = []

    total_replaced = 0
    total_missing = 0
    new_mapping = {}

    for area in AREAS:
        log(f"\n🌍 {area}")
        new_mapping[area] = {}

        for cat in CATEGORIES:
            mapped_files = mapping.get(area, {}).get(cat, [])
            pool = real_pool.get(area, {}).get(cat, [])
            pool_idx = 0

            dst_dir = IMAGES_DIR / area / cat
            dst_dir.mkdir(parents=True, exist_ok=True)

            new_files = []
            replaced = 0
            missing = 0

            for old_filename in mapped_files:
                dst_path = dst_dir / old_filename

                if pool and pool_idx < len(pool):
                    # Use real image from pool (cycle if needed)
                    src_path = pool[pool_idx % len(pool)]
                    pool_idx += 1

                    # Copy and rename to match mapping
                    shutil.copy2(src_path, dst_path)
                    new_files.append(old_filename)
                    replaced += 1
                else:
                    # No real image available - keep existing if it exists
                    if dst_path.exists():
                        new_files.append(old_filename)
                    else:
                        missing += 1

            new_mapping[area][cat] = new_files
            total_replaced += replaced
            total_missing += missing

            if replaced > 0 or missing > 0:
                log(f"  {area}/{cat}: {replaced} replaced, {missing} missing (pool: {len(pool)})")

    # Save updated mapping
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(new_mapping, f, ensure_ascii=False, indent=2)

    log(f"\n{'='*60}")
    log(f"✅ Replace complete!")
    log(f"   Replaced: {total_replaced}")
    log(f"   Missing: {total_missing}")
    log(f"{'='*60}")

    # Verify HTML references
    log("\n🔍 Verifying HTML image references...")
    html_files = sorted(HTML_DIR.rglob("*.html"))
    broken = 0
    total_refs = 0

    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8")
        except:
            continue

        # Find all image references
        import re
        img_refs = re.findall(r'src="[^"]*?/images/([^"]+\.webp)"', content)
        og_refs = re.findall(r'content="[^"]*?/images/([^"]+\.webp)"', content)

        for ref in img_refs + og_refs:
            total_refs += 1
            img_path = IMAGES_DIR / ref
            if not img_path.exists():
                broken += 1
                if broken <= 10:
                    log(f"  ❌ Missing: {ref}")

    log(f"\n📊 HTML verification: {total_refs} refs, {broken} broken")

    # Summary
    log("\n📊 Final image counts:")
    for area in AREAS:
        cnt = 0
        for cat in CATEGORIES:
            d = IMAGES_DIR / area / cat
            if d.exists():
                cnt += len(list(d.glob("*.webp")))
        log(f"  {area}: {cnt}")

if __name__ == "__main__":
    main()
