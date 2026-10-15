# 오행 신수 로스터 (roster.json 요약)

- 상태: 초안 v0.1. 원본 `pokemon-splendor/src/data/cards.js` 90장 1:1 대응. sprite 키 = 카드 id.
- 코드 키(monster/super/hyper/heal/quick/master)는 유지, 표시명·색만 교체.

## 1. 색 매핑
| 코드 키 | 기운 | 토큰 | hex | 원본 |
|---|---|---|---|---|
| monster | 火 | 화령주 | #D9453B | 몬스터볼 |
| super | 水 | 수령주 | #1F2F5C | 슈퍼볼 |
| hyper | 土 | 토령주 | #D9A633 | 하이퍼볼 |
| heal | 木 | 목령주 | #3FA56B | 힐볼 |
| quick | 金 | 금령주 | #E6E4DA | 퀵볼 |
| master | 특수 | 여의주 | #9FE8F0 (accent #F2D16B) | 마스터볼 |

매핑 근거: 원본 볼 색상 인상(몬스터=적, 슈퍼/퀵=청/백, 하이퍼=황, 힐=분홍/녹)에 가장 가까운 기운 배정. 水(#1F2F5C)는 어두워 UI 배경에서 대비 확인 필요(아트).

## 2. archetype 분포 (90)
| archetype | 수 | archetype | 수 |
|---|---|---|---|
| bird | 12 | serpent | 8 |
| critter | 12 | insect | 8 |
| spirit | 12 | turtle | 7 |
| fish | 9 | feline | 6 |
| canine | 6 | hoofed | 6 |
| bear | 4 | | |

## 3. 진화 라인 (T1 -> T2 -> T3)
| 라인 | 계열 | 이름 |
|---|---|---|
| 001 | feline | 불씨범 > 홍염범 > 적염산군 |
| 002 | turtle | 남생이 > 물남생 > 흑수귀왕 |
| 003 | bear | 굴곰이 > 황토곰 > 토산웅왕 |
| 004 | insect | 잎누에 > 초록고치 > 청엽나비 |
| 005 | insect | 바늘벌 > 은침벌 > 백침말벌 |
| 006 | bird | 홍참새 > 불까치 > 적염수리 |
| 007 | spirit | 안개정령 > 물도깨비 > 수신대왕 |
| 008 | spirit | 아기장승 > 돌장승 > 천하대장군 |
| 009 | spirit | 산삼동이 > 산삼동자 > 천년삼왕 |
| 010 | critter | 아기천산 > 쇠천산갑 > 금강천산갑 |
| 011 | fish | 홍붕어 > 불잉어 > 화린대어 |
| 012 | serpent | 물구렁이 > 이무기 > 묵룡 |
| 013 | critter | t1-013 홍다람쥐 > t2-013 황갈다람쥐 |
| 016 | serpent | t1-016 황토뱀 > t2-014 청살모사 |
| 017 | canine | t1-017 달여우 > t2-015 삼미호 |
| 018 | critter | t1-018 달토끼 > t2-016 옥토끼 |
| 019 | bird | t1-019 쇠박쥐 > t2-017 은날개박쥐 |
| 020 | critter | t1-020 청개구리 > t2-018 불두꺼비 |
| 021 | insect | t1-021 물방개 > t2-019 홍갑충 |
| 022 | critter | t1-022 두더지 > t2-020 물두더지 |
| 023 | feline | t1-023 새끼삵 > t2-021 숲삵 |
| 024 | bird | t1-024 새끼원앙 > t2-022 황원앙 |
| 025 | canine | t1-025 삽살이 > t2-023 불삽살개 |
| 026 | fish | t1-026 꽃해파리 > t2-024 독해파리 |
| 027 | hoofed | t1-027 망아지 > t2-025 청총마 |
| 028 | hoofed | t1-028 불송아지 > t2-026 철우 |
| 029 | spirit | t1-029 쇠도깨비 > t2-027 도깨비장군 |
| 030 | bird | t1-030 아기두루미 > t2-028 청학 |
| 031 | fish | t1-031 아기물범 > t2-029 점박물범 |
| 033 | turtle | t1-033 물조개 > t2-030 진주조개 |

- 진화 없음(evolvesTo null) T1: t1-014 초록들쥐, t1-015 쇠솔개, t1-032 진흙귀, t1-034 화암뱀, t1-035 바다별.
- 단독 T3(선행 라인 없음): t3-013 등룡어, t3-014 벽해거북, t3-015 금각맹우.
- 진화 시 element(bonus)는 원본 데이터대로 바뀌는 라인이 있음(예: t1-013 火 > t2-013 土). 외형 archetype은 라인 내 고정.

## 4. R/L 목록
| id | 이름 | element / element2 | archetype | 원본 점수 |
|---|---|---|---|---|
| rare-001 | 현무 | 水 / 土 | turtle | 4 |
| rare-002 | 주작 | 火 / 水 | bird | 3 |
| rare-003 | 청룡 | 木 / 金 | serpent | 3 |
| rare-004 | 황룡 | 土 / 木 | serpent | 3 |
| rare-005 | 백호 | 金 / 火 | feline | 4 |
| legend-001 | 불가사리 | 金 / 水 | bear | 4 |
| legend-002 | 기린 | 木 / 火 | hoofed | 5 |
| legend-003 | 봉황 | 火 / 土 | bird | 5 |
| legend-004 | 해태 | 水 / 木 | canine | 6 |
| legend-005 | 구미호 | 土 / 金 | canine | 4 |

주의: 사신의 전통 오행(청룡=木 등)과 원본 bonus 쌍이 어긋나는 경우가 있어(예: 주작 火+水) element는 원본 bonus 첫 항목을 따랐다. 전통 오행과 맞추려면 R/L 이름 배정을 bonus 쌍에 맞춰 재배치 가능.

## 5. 전체 카드 표
전체 90장의 element/archetype/features/palette/desc는 `roster.json`의 `cards` 참조.
