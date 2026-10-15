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

## PixelLab 카드 인물 (D17, 완료)
- 90장 PixelLab 도트로 교체 완료: 재디자인(왕관·관복 인물 차별화) → 인물별 표정 → 역동적 자세 순으로 반복, 사물 8장은 1차본 유지
- 시트: `docs/art/pixellab/roster90-v3.png` (v1·v2는 이전 단계)
- 재현: `tools/pixellab/prompts.json`(common/items/expressions/poses), `objects.json`(카드↔PixelLab 오브젝트 ID)
- 대기 모션: PixelLab v3 4프레임(`animate_all.py`) → `fetch_build.py <repo> <cache>`로 PNG·GIF 동시 정규화
  - 불량 9장은 `motion_reject.txt` → `idle_gif.py` 1px 숨쉬기
  - 카드 CSS `.card .art .sprite` 미세 흔들림(카드별 위상, reduced-motion 시 끔)
- 스프라이트 바꾼 뒤엔 `python -I tools/sprites/spritebox.py .` 필수
- 네트워크: backblaze.pixellab.ai 차단 → API ZIP 경유. 크레딧 2000/월(11-14 갱신), 약 530 사용
- 작업 현황 대시보드: https://claude.ai/artifact/Chfo6uoUY7dAEKr4tFxFgw (비공개)

## 사용자 결정 대기
1. 이모트 `emo_tiger`('호랑이 울음') 유지/교체
(처용 확정·바리 꽃가지 확정·후광 대신 등급 이펙트 = D19)

## 사용자 측 미해결
- Firebase 규칙에 `ohsp-rooms` 추가(또는 새 Firebase 프로젝트) — 온라인 매칭 전제
- 게임 제목: '스플렌더' 상표 충돌 가능성 검토 필요
- 참조 원본 버그 B1~B5 미수정 (`docs/design/rules-baseline.md`), 서버 권한(D8) 설계 미착수
