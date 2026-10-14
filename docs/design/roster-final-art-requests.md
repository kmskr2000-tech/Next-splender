# 아트팀 요청: 한국 로스터 v2-final 신규 sprite 값

기준: `roster-korea.json` (v2-final, D16). 수치·슬롯 불변. 톤 가이드는 `roster-swap-v2.md` (e).

## 1. person.py 신규 값
| 종류 | 값 | 사용 카드 | 비고 |
|---|---|---|---|
| props | mapae | t2-014 이몽룡 | 마패. 장식 소품만 |
| props | flower_branch | t2-008 바리공주, t3-008 무조신 바리, t3-015 처용(모란 대용) | 꽃가지 |
| props | shaman_bell | t3-008 무조신 바리 | 무구 방울. 무복 고증 확인 |
| props | swing_rope | t1-024 광한루 춘향 | 그네 줄 |
| props | cloud_scroll | t3-014 전우치 | 구름 두루마리(도술) |
| props | mirror | t1-034 팥쥐 | 거울 |
| expression | smirk | t1-034 팥쥐 | 가벼운 시샘. 외모 비하·악랄한 표정 금지 |

기존 값 재사용 확인 요청: headwear hwagwan/samo/monk/crown/topknot/gat/paeraengi/braid, outfit shaman/official/scholar/monk/royal, props gourd_bowl/staff/lotus/book/fan/scroll/hwando/gourd, crown_style flame, blush, sash, pal.

## 2. 신규/변경 카드 스프라이트 (사람)
서자 길동(t1-022), 활빈당 홍길동(t2-020), 남원 도령(t1-016), 이몽룡(t2-014), 승려 선종(t1-013), 미륵왕 궁예(t2-013), 광한루 춘향(t1-024), 정렬부인 춘향(t2-022), 버려진 공주(t1-008), 바리공주(t2-008), 무조신 바리(t3-008), 팥쥐(t1-034), 전우치(t3-014), 처용(t3-015). 총 14명.
- 궁예: 한쪽 눈 가림 등 장애 희화 금지, 폭군·광인 연출 금지. 왕건 카드와 선악 대비 금지.
- 무조신: 굿 의상 고증. 희화 금지.
- 처용: 처용탈 인상은 붉은 얼굴·사모·모란 정도로 암시. 탈 자체를 씌우지 않아도 됨(아트 판단).

## 3. 크리처 (기존 archetype + features, 신규 archetype 없음)
| id | 이름 | archetype | features | palette (main/accent/detail) |
|---|---|---|---|---|
| rare-004 | 청룡 | serpent | horns, whiskers, mane, scales, cloud, aura | #2E9C8A / #E3B130 / #14493E |
| legend-001 | 백호 | feline | stripes, mane, aura | #F1EEE4 / #343B4D / #3F4A58 |
| rare-002 | 주작 | bird | crest, multi_tail(3), flame, aura | #D63B35 / #F2A33A / #12151F |
| legend-004 | 현무 | turtle | shell, multi_tail(2) (뱀 꼬리로 표현), aura | #343B4D / #2E9C8A / #12151F |
| t1-035 | 두억시니 | spirit | cloud, aura, spots | #343B4D / #8FA3C9 / #12151F |

- 확인 요청: bird/turtle 의 multi_tail 지원 여부. 미지원 시 turtle 에 뱀 꼬리 변형 필요.
- 사신 4장은 한 벌 느낌의 통일된 외곽선/아우라 처리 권장. 고구려 강서대묘 사신도 근거.
- 두억시니: 어둠/연기 형상, 인간형 외모 회피.

## 4. 제거된 sprite (불필요)
object shape pillar, persimmon. egg variant tall. person: 혹부리 wen. 제거 카드: 장승 3종, 정약용 2, 나정의 알, 박혁거세, 혹부리 2, 곶감, 물귀신, 퇴계, 김수로 2, 저승사자, 호랑이, 불가사리, 해태.
