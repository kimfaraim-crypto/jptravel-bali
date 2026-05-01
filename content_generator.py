#!/usr/bin/env python3
"""
AI 기반 고유 콘텐츠 생성기
- 11지역 × 6카테고리 × 14페이지 = 924 고유 글
- 네이버 Cue: 최적화 구조 (표, 리스트, 결론박스)
- MiMo 모델 기반 생성
"""
import os, sys, json, time, hashlib, random
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
OUTPUT_HTML = BASE_DIR / "output" / "html" / "bali"
MAPPING_FILE = BASE_DIR / "image_mapping_v3.json"
CONTENT_DB = BASE_DIR / "generated_content.json"

AREAS = ["우붓", "스미냑", "꾸따", "사누르", "누사두아", "울루와뚜", "짠디다사", "로비나", "킨타마니", "타나롯", "베두굴"]

CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "🍜", "desc": "맛집 탐방", "en": "food"},
    "culture": {"name": "문화/사원", "icon": "🛕", "desc": "문화 체험", "en": "culture"},
    "beach": {"name": "해변/서핑", "icon": "🏖️", "desc": "해변 액티비티", "en": "beach"},
    "nature": {"name": "자연/모험", "icon": "🌿", "desc": "자연 탐방", "en": "nature"},
    "shopping": {"name": "쇼핑/마사지", "icon": "🛍️", "desc": "쇼핑 & 힐링", "en": "shopping"},
    "transport": {"name": "여행/교통", "icon": "🚗", "desc": "이동 정보", "en": "transport"},
}

AFFILIATE_URL = "https://myrealt.rip/YuJbb5"
TOUR_URL = "https://myrealt.rip/YoEc1b"
HOTEL_URL = "https://www.myrealtrip.com/search?keyword=%EB%B0%9C%EB%A6%AC+%ED%98%B8%ED%85%94&mylink_id=1696108"
SITE_URL = "https://balitravel.blog"
AUTHOR = "발리 여행 10년차 블로거"
CURRENT_YEAR = datetime.now().year

# 지역별 상세 데이터 (기존 BALI_DATA 활용)
from build_bali import BALI_DATA, CATEGORIES as CAT_DATA, CATEGORY_EXTRA_CONTENT

def load_image_mapping():
    if MAPPING_FILE.exists():
        return json.loads(MAPPING_FILE.read_text())
    return {}

def get_images(area, category, count=10, page_offset=0):
    """페이지별 고유 이미지 선택 (오프셋 기반)"""
    mapping = load_image_mapping()
    imgs = mapping.get(area, {}).get(category, [])
    if not imgs:
        # Picsum fallback
        return [f"https://picsum.photos/seed/{hashlib.md5(f'{area}_{category}_{i}_{page_offset}'.encode()).hexdigest()[:10]}/1200/800" for i in range(count)]
    
    # 페이지 오프셋 기반으로 다른 이미지 선택
    total = len(imgs)
    if total >= count:
        start = (page_offset * count) % total
        selected = []
        for i in range(count):
            idx = (start + i) % total
            selected.append(imgs[idx])
        return selected
    return imgs[:count]

def generate_content_prompt(area, category, page_idx, data):
    """AI 콘텐츠 생성 프롬프트"""
    cat_info = CATEGORIES[category]
    
    # 기존 데이터에서 참조 정보 추출
    cat_data = data.get(category, [])
    food_items = data.get("food", [])
    qa = data.get("intro_qa", [])
    spots = data.get("spots", [])
    hidden = data.get("hidden_gem", "")
    hotels = data.get("hotels", {})
    price_comp = data.get("price_comparison", [])
    transport = data.get("transport", [])
    
    # 음식점/명소 이름 리스트
    food_names = [f["name"] for f in food_items] if food_items else []
    spot_names = spots if spots else []
    
    # 페이지 변형을 위한 시드
    angles = [
        "실제 후기 기반 상세 가이드",
        "가성비 최적화 여행 코스",
        "현지인 추천 숨은 명소 중심",
        "첫 방문자를 위한 완벽 가이드",
        "커플/가족 여행 추천 코스",
        "예산별 여행 계획 (저예산/중급/럭셔리)",
        "사진 찍기 좋은 포토스팟 중심",
        "혼자 떠나는 자유여행 가이드",
        "비수기 여행의 장점과 팁",
        "맛집 투어 코스 추천",
        "액티비티 중심 여행 코스",
        "힐링/휴양 중심 여행 코스",
        "역사와 문화 중심 여행 코스",
        "일몰/일출 명소 완벽 가이드",
    ]
    angle = angles[page_idx % len(angles)]
    
    prompt = f"""발리 {area}의 {cat_info['name']}에 대한 여행 블로그 글을 작성해주세요.

## 작성 조건
- 주제: {area} {cat_info['name']} — {angle}
- 페이지 번호: {page_idx + 1}번째 변형
- 언어: 한국어
- 독자: 20~40대 한국인 자유여행객
- 톤: 친근하지만 정보가 풍부한 블로거 톤

## 반드시 포함할 요소 (네이버 Cue: 최적화)
1. **첫 문단 (100~200자)**: 결론 요약 박스 — "{area}에서 {cat_info['desc']}을(를) 즐기려면 [핵심 결론]. 특히 [조건]이라면 [변수1], [변수2], [변수3]을 함께 고려해야 합니다."
2. **Q&A 형태 소제목**: 사용자가 검색할 법한 질문형 소제목 3개 이상
3. **번호 리스트/불릿 리스트**: 최소 2개 이상
4. **비교 표 (HTML table)**: 가격 비교 또는 옵션 비교 표 1개 이상
5. **구체 수치**: 가격(루피아/원), 시간, 거리 등 구체적 숫자 5개 이상
6. **팁 박스**: 💡 실전 팁 3개
7. **숨은 명소/꿀팁**: 관광객이 잘 모르는 정보 1개

## 참조 데이터 (이 데이터를 기반으로 고유한 글을 작성)
- 지역: {area} — {data.get('description', '')}
- 음식점: {', '.join(food_names[:5]) if food_names else 'N/A'}
- 명소: {', '.join(spot_names[:5]) if spot_names else 'N/A'}
- 숨은 명소: {hidden or 'N/A'}
- 예산형 숙소: {hotels.get('budget', 'N/A')}
- 중급 숙소: {hotels.get('mid', 'N/A')}
- 고급 숙소: {hotels.get('high', 'N/A')}
- 최적 시기: {data.get('best_season', 'N/A')}
- 가격 비교 항목: {json.dumps(price_comp[:3], ensure_ascii=False) if price_comp else 'N/A'}

## 카테고리별 특화 정보
{json.dumps(cat_data[:4], ensure_ascii=False) if cat_data else 'N/A'}

## 출력 형식
순수 HTML 콘텐츠만 출력 (<!DOCTYPE html> 없이, <article> 태그 내부만).
CSS 스타일은 포함하지 마세요 (외부 CSS에서 처리).
다음 구조로 작성:

<div class="content-intro">첫 문단 결론 박스</div>

<h2>❓ [질문형 소제목 1]</h2>
<p>내용...</p>

<h2>📊 [비교/정리 소제목]</h2>
<table class="price-table">...</table>

<h2>💡 실전 팁</h2>
<ul>
<li>팁 1</li>
<li>팁 2</li>
<li>팁 3</li>
</ul>

<h2>💎 숨은 명소</h2>
<p>내용...</p>

<h2>📍 추천 코스</h2>
<ol>
<li>코스 1</li>
<li>코스 2</li>
</ol>

<div class="content-footer">마무리 + 업데이트 날짜 ({CURRENT_YEAR}년 기준)</div>

최소 1500자 이상 작성하세요. 다른 페이지와 동일한 내용이면 안 됩니다.
"""
    return prompt

def generate_html_template(area, category, page_idx, content_html, images):
    """HTML 템플릿에 콘텐츠 삽입"""
    cat_info = CATEGORIES[category]
    data = BALI_DATA.get(area, {})
    
    # SEO 제목 (고유)
    title_seeds = [
        f"{area} {cat_info['name']} 추천 — {CURRENT_YEAR} 최신 가이드 #{page_idx+1}",
        f"{area} {cat_info['name']} 완벽 정리 — 가격·팁·후기",
        f"{area} 여행 {cat_info['name']} — 현지인이 추천하는 진짜 정보",
        f"{area} {cat_info['name']} 베스트 — {CURRENT_YEAR} 실제 후기",
        f"{area} 자유여행 {cat_info['name']} — 놓치면 후회하는 꿀팁",
        f"{area} {cat_info['name']} 가이드 — 10년차 블로거 추천",
        f"{area} {cat_info['name']} 총정리 — 비용·위치·팁 비교",
        f"{area} {cat_info['name']} 탐방기 — 직접 다녀온 솔직 리뷰",
        f"{area} {cat_info['name']} 추천 리스트 — 예산별 BEST",
        f"{area} {cat_info['name']} 숨은 명소 — 현지인만 아는 곳",
        f"{area} {cat_info['name']} 맛있는 코스 — 하루 일정 추천",
        f"{area} {cat_info['name']} 포토스팟 — 인생샷 찍는 법",
        f"{area} {cat_info['name']} 비용 절약 — 가성비 최적화 팁",
        f"{area} {cat_info['name']} 초보 가이드 — 처음 방문자를 위해",
    ]
    title = title_seeds[page_idx % len(title_seeds)]
    
    meta_desc = f"{area} {cat_info['name']} 여행 정보. 가격 비교, 숨은 명소, 실전 팁까지. {CURRENT_YEAR}년 기준 최신 후기."
    
    # 날짜
    base_date = datetime(2026, 4, 1)
    page_date = base_date + timedelta(days=page_idx % 30)
    date_str = page_date.strftime("%Y-%m-%d")
    
    # 이미지 HTML
    images_html = ""
    for i, img in enumerate(images):
        if img.startswith("http"):
            img_src = img
        else:
            img_src = f"../../images/{area}/{category}/{img}"
        alt_text = f"{area} {cat_info['name']} 여행 사진 {i+1}"
        images_html += f'<figure style="margin:20px 0;text-align:center"><img src="{img_src}" alt="{alt_text}" loading="lazy" style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)" /></figure>\n'
    
    # 관련 지역 링크
    other_areas = [a for a in AREAS if a != area]
    random.seed(f"{area}_{category}_{page_idx}")
    related = random.sample(other_areas, min(3, len(other_areas)))
    related_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0">'
    for ra in related:
        rpage = (page_idx + 1) % 14 + 1
        related_html += f'<a href="/{ra}/{category}/{rpage:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{ra} {cat_info["name"]}</a>'
    related_html += '</div>'
    
    # 쿠폰 HTML
    coupon_html = f'''<div style="margin:24px 0;text-align:center">
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰" style="max-width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12)" loading="lazy" />
</a>
<p style="margin-top:10px;font-size:.85em;color:#666">마이리얼트립 할인쿠폰 — 투어/티켓/숙소 최대 30% 할인</p>
</div>'''
    
    # 가격비교 표
    price_comp = data.get("price_comparison", [])
    price_table = ""
    if price_comp:
        price_table = '''<h2>💰 가격 비교 (로컬 vs 투어 vs 호텔)</h2>
<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.9em">
<thead><tr style="background:#FF6B35;color:white">
<th style="padding:10px 8px;text-align:left;border:1px solid #ddd">항목</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">로컬</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">투어</th>
<th style="padding:10px 8px;text-align:center;border:1px solid #ddd">호텔</th>
</tr></thead><tbody>'''
        for i, pc in enumerate(price_comp):
            bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            price_table += f'''<tr style="background:{bg}">
<td style="padding:10px 8px;border:1px solid #ddd;font-weight:600">{pc["item"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd;color:#2e7d32;font-weight:600">{pc["local"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd">{pc["tour"]}</td>
<td style="padding:10px 8px;text-align:center;border:1px solid #ddd">{pc["hotel"]}</td>
</tr>'''
        price_table += '</tbody></table></div>'
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{area}, 발리, 인도네시아, {cat_info['name']}, 여행, 자유여행, 가격비교, {CURRENT_YEAR}">
<link rel="canonical" href="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{SITE_URL}/images/{area}/001.webp">
<meta property="og:url" content="{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html">
<meta property="og:site_name" content="발리 여행 블로그">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "{title}", "description": "{meta_desc}", "image": ["{SITE_URL}/images/{area}/001.webp"], "datePublished": "{date_str}", "dateModified": "{date_str}", "author": {{"@type": "Person", "name": "{AUTHOR}"}}, "publisher": {{"@type": "Organization", "name": "발리 여행 블로그"}}, "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE_URL}/{area}/{category}/{page_idx+1:03d}.html"}}}}</script>
<style>
:root {{ --primary: #FF6B35; --bg: #FAFAFA; --text: #1A1A2E; --text-light: #666; --border: #E0E0E0; --card-bg: #FFFFFF; --shadow: 0 2px 8px rgba(0,0,0,0.08); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
header {{ background: linear-gradient(135deg, #FF6B35, #FF8C61); color: white; padding: 40px 20px; text-align: center; }}
header h1 {{ font-size: 1.8rem; margin-bottom: 10px; }}
header .meta {{ opacity: 0.9; font-size: 0.9rem; }}
.breadcrumb {{ padding: 15px 0; font-size: 0.85rem; color: var(--text-light); }}
.breadcrumb a {{ color: var(--primary); text-decoration: none; }}
article {{ background: var(--card-bg); border-radius: 12px; padding: 30px; box-shadow: var(--shadow); margin: 20px 0; }}
article h2 {{ color: var(--primary); font-size: 1.4rem; margin: 30px 0 15px; padding-bottom: 8px; border-bottom: 2px solid var(--primary); }}
article h3 {{ color: #333; font-size: 1.15rem; margin: 20px 0 10px; }}
article table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
article th, article td {{ padding: 10px 8px; border: 1px solid #ddd; text-align: left; }}
article th {{ background: #FF6B35; color: white; }}
article tr:nth-child(even) {{ background: #f9f9f9; }}
article ul, article ol {{ padding-left: 20px; margin: 16px 0; }}
article li {{ margin-bottom: 8px; line-height: 1.7; }}
.content-intro {{ margin: 0 0 20px; padding: 16px 20px; background: linear-gradient(135deg, #fff7ed, #fff3e0); border-radius: 10px; border: 1px solid #ffe0b2; font-weight: 500; }}
.content-footer {{ margin: 24px 0; padding: 12px; background: #f5f5f5; border-radius: 8px; font-size: 0.9em; color: #666; }}
.tags {{ margin: 20px 0; }}
.tag {{ display: inline-block; background: #F0F0F0; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 3px; color: var(--text-light); }}
footer {{ text-align: center; padding: 30px; color: var(--text-light); font-size: 0.85rem; }}
@media (max-width: 600px) {{ .container {{ padding: 10px; }} article {{ padding: 20px; }} header h1 {{ font-size: 1.4rem; }} table {{ font-size: .8em; }} }}
</style>
</head>
<body>

<div style="background:#f5f5f5;padding:10px 15px;border-bottom:1px solid #e0e0e0;font-size:13px;color:#555;text-align:center;line-height:1.6">
📌 이 글은 <strong>마이리얼트립 파트너스 활동</strong>의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다. 
구매에 추가 비용이 발생하지 않습니다. | 
<a href="{AFFILIATE_URL}" target="_blank" rel="noopener sponsored" style="color:#d84315;font-weight:600">🎫 마이리얼트립 할인쿠폰 받기</a>
</div>

<header>
<h1>{title}</h1>
<div class="meta">{cat_info['icon']} {area} | {cat_info['name']} | 📅 {CURRENT_YEAR}년 기준 | ✍️ {AUTHOR}</div>
</header>

<div class="container">
<nav class="breadcrumb">
<a href="/">🏠 홈</a> &gt; 
<a href="/{area}/">{area}</a> &gt; 
<a href="/{area}/{category}/">{cat_info['name']}</a> &gt; 
<span>{title[:30]}...</span>
</nav>

<article>

{coupon_html}

{images_html}

{content_html}

{price_table}

<h2>🔗 관련 지역 추천</h2>
{related_html}

{coupon_html}

<div class="tags">
<span class="tag">{area}</span>
<span class="tag">발리</span>
<span class="tag">{cat_info['name']}</span>
<span class="tag">자유여행</span>
<span class="tag">가격비교</span>
<span class="tag">{CURRENT_YEAR}</span>
</div>

</article>

<footer>
<p>© {CURRENT_YEAR} 발리 여행 블로그 | {AUTHOR}</p>
<p style="margin-top:8px">이 글은 마이리얼트립 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>
</footer>
</div>
</body>
</html>'''
    return html

def load_generated_content():
    if CONTENT_DB.exists():
        return json.loads(CONTENT_DB.read_text())
    return {}

def save_generated_content(content):
    CONTENT_DB.write_text(json.dumps(content, ensure_ascii=False, indent=2))

def main():
    """메인 실행 — AI에게 콘텐츠 생성 요청"""
    print("=" * 60)
    print("✍️ AI 기반 고유 콘텐츠 생성기")
    print("=" * 60)
    
    content_db = load_generated_content()
    images = load_image_mapping()
    
    total_generated = 0
    total_skipped = 0
    
    for area in AREAS:
        data = BALI_DATA.get(area, {})
        print(f"\n📍 {area}")
        
        for category in CATEGORIES:
            cat_info = CATEGORIES[category]
            print(f"  {cat_info['icon']} {category}")
            
            for page_idx in range(14):
                key = f"{area}_{category}_{page_idx:03d}"
                
                # 이미 생성되었는지 확인
                if key in content_db:
                    total_skipped += 1
                    continue
                
                # 프롬프트 생성
                prompt = generate_content_prompt(area, category, page_idx, data)
                
                # 콘텐츠 DB에 프롬프트 저장 (AI 생성은 별도 처리)
                content_db[key] = {
                    "prompt": prompt,
                    "area": area,
                    "category": category,
                    "page_idx": page_idx,
                    "status": "pending",
                    "created": datetime.now().isoformat(),
                }
                total_generated += 1
            
            save_generated_content(content_db)
    
    print(f"\n{'='*60}")
    print(f"✅ 프롬프트 생성 완료!")
    print(f"   신규: {total_generated}")
    print(f"   기존: {total_skipped}")
    print(f"   총: {total_generated + total_skipped}")

if __name__ == "__main__":
    main()
