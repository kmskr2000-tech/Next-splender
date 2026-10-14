# 리스킨 문자열 전수 조사 (1단계)
대상: index.html, css, src/** (cards.js 제외, 별도 섹션). 작성: 프로그래밍팀. 교체는 roster.json 확정 후 디렉터 지시.
검색 패턴: 포켓몬/몬스터/마스터볼/슈퍼볼/하이퍼/힐볼/퀵볼/볼/트레이너/도감/진화/잡-/희귀/전설/환상/챔피언/지우/이슬/웅이/로이/Pok*. 줄 번호는 이 문서 작성 시점 기준.
이미 변경됨: 타이틀 '포켓몬 스플렌더' -> '오행 스플렌더' (index.html:7, view.js 2곳), 부제 POKEMON SPLENDOR -> OHAENG SPLENDOR.
## 1. 구조적 의존 (키/식별자, 문구 교체 시 같이 손봐야 함)
| 위치 | 내용 |
|---|---|
| src/core/constants.js:3 | 색 키 `monster/super/hyper/heal/quick` + `master` (엔진/AI/CSS 변수 `--monster` 등 전역 사용). 표시명은 controller.js BALLS 에서만 바뀜. 키 이름 변경은 대규모라 비권장, 오행 매핑은 표시명/아이콘만 교체 권장 |
| css/style.css:9 | `--monster/--super/--hyper/--heal/--quick/--master` 색상값. 오행 색(목화토금수)으로 교체 대상 |
| src/data/cards.js | `dex` 필드(전국도감번호), 카드 `name`(포켓몬 이름 90개). id 기반 스프라이트로 이미 전환. `dex` 는 view.js:508 도감 정렬에만 쓰임 |
| src/storage/store.js:5-9,28-70 | `DEX_KEY`, `loadDex/recordCatch/dexSummary` 등 내부 이름 dex (표시와 무관, 유지 가능). 키 접두 `pks-` |
| src/net/fireroom.js:22 / peerroom.js:9 / session.js:51,56,62 | `pkmspl-` 접두 (Firebase 경로, PeerJS ID, rejoin 키). 5번 Firebase 판단 참조 |
| src/core/engine.js:1 | 주석 'Pokemon Splendor rule engine' |

## 2. 문자열 위치 표

| 파일:라인 | 내용 |
|---|---|
| index.html:24 | `<div class="lbl">■ 볼 공급처 (탭해서 고르기)</div>` |
| src/core/engine.js:1 | `// Pokemon Splendor rule engine. Pure functions over a plain-JSON state.` |
| src/data/achievements.js:9 | `{ id: 'no-evo-win', icon: '🌱', name: '순수 육성', desc: '진화 없이 승리하기', check: (c) => c.won && c.evolutions === 0 },` |
| src/data/achievements.js:10 | `{ id: 'evo-master', icon: '🌀', name: '진화 마스터', desc: '한 게임에서 5회 진화하기', check: (c) => c.evolutions >= 5 },` |
| src/data/achievements.js:12 | `{ id: 'legend-catch', icon: '✨', name: '전설 포획', desc: '전설·환상 포켓몬 잡기', check: (c) => c.caughtLegend },` |
| src/data/achievements.js:13 | `{ id: 'hard-win', icon: '👑', name: '진정한 챔피언', desc: '어려움 난이도에서 승리하기', check: (c) => c.won && c.difficulty =...` |
| src/data/challenges.js:28 | `name: '진화의 길',` |
| src/data/challenges.js:29 | `desc: '20턴 안에 3회 진화하기',` |
| src/data/challenges.js:48 | `name: '전설 사냥',` |
| src/data/challenges.js:49 | `desc: '25턴 안에 희귀·전설 2장 잡기',` |
| src/data/challenges.js:58 | `name: '챔피언의 증명',` |
| src/data/challenges.js:72 | `if (g.evolutions != null) return { cur: me.evolved.length, target: g.evolutions, label: '진화' };` |
| src/net/session.js:66 | `return String(n \|\| '').trim().slice(0, 12) \|\| '트레이너';` |
| src/net/session.js:178 | `const pool = ['지우', '이슬', '웅이', '로이'].filter((n) => !this.names.includes(n));` |
| src/storage/store.js:1 | `// localStorage persistence: Pokedex (cumulative caught record) and the in-progress game save.` |
| src/storage/store.js:28 | `// ---------- Pokedex ----------` |
| src/ui/controller.js:12 | `monster: { file: 'monster', name: '몬스터볼', short: '몬스터' },` |
| src/ui/controller.js:13 | `super: { file: 'super', name: '슈퍼볼', short: '슈퍼' },` |
| src/ui/controller.js:14 | `hyper: { file: 'hyper', name: '하이퍼볼', short: '하이퍼' },` |
| src/ui/controller.js:15 | `heal: { file: 'heal', name: '힐볼', short: '힐' },` |
| src/ui/controller.js:16 | `quick: { file: 'quick', name: '퀵볼', short: '퀵' },` |
| src/ui/controller.js:17 | `master: { file: 'master', name: '마스터볼', short: '마스터' },` |
| src/ui/controller.js:20 | `export const TRAINERS = ['지우', '이슬', '웅이', '로이'];` |
| src/ui/controller.js:23 | `bad_ball_count: '서로 다른 볼 3개를 골라주세요 (남은 종류가 적으면 그만큼만).',` |
| src/ui/controller.js:24 | `supply_empty: '공급처에 없는 볼이에요.',` |
| src/ui/controller.js:25 | `supply_too_low: '같은 볼 2개는 공급처에 4개 이상 남아야 해요.',` |
| src/ui/controller.js:27 | `cannot_reserve: '희귀·전설 카드는 찜할 수 없어요.',` |
| src/ui/controller.js:29 | `cannot_afford: '볼이 부족해서 잡을 수 없어요.',` |
| src/ui/controller.js:30 | `master_required: '희귀·전설은 마스터볼이 1개 필요해요.',` |
| src/ui/controller.js:33 | `discard_owned: '가진 볼보다 많이 반환할 수 없어요.',` |
| src/ui/controller.js:34 | `cannot_evolve: '진화할 수 없어요.',` |
| src/ui/controller.js:56 | `export function createController({ cards, seed, humanName = '나', aiNames = ['지우', '이슬', '웅이'], resume = nul...` |
| src/ui/controller.js:296 | `if (card.tier === 'rare' \|\| card.tier === 'legend') return '보너스 2개 · 마스터볼 필수';` |
| src/ui/controller.js:297 | `return card.tier === 3 ? '최종 진화' : '진화 없음';` |
| src/ui/controller.js:311 | `case 'reserve': return `${who}: ${ev.source === 'deck' ? '덱 위 카드를' : `${name(ev.cardId)}을(를)`} 찜${ev.gotMas...` |
| src/ui/controller.js:312 | `case 'buy': return `${who}: ${name(ev.cardId)} 잡음!`;` |
| src/ui/controller.js:314 | `case 'evolve': return `${who}: ${name(ev.from)} → ${name(ev.to)} 진화!`;` |
| src/ui/main.js:58 | `const AI_NAMES = ['지우', '이슬', '웅이', '로이'];` |
| src/ui/main.js:412 | `return clean \|\| '트레이너';` |
| src/ui/view.js:20 | `'지우': 'trainer-1',` |
| src/ui/view.js:21 | `'이슬': 'trainer-2',` |
| src/ui/view.js:22 | `'웅이': 'trainer-3',` |
| src/ui/view.js:23 | `'로이': 'trainer-4',` |
| src/ui/view.js:34 | `const tierLabel = { 1: '1단계', 2: '2단계', 3: '3단계', rare: '희귀', legend: '전설' };` |
| src/ui/view.js:130 | `<div class="olbl2">가진 볼</div>` |
| src/ui/view.js:132 | `<div class="meta">찜 ${p.hand.length} · 포켓몬 ${p.tableau.length}마리<br><span class="more">눌러서 자세히</span></div>` |
| src/ui/view.js:168 | `if (!me.tableau.length) return '<div class="empty-note">아직 잡은 포켓몬이 없어요</div>';` |
| src/ui/view.js:177 | `${evolvable.has(card.id) ? '<span class="ev">진화 가능!</span>' : ''}</button>`).join('')}</div>`;` |
| src/ui/view.js:196 | `<div class="tkcount ${tc >= 10 ? 'full' : ''}">볼 ${tc}/10</div>` |
| src/ui/view.js:197 | `<div class="evcount">진화 ${me.evolved.length}회</div>` |
| src/ui/view.js:201 | `<div class="lbl">■ 보유 볼</div>` |
| src/ui/view.js:203 | `<div class="lbl">■ 내 포켓몬 (${me.tableau.length})</div>` |
| src/ui/view.js:221 | `return `<div class="hint">볼이 10개를 넘었어요. 내 볼을 눌러 <b>${need}개</b> 반환하세요. 누를 때마다 +1, 빨간 − 로 되돌려요. (${have}/${n...` |
| src/ui/view.js:229 | `return `<button class="btn evo" data-action="evolve" data-card="${o.cardId}">${from.name} → ${to.name} 진화</...` |
| src/ui/view.js:231 | `return `<div class="hint evohint">진화할 수 있어요! 한 마리만 골라 진화하거나 건너뛰세요.</div>${err}` |
| src/ui/view.js:232 | `<div class="btnrow col">${opts}<button class="btn ghost" data-action="skip-evolve">진화 안 함</button></div>`;` |
| src/ui/view.js:241 | `let hint = '볼을 고르거나, 카드를 눌러 잡기·찜하기를 하세요.';` |
| src/ui/view.js:244 | `hint = valid ? `${names} 선택! 가져가기를 눌러 턴을 마치세요.` : `${names} 선택 중 — ${pe ? ({ bad_ball_count: '서로 다른 볼을 3개까지...` |
| src/ui/view.js:246 | `const label = n === 2 && ctrl.balls[0] === ctrl.balls[1] ? `${BALLS[ctrl.balls[0]].name} 2개 가져가기` : (n ? `볼...` |
| src/ui/view.js:267 | `body = card ? `${staticSprite(card)}<b>${card.name}</b> 잡음!` : '포켓몬 잡음!';` |
| src/ui/view.js:274 | `body = from && to ? `${staticSprite(from)} → ${staticSprite(to)}<b>진화!</b>` : '진화!';` |
| src/ui/view.js:295 | `<div class="sheet-title">${trainerFaceSrc(p.name) ? `<img class="tface big" src="${trainerFaceSrc(p.name)}"...` |
| src/ui/view.js:298 | `<div class="olbl">■ 가진 볼 (${tokenCount(p)}/10)</div>` |
| src/ui/view.js:300 | `<div class="olbl">■ 포켓몬 (${p.tableau.length}마리)</div>` |
| src/ui/view.js:317 | `? `<span class="need lack">${ballImg(MASTER, 'mini2')}마스터볼 필요</span>` : '';` |
| src/ui/view.js:318 | `return parts + masterNote \|\| '볼이 부족해요';` |
| src/ui/view.js:339 | `<div class="paylbl">진화 정보</div>` |
| src/ui/view.js:347 | `<p class="sheet-p">뒷면 그대로 찜해요. 마스터볼이 남아 있으면 1개를 받아요.</p>` |
| src/ui/view.js:363 | `const reserveNote = inHand ? '' : isSpecial(card) ? '희귀·전설은 찜 불가' : !ctrl.canReserve() ? '찜 한도(3장) 초과' : '';` |
| src/ui/view.js:365 | `const reserveLabel = masterLeft ? '찜하기 (+마스터볼)' : '찜하기 (마스터볼 품절)';` |
| src/ui/view.js:370 | `<div class="paylbl">내가 낼 볼 (보너스 할인 적용)</div>` |
| src/ui/view.js:375 | `<button class="btn primary" data-action="buy" data-card="${card.id}" ${pay ? '' : 'disabled'}>포켓몬 잡기</button>` |
| src/ui/view.js:390 | `<p class="sheet-p">트레이너를 골라 AI 3명과 4인전을 시작해요.<br>21점을 먼저 모으는 트레이너가 승리!</p>` |
| src/ui/view.js:400 | `<div class="btnrow"><button class="btn alt" data-action="dex">도감 ${sum ? `${sum.caught}/${sum.total}` : ''}...` |
| src/ui/view.js:418 | `<p>① <b>서로 다른 볼 3개</b> 가져오기 (마스터볼 제외)<br>` |
| src/ui/view.js:419 | `② <b>같은 볼 2개</b> 가져오기 (공급처에 4개 이상 남았을 때만)<br>` |
| src/ui/view.js:420 | `③ <b>카드 찜하기</b> (최대 3장, 마스터볼 1개를 받아요 · 마스터볼은 5개 한정이라 품절되면 찜만 돼요 · 희귀/전설은 찜 불가)<br>` |
| src/ui/view.js:421 | `④ <b>포켓몬 잡기</b> (볼을 내고 카드를 가져와요)<br>` |
| src/ui/view.js:422 | `<span style="color:#4ade80">■</span> <b>초록 테두리</b>=지금 바로 잡을 수 있음 · <span style="color:#60a5fa">■</span> <b>...` |
| src/ui/view.js:424 | `<p>잡은 포켓몬의 보너스 1개(희귀/전설은 2개)마다 해당 볼 1개씩 영구 할인! 게임 끝까지 유지돼요.</p>` |
| src/ui/view.js:425 | `<h4>■ 진화</h4>` |
| src/ui/view.js:426 | `<p>내 턴이 끝나면, 필요한 보너스를 가진 포켓몬은 다음 단계로 <b>진화</b>할 수 있어요. 점수와 보너스가 올라가요. (1→2→3단계만 가능)</p>` |
| src/ui/view.js:427 | `<h4>■ 볼 10개 제한</h4>` |
| src/ui/view.js:428 | `<p>마스터볼 포함 10개를 넘기면, 초과분을 골라 반환해야 해요.</p>` |
| src/ui/view.js:429 | `<h4>■ 마스터볼</h4>` |
| src/ui/view.js:430 | `<p>어떤 볼이든 1개로 대체할 수 있는 만능 볼! <b>희귀/전설 포켓몬을 잡으려면 마스터볼 1개가 꼭 필요</b>해요.</p>` |
| src/ui/view.js:432 | `<p>① 진화 횟수가 많은 쪽 → ② 그래도 동점이면 앞면 포켓몬이 적은 쪽이 이겨요.</p>` |
| src/ui/view.js:441 | ``<b>STEP 1</b> 볼을 모아보세요!<br>서로 다른 볼 3개를 누른 뒤 <b>[가져가기]</b>를 누르세요.`,` |
| src/ui/view.js:442 | ``<b>STEP 2</b> 포켓몬을 잡아보세요!<br>카드를 누르면 필요한 볼을 확인할 수 있어요. 볼이 모자라면 몇 턴 더 모아보세요.`,` |
| src/ui/view.js:443 | ``<b>STEP 3</b> 보너스 획득!<br>잡은 포켓몬의 보너스 색 볼은 게임 끝까지 1개씩 영구 할인돼요.`,` |
| src/ui/view.js:444 | ``<b>STEP 4</b> 21점을 먼저 모으면 승리!<br>카드를 미리 <b>[찜하기]</b>로 확보하거나, 보너스를 모아 <b>진화</b>시켜보세요. 행운을 빌어요!`,` |
| src/ui/view.js:481 | `if (s.phase === PHASES.DISCARD) return '볼이 10개를 넘었어요. 아래 내 볼을 눌러 초과분을 반환하세요.';` |
| src/ui/view.js:482 | `if (s.phase === PHASES.EVOLVE) return '진화 찬스! 조건을 만족한 포켓몬을 진화시키면 점수와 보너스가 올라가요.';` |
| src/ui/view.js:487 | `? '좋아요! [가져가기]를 누르면 볼을 가져오고 턴이 끝나요.'` |
| src/ui/view.js:488 | `: '서로 다른 볼 3개, 또는 같은 볼 2개(공급처에 4개 이상 남았을 때)를 고를 수 있어요.';` |
| src/ui/view.js:492 | `if (card && ctrl.canBuy(card.id)) return '지금 바로 잡을 수 있는 포켓몬이 있어요! 반짝이는 카드를 눌러보세요.';` |
| src/ui/view.js:495 | `return '21점이 목표! 볼을 모아서 포켓몬을 잡으세요. 보너스가 쌓이면 할인이 커져요.';` |
| src/ui/view.js:512 | `? `<div class="dexcell got"><img src="${pokeSrc(c.id)}" alt="${c.name}"><span class="dn">${c.name}</span><s...` |
| src/ui/view.js:517 | `<div class="title big">도감<small>잡은 포켓몬 ${sum.caught}/${sum.total} · ${g.played}판 ${g.won}승</small></div>` |
| src/ui/view.js:527 | `return `<tr class="${r.rank === 1 ? 'win' : ''} ${p.id === ctrl.human ? 'me' : ''}"><td>${r.rank}</td><td>$...` |
| src/ui/view.js:537 | `<p class="sheet-p">동점은 진화 횟수가 많은 쪽 → 앞면 포켓몬 수가 적은 쪽이 이겨요.</p>` |
| src/ui/view.js:538 | `<div class="btnrow"><button class="btn alt" data-action="dex">도감</button>` |

## 3. 카드 이름 / AI 이름 / 기타

- 카드 이름 90개: src/data/cards.js (`name:`). roster.json 의 id 매칭으로 일괄 치환 스크립트 권장.
- AI/트레이너 이름 ['지우','이슬','웅이','로이'] 4곳 동일 목록: src/ui/controller.js:20 (TRAINERS), controller.js:56 (aiNames 기본값 3명), src/ui/main.js:58 (AI_NAMES), src/net/session.js:178 (게스트 AI 풀). 추가로 view.js:20-23 TRAINER_FACE 키. 이름이 바뀌면 5곳 동시 수정.
- 기본 이름 '트레이너': session.js:66, main.js:412.
- 업적(achievements.js 8개) / 도전(challenges.js 6개): 위 표의 진화·전설·챔피언·포켓몬 포함 항목 + 이름 '순수 육성','진화 마스터','전설 포획','진정한 챔피언','전설 사냥','챔피언의 증명' 검토.
- AI 성격/난이도 문구는 ai/heuristic.js 에 한글 문자열 없음(확인 필요 시 grep 결과 0건).
- view.js 도움말(약 417-432행), 튜토리얼 STEP(441-444행), 상황 힌트(481-495행)에 규칙 설명형 문구 다수: 표 참조.
- 이모지 아이콘(업적 🏆⚡💯🌱🌀🌈✨👑)은 IP 무관, 유지 가능.
