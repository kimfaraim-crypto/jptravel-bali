# JP Travel Bali — 시스템 아키텍처 및 구조 문서

> 최종 업데이트: 2026-05-02
> 프로젝트: 발리 여행 블로그 자동 생성 시스템
> GitHub: https://github.com/kimfaraim-crypto/jptravel-bali

---

## 1. 프로젝트 개요

### 1.1 목적
- 네이버 AI 검색(Cue:) 최적화 발리 여행 콘텐츠 자동 생성
- 11개 지역 × 6개 카테고리 × 14페이지 = **924개 HTML 페이지**
- 각 페이지당 **10개 고유 이미지** 포함
- 총 **5,138개 고유 이미지** (WebP 형식)
- 마이리얼트립 파트너스 제휴 수익 모델

### 1.2 기술 스택
| 구분 | 기술 |
|------|------|
| 언어 | Python 3.12 |
| 이미지 형식 | WebP (품질 80, 최소 1200×800) |
| 마크업 | HTML5 + CSS3 (반응형) |
| SEO | Schema.org Article, Open Graph, canonical URL |
| 데이터 | JSON (이미지 매핑, 해시 DB) |
| 이미지 소스 | Openverse API, Flickr, Wikimedia Commons |
| 버전 관리 | Git + GitHub |

### 1.3 현재 규모
| 항목 | 수치 |
|------|------|
| HTML 페이지 | 924개 |
| 지역 | 11개 |
| 카테고리 | 6개 |
| 페이지/조합 | 14개 |
| 총 이미지 | 5,138개 |
| 고유 이미지 | 5,138개 (중복 0) |
| 총 이미지 용량 | 648.9MB |
| 평균 이미지 크기 | 129.3KB |

---

## 2. 디렉토리 구조

```
jptravel-bali/
├── build_bali.py                ← 메인 빌드 스크립트 (BALI_DATA 정의)
├── build_bali_v5.py             ← 이전 버전 (보관)
├── build_bali_v6.py             ← 이전 버전 (보관)
├── build_bali_v7.py             ← 최신 빌드 스크립트 (924 HTML 생성)
├── content_generator.py         ← 콘텐츠 생성기 (기본)
├── content_generator_v7.py      ← 콘텐츠 생성기 v7 (고품질)
├── seo_titles.py                ← SEO 제목/메타 설명 생성기
├── seo_titles_v2.py             ← SEO v2 (해시 버그 수정)
├── scraper_enhanced.py          ← 이미지 스크래퍼 (Openverse/Flickr)
├── scraper_expanded.py          ← 확장 스크래퍼
├── scraper_mega.py              ← 메가 스크래퍼
├── scraper_multi.py             ← 멀티소스 스크래퍼
├── scraper_unique.py            ← 고유 이미지 전용 스크래퍼
├── scraper_bali_real.py         ← 실제 발리 이미지 스크래퍼
├── scraper_bali_real_v2.py      ← 실제 발리 이미지 스크래퍼 v2
├── scraper_real_bali.py         ← 실제 발리 이미지 스크래퍼 v3
├── image_scraper_v8.py          ← 이미지 스크래퍼 v8
├── scrape_flickr.py             ← Flickr 전용 스크래퍼
├── scrape_cn_sites.py           ← 중국 사이트 스크래퍼
├── scrape_real_images.py        ← 실제 이미지 스크래퍼
├── scraper_replace_picsum.py    ← Picsum 교체 스크래퍼
├── fill_shortages.py            ← 이미지 부족분 보충
├── fast_expand.py               ← 고속 이미지 확장 v1
├── fast_expand2.py              ← 고속 이미지 확장 v2
├── fast_expand3.py              ← 고속 이미지 확장 v3
├── replace_images.py            ← 이미지 교체 스크립트
├── merge_real_images.py         ← 실제 이미지 병합
├── improve_content.py           ← 콘텐츠 품질 개선 스크립트
├── fix_rounds.py                ← 3라운드 수정 스크립트
├── improve_10rounds.py          ← 10라운드 개선 스크립트
├── fix_final.py                 ← 최종 수정 스크립트
├── image_mapping_v3.json        ← 이미지 매핑 (지역→카테고리→파일명)
├── image_hashes_v7.json         ← perceptual hash DB v7
├── global_image_hashes.json     ← 전역 이미지 해시 DB
├── global_hashes_real.json      ← 실제 이미지 해시 DB
├── file_hashes.json             ← 파일 해시 DB
├── mrt_coupon.jpg               ← 마이리얼트립 쿠폰 이미지
├── naver_prompt.txt             ← 네이버 AI 검색 프롬프트
├── .gitignore                   ← Git 무시 파일
├── ARCHITECTURE.md              ← 이 파일
├── IMAGE_STRATEGY.md            ← 이미지 전략서
├── CONTENT_STRATEGY.md          ← 콘텐츠 전략서
├── EXPANSION_GUIDE.md           ← 확장 가이드
├── CATEGORY_REFERENCE.md        ← 카테고리 참조서
├── ANALYSIS_REPORT.md           ← 분석 보고서
├── DESCRIPTION.md               ← 상세 설명서
├── PLAN.md                      ← 계획서
├── REVISION_LOG.md              ← 수정 로그
├── IMPROVEMENT_PLAN.md          ← 개선 계획
├── SEO_STRATEGY.md              ← SEO 전략
├── IMAGE_SCRAPING_GUIDE.md      ← 이미지 스크래핑 가이드
├── PROGRESS.md                  ← 진행 현황
├── PROGRESS_REPORT.md           ← 진행 보고서
├── README.md                    ← 프로젝트 README
├── output/
│   ├── html/
│   │   ├── bali/                ← 924개 HTML (11지역/6카테고리/14페이지)
│   │   │   ├── 우붓/
│   │   │   │   ├── food/        ← 001~014.html
│   │   │   │   ├── culture/
│   │   │   │   ├── beach/
│   │   │   │   ├── nature/
│   │   │   │   ├── shopping/
│   │   │   │   └── transport/
│   │   │   ├── 스미냑/
│   │   │   ├── 꾸따/
│   │   │   ├── 사누르/
│   │   │   ├── 누사두아/
│   │   │   ├── 울루와뚜/
│   │   │   ├── 짠디다사/
│   │   │   ├── 로비나/
│   │   │   ├── 킨타마니/
│   │   │   ├── 타나롯/
│   │   │   └── 베두굴/
│   │   └── images/
│   │       └── mrt_coupon.jpg   ← 쿠폰 이미지 (상대 경로용)
│   └── images/                  ← 5,138개 WebP 이미지
│       ├── 우붓/
│       │   ├── food/            ← 우붓_food_0001.webp ~
│       │   ├── culture/
│       │   ├── beach/
│       │   ├── nature/
│       │   ├── shopping/
│       │   └── transport/
│       ├── 스미냑/
│       ├── 꾸따/
│       ├── 사누르/
│       ├── 누사두아/
│       ├── 울루와뚜/
│       ├── 짠디다사/
│       ├── 로비나/
│       ├── 킨타마니/
│       ├── 타나롯/
│       └── 베두굴/
└── images_real/                 ← 실제 발리 이미지 (보관)
```

---

## 3. 빌드 시스템

### 3.1 빌드 흐름
```
[1] BALI_DATA 정의 (build_bali.py)
    ↓
[2] 이미지 매핑 로드 (image_mapping_v3.json)
    ↓
[3] SEO 제목 생성 (seo_titles_v2.py)
    ↓
[4] 콘텐츠 생성 (content_generator_v7.py)
    ↓
[5] 이미지 배분 (Fisher-Yates 시드 셔플)
    ↓
[6] HTML 렌더링 (924개 파일)
    ↓
[7] 사이트맵/robots.txt 생성
```

### 3.2 핵심 데이터 구조 — BALI_DATA
```python
BALI_DATA = {
    "우붓": {
        "name_kr": "우붓",
        "name_en": "Ubud",
        "slug": "ubud",
        "vibe": "예술가 마을",
        "spots": ["테갈랑 라이스 테라스", "원숭이 숲", "우붓 아트 마켓", ...],
        "food": [
            {"name": "Bebek Bengil", "price": "95,000Rp~", "desc": "바삭한 크리스피덕"},
            ...
        ],
        "hotels": [
            {"name": "알리라 우붓", "price": "3,000,000Rp~/1박", "level": "고급"},
            ...
        ],
        "transport": {
            "airport": "300,000Rp (차량 90분)",
            "local": "스쿠터 80,000Rp/일",
        },
    },
    # ... 11개 지역
}
```

### 3.3 HTML 페이지 구조
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <!-- SEO 메타태그 -->
    <title>{지역} {카테고리} 완벽 가이드 — 가격·위치·팁 총정리 (2026)</title>
    <meta name="description" content="...">
    <link rel="canonical" href="...">
    <meta property="og:title" content="...">
    <meta property="og:image" content="...">
    <script type="application/ld+json">{"@type": "Article", ...}</script>
</head>
<body>
    <div id="reading-progress"></div>           <!-- 읽기 진행률 -->
    <div>파트너스 고지문</div>                   <!-- 광고 고지 -->
    <header>제목 + 메타정보</header>
    <article>
        <div class="content-intro">도입부</div>  <!-- Hook -->
        <div>쿠폰 이미지</div>                   <!-- 제휴 링크 -->
        <figure>이미지 10장 + figcaption</figure>
        <h2>❓ 자주 묻는 질문</h2>              <!-- Q&A 4개 -->
        <h2>📍 추천 장소 상세</h2>              <!-- 장소 5개 -->
        <h2>💰 가격 비교</h2>                   <!-- 가격표 -->
        <h2>🗺️ 추천 명소</h2>                   <!-- 명소 리스트 -->
        <h2>💎 숨은 명소</h2>                    <!-- 숨은 명소 -->
        <h2>🚗 교통 정보</h2>                    <!-- 교통표 -->
        <h2>🏨 숙소 추천</h2>                    <!-- 숙소표 -->
        <h2>💰 예산 가이드</h2>                  <!-- 예산 + 일정 -->
        <h2>🔑 현지인 꿀팁</h2>                  <!-- 꿀팁 -->
        <h2>💡 실전 팁</h2>                      <!-- 팁 5개 -->
        <h2>📝 여행 에피소드</h2>                <!-- 에피소드 -->
        <h2>🔗 관련 지역 링크</h2>               <!-- 내부 링크 -->
        <div class="tags">태그</div>
        <div class="content-footer">마무리</div>
    </article>
    <footer>저작권 + 파트너스 고지</footer>
</body>
</html>
```

---

## 4. 이미지 시스템

### 4.1 이미지 소스
| 소스 | 용도 | API |
|------|------|------|
| Openverse | 주요 이미지 소스 | REST API |
| Flickr | 보조 이미지 소스 | REST API |
| Wikimedia Commons | 보조 이미지 소스 | REST API |
| Picsum Photos | fallback (이전 버전) | URL 기반 |

### 4.2 이미지 처리 파이프라인
```
[1] 키워드 생성 (지역 + 카테고리 + 영어)
    ↓
[2] API 호출 (Openverse/Flickr/Wikimedia)
    ↓
[3] 다운로드 (64 스레드 병렬, ~80개/초)
    ↓
[4] Perceptual Hash 계산 (8×8 그레이스케일 → 64비트)
    ↓
[5] 중복 검사 (해밍거리 ≤5 → 중복 판정)
    ↓
[6] WebP 변환 (품질 80, 최소 1200×800)
    ↓
[7] 매핑 업데이트 (image_mapping_v3.json)
    ↓
[8] 파일 저장 (output/images/{지역}/{카테고리}/)
```

### 4.3 이미지 파일명 규칙
```
{지역}_{카테고리}_{일련번호}.webp

예시:
- 우붓_food_0001.webp
- 스미냑_beach_0045.webp
- 꾸따_culture_0157.webp
```

### 4.4 이미지 배분 알고리즘 (Fisher-Yates 시드 셔플)
```python
def seeded_shuffle(lst, seed_str):
    """Deterministic Fisher-Yates shuffle"""
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    result = list(lst)
    rng = seed_val
    for i in range(len(result) - 1, 0, -1):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        j = rng % (i + 1)
        result[i], result[j] = result[j], result[i]
    return result

# 사용법:
# {지역}_{카테고리}_{페이지인덱스}_img_v7 시드로 셔플
# → 같은 지역/카테고리의 14페이지가 모두 다른 10개 이미지 배치
```

### 4.5 Perceptual Hash 중복 검사
```python
def perceptual_hash(image_path):
    """8×8 그레이스케일 → 64비트 해시"""
    img = Image.open(image_path).convert('L').resize((8, 8))
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = ''.join('1' if p > avg else '0' for p in pixels)
    return int(bits, 2)

def is_duplicate(hash1, hash2, threshold=5):
    """해밍거리 ≤5 → 중복 판정"""
    return bin(hash1 ^ hash2).count('1') <= threshold
```

---

## 5. 콘텐츠 시스템

### 5.1 콘텐츠 생성 흐름
```
[1] BALI_DATA에서 지역/카테고리 데이터 로드
    ↓
[2] SEO 제목 생성 (지역 + 카테고리 + 페이지번호 + 연도)
    ↓
[3] Hook 인트로 생성 (5가지 템플릿 랜덤)
    ↓
[4] Q&A 생성 (4개, 카테고리별 고유 답변)
    ↓
[5] 추천 장소 생성 (5개, 가격/위치/팁/추천메뉴)
    ↓
[6] 가격 비교표 생성 (로컬 vs 투어 vs 호텔)
    ↓
[7] 교통 정보표 생성
    ↓
[8] 숙소 추천표 생성
    ↓
[9] 예산 가이드 + 추천 일정 생성
    ↓
[10] 현지인 꿀팁 + 실전 팁 생성
    ↓
[11] 여행 에피소드 생성 (지역별 고유)
    ↓
[12] 관련 지역 링크 생성
    ↓
[13] 태그 + 마무리 생성
```

### 5.2 제목 생성 규칙
```
{지역} {카테고리명} {_suffix} — {편번호}편 ({연도})

_suffix 매핑:
- 001: 핵심 코스
- 002: 숨은 명소
- 003: 가성비 추천
- 004: 현지인 팁
- 005: 포토스팟
- 006: 액티비티
- 007: 힐링 코스
- 008: 맛집 투어
- 009: 쇼핑 가이드
- 010: 교통 정보
- 011: 숙소 추천
- 012: 예산 정리
- 013: 일정 추천
- 014: 종합 가이드
```

### 5.3 콘텐츠 품질 기준
| 항목 | 기준 |
|------|------|
| 글자 수 | 1,500자 이상 |
| Q&A 답변 | 같은 페이지 내 중복 없음 |
| 블로거 팁 | 모든 페이지에 존재, 장소별 고유 |
| 에피소드 | 지역별 고유 경험담 |
| 가격 정보 | Rp + 원화 병기 |
| 이미지 alt | 10개 모두 고유 |
| figcaption | 모든 이미지에 존재 |
| 읽기 시간 | 모든 페이지에 표시 |
| 예산 일정 | 모든 예산 가이드에 포함 |

---

## 6. SEO 시스템

### 6.1 메타태그 구조
```html
<title>{지역} {카테고리} 완벽 가이드 — 가격·위치·팁 총정리 (2026)</title>
<meta name="description" content="{지역} {카테고리} 여행 정보. {지역} {핵심키워드}. 가격 비교. 2026년 기준 최신 후기.">
<meta name="keywords" content="{지역} {키워드1}, {지역} {키워드2}, 발리, 인도네시아, 자유여행, 2026">
<link rel="canonical" href="https://balitravel.blog/{slug}/{cat}/{page}.html">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="https://balitravel.blog/images/{area}/{cat}/{first_image}.webp">
<meta property="og:type" content="article">
```

### 6.2 Schema.org 마크업
```json
{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "...",
    "description": "...",
    "image": ["..."],
    "datePublished": "2026-04-01",
    "dateModified": "2026-04-01",
    "author": {"@type": "Person", "name": "발리 여행 10년차 블로거"},
    "publisher": {"@type": "Organization", "name": "발리 여행 블로그"},
    "mainEntityOfPage": {"@type": "WebPage", "@id": "..."}
}
```

---

## 7. 성능 지표

| 지표 | 값 |
|------|-----|
| HTML 빌드 시간 | ~60초 (924페이지) |
| 이미지 다운로드 속도 | ~80개/초 (64 스레드) |
| 이미지 평균 크기 | 129.3KB (WebP) |
| 총 이미지 용량 | 648.9MB |
| Perceptual hash 검사 | ~1000건/초 |

---

## 8. 보안

- `.gitignore`: `.env`, `__pycache__`, `*.pyc` 제외
- API 키: `.env` 파일에 저장 (git 추적 제외)
- 제휴 링크: HTML에 하드코딩
- 외부 이미지: Openverse/Flickr/Wikimedia (오픈 라이선스)
