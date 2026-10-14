// Pure HTML-string renderers. Each takes the controller and returns markup; main.js owns the DOM.
// All text interpolated here comes from our own card data / constants (no user input).

import { COLORS, MASTER, PHASES, TOKEN_KEYS } from '../core/constants.js?v=1791962003';
import { getBonuses, getPoints, tokenCount, bonusList, isSpecial } from '../core/engine.js?v=1791962003';
import { BALLS, TRAINERS, evoText } from './controller.js?v=1791962003';
import { dexSummary } from '../storage/store.js?v=1791962003';
import { ACHIEVEMENTS } from '../data/achievements.js?v=1791962003';
import { ROSTER, LINES } from '../data/roster.js?v=1791962003';
import { resolveCardSprite, avatarFrameClass, cardFrameClass, titleOf, owns, isEquipped } from '../meta/cosmetics.js?v=1791962003';
import { CATALOG, CATEGORIES, itemById, isFree, itemName } from '../meta/catalog.js?v=1791962003';
import { RANKED, SEASON_LABEL, RANKED_UNLOCK } from '../meta/config.js?v=1791962003';
import { displayOf } from '../meta/rating.js?v=1791962003';


const ASSET = 'assets';
export const ballSrc = (key) => `${ASSET}/items/${BALLS[key].file}.png`;
const pokeSrc = (id, mine = false) => (mine ? resolveCardSprite(id, myEquipped) : `${ASSET}/creatures/${id}.png`);
const animSrc = (id) => `${ASSET}/creatures/anim/${id}.gif`;

// AI trainer face portraits by name.
const TRAINER_FACE = {
  '하늘': 'trainer-1',
  '솔이': 'trainer-2',
  '바우': 'trainer-3',
  '달래': 'trainer-4',
};
export const trainerFaceSrc = (name) => TRAINER_FACE[name] ? `${ASSET}/trainers/${TRAINER_FACE[name]}.webp` : null;

const hj = (k) => (BALLS[k].hanja ? `<i class="hj" aria-hidden="true">${BALLS[k].hanja}</i>` : '');
const ballImg = (key, cls = 'miniball') => `<img class="${cls}" src="${ballSrc(key)}" alt="${BALLS[key].name}">`;
// Escape user-supplied text (multiplayer names). Card data is trusted; names are not.
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const staticSprite = (card, cls = 'tiny', mine = false) => `<img class="${cls}" src="${pokeSrc(card.id, mine)}" alt="">`;
// Own cards with an equipped skin use the skin PNG (no gif); everything else keeps the animated gif.
const animSprite = (card, mine = false) => {
  const skin = mine ? pokeSrc(card.id, true) : null;
  if (skin && skin !== pokeSrc(card.id)) return `<img class="sprite" src="${skin}" onerror="this.onerror=null;this.src='${pokeSrc(card.id)}'" alt="${card.name}">`;
  return `<img class="sprite" src="${animSrc(card.id)}" onerror="this.onerror=null;this.src='${pokeSrc(card.id)}'" alt="${card.name}">`;
};

// ---------- cosmetics (my equipped set; opponents' values are a TODO until the net protocol carries them) ----------
let myEquipped = null;
export const setMyCosmetics = (equipped) => { myEquipped = equipped; };
// TODO(net): opponents' avatarFrame/title/cardFrame come from SeatCosmetics (monetization 5.4) once protocol.js/session.js
// carry them; then pass them as `frame`/`ownerEquipped` below instead of the local player's values.
const myFrame = () => avatarFrameClass(myEquipped);
const myCardFrame = () => cardFrameClass(myEquipped);
const myTitleHTML = () => { const t = titleOf(myEquipped); return t ? `<span class="ttl ${t.css}">${esc(t.text)}</span>` : ''; };

// 인물 설명: 라인 내 관계(relation) + 한 줄 소개(desc) from data/roster.js
function relHTML(card) {
  const r = ROSTER[card.id];
  if (!r) return '';
  const line = LINES[r.line_id];
  return `<div class="relinfo">${esc(r.desc)}<small>${esc(r.relation)}${line ? ` · ${esc(line.title)}` : ''}</small></div>`;
}
const tierLabel = { 1: '1단계', 2: '2단계', 3: '3단계', rare: '희귀', legend: '전설' };

// ---------- cards ----------

export function cardHTML(card, ctrl, { zone = 'table', buyable = false, buyableNext = false, animated = true, interactive = true, mine = false } = {}) {
  const bonuses = bonusList(card);
  const special = isSpecial(card);
  const cost = COLORS.filter((c) => card.cost[c])
    .map((c) => `<span class="costchip">${ballImg(c)}${card.cost[c]}</span>`).join('')
    + (special ? `<span class="costchip">${ballImg(MASTER)}1</span>` : '');
  const classes = ['card', `b-${bonuses[0]}`, special ? card.tier : '', buyable ? 'buyable' : '', buyableNext && !buyable ? 'buyable-next' : '', mine ? myCardFrame() : ''].filter(Boolean).join(' ');
  const tag = special ? `<span class="tag ${card.tier}">${tierLabel[card.tier]}</span><br>` : '';
  const attrs = interactive ? `data-action="card" data-card="${card.id}" data-zone="${zone}"` : 'disabled';
  return `<button class="${classes}" ${attrs}>
    ${card.points ? `<span class="pts">${card.points}</span>` : ''}
    <span class="bonusicons">${bonuses.map((b) => ballImg(b, 'bonusdotimg')).join('')}</span>
    ${animated ? animSprite(card, mine) : `<img class="sprite" src="${pokeSrc(card.id, mine)}" alt="${card.name}">`}
    <span class="nm">${tag}${card.name}</span>
    <span class="cost">${cost}</span>
    <span class="evo">${evoText(card, ctrl.cardsById)}</span>
  </button>`;
}

const emptySlot = () => '<div class="card empty"></div>';

function tierRow(ctrl, key) {
  const s = ctrl.state;
  const reservableDeck = ['1', '2', '3'].includes(key);
  const deckN = s.decks[key].length;
  const canDeck = reservableDeck && ctrl.canReserve() && deckN > 0;
  const deck = `<button class="deck px" ${canDeck ? `data-action="deck" data-tier="${key}"` : 'disabled'}>
      <b>${deckN}</b>${tierLabel[key]}</button>`;
  const cards = s.table[key].map((card) => (card ? cardHTML(card, ctrl, { buyable: ctrl.canBuy(card.id), buyableNext: ctrl.canBuyAfterTake(card.id) }) : emptySlot())).join('');
  return { deck, cards };
}

export function boardHTML(ctrl) {
  const rows = ['3', '2', '1'].map((key) => {
    const { deck, cards } = tierRow(ctrl, key);
    return `<div class="tier-row">${deck}<div class="cards">${cards}</div></div>`;
  }).join('');
  const rare = tierRow(ctrl, 'rare');
  const legend = tierRow(ctrl, 'legend');
  return `${rows}<div class="tier-row special">
    <div class="half">${rare.deck}<div class="cards">${rare.cards}</div></div>
    <div class="half">${legend.deck}<div class="cards">${legend.cards}</div></div>
  </div>`;
}

// ---------- avatars ----------

const SEAT_COLORS = ['var(--obang-red)', 'var(--obang-blue)', 'var(--obang-yellow)', 'var(--obang-green)'];
let myAvatar = '하늘';
export const setMyAvatar = (name) => { myAvatar = name; };

/** Round avatar: trainer portrait when known, else a colored initial. */
export function avatarHTML(name, seat = 0, { me = false, cls = '' } = {}) {
  const face = trainerFaceSrc(me ? myAvatar : name) || trainerFaceSrc(name);
  const fr = me ? myFrame() : '';
  if (face) return `<img class="av ${cls} ${fr}" src="${face}" alt="">`;
  const ch = esc([...String(name || '?')][0] || '?');
  return `<span class="av ini ${cls} ${fr}" style="background:${SEAT_COLORS[seat % 4]}">${ch}</span>`;
}

export const AVATARS = TRAINERS;

// AI seats are bots, except in the offline ranked simulation where they are labelled "시뮬 유저".
const aiTag = (ctrl) => (ctrl.simUsers ? '<em class="botmark sim">시뮬 유저</em>' : '<em class="botmark">BOT</em>');
const aiPrefix = (ctrl) => (ctrl.simUsers ? '시뮬 ' : 'BOT ');

// ---------- top bar (round + turn timer) / side rail ----------

// timer: { remaining, limit } seconds
export function headerHTML(ctrl, timer = { remaining: 0, limit: 45 }) {
  const s = ctrl.state;
  const round = Math.floor(s.turn / s.players.length) + 1;
  let badge;
  if (ctrl.finished) badge = '게임 종료';
  else if (ctrl.isHumanTurn) badge = '▶ 내 차례';
  else badge = `${esc(ctrl.current.name)} 차례`;
  const last = ctrl.lastRound ? `<div class="lastround">마지막 라운드! ${esc(s.players[s.endTriggeredBy].name)}이(가) 21점 달성</div>` : '';
  const pct = ctrl.finished ? 0 : Math.max(0, Math.min(100, (timer.remaining / timer.limit) * 100));
  const urgent = !ctrl.finished && timer.remaining <= 10 ? ' urgent' : '';
  return `<div class="topbar">
      <div class="round">라운드 <b>${round}</b></div>
      <div class="turn ${ctrl.isHumanTurn ? 'mine' : ''}">${badge}</div>
      <div class="headbtns">
        <button class="iconbtn" data-action="rules" aria-label="룰 설명">?</button>
        <button class="iconbtn" data-action="options" aria-label="설정">⚙</button>
      </div>
    </div>
    <div class="timerbar${urgent}" id="timerbar"><i id="timerfill" style="width:${pct}%"></i><span id="turntimer">⏱ ${timer.remaining}초</span></div>${last}`;
}

/** Right-side vertical rail: every player's avatar + 21-point progress bar. */
export function railHTML(ctrl) {
  const s = ctrl.state;
  return s.players.map((p) => {
    const pts = getPoints(p);
    const pct = Math.min(100, (pts / 21) * 100);
    const active = s.current === p.id && !ctrl.finished;
    const isMe = p.id === ctrl.human;
    return `<button class="rail-item ${active ? 'active' : ''} ${isMe ? 'me' : ''}" data-action="opp" data-id="${p.id}" aria-label="${esc(p.name)} 상세">
      <span class="avwrap">${avatarHTML(p.name, p.id, { me: isMe })}${p.isAI ? aiTag(ctrl) : ''}</span>
      <span class="rnm">${esc(p.name)}</span>
      <span class="rsc"><b>${pts}</b>/21</span>
      <span class="hpbar"><i style="width:${pct}%"></i></span>
    </button>`;
  }).join('');
}



// ---------- supply ----------

export function supplyHTML(ctrl) {
  const s = ctrl.state;
  const sel = (c) => ctrl.balls.filter((x) => x === c).length;
  const canPick = ctrl.isHumanTurn && s.phase === PHASES.ACTION;
  return TOKEN_KEYS.map((k) => {
    const n = sel(k);
    const empty = s.supply[k] === 0;
    const pickable = canPick && k !== MASTER;
    return `<button class="ball ${n ? 'sel' : ''} ${empty ? 'empty' : ''}" ${pickable ? `data-action="ball" data-color="${k}"` : 'disabled'}>
      <span class="ballwrap">${ballImg(k, 'ballspr')}${n ? `<span class="selcount">×${n}</span>` : ''}</span>
      <span class="bnm">${BALLS[k].name}${hj(k)}</span><span class="cnt">${s.supply[k]}개</span></button>`;
  }).join('');
}

// ---------- my area ----------

function tokensHTML(ctrl) {
  const me = ctrl.me;
  const discarding = ctrl.isHumanTurn && ctrl.state.phase === PHASES.DISCARD;
  return TOKEN_KEYS.map((k) => {
    const d = ctrl.discard[k] || 0;
    const attr = discarding && me.tokens[k] > 0 ? `data-action="discard" data-token="${k}"` : 'disabled';
    const minus = discarding && d ? `<button class="tkminus" data-action="undiscard" data-token="${k}" aria-label="${BALLS[k].name} 반환 취소">−</button>` : '';
    return `<span class="tkwrap"><button class="mytk ${d ? 'dsel' : ''}" ${attr}>${ballImg(k, 'mytkimg')}<span>${me.tokens[k]}</span>${d ? `<em>-${d}</em>` : ''}</button>${minus}</span>`;
  }).join('');
}

function tableauHTML(ctrl) {
  const me = ctrl.me;
  if (!me.tableau.length) return '<div class="empty-note">아직 영입한 인물이 없어요</div>';
  const evolvable = ctrl.evolvableIds();
  const groups = COLORS.map((c) => {
    const list = me.tableau.filter((card) => bonusList(card)[0] === c);
    if (!list.length) return '';
    return `<div class="grp g-${c}">${list.map((card) => `
      <button class="mp ${myCardFrame()} ${evolvable.has(card.id) ? 'evolvable' : ''}" data-action="view-card" data-card="${card.id}">${staticSprite(card, 'tiny', true)}
        <span>${card.name}${card.points ? ` <i>${card.points}점</i>` : ''}</span>
        ${bonusList(card).map((b) => ballImg(b, 'mini2')).join('')}
        ${evolvable.has(card.id) ? '<span class="ev">성장 가능!</span>' : ''}</button>`).join('')}</div>`;
  });
  return groups.join('');
}

function handHTML(ctrl) {
  const me = ctrl.me;
  if (!me.hand.length) return '<div class="empty-note">찜한 카드 없음 (최대 3장)</div>';
  return me.hand.map((card) => `
    <button class="rsv ${ctrl.canBuy(card.id) ? 'buyable' : ctrl.canBuyAfterTake(card.id) ? 'buyable-next' : ''}" data-action="card" data-card="${card.id}" data-zone="hand" ${ctrl.isHumanTurn ? '' : 'disabled'}>
      ${staticSprite(card, 'tiny', true)}${card.name} <small>${tierLabel[card.tier]}${card.points ? ` · ${card.points}점` : ''}</small></button>`).join('');
}

export function meHTML(ctrl) {
  const me = ctrl.me;
  return `<div class="lbl">■ 내 인물 (${me.tableau.length}) · 성장 ${me.evolved.length}회 ${myTitleHTML()}</div>
    <div class="mypoke">${tableauHTML(ctrl)}</div>
    <div class="lbl">■ 찜한 카드 (${me.hand.length}/3)</div>
    <div class="reserved">${handHTML(ctrl)}</div>`;
}

// ---------- action bar ----------

export function actionBarHTML(ctrl) {
  const s = ctrl.state;
  if (ctrl.finished) return '<div class="hint">게임이 끝났어요.</div>';
  if (!ctrl.isHumanTurn) {
    return aiToastHTML(ctrl) || `<div class="hint">${ctrl.current.name}이(가) 생각 중…</div>`;
  }
  const err = ctrl.message ? `<div class="hint err">${ctrl.message}</div>` : '';
  if (s.phase === PHASES.DISCARD) {
    const need = ctrl.discardNeed;
    const have = ctrl.discardCount();
    return `<div class="hint">구슬이 10개를 넘었어요. 내 구슬을 눌러 <b>${need}개</b> 반환하세요. 누를 때마다 +1, 빨간 − 로 되돌려요. (${have}/${need})</div>${err}
      <div class="btnrow"><button class="btn ghost" data-action="clear">초기화</button>
      <button class="btn primary" data-action="confirm-discard" ${have === need ? '' : 'disabled'}>${need}개 반환</button></div>`;
  }
  if (s.phase === PHASES.EVOLVE) {
    const opts = ctrl.evolveChoices().map((o) => {
      const from = ctrl.cardsById.get(o.cardId);
      const to = ctrl.cardsById.get(o.nextId);
      return `<button class="btn evo" data-action="evolve" data-card="${o.cardId}">${from.name} → ${to.name} 성장</button>`;
    }).join('');
    return `<div class="hint evohint">성장할 수 있어요! 한 명만 골라 성장시키거나 건너뛰세요.</div>${err}
      <div class="btnrow col">${opts}<button class="btn ghost" data-action="skip-evolve">성장 안 함</button></div>`;
  }
  if (ctrl.canPass()) {
    return `<div class="hint">할 수 있는 행동이 없어요.</div>
      <div class="btnrow"><button class="btn primary" data-action="pass">차례 넘기기</button></div>`;
  }
  const n = ctrl.balls.length;
  const valid = ctrl.pendingValid();
  const pe = ctrl.pendingError();
  let hint = '구슬을 고르거나, 카드를 눌러 영입·찜하기를 하세요.';
  if (n) {
    const names = ctrl.balls.map((c) => BALLS[c].name).join('·');
    hint = valid ? `${names} 선택! 가져가기를 눌러 턴을 마치세요.` : `${names} 선택 중 — ${pe ? ({ bad_ball_count: '서로 다른 구슬을 3개까지 골라주세요.' }[pe] ?? '') : ''}`;
  }
  const label = n === 2 && ctrl.balls[0] === ctrl.balls[1] ? `${BALLS[ctrl.balls[0]].name} 2개 가져가기` : (n ? `구슬 ${n}개 가져가기` : '구슬 가져가기');
  return `<div class="hint">${hint}</div>${err}
    <div class="btnrow"><button class="btn ghost" data-action="clear" ${n ? '' : 'disabled'}>선택 취소</button>
    <button class="btn primary" data-action="confirm-balls" ${valid ? '' : 'disabled'}>${label}</button></div>`;
}

/** Bottom shop-bar: my score, bonuses, resources, then the action buttons. */
export function dockHTML(ctrl) {
  const me = ctrl.me;
  const b = getBonuses(me);
  const tc = tokenCount(me);
  return `<div class="dock-top">
      ${avatarHTML(me.name, ctrl.human, { me: true, cls: 'sm' })}
      <span class="dock-name">${esc(me.name)}</span>
      <span class="dock-sc"><b>${getPoints(me)}</b>점</span>
      <span class="dock-pips">${COLORS.map((c) => `<span class="pip d-${c}">${ballImg(c, 'mini2')}${hj(c)}${b[c]}</span>`).join('')}</span>
      <span class="tkcount ${tc >= 10 ? 'full' : ''}">구슬 ${tc}/10</span>
    </div>
    <div class="mytokens">${tokensHTML(ctrl)}</div>
    ${actionBarHTML(ctrl)}`;
}

export function logHTML(ctrl) {
  if (!ctrl.log.length) return '';
  return `<div class="log">${ctrl.log.slice(-4).map((l) => `<div>${l}</div>`).join('')}</div>`;
}

export function aiToastHTML(ctrl) {
  const ev = ctrl.lastAIEvent;
  if (!ev || ctrl.isHumanTurn || ctrl.finished) return '';
  const p = ctrl.state.players[ev.player];
  if (!p) return '';
  let body = '';
  if (ev.type === 'takeBalls') body = `${ev.colors.map((c) => ballImg(c, 'ballspr')).join('')} 가져감`;
  else if (ev.type === 'takeTwo') body = `${ballImg(ev.color, 'ballspr')}<b>×2</b> 가져감`;
  else if (ev.type === 'buy') {
    const card = ctrl.cardsById.get(ev.cardId);
    body = card ? `${staticSprite(card)}<b>${card.name}</b> 영입!` : '인물 영입!';
  } else if (ev.type === 'reserve') {
    const card = ev.cardId ? ctrl.cardsById.get(ev.cardId) : null;
    body = card ? `${staticSprite(card)}<b>${card.name}</b> 찜!` : '덱에서 찜!';
  } else if (ev.type === 'evolve') {
    const from = ctrl.cardsById.get(ev.from);
    const to = ctrl.cardsById.get(ev.to);
    body = from && to ? `${staticSprite(from)} → ${staticSprite(to)}<b>성장!</b>` : '성장!';
  } else return '';
  return `<div class="aitoast"><span class="who">${p.isAI ? aiPrefix(ctrl) : ''}${esc(p.name)}</span><span class="what">${body}</span></div>`;
}

// ---------- sheet + overlays ----------

function oppSheetHTML(p, ctrl) {
  const b = getBonuses(p);
  const tokens = TOKEN_KEYS.filter((k) => p.tokens[k] > 0)
    .map((k) => `<span class="otk">${ballImg(k, 'mini2')}${p.tokens[k]}</span>`).join('') || '없음';
  const groups = COLORS.map((c) => {
    const list = p.tableau.filter((card) => bonusList(card)[0] === c);
    if (!list.length) return '';
    return `<div class="grp g-${c}">${list.map((card) => `
      <button class="mp" data-action="view-card" data-card="${card.id}" data-from="opp" data-pid="${p.id}">${staticSprite(card)}<span>${card.name}${card.points ? ` <i>${card.points}점</i>` : ''}</span></button>`).join('')}</div>`;
  }).join('');
  const hand = p.hand.length
    ? p.hand.map((card) => `<button class="orsv" data-action="view-card" data-card="${card.id}" data-from="opp" data-pid="${p.id}">${staticSprite(card)}${card.name} <small>${tierLabel[card.tier]}${card.points ? ` · ${card.points}점` : ''}</small></button>`).join('')
    : '<div class="empty-note">없음</div>';
  return `<div class="sheet-back" data-action="close"></div><div class="sheet wide">
    <div class="sheet-title">${avatarHTML(p.name, p.id, { me: p.id === ctrl.human, cls: 'md' })}${p.isAI ? aiPrefix(ctrl) : ''}${esc(p.name)} <small>· ${getPoints(p)}점 · 성장 ${p.evolved.length}회</small></div>
    <div class="olbl">■ 보너스 (할인)</div>
    <div class="pips big">${COLORS.map((c) => `<span class="pip d-${c}">${ballImg(c, 'mini2')}${hj(c)}${b[c]}</span>`).join('')}</div>
    <div class="olbl">■ 가진 구슬 (${tokenCount(p)}/10)</div>
    <div class="otks">${tokens}</div>
    <div class="olbl">■ 인물 (${p.tableau.length}명)</div>
    <div class="opoke">${groups || '<div class="empty-note">아직 없음</div>'}</div>
    <div class="olbl">■ 찜한 카드 (${p.hand.length}/3)</div>
    <div class="ohand">${hand}</div>
    <div class="btnrow"><button class="btn primary" data-action="close">닫기</button></div></div>`;
}

// have/need per color when the player can't afford a card (red = short)
function shortfallHTML(player, card) {
  const bonuses = getBonuses(player);
  const parts = COLORS.map((c) => {
    const need = Math.max(0, (card.cost[c] || 0) - bonuses[c]);
    if (!need) return '';
    const have = player.tokens[c] || 0;
    return `<span class="need ${have >= need ? 'ok' : 'lack'}">${ballImg(c, 'mini2')}${have}/${need}</span>`;
  }).join('');
  const masterNote = isSpecial(card) && !(player.tokens[MASTER] > 0)
    ? `<span class="need lack">${ballImg(MASTER, 'mini2')}여의주 필요</span>` : '';
  return parts + masterNote || '구슬이 부족해요';
}

export function sheetHTML(ctrl) {
  const sh = ctrl.sheet;
  if (!sh) return '';
  if (sh.kind === 'opp') {
    const p = ctrl.state.players[sh.playerId];
    return p ? oppSheetHTML(p, ctrl) : '';
  }
  if (sh.kind === 'view') {
    const card = ctrl.cardsById.get(sh.cardId);
    if (!card) return '';
    const backBtn = sh.from && sh.from.kind === 'opp'
      ? `<button class="btn alt" data-action="view-back">← 상대 정보로</button>` : '';
    return `<div class="sheet-back" data-action="close"></div><div class="sheet">
      <div class="sheet-card">${cardHTML(card, ctrl, { interactive: false, mine: !(sh.from && sh.from.kind === 'opp') && ctrl.me.tableau.some((c) => c.id === card.id) })}</div>
      <div class="sheet-info">
        <div class="sheet-title">${card.name}</div>
        <div class="paylbl">보너스</div>
        <div class="pay">${bonusList(card).map((b) => ballImg(b)).join(' ')}</div>
        <div class="paylbl">성장 조건</div>
        <div class="evoinfo">${evoText(card, ctrl.cardsById)}</div>
        ${relHTML(card)}
      </div>
      <div class="btnrow">${backBtn}<button class="btn primary" data-action="close">닫기</button></div></div>`;
  }
  if (sh.kind === 'deck') {
    return `<div class="sheet-back" data-action="close"></div><div class="sheet">
      <div class="sheet-title">${tierLabel[sh.tier]} 덱 맨 위 카드</div>
      <p class="sheet-p">뒷면 그대로 찜해요. 여의주가 남아 있으면 1개를 받아요.</p>
      <div class="btnrow"><button class="btn ghost" data-action="close">닫기</button>
      <button class="btn primary" data-action="reserve-deck" data-tier="${sh.tier}" ${ctrl.canReserve() ? '' : 'disabled'}>찜하기</button></div></div>`;
  }
  const card = ctrl.cardsById.get(sh.cardId);
  const inHand = ctrl.zone(card.id) === 'hand';
  const pay = ctrl.payment(card.id);
  let payText, payCls;
  if (pay) {
    payCls = '';
    payText = TOKEN_KEYS.filter((k) => pay[k]).map((k) => `${ballImg(k)}${pay[k]}`).join(' ') || '무료!';
  } else {
    payCls = 'no';
    payText = shortfallHTML(ctrl.me, card);
  }
  const canReserve = !inHand && !isSpecial(card) && ctrl.canReserve();
  const reserveNote = inHand ? '' : isSpecial(card) ? '희귀·전설은 찜 불가' : !ctrl.canReserve() ? '찜 한도(3장) 초과' : '';
  const masterLeft = ctrl.state.supply[MASTER] > 0;
  const reserveLabel = masterLeft ? '찜하기 (+여의주)' : '찜하기 (여의주 품절)';
  return `<div class="sheet-back" data-action="close"></div><div class="sheet">
    <div class="sheet-card">${cardHTML(card, ctrl, { interactive: false, mine: inHand })}</div>
    <div class="sheet-info">
      <div class="sheet-title">${card.name}</div>
      <div class="paylbl">내가 낼 구슬 (보너스 할인 적용)</div>
      <div class="pay ${payCls}">${payText}</div>
      ${reserveNote ? `<div class="note">${reserveNote}</div>` : ''}
      ${relHTML(card)}
    </div>
    <div class="btnrow col">
      <button class="btn primary" data-action="buy" data-card="${card.id}" ${pay ? '' : 'disabled'}>인물 영입</button>
      ${inHand ? '' : `<button class="btn alt" data-action="reserve" data-card="${card.id}" ${canReserve ? '' : 'disabled'}>${reserveLabel}</button>`}
      <button class="btn ghost" data-action="close">닫기</button>
    </div></div>`;
}

export function rulesHTML() {
  return `<div class="overlay"><div class="panel rulespanel">
    <div class="title big">룰 설명</div>
    <div class="rules">
      <h4>■ 목표</h4>
      <p><b>21점</b>을 먼저 모으면 마지막 라운드! 전원이 같은 턴 수를 마치면 종료, 최고점이 승리해요.</p>
      <h4>■ 내 차례에 하는 일 (하나만 선택)</h4>
      <p>① <b>서로 다른 구슬 3개</b> 가져오기 (여의주 제외)<br>
      ② <b>같은 구슬 2개</b> 가져오기 (공급처에 4개 이상 남았을 때만)<br>
      ③ <b>카드 찜하기</b> (최대 3장, 여의주 1개를 받아요 · 여의주는 5개 한정이라 품절되면 찜만 돼요 · 희귀/전설은 찜 불가)<br>
      ④ <b>인물 영입</b> (구슬을 내고 카드를 데려와요)<br>
      <span style="color:var(--ok)">■</span> <b>초록 테두리</b>=지금 바로 영입할 수 있음 · <span style="color:var(--next)">■</span> <b>파랑 테두리</b>=고른 구슬을 가져가면 다음 턴에 영입할 수 있음</p>
      <h4>■ 보너스 = 할인</h4>
      <p>영입한 인물의 보너스 1개(희귀/전설은 2개)마다 같은 색 구슬 1개씩 영구 할인! 게임 끝까지 유지돼요.</p>
      <h4>■ 성장</h4>
      <p>내 턴이 끝나면, 성장 조건의 보너스를 갖춘 인물은 다음 단계로 <b>성장</b>할 수 있어요. 점수와 보너스가 올라가요. (1→2→3단계만 가능)</p>
      <h4>■ 구슬 10개 제한</h4>
      <p>여의주 포함 10개를 넘기면, 초과분을 골라 반환해야 해요.</p>
      <h4>■ 여의주</h4>
      <p>어떤 구슬이든 1개로 대신할 수 있는 만능 구슬! <b>희귀/전설 인물을 영입하려면 여의주 1개가 꼭 필요</b>해요.</p>
      <h4>■ 동점 처리</h4>
      <p>① 성장 횟수가 많은 쪽 → ② 그래도 동점이면 영입한 인물이 적은 쪽이 이겨요.</p>
    </div>
    <div class="btnrow"><button class="btn primary" data-action="rules-close">닫기</button></div>
  </div></div>`;
}

function beginnerTip(ctrl) {
  const s = ctrl.state;
  if (s.phase === PHASES.DISCARD) return '구슬이 10개를 넘었어요. 아래 내 구슬을 눌러 초과분을 반환하세요.';
  if (s.phase === PHASES.EVOLVE) return '성장 찬스! 조건을 갖춘 인물을 성장시키면 점수와 보너스가 올라가요.';
  if (!ctrl.isHumanTurn) return null;
  const n = ctrl.balls.length;
  if (n > 0) {
    return ctrl.pendingValid()
      ? '좋아요! [가져가기]를 누르면 구슬을 가져오고 턴이 끝나요.'
      : '서로 다른 구슬 3개, 또는 같은 구슬 2개(공급처에 4개 이상 남았을 때)를 고를 수 있어요.';
  }
  for (const key of ['1', '2', '3', 'rare', 'legend']) {
    for (const card of s.table[key] || []) {
      if (card && ctrl.canBuy(card.id)) return '지금 바로 영입할 수 있는 인물이 있어요! 반짝이는 카드를 눌러보세요.';
    }
  }
  return '21점이 목표! 구슬을 모아 인물을 영입하세요. 보너스가 쌓이면 할인이 커져요.';
}

export function helpHTML(ctrl, options) {
  if (!options.beginnerHelp || !ctrl || ctrl.finished) return '';
  const tip = beginnerTip(ctrl);
  if (!tip) return '';
  return `<div class="helpbanner"><span class="helptag">TIP</span><span>${tip}</span></div>`;
}

export function dexHTML(dex, cards) {
  const sum = dexSummary(dex, cards);
  const order = { 1: 1, 2: 2, 3: 3, rare: 4, legend: 5 };
  const list = [...cards].sort((a, b) => order[a.tier] - order[b.tier] || a.id.localeCompare(b.id));
  const cell = (c) => {
    const e = dex.caught[c.id];
    return e
      ? `<div class="dexcell got" title="${esc(ROSTER[c.id]?.desc ?? '')}"><img src="${pokeSrc(c.id)}" alt="${c.name}"><span class="dn">${c.name}</span><span class="dc">×${e.n}${e.evolved ? ` · 성장 ${e.evolved}` : ''}</span></div>`
      : `<div class="dexcell"><img class="sil" src="${pokeSrc(c.id)}" alt=""><span class="dn">???</span><span class="dc">${tierLabel[c.tier]}</span></div>`;
  };
  const g = dex.games;
  return `<div class="overlay"><div class="panel dexpanel">
    <div class="title big">인물록<small>영입한 인물 ${sum.caught}/${sum.total} · ${g.played}판 ${g.won}승</small></div>
    <div class="dexgrid">${list.map(cell).join('')}</div>
    <div class="btnrow"><button class="btn primary" data-action="dex-close">닫기</button></div>
  </div></div>`;
}

export function achvHTML(unlocked) {
  const rows = ACHIEVEMENTS.map((a) => {
    const got = !!unlocked[a.id];
    return `<div class="achvrow ${got ? 'got' : ''}"><span class="achvicon">${got ? a.icon : '🔒'}</span>
      <div><b>${a.name}</b><br><small>${a.desc}</small></div></div>`;
  }).join('');
  const n = Object.keys(unlocked).length;
  return `<div class="overlay"><div class="panel">
    <div class="title big">업적<small>${n}/${ACHIEVEMENTS.length} 달성</small></div>
    <div class="achvlist">${rows}</div>
    <div class="btnrow"><button class="btn primary" data-action="achv-close">닫기</button></div>
  </div></div>`;
}

// ---------- lobby / matching / result screens ----------

/** Tier badge: text + color + number + shape (never color alone). `art` is an empty slot for the badge image. */
export function tierBadgeHTML(disp, { size = '' } = {}) {
  const un = RANKED.official ? '' : ' unofficial';
  if (disp.placing) {
    return `<span class="tbadge placing ${size}${un}" aria-label="배치 ${disp.progress}/${disp.of}"><b class="tb-num">?</b><span class="tb-name">배치 ${disp.progress}/${disp.of}</span></span>`;
  }
  const t = disp.tier;
  return `<span class="tbadge tg-${t.grade} ${t.half} ${size}${un}" data-tier="${t.id}" aria-label="${t.name}">`
    + `<span class="tb-art" data-art="assets/tiers/${t.id}.png"></span><b class="tb-num">${t.grade}</b><span class="tb-name">${t.name}</span></span>`;
}

const fmtWait = (sec) => `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;

/** Allowed rating spread by queue wait time (modes-ranked 1.2.1) -- shown as text only; matching itself is server-side later. */
export function rangeNote(sec) {
  if (sec < 15) return '비슷한 품계의 도사를 찾는 중';
  if (sec < 30) return '찾는 범위를 조금 넓히는 중';
  if (sec < 60) return '찾는 범위를 넓히는 중';
  if (sec < 120) return '품계 차이를 더 넓혀 찾는 중';
  return '품계 제한 없이 찾는 중 (최대 3단계 차이)';
}

function rankedPanelHTML({ profile, gate, ban, rankedDisp }) {
  const lock = !gate.unlocked;
  const status = rankedDisp.placing
    ? `<div class="rk-rp">배치고사 <b>${rankedDisp.progress}/${rankedDisp.of}</b><small>5판 뒤 첫 품계가 정해져요</small></div>`
    : `<div class="rk-rp"><b>${rankedDisp.rp}</b> RP<small>${rankedDisp.tier.name}${rankedDisp.shield ? ` · 승급 보호 ${rankedDisp.shield}판` : ''}</small></div>`;
  const gateHTML = gate.enforced && !gate.met
    ? `<ul class="gate">${gate.items.map((i) => `<li class="${i.ok ? 'ok' : 'no'}">${i.ok ? '✔' : '🔒'} ${i.label} ${i.bool ? '' : `${i.cur}/${i.need}`}</li>`).join('')}</ul>` : '';
  return `<div class="rk-card">
      <div class="rk-head">${tierBadgeHTML(rankedDisp, { size: 'lg' })}${status}</div>
      <div class="season-tag">${SEASON_LABEL}</div>
      <ul class="rk-rules"><li>4인 고정 · 봇 채움 없음</li><li>정원이 찰 때까지 계속 대기 (취소 가능)</li><li>턴 제한 ${RANKED.turnLimitMs / 1000}초 · 도중 이탈은 감점</li></ul>
      ${gateHTML}
      ${ban ? `<p class="sheet-p warn">큐 제한 중 · ${ban}분 남음</p>` : ''}
    </div>
    <button class="btn bigstart ranked" data-action="match" ${lock || ban ? 'disabled' : ''}>${lock ? '🔒 랭킹전 잠김' : '랭킹전 시작'}<small>4인 대전 · 시범(비공식)</small></button>`;
}

export function homeHTML({ options, dex, notice = '', profile, gate, ban = 0, sim = false }) {
  const g = dex?.games || { played: 0, won: 0 };
  const size = options.queueSize;
  const name = esc(options.playerName || '도사');
  const ranked = options.mode === 'ranked';
  const rankedDisp = displayOf(profile.ranked);
  const normalPanel = `<div class="seg" role="group" aria-label="인원 선택">${[2, 3, 4].map((n) =>
        `<button class="segbtn ${size === n ? 'sel' : ''}" data-action="queue-size" data-n="${n}">${n}인</button>`).join('')}</div>
      <button class="btn bigstart" data-action="match">매칭 시작<small>${size}인 대전 · 랭크 점수 변동 없음</small></button>
      <button class="optrow slim" data-action="toggle-fill"><span>정원 미달 시 봇으로 자리 채움</span>
        <span class="toggle ${options.fillBots ? 'on' : ''}">${options.fillBots ? '켬' : '끔'}</span></button>`;
  return `<div class="overlay screen home">
    <div class="home-top">
      <button class="profile-chip px" data-action="profile">${avatarHTML(options.avatar, 0, { me: true, cls: 'sm' })}
        <span><b>${name}</b>${myTitleHTML()}<small>${g.played}판 ${g.won}승</small></span>${tierBadgeHTML(rankedDisp, { size: 'sm' })}</button>
      <button class="iconbtn" data-action="options" aria-label="설정">⚙</button>
    </div>
    <div class="home-hero">
      <div class="title big">조선 스플렌더<small>K-SPLENDOR · DOT EDITION</small></div>
      <div class="hero-av">${avatarHTML(options.avatar, 0, { me: true, cls: 'lg' })}</div>
      <p class="hero-sub">구슬을 모아 21점을 먼저 채워라!</p>
    </div>
    ${notice ? `<p class="sheet-p warn">${esc(notice)}</p>` : ''}
    <div class="home-match">
      <div class="modetabs" role="tablist" aria-label="모드 선택">
        <button class="modetab ${ranked ? '' : 'sel'}" role="tab" data-action="mode" data-mode="normal">일반전</button>
        <button class="modetab ${ranked ? 'sel' : ''}" role="tab" data-action="mode" data-mode="ranked">랭킹전${gate.unlocked ? '' : ' 🔒'}</button>
      </div>
      ${ranked ? rankedPanelHTML({ profile, gate, ban, rankedDisp }) : normalPanel}
      <div class="friend-row"><span class="nonrank">친구 방 · 비랭크</span>
      <div class="btnrow"><button class="btn alt" data-action="room-create">친구와 방 만들기</button>
      <button class="btn alt" data-action="room-join">코드로 참가</button></div></div>
    </div>
    <nav class="tabbar">
      <button data-action="dex"><span>📖</span>인물록</button>
      <button data-action="achv"><span>🏆</span>업적</button>
      <button data-action="shop"><span>🏮</span>상점</button>
      <button data-action="rules"><span>📜</span>룰</button>
      <button data-action="options"><span>⚙</span>설정</button>
    </nav>
  </div>`;
}

/**
 * Matching queue / friend room.
 * v: { title, size, slots: [{name, bot, sim, me}], countdown (sec|null), code, host, fillBots, notice, starting,
 *      ranked, isRoom, waited (sec), tierDisp }
 */
export function queueHTML(v) {
  const slots = Array.from({ length: v.size }, (_, i) => {
    const sl = v.slots[i];
    if (!sl) return `<div class="slot empty"><span class="av ini wait">?</span><span class="slotnm">대기 중…</span></div>`;
    const mark = sl.bot ? '<em class="botmark">BOT</em>' : sl.sim ? '<em class="botmark sim">시뮬 유저</em>' : sl.me ? '<em class="memark">나</em>' : '';
    return `<div class="slot ${sl.me ? 'me' : ''}">${avatarHTML(sl.name, i, { me: sl.me })}
      <span class="slotnm">${esc(sl.name)}</span>${mark}</div>`;
  }).join('');
  const have = v.slots.length;
  let cd;
  if (v.ranked) {
    cd = `<div class="cd"><b>${fmtWait(v.waited ?? 0)}</b><small>${rangeNote(v.waited ?? 0)} · 봇 채움 없음</small></div>`;
  } else if (v.countdown != null && v.fillBots) {
    cd = `<div class="cd"><b>${v.countdown}</b><small>초 후 빈 자리를 봇으로 채워요</small></div>`;
  } else {
    cd = `<div class="cd"><b class="dots">…</b><small>${v.fillBots ? '' : '봇 채움 꺼짐 · '}상대를 기다리는 중</small></div>`;
  }
  const tag = v.ranked ? `<div class="modetag ranked">랭킹전 · ${SEASON_LABEL}</div>`
    : v.isRoom ? '<div class="modetag">친구 방 · 비랭크</div>' : '<div class="modetag">일반전 · 랭크 점수 변동 없음</div>';
  return `<div class="overlay screen queue">
    <div class="title big">${esc(v.title)}<small>${have}/${v.size}명</small></div>
    ${tag}
    ${v.ranked && v.tierDisp ? `<div class="qtier">${tierBadgeHTML(v.tierDisp)}</div>` : ''}
    ${v.notice ? `<p class="sheet-p warn">${esc(v.notice)}</p>` : ''}
    ${v.code ? `<div class="shortcode"><span>방 코드 (친구에게 알려주세요)</span><b>${esc(v.code)}</b></div>` : ''}
    <div class="slots n${v.size}">${slots}</div>
    ${v.starting ? '<div class="cd"><b>GO!</b><small>게임에 입장하는 중</small></div>' : cd}
    <div class="btnrow">
      ${v.host && !v.starting && !v.ranked ? `<button class="btn primary" data-action="room-start" ${have < 2 && !v.fillBots ? 'disabled' : ''}>${have < v.size ? '봇 채우고 시작' : '게임 시작'}</button>` : ''}
      <button class="btn ghost" data-action="queue-cancel">${v.isRoom ? '방 나가기' : '매칭 취소'}</button>
    </div>
  </div>`;
}

export function joinCodeHTML(notice = '') {
  return `<div class="overlay"><div class="panel">
    <div class="title big">코드로 참가</div>
    ${notice ? `<p class="sheet-p warn">${esc(notice)}</p>` : ''}
    <p class="sheet-p">친구가 알려준 6자리 방 코드를 입력하세요.</p>
    <input id="joincode" class="netinput code" maxlength="6" placeholder="ABC123" autocomplete="off">
    <div class="btnrow"><button class="btn ghost" data-action="join-close">취소</button>
    <button class="btn primary" data-action="join-go">참가</button></div>
  </div></div>`;
}

export function profileHTML(options) {
  return `<div class="overlay"><div class="panel">
    <div class="title big">프로필</div>
    <p class="sheet-p">닉네임</p>
    <input id="profname" class="netinput" maxlength="12" placeholder="도사" value="${esc(options.playerName)}">
    <p class="sheet-p">대표 캐릭터</p>
    <div class="avpick">${AVATARS.map((n) => `<button class="avopt ${options.avatar === n ? 'sel' : ''}" data-action="avatar" data-name="${n}">${avatarHTML(n, 0, { cls: 'md' })}<span>${n}</span></button>`).join('')}</div>
    <div class="btnrow"><button class="btn primary" data-action="profile-save">저장</button></div>
  </div></div>`;
}

export function optionsHTML(options, inGame = false) {
  return `<div class="overlay"><div class="panel">
    <div class="title big">설정</div>
    <button class="optrow" data-action="toggle-help">
      <span>초보자 팁 표시</span>
      <span class="toggle ${options.beginnerHelp ? 'on' : ''}">${options.beginnerHelp ? '켬' : '끔'}</span>
    </button>
    <button class="optrow" data-action="toggle-bgm">
      <span>🎵 배경음악</span>
      <span class="toggle ${options.bgm ? 'on' : ''}">${options.bgm ? '켬' : '끔'}</span>
    </button>
    <button class="optrow" data-action="toggle-sfx">
      <span>🔔 효과음</span>
      <span class="toggle ${options.sfx ? 'on' : ''}">${options.sfx ? '켬' : '끔'}</span>
    </button>
    ${inGame ? '<div class="btnrow"><button class="btn danger" data-action="restart">게임 나가기 (홈으로)</button></div>' : ''}
    <div class="btnrow"><button class="btn primary" data-action="options-close">닫기</button></div>
  </div></div>`;
}

function rpResultHTML(res) {
  if (!res) return '';
  if (res.mode === 'private') return '<div class="rpblock plain">친구 방 · 비랭크 판이라 점수 변동이 없어요.</div>';
  if (res.mode !== 'ranked') return '<div class="rpblock plain">일반전 · 랭크 점수 변동이 없어요.</div>';
  const c = res.change;
  const label = `<div class="season-tag">${SEASON_LABEL}</div>`;
  if (c.wasPlacing && !c.placementDone) {
    return `<div class="rpblock">${label}<div class="rp-line">${tierBadgeHTML(c.after)}<span>배치고사 ${c.after.progress}/${c.after.of} 기록 완료</span></div>
      <small class="rp-note">배치 중에는 RP와 품계가 공개되지 않아요.</small></div>`;
  }
  const sign = c.delta > 0 ? 'pos' : c.delta < 0 ? 'neg' : '';
  const d = c.delta > 0 ? `+${c.delta}` : `${c.delta}`;
  const from = c.before.placing ? null : c.before.rp;
  const toPct = c.after.pct ?? 0;
  const fromPct = c.before.placing ? 0 : (c.before.pct ?? 0);
  let event = '';
  if (c.placementDone) event = `<div class="promo up">배치 완료! 시작 품계 <b>${c.after.tier.name}</b></div>`;
  else if (c.promoted) event = `<div class="promo up">승급! ${c.before.tier.name} → <b>${c.after.tier.name}</b><small>3판간 강등 보호</small></div>`;
  else if (c.demoted) event = `<div class="promo down">강등… ${c.before.tier.name} → <b>${c.after.tier.name}</b></div>`;
  else if (c.shielded) event = '<div class="promo shield">승급 보호 중이라 품계는 유지돼요</div>';
  return `<div class="rpblock">${label}
    <div class="rp-line">${tierBadgeHTML(c.after)}<span class="rp-num">${from !== null ? `${from} → ` : ''}<b>${c.after.rp}</b> RP <em class="rp-d ${sign}">${d}</em></span></div>
    <div class="rpbar" role="progressbar" aria-valuenow="${Math.round(toPct)}" aria-valuemin="0" aria-valuemax="100"><i style="--from:${fromPct}%;--to:${toPct}%"></i></div>
    ${event}</div>`;
}

export function leaveConfirmHTML({ voidLeave }) {
  return `<div class="overlay"><div class="panel">
    <div class="title big">랭킹전에서 나갈까요?</div>
    <p class="sheet-p warn">${voidLeave
      ? '아직 초반이라 판이 무효 처리돼요. 다른 도사의 점수는 그대로지만 나는 <b>-15 RP</b>와 10분간 큐 제한을 받아요.'
      : '지금 나가면 최하위로 처리되고 <b>-10 RP</b> 추가 감점을 받아요.'}</p>
    <div class="btnrow"><button class="btn ghost" data-action="leave-cancel">계속하기</button>
    <button class="btn danger" data-action="leave-confirm">나가기</button></div>
  </div></div>`;
}

export function endHTML(ctrl, res = null) {
  const s = ctrl.state;
  const rows = s.ranking.map((r) => {
    const p = s.players[r.player];
    const isMe = p.id === ctrl.human;
    return `<tr class="${r.rank === 1 ? 'win' : ''} ${isMe ? 'me' : ''}"><td class="rk">${r.rank}</td>
      <td class="who">${avatarHTML(p.name, p.id, { me: isMe, cls: 'sm' })}<span>${p.isAI ? (ctrl.simUsers ? '<em class="botmark sim">시뮬 유저</em> ' : 'BOT ') : ''}${esc(p.name)}</span></td>
      <td>${r.points}점</td><td>성장 ${r.evolutions}</td><td>${r.pokemon}명</td></tr>`;
  }).join('');
  const myRank = s.ranking.find((r) => r.player === ctrl.human)?.rank;
  const again = res?.mode === 'ranked' ? '다시 랭킹전' : '다시 매칭';
  return `<div class="overlay screen result"><div class="panel">
    <div class="title big">${myRank === 1 ? '우승!' : `${myRank}위`}<small>${s.stalled ? '아무도 행동할 수 없어 종료됐어요' : '최종 순위'}</small></div>
    <table class="rank">${rows}</table>
    ${rpResultHTML(res)}
    <p class="sheet-p">동점은 성장 횟수가 많은 쪽 → 영입한 인물 수가 적은 쪽이 이겨요.</p>
    <div class="btnrow"><button class="btn ghost" data-action="restart">홈으로</button>
    <button class="btn primary" data-action="rematch">${again}</button></div>
  </div></div>`;
}

// ---------- shop (skeleton: free claim + equip only; paid items show "준비 중") ----------

function itemPreview(it, inv) {
  if (it.type === 'avatarFrame') return `<span class="av ini sm pv ${it.css}" style="background:var(--obang-blue)">도</span>`;
  if (it.type === 'cardFrame') return `<span class="pv-card ${it.css}"></span>`;
  if (it.type === 'title') return `<span class="ttl pv-ttl ${it.css}">${esc(itemName(it))}</span>`;
  if (it.type === 'emote') return `<span class="pv-emote">${it.glyph}</span>`;
  return '<span class="pv-emote">🎴</span>';
}

export function shopHTML({ inv, tab, toast = '' }) {
  const items = CATALOG.filter((i) => i.type === tab);
  const rows = items.map((it) => {
    const own = owns(inv, it.id);
    const eq = own && isEquipped(inv, it);
    const free = isFree(it);
    const price = free ? '무료' : `엽전 ${it.price.amount}`;
    let btn;
    if (!own && free) btn = `<button class="btn primary" data-action="shop-claim" data-item="${it.id}">받기</button>`;
    else if (!own) btn = '<button class="btn ghost" disabled>준비 중</button>';
    else if (eq && (it.type === 'emote' || it.type === 'cardSkin')) btn = `<button class="btn ghost" data-action="shop-equip" data-item="${it.id}">해제</button>`;
    else if (eq) btn = '<button class="btn ghost" disabled>장착 중</button>';
    else btn = `<button class="btn alt" data-action="shop-equip" data-item="${it.id}">장착</button>`;
    return `<div class="shopitem ${own ? 'own' : ''} ${eq ? 'eq' : ''}">
      <div class="si-pv">${itemPreview(it, inv)}</div>
      <div class="si-info"><b>${esc(itemName(it))}</b><small>${esc(it.description.ko)}</small>
        <span class="si-meta"><em class="rar ${it.rarity}">${it.rarity}</em><span class="si-price ${free ? 'free' : ''}">${own ? '보유' : price}</span></span></div>
      <div class="si-btn">${btn}</div></div>`;
  }).join('');
  return `<div class="overlay"><div class="panel shoppanel">
    <div class="title big">상점<small>엽전 ${inv.wallet.yeopjeon} · 외형만 바뀌고 게임 규칙은 그대로예요</small></div>
    <div class="shoptabs" role="tablist">${CATEGORIES.map((c) => `<button class="shoptab ${c.id === tab ? 'sel' : ''}" role="tab" data-action="shop-tab" data-tab="${c.id}">${c.label}</button>`).join('')}</div>
    ${toast ? `<p class="sheet-p shoptoast">${esc(toast)}</p>` : ''}
    <div class="shoplist">${rows || '<div class="empty-note">준비 중이에요</div>'}</div>
    <div class="btnrow"><button class="btn primary" data-action="shop-close">닫기</button></div>
  </div></div>`;
}
