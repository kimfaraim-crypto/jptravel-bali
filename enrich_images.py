#!/usr/bin/env python3
"""
924개 HTML에 이미지를 풍부하게 추가
각 아티클에 사용 가능한 이미지를 최대한 활용
"""

import os, re, random
from pathlib import Path

BASE = Path(__file__).parent / "output"
HTML_DIR = BASE / "html" / "bali"
IMG_DIR = BASE / "images"

def get_available_images(city, category):
    """사용 가능한 이미지 목록 반환"""
    img_path = IMG_DIR / city / category
    if not img_path.exists():
        return []
    files = sorted([f for f in img_path.iterdir() if f.suffix == '.webp'])
    return [f.name for f in files]

def get_used_images(content, city, category):
    """현재 HTML에서 사용 중인 이미지 목록"""
    pattern = f'../../images/{city}/{category}/([^"]+\\.webp)'
    return set(re.findall(pattern, content))

def get_unused_images(city, category, used):
    """사용하지 않는 이미지 목록"""
    available = get_available_images(city, category)
    return [img for img in available if img not in used]

def make_image_tag(city, category, filename, caption=""):
    """이미지 태그 생성"""
    src = f"../../images/{city}/{category}/{filename}"
    alt = caption if caption else f"{city} {category} {filename.replace('.webp','').replace('_',' ')}"
    return f'''<figure style="margin:20px 0;text-align:center">
<img src="{src}" alt="{alt}" style="max-width:100%;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)" loading="lazy">
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">{alt}</figcaption>
</figure>'''

def add_images_to_html(filepath):
    """HTML 파일에 이미지 추가"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 도시/카테고리 추출
    parts = filepath.parts
    city = None
    category = None
    for part in parts:
        if part in ['꾸따','우붓','스미냑','사누르','누사두아','울루와뚜','짠디다사','로비나','킨타마니','타나롯','베두굴','타바난']:
            city = part
        if part in ['food','beach','culture','nature','shopping','transport']:
            category = part
    
    if not city or not category:
        return False
    
    # 사용 가능한 이미지 확인
    used = get_used_images(content, city, category)
    unused = get_unused_images(city, category, used)
    
    if len(unused) < 3:
        return False
    
    # 랜덤 시드 설정
    rng = random.Random(hash(f"{city}_{category}_{filepath.stem}"))
    rng.shuffle(unused)
    
    # H2 태그 뒤에 이미지 추가
    h2_pattern = r'(</h2>)'
    added = 0
    max_add = min(8, len(unused))  # 최대 8개 추가
    
    def add_after_h2(match):
        nonlocal added
        if added >= max_add:
            return match.group(0)
        img_file = unused[added]
        added += 1
        caption = f"{city} {category}"
        return match.group(0) + '\n' + make_image_tag(city, category, img_file, caption)
    
    content = re.sub(h2_pattern, add_after_h2, content, count=max_add)
    
    # figure 태그가 적은 경우 콘텐츠 중간에도 추가
    figure_count = content.count('<figure')
    if figure_count < 8 and added < max_add:
        # </p> 태그 뒤에 이미지 추가 (랜덤 위치)
        p_tags = list(re.finditer(r'</p>', content))
        if len(p_tags) > 5:
            # 3~5개 위치에 이미지 추가
            insert_positions = rng.sample(p_tags[2:-2], min(3, len(p_tags)-4, max_add-added))
            insert_positions.sort(key=lambda m: m.start(), reverse=True)
            
            for pos in insert_positions:
                if added >= max_add:
                    break
                img_file = unused[added % len(unused)]
                added += 1
                img_tag = make_image_tag(city, category, img_file, f"{city} {category}")
                content = content[:pos.end()] + '\n' + img_tag + content[pos.end():]
    
    if added > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("=== 이미지 풍부화 시작 ===\n")
    
    html_files = list(HTML_DIR.rglob("*.html"))
    print(f"총 HTML 파일: {len(html_files)}개\n")
    
    enriched = 0
    total_added = 0
    for i, filepath in enumerate(html_files):
        before_figures = filepath.read_text(encoding='utf-8').count('<figure')
        if add_images_to_html(filepath):
            after_figures = filepath.read_text(encoding='utf-8').count('<figure')
            added = after_figures - before_figures
            total_added += added
            enriched += 1
        if (i + 1) % 100 == 0:
            print(f"  진행: {i+1}/{len(html_files)} 처리 완료...")
    
    print(f"\n✅ 이미지 풍부화 완료")
    print(f"   - 처리된 파일: {enriched}/{len(html_files)}")
    print(f"   - 추가된 이미지 태그: {total_added}개")
    
    # 검증
    print("\n=== 검증 ===")
    sample_files = [
        HTML_DIR / "꾸따" / "food" / "001.html",
        HTML_DIR / "우붓" / "food" / "001.html",
        HTML_DIR / "스미냑" / "beach" / "001.html",
    ]
    for f in sample_files:
        if f.exists():
            count = f.read_text(encoding='utf-8').count('<figure')
            print(f"  {f.parent.parent.name}/{f.parent.name}/{f.name}: {count}개 figure")

if __name__ == "__main__":
    main()
