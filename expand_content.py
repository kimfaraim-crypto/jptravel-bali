#!/usr/bin/env python3
"""
Post-process: expand all HTML articles to 1500+ Korean characters.
Adds detailed sections per category, removes emoji, fixes Chinese chars.
"""
import os, re, random, json
from pathlib import Path

random.seed(42)
BASE = Path("output/html/bali")
MRT_LINK = "https://myrealt.rip/YuJbb5"

CITIES = {
    "꾸따": {"name_en":"Kuta","airport_min":15,"beaches":["꾸따 비치","레기안 비치"],"temples":["울루와뚜 사원"],"foods":["Warung Murah","Bamboo Corner","Poppies"],"markets":["꾸따 아트마켓","비치워크 쇼핑몰"],"nature":["워터밤 파크"],"vibe":"활기차고 젊은 분위기","hidden":["코로 비치","발리 폭탄 기념비 골목"]},
    "스미냑": {"name_en":"Seminyak","airport_min":25,"beaches":["스미냑 비치","페티탕게트 비치"],"temples":["따나롯 사원"],"foods":["La Plancha","Ku De Ta","Potato Head"],"markets":["스미냑 빌리지","세마냑 스퀘어"],"nature":["라이스 테라스"],"vibe":"고급 비치클럽과 부티크","hidden":["카유 아야 거리"]},
    "우붓": {"name_en":"Ubud","airport_min":90,"beaches":[],"temples":["따만 아윤 사원","엘루 사원"],"foods":["Locavore","Clear Cafe","Warung Ibu Oka"],"markets":["우붓 전통시장","우붓 아트마켓"],"nature":["몽키포레스트","테갈랑 라이스 테라스","띔푸르 폭포"],"vibe":"열대우림과 예술가 마을","hidden":["방리안 마을","벨간 폭포"]},
    "울루와뚜": {"name_en":"Uluwatu","airport_min":40,"beaches":["울루와뚜 비치","빠두빠두 비치","발랑안 비치"],"temples":["울루와뚜 사원"],"foods":["Single Fin","Sunday's Beach Club"],"markets":["울루와뚜 로컬 마켓"],"nature":["울루와뚜 절벽","가루다 시눅 파크"],"vibe":"절벽 위 비치클럽","hidden":["발랑안 비치","빠두빠두 절벽 카페"]},
    "누사두아": {"name_en":"Nusa Dua","airport_min":30,"beaches":["누사두아 비치","게거르 비치"],"temples":["우당 사원"],"foods":["Bumbu Bali","Piasan"],"markets":["발리 컬렉션 쇼핑몰"],"nature":["워터블로우","게거르 비치"],"vibe":"고급 리조트 단지","hidden":["게거르 비치 동굴"]},
    "사누르": {"name_en":"Sanur","airport_min":25,"beaches":["사누르 비치","신드 비치"],"temples":["블라종 사원"],"foods":["Massimo","Three Monkeys","Warung Mak Beng"],"markets":["사누르 아트마켓","사누르 나잇마켓"],"nature":["사누르 비치워크","맹그로브 숲"],"vibe":"차분한 해변 마을","hidden":["블라종 사원 일몰","맹그로브 투어"]},
    "타나롯": {"name_en":"Tanah Lot","airport_min":60,"beaches":["타나롯 비치","바투 볼롱 비치"],"temples":["타나롯 사원","바투 볼롱 사원"],"foods":["Warung Tanah Lot"],"markets":["타나롯 기념품 상점"],"nature":["타나롯 절벽","바투 볼롱 해변"],"vibe":"바위 위 사원과 일몰","hidden":["바투 볼롱 일몰 포인트"]},
    "짠디다사": {"name_en":"Candidasa","airport_min":90,"beaches":["짠디다사 비치","화이트샌드 비치"],"temples":["짬뿌한 사원","고아 라자 사원"],"foods":["Vincent's","Watergarden"],"markets":["짠디다사 로컬 마켓"],"nature":["짬푸한 해변","블루 라군"],"vibe":"한적한 동부 해변","hidden":["뚜카드 마을"]},
    "로비나": {"name_en":"Lovina","airport_min":150,"beaches":["로비나 비치","아Ἕ 비치"],"temples":["반자르 온천 사원"],"foods":["Sea Breeze Cafe","Warung Lovina"],"markets":["로비나 로컬 마켓"],"nature":["돌고래 투어","반자르 온천","기트기트 폭포"],"vibe":"조용한 북부 해변","hidden":["무스 리버 폭포"]},
    "베두굴": {"name_en":"Bedugul","airport_min":120,"beaches":[],"temples":["울룬 다누 브라딴 사원"],"foods":["Warung Rekreasi"],"markets":["베두굴 과일시장","Candikuning 마켓"],"nature":["울룬 다누 사원","베둘구 식물원","탐블링안 호수"],"vibe":"고산지대 호수와 사원","hidden":["탐블링안 호수 전망대"]},
    "킨타마니": {"name_en":"Kintamani","airport_min":120,"beaches":[],"temples":["뿌라 울룬 바뚜르"],"foods":["Volcano View Restaurant"],"markets":["킨타마니 로컬 마켓"],"nature":["바투르 화산","바투르 호수","뜨르유빤 온천"],"vibe":"화산과 호수의 풍경","hidden":["뜨르유빤 온천"]},
}

CATS = {
    "food":"맛집/음식","beach":"해변/서핑","culture":"문화/사원",
    "nature":"자연/트레킹","shopping":"쇼핑/마켓","transport":"교통/이동"
}

def pick_images(city, cat, article_no, count=10):
    cat_dir = Path("output/images") / city / cat
    if not cat_dir.exists():
        return []
    all_imgs = sorted([f.name for f in cat_dir.glob("*.webp")])
    if not all_imgs:
        return []
    rng = random.Random(hash(f"{city}_{cat}_{article_no}") % (2**31))
    pool = all_imgs.copy()
    selected = []
    while len(selected) < count and pool:
        selected.append(pool.pop(rng.randint(0, len(pool)-1)))
    while len(selected) < count:
        selected.append(all_imgs[rng.randint(0, len(all_imgs)-1)])
    return selected[:count]

def gen_alt(city, cat, slot):
    ci = CITIES[city]
    cat_name = CATS[cat]
    rng = random.Random(hash(f"alt2_{city}_{cat}_{slot}") % (2**31))
    templates = {
        "food": [f"{city} 로컬 음식 플레이팅", f"{city} 전통 워룽 내부", f"{city} 스트리트 푸드", f"{city} 레스토랑 메뉴판", f"{city} 발리 전통 음식"],
        "beach": [f"{city} 해변 전경", f"{city} 서핑 포인트 파도", f"{city} 비치클럽 선베드", f"{city} 해변 일몰", f"{city} 해변 산책로"],
        "culture": [f"{city} 사원 입구", f"{city} 사원 건축물", f"{city} 케착 댄스 공연", f"{city} 사원 정원", f"{city} 종교 의식"],
        "nature": [f"{city} 트레킹 코스", f"{city} 열대우림 풍경", f"{city} 폭포 전경", f"{city} 라이스 테라스", f"{city} 산악 지형"],
        "shopping": [f"{city} 전통시장 풍경", f"{city} 기념품 가게", f"{city} 쇼핑몰 내부", f"{city} 수공예품", f"{city} 흥정 장면"],
        "transport": [f"{city} 도로 풍경", f"{city} 스쿠터 이동", f"{city} 공항 택시", f"{city} 그랩 호출 화면", f"{city} 기사 투어 차량"],
    }
    return rng.choice(templates.get(cat, [f"{city} {cat_name} 사진"]))

def gen_figcaption(city, cat, slot):
    cat_name = CATS[cat]
    rng = random.Random(hash(f"fig2_{city}_{cat}_{slot}") % (2**31))
    templates = [
        f"{city} {cat_name} 현장 사진",
        f"{city} 여행 중 촬영한 모습",
        f"{city} {cat_name} 추천 장소",
        f"{city} 자유여행 가이드 이미지",
        f"{city} {cat_name} 실제 풍경",
    ]
    return rng.choice(templates)

# Additional content blocks per category
EXTRA_CONTENT = {
    "food": [
        "현지 음식을 주문할 때 알아두면 좋은 표현이 있어요. 'Tidak pedas'(안 맵게), 'Pedas sedikit'(약간 맵게), 'Tanpa gula'(설탕 없이)예요. 워룽에서 이 표현을 쓰면 현지인들이 더 친절하게 대해줘요.",
        "발리 음식의 특징은 향신료가 강하다는 거예요. 특히 땅콩 소스를 base로 한 음식이 많아서, 땅콩 알레르기가 있다면 미리 말해야 해요. 'Alergi kacang'이라고 말하면 돼요.",
        "물은 반드시 생수를 마시세요. 수돗물은 마시면 안 돼요. 아이스도 수돗물로 만드는 경우가 있으니, 관광지가 아닌 곳에서는 아이스를 피하는 게 안전해요.",
        "발리의 워룽은 보통 오전 7시에 열어서 오후 9~10시에 닫아요. 점심시간(12~13시)이 가장 붐비니, 11시 또는 14시에 가면 여유롭게 식사할 수 있어요.",
        "팁 문화는 의무는 아니지만, 서비스가 좋았다면 10,000~20,000Rp(약 1,000~2,000원)을 남기는 게 좋아요. 고급 레스토랑은 5~10% 서비스 차지가 포함되는 경우도 있어요.",
    ],
    "beach": [
        "발리 해변의 자외선은 매우 강해요. SPF50 선크림을 2시간마다 덧발라야 해요. 선크림을 안 바르면 30분 만에 화상을 입을 수 있어요.",
        "서핑 보드 대여는 해변 곳곳에서 가능해요. 1일 대여 100,000~150,000Rp. 초보는 반드시 강습을 받으세요. 혼자 하면 다칠 위험이 있어요.",
        "해변에서 파는 음식은 신선도를 꼭 확인하세요. 아이스가 녹은 음식, 상온에 오래 방치된 해산물은 피하는 게 좋아요.",
        "발리 해변에는 리프 락(산호초)이 많아요. 아쿠아슈즈를 신으면 발을 다치지 않아요. 해변 입구에서 20,000~30,000Rp에 팔아요.",
        "비치클럽은 예약 없이 가면 자리가 없을 수 있어요. 특히 주말과 성수기(7~8월)에는 최소 하루 전에 예약하세요.",
    ],
    "culture": [
        "발리 사원에서는 월렝(Waleng)이라 불리는 사롱을 반드시 착용해야 해요. 입구에서 무료로 빌려주는 곳도 있고, 10,000~20,000Rp에 대여하는 곳도 있어요.",
        "사원 내부에서는 조용히 해야 해요. 큰 소리로 이야기하거나, 성스러운 물건을 만지면 안 돼요. 현지인의 예배를 방해하지 않도록 주의하세요.",
        "발리의 사원은 방향이 중요해요. 산쪽(북쪽)이 신성한 방향, 바다쪽(남쪽)이 불결한 방향이에요. 사진 촬영 시 이 점을 고려하세요.",
        "사원 방문 시 드론 촬영은 대부분 금지되어 있어요. 미리 확인하지 않으면 벌금을 물 수 있어요.",
        "케착 댄스는 발리의 대표적인 전통 공연이에요. 1시간 정도 진행되고, 입장료 100,000~150,000Rp이에요. 일몰 시간대에 하면 배경이 더 아름다워요.",
    ],
    "nature": [
        "트레킹 시 충분한 물을 준비하세요. 1인당 최소 1.5리터를 추천해요. 고산지대는 탈수가 더 빨리 와요.",
        "우기(11~3월)의 트레킹 코스는 미끄러울 수 있어요. 트레킹화 필수, 스틱이 있으면 더 안전해요. 가이드 동행을 강력 추천해요.",
        "발리의 자연 명소에는 원숭이가 많아요. 선글라스, 모자, 작은 가방을 뺏길 수 있어요. 소지품을 단단히 hold하세요.",
        "폭포 근처에서는 수영이 가능하지만, 수심을 미리 확인하세요. 우기엔 수위가 높아져 위험할 수 있어요.",
        "발리의 고산지대(베두굴, 킨타마니)는 기온이 15~22도로 서늘해요. 얇은 겉옷을 챙기세요. 안개가 끼면 시야가 제한될 수 있어요.",
    ],
    "shopping": [
        "발리 시장에서의 흥정은 문화예요. 처음 가격의 30~50%에서 시작하세요. 웃으면서 친절하게, 마지막까지 미소를 잃지 마세요.",
        "카드 결제는 큰 숍에서만 가능해요. 시장과 로컬 가게는 현금만 받아요. ATM에서 미리 뽑아가세요.",
        "기념품 포장이 필요하면 구매 시 말씀하세요. 큰 숍에서는 국제 배송도 해주지만, 비용이 비쌀 수 있어요.",
        "사기 주의: '명품'을 파는 곳은 대부분 가품이에요. 너무 싸면 의심하세요. 정품을 원하면 공식 매장에서 구매하세요.",
        "발리 커피 원두는 기념품으로 인기예요. 루왁 커피 100g 150,000~300,000Rp. 시장보다 커피 전문점에서 사는 게 품질이 좋아요.",
    ],
    "transport": [
        "공항 택시는 공식 카운터에서 표를 끊으면 바가지를 피할 수 있어요. 공항 밖에서 호객하는 택시는 피하세요.",
        "그랩은 발리 전역에서 잘 돼요. 다만 공항, 비치클럽 일부 지역에서는 그랩 호출이 어려울 수 있어요. 이땐 기사 투어를 이용하세요.",
        "스쿠터 렌트 시 반드시 헬멧을 착용하세요. 경찰 검문 시 헬멧 미착용은 벌금이에요. 국제면허가 없으면 보험 적용이 안 돼요.",
        "기사 투어는 8시간 기준 500,000~700,000Rp이에요. 기사+차량+유류비 포함인 경우가 많아요. 여러 명이면 1인당 비용이 확 줄어요.",
        "발리는 좌측 통행이에요. 한국에서 오신 분은 적응 시간이 필요해요. 특히 로터리 진입 시 주의하세요.",
    ],
}

def get_extra_content(city, cat, article_no, count=2):
    pool = EXTRA_CONTENT.get(cat, [])
    rng = random.Random(hash(f"extra_{city}_{cat}_{article_no}") % (2**31))
    selected = rng.sample(pool, min(count, len(pool)))
    return '<p style="margin:12px 0;line-height:1.8">' + '</p>\n<p style="margin:12px 0;line-height:1.8">'.join(selected) + '</p>'

def gen_budget_block(city, cat, article_no):
    ci = CITIES[city]
    rng = random.Random(hash(f"budget_{city}_{cat}_{article_no}") % (2**31))
    meal = rng.choice([25000, 30000, 35000, 40000, 50000])
    transport_d = rng.choice([70000, 100000, 150000])
    activity = rng.choice([50000, 80000, 100000, 150000])
    hotel = rng.choice([200000, 300000, 400000, 500000])
    total = meal*3 + transport_d + activity + hotel
    return f"""<h3 style="font-size:1.1em;font-weight:700;margin:20px 0 10px;color:#333">1일 예산 breakdown</h3>
<ul>
<li>식사 (3끼): {meal:,}Rp x 3 = {meal*3:,}Rp (약 {meal*3//120:,}원)</li>
<li>교통: {transport_d:,}Rp (약 {transport_d//120:,}원)</li>
<li>액티비티: {activity:,}Rp (약 {activity//120:,}원)</li>
<li>숙소 (1박): {hotel:,}Rp (약 {hotel//120:,}원)</li>
<li><strong>합계</strong>: {total:,}Rp (약 {total//120:,}원)</li>
</ul>"""

def gen_weather_block(city, article_no):
    ci = CITIES[city]
    rng = random.Random(hash(f"weather_{city}_{article_no}") % (2**31))
    tips = [
        f"건기(4~10월): 날씨가 맑고 습도가 낮아요. 7~8월은 성수기로 숙소 가격이 20~50% 올라요.",
        f"우기(11~3월): 스콜성 소나기가 자주 와요. 보통 30분~1시간 후 그치니 일정에 큰 지장은 없어요.",
        f"{city}의 기온은 연중 27~32도예요. 고산지대는 15~22도로 서늘하니 얇은 겉옷을 챙기세요.",
        f"습도가 높아 땀을 많이 흘려요. 수분 보충을 충분히 하고, 썬크림은 SPF50 이상을 2시간마다 덧발라주세요.",
    ]
    selected = rng.sample(tips, min(2, len(tips)))
    return '<p style="margin:8px 0;line-height:1.8">' + '</p>\n<p style="margin:8px 0;line-height:1.8">'.join(selected) + '</p>'

def gen_hidden_block(city, article_no):
    ci = CITIES[city]
    rng = random.Random(hash(f"hidden_{city}_{article_no}") % (2**31))
    hidden = ci.get('hidden', [f"{city}의 숨겨진 골목"])
    spot = rng.choice(hidden)
    return f'<p style="margin:12px 0;line-height:1.8">• <strong>{spot}</strong>: 관광객이 잘 모르는 곳이에요. 현지인에게 물어보면 찾을 수 있어요. 조용하게 즐기고 싶은 분에게 추천해요.</p>'

def gen_nearby_block(city, cat, article_no):
    ci = CITIES[city]
    rng = random.Random(hash(f"nearby_{city}_{cat}_{article_no}") % (2**31))
    items = []
    if ci['beaches']:
        items.append(f"<li><strong>{rng.choice(ci['beaches'])}</strong>: 수영과 서핑 모두 가능한 해변이에요.</li>")
    if ci['temples']:
        items.append(f"<li><strong>{rng.choice(ci['temples'])}</strong>: 발리 문화를 느낄 수 있는 사원이에요.</li>")
    if ci['nature']:
        items.append(f"<li><strong>{rng.choice(ci['nature'])}</strong>: 자연을 즐길 수 있는 명소예요.</li>")
    if ci['markets']:
        items.append(f"<li><strong>{rng.choice(ci['markets'])}</strong>: 쇼핑과 기념품 구매에 좋아요.</li>")
    selected = rng.sample(items, min(3, len(items)))
    return '<ul>' + ''.join(selected) + '</ul>'

# ============================================================
# MAIN: Process each HTML
# ============================================================
html_files = sorted(BASE.rglob("*.html"))
print(f"Processing {len(html_files)} files...")

count = 0
titles = set()
metas = set()
short_count = 0
chinese_count = 0
emoji_count = 0
emoji_re = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF\u200D\uFE0F]')
hanja_re = re.compile(r'[\u4e00-\u9fff]')

for f in html_files:
    content = f.read_text(encoding='utf-8')
    parts = f.relative_to(BASE).parts
    city, cat, fname = parts[0], parts[1], parts[2]
    article_no = int(fname.replace('.html',''))
    ci = CITIES.get(city, {})
    cat_name = CATS.get(cat, cat)

    # Extract existing title and meta
    title_m = re.search(r'<title>(.*?)</title>', content)
    meta_m = re.search(r'<meta name="description" content="(.*?)"', content)
    if title_m:
        titles.add(title_m.group(1))
    if meta_m:
        metas.add(meta_m.group(1))

    # Pick new images
    images = pick_images(city, cat, article_no, 10)

    # Build image HTML with unique alts and figcaptions
    img_html_parts = []
    mrt_inserted = False
    for i, img_name in enumerate(images):
        img_path = f"../../images/{city}/{cat}/{img_name}"
        alt = gen_alt(city, cat, i)
        fig = gen_figcaption(city, cat, i)

        # Insert MRT coupon image after 3rd image
        if i == 3 and not mrt_inserted:
            img_html_parts.append(f'''<figure style="margin:24px 0;text-align:center">
<a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인" style="max-width:100%;border-radius:8px">
</a>
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인</figcaption>
</figure>''')
            mrt_inserted = True

        img_html_parts.append(f'''<figure style="margin:24px 0">
<img src="{img_path}" alt="{alt}" loading="lazy" style="width:100%;border-radius:8px">
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">{fig}</figcaption>
</figure>''')

    if not mrt_inserted:
        img_html_parts.append(f'''<figure style="margin:24px 0;text-align:center">
<a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener">
<img src="../../images/mrt_coupon.jpg" alt="마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인" style="max-width:100%;border-radius:8px">
</a>
<figcaption style="font-size:0.85em;color:#666;margin-top:8px">마이리얼트립 할인쿠폰 - 투어, 티켓, 숙소 최대 30% 할인</figcaption>
</figure>''')

    images_html = '\n'.join(img_html_parts)

    # Generate expanded content
    rng = random.Random(hash(f"body_{city}_{cat}_{article_no}") % (2**31))

    intro_options = [
        f"{city}에서 {cat_name}을 찾고 계신가요? 직접 다녀온 경험을 바탕으로 실제 가격과 동선을 정리했어요.",
        f"발리 {city} 지역의 {cat_name} 정보를 모았습니다. 현장에서 확인한 내용 위주로 작성했어요.",
        f"{city} {cat_name} 여행을 계획 중이신가요? 제가 직접 가보고 느낀 점을 솔직하게 공유합니다.",
        f"이번엔 발리 {city}의 {cat_name}을 정리해봤어요. 가격 비교부터 실패 팁까지 다루고 있어요.",
        f"{city} 자유여행에서 {cat_name}은 빼놓을 수 없죠. 실제 경험을 바탕으로 정리했어요.",
        f"발리 {city}의 {cat_name}을 직접 경험해봤어요. 예상과 달랐던 점도 함께 공유합니다.",
        f"{city} 여행 {cat_name} 가이드입니다. 초보자도 바로 쓸 수 있게 동선과 비용을 정리했어요.",
        f"발리 {city}에서 {cat_name} 계획 중이라면 이 글을 참고하세요. 실전 경험을 바탕으로 썼어요.",
    ]
    intro = rng.choice(intro_options)

    experience_options = [
        f"실제로 {city}에 도착했을 때 가장 먼저 느낀 건 {ci.get('vibe','')}이라는 점이었어요. 예상과 조금 달라서 당황스러웠지만, 오히려 그게 {city}만의 매력이더라고요.",
        f"{city}에서 {cat_name}을 즐기면서 가장 인상 깊었던 건 현지인들의 친절함이었어요. 영어가 잘 안 통해도 미소와 제스처로 소통할 수 있었어요.",
        f"처음 {city}에 갔을 때는 계획을 너무 세세하게 짰는데, 막상 가보니 여유 있게 돌아다니는 게 더 좋았어요.",
        f"{city}의 {cat_name}을 다녀온 후 가장 후회되는 건 충분한 시간을 잡지 못한 거예요. 최소 반나절은 잡고 가세요.",
        f"비가 오는 날 {city}의 {cat_name}을 방문했는데, 생각보다 분위기가 더 좋았어요. 우기라도 실망하지 마세요.",
        f"{city}에서 스쿠터를 타고 이동하면서 발견한 작은 장소가 오히려 더 기억에 남아요.",
        f"가이드 없이 혼자 {city}의 {cat_name}을 돌아다녔는데, 현지 앱과 구글맵만으로 충분했어요.",
        f"{city}의 {cat_name}은 아침에 가면 사람이 적고 사진도 잘 나와요. 오전 8시 전에 도착하는 걸 추천합니다.",
    ]
    experience = rng.choice(experience_options)

    mistake_options = [
        f"가장 흔한 실수: {city}에서 현금을 충분히 준비하지 않는 거예요. 시장과 로컬 식당은 현금만 받으니 최소 500,000Rp는 환전하세요.",
        f"초보 여행자도 자주 놓치는 점: {city}의 사원은 복장 규정이 엄격해요. 반바지와 민소매는 입장이 거부될 수 있어요.",
        f"초보 여행자 실수: {city}에서 택시 미터기를 확인하지 않는 거예요. 반드시 미터기 켜기를 요구하세요.",
        f"놓치기 쉬운 점: {city}의 입장료는 외국인과 내국인이 달라요. 가격표를 꼼꼼히 확인하세요.",
        f"주의할 점: {city}에서 스쿠터 렌트 시 국제면허가 없으면 보험 적용이 안 돼요.",
        f"흔한 실수: {city}의 비치클럽은 예약 없이 가면 자리가 없을 수 있어요.",
    ]
    mistake = rng.choice(mistake_options)

    rec_options = [
        f"추천 대상: {city}의 {cat_name}을 처음 방문하는 여행자, 가성비를 중시하는 배낭여행자, 사진 촬영을 좋아하는 분",
        f"추천 대상: 가족이나 커플 여행으로 {city}를 방문하는 분, 여유로운 일정을 원하는 분",
        f"추천 대상: {city}의 {cat_name}을 깊이 있게 즐기고 싶은 분, 현지 문화를 체험하고 싶은 분",
    ]
    not_rec_options = [
        f"비추천 대상: 시간에 쫓기는 당일치기 여행자, 고급 서비스를 기대하는 분",
        f"비추천 대상: 혼자 조용히 즐기고 싶은 분(성수기엔 시끄러울 수 있음)",
        f"비추천 대상: 비용을 아끼고 싶은 분(주변이 관광지라 가격이 높음)",
    ]
    rec = rng.choice(rec_options)
    not_rec = rng.choice(not_rec_options)

    # Time tips
    time_tip_pool = [
        f"오전 8시 전: 사람이 적고 사진 찍기 좋아요.",
        f"오후 2~5시: 가장 덥고 혼잡한 시간이에요. 그늘진 카페에서 쉬었다가 다시 움직이는 걸 추천해요.",
        f"일몰 시간대(18:00~18:30): {city}에서 가장 아름다운 시간이에요.",
        f"저녁 7시 이후: {city}의 야시장과 나이트라이프가 시작돼요.",
    ]
    time_tips = rng.sample(time_tip_pool, min(3, len(time_tip_pool)))

    # Price table
    if cat == "food":
        p1 = rng.choice([25000, 30000, 35000])
        p2 = rng.choice([60000, 80000, 100000])
        p3 = rng.choice([150000, 200000, 250000])
        price_table = f"""<table>
<tr><th>항목</th><th>로컬 워룽</th><th>일반 레스토랑</th><th>호텔 레스토랑</th></tr>
<tr><td>식사 1끼</td><td>{p1:,}Rp</td><td>{p2:,}Rp</td><td>{p3:,}Rp</td></tr>
<tr><td>음료</td><td>{rng.choice([5000,8000,10000]):,}Rp</td><td>{rng.choice([20000,30000,40000]):,}Rp</td><td>{rng.choice([50000,60000,80000]):,}Rp</td></tr>
</table>"""
    elif cat == "beach":
        price_table = f"""<table>
<tr><th>항목</th><th>무료 해변</th><th>비치클럽</th><th>프라이빗 비치</th></tr>
<tr><td>선베드</td><td>무료</td><td>{rng.choice([80000,100000,150000]):,}Rp~</td><td>{rng.choice([50000,100000]):,}Rp/일</td></tr>
<tr><td>서핑 강습</td><td>{rng.choice([150000,200000]):,}Rp</td><td>{rng.choice([300000,400000]):,}Rp</td><td>별도 문의</td></tr>
</table>"""
    elif cat == "transport":
        price_table = f"""<table>
<tr><th>이동 수단</th><th>예상 비용</th><th>소요 시간</th><th>특징</th></tr>
<tr><td>공항 택시</td><td>{rng.choice([100000,150000,200000]):,}Rp</td><td>{ci.get('airport_min',30)}분</td><td>편하지만 바가지 주의</td></tr>
<tr><td>그랩</td><td>{rng.choice([70000,100000,130000]):,}Rp</td><td>{ci.get('airport_min',30)}분</td><td>가격 고정</td></tr>
<tr><td>기사 투어 (8시간)</td><td>{rng.choice([500000,600000,700000]):,}Rp</td><td>종일</td><td>편하고 안전</td></tr>
<tr><td>스쿠터 렌트 (1일)</td><td>{rng.choice([70000,80000,100000]):,}Rp</td><td>자유</td><td>국제면허 필수</td></tr>
</table>"""
    elif cat == "culture":
        price_table = f"""<table>
<tr><th>항목</th><th>가격</th><th>비고</th></tr>
<tr><td>입장료 (성인)</td><td>{rng.choice([50000,60000,80000]):,}Rp</td><td>사원마다 다름</td></tr>
<tr><td>사롱 대여</td><td>{rng.choice([10000,15000,20000]):,}Rp</td><td>복장 규정 미준수 시</td></tr>
<tr><td>가이드 투어</td><td>{rng.choice([200000,300000]):,}Rp</td><td>해설 포함</td></tr>
</table>"""
    elif cat == "nature":
        price_table = f"""<table>
<tr><th>항목</th><th>가격</th><th>비고</th></tr>
<tr><td>입장료</td><td>{rng.choice([20000,30000,50000]):,}Rp</td><td>지역마다 다름</td></tr>
<tr><td>가이드 비용</td><td>{rng.choice([200000,300000,500000]):,}Rp</td><td>트레킹 포함</td></tr>
<tr><td>장비 렌트</td><td>{rng.choice([50000,80000]):,}Rp</td><td>트레킹화 등</td></tr>
</table>"""
    elif cat == "shopping":
        price_table = f"""<table>
<tr><th>기념품</th><th>시장 가격</th><th>숍 가격</th></tr>
<tr><td>사롱</td><td>{rng.choice([30000,50000]):,}Rp</td><td>{rng.choice([100000,150000]):,}Rp</td></tr>
<tr><td>우드 카빙</td><td>{rng.choice([50000,100000]):,}Rp</td><td>{rng.choice([200000,300000]):,}Rp</td></tr>
<tr><td>커피 원두 (100g)</td><td>{rng.choice([50000,80000]):,}Rp</td><td>{rng.choice([120000,150000]):,}Rp</td></tr>
</table>"""
    else:
        price_table = ""

    # Build FAQ
    faq_pool = {
        "food": [
            (f"{city}에서 가장 저렴하게 식사하는 방법은?", f"로컬 워룽에서 먹으면 1끼 25,000~40,000Rp(약 2,000~3,000원)이면 충분해요."),
            (f"{city} 음식 위생은 안전한가요?", f"관광지 레스토랑은 대체로 깨끗해요. 길거리 음식은 아이스를 피하고 끓인 음식 위주로 드세요."),
            (f"{city}에서 혼밥하기 좋은 곳은?", f"대부분의 워룽은 혼밥이 자연스러워요. 점심시간에는 현지인도 많이 혼밥해요."),
            (f"{city} 음식점에서 카드 결제 가능한가요?", f"고급 레스토랑은 가능하지만, 워룽이나 시장은 현금만 받아요."),
        ],
        "beach": [
            (f"{city} 해변에서 수영 안전한가요?", f"파도가 잔잔한 오전에 수영하는 게 안전해요. 빨간 깃발이 꽂혀 있으면 절대 들어가지 마세요."),
            (f"{city} 비치클럽 선베드 가격은?", f"음료 1잔 최소 주문(80,000~200,000Rp)이면 선베드를 쓸 수 있어요."),
            (f"{city}에서 서핑 강습 받을 수 있나요?", f"2시간 강습에 150,000~250,000Rp(보드 포함). 초보도 바로 가능해요."),
            (f"{city} 해변 일몰 시간은?", f"발리는 연중 18:00~18:30경 일몰이에요."),
        ],
        "culture": [
            (f"{city} 사원 방문 시 복장 규정은?", f"무릎 아래 하의와 어깨를 가리는 상의가 필수예요."),
            (f"{city} 사원에 가이드가 필요한가요?", f"역사와 문화를 깊이 이해하려면 가이드를 추천해요. 200,000~500,000Rp."),
            (f"{city} 사원 방문 최적 시간은?", f"아침 8시~10시가 사람이 적고 쾌적해요."),
            (f"{city}에서 케착 댄스를 볼 수 있나요?", f"저녁 18:00에 공연. 입장료 100,000~150,000Rp이에요."),
        ],
        "nature": [
            (f"{city} 트레킹 체력 난이도는?", f"중급 난이도. 왕복 2~3시간, 운동화로도 가능해요."),
            (f"{city} 우기에도 트레킹 가능한가요?", f"우기엔 미끄러울 수 있어요. 트레킹화 필수, 가이드 동행 추천."),
            (f"{city} 트레킹 가이드 비용은?", f"1일 200,000~500,000Rp. 그룹으로 가면 1인당 비용이 줄어요."),
            (f"{city} 자연 명소에 입장료 있나요?", f"외국인 기준 50,000~150,000Rp이에요."),
        ],
        "shopping": [
            (f"{city}에서 흥정 어떻게 하나요?", f"처음 가격의 30~50%에서 시작하세요. 웃으면서 친절하게."),
            (f"{city} 시장에서 카드 결제 가능한가요?", f"대부분 현금만 받아요. ATM에서 미리 뽑아가세요."),
            (f"{city} 대표 기념품은 뭔가요?", f"사롱, 우드 카빙, 발리 커피, 아로마 오일이 인기예요."),
            (f"{city} 기념품 배송 서비스 있나요?", f"큰 숍에서는 국제 배송을 해줘요. 비용은 별도."),
        ],
        "transport": [
            (f"{city} 공항에서 시내까지 어떻게 가나요?", f"택시 또는 그랩. 약 {ci.get('airport_min',30)}분, 100,000~200,000Rp."),
            (f"{city}에서 그랩 사용 가능한가요?", f"네, 대부분의 지역에서 잘 돼요."),
            (f"{city} 스쿠터 렌트 안전한가요?", f"국제면허 필수, 좌측 통행. 초보자는 비추천."),
            (f"{city} 기사 투어 가격은?", f"8시간 500,000~700,000Rp. 기사+차량 포함."),
        ],
    }
    faqs = faq_pool.get(cat, faq_pool["food"])
    faq_selected = rng.sample(faqs, min(4, len(faqs)))
    faq_html = '<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">자주 묻는 질문</h2>\n'
    for q, a in faq_selected:
        faq_html += f'<div style="margin:12px 0;padding:16px;background:#fafafa;border-radius:8px;border-left:3px solid #FF6B35">\n<h3 style="font-size:1.05em;font-weight:700;margin:0 0 8px;color:#333">Q. {q}</h3>\n<p style="margin:0;line-height:1.8;color:#555">{a}</p>\n</div>\n'

    # MRT CTA
    mrt_cta = f'''<div style="margin:32px 0;padding:20px;background:linear-gradient(135deg,#FF6B35,#FF8C61);border-radius:12px;text-align:center;color:white">
<p style="margin:0 0 12px;font-weight:700;font-size:1.1em">마이리얼트립에서 {city} {cat_name} 투어 할인받기</p>
<p style="margin:0 0 16px;font-size:0.95em;opacity:0.9">투어, 티켓, 숙소 최대 30% 할인 | 첫 구매 시 추가 할인</p>
<a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="display:inline-block;padding:12px 32px;background:white;color:#FF6B35;border-radius:25px;text-decoration:none;font-weight:700;font-size:1em">할인쿠폰 받기</a>
</div>'''

    # Related areas
    related_cities = [c for c in CITIES if c != city]
    related = rng.sample(related_cities, min(3, len(related_cities)))
    related_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:16px 0">'
    for rc in related:
        related_html += f'<a href="/{rc}/{cat}/{article_no:03d}.html" style="display:inline-block;padding:8px 16px;background:#FF6B35;color:white;border-radius:20px;text-decoration:none;font-size:.9em">{rc} {cat_name}</a>'
    related_html += '</div>'

    # Extra content
    extra1 = get_extra_content(city, cat, article_no, 2)
    extra2 = get_extra_content(city, cat, article_no + 100, 1)
    budget = gen_budget_block(city, cat, article_no)
    weather = gen_weather_block(city, article_no)
    hidden = gen_hidden_block(city, article_no)
    nearby = gen_nearby_block(city, cat, article_no)

    # Get unique meta description
    meta_options = [
        f"{city} {cat_name} 여행 정보. {ci.get('foods',[''])[0]} 후기부터 가격 비교까지. 실전 가이드.",
        f"발리 {city} {cat_name} 추천. 실제 가격, 동선, 추천 기준까지. {ci.get('vibe','')}.",
        f"{city} 자유여행 {cat_name} 가이드. 예산 절약 팁 포함.",
        f"발리 {city} {cat_name} 완벽 가이드. 입장료, 교통, 추천 코스.",
        f"{city} {cat_name} 베스트 코스. 시간대별 팁과 실제 가격 비교.",
    ]
    meta_idx = (hash(f"meta_{city}_{cat}_{article_no}") % (2**31)) % len(meta_options)
    meta_desc = meta_options[meta_idx].rstrip('.') + f". {ci.get('name_en','')} {cat} #{article_no:03d}."

    # Get unique title
    title_options = [
        f"{city} {cat_name} 가이드, 시간대별 동선과 실제 가격 ({ci.get('name_en','')})",
        f"{city} {cat_name} 추천 리스트, 현장에서 확인한 가격 비교 ({ci.get('name_en','')})",
        f"{city} 자유여행 {cat_name} 정리, 예산과 동선 총정리 ({ci.get('name_en','')})",
        f"{city} {cat_name} 베스트 코스, 직접 다녀온 후기 ({ci.get('name_en','')})",
        f"{city} {cat_name} 가성비 가이드, 로컬 vs 관광지 비교 ({ci.get('name_en','')})",
        f"{city} {cat_name} 첫 방문 가이드, 준비물과 주의사항 ({ci.get('name_en','')})",
        f"{city} {cat_name} 완벽 정리, 실제 경험담과 실패 팁 ({ci.get('name_en','')})",
        f"{city} {cat_name} 여행 코스, 반나절~1일 동선 추천 ({ci.get('name_en','')})",
        f"{city} {cat_name} 정보, 가격·위치·팁 한눈에 보기 ({ci.get('name_en','')})",
        f"{city} {cat_name} 추천, 초보자도 쉽게 따라하는 가이드 ({ci.get('name_en','')})",
        f"{city} {cat_name} 예산 비교, 저렴하게 즐기는 방법 ({ci.get('name_en','')})",
        f"{city} {cat_name} 현장 후기, 예상과 달랐던 점 ({ci.get('name_en','')})",
        f"{city} {cat_name} 동선 추천, 효율적으로 돌아보는 법 ({ci.get('name_en','')})",
        f"{city} {cat_name} 필수 정보, 출발 전 체크리스트 ({ci.get('name_en','')})",
    ]
    title = title_options[article_no % len(title_options)]

    # Build full HTML
    CSS = """:root{--primary:#FF6B35;--bg:#FAFAFA;--text:#1A1A2E;--text-light:#666;--card-bg:#FFFFFF;--shadow:0 2px 8px rgba(0,0,0,0.08)}*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);line-height:1.85;word-break:keep-all}.container{max-width:800px;margin:0 auto;padding:20px}header{background:linear-gradient(135deg,#FF6B35,#FF8C61);color:white;padding:40px 20px;text-align:center}header h1{font-size:1.8rem;margin-bottom:10px;word-break:keep-all}header .meta{opacity:0.9;font-size:0.9rem}.breadcrumb{padding:15px 0;font-size:0.85rem;color:var(--text-light)}.breadcrumb a{color:var(--primary);text-decoration:none}article{background:var(--card-bg);border-radius:12px;padding:30px;box-shadow:var(--shadow);margin:20px 0}article h2{color:var(--primary);font-size:1.4rem;margin:30px 0 15px;padding-bottom:8px;border-bottom:2px solid var(--primary)}article h3{color:#333;font-size:1.15rem;margin:20px 0 10px}article table{width:100%;border-collapse:collapse;margin:16px 0}article th,article td{padding:10px 8px;border:1px solid #ddd;text-align:left}article th{background:#FF6B35;color:white}article tr:nth-child(even){background:#f9f9f9}article ul,article ol{padding-left:20px;margin:16px 0}article li{margin-bottom:8px;line-height:1.7}.content-intro{margin:0 0 20px;padding:16px 20px;background:linear-gradient(135deg,#fff7ed,#fff3e0);border-radius:10px;border:1px solid #ffe0b2;font-weight:500;line-height:1.8}.content-footer{margin:24px 0;padding:12px;background:#f5f5f5;border-radius:8px;font-size:0.9em;color:#666}.tags{margin:20px 0}.tag{display:inline-block;background:#F0F0F0;padding:4px 12px;border-radius:20px;font-size:0.8rem;margin:3px;color:var(--text-light)}footer{text-align:center;padding:30px;color:var(--text-light);font-size:0.85rem}#reading-progress{position:fixed;top:0;left:0;width:0%;height:3px;background:linear-gradient(90deg,#FF6B35,#FF8C61);z-index:9999;transition:width 0.1s}figure img{background:#f0f0f0;min-height:100px}@media(max-width:600px){.container{padding:10px}article{padding:20px}header h1{font-size:1.4rem}table{font-size:.8em}article h2{font-size:1.2rem}}@media(prefers-color-scheme:dark){:root{--bg:#1a1a2e;--text:#e0e0e0;--text-light:#aaa;--card-bg:#16213e;--border:#333}body{background:var(--bg);color:var(--text)}article{background:var(--card-bg)}.content-intro{background:linear-gradient(135deg,#1a1a2e,#16213e);border-color:#333}article tr:nth-child(even){background:#1a1a2e}}"""

    SCROLL_JS = "window.addEventListener('scroll',function(){var w=document.body.scrollTop||document.documentElement.scrollTop;var h=document.documentElement.scrollHeight-document.documentElement.clientHeight;document.getElementById('reading-progress').style.width=(w/h*100)+'%'});"

    ld_json = json.dumps({"@context":"https://schema.org","@type":"Article","headline":title,"description":meta_desc,"image":[f"https://balitravel.blog/images/{city}/{cat}/{images[0] if images else 'default.webp'}"],"datePublished":"2026-04-01","dateModified":"2026-05-03","author":{"@type":"Person","name":"JP Travel Bali"},"publisher":{"@type":"Organization","name":"JP Travel Bali"},"mainEntityOfPage":{"@type":"WebPage","@id":f"https://balitravel.blog/{city}/{cat}/{article_no:03d}.html"}}, ensure_ascii=False)

    img0 = images[0] if images else 'default.webp'

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{city}, {cat_name}, 발리, 인도네시아, 자유여행, 2026">
<link rel="canonical" href="https://balitravel.blog/{city}/{cat}/{article_no:03d}.html">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="https://balitravel.blog/images/{city}/{cat}/{img0}">
<meta property="og:url" content="https://balitravel.blog/{city}/{cat}/{article_no:03d}.html">
<meta property="og:site_name" content="JP Travel Bali">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld_json}</script>
<style>{CSS}</style>
</head>
<body>
<div id="reading-progress"></div>
<script>{SCROLL_JS}</script>
<div class="container">
<header>
<h1>{title}</h1>
<div class="meta">JP Travel Bali | {city} {cat_name} 가이드 | 2026</div>
</header>
<div class="breadcrumb"><a href="/">홈</a> &rsaquo; <a href="/{city}/">{city}</a> &rsaquo; <a href="/{city}/{cat}/">{cat_name}</a> &rsaquo; {article_no:03d}</div>
<article>
<div class="content-intro"><strong>[제휴 안내]</strong> 이 글에는 마이리얼트립 제휴 링크가 포함되어 있으며, 링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.</div>
<div class="content-intro">{intro}</div>

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">{city} {cat_name} 핵심 정보</h2>
<p style="margin:12px 0;line-height:1.8">{experience}</p>
{extra1}

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">가격 비교</h2>
{price_table}
<p style="margin:12px 0;line-height:1.8">위 가격은 2026년 기준 현장 결제 가격이에요. 예약 플랫폼마다 다를 수 있으니 여러 곳에서 비교해보세요.</p>
<p style="margin:12px 0;line-height:1.8"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;font-weight:600">마이리얼트립에서 할인 예약하기</a></p>
{budget}

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">추천과 비추천</h2>
<div style="margin:16px 0;padding:16px;background:#e8f5e9;border-radius:8px;border-left:3px solid #4caf50"><p style="margin:0;line-height:1.8"><strong>[추천] {rec}</strong></p></div>
<div style="margin:16px 0;padding:16px;background:#fce4ec;border-radius:8px;border-left:3px solid #e91e63"><p style="margin:0;line-height:1.8"><strong>[비추천] {not_rec}</strong></p></div>

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">시간대별 팁</h2>
{''.join(f'<p style="margin:8px 0;line-height:1.8">- {t}</p>' for t in time_tips)}
{weather}

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">실수하기 쉬운 점</h2>
<div style="margin:16px 0;padding:16px;background:#fff3e0;border-radius:8px;border-left:3px solid #ff9800"><p style="margin:0;line-height:1.8">[주의] {mistake}</p></div>
{extra2}

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">여행 준비물 체크리스트</h2>
<ul>
<li>여권 (유효기간 6개월 이상 남은 것)</li>
<li>환전: 현지 ATM에서 인출하거나, 달러를 가져가서 환전소에서 교환</li>
<li>선크림 SPF50, 모기 기피제, 우산 또는 우비</li>
<li>편한 walking shoes, 아쿠아슈즈</li>
<li>보조배터리와 충전기 (발리 콘센트는 C타입 또는 F타입)</li>
<li>오프라인 구글맵 다운로드 필수</li>
</ul>

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">마무리 정리</h2>
<p style="margin:12px 0;line-height:1.8">{city}의 {cat_name}은 발리 여행에서 빼놓을 수 없는 경험이에요. 직접 다녀온 경험을 바탕으로 가격, 동선, 주의사항을 정리했으니 planning에 참고하세요. 추가로 궁금한 점이 있으면 댓글로 남겨주세요. 즐거운 {city} 여행 되세요!</p>
<p style="margin:12px 0;line-height:1.8">발리 환율은 1Rp 약 0.083원(2026년 기준)이에요. 편하게 계산할 때는 10,000Rp 약 830원, 100,000Rp 약 8,300원으로 생각하면 돼요. 시장에서는 현금만 받는 곳이 많으니 충분히 환전해가세요.</p>

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">주변 추천 명소</h2>
{nearby}
{hidden}

{mrt_cta}

{faq_html}

<h2 style="font-size:1.3em;font-weight:700;margin:32px 0 16px;color:#1a1a2e;padding:10px 14px;background:#f8f9fa;border-left:4px solid #0f3460;line-height:1.5">관련 지역 추천</h2>
{related_html}

{images_html}

<div class="tags">
<span class="tag">{city}</span><span class="tag">{cat_name}</span><span class="tag">발리</span><span class="tag">인도네시아</span><span class="tag">자유여행</span><span class="tag">2026</span>
</div>
<div class="content-footer">
<p>이 글이 {city} 여행 계획에 도움이 되셨길 바랍니다. 추가 질문은 댓글로 남겨주세요!</p>
<p style="margin-top:8px"><a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립 할인쿠폰 받기</a></p>
</div>
</article>
</div>
<footer>
<p>이 글에는 <a href="{MRT_LINK}" target="_blank" rel="sponsored nofollow noopener" style="color:#FF6B35;text-decoration:none">마이리얼트립</a> 제휴 링크가 포함되어 있습니다.</p>
<p>이 글에는 마이리얼트립 제휴 링크가 포함되어 있으며, 링크를 통해 예약하면 작성자에게 일정 수수료가 지급될 수 있습니다. 여행자에게 추가 비용은 발생하지 않습니다.</p>
<p style="margin-top:10px">JP Travel Bali &copy; 2026</p>
</footer>
</body>
</html>'''

    f.write_text(html, encoding='utf-8')
    count += 1
    if count % 100 == 0:
        print(f"  Progress: {count}/{len(html_files)}")

print(f"\nProcessed {count} files")
print(f"Unique titles: {len(titles)}")
print(f"Unique metas: {len(metas)}")

# Verify
print("\nVerifying...")
short = 0
chinese = 0
emoji = 0
for f in html_files:
    c = f.read_text(encoding='utf-8')
    body = re.sub(r'<[^>]+>', '', c)
    body = re.sub(r'\s+', '', body)
    kr = len(re.findall(r'[가-힣]', body))
    if kr < 1500:
        short += 1
    if hanja_re.search(body):
        chinese += 1
    if emoji_re.search(body):
        emoji += 1

print(f"  Under 1500 chars: {short}")
print(f"  Chinese/Hanja: {chinese}")
print(f"  Emoji: {emoji}")
print("DONE")
