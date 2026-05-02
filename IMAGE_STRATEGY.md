# 이미지 전략서 — JP Travel Bali

> 최종 업데이트: 2026-05-02

---

## 1. 이미지 수집 전략

### 1.1 소스 우선순위
| 순위 | 소스 | 장점 | 단점 |
|------|------|------|------|
| 1 | Openverse API | 대량 수집, 오픈 라이선스 | 품질 편차 |
| 2 | Flickr API | 고품질 사진 많음 | API 제한 |
| 3 | Wikimedia Commons | 무료, 고품질 | 발리 사진 제한적 |
| 4 | Picsum Photos | 빠르고 안정적 | 랜덤 사진 (장소 무관) |

### 1.2 검색 키워드 전략
```
지역명(영어) + 카테고리(영어) + 확장 키워드

예시:
- "ubud rice terrace" (우붓 + 자연)
- "seminyak beach sunset" (스미냑 + 해변)
- "kuta surfing" (꾸따 + 해변)
- "uluwatu temple" (울루와뚜 + 문화)
- "bali food warung" (발리 + 음식)
- "nusa dua resort" (누사두아 + 쇼핑)
```

### 1.3 키워드 테이블 (지역 × 카테고리)
| 지역 | food | culture | beach | nature | shopping | transport |
|------|------|---------|-------|--------|----------|-----------|
| 우붓 | ubud restaurant food | ubud temple | - | ubud rice terrace waterfall | ubud art market | ubud scooter |
| 스미냑 | seminyak cafe restaurant | seminyak temple | seminyak beach sunset | - | seminyak boutique spa | seminyak taxi |
| 꾸따 | kuta warung food | kuta art market | kuta beach surfing | - | kuta beachwalk mall | kuta airport |
| 사누르 | sanur warung seafood | sanur museum | sanur beach sunrise | - | sanur art market | sanur bicycle |
| 누사두아 | nusa dua restaurant | nusa dua theater | nusa dua beach | - | nusa dua collection | nusa dua shuttle |
| 울루와뚜 | uluwatu cafe | uluwatu temple kecak | uluwatu beach surf | - | uluwatu souvenir | uluwatu taxi |
| 짠디다사 | candidasa warung | besakih temple | candidasa beach | agung volcano | candidasa market | candidasa car |
| 로비나 | lovina seafood | lovina temple | lovina beach dolphin | - | lovina market | lovina car |
| 킨타마니 | kintamani restaurant | kintamani temple | - | batur volcano trek | kintamani market | kintamani car |
| 타나롯 | tanah lot market | tanah lot temple | tanah lot beach | - | tanah lot market | tanah lot car |
| 베두굴 | bedugul market | ulun danu temple | - | bedugul botanical | bedugul market | bedugul car |

---

## 2. 이미지 처리 파이프라인

### 2.1 다운로드
```python
# 64 스레드 병렬 다운로드
# ~80개/초 속도
# 타임아웃: 10초/이미지
# 재시도: 3회
```

### 2.2 품질 필터
```
[1] 최소 크기: 1200×800 픽셀
[2] 최소 파일 크기: 10KB
[3] 최대 파일 크기: 5MB
[4] 형식: JPG, PNG, WebP 지원
[5] 손상 파일 검사: 파일 헤더 확인
```

### 2.3 중복 검사 (Perceptual Hash)
```python
# 8×8 그레이스케일 → 64비트 해시
# 해밍거리 ≤5 → 중복 판정
# 같은 지역 내 카테고리 간 중복도 검사
# 전역 해시 DB로 크로스-지역 중복도 방지
```

### 2.4 WebP 변환
```python
# 품질: 80
# 최소 크기: 1200×800 (작으면 리사이즈)
# 최대 크기: 원본 유지 (확대 없음)
# 메타데이터: 제거 (용량 절약)
```

### 2.5 파일명 규칙
```
{지역}_{카테고리}_{4자리 일련번호}.webp

예시:
- 우붓_food_0001.webp
- 스미냑_beach_0045.webp
- 꾸따_culture_0157.webp

일련번호는 0001부터 시작, 순차 증가
```

---

## 3. 이미지 매핑 시스템

### 3.1 매핑 파일 구조 (image_mapping_v3.json)
```json
{
    "우붓": {
        "food": ["우붓_food_0001.webp", "우붓_food_0002.webp", ...],
        "culture": ["우붓_culture_0001.webp", ...],
        "beach": ["우붓_beach_0001.webp", ...],
        "nature": ["우붓_nature_0001.webp", ...],
        "shopping": ["우붓_shopping_0001.webp", ...],
        "transport": ["우붓_transport_0001.webp", ...]
    },
    // ... 11개 지역
}
```

### 3.2 이미지 배분 알고리즘
```python
# Fisher-Yates 시드 셔플
# 시드: "{지역}_{카테고리}_{페이지인덱스}_img_v7"
# → 같은 시드 → 항상 같은 순서 (결정적)
# → 14페이지 × 10장 = 140개 필요
# → 실제 이미지가 140개 미만이면 다른 카테고리에서 보충

def get_images(area, category, page_idx, count=10):
    # 1. 해당 카테고리에서 이미지 로드
    # 2. 부족하면 같은 지역 다른 카테고리에서 보충
    # 3. still 부족하면 파일시스템에서 직접 검색
    # 4. Fisher-Yates 시드 셔플 → page_idx별 다른 10장
    # 5. 부족하면 순환 배분
```

### 3.3 이미지-페이지 매칭 보장
- 같은 지역/카테고리 14페이지: 모두 다른 10장 이미지
- 같은 지역 다른 카테고리: 이미지 공유 가능 (보충 시)
- 다른 지역: 이미지 완전 독립

---

## 4. 이미지 품질 기준

### 4.1 해상도
| 기준 | 값 |
|------|-----|
| 최소 너비 | 1200px |
| 최소 높이 | 800px |
| 권장 비율 | 3:2 또는 4:3 |
| 최대 크기 | 제한 없음 |

### 4.2 파일 크기
| 기준 | 값 |
|------|-----|
| 최소 | 10KB |
| 평균 | 129.3KB |
| 최대 | 5MB |
| 목표 | 50~200KB |

### 4.3 WebP 품질 설정
```python
quality = 80        # 품질 (0~100)
method = 4          # 압축 방법 (0~6, 높을수록 느리지만 작음)
target_size = None  # 목표 크기 (자동)
alpha_compression = True  # 알파 채널 압축
```

---

## 5. 이미지 통계

### 5.1 지역별 이미지 수
| 지역 | 총 이미지 | food | culture | beach | nature | shopping | transport |
|------|-----------|------|---------|-------|--------|----------|-----------|
| 꾸따 | 778 | 130 | 125 | 132 | 141 | 128 | 122 |
| 우붓 | 669 | 102 | 101 | 109 | 127 | 116 | 114 |
| 누사두아 | 641 | 105 | 111 | 121 | 99 | 108 | 97 |
| 스미냑 | 598 | 127 | 134 | 125 | 80 | 65 | 67 |
| 사누르 | 565 | 108 | 138 | 94 | 80 | 83 | 62 |
| 로비나 | 442 | 66 | 72 | 79 | 71 | 100 | 54 |
| 울루와뚜 | 403 | 81 | 108 | 90 | 54 | 36 | 34 |
| 베두굴 | 393 | 56 | 102 | 65 | 57 | 53 | 60 |
| 킨타마니 | 258 | 24 | 23 | 29 | 116 | 14 | 52 |
| 짠디다사 | 220 | 39 | 33 | 40 | 35 | 28 | 45 |
| 타나롯 | 171 | 20 | 38 | 26 | 19 | 21 | 47 |
| **합계** | **5,138** | **858** | **985** | **910** | **879** | **752** | **754** |

### 5.2 카테고리별 이미지 수
| 카테고리 | 이미지 수 | 비율 |
|----------|-----------|------|
| culture | 985 | 19.2% |
| beach | 910 | 17.7% |
| nature | 879 | 17.1% |
| food | 858 | 16.7% |
| transport | 754 | 14.7% |
| shopping | 752 | 14.6% |

---

## 6. 이미지 alt 텍스트 전략

### 6.1 alt 텍스트 규칙
- 모든 이미지에 고유 alt 텍스트
- 10자 이상, 50자 이하
- 지역명 + 카테고리명 + 구체적 설명
- 같은 페이지 내 10개 alt 모두 고유

### 6.2 alt 텍스트 템플릿 (카테고리별)
```
food:
  - {area} 맛집 음식 사진
  - {area} 현지 레스토랑 사진
  - {area} 비치클럽 음료 사진
  - {area} 로컬 와룽 식사 사진
  - {area} 브런치 카페 분위기
  - {area} 해산물 BBQ 사진
  - {area} 전통 발리 요리 사진
  - {area} 카페 인테리어 사진
  - {area} 디저트 메뉴 사진
  - {area} 야시장 음식 사진
  - {area} 생선구이 사진
  - {area} 열대 과일 사진

culture:
  - {area} 사원 전경 사진
  - {area} 전통 공연 케착춤 사진
  - {area} 사원 건축 양식 사진
  - {area} 힌두교 의식 사진
  - {area} 문화 체험 활동 사진
  - {area} 미술관 전시 사진
  - {area} 사원 조각상 사진
  - {area} 전통 춤 공연 사진
  - {area} 사원 입구 풍경
  - {area} 예술 공방 사진
  - {area} 사원 장식 사진
  - {area} 전통 의상 사진

beach:
  - {area} 해변 전경 사진
  - {area} 서핑 포인트 파도 사진
  - {area} 비치클럽 선셋 사진
  - {area} 스노클링 포인트 사진
  - {area} 해변 산책로 사진
  - {area} 수영장/비치 풍경
  - {area} 해변 일몰 사진
  - {area} 해변 액티비티 사진
  - {area} 해변 카페 사진
  - {area} 해변 모래사장 사진
  - {area} 파도 사진
  - {area} 해변 의자 사진

nature:
  - {area} 라이스 테라스 풍경
  - {area} 폭포 전경 사진
  - {area} 트레킹 코스 사진
  - {area} 화산 일출 사진
  - {area} 열대 우림 풍경
  - {area} 원숭이 숲 사진
  - {area} 자연 수영장 사진
  - {area} 정원/식물원 사진
  - {area} 강변 풍경 사진
  - {area} 전망대 뷰 사진
  - {area} 폭포 아래 사진
  - {area} 정글 트레킹 사진

shopping:
  - {area} 아트 마켓 풍경
  - {area} 기념품 가게 사진
  - {area} 마사지/스파 내부 사진
  - {area} 쇼핑몰 전경
  - {area} 전통 공예품 사진
  - {area} 시장 풍경 사진
  - {area} 라탄 가방/기념품 사진
  - {area} 스파 트리트먼트 사진
  - {area} 로컬 시장 쇼핑 사진
  - {area} 부티크숍 내부 사진
  - {area} 수공예품 사진
  - {area} 기념품 진열 사진

transport:
  - {area} 공항 풍경 사진
  - {area} 스쿠터 렌트 사진
  - {area} 그랩 택시 이용 사진
  - {area} 교통체증 풍경
  - {area} 보트/페리 사진
  - {area} 도로 풍경 사진
  - {area} 주차장/차량 사진
  - {area} 공항 셔틀 사진
  - {area} 시내 이동 풍경
  - {area} 교통 수단 비교 사진
  - {area} 보트 투어 사진
  - {area} 도로 표지판 사진
```

---

## 7. figcaption 전략

### 7.1 figcaption 규칙
- 모든 `<figure>`에 `<figcaption>` 포함
- figcaption 텍스트 = alt 텍스트와 동기화
- 스타일: `font-size:.85em;color:#666;margin-top:6px;text-align:center`

### 7.2 HTML 구조
```html
<figure style="margin:20px 0;text-align:center">
    <img src="../../../../images/{area}/{cat}/{file}.webp" 
         alt="{area} {cat_alt_text}" 
         loading="lazy" 
         style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);background:#f0f0f0" />
    <figcaption style="font-size:.85em;color:#666;margin-top:6px;text-align:center">
        {area} {cat_alt_text}
    </figcaption>
</figure>
```
