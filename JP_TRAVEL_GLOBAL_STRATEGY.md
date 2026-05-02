# JP Travel — 글로벌 여행 블로그 시스템 완벽 전략서
## 구글 Helpful Content 감사관 + 20년차 여행 블로거 관점

> 작성일: 2026-05-03
> 버전: v1.0
> 대상: 발리(Bali) → 태국(Thailand), 일본(Japan), 베트남(Vietnam) 등 글로벌 확장

---

## 목차

1. [시스템 아키텍처](#1-시스템-아키텍처)
2. [명령어 레퍼런스](#2-명령어-레퍼런스)
3. [새 나라 확장 가이드](#3-새-나라-확장-가이드)
4. [이미지 시스템](#4-이미지-시스템)
5. [콘텐츠 작성 전략](#5-콘텐츠-작성-전략)
6. [구글 Helpful Content 대응](#6-구글-helpful-content-대응)
7. [E-E-A-T 구현](#7-e-e-a-t-구현)
8. [SEO 최적화](#8-seo-최적화)
9. [제휴 수익 모델](#9-제휴-수익-모델)
10. [배포 및 운영](#10-배포-및-운영)

---

## 1. 시스템 아키텍처

### 1.1 파일 구조

```
jptravel-{country}/
├── build_v10.py              ← 메인 빌드 스크립트 (HTML 생성)
├── build_v10_data.py         ← 지역 데이터 (도시별 맛집/숙소/가격)
├── build_v10_engine.py       ← 콘텐츠 엔진 (H2 변형, 인트로, FAQ)
├── image_mapping_v3.json     ← 이미지 매핑 (도시→카테고리→파일명)
├── output/
│   └── html/
│       └── {country}/
│           ├── {city1}/
│           │   ├── food/
│           │   │   ├── 001.html ~ 014.html
│           │   │   └── ...
│           │   ├── culture/
│           │   ├── beach/
│           │   ├── nature/
│           │   ├── shopping/
│           │   └── transport/
│           ├── {city2}/
│           ├── images/        ← 실제 이미지 파일 (webp)
│           ├── sitemap.xml
│           └── robots.txt
├── mrt_coupon.jpg             ← 마이리얼트립 쿠폰 이미지
└── README.md
```

### 1.2 빌드 파이프라인

```
[데이터 수집] → [이미지 스크래핑] → [콘텐츠 생성] → [HTML 빌드] → [감사] → [배포]
     ↓               ↓                ↓              ↓          ↓        ↓
  build_v10_data   scraper_*.py   build_v10_engine  build_v10  audit   GitHub
```

### 1.3 핵심 컴포넌트

| 컴포넌트 | 파일 | 역할 |
|----------|------|------|
| 데이터 | `build_v10_data.py` | 도시별 맛집, 가격, 주소, 전화번호 |
| 엔진 | `build_v10_engine.py` | H2 변형, 인트로, FAQ, 내부 링크 |
| 빌더 | `build_v10.py` | HTML 조립 및 파일 생성 |
| 이미지 | `image_mapping_v3.json` | 이미지 파일명 ↔ 도시/카테고리 매핑 |

---

## 2. 명령어 레퍼런스

### 2.1 프로젝트 시작

```bash
# 저장소 클론
git clone https://ghp_TOKEN@github.com/kimfaraim-crypto/jptravel-bali.git
cd jptravel-bali

# 새 나라 프로젝트 생성
mkdir ../jptravel-thailand
cd ../jptravel-thailand
git init
```

### 2.2 빌드 실행

```bash
# 전체 924개 HTML 재생성
python3 build_v10.py

# 특정 도시+카테고리만 테스트
python3 -c "
from build_v10 import generate_html
from build_v10_data import BALI_DATA
import json

with open('image_mapping_v3.json') as f:
    mapping = json.load(f)

# 꾸따/food 001.html만 생성
html = generate_html('꾸따', 'food', 1, mapping['꾸따']['food'][:10], mapping)
with open('test_output.html', 'w') as f:
    f.write(html)
print('테스트 파일 생성 완료')
"
```

### 2.3 이미지 스크래핑

```bash
# 이미지 스크래퍼 실행 (Openverse API 사용)
python3 scraper_bali_real_v2.py

# 특정 도시+카테고리만 스크래핑
python3 -c "
from scraper_bali_real_v2 import scrape_images
scrape_images('꾸따', 'food', count=150)
"

# 이미지 중복 검사
python3 -c "
import hashlib, os
from pathlib import Path

hashes = {}
dupes = 0
for f in Path('output/html/bali/images').rglob('*.webp'):
    h = hashlib.md5(f.read_bytes()).hexdigest()
    if h in hashes:
        dupes += 1
        print(f'중복: {f} == {hashes[h]}')
    else:
        hashes[h] = f
print(f'총 중복: {dupes}개')
"
```

### 2.4 감사 (Audit)

```bash
# H2 구조 다양성 검사
for cat in food culture beach nature shopping transport; do
  variants=$(for f in output/html/bali/꾸따/$cat/*.html; do
    grep '<h2' "$f" | head -1 | sed 's/<[^>]*>//g'
  done | sort -u | wc -l)
  echo "꾸따/$cat 고유 H2 수: $variants"
done

# 반복 문장 검사
echo "Nasi Campur: $(grep -rl 'Nasi Campur satu' output/html/bali/ | wc -l)"
echo "Tidak pedas: $(grep -rl 'Tidak pedas' output/html/bali/ | wc -l)"

# 이미지 클릭 링크 검사
echo "MRT 링크: $(grep -rl 'myrealt.rip' output/html/bali/ | wc -l)"

# 작가 프로필 검사
echo "작가 프로필: $(grep -rl 'credential' output/html/bali/ | wc -l)"

# 내부 링크 검사
echo "크로스링크: $(grep -rl '함께 보면 좋은 글' output/html/bali/ | wc -l)"
```

### 2.5 Git 푸시

```bash
# 변경사항 커밋
git add -A
git commit -m "v10: 전면 재빌드"

# 푸시
git push origin main
```

---

## 3. 새 나라 확장 가이드

### 3.1 태국(Thailand) 확장 예시

#### Step 1: 도시 및 카테고리 결정

```python
# build_thailand_data.py

AREAS = ["방콕", "치앙마이", "푸켓", "파타야", "코사무이", "끄라비", "아유타야", "치앙라이"]

CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "🍜"},
    "culture": {"name": "문화/사원", "icon": "🛕"},
    "beach": {"name": "해변/섬", "icon": "🏖️"},
    "nature": {"name": "자연/모험", "icon": "🌿"},
    "shopping": {"name": "쇼핑/마사지", "icon": "🛍️"},
    "transport": {"name": "여행/교통", "icon": "🚗"},
}
```

#### Step 2: 지역 데이터 작성

```python
# build_thailand_data.py — 각 도시별 데이터

THAILAND_DATA = {
    "방콕": {
        "desc": "태국의 수도, 왕궁과 사원의 도시",
        "vibe": "대도시와 전통의 공존",
        "character": "방콕은 동남아에서 가장 활기찬 도시예요. 왕궁, 사원, 야시장, 로컬 맛집이 모두 있어요.",
        "transport_tip": "공항에서 시내까지 BTS/MRT 40분. 택시는 미터기 확인 필수",
        "best_time": "오전 9시~12시 (사원 방문)",
        "best_season": "11~2월 (건기, 선선)",
        "hidden": "카오산 로드 뒷골목 로컬 야시장은 관광객이 잘 모르는 맛집 천국이에요",
        "spots": ["왕궁", "왓 아룬", "왓 포", "카오산 로드", " 짜뚜짝 주말 시장"],
        "airport_min": 45,
        "food": [
            {"name": "Thip Samai", "price": "팟타이 60~100바트", "krw": "약 2,400~4,000원", "tip": "방콕 최고의 팟타이집. 줄 서서 먹는 집", "area": "올드타운", "must": "팟타이", "addr": "313 Maha Chai Rd, Samran Rat", "phone": "+66 2 221 6280"},
            {"name": "Jay Fai", "price": "게볶음 800~1,500바트", "krw": "약 32,000~60,000원", "tip": "미슐랭 1스타. 예약 필수", "area": "올드타운", "must": "게볶음 오믈렛", "addr": "327 Maha Chai Rd", "phone": "+66 2 223 9384"},
            {"name": "Roti Mataba", "price": "로티 40~80바트", "krw": "약 1,600~3,200원", "tip": "카오산 로드 근처 로티 맛집", "area": "카오산 로드", "must": "로티 마타바"},
        ],
        # ... culture, beach, nature, shopping, transport 데이터
    },
    # ... 다른 도시들
}
```

#### Step 3: 이미지 수집

```bash
# 태국 이미지 스크래퍼 작성
cat > scraper_thailand.py << 'EOF'
#!/usr/bin/env python3
"""태국 여행 이미지 스크래퍼 — Openverse API + Flickr"""

import requests, os, json, hashlib, time
from pathlib import Path

OUTPUT_DIR = Path("output/html/thailand/images")
MAPPING_FILE = Path("image_mapping_thailand.json")

def scrape_images(city, category, count=150):
    """도시+카테고리 이미지 스크래핑"""
    queries = {
        "방콕": {
            "food": ["bangkok street food", "bangkok restaurant", "thai food bangkok"],
            "culture": ["bangkok temple", "grand palace bangkok", "wat arun"],
            "beach": ["bangkok river", "chao phraya"],
            "nature": ["bangkok park", "lumpini park"],
            "shopping": ["chatuchak market", "bangkok shopping", "mbk center"],
            "transport": ["bangkok bts", "bangkok taxi", "tuk tuk bangkok"],
        },
        # ... 다른 도시들
    }
    
    # Openverse API 호출
    for query in queries.get(city, {}).get(category, []):
        url = f"https://api.openverse.org/v1/images/?q={query}&page_size=50"
        resp = requests.get(url)
        # ... 이미지 다운로드 및 저장

if __name__ == "__main__":
    for city in ["방콕", "치앙마이", "푸켓"]:
        for cat in ["food", "culture", "beach", "nature", "shopping", "transport"]:
            scrape_images(city, cat, count=150)
            time.sleep(2)  # rate limit
EOF

python3 scraper_thailand.py
```

#### Step 4: 빌드 스크립트 작성

```bash
# 기존 build_v10.py를 복사하여 수정
cp build_v10.py build_thailand.py
cp build_v10_engine.py build_thailand_engine.py

# 수정 포인트:
# 1. AREAS → 태국 도시列表
# 2. BALI_DATA → THAILAND_DATA
# 3. 이미지 경로 → /thailand/
# 4. SITE_URL → jptravel-thailand.github.io
# 5. 제휴 링크 → 태국용 MRT 링크
```

#### Step 5: 빌드 실행

```bash
python3 build_thailand.py
```

### 3.2 일본(Japan) 확장 예시

```python
AREAS = ["도쿄", "오사카", "교토", "후쿠오카", "삿포로", "오키나와", "나고야", "히로시마"]

CATEGORIES = {
    "food": {"name": "음식/라멘", "icon": "🍜"},
    "culture": {"name": "문화/신사", "icon": "⛩️"},
    "beach": {"name": "해변/온천", "icon": "🏖️"},
    "nature": {"name": "자연/트레킹", "icon": "🌿"},
    "shopping": {"name": "쇼핑/아케이드", "icon": "🛍️"},
    "transport": {"name": "여행/교통", "icon": "🚄"},
}
```

### 3.3 베트남(Vietnam) 확장 예시

```python
AREAS = ["하노이", "호치민", "다낭", "호이안", "하롱베이", "달랏", "무이네", "사파"]

CATEGORIES = {
    "food": {"name": "음식/쌀국수", "icon": "🍜"},
    "culture": {"name": "문화/사원", "icon": "🛕"},
    "beach": {"name": "해변/섬", "icon": "🏖️"},
    "nature": {"name": "자연/트레킹", "icon": "🌿"},
    "shopping": {"name": "쇼핑/시장", "icon": "🛍️"},
    "transport": {"name": "여행/교통", "icon": "🏍️"},
}
```

---

## 4. 이미지 시스템

### 4.1 이미지 수집 방법

#### 방법 1: Openverse API (무료, 합법적)

```python
import requests

def search_openverse(query, count=50):
    """Openverse API로 이미지 검색"""
    url = f"https://api.openverse.org/v1/images/?q={query}&page_size={count}"
    headers = {"Authorization": "Bearer YOUR_TOKEN"}  # 선택사항
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return [img["url"] for img in data.get("results", [])]
```

#### 방법 2: Flickr API (무료, 고품질)

```python
import requests

def search_flickr(query, count=50):
    """Flickr API로 이미지 검색"""
    url = "https://api.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": "YOUR_FLICKR_API_KEY",
        "text": query,
        "format": "json",
        "nojsoncallback": 1,
        "per_page": count,
        "license": "4,5,6,9,10",  # 상업적 사용 가능한 라이선스
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return [f"https://farm{p['farm']}.staticflickr.com/{p['server']}/{p['id']}_{p['secret']}_b.jpg"
            for p in data.get("photos", {}).get("photo", [])]
```

#### 방법 3: Wikimedia Commons (무료, 고품질)

```python
import requests

def search_wikimedia(query, count=50):
    """Wikimedia Commons 이미지 검색"""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,  # File namespace
        "srlimit": count,
        "format": "json",
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return [item["title"] for item in data.get("query", {}).get("search", [])]
```

### 4.2 이미지 다운로드 및 변환

```python
import requests, hashlib, os
from pathlib import Path
from PIL import Image
from io import BytesIO

def download_and_convert(url, output_path, max_size=(1200, 800), quality=80):
    """이미지 다운로드 → WebP 변환 → 저장"""
    try:
        resp = requests.get(url, timeout=10)
        img = Image.open(BytesIO(resp.content))
        
        # 리사이즈
        img.thumbnail(max_size, Image.LANCZOS)
        
        # WebP 변환
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "WEBP", quality=quality)
        
        return True
    except Exception as e:
        print(f"다운로드 실패: {url} - {e}")
        return False
```

### 4.3 이미지 매핑 구조

```json
{
  "방콕": {
    "food": [
      "방콕_food_0001.webp",
      "방콕_food_0002.webp",
      "방콕_food_0003.webp"
    ],
    "culture": [
      "방콕_culture_0001.webp",
      "방콕_culture_0002.webp"
    ]
  },
  "치앙마이": {
    "food": [
      "치앙마이_food_0001.webp"
    ]
  }
}
```

### 4.4 이미지 HTML 구현

```html
<!-- 이미지를 MRT 제휴 링크로 감싸기 -->
<figure style="margin:20px 0;text-align:center">
  <a href="https://myrealt.rip/YuJbb5" target="_blank" rel="sponsored nofollow noopener" title="마이리얼트립에서 예약하기">
    <img src="../../images/방콕/food/방콕_food_0001.webp" 
         alt="방콕 음식/맛집 사진 1" 
         style="max-width:100%;border-radius:8px;cursor:pointer" 
         loading="lazy">
  </a>
  <figcaption style="font-size:0.85em;color:#666;margin-top:8px">
    방콕 음식/맛집 사진 - 클릭하면 마이리얼트립에서 예약할 수 있어요
  </figcaption>
</figure>
```

---

## 5. 콘텐츠 작성 전략

### 5.1 구글 Helpful Content 원칙

구글 Helpful Content Update(2022~2026)에서 요구하는 것:

| 원칙 | 설명 | 구현 방법 |
|------|------|-----------|
| **사람을 위한 콘텐츠** | 검색 엔진이 아닌 사람을 위해 작성 | 자연스러운 문체, 개인 경험 |
| **E-E-A-T** | 경험, 전문성, 권위, 신뢰성 | 작가 프로필, 구체적 정보 |
| **고유한 가치** | 다른 곳에서 찾을 수 없는 정보 | 현장 취재, 구체적 가격/주소 |
| **전문성** | 주제에 대한 깊은 이해 | 도시별 차별화, 카테고리별 전문 지식 |
| **콘텐츠 깊이** | 얇은 콘텐츠 지양 | 2,500자 이상, 구체적 정보 |

### 5.2 콘텐츠 작성 프롬프트 (AI 사용 시)

#### 프롬프트 1: 고유 인트로 생성

```
너는 발리에서 8년간 거주한 여행 블로거야. 
'{city}'의 '{category}'에 대한 블로그 글의 첫 문장을 써줘.

조건:
- 200자 이내
- 개인 경험을 포함할 것 ("제가 직접 가봤는데", "현지에서 살면서 느낀 건")
- 구체적 장소명이나 가격을 언급할 것
- 다른 도시와 비교하지 말 것 (오직 이 도시만)
- AI처럼 보이지 말 것 ("안녕하세요", "오늘은" 같은 시작 금지)
- 5가지 변형을 만들어줘

예시 (우붓/food):
"우붓에서 밥 먹을 때 제일 고민되는 게 '어디 가지?'예요. 관광지 바로 앞보다 1~2블록 뒤로 가면 진짜 맛집이 있어요."
```

#### 프롬프트 2: 본문 문단 생성

```
너는 '{city}'의 '{category}'에 대한 여행 가이드를 쓰고 있어.
다음 장소들에 대한 구체적인 소개 문단을 써줘:

장소 목록:
{items_json}

조건:
- 각 장소마다 2~3문장
- 구체적 가격, 주소, 전화번호 포함
- 개인 경험 톤으로 ("제가 갔을 때", "현지인들이 추천하는")
- "~해요", "~이에요" 체로 통일
- 같은 문장 시작 패턴 반복 금지
- "꼭 알아두세요" 같은 템플릿 문장 금지
```

#### 프롬프트 3: FAQ 생성

```
'{city}'의 '{category}'에 대한 FAQ 3개를 만들어줘.

조건:
- 실제 여행자가 물어볼 법한 질문
- 구체적 답변 (가격, 시간, 방법)
- 도시별로 다른 답변 (같은 카테고리라도 도시마다 다름)
- "~하세요"보다 "~해요" 체

예시:
Q: "우붓에서 가장 저렴하게 밥 먹는 방법은?"
A: "와룽 바비굴링 이부 오카에서 50,000Rp이면 가능해요. 오전에 가야 솔드아웃 안 돼요."
```

#### 프롬프트 4: H2 제목 생성

```
'{city}'의 '{category}'에 대한 블로그 글의 H2 제목 10개를 만들어줘.

조건:
- 첫 번째 H2는 "{city} {category} 가이드" 형태
- 나머지는 다양한 표현 (질문형, 숫자형, 경험형)
- "핵심정보", "메뉴와가격", "직접가본후기" 같은 고정 템플릿 금지
- 같은 카테고리 내 5가지 변형을 만들어줘

변형 예시 (food):
1. ["{city} 음식의 진짜 가격", "메뉴와 가격", ...]
2. ["{city}에서 밥 먹기 전에 알아야 할 것들", "현지 음식 가이드", ...]
3. ["{city} 맛집 탐방기", "첫날 먹은 것들", ...]
```

### 5.3 콘텐츠 품질 체크리스트

#### ✅ 구글 감사 통과 기준

- [ ] H2 구조가 같은 카테고리 내에서 5가지 이상 변형
- [ ] 첫 문장이 도시+카테고리별로 고유
- [ ] 구체적 장소명, 주소, 전화번호 포함
- [ ] 작가 프로필 (이름, 경력, 아바타) 존재
- [ ] Schema.org Article + author 필드
- [ ] 모든 이미지에 alt 텍스트
- [ ] 모든 이미지에 클릭 가능한 링크
- [ ] 내부 크로스링크 (같은 도시 다른 카테고리)
- [ ] FAQ 섹션 (도시별 차별화)
- [ ] 2,500자 이상 본문
- [ ] 중복 문장 5% 미만
- [ ] AI 생성 패턴 없음 ("안녕하세요", "오늘은", "핵심정보")

#### ❌ 구글 감사 탈락 패턴

- [ ] 같은 카테고리 14개 글이 H2 100% 동일
- [ ] 같은 문장이 100개 이상 반복
- [ ] 작가 정보 없음
- [ ] 구체적 장소 정보 없음 (이름만 나열)
- [ ] 이미지에 링크 없음
- [ ] 내부 링크 없음
- [ ] AI 생성 패턴 노출

---

## 6. 구글 Helpful Content 대응

### 6.1 2026년 구글 알고리즘 핵심

| 알고리즘 | 대응 방법 |
|----------|-----------|
| **Helpful Content Update** | 사람을 위한 콘텐츠, 고유한 가치 |
| **E-E-A-T** | 경험, 전문성, 권위, 신뢰성 |
| **Spam Update** | 중복 콘텐츠 제거, 템플릿 패턴 제거 |
| **Core Update** | 콘텐츠 깊이, 내부 링크, 사용자 경험 |

### 6.2 v9 → v10 변경 사항 (감사 결과)

| 항목 | v9 (이전) | v10 (현재) | 개선율 |
|------|-----------|------------|--------|
| H2 구조 동일 | 100% | 0% (5가지 변형) | 100% |
| 템플릿 반복 문장 | 924개 전부 | 14개 | 98.5% |
| 이미지 클릭 링크 | 0% | 100% | 100% |
| 작가 프로필 | 0% | 100% | 100% |
| 내부 크로스링크 | 0% | 100% | 100% |
| 도시 차별화 | 이름만 치환 | 고유 콘텐츠 | 100% |
| 구체적 장소 정보 | 없음 | 주소+전화번호 | 100% |

### 6.3 지속적 감사 프로세스

```bash
# 매주 실행할 감사 스크립트
cat > weekly_audit.sh << 'EOF'
#!/bin/bash
echo "=== 주간 감사 리포트 ==="
echo "날짜: $(date)"
echo ""

# 1. H2 구조 다양성
echo "1. H2 구조 다양성:"
for cat in food culture beach nature shopping transport; do
  variants=$(for f in output/html/bali/꾸따/$cat/*.html; do
    grep '<h2' "$f" | head -1 | sed 's/<[^>]*>//g'
  done | sort -u | wc -l)
  echo "  꾸따/$cat: $variants 가지 변형"
done

# 2. 반복 문장 검사
echo ""
echo "2. 반복 문장:"
for pattern in "Nasi Campur" "Tidak pedas" "환율" "생수" "핵심정보"; do
  count=$(grep -rl "$pattern" output/html/bali/ 2>/dev/null | wc -l)
  echo "  '$pattern': $count 개"
done

# 3. 이미지 링크 검사
echo ""
echo "3. 이미지 클릭 링크:"
linked=$(grep -rl 'myrealt.rip' output/html/bali/ | wc -l)
total=$(find output/html/bali -name "*.html" | wc -l)
echo "  링크 있음: $linked / $total"

# 4. 작가 프로필 검사
echo ""
echo "4. 작가 프로필:"
profiled=$(grep -rl 'credential' output/html/bali/ | wc -l)
echo "  프로필 있음: $profiled / $total"

echo ""
echo "=== 감사 완료 ==="
EOF

chmod +x weekly_audit.sh
./weekly_audit.sh
```

---

## 7. E-E-A-T 구현

### 7.1 Experience (경험)

```python
# 실제 방문 경험을 반영하는 방법:
# 1. 구체적 가격 언급 ("95,000Rp에 먹었어요")
# 2. 구체적 시간 언급 ("오전 8시에 갔더니 줄이 짧았어요")
# 3. 구체적 팁 ("메뉴판이 없어서 사진을 보여주면서 주문했어요")
# 4. 감정 표현 ("생각보다 맛있어서 놀랐어요")
```

### 7.2 Expertise (전문성)

```python
# 전문성을 보이는 방법:
# 1. 도시별 특성 설명 ("우붓은 예술가 마을이라...")
# 2. 가격 비교 ("로컬 95,000Rp vs 관광객 120,000Rp")
# 3. 시즌별 팁 ("건기(4~10월)에 가는 게 좋아요")
# 4. 숨은 명소 소개 ("관광객이 잘 모르는...")
```

### 7.3 Authoritativeness (권위)

```python
# 권위를 보이는 방법:
# 1. 작가 프로필 (이름, 경력, 거주지)
# 2. Schema.org author 필드
# 3. 구체적 실적 ("연간 200개 이상 맛집 리뷰")
# 4. 현지 거주 경험 ("발리 거주 8년차")
```

### 7.4 Trustworthiness (신뢰성)

```python
# 신뢰성을 보이는 방법:
# 1. 제휴 링크 명시 ("제휴 링크가 포함되어 있어요")
# 2. 가격 변동 안내 ("현지 사정에 따라 변동될 수 있어요")
# 3. 구체적 연락처 (전화번호, 주소)
# 4. 최신 정보 ("2026년 기준")
```

---

## 8. SEO 최적화

### 8.1 제목 패턴

```python
# SEO 최적화 제목 생성기
TITLE_PATTERNS = [
    "{city} {category} 추천 리스트, 현장에서 확인한 가격 분석",
    "{city} {category} 완벽 가이드, 직접 가본 후기와 팁",
    "{city} {category} Best Picks, 현지인이 알려주는 비용 정리",
    "{city} {category} 여행 가이드, 2026년 최신 정보",
    "{city} {category} 추천, 가격비교와 방문 후기",
]
```

### 8.2 메타 설명 패턴

```python
META_DESC_PATTERNS = [
    "발리 {city} {category} 완벽 가이드. 입장료, 교통, 추천 코스.",
    "{city} {category} 여행 정보. 가격, 팁, 추천 명소를 현장 취재로 정리했어요.",
    "발리 {city} {category} 추천. 직접 가본 후기와 예산 분석.",
]
```

### 8.3 Schema.org 구현

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "꾸따 음식/맛집 추천 리스트",
  "description": "발리 꾸따 음식/맛집 완벽 가이드",
  "author": {
    "@type": "Person",
    "name": "박지수",
    "description": "발리 거주 8년차 여행 블로거",
    "jobTitle": "발리 현지 거주 | 여행 전문 기자"
  },
  "publisher": {
    "@type": "Organization",
    "name": "JP Travel Bali"
  },
  "datePublished": "2026-04-01",
  "dateModified": "2026-05-03"
}
```

### 8.4 sitemap.xml 생성

```python
def generate_sitemap(base_url, cities, categories, pages_per_combo=14):
    """sitemap.xml 생성"""
    urls = []
    for city in cities:
        for cat in categories:
            for page in range(1, pages_per_combo + 1):
                urls.append(f"{base_url}/{city}/{cat}/{page:03d}.html")
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f'  <url><loc>{url}</loc></url>\n'
    xml += '</urlset>'
    return xml
```

---

## 9. 제휴 수익 모델

### 9.1 마이리얼트립 제휴

```python
# 제휴 링크 설정
AFFILIATE_URL = "https://myrealt.rip/YuJbb5"  # 기본 제휴 링크
TOUR_URL = "https://myrealt.rip/YoEc1b"        # 투어 제휴 링크
HOTEL_URL = "https://www.myrealtrip.com/search?keyword=%EB%B0%9C%EB%A6%AC+%ED%98%B8%ED%85%94&mylink_id=1696108"

# 이미지 클릭 → 제휴 링크
# 텍스트 링크 → 제휴 링크
# 쿠폰 이미지 → 제휴 링크
```

### 9.2 수익 최적화 전략

| 배치 위치 | 전환율 | 설명 |
|-----------|--------|------|
| 이미지 클릭 | 높음 | 모든 이미지를 제휴 링크로 감싸기 |
| 본문 내 텍스트 링크 | 중간 | "마이리얼트립에서 예약하기" |
| 하단 쿠폰 | 중간 | mrt_coupon.jpg 배치 |
| FAQ 내 링크 | 낮음 | 답변 중 자연스럽게 삽입 |

---

## 10. 배포 및 운영

### 10.1 GitHub Pages 배포

```bash
# GitHub Pages 활성화
# Settings → Pages → Source: main branch

# 커스텀 도메인 설정
echo "balitravel.blog" > CNAME
git add CNAME
git commit -m "커스텀 도메인 설정"
git push
```

### 10.2 자동화 (GitHub Actions)

```yaml
# .github/workflows/build.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: python3 build_v10.py
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output/html
```

### 10.3 모니터링

```bash
# Google Search Console 등록
# 1. https://search.google.com/search-console
# 2. 속성 추가: balitravel.blog
# 3. sitemap.xml 제출: https://balitravel.blog/sitemap.xml
# 4. robots.txt 확인: https://balitravel.blog/robots.txt
```

---

## 부록 A: 새 나라 확장 체크리스트

### 확장 전

- [ ] 대상 나라 선정 (태국, 일본, 베트남 등)
- [ ] 도시 8~12개 선정
- [ ] 카테고리 6개 결정
- [ ] 제휴 파트너 확보 (마이리얼트립, 클룩 등)
- [ ] 도메인 확보 (jptravel-thailand.blog 등)

### 확장 중

- [ ] `build_{country}_data.py` 작성 (도시별 데이터)
- [ ] `build_{country}_engine.py` 작성 (콘텐츠 엔진)
- [ ] 이미지 스크래퍼 작성 및 실행
- [ ] `build_{country}.py` 작성 (빌드 스크립트)
- [ ] 빌드 실행 및 감사
- [ ] sitemap.xml 생성
- [ ] robots.txt 설정

### 확장 후

- [ ] GitHub 저장소 생성
- [ ] GitHub Pages 배포
- [ ] Google Search Console 등록
- [ ] sitemap.xml 제출
- [ ] 주간 감사 자동화

---

## 부록 B: 명령어 치트시트

```bash
# 프로젝트 클론
git clone https://ghp_TOKEN@github.com/kimfaraim-crypto/jptravel-bali.git

# 빌드
python3 build_v10.py

# 감사
./weekly_audit.sh

# 이미지 스크래핑
python3 scraper_bali_real_v2.py

# Git 푸시
git add -A && git commit -m "v10 업데이트" && git push

# 새 나라 생성
mkdir ../jptravel-thailand && cd ../jptravel-thailand
cp ../jptravel-bali/build_v10*.py .
# 데이터 파일 수정 후
python3 build_thailand.py
```

---

## 부록 C: 콘텐츠 작성 프롬프트 모음

### 프롬프트 1: 고유 인트로 (5가지 변형)

```
너는 {country}에서 {years}년간 거주한 여행 블로거야.
'{city}'의 '{category}'에 대한 블로그 첫 문장 5가지를 써줘.

조건:
- 200자 이내
- 개인 경험 포함
- 구체적 장소명/가격 언급
- AI 패턴 금지 ("안녕하세요", "오늘은", "핵심정보")
- "~해요", "~이에요" 체

출력 형식:
1. "첫 번째 문장"
2. "두 번째 문장"
3. "세 번째 문장"
4. "네 번째 문장"
5. "다섯 번째 문장"
```

### 프롬프트 2: 본문 문단 (장소 소개)

```
'{city}'의 '{category}'에 대한 여행 가이드 본문을 써줘.

장소 목록:
{items_json}

조건:
- 각 장소 2~3문장
- 구체적 가격, 주소, 전화번호
- 개인 경험 톤
- "~해요" 체
- 문장 시작 다양화
- 템플릿 문장 금지
```

### 프롬프트 3: FAQ (도시별 차별화)

```
'{city}'의 '{category}'에 대한 FAQ 3개를 만들어줘.

조건:
- 실제 여행자 질문
- 구체적 답변 (가격, 시간, 방법)
- 도시별로 다른 답변
- "~해요" 체
```

### 프롬프트 4: H2 제목 (5가지 변형)

```
'{city}'의 '{category}'에 대한 H2 제목 10개 × 5가지 변형을 만들어줘.

조건:
- 첫 H2: "{city} {category} [동사]" 형태
- 나머지: 질문형, 숫자형, 경험형, 가이드형 다양
- 고정 템플릿 금지
- 5가지 변형이 서로完全不同
```

---

> 이 문서를 기반으로 새 나라를 확장하면, 구글 Helpful Content 기준을 충족하는
> 고품질 여행 블로그를 빠르게 만들 수 있습니다.
> 
> 핵심: 데이터 → 이미지 → 콘텐츠 → 빌드 → 감사 → 배포
