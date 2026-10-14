# PixelLab 활용 계획 (문서 https://api.pixellab.ai/mcp/docs 기준)

## 우리 게임에 쓸 도구
| 용도 | 도구 | 비용(문서 기재) | 비고 |
|---|---|---|---|
| 카드 인물 90장 일괄 | `create_1_direction_object` | 10~25 generations/작업 | size ≤85면 한 번에 **16개** 후보, `item_descriptions`로 인물별 설명, `style_images`(최대 8장)로 화풍 통일 → 약 6작업이면 90장 |
| 단일 인물 빠른 시안 | `create_image_pixflux` / `create_image_pixen` | 1 generation, 10~40초 | 자유 픽셀아트, 리그 없음 |
| 성장 3단계 일관성 | `create_character_state` | 10~25 generations | 같은 인물 정체성 유지하며 복식 변경("wearing general armor") |
| 고품질 단일 캐릭터 | `create_character` mode=v3 | 2~9 generations | 8방향 생성(카드는 south만 사용), 사족보행은 bear/cat/dog/horse/lion 템플릿 |
| 카드 idle 애니메이션 | `animate_character` `breathing-idle` | 1 generation/방향 | south 1방향만 |
| 프로필 아바타 | `create_portrait_character` / `set_character_portrait` | — | 흉상 초상 |
| 잔액 확인 | `get_balance` | 무료 | 남은 크레딧(USD)·구독 generation |

- 모든 생성은 비동기: 생성 호출 → ID 즉시 반환 → `get_*`로 상태 확인 → 다운로드 URL(인증 불필요)
- REST API v2(https://api.pixellab.ai/v2/llms.txt)로 같은 기능을 스크립트 일괄 처리 가능
- 무료 할당량은 문서에 명시 없음 → 연결 후 `get_balance`로 확인

## 파이프라인
1. 스타일 기준 3장 확정: 현재 생성기 스프라이트 중 좋은 것(이순신·세종·도깨비)을 `style_images`로
2. 라인별 1단계 16명씩 `create_1_direction_object`(size 64~80, view sidescroller, 정면) → 검수 `select_object_frames`
3. 2·3단계는 `create_character_state` 또는 같은 방식 + 1단계 이미지를 style 참조
4. 결과를 96x96 투명 PNG로 정규화 → `assets/creatures/{id}.png` → `tools/sprites/spritebox.py`로 크롭 데이터 갱신
5. idle 애니메이션은 상위 등급(희귀·전설)부터

## 연결 조건 (현재 막힘)
- 환경 Network access에 `api.pixellab.ai` 허용
- 시크릿 `PIXELLAB_API_KEY` 등록 → 저장소 `.mcp.json`이 읽음
- 새 세션에서 연결
