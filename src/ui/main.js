// DOM glue: renders controller state into regions, wires taps, and paces AI turns.

// Self-update: if a newer build is deployed, jump to the versioned URL so
// browsers and home-screen web apps never sit on stale cached files.
(async () => {
  try {
    const mine = window.__V;
    if (!mine) return;
    const r = await fetch('assets/version.json', { cache: 'no-store' });
    const { v } = await r.json();
    const param = new URLSearchParams(location.search).get('v');
    if (v && v !== mine && param !== String(v)) {
      location.replace(location.pathname + '?v=' + v);
    }
  } catch { /* offline or first deploy: stay put */ }
})();

// In-app browser guard: KakaoTalk/etc. popups die when swiped away, killing
// multiplayer. iOS can't force-open Safari from JS, so detect and guide.
const INAPP_RE = /KAKAOTALK|Instagram|FBAN|FBAV|FB_IAB|Line\/|NAVER|DaumApp|Whale|MiuiBrowser/i;
function showInAppGuide() {
  try {
    const ua = navigator.userAgent || '';
    if (!INAPP_RE.test(ua) || sessionStorage.getItem('inapp-dismissed')) return;
    const bar = document.createElement('div');
    bar.id = 'inappbar';
    bar.innerHTML = `<div><b>📱 Safari에서 열어주세요</b><br><small>인앱 브라우저(팝업)는 실수로 내리면 게임 연결이 끊겨요.<br>메뉴(•••) → 'Safari로 열기' 또는 '다른 브라우저로 열기'를 눌러주세요.</small></div>
      <button id="inapp-copy">URL 복사</button><button id="inapp-x" aria-label="닫기">✕</button>`;
    document.body.prepend(bar);
    document.getElementById('inapp-x').onclick = () => {
      bar.remove();
      try { sessionStorage.setItem('inapp-dismissed', '1'); } catch {}
    };
    document.getElementById('inapp-copy').onclick = async () => {
      try {
        await navigator.clipboard.writeText(location.href);
        document.getElementById('inapp-copy').textContent = '복사됨!';
      } catch {}
    };
  } catch {}
}
showInAppGuide();

import { CARDS } from '../data/cards.js?v=1791962003';
import { ACHIEVEMENTS, checkAchievements } from '../data/achievements.js?v=1791962003';
import { createController, TRAINERS } from './controller.js?v=1791962003';
import * as V from './view.js?v=1791962003';
import { NetSession } from '../net/session.js?v=1791962003';
import { listRooms } from '../net/fireroom.js?v=1791962003';
import { getPoints, bonusList } from '../core/engine.js?v=1791962003';
import { startBGM, stopBGM, unlockAudio } from '../audio/bgm.js?v=1791962003';
import { sfx, setSFXEnabled } from '../audio/sfx.js?v=1791962003';
import { browserStorage, loadDex, recordCatch, recordGame, loadOptions, saveOptions, loadAchv, unlockAchv, recordResult } from '../storage/store.js?v=1791962003';

// App flow: home (lobby) -> matching queue / friend room -> in-game -> result -> home.
// There is no solo mode: bots exist only as seat fillers when a queue times out.

const params = new URLSearchParams(location.search);
const AI_DELAY = params.has('fast') ? 0 : 1600; // ?fast=1 skips the pacing delay (tests)
const QUEUE_WAIT_S = params.has('fast') ? 2 : 12; // seconds before empty seats are bot-filled
const LOCAL_TURN_LIMIT_S = 45;
const FORCE_SIM = params.has('sim');

const regions = {
  header: ['header', () => V.headerHTML(ctrl, turnInfo())],
  help: ['help', () => V.helpHTML(ctrl, options)],
  rail: ['rail', V.railHTML],
  board: ['board', V.boardHTML],
  supply: ['supply', V.supplyHTML],
  me: ['me', V.meHTML],
  log: ['log', V.logHTML],
  actionbar: ['actionbar', V.dockHTML],
  sheet: ['sheet', V.sheetHTML],
};
const cache = {};
let ctrl = null;
let aiTimer = null;
let net = null; // NetSession while in a friend room / online queue / online game
let queue = null; // { mode:'sim'|'net', size, isRoom, deadline, slots, starting, searching, notice }
let netNotice = ''; // one-shot notice shown on the home/queue screen
let dexOpen = false;
let rulesOpen = false;
let achvOpen = false;
let optionsOpen = false;
let profileOpen = false;
let joinOpen = false;
const storage = browserStorage();
const options = loadOptions(storage);
setSFXEnabled(options.sfx);
V.setMyAvatar(options.avatar);

const $ = (id) => document.getElementById(id);
const myName = () => options.playerName || '도사';
const onlineAvailable = () => !FORCE_SIM && typeof window.firebase !== 'undefined';

function setHTML(id, html) {
  if (cache[id] === html) return; // keeps animated sprites from restarting needlessly
  cache[id] = html;
  $(id).innerHTML = html;
}

let lastFinished = false;
let lastTurnPlayer = -1;

// ---------- turn timer (online: from NetSession, local: tracked here) ----------

const localTimer = { key: '', deadline: 0 };

function turnInfo() {
  if (!ctrl) return { remaining: 0, limit: LOCAL_TURN_LIMIT_S };
  if (net && ctrl.mp) return { remaining: net.getTurnRemaining(), limit: Math.round((net.turnLimitMs || 45000) / 1000) };
  const g = ctrl.game;
  const key = `${g.turn}:${g.current}:${g.phase}`;
  if (localTimer.key !== key) { localTimer.key = key; localTimer.deadline = Date.now() + LOCAL_TURN_LIMIT_S * 1000; }
  return { remaining: Math.max(0, Math.ceil((localTimer.deadline - Date.now()) / 1000)), limit: LOCAL_TURN_LIMIT_S };
}

function tick() {
  // Queue countdown / bot fill
  if (queue) queueTick();
  if (!ctrl || ctrl.finished) { if (queue) render(); return; }
  const t = turnInfo();
  const fill = $('timerfill');
  if (fill) fill.style.width = Math.max(0, Math.min(100, (t.remaining / t.limit) * 100)) + '%';
  const label = $('turntimer');
  if (label) label.textContent = `⏱ ${t.remaining}초`;
  const bar = $('timerbar');
  if (bar) bar.classList.toggle('urgent', t.remaining <= 10);
  // Local game: the human seat times out like online seats do.
  if (!ctrl.mp && t.remaining <= 0 && ctrl.isHumanTurn) { ctrl.dispatch({ type: 'timeout' }); render(); }
}
setInterval(tick, 500);

function render() {
  // Game end SFX (once)
  if (ctrl && ctrl.finished && !lastFinished) {
    lastFinished = true;
    const won = ctrl.state.ranking && ctrl.state.ranking[0]?.player === ctrl.human;
    if (won) sfx.win(); else sfx.lose();
  } else if (!ctrl || !ctrl.finished) {
    lastFinished = false;
  }
  if (ctrl && !ctrl.finished && ctrl.isHumanTurn && lastTurnPlayer !== ctrl.game.current) {
    if (lastTurnPlayer !== -1) sfx.yourTurn();
  }
  lastTurnPlayer = ctrl ? ctrl.game.current : -1;

  if (ctrl) for (const [id, fn] of Object.values(regions)) setHTML(id, fn(ctrl));
  else for (const [id] of Object.values(regions)) setHTML(id, '');

  checkNetFail();
  let overlay;
  if (ctrl) overlay = ctrl.finished ? V.endHTML(ctrl) : '';
  else if (queue) overlay = V.queueHTML(queueView());
  else { overlay = V.homeHTML({ options, dex: loadDex(storage), notice: netNotice }); netNotice = ''; }
  if (dexOpen) overlay = V.dexHTML(loadDex(storage), CARDS);
  else if (rulesOpen) overlay = V.rulesHTML();
  else if (achvOpen) overlay = V.achvHTML(loadAchv(storage).unlocked);
  else if (profileOpen) overlay = V.profileHTML(options);
  else if (joinOpen) overlay = V.joinCodeHTML(netNotice);
  else if (optionsOpen) overlay = V.optionsHTML(options, !!ctrl && !ctrl.finished);
  // Don't clobber a half-typed input on the home/join screens with an identical re-render.
  setHTML('overlay', overlay);
  scheduleAI();
}

function scheduleAI() {
  if (aiTimer || !ctrl || ctrl.finished || ctrl.isHumanTurn) return;
  // In multiplayer, only the host acts for AI seats; guests wait for the relay.
  if (net && net.phase === 'playing' && net.role !== 'host') return;
  if (!ctrl.game.players[ctrl.game.current].isAI) return;
  aiTimer = setTimeout(() => {
    aiTimer = null;
    if (ctrl) {
      const snap = snapshotMovables();
      ctrl.stepAI();
      render();
      animateAIFromSnap(snap);
    }
  }, AI_DELAY);
}

// ---------- fly animations ----------

const REDUCED_MOTION = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

// Detached-but-clonable refs to cards on the table and balls in the supply,
// captured BEFORE a state change so we can fly a clone to its destination.
// Rects must be read here too — after render() the nodes are detached and measure zero.
function snapshotMovables() {
  const snap = new Map();
  document.querySelectorAll('[data-action="card"]').forEach((el) =>
    snap.set('card:' + el.dataset.card, { el, rect: el.getBoundingClientRect() }));
  document.querySelectorAll('#supply [data-action="ball"]').forEach((el) =>
    snap.set('ball:' + el.dataset.color, { el, rect: el.getBoundingClientRect() }));
  return snap;
}

function flyClone(src, dstEl, ms = 650) {
  if (!src || !dstEl || REDUCED_MOTION) return;
  const r1 = src.rect;
  const r2 = dstEl.getBoundingClientRect();
  if (!r1.width || !r2.width) return;
  const clone = src.el.cloneNode(true);
  clone.removeAttribute('data-action');
  Object.assign(clone.style, {
    position: 'fixed', left: r1.left + 'px', top: r1.top + 'px',
    width: r1.width + 'px', height: r1.height + 'px', margin: '0',
    zIndex: 60, pointerEvents: 'none',
  });
  document.body.appendChild(clone);
  const dx = r2.left + r2.width / 2 - (r1.left + r1.width / 2);
  const dy = r2.top + r2.height / 2 - (r1.top + r1.height / 2);
  const anim = clone.animate(
    [
      { transform: 'translate(0, 0) scale(1)', opacity: 1 },
      { transform: `translate(${dx * 0.7}px, ${dy * 0.7 - 24}px) scale(.7)`, opacity: 1, offset: 0.7 },
      { transform: `translate(${dx}px, ${dy}px) scale(.4)`, opacity: 0.85 },
    ],
    { duration: ms, easing: 'cubic-bezier(.3,.7,.4,1)' },
  );
  anim.onfinish = () => clone.remove();
}

function flyBalls(snap, colors, dstEl) {
  colors.forEach((c, i) => {
    const src = snap.get('ball:' + c);
    if (src) setTimeout(() => flyClone(src, dstEl, 500), i * 90);
  });
}

function animateAIFromSnap(snap) {
  const ev = ctrl.lastAIEvent;
  if (!ev) return;
  const dst = document.querySelector(`.rail-item[data-id="${ev.player}"]`);
  if (!dst) return;
  if (ev.type === 'buy' || ev.type === 'reserve') {
    flyClone(snap.get('card:' + ev.cardId), dst);
  } else if (ev.type === 'takeBalls') {
    flyBalls(snap, ev.colors, dst);
  } else if (ev.type === 'takeTwo') {
    flyBalls(snap, [ev.color, ev.color], dst);
  }
}

const cardsById = new Map(CARDS.map((c) => [c.id, c]));
let caughtLegend = false; // this game's legend catch flag (for achievements)
let achvToasts = []; // newly unlocked achievements waiting to toast
let achvToastTimer = null;

function queueAchvToasts(list) {
  achvToasts = achvToasts.concat(list);
  renderAchvToast();
}

function renderAchvToast() {
  const el = document.getElementById('achvtoast');
  if (!el) return;
  const a = achvToasts[0];
  el.innerHTML = a ? `<div class="achvtoast-in"><span class="achvicon">${a.icon}</span><div><b>업적 달성!</b><br>${a.name}</div></div>` : '';
  el.style.display = a ? 'block' : 'none';
  clearTimeout(achvToastTimer);
  if (a) achvToastTimer = setTimeout(() => { achvToasts = achvToasts.slice(1); renderAchvToast(); }, 3000);
}

const hooks = {
  onCatch: (cardId, kind) => {
    recordCatch(storage, cardId, kind);
    const card = cardsById.get(cardId);
    if (card && (card.tier === 'rare' || card.tier === 'legend')) caughtLegend = true;
  },
  onEnd: (won) => {
    recordGame(storage, won);
    if (!ctrl) return;
    const me = ctrl.me;
    const bonusColors = new Set();
    for (const card of me.tableau) for (const b of bonusList(card)) bonusColors.add(b);
    const ctx = { won, turns: ctrl.game.turn, evolutions: me.evolved.length, difficulty: ctrl.difficulty, points: getPoints(me), bonusColors, caughtLegend };
    const newly = checkAchievements(ctx, loadAchv(storage).unlocked);
    if (newly.length) {
      unlockAchv(storage, newly.map((a) => a.id));
      queueAchvToasts(newly);
    }
    recordResult(storage, { won, points: ctx.points, turns: ctx.turns, difficulty: ctx.difficulty });
    caughtLegend = false;
  },
};

// ---------- matching ----------

function resetCache() { Object.keys(cache).forEach((k) => delete cache[k]); }

function enterGame(c) {
  clearTimeout(aiTimer); aiTimer = null;
  ctrl = c;
  queue = null;
  localTimer.key = '';
  resetCache();
  window.__ctrl = ctrl; // debugging / automated tests
  if (options.bgm) startBGM('main');
  render();
}

/** Local game with the queue's seats: me + bot seat-fillers (no standalone AI mode). */
function startFilledGame(size) {
  const seedParam = params.get('seed');
  const seed = seedParam !== null ? Number(seedParam) : (crypto.getRandomValues(new Uint32Array(1))[0] || 1);
  const bots = TRAINERS.filter((n) => n !== options.avatar).slice(0, size - 1);
  enterGame(createController({ cards: CARDS, seed, humanName: myName(), aiNames: bots, hooks, difficulty: 'normal' }));
}

function startQueue(size) {
  cancelQueue();
  if (onlineAvailable()) startNetQueue(size); else startSimQueue(size, '');
}

function startSimQueue(size, notice) {
  queue = { mode: 'sim', size, isRoom: false, deadline: Date.now() + QUEUE_WAIT_S * 1000, slots: [{ name: myName(), me: true }], starting: false, notice };
  render();
}

async function startNetQueue(size) {
  queue = { mode: 'net', size, isRoom: false, deadline: 0, searching: true, starting: false, notice: '' };
  openNet();
  render();
  let target = null;
  try {
    const rooms = await listRooms();
    target = rooms.find((r) => r.title === `빠른대전 ${size}인` && r.playerCount < size);
  } catch {
    if (queue && net) { dropNet(); startSimQueue(size, '온라인 서버에 연결할 수 없어 로컬 매칭으로 진행해요.'); }
    return;
  }
  if (!queue || !net) return; // cancelled meanwhile
  queue.searching = false;
  if (target) net.guestJoin(myName(), target.code);
  else net.hostCreate(myName(), `빠른대전 ${size}인`, 45000);
}

function createFriendRoom() {
  cancelQueue();
  queue = { mode: 'net', size: options.queueSize, isRoom: true, deadline: 0, searching: false, starting: false, notice: '' };
  openNet();
  net.hostCreate(myName(), '친구방', 45000);
  render();
}

function joinFriendRoom(code) {
  const clean = String(code || '').trim().toUpperCase();
  if (clean.length < 4) { netNotice = '방 코드를 확인해주세요.'; return false; }
  cancelQueue();
  queue = { mode: 'net', size: 4, isRoom: true, deadline: 0, searching: false, starting: false, notice: '' };
  openNet();
  net.guestJoin(myName(), clean);
  return true;
}

function dropNet() {
  if (!net) return;
  const n = net; net = null;
  try { n.end(); } catch {}
}

function cancelQueue() {
  queue = null;
  dropNet();
}

// Online connection failed before reaching a lobby phase.
function checkNetFail() {
  if (!queue || queue.mode !== 'net' || !net || queue.searching || queue.failing) return;
  if (!['menu', 'hostname', 'guestname', 'guestjoin'].includes(net.phase)) return;
  queue.failing = true;
  const isRoom = queue.isRoom;
  const size = queue.size;
  setTimeout(() => {
    dropNet();
    if (isRoom) { queue = null; netNotice = netNotice || '방에 연결하지 못했어요. 다시 시도해주세요.'; render(); }
    else startSimQueue(size, '온라인 서버에 연결할 수 없어 로컬 매칭으로 진행해요.');
  }, 0);
}

function queueView() {
  const q = queue;
  const left = q.deadline ? Math.max(0, Math.ceil((q.deadline - Date.now()) / 1000)) : null;
  if (q.mode === 'sim') {
    return { title: '매칭 중…', size: q.size, slots: q.slots, countdown: left, fillBots: options.fillBots, notice: q.notice, starting: q.starting };
  }
  const names = net?.names?.length ? net.names : [myName()];
  const slots = names.map((name, i) => ({ name, me: net?.names?.length ? i === net.myIndex : true }));
  return {
    title: q.isRoom ? '친구와 방' : '매칭 중…', size: q.size, slots, countdown: left, fillBots: q.isRoom ? true : options.fillBots,
    code: q.isRoom ? net?.shortCode : '', host: net?.role === 'host' && net.phase === 'hostlobby', isRoom: q.isRoom,
    notice: q.notice, starting: q.starting,
  };
}

function queueTick() {
  const q = queue;
  if (!q || q.starting) return;
  const now = Date.now();
  if (q.mode === 'sim') {
    if (now < q.deadline) return;
    if (!options.fillBots) { render(); return; }
    // Fill the empty seats with bots, then enter after a short beat.
    const bots = TRAINERS.filter((n) => n !== options.avatar).slice(0, q.size - 1);
    q.slots = [q.slots[0], ...bots.map((name) => ({ name, bot: true }))];
    q.starting = true;
    render();
    setTimeout(() => { if (queue === q) startFilledGame(q.size); }, 900);
    return;
  }
  // net: only the host drives the clock / start.
  if (!net || net.role !== 'host' || net.phase !== 'hostlobby') return;
  if (!q.isRoom && !q.deadline) q.deadline = now + QUEUE_WAIT_S * 1000;
  if (net.names.length >= q.size) { startNetGame(q, 0); return; }
  if (!q.isRoom && now >= q.deadline && options.fillBots) startNetGame(q, q.size - net.names.length);
}

function startNetGame(q, bots) {
  q.starting = true;
  net.aiCount = Math.max(0, Math.min(4 - net.names.length, bots));
  net.hostStart();
  if (net.phase !== 'playing') { q.starting = false; q.deadline = 0; }
  render();
}

// ---------- multiplayer session plumbing ----------

function openNet() {
  if (net) return;
  net = new NetSession({
    onRender: () => render(),
    onGameStart: (c) => enterGame(c),
    onGameEnd: () => { net = null; ctrl = null; queue = null; render(); },
    onNotice: (msg) => { netNotice = msg; if (queue) queue.notice = msg; render(); },
  });
  net.myName = myName();
}

function saveProfile(name, avatar) {
  const clean = String(name || '').trim().slice(0, 12);
  options.playerName = clean;
  if (avatar) options.avatar = avatar;
  saveOptions(storage, options);
  V.setMyAvatar(options.avatar);
}

let pendingAvatar = null;

document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-action]');
  if (!el || el.disabled) return;
  unlockAudio();
  if (options.bgm && !ctrl) startBGM('calm');
  const d = el.dataset;
  switch (d.action) {
    case 'dex': dexOpen = true; break;
    case 'dex-close': dexOpen = false; break;
    case 'rules': rulesOpen = true; break;
    case 'rules-close': rulesOpen = false; break;
    case 'achv': achvOpen = true; break;
    case 'achv-close': achvOpen = false; break;
    case 'options': optionsOpen = true; break;
    case 'options-close': optionsOpen = false; break;
    case 'toggle-help':
      options.beginnerHelp = !options.beginnerHelp;
      saveOptions(storage, options);
      break;
    case 'toggle-fill':
      options.fillBots = !options.fillBots;
      saveOptions(storage, options);
      break;
    case 'toggle-bgm':
      options.bgm = !options.bgm;
      saveOptions(storage, options);
      if (options.bgm) startBGM(ctrl ? 'main' : 'calm'); else stopBGM();
      break;
    case 'toggle-sfx':
      options.sfx = !options.sfx;
      saveOptions(storage, options);
      setSFXEnabled(options.sfx);
      break;
    // ----- home / matching -----
    case 'queue-size':
      options.queueSize = Number(d.n);
      saveOptions(storage, options);
      break;
    case 'match': startQueue(options.queueSize); return;
    case 'queue-cancel': cancelQueue(); netNotice = ''; break;
    case 'room-create': createFriendRoom(); return;
    case 'room-join': joinOpen = true; netNotice = ''; break;
    case 'join-close': joinOpen = false; netNotice = ''; break;
    case 'join-go':
      if (joinFriendRoom($('joincode')?.value)) { joinOpen = false; netNotice = ''; }
      break;
    case 'room-start': if (net && queue) startNetGame(queue, options.fillBots ? Math.max(0, queue.size - net.names.length) : 0); return;
    case 'profile': profileOpen = true; pendingAvatar = options.avatar; break;
    case 'avatar': pendingAvatar = d.name; saveProfile($('profname')?.value ?? options.playerName, d.name); break;
    case 'profile-save': saveProfile($('profname')?.value, pendingAvatar || options.avatar); profileOpen = false; break;
    case 'rematch':
      dropNet(); ctrl = null; optionsOpen = false; clearTimeout(aiTimer); aiTimer = null;
      startQueue(options.queueSize);
      return;
    case 'restart':
      dropNet(); ctrl = null; queue = null; optionsOpen = false; clearTimeout(aiTimer); aiTimer = null;
      if (options.bgm) startBGM('calm');
      break;
    // ----- in-game -----
    case 'opp': ctrl.openOpp(d.id); break;
    case 'view-card':
      ctrl.viewCard(d.card, d.from === 'opp' ? { kind: 'opp', playerId: Number(d.pid) } : null);
      break;
    case 'view-back': {
      const from = ctrl.sheet && ctrl.sheet.from;
      ctrl.sheet = from || null;
      break;
    }
    case 'ball': ctrl.toggleBall(d.color); break;
    case 'clear': ctrl.clearSelection(); break;
    case 'confirm-balls': {
      const colors = [...ctrl.balls];
      const snap = snapshotMovables();
      ctrl.confirmBalls();
      sfx.takeBall();
      render();
      flyBalls(snap, colors, document.getElementById('actionbar'));
      return;
    }
    case 'card': ctrl.openCard(d.card); break;
    case 'deck': ctrl.openDeck(d.tier); break;
    case 'close': ctrl.closeSheet(); break;
    case 'buy': {
      const snap = snapshotMovables();
      const card = ctrl.cardsById.get(d.card);
      const isMaster = card && (card.tier === 'rare' || card.tier === 'legend');
      ctrl.buy(d.card);
      sfx.catch();
      if (isMaster) setTimeout(() => sfx.masterBall(), 200);
      render();
      flyClone(snap.get('card:' + d.card), document.getElementById('actionbar'));
      return;
    }
    case 'reserve': {
      const snap = snapshotMovables();
      ctrl.reserveCard(d.card);
      sfx.reserve();
      render();
      flyClone(snap.get('card:' + d.card), document.getElementById('actionbar'));
      return;
    }
    case 'reserve-deck': ctrl.reserveDeck(d.tier); sfx.reserve(); break;
    case 'discard': ctrl.toggleDiscard(d.token); break;
    case 'undiscard': ctrl.undoDiscard(d.token); break;
    case 'confirm-discard': ctrl.confirmDiscard(); sfx.discard(); break;
    case 'evolve': ctrl.evolve(d.card); sfx.evolve(); break;
    case 'skip-evolve': ctrl.skipEvolve(); break;
    case 'pass': ctrl.pass(); break;
    default: return;
  }
  render();
});

window.__render = render; // automated tests
render();
