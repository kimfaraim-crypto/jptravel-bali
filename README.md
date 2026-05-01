# JP Travel Bali — 발리 여행 블로그

발리 여행 블로그 자동 생성 시스템

## 개요

- **924개 HTML 페이지** (11개 지역 × 6개 카테고리 × 14개)
- **네이버 AI 검색(Cue:) 최적화**
- **마이리얼트립 제휴 링크 시스템**
- **도시별 고유 콘텐츠** (실제 식당, 가격, 교통 정보)
- **다중 소스 이미지** (Openverse, Flickr, Wikimedia, Picsum)

## 지역

우붓, 스미냑, 꾸따, 사누르, 누사두아, 울루와뚜, 짠디다사, 로비나, 킨타마니, 타나롯, 베두굴

## 카테고리

- 🍜 음식/맛집
- 🛕 문화/사원
- 🏖️ 해변/서핑
- 🌿 자연/모험
- 🛍️ 쇼핑/마사지
- 🚗 여행/교통

## 빌드

```bash
python3 build_bali.py
```

## 이미지 스크래핑

```bash
python3 scraper_multi.py
```

## 구조

```
jptravel-bali/
├── .env                  ← 환경 변수
├── build_bali.py         ← 빌드 스크립트
├── scraper_multi.py      ← 이미지 스크래퍼
├── seo_titles.py         ← SEO 제목 생성기
├── mrt_coupon.jpg        ← 마이리얼트립 쿠폰 이미지
├── naver_prompt.txt      ← 네이버 AI 검색 프롬프트
├── output/
│   ├── html/bali/        ← 924개 HTML
│   └── images/           ← 지역별 이미지
└── image_mapping_v3.json ← 이미지 매핑
```

## 제휴 링크

- 할인쿠폰: https://myrealt.rip/YuJbb5
- 투어/티켓: https://myrealt.rip/YoEc1b
