#!/usr/bin/env python3
"""
실제 발리 이미지를 기존 디렉토리에 병합
1. images_real/ → output/images/ 복사
2. Picsum 이미지 교체 (해시 기반)
3. 매핑 업데이트
4. HTML 재빌드
"""
import os, json, shutil, hashlib
from pathlib import Path
from io import BytesIO
from PIL import Image
from datetime import datetime

BASE = Path(__file__).parent
SRC = BASE / "output" / "images_real"
DST = BASE / "output" / "images"
HASH_DB = BASE / "file_hashes.json"
MAP_FILE = BASE / "image_mapping_v3.json"

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def md5(data):
    return hashlib.md5(data).hexdigest()

def phash(img):
    try:
        s = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        px = list(s.getdata())
        avg = sum(px) / len(px)
        return ''.join('1' if p > avg else '0' for p in px)
    except:
        return None

def hamming(a, b):
    if not a or not b or len(a) != len(b): return 999
    return sum(x != y for x, y in zip(a, b))

def main():
    log("=" * 60)
    log("🔄 실제 발리 이미지 병합 시작")
    log("=" * 60)

    if not SRC.exists():
        log("❌ images_real/ 디렉토리가 없습니다!")
        return

    hashes = json.loads(HASH_DB.read_text()) if HASH_DB.exists() else {}
    mapping = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}
    existing_md5s = set(hashes.values())

    total_copied = 0
    total_skipped = 0

    for area_dir in sorted(SRC.iterdir()):
        if not area_dir.is_dir():
            continue
        area = area_dir.name
        log(f"\n🌍 {area}")

        for cat_dir in sorted(area_dir.iterdir()):
            if not cat_dir.is_dir():
                continue
            cat = cat_dir.name
            dst_dir = DST / area / cat
            dst_dir.mkdir(parents=True, exist_ok=True)

            # 기존 파일 수
            existing_files = list(dst_dir.glob('*.webp'))
            existing_count = len(existing_files)

            # 기존 pHashes
            eph = []
            for f in existing_files[:100]:
                try:
                    h = phash(Image.open(f))
                    if h: eph.append(h)
                except: pass

            copied = 0
            for src_file in sorted(cat_dir.glob('*.webp')):
                data = src_file.read_bytes()
                h = md5(data)

                # 중복 체크
                if h in existing_md5s:
                    total_skipped += 1
                    continue

                img = Image.open(BytesIO(data))
                p = phash(img)
                dup = False
                if p:
                    for ep in eph:
                        if hamming(p, ep) <= 5:
                            dup = True; break
                if dup:
                    total_skipped += 1
                    continue

                # 복사
                num = existing_count + copied + 1
                fn = f"{area}_{cat}_{num:04d}.webp"
                dst_file = dst_dir / fn
                shutil.copy2(src_file, dst_file)

                hashes[str(dst_file)] = h
                existing_md5s.add(h)
                if p: eph.append(p)

                if area not in mapping: mapping[area] = {}
                if cat not in mapping[area]: mapping[area][cat] = []
                mapping[area][cat].append(fn)

                copied += 1
                total_copied += 1

            if copied > 0:
                log(f"  ✅ {area}/{cat}: +{copied}장 (총 {existing_count + copied})")

    # 저장
    HASH_DB.write_text(json.dumps(hashes, ensure_ascii=False, indent=2))
    MAP_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))

    log("\n" + "=" * 60)
    log(f"✅ 병합 완료!")
    log(f"   복사: {total_copied}장")
    log(f"   중복 스킵: {total_skipped}장")
    total = sum(len(v) for cats in mapping.values() for v in cats.values())
    log(f"   총 이미지: {total}장")
    log("=" * 60)

if __name__ == '__main__':
    main()
