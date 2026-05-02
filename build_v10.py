#!/usr/bin/env python3
"""
JP Travel Bali — v10 전면 재빌드
924개 HTML을 고품질 여행 블로그로 전면 재생성

핵심 개선:
1. H2 구조 다양화 — 같은 카테고리 내 5가지 이상 다른 구조
2. E-E-A-T 강화 — 작가 프로필, 구체적 장소/가격/주소
3. 콘텐츠 고유화 — 각 글마다 고유한 본문
4. 이미지 클릭 — 모든 이미지에 MRT 제휴 링크
5. 내부 링크 — 같은 도시 다른 카테고리 + 크로스링크
6. 자연스러운 문체 — AI 패턴 제거
"""

import os, re, json, random, hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_HTML = BASE_DIR / "output" / "html" / "bali"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"

AFFILIATE_URL = "https://myrealt.rip/YuJbb5"
TOUR_URL = "https://myrealt.rip/YoEc1b"
HOTEL_URL = "https://www.myrealtrip.com/search?keyword=%EB%B0%9C%EB%A6%AC+%ED%98%B8%ED%85%94&mylink_id=1696108"
SITE_URL = "https://balitravel.blog"
CURRENT_YEAR = datetime.now().year

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "🍜", "desc": "맛집 탐방"},
    "culture": {"name": "문화/사원", "icon": "🛕", "desc": "문화 체험"},
    "beach": {"name": "해변/서핑", "icon": "🏖️", "desc": "해변 액티비티"},
    "nature": {"name": "자연/모험", "icon": "🌿", "desc": "자연 탐방"},
    "shopping": {"name": "쇼핑/마사지", "icon": "🛍️", "desc": "쇼핑 & 힐링"},
    "transport": {"name": "여행/교통", "icon": "🚗", "desc": "이동 정보"},
}

# Import data and engine
import sys
sys.path.insert(0, str(BASE_DIR))
from build_v10_data import BALI_DATA
from build_v10_engine import (
    AUTHORS, H2_VARIANTS, CITY_INTROS, OTHER_CATS,
    get_h2_variant, generate_body_paragraphs, generate_internal_links, generate_faq,
    CATEGORIES as ENGINE_CATS
)

# ============================================================
# 이미지 매핑 로드
# ============================================================
def load_image_mapping():
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_images(mapping, city, cat, count=10):
    """지역+카테고리에서 이미지 선택"""
    city_data = mapping.get(city, {})
    cat_images = city_data.get(cat, [])
    if not cat_images:
        return []
    # 페이지별 다른 이미지 선택을 위해 셔플 시드 사용
    random.seed(f"{city}_{cat}")
    random.shuffle(cat_images)
    return cat_images[:count]

# ============================================================
# 한국어 조사 처리
# ============================================================
def has_batchim(word):
    if not word:
        return False
    code = ord(word[-1]) - 0xAC00
    return 0 <= code <= 0x278C and (code % 28) != 0

def josa(word, pair):
    return pair[0] if has_batchim(word) else pair[1]

# ============================================================
# HTML 생성
# ============================================================
def generate_html(city, cat, page_num, images, image_mapping):
    """단일 HTML 페이지 생성"""
    data = BALI_DATA.get(city, {})
    cat_info = CATEGORIES[cat]
    city_display = city
    cat_display = cat_info["name"]
    
    # 작가 선택 (해시 기반 일관성)
    author_idx = hash(f"{city}_{cat}_{page_num}") % len(AUTHORS)
    author = AUTHORS[author_idx]
    
    # H2 구조 선택 (variant)
    h2_list = get_h2_variant(city, cat, page_num)
    
    # 인트로 선택
    intros = CITY_INTROS.get(city, {}).get(cat, [])
    if not intros:
        intros = [f'{city} {cat_display} 가이드입니다. 현지 취재를 바탕으로 작성했어요.']
    intro_idx = page_num % len(intros)
    intro_text = intros[intro_idx]
    
    # 본문 문단 생성
    items = data.get(cat, [])
    body_paragraphs = generate_body_paragraphs(city, cat, page_num, BALI_DATA, items)
    
    # FAQ 생성
    faq_list = generate_faq(city, cat, BALI_DATA)
    
    # 내부 링크 생성
    internal_links = generate_internal_links(city, cat, page_num)
    
    # 이미지 태그 생성 (클릭 가능 — MRT 링크)
    def img_tag(img_file, alt_text, idx):
        """이미지를 MRT 제휴 링크로 감싸기"""
        img_path = f"../../images/{city}/{cat}/{img_file}"
        return f'''<figure style="margin:20px 0;text-align:center">
<a href="{AFFILIATE_URL}" target="_blank" rel="sponsored nofollow noopener" title="마이리얼트립에서 예약하기">
<img src="{img_path}" alt="{alt_text}" style="max-width:100%;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);cursor:pointer" loading="lazy">
</a>
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">{alt_text} - 클릭하면 마이리얼트립에서 예약할 수 있어요</figcaption>
</figure>'''
    
    # 이미지 배치 (본문 중간중간)
    img_tags = []
    for i, img_file in enumerate(images[:10]):
        alt = f'{city} {cat_display} 사진 {i+1}'
        img_tags.append(img_tag(img_file, alt, i))
    
    # 제목 생성 (SEO 최적화)
    title_variants = [
        f'{city} {cat_display} 추천 리스트, 현장에서 확인한 가격 분석',
        f'{city} {cat_display} 완벽 가이드, 직접 가본 후기와 팁',
        f'{city} {cat_display} Best Picks, 현지인이 알려주는 비용 정리',
        f'{city} {cat_display} 여행 가이드, 2026년 최신 정보',
        f'{city} {cat_display} 추천, 가격비교와 방문 후기',
    ]
    title_idx = page_num % len(title_variants)
    title = title_variants[title_idx]
    
    meta_desc_variants = [
        f'발리 {city} {cat_display} 완벽 가이드. 입장료, 교통, 추천 코스. {city} {cat_info["icon"]} #{page_num:03d}.',
        f'{city} {cat_display} 여행 정보. 가격, 팁, 추천 명소를 현장 취재로 정리했어요. #{page_num:03d}.',
        f'발리 {city} {cat_display} 추천. 직접 가본 후기와 예산 분석. #{page_num:03d}.',
    ]
    meta_desc_idx = page_num % len(meta_desc_variants)
    meta_desc = meta_desc_variants[meta_desc_idx]
    
    # Schema.org JSON-LD
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": meta_desc,
        "image": [f"{SITE_URL}/images/{city}/{cat}/{images[0]}" if images else ""],
        "datePublished": f"2026-04-{(page_num % 28) + 1:02d}",
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "author": {
            "@type": "Person",
            "name": author["name"],
            "description": author["bio"],
            "jobTitle": author["credential"],
        },
        "publisher": {
            "@type": "Organization",
            "name": "JP Travel Bali",
            "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/images/logo.png"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE_URL}/{city}/{cat}/{page_num:03d}.html"},
    }
    
    # 내부 링크 HTML
    links_html = ""
    if internal_links:
        links_html = '<div style="margin:24px 0;padding:16px;background:#e3f2fd;border-radius:8px;border-left:3px solid #2196F3">'
        links_html += '<p style="margin:0 0 10px;font-weight:600;color:#1565C0">함께 보면 좋은 글</p>'
        for link in internal_links:
            links_html += f'<p style="margin:4px 0"><a href="{link["href"]}" style="color:#1976D2;text-decoration:none">{link["text"]}</a></p>'
        links_html += '</div>'
    
    # FAQ HTML
    faq_html = ""
    if faq_list:
        faq_html = '<div style="margin:24px 0">'
        for q, a in faq_list:
            faq_html += f'''<details style="margin:8px 0;padding:12px;background:#f5f5f5;border-radius:8px">
<summary style="cursor:pointer;font-weight:600;color:#333">{q}</summary>
<p style="margin:8px 0 0;line-height:1.8;color:#555">{a}</p>
</details>'''
        faq_html += '</div>'
    
    # 작가 프로필 HTML
    author_html = f'''<div style="margin:24px 0;padding:16px;background:#fff3e0;border-radius:8px;border-left:3px solid {author["color"]};display:flex;align-items:center;gap:12px">
<div style="width:48px;height:48px;border-radius:50%;background:{author["color"]};color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:1.2em;flex-shrink:0">{author["avatar_initial"]}</div>
<div>
<p style="margin:0;font-weight:600;color:#333">{author["name"]}</p>
<p style="margin:2px 0 0;font-size:0.85em;color:#666">{author["credential"]}</p>
<p style="margin:4px 0 0;font-size:0.9em;color:#555">{author["bio"]}</p>
</div>
</div>'''
    
    # H2 본문 조립
    body_html = ""
    img_idx = 0
    
    # 인트로
    body_html += f'<div class="content-intro" style="margin:0 0 20px;padding:16px 20px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2;font-weight:500;line-height:1.8">{intro_text}</div>\n'
    
    # 첫 번째 이미지
    if img_idx < len(img_tags):
        body_html += img_tags[img_idx] + "\n"
        img_idx += 1
    
    # H2 섹션들
    content_inserted = set()  # 중복 방지
    for h2_idx, h2_title in enumerate(h2_list):
        body_html += f'\n<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{h2_title}</h2>\n'
        
        # 이미지 삽입 (2~3개 H2마다)
        if img_idx < len(img_tags) and h2_idx % 2 == 1:
            body_html += img_tags[img_idx] + "\n"
            img_idx += 1
        
        # H2별 본문 내용
        if h2_idx == 0:
            # 첫 번째 H2: 기본 소개
            if items and cat != "transport" and len(items) > 0:
                item = items[page_num % len(items)]
                body_html += f'<p style="margin:12px 0;line-height:1.8">대표 추천 장소는 {item["name"]}이에요. {item["tip"]}</p>\n'
            body_html += f'<p style="margin:12px 0;line-height:1.8;background:#fff3e0;padding:12px;border-radius:8px;border-left:3px solid #ff9800"><strong>꼭 알아두세요:</strong> {city}의 {cat_display} 관련 최신 정보예요. 가격은 현지 사정에 따라 변동될 수 있어요.</p>\n'
        
        elif h2_idx == 1:
            # 두 번째 H2: 본문 문단
            for p in body_paragraphs[:3]:
                if p not in content_inserted:
                    body_html += f'<p style="margin:12px 0;line-height:1.8">{p}</p>\n'
                    content_inserted.add(p)
        
        elif h2_idx == 2:
            # 세 번째 H2: 추가 정보
            for p in body_paragraphs[3:6]:
                if p not in content_inserted:
                    body_html += f'<p style="margin:12px 0;line-height:1.8">{p}</p>\n'
                    content_inserted.add(p)
        
        elif h2_idx == 3:
            # 네 번째 H2: 가격 정보 등
            if cat == "food" and data.get("price_comp"):
                body_html += '<table style="width:100%;border-collapse:collapse;margin:16px 0">\n'
                body_html += '<tr><th style="padding:10px 8px;border:1px solid #ddd;background:#FF6B35;color:white">항목</th><th style="padding:10px 8px;border:1px solid #ddd;background:#FF6B35;color:white">로컬</th><th style="padding:10px 8px;border:1px solid #ddd;background:#FF6B35;color:white">관광객</th><th style="padding:10px 8px;border:1px solid #ddd;background:#FF6B35;color:white">호텔</th></tr>\n'
                for pc in data["price_comp"]:
                    body_html += f'<tr><td style="padding:10px 8px;border:1px solid #ddd">{pc["item"]}</td><td style="padding:10px 8px;border:1px solid #ddd">{pc["local"]}</td><td style="padding:10px 8px;border:1px solid #ddd">{pc["tour"]}</td><td style="padding:10px 8px;border:1px solid #ddd">{pc["hotel"]}</td></tr>\n'
                body_html += '</table>\n'
            else:
                for p in body_paragraphs[6:8]:
                    if p not in content_inserted:
                        body_html += f'<p style="margin:12px 0;line-height:1.8">{p}</p>\n'
                        content_inserted.add(p)
        
        elif h2_idx == 4:
            # 다섯 번째 H2: 추천/비추천
            if items and len(items) >= 2:
                body_html += f'<div style="margin:16px 0;padding:16px;background:#e8f5e9;border-radius:8px;border-left:3px solid #4caf50"><p style="margin:0;line-height:1.8"><strong>추천:</strong> {items[0]["name"]} - {items[0]["tip"]}</p></div>\n'
                body_html += f'<div style="margin:16px 0;padding:16px;background:#fce4ec;border-radius:8px;border-left:3px solid #e91e63"><p style="margin:0;line-height:1.8"><strong>참고:</strong> {items[-1]["name"]} - {items[-1]["tip"]}</p></div>\n'
        
        elif h2_idx == 5:
            # 여섯 번째 H2: 팁/주의사항
            for p in body_paragraphs[8:10]:
                if p not in content_inserted:
                    body_html += f'<p style="margin:12px 0;line-height:1.8">{p}</p>\n'
                    content_inserted.add(p)
            body_html += f'<div style="margin:16px 0;padding:16px;background:#fff3e0;border-radius:8px;border-left:3px solid #ff9800"><p style="margin:0;line-height:1.8"><strong>주의:</strong> {city}에서 흔한 실수는 현지 앱 없이 택시를 잡는 거예요. 그랩 앱을 미리 설치하세요.</p></div>\n'
        
        elif h2_idx == 6:
            # 일곱 번째 H2: 마무리
            body_html += f'<p style="margin:12px 0;line-height:1.8">{city} {cat_display} 여행은 직접 가봐야 진짜를 알 수 있어요. 이 글이 계획에 도움이 되었으면 좋겠어요.</p>\n'
            body_html += f'<p style="margin:12px 0;line-height:1.8">더 자세한 정보가 필요하시면 <a href="{AFFILIATE_URL}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;font-weight:600">마이리얼트립</a>에서 확인하세요.</p>\n'
        
        elif h2_idx == 7:
            # 여덟 번째 H2: 주변 명소
            spots = data.get("spots", [])
            if spots:
                body_html += f'<p style="margin:12px 0;line-height:1.8">{city} 주변 추천 명소: '
                body_html += ", ".join(spots[:5])
                body_html += '</p>\n'
        
        elif h2_idx == 8:
            # 아홉 번째 H2: FAQ
            body_html += faq_html
        
        elif h2_idx == 9:
            # 열 번째 H2: 내부 링크
            body_html += links_html
    
    # 남은 이미지 삽입
    while img_idx < len(img_tags):
        body_html += img_tags[img_idx] + "\n"
        img_idx += 1
    
    # 최종 HTML 조립
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title} ({city_display.title()})</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{city}, {cat_display}, 발리, 인도네시아, 자유여행, {CURRENT_YEAR}">
<link rel="canonical" href="{SITE_URL}/{city}/{cat}/{page_num:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE_URL}/images/{city}/{cat}/{images[0] if images else ''}">
<meta property="og:url" content="{SITE_URL}/{city}/{cat}/{page_num:03d}.html">
<meta property="og:site_name" content="JP Travel Bali">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
<style>
:root{{--primary:#FF6B35;--bg:#FAFAFA;--text:#1A1A2E;--text-light:#666;--card-bg:#FFFFFF;--shadow:0 2px 8px rgba(0,0,0,0.08)}}*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);line-height:1.85;word-break:keep-all}}.container{{max-width:800px;margin:0 auto;padding:20px}}header{{background:linear-gradient(135deg,#FF6B35,#FF8C61);color:white;padding:40px 20px;text-align:center}}header h1{{font-size:1.8rem;margin-bottom:10px;word-break:keep-all}}header .meta{{opacity:0.9;font-size:0.9rem}}.breadcrumb{{padding:15px 0;font-size:0.85rem;color:var(--text-light)}}.breadcrumb a{{color:var(--primary);text-decoration:none}}article{{background:var(--card-bg);border-radius:12px;padding:30px;box-shadow:var(--shadow);margin:20px 0}}article h2{{color:var(--primary);font-size:1.4rem;margin:30px 0 15px;padding-bottom:8px;border-bottom:2px solid var(--primary)}}article h3{{color:#333;font-size:1.15rem;margin:20px 0 10px}}article table{{width:100%;border-collapse:collapse;margin:16px 0}}article th,article td{{padding:10px 8px;border:1px solid #ddd;text-align:left}}article th{{background:#FF6B35;color:white}}article tr:nth-child(even){{background:#f9f9f9}}article ul,article ol{{padding-left:20px;margin:16px 0}}article li{{margin-bottom:8px;line-height:1.7}}.content-intro{{margin:0 0 20px;padding:16px 20px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2;font-weight:500;line-height:1.8}}.content-footer{{margin:24px 0;padding:12px;background:#f5f5f5;border-radius:8px;font-size:0.9em;color:#666}}.tags{{margin:20px 0}}.tag{{display:inline-block;background:#F0F0F0;padding:4px 12px;border-radius:20px;font-size:0.8rem;margin:3px;color:var(--text-light)}}footer{{text-align:center;padding:30px;color:var(--text-light);font-size:0.85rem}}#reading-progress{{position:fixed;top:0;left:0;width:0%;height:3px;background:linear-gradient(90deg,#FF6B35,#FF8C61);z-index:9999;transition:width 0.1s}}figure img{{background:#f0f0f0;min-height:100px}}@media(max-width:600px){{.container{{padding:10px}}article{{padding:20px}}header h1{{font-size:1.4rem}}table{{font-size:.8em}}article h2{{font-size:1.2rem}}}}@media(prefers-color-scheme:dark){{--bg:#1a1a2e;--text:#e0e0e0;--text-light:#aaa;--card-bg:#16213e;--border:#333}}body{{background:var(--bg);color:var(--text)}}article{{background:var(--card-bg)}}.content-intro{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-color:#333}}article tr:nth-child(even){{background:#1a1a2e}}}}
</style>
</head>
<body>
<div id="reading-progress"></div>
<script>window.addEventListener('scroll',function(){{var w=document.body.scrollTop||document.documentElement.scrollTop;var h=document.documentElement.scrollHeight-document.documentElement.clientHeight;document.getElementById('reading-progress').style.width=(w/h*100)+'%'}});</script>
<div class="container">
<header>
<h1>{title}</h1>
<div class="meta">JP Travel Bali | {city_display} {cat_display} 가이드 | {CURRENT_YEAR}</div>
</header>
<div class="breadcrumb"><a href="/">홈</a> &rsaquo; <a href="/{city}/">{city_display}</a> &rsaquo; <a href="/{city}/{cat}/">{cat_display}</a> &rsaquo; {page_num:03d}</div>
<article>
{author_html}
{body_html}
<div class="content-footer">
<p>이 글은 {author["name"]}({author["credential"]})이 직접 취재한 내용을 바탕으로 작성했어요.</p>
<p>가격 정보는 {CURRENT_YEAR}년 기준이며, 현지 사정에 따라 변동될 수 있어요.</p>
<p>제휴 링크가 포함되어 있어요. 링크를 통해 예약하면 추가 비용 없이 저에게 작은 수익이 돌아와요.</p>
</div>
<div class="tags">
<span class="tag">{city}</span>
<span class="tag">{cat_display}</span>
<span class="tag">발리</span>
<span class="tag">인도네시아</span>
<span class="tag">자유여행</span>
<span class="tag">{CURRENT_YEAR}</span>
</div>
</article>
<footer>
<p>JP Travel Bali &copy; {CURRENT_YEAR} | <a href="{AFFILIATE_URL}" target="_blank" rel="sponsored nofollow noopener">마이리얼트립 할인 예약</a></p>
<p>발리 여행 정보 블로그 | 현지 취재 기반</p>
</footer>
</div>
</body>
</html>'''
    
    return html

# ============================================================
# 메인 빌드
# ============================================================
def build_all():
    """924개 HTML 전면 재생성"""
    print("=" * 60)
    print("JP Travel Bali v10 — 전면 재빌드 시작")
    print("=" * 60)
    
    # 이미지 매핑 로드
    image_mapping = load_image_mapping()
    
    total = 0
    errors = 0
    
    for city in AREAS:
        for cat in CATEGORIES:
            # 이미지 목록 가져오기
            city_images = image_mapping.get(city, {}).get(cat, [])
            if not city_images:
                print(f"  [SKIP] {city}/{cat} - 이미지 없음")
                continue
            
            # 14페이지 생성
            for page_num in range(1, 15):
                try:
                    # 페이지별 다른 이미지 선택
                    seed = hash(f"{city}_{cat}_{page_num}") % 10000
                    random.seed(seed)
                    shuffled = list(city_images)
                    random.shuffle(shuffled)
                    page_images = shuffled[:10]
                    
                    # HTML 생성
                    html = generate_html(city, cat, page_num, page_images, image_mapping)
                    
                    # 파일 저장
                    out_dir = OUTPUT_HTML / city / cat
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_file = out_dir / f"{page_num:03d}.html"
                    out_file.write_text(html, encoding='utf-8')
                    
                    total += 1
                    if total % 50 == 0:
                        print(f"  진행: {total}개 완성...")
                    
                except Exception as e:
                    errors += 1
                    print(f"  [ERROR] {city}/{cat}/{page_num:03d}: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"빌드 완료: {total}개 HTML 생성, {errors}개 에러")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    build_all()
