#!/usr/bin/env python3
"""Full 924-file quality audit - every check, every file."""
import re, json, hashlib
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path('output/html/bali')
MRT = 'https://myrealt.rip/YuJbb5'

html_files = sorted(BASE.rglob('*.html'))
total = len(html_files)
print(f'총 HTML 파일: {total}')
print('='*70)

issues = defaultdict(list)
stats = defaultdict(int)

hanja_re = re.compile(r'[\u4e00-\u9fff]')
emoji_re = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\u200D\uFE0F]')
particle_re = re.compile(r'을\(를\)|은\(는\)|이\(가\)|와\(과\)|\{을\(를\)\}|\{은\(는\)\}|\{이\(가\)\}|\{와\(과\)\}')

titles = []
metas = []
korean_counts = []
h2_sigs = []
faq_sigs = []
phrase_check = ['2026년 기준', '여행 준비물 체크리스트', '숨은 명소', '실전 팁', '끝까지 읽어보세요', '추천이에요', '10년차 블로거', '인생샷', '포토스팟']
phrase_counts = defaultdict(int)

for i, f in enumerate(html_files):
    c = f.read_text(encoding='utf-8')
    rel = str(f.relative_to(BASE))
    parts = f.relative_to(BASE).parts
    city, cat, fname = parts[0], parts[1], parts[2]
    an = int(fname.replace('.html',''))

    # 1: Title
    m = re.search(r'<title>(.*?)</title>', c)
    titles.append(m.group(1) if m else 'MISSING')
    if not m: issues['title_missing'].append(rel)

    # 2: Meta
    m = re.search(r'<meta name="description" content="(.*?)"', c)
    metas.append(m.group(1) if m else 'MISSING')
    if not m: issues['meta_missing'].append(rel)

    # 3: Korean chars
    body = re.sub(r'<script[^>]*>.*?</script>', '', c, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', '', body)
    kr = len(re.findall(r'[가-힣]', body))
    korean_counts.append(kr)
    if kr < 1500: issues['short_content'].append((rel, kr))

    # 4: Chinese
    hanja = hanja_re.findall(body)
    if hanja: issues['chinese_chars'].append((rel, ''.join(hanja[:10])))

    # 5: Emoji
    emojis = emoji_re.findall(body)
    if emojis: issues['emoji'].append((rel, ''.join(emojis[:5])))

    # 6: Particles
    if particle_re.search(c): issues['particle_errors'].append(rel)

    # 7: Image refs
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']*)["\']', c)
    for img in imgs:
        if img.startswith('http'): continue
        resolved = (f.parent / img).resolve()
        if not resolved.exists(): issues['img_missing'].append((rel, img))

    # 8: In-page img dup
    img_counter = Counter(imgs)
    for img, cnt in img_counter.items():
        if cnt > 1: issues['img_inpage_dup'].append((rel, img, cnt))

    # 9: alt
    alts = re.findall(r'<img[^>]+alt=["\']([^"\']*)["\']', c)
    for alt in alts:
        if len(re.sub(r'\s','',alt)) < 3 and 'mrt_coupon' not in alt:
            issues['short_alt'].append((rel, alt))

    # 10: figcaption
    figs = re.findall(r'<figcaption[^>]*>(.*?)</figcaption>', c, re.DOTALL)
    for fig in figs:
        fig_clean = re.sub(r'<[^>]+>', '', fig).strip()
        if len(fig_clean) < 5:
            issues['short_figcaption'].append((rel, fig_clean))

    # 11: H2 structure
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', c, re.DOTALL)
    h2_clean = [re.sub(r'<[^>]+>', '', h).strip() for h in h2s]
    h2_sigs.append('|'.join(h2_clean))

    # 12: FAQ
    faq_qs = re.findall(r'Q\.\s*(.*?)</h3>', c)
    faq_sigs.append('|'.join([q.strip() for q in faq_qs[:4]]))

    # 13: MRT
    mrt_count = c.count(MRT)
    stats['total_mrt_links'] += mrt_count

    coupon_ok = bool(re.search(r'<a[^>]*href=["\']' + re.escape(MRT) + r'["\'][^>]*>\s*<img[^>]*mrt_coupon', c, re.DOTALL))
    if not coupon_ok: issues['coupon_wrong_link'].append(rel)

    hidden_ok = bool(re.search(r'width="1"\s*height="1"', c))
    if not hidden_ok: issues['no_hidden_img'].append(rel)

    if '제휴' not in c: issues['no_disclosure'].append(rel)
    if 'sponsored nofollow noopener' not in c: issues['no_rel_sponsored'].append(rel)
    if 'rel="canonical"' not in c: issues['no_canonical'].append(rel)
    if '@type' not in c or 'Article' not in c: issues['no_jsonld'].append(rel)
    if 'og:title' not in c: issues['no_og'].append(rel)
    if 'twitter:card' not in c: issues['no_twitter'].append(rel)
    if 'reading-progress' not in c: issues['no_progress_bar'].append(rel)

    # 14: Phrases
    for phrase in phrase_check:
        if phrase in c:
            phrase_counts[phrase] += 1

    if (i+1) % 300 == 0:
        print(f'  진행: {i+1}/{total}')

# ============================================================
print()
print('='*70)
print('전체 분석 결과 리포트')
print('='*70)

def status(ok, val='', target=''):
    return '[OK]' if ok else '[!!]'

print()
print('=== 1. 콘텐츠 품질 ===')
dup_t = len(titles) - len(set(titles))
dup_m = len(metas) - len(set(metas))
kr_min, kr_max = min(korean_counts), max(korean_counts)
kr_avg = sum(korean_counts) // len(korean_counts)
short = len(issues['short_content'])
print(f'  [1]  HTML 총 수:                   {total}')
print(f'  {status(dup_t==0)} Title 고유:                   {len(set(titles))}/{total} (중복: {dup_t})')
print(f'  {status(dup_m==0)} Meta desc 고유:               {len(set(metas))}/{total} (중복: {dup_m})')
print(f'  {status(short==0)} 한국어 본문 1500자 미만:      {short}개')
print(f'       한국어 글자:                    min={kr_min} avg={kr_avg} max={kr_max}')
print(f'  {status(len(issues["chinese_chars"])==0)} 한자/중국어:                   {len(issues["chinese_chars"])}개')
print(f'  {status(len(issues["emoji"])==0)} 이모지:                       {len(issues["emoji"])}개')
print(f'  {status(len(issues["particle_errors"])==0)} 조사 플레이스홀더:            {len(issues["particle_errors"])}개')

print()
print('=== 2. 이미지 ===')
print(f'  {status(len(issues["img_missing"])==0)} 이미지 파일 누락:             {len(issues["img_missing"])}개')
print(f'  {status(len(issues["img_inpage_dup"])==0)} 같은 페이지 내 이미지 중복:   {len(issues["img_inpage_dup"])}개')
print(f'  {status(len(issues["short_alt"])==0)} alt 텍스트 부족(3자 미만):    {len(issues["short_alt"])}개')
print(f'  {status(len(issues["short_figcaption"])==0)} figcaption 부족:             {len(issues["short_figcaption"])}개')

print()
print('=== 3. H2/FAQ 구조 다양성 ===')
unique_h2 = len(set(h2_sigs))
dup_h2_groups = sum(1 for v in Counter(h2_sigs).values() if v > 1)
unique_faq = len(set(faq_sigs))
dup_faq_groups = sum(1 for v in Counter(faq_sigs).values() if v > 1)
print(f'  {status(unique_h2>100)} H2 구조 유니크:              {unique_h2}개')
print(f'       H2 중복 그룹:                  {dup_h2_groups}개 (같은 구조를 공유하는 그룹)')
# Top H2 duplicates
top_h2 = Counter(h2_sigs).most_common(3)
for sig, cnt in top_h2:
    print(f'         [{cnt}x] {sig[:70]}...')
print(f'  {status(unique_faq>500)} FAQ 유니크:                   {unique_faq}개')
print(f'       FAQ 중복 그룹:                 {dup_faq_groups}개')

print()
print('=== 4. MRT 제휴 링크 ===')
print(f'  {status(total - len(issues["coupon_wrong_link"])==total)} 쿠폰 이미지→MRT 링크:        {total - len(issues["coupon_wrong_link"])}/{total}')
print(f'  {status(total - len(issues["no_hidden_img"])==total)} 히든 이미지(1x1px):           {total - len(issues["no_hidden_img"])}/{total}')
print(f'  {status(total - len(issues["no_disclosure"])==total)} 제휴 고지문:                  {total - len(issues["no_disclosure"])}/{total}')
print(f'  {status(total - len(issues["no_rel_sponsored"])==total)} rel=sponsored nofollow:       {total - len(issues["no_rel_sponsored"])}/{total}')
print(f'       MRT 링크 총 개수:              {stats["total_mrt_links"]} (평균 {stats["total_mrt_links"]//total}/파일)')

print()
print('=== 5. 기술 SEO ===')
print(f'  {status(total - len(issues["no_canonical"])==total)} canonical URL:                {total - len(issues["no_canonical"])}/{total}')
print(f'  {status(total - len(issues["no_jsonld"])==total)} JSON-LD (Article):            {total - len(issues["no_jsonld"])}/{total}')
print(f'  {status(total - len(issues["no_og"])==total)} OG 태그:                      {total - len(issues["no_og"])}/{total}')
print(f'  {status(total - len(issues["no_twitter"])==total)} Twitter 카드:                 {total - len(issues["no_twitter"])}/{total}')
print(f'  {status(total - len(issues["no_progress_bar"])==total)} 읽기 진행 바:                 {total - len(issues["no_progress_bar"])}/{total}')
print(f'  {status(Path("sitemap.xml").exists())} sitemap.xml:                  {"존재" if Path("sitemap.xml").exists() else "없음"}')
print(f'  {status(Path("robots.txt").exists())} robots.txt:                   {"존재" if Path("robots.txt").exists() else "없음"}')

print()
print('=== 6. 반복 문구 빈도 ===')
for phrase in phrase_check:
    cnt = phrase_counts.get(phrase, 0)
    pct = cnt * 100 // total
    mark = status(cnt < total * 0.5)
    print(f'  {mark} "{phrase}": {cnt}/{total} ({pct}%)')

print()
print('=== 7. 도시·카테고리 분포 ===')
city_cat_count = defaultdict(lambda: defaultdict(int))
for f in html_files:
    parts = f.relative_to(BASE).parts
    city_cat_count[parts[0]][parts[1]] += 1
for city in sorted(city_cat_count):
    cats = city_cat_count[city]
    total_c = sum(cats.values())
    cat_str = ', '.join(f'{c}:{n}' for c, n in sorted(cats.items()))
    print(f'  {city}: {total_c} ({cat_str})')

# Issue details
print()
print('='*70)
print('상세 이슈 목록 (FAIL인 항목만)')
print('='*70)

any_issues = False
for key in ['title_missing','meta_missing','short_content','chinese_chars','emoji',
            'particle_errors','img_missing','img_inpage_dup','short_alt','short_figcaption',
            'coupon_wrong_link','no_hidden_img','no_disclosure','no_rel_sponsored',
            'no_canonical','no_jsonld','no_og','no_twitter','no_progress_bar']:
    items = issues.get(key, [])
    if items:
        any_issues = True
        print(f'\n[{key}] {len(items)}개:')
        for item in items[:5]:
            if isinstance(item, tuple):
                print(f'  - {item[0]}: {item[1]}')
            else:
                print(f'  - {item}')
        if len(items) > 5:
            print(f'  ... 외 {len(items)-5}개')

if not any_issues:
    print('\n  ==> 모든 검사 통과! 이슈 없음.')

# Final verdict
print()
print('='*70)
fail_count = 0
checks = [
    (dup_t == 0, 'Title 중복'),
    (dup_m == 0, 'Meta 중복'),
    (short == 0, '본문 1500자 미만'),
    (len(issues['chinese_chars']) == 0, '한자/중국어'),
    (len(issues['emoji']) == 0, '이모지'),
    (len(issues['particle_errors']) == 0, '조사 오류'),
    (len(issues['img_missing']) == 0, '이미지 누락'),
    (len(issues['img_inpage_dup']) == 0, '페이지 내 이미지 중복'),
    (total - len(issues['coupon_wrong_link']) == total, '쿠폰→MRT 링크'),
    (total - len(issues['no_hidden_img']) == total, '히든 이미지'),
    (total - len(issues['no_disclosure']) == total, '제휴 고지문'),
    (total - len(issues['no_rel_sponsored']) == total, 'rel=sponsored'),
    (Path('sitemap.xml').exists(), 'sitemap.xml'),
    (Path('robots.txt').exists(), 'robots.txt'),
]
for ok, name in checks:
    if not ok:
        fail_count += 1
        print(f'  [FAIL] {name}')
    else:
        print(f'  [PASS] {name}')

print()
if fail_count == 0:
    print('==> 최종 결과: 전체 통과 (14/14 PASS)')
else:
    print(f'==> 최종 결과: {fail_count}개 실패 / {len(checks)}개 검사')
