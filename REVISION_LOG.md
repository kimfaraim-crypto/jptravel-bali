# JP Travel Bali — 수정서 (변경 이력)
> 작성일: 2026-05-02

---

## 변경 이력

### v4.0 — 2026-05-02 (현재)

#### 이미지 시스템 전면 개선

**변경 사항:**
1. `build_bali.py` — `get_images()` 함수 수정
   - 기존: `area_imgs[:count]` 단순 슬라이싱 (페이지 간 중복)
   - 변경: Fisher-Yates 시드 셔플 방식 (페이지별 고유 시드)
   - 알고리즘: `seed = MD5(f"{area}_{category}_{pageIndex}")` → 셔플 → 앞에서 10개 선택

2. 이미지 부족분 보충
   - `fill_shortages.py` 신규 작성 (Picsum 기반 자동 보충)
   - 20개 지역/카테고리 조합 보충 (196개 신규)
   - 결과: 모든 조합 14개 이상 확보

3. 이미지 대량 확장
   - `fast_expand.py`, `fast_expand2.py`, `fast_expand3.py` 신규 작성
   - Picsum ID 기반 병렬 다운로드 (64 스레드)
   - 결과: 4,681개 → 8,926개 (+4,245개)

4. 중복 이미지 검증
   - 924페이지 모두 고유 이미지 세트 확인
   - 카테고리 간 크로스 중복 0건 확인

**파일 변경:**
| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `build_bali.py` | 수정 | get_images() 시드 셔플, generate_images_html() 인덱스 전달 |
| `fill_shortages.py` | 신규 | 이미지 부족분 자동 보충 |
| `fast_expand.py` | 신규 | 고속 이미지 확장 v1 |
| `fast_expand2.py` | 신규 | 고속 이미지 확장 v2 (Unsplash+Picsum) |
| `fast_expand3.py` | 신규 | 고속 이미지 확장 v3 (Picsum ID) |
| `image_mapping_v3.json` | 수정 | 8,926개 이미지 매핑 |
| `global_image_hashes.json` | 수정 | 전역 perceptual hash DB |
| `image_hashes_v7.json` | 수정 | 이미지 해시 DB v7 |
| `output/html/bali/**/*.html` | 수정 | 924개 HTML 재생성 |
| `output/images/**/*.webp` | 신규 | 4,245개 WEBP 이미지 |
| `progress.txt` | 신규 | 작업 진행 현황 |

**Git 커밋:**
- `f35f26c` — feat: 이미지 4,245개 추가 확장 (총 8,926개)
- `b145e1a` — feat: 이미지 고유 배분 + 부족분 보충

---

### v3.0 — 이전 (원본)

**기존 상태:**
- 924개 HTML 페이지 (11지역 × 6카테고리 × 14페이지)
- 4,681개 이미지
- 20개 지역/카테고리 조합 이미지 부족 (최소 9개)
- 페이지 간 이미지 중복 존재
- 다중 소스 스크래퍼 존재 (scraper_*.py)
- SEO 메타 태그 시스템 존재

---

## 수정 전/후 비교

### 이미지 배분 (핵심 변경)

**Before:**
```python
def get_images(area, category, count=10):
    area_imgs = mapping.get(area, {}).get(category, [])
    if len(area_imgs) >= count:
        return area_imgs[:count]  # ❌ 모든 페이지가 동일한 10장
```

**After:**
```python
def get_images(area, category, page_index=0, count=10):
    area_imgs = mapping.get(area, {}).get(category, [])
    if len(area_imgs) >= count:
        # ✅ 페이지별 고유 시드로 셔플
        seed = MD5(f"{area}_{category}_{page_index}")
        shuffled = fisher_yates_shuffle(area_imgs, seed)
        return shuffled[:count]
```

### 이미지 수량

**Before:** 4,681개 (일부 조합 9~10개)
**After:** 8,926개 (모든 조합 119개+)

| 지역 | Before | After | 변화 |
|------|--------|-------|------|
| 우붓 | 730 | 739 | +9 |
| 스미냑 | 549 | 777 | +228 |
| 꾸따 | 558 | 786 | +228 |
| 사누르 | 521 | 809 | +288 |
| 누사두아 | 366 | 808 | +442 |
| 울루와뚜 | 503 | 786 | +283 |
| 짠디다사 | 519→539 | 844 | +305 |
| 로비나 | 148→198 | 831 | +633 |
| 킨타마니 | 247→287 | 896 | +609 |
| 타나롯 | 138→188 | 865 | +677 |
| 베두굴 | 206→242 | 785 | +543 |

### 페이지 고유성

**Before:** 560/924 고유 (61%)
**After:** 924/924 고유 (100%)

---

## 알려진 제한사항

1. **이미지 소스**: Picsum Photos 사용 (랜덤 사진, 실제 발리 사진 아님)
2. **콘텐츠**: 하드코딩 (동적 업데이트 불가)
3. **빌드**: 수동 실행 (CI/CD 미구축)
4. **호스팅**: GitHub repo만 존재 (정적 사이트 미배포)

---

## 롤백 방법

이전 상태로 되돌리려면:
```bash
git checkout 69688f2  # v3.0 원본 커밋
git checkout -b rollback-branch
git push origin rollback-branch
```

현재 상태로 복구:
```bash
git checkout main  # f35f26c (현재)
```
