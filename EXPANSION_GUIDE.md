# 확장 가이드 — 다른 나라 여행 블로그 생성

> 최종 업데이트: 2026-05-02

---

## 1. 확장 개요

이 시스템은 발리(Bali)에 최적화되어 있지만, 구조가 일반화되어 있어 **어떤 여행지**든 확장 가능합니다.

### 1.1 확장 가능한 나라 예시
| 나라 | 추천 지역 수 | 주요 카테고리 |
|------|-------------|---------------|
| 일본 (도쿄) | 10~15 | 음식, 문화, 쇼핑, 교통 |
| 태국 (방콕/푸켓) | 8~12 | 음식, 해변, 문화, 쇼핑 |
| 베트남 (하노이/호치민) | 8~10 | 음식, 문화, 자연, 교통 |
| 필리핀 (세부/보라카이) | 6~8 | 해변, 음식, 액티비티 |
| 유럽 (파리/로마) | 10~15 | 문화, 음식, 쇼핑 |
| 미국 (뉴욕/LA) | 10~15 | 음식, 쇼핑, 엔터테인먼트 |

---

## 2. 확장 절차

### 2.1 Step 1: 데이터 수집
```
[1] 대상 나라/도시 선정
[2] 주요 관광지 조사 (10~15개 지역)
[3] 카테고리 선정 (6개 권장)
[4] 각 지역별 맛집/명소/숙소/교통 데이터 수집
[5] 가격 데이터 수집 (현지 통화 + 원화 환율)
```

### 2.2 Step 2: 이미지 수집
```
[1] 이미지 스크래퍼 스크립트 복사 (scraper_*.py)
[2] 키워드를 대상 나라/도시에 맞게 수정
[3] Openverse/Flickr/Wikimedia에서 이미지 다운로드
[4] Perceptual Hash 중복 검사
[5] WebP 변환
[6] image_mapping_v3.json 업데이트
```

### 2.3 Step 3: 콘텐츠 데이터 작성
```
[1] build_bali.py의 BALI_DATA를 새 나라 데이터로 교체
[2] AREA_DATA (지역별 상세 정보) 작성
[3] QA_ANSWERS (Q&A 답변) 작성
[4] UNIQUE_TIPS (지역별 팁) 작성
[5] AREA_SECRETS (에피소드 + 블로거 팁) 작성
```

### 2.4 Step 4: 빌드 스크립트 수정
```
[1] build_bali.py에서 AREAS, CATEGORIES 수정
[2] AREA_SLUGS (URL 슬러그) 수정
[3] SITE_URL, AFFILIATE_URL 수정
[4] AUTHOR 정보 수정
```

### 2.5 Step 5: 빌드 실행
```
[1] python3 build_bali.py 실행
[2] 924개 HTML 자동 생성
[3] 이미지 경로 검증
[4] 콘텐츠 품질 검증
[5] GitHub 푸시
```

---

## 3. 새 나라 데이터 구조

### 3.1 BALI_DATA → {COUNTRY}_DATA
```python
# 예시: 일본 도쿄
TOKYO_DATA = {
    "시부야": {
        "name_kr": "시부야",
        "name_en": "Shibuya",
        "slug": "shibuya",
        "vibe": "젊은이의 거리",
        "spots": ["시부야 크로싱", "메이지 신궁", "하라주쿠", ...],
        "food": [
            {"name": "이치란 라멘", "price": "980엔~", "desc": "자판기 라멘"},
            ...
        ],
        "hotels": [
            {"name": "시부야 엑셀 호텔", "price": "15,000엔~/1박", "level": "중급"},
            ...
        ],
        "transport": {
            "airport": "3,000엔 (나리타 익스프레스 90분)",
            "local": "지하철 200엔~",
        },
    },
    # ... 10~15개 지역
}
```

### 3.2 AREA_DATA 구조 (지역별 상세)
```python
AREA_DATA = {
    "시부야": {
        "vibe": "젊은이의 거리",
        "must_eat": ["이치란 라멘", "스시로", "츠케멘"],
        "hidden_gem": "시부야 109 뒷골목 — 빈티지숍 천국",
        "local_tip": "시부야 크로싱은 오후 2~4시가 가장 한가해요",
        "transport_secret": "시부야역 JR 야마노테선으로 주요 관광지 이동 가능",
        "photo_spot": "시부야 크로싱 전망대 — 마그렛 위도우 빌딩 8층",
        "budget_meal": "마츠야 규동 — 500엔~",
        "splurge": "스시 사이토 — 30,000엔~",
        "avoid": "시부야역 하치코 출구는 출퇴근 시간에 매우 혼잡해요",
        "best_season": "3~5월 (벚꽃), 10~11월 (단풍)",
    },
    # ... 모든 지역
}
```

### 3.3 QA_ANSWERS 구조 (카테고리 × 지역)
```python
QA_ANSWERS = {
    "food": {
        "시부야": [
            "이치란 라멘 시부야점 추천이에요. 980엔~. 24시간 영업이에요.",
            "스시로는 가성비 스시 전문점이에요. 100엔~. 회전 스시예요.",
            ...
        ],
        "신주쿠": [
            "오모이데 요코초에서 야키토리 300엔~. 분위기 최고예요.",
            ...
        ],
        # ... 모든 지역
    },
    "culture": {
        "시부야": [
            "메이지 신궁은 무료 입장이에요. 아침에 가면 사람이 적어요.",
            ...
        ],
        # ... 모든 지역
    },
    # ... 모든 카테고리
}
```

### 3.4 AREA_SECRETS 구조 (에피소드 + 블로거 팁)
```python
AREA_SECRETS = {
    "시부야": {
        "episodes": [
            "시부야 크로싱에서 신호가 바뀌는 순간 수천 명이 동시에 걷는 모습을 봤어요. 그 장관을 잊을 수 없어요.",
            "시부야 109 뒷골목에서 빈티지 청재킷을 발견했는데, 2,000엔이었어요. 한국에서는 10만원짜리예요.",
            ...
        ],
        "blogger_tips": [
            "시부야 크로싱은 마그렛 위도우 빌딩 8층에서 내려다보는 게 가장 인상적이에요.",
            "시부야역 하치코 출구는 출퇴근 시간에 매우 혼잡해요. 다른 출구를 이용하세요.",
            ...
        ],
    },
    # ... 모든 지역
}
```

---

## 4. 이미지 확장 전략

### 4.1 키워드 변경
```python
# 기존 (발리)
SEARCH_KEYWORDS = {
    "우붓": {
        "food": ["ubud restaurant", "ubud food", "bali warung"],
        "nature": ["ubud rice terrace", "ubud waterfall"],
        ...
    },
}

# 확장 (도쿄)
SEARCH_KEYWORDS = {
    "시부야": {
        "food": ["shibuya restaurant", "shibuya ramen", "tokyo food"],
        "culture": ["meiji shrine", "shibuya temple"],
        ...
    },
}
```

### 4.2 이미지 매핑 확장
```json
{
    "시부야": {
        "food": ["시부야_food_0001.webp", ...],
        "culture": ["시부야_culture_0001.webp", ...],
        ...
    },
    "신주쿠": {
        ...
    }
}
```

---

## 5. 카테고리 커스터마이징

### 5.1 기본 6카테고리 (발리 기준)
| 카테고리 | 이름 | 아이콘 |
|----------|------|--------|
| food | 음식/맛집 | 🍜 |
| culture | 문화/사원 | 🛕 |
| beach | 해변/서핑 | 🏖️ |
| nature | 자연/모험 | 🌿 |
| shopping | 쇼핑/마사지 | 🛍️ |
| transport | 여행/교통 | 🚗 |

### 5.2 나라별 카테고리 조정
```
도쿄: food, culture, shopping, transport, entertainment, nature
방콕: food, culture, beach, shopping, nightlife, transport
파리: food, culture, shopping, art, nature, transport
뉴욕: food, culture, shopping, entertainment, nightlife, transport
```

### 5.3 카테고리 추가/삭제
```python
# build_bali.py의 CATEGORIES 수정
CATEGORIES = {
    "food": {"name": "음식/맛집", "icon": "🍜", "desc": "맛집 탐방", "en": "food"},
    "culture": {"name": "문화/사원", "icon": "🛕", "desc": "문화 체험", "en": "culture"},
    # ... 추가/삭제
}
```

---

## 6. 빌드 스크립트 수정 가이드

### 6.1 수정 파일 목록
| 파일 | 수정 내용 |
|------|-----------|
| build_bali.py | AREAS, CATEGORIES, BALI_DATA |
| build_bali_v7.py | AREA_SLUGS, SITE_URL, AFFILIATE_URL |
| content_generator_v7.py | AREA_DATA, QA_ANSWERS, UNIQUE_TIPS |
| improve_content.py | AREA_SECRETS |
| fix_rounds.py | QA_FULL (전 카테고리 Q&A) |
| improve_10rounds.py | AREA_SECRETS (에피소드 + 팁) |
| fix_final.py | cat_img_alts (이미지 alt 템플릿) |
| seo_titles.py | 제목 생성 규칙 |

### 6.2 수정 순서
```
[1] build_bali.py — BALI_DATA 작성
[2] content_generator_v7.py — AREA_DATA, QA_ANSWERS 작성
[3] build_bali_v7.py — AREA_SLUGS, SITE_URL 수정
[4] scraper_*.py — 이미지 키워드 수정
[5] 이미지 다운로드 + 매핑
[6] python3 build_bali.py 실행
[7] improve_content.py 실행
[8] fix_rounds.py 실행
[9] improve_10rounds.py 실행
[10] fix_final.py 실행
[11] 검증 + 푸시
```

---

## 7. 멀티 나라 시스템

### 7.1 디렉토리 구조
```
jptravel/
├── bali/                  ← 발리 (기존)
│   ├── build_bali.py
│   ├── output/
│   │   ├── html/bali/
│   │   └── images/
│   └── ...
├── tokyo/                 ← 도쿄 (확장)
│   ├── build_tokyo.py
│   ├── output/
│   │   ├── html/tokyo/
│   │   └── images/
│   └── ...
├── bangkok/               ← 방콕 (확장)
│   └── ...
└── shared/                ← 공유 코드
    ├── scraper.py         ← 이미지 스크래퍼 (공통)
    ├── content_gen.py     ← 콘텐츠 생성기 (공통)
    └── templates/         ← HTML 템플릿 (공통)
```

### 7.2 공통 코드 추출
```python
# shared/base_builder.py
class TravelBlogBuilder:
    """여행 블로그 빌더 기본 클래스"""
    
    def __init__(self, country, areas, categories):
        self.country = country
        self.areas = areas
        self.categories = categories
    
    def build(self):
        for area in self.areas:
            for cat in self.categories:
                for page in range(1, 15):
                    self.generate_html(area, cat, page)
    
    def generate_html(self, area, cat, page):
        # 공통 HTML 생성 로직
        pass

# bali/build_bali.py
from shared.base_builder import TravelBlogBuilder

class BaliBlogBuilder(TravelBlogBuilder):
    def __init__(self):
        super().__init__(
            country="bali",
            areas=["우붓", "스미냑", ...],
            categories=["food", "culture", ...]
        )
    
    # 발리 전용 오버라이드
```

---

## 8. 확장 체크리스트

### 8.1 데이터 수집
- [ ] 대상 나라/도시 선정
- [ ] 10~15개 지역 선정
- [ ] 6개 카테고리 선정
- [ ] 각 지역별 맛집 5~10개 수집
- [ ] 각 지역별 명소 5~10개 수집
- [ ] 각 지역별 숙소 3~5개 수집
- [ ] 각 지역별 교통 정보 수집
- [ ] 각 지역별 가격 데이터 수집
- [ ] 환율 정보 업데이트

### 8.2 이미지
- [ ] 이미지 키워드 작성 (영어)
- [ ] Openverse/Flickr에서 이미지 다운로드
- [ ] Perceptual Hash 중복 검사
- [ ] WebP 변환
- [ ] image_mapping.json 작성
- [ ] 이미지-카테고리 매핑 검증

### 8.3 콘텐츠
- [ ] BALI_DATA → {COUNTRY}_DATA 작성
- [ ] AREA_DATA 작성 (지역별 상세)
- [ ] QA_ANSWERS 작성 (66개 조합)
- [ ] UNIQUE_TIPS 작성 (66개 조합)
- [ ] AREA_SECRETS 작성 (에피소드 + 팁)
- [ ] SEO 제목 템플릿 작성

### 8.4 빌드
- [ ] 빌드 스크립트 수정
- [ ] 빌드 실행
- [ ] 이미지 경로 검증
- [ ] 콘텐츠 품질 검증
- [ ] GitHub 푸시

### 8.5 배포
- [ ] 도메인 설정
- [ ] 사이트맵 제출 (네이버, 구글)
- [ ] robots.txt 설정
- [ ] 파트너스 링크 설정
