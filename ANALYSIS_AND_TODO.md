# JP Travel Bali — 분석 및 개선 TODO

**작성일:** 2026-05-02
**현재 상태:** 3,421장 이미지 / 924개 HTML / 11지역 × 6카테고리

---

## ✅ 완료된 작업

### 1. HTML 빌드 시스템 (v6 — 최신)
- **924개 고유 HTML** (11지역 × 6카테고리 × 14페이지)
- `build_bali_v6.py` — 대폭 개선된 빌드 스크립트
  - 제목: 30가지 변형 템플릿 → 924개 전부 고유 ✅
  - 메타 설명: 20가지 변형 → 페이지별 고유 ✅
  - OG 이미지: 실제 이미지 경로로 동적 생성 ✅
  - 내부 링크: 지리적 근접성 기반 (랜덤 대체) ✅
  - 쿠폰 중복 제거: 상단 1회만 표시 ✅

### 2. 인프라 파일
- `index.html` — 11지역 카드형 인덱스 페이지 ✅
- `sitemap.xml` — 924개 URL 자동 생성 ✅
- `robots.txt` — Googlebot/NaverBot 허용 ✅

### 3. 이미지 시스템
- **총 3,421장** (WebP 포맷)
- 우붓: 885장 (6카테고리 전부 137~150장)
- 스미냑: 571장 (일부 보충 완료)
- 꾸따~베두굴: 각 60~123장 (보충 진행 중)

### 4. 스크래퍼 버전
| 버전 | 파일 | 특징 |
|------|------|------|
| v4 | `scraper_multi.py` | 기본 4소스, 10장/조합 |
| v5 | `scraper_enhanced.py` | 확장 키워드, 150장 목표 |
| v7 | `scraper_mega.py` | Openverse+Flickr+Wikimedia+Picsum |
| **v9** | **`scraper_unique.py`** | **MD5 전역중복차단 + pHash 조합내중복차단** ← 현재 최신 |

### 5. SEO/콘텐츠 전략
- `naver_prompt.txt` — 네이버 Cue: 최적화 전략 문서 ✅
- `seo_titles.py` — SEO 제목 생성기 ✅
- `content_generator.py` — AI 콘텐츠 생성 프롬프트 ✅

### 6. 버그 수정
- 중국어 `猴子` → `원숭이` 수정 ✅
- 중복 이미지 236장 삭제 ✅
- 파일 해시 DB 2,750개 등록 ✅

---

## 🚨 현재 문제점

### Critical
1. **이미지 부족 (3,421/9,000)** — 목표 대비 38% 달성
   - 원인: Flickr/Wikimedia만으로는 발리 고유 이미지 9,000장 확보 불가
   - Openverse API가 Cloudflare 차단으로 사용 불가
   - Picsum은 발리 사진이 아닌 랜덤 이미지

2. **카테고리 간 이미지 유사도** — perceptual hash로 필터링했으나, 비슷한 배경/구도의 발리 사진이 카테고리별로 다를 수 있음
   - food 카테고리의 사진 중 beach 배경이 포함될 수 있음
   - 해결: 이미지 분류 AI 도입 또는 수동 검수 필요

### Major
3. **콘텐츠가 템플릿 기반** — AI 생성 콘텐츠가 아니라 템플릿 변형
   - 같은 조합 내 유사도 약 30~40%
   - MiMo 모델 연동으로 고유 글 생성 필요

4. **Picsum fallback 품질** — 발리와 무관한 랜덤 사진
   - 실전 배포 전 Picsum 이미지 전부 교체 필요

5. **일부 조합 데이터 부족**
   - 스미냑/nature: 1개 → 69개 (보충됨)
   - 누사두아/nature: 0개 (데이터 자체가 없음)
   - 짠디다사/로비나/킨타마니: 카테고리별 데이터 적음

### Minor
6. **이미지 파일명에 한글 포함** — URL 인코딩 이슈 가능
   - 현재: `우붓_food_0001.webp`
   - 개선: `ubud_food_0001.webp` (영문 slug 사용)

7. **robots.txt/Sitemap 실제 배포 필요** — 현재 파일만 생성, 서버 배포 안 됨

---

## 📋 다음 개선 TODO

### Phase 1: 이미지 확장 (우선순위 1)
- [ ] `scraper_unique.py` 재실행하여 3,421 → 9,000장 확보
  - Flickr 키워드 더 확장 (지역별 20개 이상)
  - Wikimedia 검색어 다양화
  - Unsplash/Pexels API 키즈 확보 시 추가
- [ ] Picsum 이미지 → 실제 발리 사진으로 교체
- [ ] 저해상도 이미지 필터링 강화 (최소 800×600)

### Phase 2: 콘텐츠 품질 (우선순위 2)
- [ ] MiMo 모델 연동 고유 글 생성
  - `content_generator.py` 완성
  - 924개 페이지별 고유 에세이 생성
  - 네이버 Cue: 최적화 구조 유지
- [ ] SEO 제목 더 다양화 (현재 30개 → 50개 이상)
- [ ] 메타 description 품질 개선 (현재 템플릿 → 실제 내용 반영)

### Phase 3: 기능 추가 (우선순위 3)
- [ ] 반응형 이미지 (srcset, WebP fallback for older browsers)
- [ ] 페이지 로딩 속도 최적화 (CSS/JS 번들링, lazy loading)
- [ ] 내부 링크 시스템 강화 (관련 글 추천 알고리즘)
- [ ] 이미지 파일명 영문화 (`우붓_food_0001.webp` → `ubud_food_0001.webp`)

### Phase 4: 배포 (우선순위 4)
- [ ] GitHub Pages 또는 Vercel/Netlify 배포
- [ ] Google Search Console 등록
- [ ] 네이버 웹마스터도구 등록
- [ ] 트래픽 모니터링 설정
- [ ] 가격 정보 주기적 업데이트 (월 1회)

### Phase 5: 고급 기능 (우선순위 5)
- [ ] 다크모드 지원
- [ ] 다국어 지원 (영어, 일본어)
- [ ] 댓글 시스템 연동
- [ ] 뉴스레터 구독
- [ ] PWA 지원

---

## 🔧 실행 방법

```bash
# 이미지 스크래핑 (v9 — 고유 이미지 전용)
python3 scraper_unique.py

# HTML 빌드 (v6 — 최신)
python3 build_bali_v6.py

# 매핑 재생성
python3 -c "
import json
from pathlib import Path
OUTPUT = Path('output/images')
mapping = {}
for ad in OUTPUT.iterdir():
    if not ad.is_dir(): continue
    mapping[ad.name] = {}
    for cd in ad.iterdir():
        if not cd.is_dir(): continue
        mapping[ad.name][cd.name] = sorted([f.name for f in cd.glob('*.webp')])
Path('image_mapping_v3.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
print(f'총 이미지: {sum(len(v) for cats in mapping.values() for v in cats.values())}장')
"
```

---

## 📊 파일 구조

```
jptravel-bali/
├── build_bali.py           ← v3 빌드 (기본 데이터)
├── build_bali_v5.py        ← v5 빌드 (고유 콘텐츠)
├── build_bali_v6.py        ← v6 빌드 (최신 — SEO/OG/인덱스 개선) ← 현재 사용
├── scraper_multi.py        ← v4 스크래퍼
├── scraper_enhanced.py     ← v5 스크래퍼
├── scraper_mega.py         ← v7 스크래퍼
├── scraper_unique.py       ← v9 스크래퍼 (최신 — 고유 이미지 전용) ← 현재 사용
├── seo_titles.py           ← SEO 제목 생성기
├── content_generator.py    ← AI 콘텐츠 생성 프롬프트
├── naver_prompt.txt        ← 네이버 Cue: 최적화 전략
├── image_mapping_v3.json   ← 이미지 매핑
├── file_hashes.json        ← 전역 MD5 해시 DB (중복 방지)
├── ANALYSIS_AND_TODO.md    ← 이 파일
├── PROGRESS.md             ← 진행 상황
├── mrt_coupon.jpg          ← 마이리얼트립 쿠폰
└── output/
    ├── html/bali/          ← 924개 HTML
    ├── images/             ← 3,421장 이미지
    ├── sitemap.xml         ← 사이트맵
    ├── robots.txt          ← robots
    └── index.html          ← 인덱스
```
