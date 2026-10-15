# 미드저니 프롬프트 패키지: 세계관 3안 캐릭터 시안 (D2 개정)

작성: 아트팀. 이미지는 사용자가 미드저니에서 직접 생성한다. 이 문서는 복사해 붙여넣는 용도.

## 0. 방향 요약

- 스타일: 핸드페인팅 질감의 스타일라이즈드 페인터리 일러스트. 2.5D 느낌은 허용, 3D 렌더/플라스틱/CGI 느낌은 배제. 치비 폐기.
- 비율: 정상~약간 과장(영웅적), 굵은 형태, 선명한 실루엣, 강한 색 대비.
- 빛: 따뜻한 자연광. 털/갈기/천/금속 고리 디테일 풍부.
- 카드용: 배경 단순화. 80pt 축소에서도 실루엣 판독 가능해야 함.
- 레퍼런스 이미지를 `--sref`, 이미지 프롬프트, `--oref`로 넣지 말 것. 상용 게임 스크린샷일 가능성이 있어 파생 저작물 리스크가 있다. 스타일은 텍스트로만 묘사하고, 첫 생성물 중 좋은 것을 우리 자체 스타일 레퍼런스로 삼는다.

### 라인 선택

| 안 | 선택 | 이유 |
|---|---|---|
| A 오행 신수 | 새끼 범 → 산군 → 백호(金) | 레퍼런스의 호랑이(줄무늬, 꼬리 고리 장식)와 가장 가깝고, 털/줄무늬 표현이 페인터리 질감에 유리함. 용은 비늘이 매끈해 3D 느낌이 나기 쉬움 |
| B 삼국지 | 의병 → 교위 → 장군 (무관) | 지시대로 |
| C 세계 신화 | 새끼 늑대 → 회색 늑대 → 펜리르 | 털/갈기 디테일이 레퍼런스 강점과 맞고, 불새 계열은 발광 이펙트가 CGI처럼 보이기 쉬움 |

---

## 1. 공통 스타일 블록과 파라미터

프롬프트는 `[캐릭터/장면 설명] + [라인 고정 키워드] + [공통 스타일 블록] + [파라미터]` 순서로 쓴다. 아래 개별 프롬프트에는 이미 모두 합쳐 놓았다.

### 1-1. 공통 스타일 블록 (영어, 고정 문구)

```
hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, ornate handcrafted accessories with metal rings, knots and cloth ribbons, 2.5D fantasy game concept art, single character centered, full body, simple soft background
```

### 1-2. 월드 악센트 (라인별 1줄, 스타일 블록 앞에 붙임)

- A: `East Asian folktale fantasy, Korean mountain spirit tale atmosphere`
- B: `ancient Chinese Three Kingdoms era historical fantasy, original character design`
- C: `Norse northern mythology fantasy, cold pine forest atmosphere`

### 1-3. 공통 파라미터

```
--ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

- 버전: `--v 7` 가정. 다른 버전이면 조정할 것. v6.x는 `--v 6.1`로 바꾸고 캐릭터 일관성은 `--cref`(옴니 레퍼런스 미지원), v7은 `--oref`.
- `--style raw`: 기본은 쓰지 않는다. 미드저니 기본 미학이 회화적 질감에 유리한 편이다. 결과가 너무 매끈하거나 CGI 같으면 `--style raw`를 추가하고 `--stylize`를 50~100으로 낮춰 비교한다.
- `--stylize` 범위: 100~250 권장(기본 150). 낮으면 지시에 충실하나 건조함, 높으면 화려하나 매끈해지고 3D 느낌이 늘 수 있음. 300 이상 비추천.
- `--no`가 약하게 먹으면 본문에 `painted by hand, flat matte surfaces, visible canvas texture`를 추가한다.
- 변형: `--chaos 10~20`으로 시안 다양성 확보(최초 탐색 단계만). 일관성 단계에서는 `--chaos 0`.
- 비교 시트는 `--ar 3:2`(가로 3단계 나란히)로 교체.
- 미드저니 파라미터 이름/동작은 업데이트로 바뀔 수 있다. 에러가 나면 `/help` 또는 공식 문서에서 확인.

---

## 2. 단계 일관성 방법

1. 1단계를 여러 번 뽑아 가장 좋은 1장을 확정한다(실루엣, 질감, 색).
2. 확정 이미지를 2·3단계 생성 시 캐릭터 레퍼런스로 쓴다.
   - v7: 프롬프트 끝에 `--oref [확정 이미지 URL] --ow 100` (옴니 레퍼런스. 닮음이 너무 강해 단계 차이가 안 나면 `--ow` 50~80으로 낮춤. 단계 차이를 키우려면 본문 묘사를 더 강하게)
   - v6.x: `--cref [URL] --cw 60~100`
   - 옴니 레퍼런스는 v7 일부 모드(예: 일부 속도/모드)와 호환이 제한될 수 있다. 에러 시 설정 확인.
3. 고유 색/문양 키워드는 라인별로 고정하고 모든 단계에 같은 문구로 넣는다(아래 프롬프트의 `FIXED` 문구). 단계가 올라가도 바뀌는 것은 크기, 장식량, 자세, 배경 스케일뿐.
4. 확정된 2단계를 3단계의 `--oref`로 써도 된다(1단계보다 3단계와 가까움). 어느 쪽이 나은지 비교.
5. 자체 스타일 레퍼런스: 라인별 가장 만족스러운 결과 1~2장을 이후 모든 시안의 `--sref`로 쓴다. 우리가 생성한 이미지이므로 외부 IP 리스크가 없다. 외부 레퍼런스 이미지는 쓰지 않는다.

### 단계 차이 규칙 (모든 라인 공통)

| 단계 | 크기/비율 | 장식 | 자세/배경 |
|---|---|---|---|
| 1 | 작고 낮은 실루엣, 장식 최소 | 거의 없음(작은 천 한 조각) | 정적, 낮은 시점, 배경 가장 단순 |
| 2 | 중간, 근육/체격 확연히 커짐 | 금속 고리, 매듭, 천 추가 | 당당한 자세, 배경에 은은한 소품 |
| 3 | 화면을 꽉 채우는 거대한 체격, 위엄 | 가장 화려, 갈기/후광/장식 풍성 | 낮은 앵글로 올려다봄, 배경에 웅장한 요소 |

---

## 3. 개별 프롬프트 (복사해서 바로 붙여넣기)

모든 프롬프트는 공통 파라미터가 포함되어 있다. 버전이 다르면 파라미터를 조정할 것.

### 3-A. 오행 신수: 백호(金) 라인

FIXED: `white fur with deep indigo-black stripes, pale gold metal rings, jade green cloth sash with red knots, amber eyes`

**A-1 새끼 범**

```
East Asian folktale fantasy, Korean mountain spirit tale atmosphere, a small tiger cub sitting low on a mossy rock, small body, big paws, curious alert gaze, white fur with deep indigo-black stripes, one tiny pale gold metal ring on the tail, a thin jade green cloth ribbon with a small red knot around the neck, amber eyes, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple soft misty green background --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**A-2 산군 (山君)**

```
East Asian folktale fantasy, Korean mountain spirit tale atmosphere, a powerful adult tiger standing on a rocky ridge, muscular body, confident wide stance, head held high, white fur with deep indigo-black stripes, pale gold metal rings on tail and forelegs, jade green cloth sash with red knots across the chest, a few small hanging charms, amber eyes, thick fur ruff around the neck, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple soft background of pine silhouettes and pale valley mist --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**A-3 백호 (白虎, 金)**

```
East Asian folktale fantasy, Korean mountain spirit tale atmosphere, a colossal majestic white tiger guardian deity seen from a low angle, enormous muscular body filling the frame, long flowing mane-like fur, thick tail with several large pale gold metal rings, white fur with deep indigo-black stripes, ornate pale gold metal rings on legs and tail, layered jade green cloth sashes with red knots flowing in the wind, a gold-and-bronze engraved ornament on the forehead, amber eyes, regal fierce expression, a faint pale gold metallic glow behind the head like a painted halo, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple background of a rocky cliff and a single ancient pine under a soft warm sky --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**A 비교 시트**

```
character evolution lineup sheet, three stages of the same tiger from left to right, small tiger cub, then powerful adult mountain tiger, then colossal majestic white tiger guardian deity, each clearly larger and more ornate than the last, evenly spaced on one ground line, East Asian folktale fantasy, white fur with deep indigo-black stripes, pale gold metal rings, jade green cloth sash with red knots, amber eyes, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, plain soft warm background --ar 3:2 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background, labels, numbers
```

### 3-B. 삼국지: 무관 라인

FIXED: `crimson red and dark teal cloth, aged bronze armor plates, black lacquered leather, white bone-colored sash`. 원본 캐릭터이며 특정 실존 인물 외형을 복제하지 않는다.

**B-1 의병**

```
ancient Chinese Three Kingdoms era historical fantasy, original character design, a young militia volunteer soldier, simple rough cloth tunic in crimson red and dark teal, a worn leather chest guard in black lacquer, a plain cloth headband, holding a wooden-shafted spear, determined youthful face, stocky grounded stance, no helmet, one small bronze buckle, white bone-colored sash, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple soft dusty field background --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**B-2 교위 (校尉)**

```
ancient Chinese Three Kingdoms era historical fantasy, original character design, a seasoned officer commander in mid-ranking armor, aged bronze shoulder plates and scale armor over crimson red and dark teal robes, black lacquered helmet with a short red plume, a long halberd held upright, short beard, stern confident face, broad stance, white bone-colored sash with bronze knots, a small banner on the back with an abstract emblem and no letters, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple soft background with faint fortress wall and banners --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**B-3 장군**

```
ancient Chinese Three Kingdoms era historical fantasy, original character design, a towering legendary general seen from a low angle, massive heroic build, ornate layered aged bronze armor with engraved patterns, large pauldrons, long flowing crimson red and dark teal cape and sashes with bronze knots, black lacquered tall crested helmet with a long crimson plume, a grand polearm with a decorated blade, long braided beard, commanding fierce gaze, white bone-colored sash, large abstract war banners behind with no letters, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple background of a distant army silhouette under a warm dusty sky --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background, specific historical figure likeness
```

**B 비교 시트**

```
character evolution lineup sheet, three stages of the same warrior line from left to right, young militia volunteer in simple cloth, then mid-ranking officer in bronze scale armor with helmet, then towering legendary general in ornate layered armor with cape and banners, each clearly larger and more ornate than the last, evenly spaced on one ground line, ancient Chinese Three Kingdoms era historical fantasy, original character design, crimson red and dark teal cloth, aged bronze armor plates, black lacquered leather, white bone-colored sash, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, 2.5D fantasy game concept art, plain soft warm background --ar 3:2 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background, labels, numbers
```

### 3-C. 세계 신화: 늑대(펜리르) 라인

FIXED: `slate grey fur with a pale silver chest, pale ice-blue eyes, dark iron rings with silver rune-like engraved patterns, deep red cloth strips`

**C-1 새끼 늑대**

```
Norse northern mythology fantasy, cold pine forest atmosphere, a small wolf pup sitting on a snowy mound, small body, big paws, oversized ears, alert gaze, slate grey fur with a pale silver chest, pale ice-blue eyes, one thin dark iron ring on the front leg, a short deep red cloth strip tied at the neck, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple soft pale blue-grey background --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**C-2 회색 늑대**

```
Norse northern mythology fantasy, cold pine forest atmosphere, a large adult grey wolf standing on a rocky outcrop, lean muscular body, head raised, thick fur ruff, slate grey fur with a pale silver chest, pale ice-blue eyes, dark iron rings on the forelegs and neck with silver rune-like engraved patterns, deep red cloth strips flowing from the collar, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple soft background of dark pine silhouettes and pale mist --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**C-3 펜리르**

```
Norse northern mythology fantasy, cold pine forest atmosphere, a gigantic mythic wolf of immense size seen from a low angle, towering body filling the frame, huge shaggy mane, bared fangs, fierce commanding expression, slate grey fur with a pale silver chest, pale ice-blue eyes, heavy broken dark iron shackle rings on legs and neck with silver rune-like engraved patterns, long tattered deep red cloth strips streaming in the wind, subtle cold pale blue rim light on the fur, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur and fabric detail, 2.5D fantasy game concept art, single character centered, full body, simple background of a stormy mountain ridge and tiny pine trees for scale --ar 3:4 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background
```

**C 비교 시트**

```
character evolution lineup sheet, three stages of the same wolf from left to right, small wolf pup, then large adult grey wolf, then gigantic mythic wolf with shaggy mane and broken iron shackles, each clearly larger and more ornate than the last, evenly spaced on one ground line, Norse northern mythology fantasy, slate grey fur with a pale silver chest, pale ice-blue eyes, dark iron rings with silver rune-like engraved patterns, deep red cloth strips, hand-painted stylized painterly illustration, visible brushwork and painted texture, matte gouache and oil paint finish, bold chunky forms, slightly exaggerated heroic proportions, strong readable silhouette, high color contrast, warm natural sunlight, rich fur detail, 2.5D fantasy game concept art, plain soft cool background --ar 3:2 --v 7 --stylize 150 --no 3d render, plastic, CGI, glossy, chibi, cute, kawaii, photograph, realistic photo, text, watermark, logo, frame, border, cluttered background, labels, numbers
```

---

## 4. 생성 순서 체크리스트

1. 라인 하나 선택(예: A). 3개 라인을 병렬로 가도 되나 라인별로 폴더를 분리한다.
2. 1단계 프롬프트를 `--chaos 15`로 4~8회 실행(탐색).
3. 평가 기준(아래)으로 1단계 1장 확정. 마음에 안 들면 `--stylize`, `--style raw` 조정 후 재시도.
4. 확정 이미지 URL을 얻어 2단계 프롬프트 뒤에 `--oref URL --ow 80` 추가, `--chaos 0`으로 실행. 단계 차이가 약하면 `--ow`를 낮춤.
5. 3단계도 같은 방식(1단계 또는 2단계를 oref로).
6. 마음에 드는 결과가 나오면 해당 이미지를 라인 자체 `--sref`로 추가해 나머지 단계 톤을 맞춘다.
7. 3장이 정해지면 비교 시트 프롬프트 실행. 시트가 일관성 없으면 확정 3장을 직접 나란히 합성(후보정)해도 됨.
8. 3D 느낌이 나면: `--style raw` 시도, `--stylize` 하향, 본문에 `flat matte, canvas texture, brush strokes` 강화, `--no` 목록에 `3d, octane, unreal engine, render` 추가.
9. 결과를 아래 기준으로 평가 후 디렉터에게 보고: 라인별 확정 3장, 불합격 사유, 사용한 프롬프트/시드/파라미터 기록.
10. 카드 크기 테스트: 이미지를 80pt(2x면 160px) 폭으로 축소하여 판독 확인.

### 평가 기준

| 항목 | 합격 조건 |
|---|---|
| 실루엣 판독 | 80pt 축소 상태에서 종류(범/무관/늑대)와 단계가 구분됨. 윤곽이 배경과 분리됨 |
| 단계 구분 | 1→2→3 크기, 체격, 장식량이 한눈에 증가. 같은 캐릭터로 보이는 고유 색/문양 유지 |
| 3D 느낌 | 붓질/종이 질감이 보임. 매끈한 하이라이트, 플라스틱 광택, 렌더 조명, 피부/털의 CG 느낌 없음 |
| 색 대비 | 캐릭터와 배경의 명도/색상 대비 충분. 고정 색 3~4개로 요약 가능 |
| 카드 적합 | 배경 단순. 텍스트/워터마크/프레임 없음. 3:4 안에서 머리/발 잘림 없음 |
| 비율 | 치비/귀여움 과다 아님. 정상~영웅 비율 |
| 접근성 | 단계 구분이 색만이 아니라 크기/형태/장식으로도 가능 |
| IP 유사성 | 아래 5장 확인. 의심되면 폐기 후 재생성 |
| 텍스트 | 한자/문자 같은 글자가 생성되면 제거(이미지에 글자 금지) |

---

## 5. IP 회피 체크

공통: 레퍼런스 이미지(상용 게임 추정)의 구도, 캐릭터 조합(붉은 호랑이+푸른 도깨비), 배경 구성(나무다리, 금줄 협곡)을 그대로 재현하지 않는다. 우리 결과물이 레퍼런스와 닮아 보이면 색 조합이나 구도를 바꾼다. 특정 작품명이나 아티스트명을 프롬프트에 넣지 않는다.

| 라인 | 피할 기존 작품 디자인 |
|---|---|
| A 백호 | 레퍼런스의 붉은 호랑이 구도와 꼬리 고리 배치 그대로 재현 금지. 포켓몬(윈디, 레이코 등)의 갈기/문양, 모바일 게임 백호 캐릭터, 쿵푸팬더 타이그리스, 리그 오브 레전드 등 호랑이 스킨, 용과 같은 동양 신수의 기존 게임 일러스트 구도. 파란 줄무늬를 쓸 때 기존 백호 디자인과 비교 |
| B 무관 | 코에이 진삼국무쌍/삼국지 시리즈 인물 디자인, 관우/장비/여포/조운 등 실존 인물의 상징 외형(청룡언월도+긴 수염+녹색 전포, 방천화극+꿩깃 투구, 장팔사모 등) 복제 금지. 특히 3단계 장군은 긴 수염+청룡도 조합과 녹색 전포를 피한다(본 프롬프트는 진홍/청록 천과 청동 갑옷으로 구분). 삼국지 게임 카드 일러스트 구도 |
| C 펜리르 | 갓 오브 워, 마블 토르(펜리스), 모노노케 히메의 모로, 몬스터 헌터, 젤다 늑대 링크, 오카미, 포켓몬(루가루암 등), 원령공주 산 디자인. 가슴의 흰 문양/붉은 눈 늑대 조합은 위 작품에서 흔하므로 얼음빛 푸른 눈과 철 고리로 구분 |

추가 확인 방법: 확정 후보를 이미지 역검색(구글 렌즈 등)에 돌려 기존 작품과 유사한 결과가 상위에 나오는지 확인한다. 유사하면 재생성한다.

### 권리 관련 주의

- 미드저니 결과물의 상업 이용 가능 여부와 저작권 성격은 사용자의 구독 등급과 약관에 따른다. 상용 출시 전에 현재 약관을 확인하고, 필요하면 최종 에셋은 사람이 다시 그리거나 후보정한다.
- 미드저니 생성물은 저작권 보호 범위가 제한될 수 있다는 점을 디렉터가 인지해야 한다(국가별 법리 상이, 법무 확인 필요).
