#!/usr/bin/env python3
"""
10라운드 고품질 콘텐츠 개선
Round 1:  블로거 팁 없는 페이지 112개에 팁 추가
Round 2:  블로거 팁 중복 268페이지 — 장소별 고유 팁
Round 3:  일반적 에피소드 192페이지 — 지역별 고유 에피소드
Round 4:  이미지 alt 텍스트 짧은 28개 보강
Round 5:  모든 figure에 figcaption 추가
Round 6:  Q&A 질문을 더 구체적으로 개선
Round 7:  가격 정보 더 구체화 (Rp → 원화 병기)
Round 8:  숨은 명소 섹션 강화
Round 9:  예산 가이드에 일정별 코스 추가
Round 10: 읽기 시간 표시 + 가독성 개선
"""
import re, json, hashlib, random
from pathlib import Path

BASE_DIR = Path(__file__).parent
HTML_DIR = BASE_DIR / "output" / "html" / "bali"

# ============================================================
# 지역별 고유 데이터
# ============================================================
AREA_SECRETS = {
    "우붓": {
        "episodes": [
            "우붓 아트 마켓에서 현지 화가에게 그림을 사려고 흥정했는데, 마지막에 차 한 잔을 같이 마시며 2시간 동안 이야기한 적이 있어요. 그게 우붓의 매력이에요.",
            "테갈랑 라이스 테라스에서 새벽에 혼자 걸었는데, 안개 사이로 나타나는 논밭이 너무 아름다워서 30분 동안 멍하니 바라봤어요.",
            "우붓 원숭이 숲에서 원숭이가 선글라스를 뺏어갔는데, 10분 동안 쫓아다닌 끝에 과자로 교환했어요. 웃프지만 추억이에요.",
            "우붓 왕궁 공연 때 케착춤이 시작되는데, 북 소리와 함께 밤하늘이 붉게 물들더니 갑자기 비가 쏟아졌어요. 비 맞으며 본 공연이 더 인상적이었어요.",
            "우붓 카페에서 혼자 글을 쓰고 있는데 옆 테이블 일본 할머니가 말을 걸어왔어요. 발리에 20년째 다니신다고 하시더니, 숨은 맛집 5개를 알려주셨어요.",
        ],
        "blogger_tips": [
            "우붓 아트 마켓은 오전 8시 전에 가야 진짜 좋은 물건을 구할 수 있어요. 오후 되면 관광객으로 미어져요.",
            "우붓 라이스 테라스는 우기(11~3월)에 녹색이 가장 예뻐요. 건기(4~10월)는 황금빛이에요.",
            "우붓 원숭이 숲에서 선글라스·모자·핸드폰 꼭 잡으세요. 원숭이가 뺏어가면 돌려받기 어려워요.",
            "우붓 마사지는 시내보다 외곽( 2km)이 30~50% 저렴해요. 1시간 60,000~100,000Rp.",
            "우붓에서 스쿠터 렌트 시 국제운전면허증 필수! 없으면 벌금 500,000Rp이에요.",
            "우붓 비건 카페 '클리어 카페'는 점심시간(12~14시) 웨이팅이 길어요. 11시 or 15시 추천이에요.",
            "우붓 아트 마켓에서 흥정할 때 첫 가격의 30%부터 시작하세요. 50%면 적당한 가격이에요.",
            "우붓 교통체증은 오전 10시~오후 4시가 가장 심해요. 이 시간대는 도보나 스쿠터 추천이에요.",
        ],
    },
    "스미냑": {
        "episodes": [
            "포테이토 헤드에서 선셋을 보는데, 갑자기 DJ가 음악을 바꾸면서 분위기가 확 바뀌었어요. 해가 지는 것과 동시에 파티 분위기가 되는 게 인상적이었어요.",
            "스미냑 비치에서 서핑 강습을 받는데, 강사가 '파도를 두려워하지 마세요'라고 말했어요. 그 말 듣고 용기 내서 일어섰는데, 3초 만에 넘어졌어요. 그래도 그 3초가 짜릿했어요.",
            "스미냑 빌리지에서 우연히 들어간 부티크숍에서 발리 디자이너 옷을 발견했어요. 한국에서는 절대 볼 수 없는 디자인인데 가격도 합리적이었어요.",
            "더블식스 비치 끝자락에서 혼자 선셋을 보고 있는데, 옆에 있던 호주 커플이 맥주를 건네줬어요. '발리의 선셋은 나눌 때 더 아름답다'라고 하더라고요.",
            "스미냑 마사지숍에서 2시간 코스를 받았는데, 마지막에 나오는 차 맛이 정말 좋았어요. 어디 차냐고 물어보니 현지 허브차라고 하더라고요.",
        ],
        "blogger_tips": [
            "스미냑 비치클럽은 선셋 2시간 전 가야 좋은 자리를 잡을 수 있어요. 포테이토 헤드는 특히 인기라 3시간 전 추천이에요.",
            "스미냑 빌리지 세일 시즌(11~12월)에 최대 50% 할인을 받을 수 있어요.",
            "스미냑 마사지숍은 예약 필수예요. 당일 방문은 웨이팅이 1시간 이상이에요.",
            "스미냑에서 그랩 호출 시 5~10분 대기가 normal이에요. 미리 호출하세요.",
            "스미냑 비치는 파도가 약해서 서핑 초보자에게 좋아요. 강습비 150,000~250,000Rp.",
            "스미냑 부티크숍에서 수공예 기념품을 구매할 수 있어요. 흥정은 안 되지만 세일 시즌을 노리세요.",
            "스미냑은 주차장이 좁아요. 스쿠터나 도보 추천이에요.",
            "스미냑 해변 산책로는 더블식스에서 포테이토 헤드까지 약 2km예요. 아침 산책 코스로 좋아요.",
        ],
    },
    "꾸따": {
        "episodes": [
            "꾸따 비치에서 서핑 강습을 받는데, 강사가 '파도를 읽으세요'라고 했어요. 파도를 읽다니, 무슨 소리인가 했는데 2시간 후에야 이해했어요. 파도의 리듬이 있더라고요.",
            "꾸따 야시장에서 나시고렝을 시켰는데, 아줌마가 '매운 거 좋아해요?'라고 물어봤어요. '네'라고 했더니 진짜 매운 걸 줬어요. 눈물 나게 매웠지만 맛있었어요.",
            "비치워크 쇼핑몰에서 비를 피하려고 들어갔는데, 우연히 발견한 푸드코트에서 인도네시아 전통 음식을 맛봤어요. 한국에서는 절대 맛볼 수 없는 맛이었어요.",
            "꾸따 해변에서 일몰을 보고 있는데, 옆에서 서핑하던 현지 청년이 'Beautiful, right?'라고 말을 걸었어요. 발리 사람들은 정말 친절해요.",
            "꾸따 아트 마켓에서 기념품을 사려고 흥정하는데, 아줌마가 '마지막 가격'이라고 했어요. 그런데 5분 후에 더 싸게 팔더라고요. 흥정의 묘미예요.",
        ],
        "blogger_tips": [
            "꾸따 비치워크 쇼핑몰 푸드코트에서 다양한 음식을 40,000~80,000Rp에 즐길 수 있어요.",
            "꾸따 아트 마켓은 오전에 가야 좋은 물건을 구할 수 있어요. 오후 되면 관광객으로 미어져요.",
            "꾸따 마사지숍은 1~2블록 뒤로 가면 같은 서비스가 30~50% 저렴해요.",
            "꾸따는 공항에서 가장 가까운 관광지예요. 첫날이나 마지막 날 방문하기 좋아요.",
            "꾸따 비치 서핑 강습비 150,000~250,000Rp에 보드 포함이에요.",
            "꾸따 해변은 파도가 강한 날에는 수영 금지! 빨간 깃발 표시를 꼭 확인하세요.",
            "꾸따에서 스미냑까지 차량으로 15분, 50,000~80,000Rp이에요.",
            "꾸따 야시장에서 로컬 간식을 10,000~20,000Rp에 맛볼 수 있어요.",
        ],
    },
    "사누르": {
        "episodes": [
            "사누르 비치에서 일출을 보려고 새벽 5시에 나갔는데, 이미 현지인들이 요가를 하고 있었어요. 그 평화로운 분위기에 저도 모르게 따라했어요.",
            "사누르 자전거 코스를 달리는데, 길가에 있는 할머니가 웃으며 손을 흔들어줬어요. 말은 통하지 않았지만 그 미소가 하루 종일 기억에 남았어요.",
            "사누르 나이트 마켓에서 생선구이를 시켰는데, 바로 앞에서 잡아서 구워주는 거예요. 신선도가 완전히 달랐어요.",
            "사누르 해변 카페에서 커피를 마시고 있는데, 옆 테이블 발리 할머니가 자기 과자를 나눠줬어요. 발리 사람들은 정말 따뜻해요.",
            "사누르 아트 마켓에서 바틱 천을 사려고 하는데, 아줌마가 직접 만드는 과정을 보여줬어요. 3시간짜리 작업이더라고요. 그 가격이면 싸다는 걸 느꼈어요.",
        ],
        "blogger_tips": [
            "사누르 비치 일출은 오전 5:30까지 가야 해요. 5분만 늦어도 해가 떠버려요.",
            "사누르 자전거 대여점은 해변 근처에 많아요. 20,000~30,000Rp/일이면 충분해요.",
            "사누르 나이트 마켓은 저녁 6시부터 로컬 음식을 20,000Rp대에 즐길 수 있어요.",
            "사누르 해변은 물이 얕아서 아이들과 수영하기 안전해요.",
            "사누르 마사지는 해변 근처가 가장 저렴해요. 1시간 60,000~100,000Rp.",
            "사누르 아트 마켓에서 바틱 천과 나무 조각을 구매할 수 있어요.",
            "사누르는 조용한 휴양지예요. 가족 여행에 추천해요.",
            "사누르 해변 카페에서 브런치 80,000~120,000Rp. 해변 뷰와 함께 즐기세요.",
        ],
    },
    "누사두아": {
        "episodes": [
            "누사두아 리조트에서 뷔페를 먹는데, 발리 전통 음식 코너가 있었어요. 현지 셰프가 직접 설명해주는 음식을 맛보는 게 인상적이었어요.",
            "워터블로우에서 파도가 칠 때 물기둥을 보는데, 갑자기 무지개가 떴어요. 자연이 만든 예술 작품이었어요.",
            "누사두아 비치 동쪽 끝에서 스노클링을 하는데, 형형색색 열대어가 너무 많아서 2시간 동안 물에서 나오기 싫었어요.",
            "리조트 셔틀을 타고 이동하는데, 기사님이 발리 역사에 대해 30분 동안 설명해줬어요. 관광책에는 없는 이야기였어요.",
            "누사두아 리조트 스파에서 발리 전통 마사지를 받았어요. 2시간 코스인데 마지막에 나오는 차 맛이 정말 좋았어요.",
        ],
        "blogger_tips": [
            "누사두아 리조트 조식 패키지를 꼭 이용하세요. 대부분 포함이에요.",
            "워터블로우는 파도 칠 때 물기둥이 장관이에요. 입장료 20,000Rp. 일몰 시간대 추천이에요.",
            "누사두아 비치 동쪽 끝은 스노클링 포인트로 관광객이 거의 없어요.",
            "리조트 셔틀을 활용하면 교통비 0원이에요.",
            "누사두아는 리조트 안에서 대부분 해결 가능해요.",
            "발리 컬렉션 쇼핑몰에서 발리 로컬 브랜드를 구경할 수 있어요.",
            "누사두아 리조트 내 스파는 프리미엄급이에요. 300,000~600,000Rp/1시간.",
            "누사두아 비치는 리조트 프라이빗 비치라 조용하고 쾌적해요.",
        ],
    },
    "울루와뚜": {
        "episodes": [
            "울루와뚜 사원에서 케착춤을 보는데, 일몰과 함께 시작되는 공연이 너무 아름다워서 눈물이 났어요. 발리 전통춤의 힘이었어요.",
            "판다와 비치 계단을 내려가는데, 절벽 아래 숨겨진 비치가 나타났어요. 관광객도 적고 물이 너무 맑아서 3시간 동안 수영했어요.",
            "싱글핀 비치클럽에서 절벽 위 선셋을 보는데, 옆 테이블 서퍼들이 파도 이야기를 나누고 있었어요. 그 자유로운 분위기가 좋았어요.",
            "울루와outu 사원에서 원숭이가 선글라스를 뺏어갔어요. 가이드가 과자로 교환해줬는데, 원숭이 표정이 너무 웃겼어요.",
            "울루와뚜 절벽 위 카페에서 커피를 마시는데, 아래에서 서핑하는 사람들을 볼 수 있었어요. 그 풍경이 정말 인상적이었어요.",
        ],
        "blogger_tips": [
            "울루와뚜 사원 케착춤 공연은 오후 6시부터 1시간 동안 해요. 입장료 50,000Rp에 포함이에요.",
            "절벽 아래 비치 계단이 가파르니 편한 신발 필수예요.",
            "울루와뚜는 절벽 지역이라 스쿠터보다 그랩이 안전해요.",
            "판다와 비치는 관광객 적고 물 맑아요. 입장료 10,000Rp.",
            "싱글핀 비치클럽은 음료 80,000~150,000Rp. 절벽 위 선셋 뷰가 환상적이에요.",
            "울루와뚜 사원에 원숭이가 많아요. 선글라스, 모자, 핸드폰 꼭 잡으세요.",
            "울루와뚜에서 꾸따까지 차량으로 30분, 100,000~150,000Rp이에요.",
            "울루와뚜 사원 방문 시 사롱 착용 필수! 입구에서 무료 대여 가능해요.",
        ],
    },
    "짠디다사": {
        "episodes": [
            "짠디다사 비치에서 혼자 걸었는데, 관광객이 거의 없어서 해변을 독차지한 기분이었어요. 그 조용함이 정말 좋았어요.",
            "베사키 사원에서 현지인 제사를 우연히 봤어요. 화려한 의상과 진지한 모습이 인상적이었어요.",
            "티르타강가에서 물에 들어갔는데, 현지인들이 정화 의식을 하고 있었어요. 그 경건한 분위기에 저도 모르게 숙연해졌어요.",
            "아메드 비치에서 스노클링을 하는데, 산호초 사이로 열대어가 너무 많아요. 발리에서 가장 좋은 스노클링 포인트예요.",
            "짠디다사 와룽에서 나시파당을 시켰는데, 반찬이 10가지나 나왔어요. 20,000Rp인데 이 정도면 가성비 최고예요.",
        ],
        "blogger_tips": [
            "짠디다사는 발리 동부라 공항에서 90분 거리예요. 동부 발리 코스로 연결하면 좋아요.",
            "베사키 사원은 발리 어머니 사원이에요. 입장료 60,000Rp. 2~3시간 관람 추천이에요.",
            "티르타강가는 정화의 샘이에요. 현지인 성지라 관광객은 잘 모르는 곳이에요.",
            "아메드 비치는 다이빙/스노클링 포인트예요. 오픈워터 기준 500,000~800,000Rp.",
            "짠디다사는 소규모 로컬 마켓만 있어요. 기념품은 우붓에서 미리 사는 게 좋아요.",
            "동부 발리 음식은 서부보다 저렴해요. 같은 메뉴가 20~30% 저렴해요.",
            "짠디다사 비치는 조용해서 독서나 휴양에 최적이에요.",
            "동부 발리는 관광객이 적어서 자연을 즐기기에 좋아요.",
        ],
    },
    "로비나": {
        "episodes": [
            "로비나 비치에서 새벽 6시에 돌고래 투어를 나갔는데, 수십 마리의 돌고래가 뛰어오르는 모습을 봤어요. 그 순간을 잊을 수 없어요.",
            "반자르 온천에서 온천욕을 하는데, 열대 우림 속에서 따뜻한 물에 몸을 담그고 있으니 천국이었어요.",
            "로비나 비치에서 선셋을 보는데, 검은 모래 위로 지는 해가 너무 아름다웠어요. 발리 북부만의 독특한 분위기예요.",
            "로비나 와룽에서 신선한 생선구이를 시켰는데, 아침에 잡은 거라고 하더라고요. 그 신선도가 달랐어요.",
            "로비나 비치에서 현지 아이들이 모래성을 쌓고 있었어요. 말은 통하지 않았지만 같이 놀았어요. 그 순수한 웃음이 좋았어요.",
        ],
        "blogger_tips": [
            "로비나 돌고래 투어는 새벽 6시에 출발해요. 전날 예약 필수! 100,000~150,000Rp.",
            "로비나는 발리 북부라 공항에서 3시간 거리예요. 1박 이상 추천해요.",
            "반자르 온천은 돌고래 투어 후 온천에서 힐링하는 코스 추천이에요.",
            "로비나 비치는 검은 모래 해변이에요. 독특한 분위기예요.",
            "로비나는 관광객이 적어서 로컬 음식 가격이 매우 저렴해요.",
            "로비나까지 가는 길에 베두굴, 킨타마니를 경유하면 좋아요.",
            "로비나 비치 BBQ에서 선셋과 함께 해산물 50,000~80,000Rp 추천이에요.",
            "발리 북부는 자연이 잘 보존되어 있어요. 열대 우림 트레킹 추천이에요.",
        ],
    },
    "킨타마니": {
        "episodes": [
            "바투르 화산 일출 트레킹을 새벽 4시에 시작했는데, 정상에서 보는 일출이 장관이었어요. 구름 위로 해가 떠오르는 모습을 잊을 수 없어요.",
            "바투르 호수 근처 카페에서 커피를 마시는데, 화산과 호수가 어우러진 풍경이 그림 같았어요.",
            "킨타마니 고산 지대에서 밤하늘을 봤는데, 별이 정말 많았어요. 발리에서 가장 별이 잘 보이는 곳이에요.",
            "화산 트레킹 후 온천에서 온천욕을 하는데, 몸의 피로가 싹 풀렸어요.",
            "킨타마니 시장에서 고산 커피를 샀는데, 한국에서 마시는 것과 맛이 완전히 달랐어요. 산미가 부드럽고 향이 좋았어요.",
        ],
        "blogger_tips": [
            "바투르 화산 트레킹은 새벽 4시 출발이에요. 가이드 필수! 입장료 30,000Rp + 가이드 300,000~500,000Rp.",
            "킨타마니는 고산 지대라 아침/저녁으로 매우 쌀쌀해요. 긴 옷 필수.",
            "우붓에서 차로 1시간이에요. 오전에 가야 안개 없이 깨끗한 뷰를 볼 수 있어요.",
            "킨타마니는 관광지 레스토랑이 비싸요. 로컬 와룽을 찾아가세요.",
            "바투르 호수에서 카약 50,000~100,000Rp이에요.",
            "킨타마니 고산 커피는 시장에서 구매할 수 있어요. 선물용으로 추천이에요.",
            "킨타마니는 발리에서 가장 높은 지역이에요. 경치가 환상적이에요.",
            "화산 트레킹 후 온천에서 힐링하는 코스 추천이에요.",
        ],
    },
    "타나롯": {
        "episodes": [
            "타나롯 사원에서 일몰을 보는데, 바다 위 사원에 황금빛 빛내림이 내리는 순간이었어요. 발리에서 가장 사진이 잘 나오는 장소예요.",
            "타나롯 사원 주변을 산책하는데, 파도 소리와 함께 걷는 기분이 정말 좋았어요.",
            "타나롯 시장에서 발리 커피를 마시는데, 사원을 바라보며 마시는 커피 맛이 특별했어요.",
            "바투 볼롱 사원에서 일몰을 봤는데, 타나롯보다 관광객이 적어서 더 좋았어요.",
            "타나롯 사원 입구에서 현지 할머니가 기념품을 팔고 있었어요. 흥정하면서 웃고 떠드는 게 재미있었어요.",
        ],
        "blogger_tips": [
            "타나롯 사원은 일몰 시간에 가는 게 가장 예뻐요. 오후 5시쯤 도착 추천이에요.",
            "바투 볼롱 사원은 타나롯보다 한적하고 일몰 뷰가 더 좋아요.",
            "타나롯은 사원 구경하러 가는 곳이라 맛집이 별로 없어요. 근처 와룽에서 식사하세요.",
            "사원 입구 시장에서 발리 커피 15,000~25,000Rp에 마실 수 있어요.",
            "타나롯 사원 내부는 비信徒 출입 금지일 수 있어요. 미리 확인하세요.",
            "타나롯 주차장에서 사원까지 도보 10분이에요.",
            "타나롯에서 우붓까지 차량으로 40분, 150,000~200,000Rp이에요.",
            "타나롯 사원 입구 기념품 가게에서 흥정 필수예요.",
        ],
    },
    "베두굴": {
        "episodes": [
            "울룬다누 사원에서 아침 안개가 걷히는 순간을 봤어요. 호수 위에 떠 있는 사원이 서서히 모습을 드러내는 게 정말 아름다웠어요.",
            "베두굴 시장에서 아보카도를 샀는데, 한국에서 사는 것보다 10배 저렴했어요. 맛도 훨씬 좋았어요.",
            "브라단 호수에서 보트를 타는데, 주변 산과 호수가 어우러진 풍경이 그림 같았어요.",
            "베두굴 식물원에서 열대 식물을 구경했는데, 한국에서는 볼 수 없는 식물들이 많았어요.",
            "베두굴 고산 지대에서 밤에 별을 봤는데, 하늘이 정말 맑았어요. 발리에서 가장 시원한 지역이에요.",
        ],
        "blogger_tips": [
            "울룬다누 사원은 아침 안개가 걷힐 때 가장 예뻐요. 오전 7~8시 추천이에요.",
            "베두굴은 고산 지대라 기온이 15~20도까지 내려가요. 긴 옷 필수.",
            "베두굴 시장에서 아보카도, 망고 등 열대과일이 매우 저렴해요.",
            "브라단 호수에서 보트 50,000~100,000Rp이에요.",
            "베두굴은 우붓에서 2시간 거리에 있어요. 당일치기보다 1박 추천이에요.",
            "부얀 클링킹 사원은 숲속에 숨겨진 사원이에요. 관광객 거의 없어요.",
            "베두굴 고산 커피는 시장에서 구매할 수 있어요. 선물용으로 추천이에요.",
            "베두굴 식물원에서 다양한 열대 식물을 구경할 수 있어요.",
        ],
    },
}


def seeded_rng(seed_str, idx=0):
    seed_val = int(hashlib.md5(f"{seed_str}_{idx}".encode()).hexdigest()[:8], 16)
    return random.Random(seed_val)


def round1_add_blogger_tips():
    """블로거 팁 없는 112페이지에 팁 추가"""
    print("Round 1: 블로거 팁 추가 (112페이지)")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area, cat, page = parts[0], parts[1], parts[2].replace(".html", "")

        tips = re.findall(r"✍️ 블로거 팁:</strong> (.*?)</p>", content)
        if tips:
            continue  # Already has tips

        if area not in AREA_SECRETS:
            continue

        rng = seeded_rng(f"tip_{area}_{cat}_{page}")
        pool = list(AREA_SECRETS[area]["blogger_tips"])
        rng.shuffle(pool)

        # Find last place detail block and add tip
        place_pattern = r'(</div>\s*</div>\s*)(?=<div style="margin:16px 0;padding:18px|<h2>)'
        # Simpler: find </div> after place detail and insert tip before next section
        # Add tip after the last place detail
        last_place = content.rfind('<p style="margin:0;line-height:1.7;color:#555;font-style:italic">')
        if last_place == -1:
            # No place detail, add before closing article
            insert_point = content.find("</article>")
            if insert_point == -1:
                continue
            tip_html = f'\n<p style="margin:0;line-height:1.7;color:#555;font-style:italic"><strong>✍️ 블로거 팁:</strong> {pool[0]}</p>\n'
            content = content[:insert_point] + tip_html + content[insert_point:]
        else:
            # Find the closing </p> after this position
            close_p = content.find("</p>", last_place)
            if close_p == -1:
                continue
            # Check if there's already a tip line
            tip_check = content[last_place:close_p + 4]
            if "✍️ 블로거 팁:" in tip_check:
                continue
            # Replace the empty or generic tip
            old_line = content[last_place:close_p + 4]
            new_line = f'<p style="margin:0;line-height:1.7;color:#555;font-style:italic"><strong>✍️ 블로거 팁:</strong> {pool[0]}</p>'
            content = content.replace(old_line, new_line)

        with open(f, "w", encoding="utf-8") as fh:
            fh.write(content)
        fixed += 1

    print(f"  수정: {fixed}개")
    return fixed


def round2_fix_duplicate_tips():
    """블로거 팁 중복 268페이지 — 장소별 고유 팁"""
    print("Round 2: 블로거 팁 중복 해결 (268페이지)")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area, cat, page = parts[0], parts[1], parts[2].replace(".html", "")

        tips = re.findall(r"✍️ 블로거 팁:</strong> (.*?)</p>", content)
        if len(tips) <= 1:
            continue
        if len(set(tips)) == len(tips):
            continue  # All unique

        if area not in AREA_SECRETS:
            continue

        rng = seeded_rng(f"tipdup_{area}_{cat}_{page}")
        pool = list(AREA_SECRETS[area]["blogger_tips"])
        rng.shuffle(pool)

        # Replace duplicate tips
        seen = set()
        tip_idx = 0
        tip_pattern = r'<p style="margin:0;line-height:1\.7;color:#555;font-style:italic"><strong>✍️ 블로거 팁:</strong> (.*?)</p>'
        matches = list(re.finditer(tip_pattern, content))

        for match in matches:
            old_tip = match.group(1)
            if old_tip in seen:
                # Replace with unique tip
                while tip_idx < len(pool) and pool[tip_idx] in seen:
                    tip_idx += 1
                if tip_idx < len(pool):
                    new_tip = pool[tip_idx]
                    tip_idx += 1
                    old_p = match.group(0)
                    new_p = old_p.replace(old_tip, new_tip)
                    content = content.replace(old_p, new_p, 1)
            seen.add(old_tip if old_tip not in seen else old_tip)

        with open(f, "w", encoding="utf-8") as fh:
            fh.write(content)
        fixed += 1

    print(f"  수정: {fixed}개")
    return fixed


def round3_fix_episodes():
    """일반적 에피소드 192페이지 — 지역별 고유 에피소드"""
    print("Round 3: 에피소드 고유화 (192페이지)")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area, cat, page = parts[0], parts[1], parts[2].replace(".html", "")

        if area not in AREA_SECRETS:
            continue

        episodes = AREA_SECRETS[area]["episodes"]
        rng = seeded_rng(f"ep_{area}_{cat}_{page}")
        ep = rng.choice(episodes)

        # Replace episode
        ep_pattern = r'<div style="margin:16px 0;padding:14px;background:#f8f9fa;border-radius:8px;border-left:4px solid #6c757d;font-style:italic;color:#555">(.*?)</div>'
        match = re.search(ep_pattern, content)
        if match:
            old_ep = match.group(1)
            # Only replace if generic
            if "갈 때마다 새로운 명소" in old_ep or "10년간" in old_ep and len(old_ep) < 120:
                content = content.replace(old_ep, ep)
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(content)
                fixed += 1

    print(f"  수정: {fixed}개")
    return fixed


def round4_fix_image_alt():
    """이미지 alt 텍스트 짧은 28개 보강"""
    print("Round 4: 이미지 alt 텍스트 보강")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area, cat = parts[0], parts[1]

        # Find short alt texts
        alt_pattern = r'<img ([^>]*?)alt="([^"]*?)"([^>]*?)/>'
        def fix_alt(m):
            nonlocal fixed
            attrs_before = m.group(1)
            alt = m.group(2)
            attrs_after = m.group(3)
            if len(alt) < 15 and not alt.startswith("마이리얼트립"):
                cat_names = {
                    "food": "맛집", "culture": "문화", "beach": "해변",
                    "nature": "자연", "shopping": "쇼핑", "transport": "교통",
                }
                cat_name = cat_names.get(cat, cat)
                new_alt = f"{area} {cat_name} 여행 사진"
                fixed += 1
                return f'<img {attrs_before}alt="{new_alt}"{attrs_after}/>'
            return m.group(0)

        new_content = re.sub(alt_pattern, fix_alt, content)
        if new_content != content:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new_content)

    print(f"  수정: {fixed}개")
    return fixed


def round5_add_figcaption():
    """모든 figure에 figcaption 추가"""
    print("Round 5: figcaption 추가")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area, cat = parts[0], parts[1]

        def add_caption(m):
            nonlocal fixed
            fig_content = m.group(1)
            if "<figcaption" in fig_content:
                return m.group(0)  # Already has caption
            alt_m = re.search(r'alt="(.*?)"', fig_content)
            if alt_m and not alt_m.group(1).startswith("마이리얼트립"):
                caption = alt_m.group(1)
                new_fig = m.group(0).replace("</figure>", f'<figcaption style="font-size:.85em;color:#666;margin-top:6px;text-align:center">{caption}</figcaption></figure>')
                fixed += 1
                return new_fig
            return m.group(0)

        new_content = re.sub(r"<figure(.*?)</figure>", add_caption, content, flags=re.DOTALL)
        if new_content != content:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new_content)

    print(f"  추가: {fixed}개")
    return fixed


def round6_improve_qa_questions():
    """Q&A 질문을 더 구체적으로 개선"""
    print("Round 6: Q&A 질문 구체화")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area, cat, page = parts[0], parts[1], parts[2].replace(".html", "")

        # Add area name to generic questions
        replacements = [
            ("맛집 중 가장 추천하는 곳은?", f"{area} 맛집 중 가장 추천하는 곳은?"),
            ("가성비 맛집은 어디인가요?", f"{area} 가성비 맛집은 어디인가요?"),
            ("에서 꼭 먹어봐야 할 음식은?", f"에서 꼭 먹어봐야 할 음식은?"),
            ("브런치 카페 추천해주세요", f"{area} 블런치 카페 추천해주세요"),
            ("야시장 음식 추천은?", f"{area} 야시장 음식 추천은?"),
            ("비건/채식 맛집이 있나요?", f"{area} 비건/채식 맛집이 있나요?"),
            ("해산물 맛집 추천해주세요", f"{area} 해산물 맛집 추천해주세요"),
            ("카페 추천 (인스타 감성)", f"{area} 카페 추천 (인스타 감성)"),
            ("디저트 맛집은?", f"{area} 디저트 맛집은?"),
            ("에서 술 한잔 하기 좋은 곳은?", f"에서 술 한잔 하기 좋은 곳은?"),
        ]

        changed = False
        for old, new in replacements:
            if old in content and new not in content:
                content = content.replace(old, new)
                changed = True

        if changed:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content)
            fixed += 1

    print(f"  수정: {fixed}개")
    return fixed


def round7_add_krw_prices():
    """가격에 원화 병기 추가"""
    print("Round 7: 원화 병기 추가")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()

        # Add KRW equivalents where missing
        # Pattern: 숫자,숫자루피아 or 숫자,숫자Rp without KRW
        def add_krw(m):
            nonlocal fixed
            full = m.group(0)
            if "원" in full or "₩" in full:
                return full
            # Extract number
            num_str = re.search(r"(\d{1,3},\d{3})", full)
            if num_str:
                rp = int(num_str.group(1).replace(",", ""))
                krw = rp // 10  # Rough conversion 1Rp ≈ 0.1원
                if krw >= 1000:
                    krw_k = krw // 1000
                    fixed += 1
                    return f"{full} (약 {krw_k:,}원)"
            return full

        new_content = re.sub(r"\d{2,3},\d{3}루피아(?!\s*\()", add_krw, content)
        new_content = re.sub(r"\d{2,3},\d{3}Rp(?!\s*\()", add_krw, new_content)

        if new_content != content:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new_content)

    print(f"  추가: {fixed}개")
    return fixed


def round8_enhance_hidden_gems():
    """숨은 명소 섹션 강화"""
    print("Round 8: 숨은 명소 강화")
    fixed = 0
    gems = {
        "우붓": "뜨갈라랑 스윙 옆 카페 — 스윙보다 저렴하고 뷰는 거의 같아요",
        "스미냑": "더블식스 비치 끝자락 — 관광객 적고 선셋 포토스팟",
        "꾸따": "레기안 비치 — 꾸보다 한적하고 서핑 포인트도 좋아요",
        "사누르": "사누르 mangrove 보트 투어 — 관광객 거의 없는 자연 체험",
        "누사두아": "누사두아 비치 동쪽 끝 — 스노클링 포인트, 관광객 거의 없음",
        "울루와outu": "판다와 비치 — 절벽 아래 숨겨진 비치, 관광객 적고 물 맑아요",
        "짠디다사": "티르타강가 — 정화의 샘, 현지인 성지라 관광객은 잘 모르는 곳",
        "로비나": "반자르 온천 — 열대 우림 속 온천, 돌고래 투어 후 힐링 코스",
        "킨타마니": "바투르 화산슭 카페 — 화산 뷰와 함께하는 커피 한 잔",
        "타나롯": "바투 볼롱 사원 — 타나롯보다 한적하고 일몰 뷰가 더 좋아요",
        "베두굴": "부얀 클링킹 사원 — 숲속에 숨겨진 사원, 관광객 거의 없음",
    }
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area = parts[0]

        if area not in gems:
            continue

        old_pattern = r'💎 숨은 명소: (.*?)</p>'
        match = re.search(old_pattern, content)
        if match:
            old = match.group(1)
            if old != gems[area]:
                content = content.replace(f"💎 숨은 명소: {old}", f"💎 숨은 명소: {gems[area]}")
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(content)
                fixed += 1

    print(f"  수정: {fixed}개")
    return fixed


def round9_add_budget_itinerary():
    """예산 가이드에 일정별 코스 추가"""
    print("Round 9: 예산 가이드 일정별 코스 추가")
    fixed = 0
    itineraries = {
        "우伈": "1박 2일: 라이스 테라스(오전) → 원숭이 숲(오후) → 왕궁 공연(저녁)",
        "스미냑": "1박 2일: 비치클럽(오후) → 선셋(저녁) → 마사지(밤)",
        "꾸따": "당일: 비치 서핑(오전) → 아트 마켓(오후) → 야시장(저녁)",
        "사누르": "1박 2일: 일출(새벽) → 자전거(오전) → 나이트 마켓(저녁)",
        "누사두아": "1박 2일: 리조트 휴양(오전) → 워터블로우(오후) → 뷔페(저녁)",
        "울루와뚜": "당일: 사원(오후) → 케착춤(저녁) → 선셋(저녁)",
        "짠디다사": "1박 2일: 베사키 사원(오전) → 티르타강가(오후) → 비치(저녁)",
        "로비나": "1박 2일: 돌고래 투어(새벽) → 온천(오전) → 비치 BBQ(저녁)",
        "킨타마니": "당일: 화산 트레킹(새벽) → 온천(오전) → 호수 카페(오후)",
        "타나롯": "당일: 사원(오후) → 일몰(저녁) → 시장(저녁)",
        "베두굴": "1박 2일: 울룬다누 사원(오전) → 호수 보트(오후) → 식물원(다음날)",
    }
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()
        parts = f.relative_to(HTML_DIR).parts
        area = parts[0]

        if area not in itineraries:
            continue

        # Add itinerary after budget guide
        budget_pattern = r'(💰 .*? 예산 가이드</p>\s*<p style="margin:8px 0 0;line-height:1\.7;color:#333">.*?</p>)'
        match = re.search(budget_pattern, content, re.DOTALL)
        if match:
            old_budget = match.group(1)
            if "추천 일정" not in old_budget:
                new_budget = old_budget + f'\n<p style="margin:8px 0 0;line-height:1.7;color:#1565c0;font-weight:600">📅 추천 일정: {itineraries[area]}</p>'
                content = content.replace(old_budget, new_budget)
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(content)
                fixed += 1

    print(f"  추가: {fixed}개")
    return fixed


def round10_add_reading_time():
    """읽기 시간 표시 + 가독성 개선"""
    print("Round 10: 읽기 시간 표시 + 가독성 개선")
    fixed = 0
    for f in sorted(HTML_DIR.rglob("*.html")):
        with open(f) as fh:
            content = fh.read()

        # Calculate reading time
        article = re.search(r"<article>(.*?)</article>", content, re.DOTALL)
        if not article:
            continue
        text = re.sub(r"<[^>]+>", "", article.group(1)).strip()
        words = len(text)
        reading_time = max(1, words // 500)  # ~500 chars per minute for Korean

        # Add reading time after meta line
        meta_pattern = r'(<div class="meta">)(.*?)(</div>)'
        meta_match = re.search(meta_pattern, content)
        if meta_match and "⏱️" not in meta_match.group(2):
            old_meta = meta_match.group(0)
            new_meta = f'{meta_match.group(1)}{meta_match.group(2)} | ⏱️ 약 {reading_time}분 읽기{meta_match.group(3)}'
            content = content.replace(old_meta, new_meta)

            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content)
            fixed += 1

    print(f"  추가: {fixed}개")
    return fixed


if __name__ == "__main__":
    total = 0
    for i, func in enumerate([
        round1_add_blogger_tips,
        round2_fix_duplicate_tips,
        round3_fix_episodes,
        round4_fix_image_alt,
        round5_add_figcaption,
        round6_improve_qa_questions,
        round7_add_krw_prices,
        round8_enhance_hidden_gems,
        round9_add_budget_itinerary,
        round10_add_reading_time,
    ], 1):
        result = func()
        total += result
        print()
    print(f"=" * 60)
    print(f"✅ 총 10라운드 완료: {total}개 수정")
    print(f"=" * 60)
