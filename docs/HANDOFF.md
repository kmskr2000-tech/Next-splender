# 세션 인계 메모 (2026-10-14)

새 세션은 이 파일과 `CLAUDE.md`, `docs/design/decisions.md`부터 읽는다.

## 현재 상태
- 작업 브랜치: `claude/ohaeng-reskin` (main에는 팀 에이전트·CLAUDE.md만 머지됨)
- 게임: pokemon-splendor 포크(vanilla JS), 멀티 전용, 세로·스마트폰 전용, TFT식 UI, 밝은 한지 테마
- 컨셉: 한국 문화(전래동화·설화·고대~조선 역사)만 (D15). 확정 로스터 90장 = `docs/design/roster-korea.json` (D16)
- 자원: 노리개·나전함·복주머니·청자·백자 + 와일드 마패 (D14). 귀족 없음 (D9)
- 모드: 일반전·랭킹전(조선 품계 20단계, 시범 시즌 0), 꾸미기 카탈로그·상점 골격(결제 코드 없음)
- 스프라이트: 절차적 도트 생성기 `tools/sprites/` (96×96, 13 아키타입) → `assets/creatures/*.png`,
  호흡 GIF `tools/sprites/breathe_idle.py`(sprite-gen v2.44.0 Breathe), 크롭 `tools/sprites/spritebox.py` → `src/ui/spritebox.js`
- 데이터: `tools/data/gen_roster_js.py`가 roster-korea.json → `src/data/roster.js`, cards.js 이름 동기화
- 테스트: `node tests/rating.test.mjs`, `node tests/meta.test.mjs`, `node tests/ranked-shots.mjs`(Playwright)

## 다음 할 일: PixelLab
- 계획서: `docs/art/pixellab-plan.md`. MCP 설정: `.mcp.json` (키는 env `PIXELLAB_API_KEY`에서만 읽음, 커밋 금지)
- 1단계: `get_balance`로 연결·잔액 확인
- 2단계: 현재 도트 3장(이순신·세종·도깨비)을 style_images로 대표 인물 시안 → 기존 생성기 결과와 인게임 비교 후 사용자 결정
- 결과는 96×96 투명 PNG로 정규화 → spritebox.py → breathe_idle.py

## 사용자 결정 대기
1. t3-015 처용 확정 vs 산군(호랑이)
2. 무조신 바리 두 번째 소품: 꽃가지(현재) vs 부채
3. 이모트 `emo_tiger`('호랑이 울음') 유지/교체

## 사용자 측 미해결
- Firebase 규칙에 `ohsp-rooms` 추가(또는 새 Firebase 프로젝트) — 온라인 매칭 전제
- 게임 제목: '스플렌더' 상표 충돌 가능성 검토 필요
- 참조 원본 버그 B1~B5 미수정 (`docs/design/rules-baseline.md`), 서버 권한(D8) 설계 미착수
