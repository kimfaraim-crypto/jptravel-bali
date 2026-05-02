#!/usr/bin/env python3
"""10-step quality audit for JP Travel Bali project."""
import os, re, json, hashlib, csv
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("output/html/bali")
IMAGES_DIR = Path("output/images")
IMAGES_REAL_DIR = Path("output/images_real")

html_files = sorted(BASE.rglob("*.html"))
print(f"Total HTML files: {len(html_files)}")

# ============================================================
# STEP 1: Distribution analysis
# ============================================================
print("\n" + "="*60)
print("STEP 1: Distribution Analysis")
print("="*60)

city_cat = defaultdict(lambda: defaultdict(list))
for f in html_files:
    parts = f.relative_to(BASE).parts  # e.g. ('스미냑', 'food', '001.html')
    city, cat = parts[0], parts[1]
    city_cat[city][cat].append(f.name)

for city in sorted(city_cat):
    cats = city_cat[city]
    total = sum(len(v) for v in cats.values())
    cat_str = ", ".join(f"{c}:{len(v)}" for c, v in sorted(cats.items()))
    print(f"  {city}: {total} files ({cat_str})")

# ============================================================
# STEP 2: Title / meta description duplication
# ============================================================
print("\n" + "="*60)
print("STEP 2: Title & Meta Description Duplication")
print("="*60)

titles = []
metas = []
title_to_files = defaultdict(list)
meta_to_files = defaultdict(list)

for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    # title
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    if m:
        t = m.group(1).strip()
        titles.append(t)
        title_to_files[t].append(str(f))
    # meta description
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.DOTALL)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', content, re.DOTALL)
    if m:
        d = m.group(1).strip()
        metas.append(d)
        meta_to_files[d].append(str(f))

dup_titles = {k: v for k, v in title_to_files.items() if len(v) > 1}
dup_metas = {k: v for k, v in meta_to_files.items() if len(v) > 1}
print(f"  Unique titles: {len(set(titles))} / {len(titles)}")
print(f"  Duplicate title groups: {len(dup_titles)}")
if dup_titles:
    for t, fs in list(dup_titles.items())[:5]:
        print(f"    [{len(fs)}x] {t[:80]}")
print(f"  Unique meta descriptions: {len(set(metas))} / {len(metas)}")
print(f"  Duplicate meta groups: {len(dup_metas)}")
if dup_metas:
    for d, fs in list(dup_metas.items())[:5]:
        print(f"    [{len(fs)}x] {d[:80]}")

# ============================================================
# STEP 3: Content length, Korean char count, Chinese/emoji
# ============================================================
print("\n" + "="*60)
print("STEP 3: Content Length & Language Analysis")
print("="*60)

content_stats = []
short_articles = []
chinese_articles = []
emoji_articles = []
hanja_articles = []

hanja_re = re.compile(r'[\u4e00-\u9fff]')
emoji_re = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0000200D\U00002640\U00002642]')

for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    # Extract main text (strip HTML tags)
    body = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', '', body)
    
    korean_chars = len(re.findall(r'[가-힣]', body))
    total_chars = len(body)
    
    has_chinese = bool(hanja_re.search(body))
    has_emoji = bool(emoji_re.search(body))
    has_hanja = has_chinese  # CJK unified includes hanja
    
    content_stats.append({
        'file': str(f),
        'total_chars': total_chars,
        'korean_chars': korean_chars,
        'has_chinese': has_chinese,
        'has_emoji': has_emoji,
    })
    
    if korean_chars < 1500:
        short_articles.append((str(f), korean_chars))
    if has_chinese:
        chinese_articles.append(str(f))
    if has_emoji:
        emoji_articles.append(str(f))

korean_counts = [s['korean_chars'] for s in content_stats]
print(f"  Korean char count: min={min(korean_counts)}, max={max(korean_counts)}, avg={sum(korean_counts)/len(korean_counts):.0f}")
print(f"  Articles < 1500 Korean chars: {len(short_articles)}")
if short_articles:
    for path, cnt in short_articles[:5]:
        print(f"    {path}: {cnt} chars")
print(f"  Articles with Chinese/Hanja characters: {len(chinese_articles)}")
print(f"  Articles with Emoji: {len(emoji_articles)}")

# ============================================================
# STEP 4: Korean particle errors
# ============================================================
print("\n" + "="*60)
print("STEP 4: Korean Particle Error Analysis")
print("="*60)

particle_patterns = {
    '을(를)': re.compile(r'을\(를\)|을\/를|\(을\)를|\(를\)을'),
    '은(는)': re.compile(r'은\(는\)|은\/는|\(은\)는|\(는\)은'),
    '이(가)': re.compile(r'이\(가\)|이\/가|\(이\)가|\(가\)이'),
    '와(과)': re.compile(r'와\(과\)|와\/과|\(와\)과|\(과\)와'),
    '로(으로)': re.compile(r'로\(으로\)|로\/으로|\(로\)으로|\(으로\)로'),
    '에서/에': re.compile(r'에서\/에|에\/에서'),
    '{을(를)}': re.compile(r'\{을\(를\)\}|\{을\/를\}'),
    '{은(는)}': re.compile(r'\{은\(는\)\}|\{은\/는\}'),
    '{이(가)}': re.compile(r'\{이\(가\)\}|\{이\/가\}'),
    '{와(과)}': re.compile(r'\{와\(과\)\}|\{와\/과\}'),
}

particle_errors = defaultdict(list)
for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    for name, pat in particle_patterns.items():
        matches = pat.findall(content)
        if matches:
            particle_errors[name].append((str(f), len(matches)))

total_particle_errors = sum(len(v) for v in particle_errors.values())
print(f"  Total particle error instances: {total_particle_errors}")
for name, files in sorted(particle_errors.items()):
    total = sum(cnt for _, cnt in files)
    print(f"    {name}: {total} occurrences in {len(files)} files")

# ============================================================
# STEP 5: Repetitive phrase analysis
# ============================================================
print("\n" + "="*60)
print("STEP 5: Repetitive Phrase Analysis")
print("="*60)

repetitive_phrases = [
    "10년차 블로거", "숨은 명소", "2026년 기준", "실전 팁",
    "가격 비교", "추천이에요", "끝까지 읽어보세요", "여행 꿀팁",
    "현지인 맛집", "인생샷", "포토스팟", "필수 코스",
    "꼭 가봐야 할", "베스트", "진짜", "완벽한", "알찬",
    "여행자라면", "이 글 하나로", "모든 정보", "총정리",
    "완전 정복", "여행 준비", "놓치지 마세요"
]

phrase_counts = {}
for phrase in repetitive_phrases:
    count = 0
    file_count = 0
    for f in html_files:
        content = f.read_text(encoding='utf-8', errors='replace')
        c = content.count(phrase)
        if c > 0:
            count += c
            file_count += 1
    phrase_counts[phrase] = (count, file_count)

print(f"  {'Phrase':<20} {'Total':>6} {'Files':>6}")
print(f"  {'-'*20} {'-'*6} {'-'*6}")
for phrase, (total, fc) in sorted(phrase_counts.items(), key=lambda x: -x[1][0]):
    print(f"  {phrase:<20} {total:>6} {fc:>6}")

# ============================================================
# STEP 6: H2/H3 structure repetition
# ============================================================
print("\n" + "="*60)
print("STEP 6: H2/H3 Structure Repetition")
print("="*60)

structure_sigs = defaultdict(list)
for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
    h2s_clean = [re.sub(r'<[^>]+>', '', h).strip() for h in h2s]
    sig = '|'.join(h2s_clean)
    structure_sigs[sig].append(str(f))

print(f"  Unique H2 structures: {len(structure_sigs)}")
dup_structures = {k: v for k, v in structure_sigs.items() if len(v) > 1}
print(f"  Duplicate structure groups: {len(dup_structures)}")
if dup_structures:
    for sig, fs in sorted(dup_structures.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"    [{len(fs)}x] {sig[:100]}...")

# ============================================================
# STEP 7: FAQ duplication
# ============================================================
print("\n" + "="*60)
print("STEP 7: FAQ/Q&A Duplication")
print("="*60)

faq_sigs = defaultdict(list)
faq_count = 0
for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    # Find FAQ sections
    faq_section = re.search(r'<(?:div|section)[^>]*(?:faq|question|qa)[^>]*>(.*?)</(?:div|section)>', content, re.DOTALL | re.IGNORECASE)
    questions = re.findall(r'<(?:h3|h4|summary|dt)[^>]*>(.*?)</(?:h3|h4|summary|dt)>', content, re.DOTALL)
    q_clean = [re.sub(r'<[^>]+>', '', q).strip() for q in questions]
    if q_clean:
        faq_count += 1
        sig = '|'.join(q_clean[:5])
        faq_sigs[sig].append(str(f))

print(f"  Files with FAQ/Q&A: {faq_count}")
dup_faqs = {k: v for k, v in faq_sigs.items() if len(v) > 1}
print(f"  Duplicate FAQ groups: {len(dup_faqs)}")
if dup_faqs:
    for sig, fs in sorted(dup_faqs.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"    [{len(fs)}x] {sig[:100]}...")

# ============================================================
# STEP 8: Image analysis
# ============================================================
print("\n" + "="*60)
print("STEP 8: Image Analysis")
print("="*60)

# Collect all image files on disk
all_webp_on_disk = set()
for d in [IMAGES_DIR, IMAGES_REAL_DIR]:
    if d.exists():
        for img in d.rglob("*.webp"):
            all_webp_on_disk.add(img)

print(f"  WebP files on disk: {len(all_webp_on_disk)}")

# Analyze HTML image references
img_refs = []
missing_images = []
non_webp = []
dup_in_page = []
image_hashes = {}

for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    page_imgs = []
    for img_path in imgs:
        img_refs.append((str(f), img_path))
        page_imgs.append(img_path)
        if not img_path.endswith('.webp'):
            non_webp.append((str(f), img_path))
        # Check if file exists
        # img_path is relative like ../../images/스미냑/food/001_01.webp
        # Need to resolve relative to the HTML file
        resolved = (f.parent / img_path).resolve()
        if not resolved.exists():
            missing_images.append((str(f), img_path))
        else:
            # Hash the file
            h = hashlib.md5(resolved.read_bytes()).hexdigest()
            image_hashes[str(resolved)] = h
    
    # Check for duplicates within the same page
    img_counter = Counter(page_imgs)
    for img, cnt in img_counter.items():
        if cnt > 1:
            dup_in_page.append((str(f), img, cnt))

print(f"  Total image references in HTML: {len(img_refs)}")
print(f"  Missing image files: {len(missing_images)}")
if missing_images:
    for path, img in missing_images[:5]:
        print(f"    {path}: {img}")
print(f"  Non-WebP images: {len(non_webp)}")
print(f"  In-page duplicates: {len(dup_in_page)}")

# Hash-based duplicate detection
hash_to_files = defaultdict(list)
for path, h in image_hashes.items():
    hash_to_files[h].append(path)
dup_hashes = {k: v for k, v in hash_to_files.items() if len(v) > 1}
print(f"  Unique image hashes: {len(hash_to_files)}")
print(f"  Duplicate hash groups (same content, different name): {len(dup_hashes)}")

# ============================================================
# STEP 9: alt/figcaption analysis
# ============================================================
print("\n" + "="*60)
print("STEP 9: alt/figcaption Analysis")
print("="*60)

alt_patterns = Counter()
fig_patterns = Counter()
generic_alts = 0
generic_figs = 0
total_alts = 0
total_figs = 0

for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    alts = re.findall(r'<img[^>]+alt=["\'](.*?)["\']', content)
    figs = re.findall(r'<figcaption[^>]*>(.*?)</figcaption>', content, re.DOTALL)
    
    for alt in alts:
        total_alts += 1
        alt_clean = re.sub(r'<[^>]+>', '', alt).strip()
        if re.match(r'^[\w\s]+(사진|이미지|포토)$', alt_clean) or len(alt_clean) < 10:
            generic_alts += 1
        alt_patterns[alt_clean[:50]] += 1
    
    for fig in figs:
        total_figs += 1
        fig_clean = re.sub(r'<[^>]+>', '', fig).strip()
        if re.match(r'^[\w\s]+(사진|이미지|포토)$', fig_clean) or len(fig_clean) < 10:
            generic_figs += 1
        fig_patterns[fig_clean[:50]] += 1

print(f"  Total alt attributes: {total_alts}")
print(f"  Generic alt patterns: {generic_alts} ({generic_alts/max(total_alts,1)*100:.1f}%)")
print(f"  Total figcaptions: {total_figs}")
print(f"  Generic figcaption patterns: {generic_figs} ({generic_figs/max(total_figs,1)*100:.1f}%)")
print(f"  Most common alt texts:")
for alt, cnt in alt_patterns.most_common(10):
    print(f"    [{cnt}x] {alt}")

# ============================================================
# STEP 10: MRT coupon/affiliate link analysis
# ============================================================
print("\n" + "="*60)
print("STEP 10: MRT Coupon/Affiliate Link Analysis")
print("="*60)

MRT_LINK = "https://myrealt.rip/YuJbb5"
mrt_stats = {
    'has_hidden_image': 0,
    'has_coupon_image': 0,
    'has_cta': 0,
    'has_disclosure': 0,
    'has_link': 0,
    'total_links': 0,
}
no_mrt = []

for f in html_files:
    content = f.read_text(encoding='utf-8', errors='replace')
    link_count = content.count(MRT_LINK)
    
    if MRT_LINK in content:
        mrt_stats['has_link'] += 1
        mrt_stats['total_links'] += link_count
        if 'hidden' in content.lower() or '숨김' in content:
            mrt_stats['has_hidden_image'] += 1
        if 'coupon' in content.lower() or '쿠폰' in content:
            mrt_stats['has_coupon_image'] += 1
        if 'cta' in content.lower() or 'button' in content.lower():
            mrt_stats['has_cta'] += 1
        if '제휴' in content or 'affiliate' in content.lower() or 'sponsored' in content.lower():
            mrt_stats['has_disclosure'] += 1
    else:
        no_mrt.append(str(f))

print(f"  Files with MRT link: {mrt_stats['has_link']} / {len(html_files)}")
print(f"  Files WITHOUT MRT link: {len(no_mrt)}")
print(f"  Total MRT link occurrences: {mrt_stats['total_links']}")
print(f"  With disclosure text: {mrt_stats['has_disclosure']}")
print(f"  With hidden image: {mrt_stats['has_hidden_image']}")
print(f"  With coupon image: {mrt_stats['has_coupon_image']}")
print(f"  With CTA: {mrt_stats['has_cta']}")

# ============================================================
# Save results
# ============================================================
print("\n" + "="*60)
print("Saving audit results...")
print("="*60)

audit = {
    "step1_distribution": {
        "total_html": len(html_files),
        "cities": len(city_cat),
        "categories_per_city": {city: {cat: len(files) for cat, files in cats.items()} for city, cats in city_cat.items()},
    },
    "step2_title_meta": {
        "total_titles": len(titles),
        "unique_titles": len(set(titles)),
        "duplicate_title_groups": len(dup_titles),
        "total_metas": len(metas),
        "unique_metas": len(set(metas)),
        "duplicate_meta_groups": len(dup_metas),
        "sample_dup_titles": {k[:80]: len(v) for k, v in list(dup_titles.items())[:10]},
    },
    "step3_content": {
        "korean_min": min(korean_counts),
        "korean_max": max(korean_counts),
        "korean_avg": round(sum(korean_counts)/len(korean_counts)),
        "articles_under_1500": len(short_articles),
        "articles_with_chinese": len(chinese_articles),
        "articles_with_emoji": len(emoji_articles),
    },
    "step4_particles": {
        "total_errors": total_particle_errors,
        "by_type": {name: sum(cnt for _, cnt in files) for name, files in particle_errors.items()},
    },
    "step5_repetitive_phrases": {phrase: {"total": t, "files": f} for phrase, (t, f) in phrase_counts.items()},
    "step6_structure": {
        "unique_h2_structures": len(structure_sigs),
        "duplicate_groups": len(dup_structures),
    },
    "step7_faq": {
        "files_with_faq": faq_count,
        "duplicate_faq_groups": len(dup_faqs),
    },
    "step8_images": {
        "webp_on_disk": len(all_webp_on_disk),
        "total_refs": len(img_refs),
        "missing": len(missing_images),
        "non_webp": len(non_webp),
        "in_page_duplicates": len(dup_in_page),
        "unique_hashes": len(hash_to_files),
        "duplicate_hash_groups": len(dup_hashes),
    },
    "step9_alt_figcaption": {
        "total_alts": total_alts,
        "generic_alts": generic_alts,
        "total_figs": total_figs,
        "generic_figs": generic_figs,
    },
    "step10_mrt": mrt_stats,
    "files_without_mrt": len(no_mrt),
}

with open("BALI_QUALITY_AUDIT_BEFORE.json", "w", encoding="utf-8") as jf:
    json.dump(audit, jf, ensure_ascii=False, indent=2)

with open("BALI_QUALITY_AUDIT_BEFORE.txt", "w", encoding="utf-8") as tf:
    tf.write("JP Travel Bali - Quality Audit (Before Improvement)\n")
    tf.write("="*60 + "\n\n")
    tf.write(f"Total HTML: {len(html_files)}\n")
    tf.write(f"Cities: {len(city_cat)} ({', '.join(sorted(city_cat.keys()))})\n")
    tf.write(f"Categories: 7 (food, beach, culture, nature, shopping, transport)\n")
    tf.write(f"Articles per city-category: 12\n\n")
    tf.write(f"STEP 2 - Title/Meta:\n")
    tf.write(f"  Unique titles: {len(set(titles))}/{len(titles)}\n")
    tf.write(f"  Duplicate title groups: {len(dup_titles)}\n")
    tf.write(f"  Unique meta descriptions: {len(set(metas))}/{len(metas)}\n")
    tf.write(f"  Duplicate meta groups: {len(dup_metas)}\n\n")
    tf.write(f"STEP 3 - Content:\n")
    tf.write(f"  Korean chars: min={min(korean_counts)} max={max(korean_counts)} avg={sum(korean_counts)//len(korean_counts)}\n")
    tf.write(f"  Under 1500 chars: {len(short_articles)}\n")
    tf.write(f"  Chinese/Hanja: {len(chinese_articles)}\n")
    tf.write(f"  Emoji: {len(emoji_articles)}\n\n")
    tf.write(f"STEP 4 - Particles:\n")
    tf.write(f"  Total errors: {total_particle_errors}\n")
    for name, files in sorted(particle_errors.items()):
        tf.write(f"    {name}: {sum(cnt for _, cnt in files)}\n")
    tf.write(f"\nSTEP 5 - Repetitive phrases:\n")
    for phrase, (total, fc) in sorted(phrase_counts.items(), key=lambda x: -x[1][0]):
        tf.write(f"  {phrase}: {total} in {fc} files\n")
    tf.write(f"\nSTEP 6 - H2 structure:\n")
    tf.write(f"  Unique: {len(structure_sigs)}, Duplicate groups: {len(dup_structures)}\n")
    tf.write(f"\nSTEP 7 - FAQ:\n")
    tf.write(f"  Files with FAQ: {faq_count}, Duplicate groups: {len(dup_faqs)}\n")
    tf.write(f"\nSTEP 8 - Images:\n")
    tf.write(f"  WebP on disk: {len(all_webp_on_disk)}\n")
    tf.write(f"  References: {len(img_refs)}, Missing: {len(missing_images)}\n")
    tf.write(f"  In-page dup: {len(dup_in_page)}, Hash dup groups: {len(dup_hashes)}\n")
    tf.write(f"\nSTEP 9 - alt/figcaption:\n")
    tf.write(f"  Total alts: {total_alts}, Generic: {generic_alts}\n")
    tf.write(f"  Total figs: {total_figs}, Generic: {generic_figs}\n")
    tf.write(f"\nSTEP 10 - MRT:\n")
    tf.write(f"  With link: {mrt_stats['has_link']}/{len(html_files)}\n")
    tf.write(f"  Without: {len(no_mrt)}\n")
    tf.write(f"  Total links: {mrt_stats['total_links']}\n")
    tf.write(f"  Disclosure: {mrt_stats['has_disclosure']}\n")

print("Audit saved to BALI_QUALITY_AUDIT_BEFORE.json and .txt")
print("DONE")
