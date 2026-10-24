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

import { CARDS } from '../data/cards.js?v=1792846825';
import { ACHIEVEMENTS, checkAchievements } from '../data/achievements.js?v=1792846825';
import { createController, TRAINERS } from './controller.js?v=1792846825';
import * as V from './view.js?v=1792846825';
import { createChatWidget } from './chat.js?v=1792846825';
import { randomLook, sanitizeLook, encodeLook, decodeLook } from './look.js?v=1792846825';
import { NetSession } from '../net/session.js?v=1792846825';
import { listRooms, watchRooms, claimName } from '../net/fireroom.js?v=1792846825';
import { getPoints, bonusList } from '../core/engine.js?v=1792846825';
import { startBGM, stopBGM, unlockAudio } from '../audio/bgm.js?v=1792846825';
import { sfx, setSFXEnabled } from '../audio/sfx.js?v=1792846825';
import { afterRender as juiceAfterRender, myTurnBanner, resetJuice, haptic } from './juice.js?v=1792846825';
import { loadMissions, missionRows, claimMission, recordGameForMissions } from '../meta/missions.js?v=1792846825';
import { NEWS } from '../data/news.js?v=1792846825';
import {
  browserStorage, loadDex, recordCatch, recordGame, loadOptions, saveOptions, loadAchv, unlockAchv, recordResult,
  loadProfile, recordNormalGame, recordRankedMatch, recordRankedLeave, rankedDisplay,
  loadInventory, claimFreeItem, equipOwnedItem,
} from '../storage/store.js?v=1792846825';
import { resolveMatch, isEarlyLeave } from '../meta/rating.js?v=1792846825';
import { RANKED, RANKED_UNLOCK, rankedUnlockStatus } from '../meta/config.js?v=1792846825';
import { itemById, itemName } from '../meta/catalog.js?v=1792846825';

// App flow: home (lobby) -> matching queue / friend room -> in-game -> result -> home.
// There is no solo mode: bots exist only as seat fillers when a queue times out.

const params = new URLSearchParams(location.search);
const AI_DELAY = params.has('fast') ? 0 : 1600; // ?fast=1 skips the pacing delay (tests)
const QUEUE_WAIT_S = params.has('fast') ? 2 : 12; // seconds before empty seats are bot-filled
const LOCAL_TURN_LIMIT_S = 25;
const FORCE_SIM = params.has('sim');
// Ranked unlock gate: off by default for development. Set RANKED_UNLOCK.enforce=true in src/meta/config.js, or open with ?lock=1.
const RANKED_ENFORCE = RANKED_UNLOCK.enforce || params.has('lock');
const SIM_JOIN_MS = params.has('fast') ? 400 : 2500; // ranked sim: one simulated user joins per step

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
let firstRun = false; // 닉네임이 없으면 첫 접속: 홈에서 바로 닉네임 설정 창을 띄운다
let profileError = '';
// 친목전 로비: 방 목록 구독 상태 + 방 만들기/비밀번호 창
const lobby = { rooms: [], status: 'idle', unsub: null }; // status: idle|loading|ok|offline
let lobbyCreate = null; // { error } while the create-room panel is open
let lobbyPw = null; // { code, error } while the password prompt is open
let shopOpen = false;
let shopTab = 'avatarFrame';
let shopToast = '';
let leaveOpen = false; // ranked leave confirmation
let curMatch = null; // { mode:'normal'|'ranked'|'private', sim, seed, startedAt, recorded }
let lastResult = null; // ranked/normal result summary shown on the end screen
const storage = browserStorage();
const options = loadOptions(storage);
setSFXEnabled(options.sfx);
V.setMyAvatar(options.avatar);
if (!options.look) { options.look = randomLook(); saveOptions(storage, options); } // 첫 실행: 무작위로 꾸며 준다
V.setMyLook(options.look);
V.setMyCosmetics(loadInventory(storage).equipped);

const $ = (id) => document.getElementById(id);
// 채팅: 친목전 방·온라인 대기실·온라인 게임에서만 보인다
const chat = createChatWidget($('chat'), { send: (t) => !!net?.sendChat(t) });
function renderChat() {
  const live = !!net && ['hostlobby', 'guestlobby', 'playing'].includes(net.phase);
  chat.update({ visible: live, log: net?.chatLog || [], mode: ctrl ? 'game' : 'lobby' });
}
const myName = () => options.playerName || '도사';
firstRun = !options.playerName;
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
  const localLimit = curMatch?.mode === 'ranked' ? RANKED.turnLimitMs / 1000 : LOCAL_TURN_LIMIT_S;
  if (!ctrl) return { remaining: 0, limit: localLimit };
  if (net && ctrl.mp) return { remaining: net.getTurnRemaining(), limit: Math.round((net.turnLimitMs || 25000) / 1000) };
  const g = ctrl.game;
  const key = `${g.turn}:${g.current}:${g.phase}`;
  if (localTimer.key !== key) { localTimer.key = key; localTimer.deadline = Date.now() + localLimit * 1000; }
  return { remaining: Math.max(0, Math.ceil((localTimer.deadline - Date.now()) / 1000)), limit: localLimit };
}

function tick() {
  // Queue countdown / bot fill
  if (queue) queueTick();
  if (!ctrl || ctrl.finished) { if (queue) render(); return; }
  const t = turnInfo();
  const label = $('turntimer');
  if (label) label.textContent = String(t.remaining);
  const bar = $('timerbar');
  if (bar) {
    bar.style.setProperty('--p', Math.max(0, Math.min(100, (t.remaining / t.limit) * 100)));
    bar.classList.toggle('urgent', t.remaining <= 7);
  }
  // Local game: the human seat times out like online seats do.
  if (!ctrl.mp && t.remaining <= 0 && ctrl.isHumanTurn) { ctrl.dispatch({ type: 'timeout' }); render(); }
}
setInterval(tick, 250); // 시간 초과 시 바로 차례가 넘어가도록 촘촘히

function render() {
  // Game end SFX (once)
  if (ctrl && ctrl.finished && !lastFinished) {
    lastFinished = true;
    // 결과 화면 위에 성장 연출·미니 알림이 남지 않게 정리
    document.querySelectorAll('.evofx, .evo-mini').forEach((el) => el.remove());
    const won = ctrl.state.ranking && ctrl.state.ranking[0]?.player === ctrl.human;
    if (won) sfx.win(); else sfx.lose();
    finalizeMatch(won);
  } else if (!ctrl || !ctrl.finished) {
    lastFinished = false;
  }
  if (ctrl && !ctrl.finished && ctrl.isHumanTurn && lastTurnPlayer !== ctrl.game.current) {
    if (lastTurnPlayer !== -1) { sfx.yourTurn(); myTurnBanner(); } // 내 차례 배너
  }
  lastTurnPlayer = ctrl ? ctrl.game.current : -1;

  if (ctrl) for (const [id, fn] of Object.values(regions)) setHTML(id, fn(ctrl));
  else for (const [id] of Object.values(regions)) setHTML(id, '');

  checkNetFail();
  { const ab = $('actionbar'); if (ab && ctrl) document.documentElement.style.setProperty('--dockh', ab.offsetHeight + 'px'); }
  syncLobbyWatch();
  document.body.classList.toggle('on-result', !!(ctrl && ctrl.finished)); // 결과 화면 전용 배치(업적 알림 위치)
  // 온라인 상대의 꾸민 모습 (오프라인/AI 게임은 초상화)
  V.setSeatLooks(net?.looks?.length ? net.looks.map((c) => (c ? decodeLook(c) : null)) : null);
  let overlay;
  if (ctrl) overlay = ctrl.finished ? V.endHTML(ctrl, lastResult) : '';
  else if (queue) overlay = V.queueHTML(queueView());
  else {
    const profile = loadProfile(storage);
    const banMin = profile.ranked.queueBanUntil > Date.now() ? Math.ceil((profile.ranked.queueBanUntil - Date.now()) / 60000) : 0;
    overlay = V.homeHTML({ options, dex: loadDex(storage), notice: netNotice, profile, gate: rankedUnlockStatus(profile, RANKED_ENFORCE), ban: banMin, sim: FORCE_SIM, lobby,
      missions: missionRows(loadMissions(storage)), wallet: loadInventory(storage).wallet, news: NEWS });
    netNotice = '';
  }
  const prof = { error: profileError, name: pendingName ?? options.playerName, look: pendingLook || options.look, tab: lookTab, busy: profileBusy };
  if (firstRun && !ctrl && !queue) overlay = V.profileHTML(options, { ...prof, first: true });
  else if (dexOpen) overlay = V.dexHTML(loadDex(storage), CARDS);
  else if (rulesOpen) overlay = V.rulesHTML();
  else if (achvOpen) overlay = V.achvHTML(loadAchv(storage).unlocked);
  else if (profileOpen) overlay = V.profileHTML(options, prof);
  else if (lobbyCreate) overlay = V.lobbyCreateHTML({ name: myName(), size: options.queueSize, error: lobbyCreate.error });
  else if (lobbyPw) overlay = V.lobbyPwHTML({ room: lobby.rooms.find((r) => r.code === lobbyPw.code), error: lobbyPw.error });
  else if (shopOpen) overlay = V.shopHTML({ inv: loadInventory(storage), tab: shopTab, toast: shopToast });
  else if (leaveOpen && ctrl && !ctrl.finished) overlay = V.leaveConfirmHTML({ voidLeave: isEarlyLeave(ctrl.game.turn, ctrl.game.players.length) });
  else if (optionsOpen) overlay = V.optionsHTML(options, !!ctrl && !ctrl.finished);
  // Don't clobber a half-typed input on the home/join screens with an identical re-render.
  setHTML('overlay', overlay);
  renderChat();
  juiceAfterRender(ctrl); // 점수/토큰 범프, +N 팝업, 마지막 라운드 알림
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

let evoFxTimer = 0;
function showEvolveFx(fromId, toId, player) {
  const from = cardsById.get(fromId), to = cardsById.get(toId);
  if (!from || !to) return;
  const others = ctrl && player != null && player !== ctrl.human;
  if (others) { showEvolveMini(from, to, player); return; }
  document.querySelector('.evofx')?.remove();
  document.body.insertAdjacentHTML('beforeend', V.evolveFxHTML(from, to));
  const el = document.body.lastElementChild;
  clearTimeout(evoFxTimer);
  evoFxTimer = setTimeout(() => el.remove(), 2900);
}

// 상대의 성장은 화면을 가리지 않게 오른쪽 플레이어 줄 그 사람 얼굴 옆에 작게 잠깐 보여 준다
function showEvolveMini(from, to, player) {
  const anchor = document.querySelector(`.rail-item[data-id="${player}"]`);
  if (!anchor) return;
  document.querySelector(`.evo-mini[data-seat="${player}"]`)?.remove();
  const r = anchor.getBoundingClientRect();
  document.body.insertAdjacentHTML('beforeend', V.evolveMiniHTML(from, to, player));
  const el = document.body.lastElementChild;
  el.style.right = `${window.innerWidth - r.left + 6}px`;
  el.style.top = `${r.top + r.height / 2}px`;
  sfx.evolve();
  setTimeout(() => el.remove(), 2200);
}

const hooks = {
  onEvolve: (fromId, toId, player) => showEvolveFx(fromId, toId, player),
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
  curMatch = {
    mode: queue?.ranked ? 'ranked' : queue?.isRoom ? 'private' : 'normal',
    sim: queue?.mode === 'sim', seed: c.seed, startedAt: Date.now(), recorded: false,
    ratingBefore: loadProfile(storage).ranked.rating,
  };
  lastResult = null;
  leaveOpen = false;
  ctrl.simUsers = curMatch.mode === 'ranked' && curMatch.sim; // view labels these AI seats "시뮬 유저", not bots
  queue = null;
  localTimer.key = '';
  resetCache();
  resetJuice(); // 이전 게임의 연출 상태 초기화
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
  if (options.mode === 'ranked') { startRankedQueue(); return; }
  if (onlineAvailable()) startNetQueue(size); else startSimQueue(size, '');
}

// Ranked: 4 players fixed, never bot-filled. Without a server it is only reachable in ?sim=1 (simulated users).
function startRankedQueue() {
  const profile = loadProfile(storage);
  const gate = rankedUnlockStatus(profile, RANKED_ENFORCE);
  if (!gate.unlocked) { netNotice = '랭킹전이 아직 잠겨 있어요. 해금 조건을 확인해주세요.'; render(); return; }
  if (profile.ranked.queueBanUntil > Date.now()) { netNotice = '큐 제한 중이에요. 잠시 후 다시 시도해주세요.'; render(); return; }
  if (FORCE_SIM) {
    queue = { mode: 'sim', ranked: true, size: RANKED.playerCount, isRoom: false, deadline: 0, startedAt: Date.now(), slots: [{ name: myName(), me: true }], starting: false, notice: '' };
    render();
  } else if (onlineAvailable()) {
    startNetQueue(RANKED.playerCount, true);
  } else {
    netNotice = '랭킹전은 온라인 연결이 필요해요. (시뮬 확인은 ?sim=1)';
    render();
  }
}

function startSimQueue(size, notice) {
  queue = { mode: 'sim', size, isRoom: false, deadline: Date.now() + QUEUE_WAIT_S * 1000, slots: [{ name: myName(), me: true }], starting: false, notice };
  render();
}

async function startNetQueue(size, ranked = false) {
  const title = ranked ? `랭킹전 ${size}인` : `빠른대전 ${size}인`;
  queue = { mode: 'net', ranked, size, isRoom: false, deadline: 0, startedAt: Date.now(), searching: true, starting: false, notice: '' };
  openNet();
  render();
  let target = null;
  try {
    const rooms = await listRooms();
    target = rooms.find((r) => r.title === title && r.playerCount < size);
  } catch {
    if (queue && net) {
      dropNet();
      if (ranked) { queue = null; netNotice = '온라인 서버에 연결할 수 없어요. 랭킹전은 봇/로컬로 대체되지 않아요.'; render(); }
      else startSimQueue(size, '온라인 서버에 연결할 수 없어 로컬 매칭으로 진행해요.');
    }
    return;
  }
  if (!queue || !net) return; // cancelled meanwhile
  queue.searching = false;
  if (target) net.guestJoin(myName(), target.code);
  else net.hostCreate(myName(), title, ranked ? RANKED.turnLimitMs : 25000);
}

// ---------- 친목전 로비 ----------
// 시뮬(?sim=1)에서는 서버가 없으니 화면 확인용 예시 방을 보여 준다.
const SIM_ROOMS = [
  { code: 'SIMAAA', title: '퇴근 후 한 판', hostName: '솔이', playerCount: 2, size: 4, locked: false, kind: 'lobby' },
  { code: 'SIMBBB', title: '우리 반 친구들만', hostName: '바우', playerCount: 1, size: 3, locked: true, pwHash: '', kind: 'lobby' },
  { code: 'SIMCCC', title: '초보 환영 🙂', hostName: '달래', playerCount: 4, size: 4, locked: false, kind: 'lobby' },
];
function lobbyActive() { return !ctrl && !queue && options.mode === 'friendly'; }
function syncLobbyWatch() {
  const want = lobbyActive();
  if (!want) { if (lobby.unsub) { lobby.unsub(); lobby.unsub = null; } if (lobby.status !== 'idle') lobby.status = 'idle'; return; }
  if (lobby.status !== 'idle') return;
  if (FORCE_SIM) { lobby.rooms = SIM_ROOMS; lobby.status = 'ok'; return; }
  if (!onlineAvailable()) { lobby.status = 'offline'; return; }
  lobby.status = 'loading';
  try {
    lobby.unsub = watchRooms((rooms) => {
      lobby.rooms = rooms.filter((r) => r.kind === 'lobby');
      lobby.status = 'ok';
      render();
    });
  } catch { lobby.status = 'offline'; }
}
async function sha256(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('ohsp-pw:' + text));
  return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, '0')).join('');
}
async function createLobbyRoom(title, size, pw) {
  const clean = String(title || '').trim().slice(0, 20) || `${myName()}의 방`;
  if (FORCE_SIM || !onlineAvailable()) { lobbyCreate = { error: '온라인 연결이 있어야 방을 만들 수 있어요.' }; render(); return; }
  const pwHash = pw ? await sha256(pw) : '';
  lobbyCreate = null;
  cancelQueue();
  queue = { mode: 'net', size, isRoom: true, title: clean, locked: !!pwHash, deadline: 0, searching: false, starting: false, notice: '' };
  openNet();
  net.hostCreate(myName(), clean, 25000, { kind: 'lobby', size, pwHash });
  render();
}
async function joinLobbyRoom(code, pw = null) {
  const room = lobby.rooms.find((r) => r.code === code);
  if (!room) { netNotice = '방이 사라졌어요. 목록을 다시 확인해 주세요.'; lobbyPw = null; render(); return; }
  if (room.playerCount >= room.size) { netNotice = '방이 가득 찼어요.'; lobbyPw = null; render(); return; }
  if (room.locked) {
    if (pw == null) { lobbyPw = { code, error: '' }; render(); return; }
    if (!pw || (await sha256(pw)) !== room.pwHash) { lobbyPw = { code, error: '비밀번호가 맞지 않아요.' }; render(); return; }
  }
  if (FORCE_SIM) { lobbyPw = null; netNotice = '시뮬 모드에서는 예시 방에 들어갈 수 없어요.'; render(); return; }
  lobbyPw = null;
  cancelQueue();
  queue = { mode: 'net', size: room.size, isRoom: true, title: room.title, locked: room.locked, deadline: 0, searching: false, starting: false, notice: '' };
  openNet();
  net.guestJoin(myName(), code);
  render();
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
  const ranked = queue.ranked;
  setTimeout(() => {
    dropNet();
    if (ranked) { queue = null; netNotice = netNotice || '온라인 서버에 연결할 수 없어요. 랭킹전은 봇/로컬로 대체되지 않아요.'; render(); }
    else if (isRoom) { queue = null; netNotice = netNotice || '방에 연결하지 못했어요. 다시 시도해주세요.'; render(); }
    else startSimQueue(size, '온라인 서버에 연결할 수 없어 로컬 매칭으로 진행해요.');
  }, 0);
}

function queueView() {
  const q = queue;
  const left = q.deadline ? Math.max(0, Math.ceil((q.deadline - Date.now()) / 1000)) : null;
  const waited = q.startedAt ? Math.floor((Date.now() - q.startedAt) / 1000) : 0;
  const tierDisp = q.ranked ? rankedDisplay(loadProfile(storage)) : null;
  if (q.mode === 'sim') {
    return { title: q.ranked ? '랭킹전 매칭 중…' : '매칭 중…', size: q.size, slots: q.slots, countdown: left, fillBots: q.ranked ? false : options.fillBots, notice: q.notice, starting: q.starting, ranked: !!q.ranked, waited, tierDisp };
  }
  const names = net?.names?.length ? net.names : [myName()];
  const slots = names.map((name, i) => ({ name, me: net?.names?.length ? i === net.myIndex : true }));
  return {
    title: q.isRoom ? (q.title || '친목전 방') : q.ranked ? '랭킹전 매칭 중…' : '매칭 중…', size: q.size, slots, countdown: left, fillBots: q.ranked ? false : q.isRoom ? true : options.fillBots,
    code: '', locked: !!q.locked, host: net?.role === 'host' && net.phase === 'hostlobby', isRoom: q.isRoom,
    notice: q.notice, starting: q.starting, ranked: !!q.ranked, waited, tierDisp,
  };
}

function queueTick() {
  const q = queue;
  if (!q || q.starting) return;
  const now = Date.now();
  if (q.mode === 'sim' && q.ranked) {
    // Simulated users join one by one; never bots. Start only when all 4 seats are filled.
    const want = Math.min(q.size, 1 + Math.floor((now - q.startedAt) / SIM_JOIN_MS));
    const names = TRAINERS.filter((n) => n !== options.avatar);
    while (q.slots.length < want) q.slots.push({ name: names[q.slots.length - 1], sim: true });
    if (q.slots.length >= q.size) {
      q.starting = true;
      render();
      setTimeout(() => { if (queue === q) startFilledGame(q.size); }, 900);
    }
    return;
  }
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
  if (!q.isRoom && !q.ranked && !q.deadline) q.deadline = now + QUEUE_WAIT_S * 1000;
  if (net.names.length >= q.size) { startNetGame(q, 0); return; }
  if (q.ranked) return; // ranked never fills with bots: keep waiting
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
    onEvolve: (fromId, toId, player) => showEvolveFx(fromId, toId, player),
    onChat: () => { renderChat(); sfx.chat(); },
    onGameEnd: () => { net = null; ctrl = null; queue = null; render(); },
    onNotice: (msg) => { netNotice = msg; if (queue) queue.notice = msg; render(); },
  });
  net.myName = myName();
  net.myLook = encodeLook(options.look);
}

// ---------- match bookkeeping (ranked rating / normal stats) ----------

// Opponent ratings are not exchanged yet (no protocol change): net games assume equal ratings (TODO: carry rating in the
// seat info + consensus result record). Sim games use fixed offsets so the screen shows non-trivial values.
const SIM_OFFSETS = [0, -120, 60, 140];
function matchInputs(c, profile) {
  const n = c.game.players.length;
  const mine = profile.ranked.rating;
  const ratings = Array.from({ length: n }, (_, i) => (i === c.human ? mine : mine + (curMatch.sim ? SIM_OFFSETS[(i - c.human + n) % n % 4] : 0)));
  const gamesPlayed = Array.from({ length: n }, (_, i) => (i === c.human ? profile.ranked.gamesTotal : 30));
  return { ratings, gamesPlayed, n };
}

function finalizeMatch(won) {
  if (!curMatch || curMatch.recorded || !ctrl) return;
  curMatch.recorded = true;
  const mode = curMatch.mode;
  // 오늘의 과제 진행 (모든 모드): 판 수·우승·영입·성장
  recordGameForMissions(storage, { won, recruited: ctrl.me.tableau.length, evolved: ctrl.me.evolved.length });
  if (mode === 'normal') recordNormalGame(storage, won);
  if (mode !== 'ranked') { lastResult = { mode }; return; }
  const profile = loadProfile(storage);
  const { ratings, gamesPlayed, n } = matchInputs(ctrl, profile);
  const ranks = Array(n).fill(n);
  for (const r of ctrl.state.ranking) ranks[r.player] = r.rank;
  const res = resolveMatch({ ratings, ranks, gamesPlayed });
  const me = ctrl.human;
  const myRow = ctrl.state.ranking.find((r) => r.player === me);
  const out = recordRankedMatch(storage, {
    matchId: `${curMatch.seed}-${curMatch.startedAt}`, seed: curMatch.seed, playerCount: n, rank: ranks[me], points: myRow?.points ?? 0,
    delta: res.deltas[me], ratingBefore: profile.ranked.rating, sim: curMatch.sim,
    players: ctrl.state.ranking.map((r) => ({ name: ctrl.state.players[r.player].name, seat: r.player, isBot: false, sim: curMatch.sim && r.player !== me, rank: r.rank, points: r.points })),
  });
  lastResult = { mode, sim: curMatch.sim, change: { ...out.change, delta: res.deltas[me] } };
}

// Leaving an unfinished ranked game (confirmed): last place + penalty, or void when it is still early.
function leaveRankedGame() {
  if (!ctrl || !curMatch || curMatch.mode !== 'ranked' || curMatch.recorded) return;
  curMatch.recorded = true;
  const profile = loadProfile(storage);
  const { ratings, gamesPlayed, n } = matchInputs(ctrl, profile);
  const me = ctrl.human;
  const early = isEarlyLeave(ctrl.game.turn, n);
  const leftAt = Array(n).fill(null);
  leftAt[me] = Date.now();
  const res = resolveMatch({ ratings, ranks: Array.from({ length: n }, (_, i) => i + 1), gamesPlayed, leftAt, early });
  recordRankedLeave(storage, {
    voided: res.voided, delta: res.deltas[me], rank: res.ranks[me], matchId: `${curMatch.seed}-${curMatch.startedAt}`,
    seed: curMatch.seed, playerCount: n, ratingBefore: profile.ranked.rating, sim: curMatch.sim,
  });
}

function saveProfile(name, avatar) {
  const clean = String(name || '').trim().slice(0, 12);
  options.playerName = clean;
  if (avatar) options.avatar = avatar;
  saveOptions(storage, options);
  V.setMyAvatar(options.avatar);
}

let pendingAvatar = null;
let pendingName = null; // 프로필 창에서 입력 중인 닉네임 (다시 그려도 유지)
let pendingLook = null; // 프로필 창에서 꾸미는 중인 모습 (저장 전)
let lookTab = 'hair';
let profileBusy = false;

// 기기 id: 닉네임 등록부의 주인 표시 (로그인 없이 기기 단위로 구분)
function deviceId() {
  try {
    let id = localStorage.getItem('ohsp-device');
    if (!id) { id = Array.from(crypto.getRandomValues(new Uint8Array(12)), (b) => b.toString(16).padStart(2, '0')).join(''); localStorage.setItem('ohsp-device', id); }
    return id;
  } catch { return 'nodevice'; }
}
// 'ok' | 'taken' | 'offline' (서버 확인 불가 시에는 막지 않는다)
async function checkName(name, prev) {
  if (FORCE_SIM || !onlineAvailable()) return 'offline';
  try { return await claimName(name, deviceId(), prev); } catch { return 'offline'; }
}
async function handleProfileSave() {
  if (profileBusy) return;
  const typed = String($('profname')?.value ?? pendingName ?? '').trim().slice(0, 12);
  pendingName = typed;
  if (firstRun && !typed) { profileError = '닉네임을 입력해 주세요.'; render(); return; }
  const prev = options.playerName;
  if (typed && typed !== prev) {
    profileBusy = true; profileError = '닉네임 확인 중…'; render();
    const r = await checkName(typed, prev);
    profileBusy = false;
    if (r === 'taken') { profileError = '이미 다른 도사가 쓰는 닉네임이에요. 다른 이름을 골라 주세요.'; render(); return; }
  }
  saveProfile(typed, pendingAvatar || options.avatar);
  if (pendingLook) { options.look = sanitizeLook(pendingLook); saveOptions(storage, options); V.setMyLook(options.look); if (net) net.myLook = encodeLook(options.look); }
  profileOpen = false; firstRun = false; profileError = ''; pendingName = null; pendingLook = null;
  render();
}
// 예전부터 쓰던 닉네임도 등록부에 올려 둔다. 다른 기기가 먼저 등록했으면 바꾸도록 안내.
async function registerExistingName() {
  if (!options.playerName) return;
  const r = await checkName(options.playerName, '');
  if (r === 'taken' && !ctrl) { profileOpen = true; pendingAvatar = options.avatar; pendingName = options.playerName; profileError = '다른 도사가 먼저 등록한 닉네임이에요. 새 닉네임을 정해 주세요.'; render(); }
}

document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-action]');
  if (!el || el.disabled) return;
  unlockAudio();
  if (options.bgm && !ctrl) startBGM('calm');
  const d = el.dataset;
  // 메뉴·탭 버튼 공통 클릭음 (게임 행동은 각자 고유 효과음이 있어 제외)
  if (!['ball', 'confirm-balls', 'buy', 'reserve', 'reserve-deck', 'evolve', 'discard', 'confirm-discard'].includes(d.action)) sfx.click();
  switch (d.action) {
    case 'dex': dexOpen = true; break;
    case 'mission-claim': {
      const r = claimMission(storage, d.id);
      if (r.ok) { sfx.catch(); haptic(20); }
      break;
    }
    case 'match-scroll': // 하단 '대전' 탭: 일반·랭킹전은 바로 매칭, 친목전은 방 목록으로 스크롤
      if (options.mode === 'friendly') { document.querySelector('.home-match')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
      if (options.mode === 'ranked' && document.querySelector('.btn.bigstart.ranked:disabled')) { document.querySelector('.home-match')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
      startQueue(options.queueSize); return;
    case 'dex-close': dexOpen = false; break;
    case 'mode': options.mode = ['ranked', 'friendly'].includes(d.mode) ? d.mode : 'normal'; saveOptions(storage, options); netNotice = ''; break;
    case 'shop': shopOpen = true; shopToast = ''; break;
    case 'shop-close': shopOpen = false; shopToast = ''; break;
    case 'shop-tab': shopTab = d.tab; shopToast = ''; break;
    case 'shop-claim': {
      const r = claimFreeItem(storage, d.item);
      shopToast = r.ok ? `${itemName(itemById(d.item))}을(를) 받았어요!` : '받을 수 없는 아이템이에요.';
      break;
    }
    case 'shop-equip': {
      const r = equipOwnedItem(storage, d.item);
      if (r.ok) { V.setMyCosmetics(loadInventory(storage).equipped); resetCache(); }
      shopToast = r.ok ? `${itemName(itemById(d.item))} 적용 완료` : r.error === 'emote_slots_full' ? '이모트 칸이 가득 찼어요.' : '장착할 수 없어요.';
      break;
    }
    case 'leave-cancel': leaveOpen = false; break;
    case 'leave-confirm':
      leaveOpen = false;
      leaveRankedGame();
      dropNet(); ctrl = null; queue = null; curMatch = null; optionsOpen = false; clearTimeout(aiTimer); aiTimer = null;
      if (options.bgm) startBGM('calm');
      break;
    case 'rules': rulesOpen = true; break;
    case 'rules-close': rulesOpen = false; break;
    case 'achv': achvOpen = true; break;
    case 'achv-close': achvOpen = false; break;
    case 'options': optionsOpen = true; break;
    case 'options-close': optionsOpen = false; break;
    case 'toggle-help':
      options.beginnerHelp = !options.beginnerHelp;
      if (options.beginnerHelp) V.resetTips(); // 다시 켜면 팁을 처음부터 한 번씩
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
    case 'lobby-create': lobbyCreate = { error: '' }; netNotice = ''; break;
    case 'lobby-create-close': lobbyCreate = null; break;
    case 'lobby-size': options.queueSize = Number(d.n); saveOptions(storage, options); break;
    case 'lobby-create-go':
      createLobbyRoom($('lobbytitle')?.value, options.queueSize, String($('lobbypw')?.value ?? '').trim());
      return;
    case 'lobby-join': netNotice = ''; joinLobbyRoom(d.code); return;
    case 'lobby-pw-close': lobbyPw = null; break;
    case 'lobby-pw-go': if (lobbyPw) joinLobbyRoom(lobbyPw.code, String($('lobbypwin')?.value ?? '')); return;
    case 'room-start': if (net && queue) startNetGame(queue, options.fillBots ? Math.max(0, queue.size - net.names.length) : 0); return;
    case 'profile': profileOpen = true; pendingAvatar = options.avatar; pendingName = null; pendingLook = null; profileError = ''; break;
    case 'look-tab': pendingName = $('profname')?.value ?? pendingName; lookTab = d.k; break;
    case 'look-pick': pendingName = $('profname')?.value ?? pendingName; pendingLook = sanitizeLook({ ...(pendingLook || options.look), [d.k]: d.v }); break;
    case 'look-random': pendingName = $('profname')?.value ?? pendingName; pendingLook = randomLook(); break;
    case 'profile-save': handleProfileSave(); return;
    case 'profile-cancel': profileOpen = false; pendingLook = null; pendingName = null; profileError = ''; break;
    case 'rematch':
      curMatch = null;
      dropNet(); ctrl = null; optionsOpen = false; clearTimeout(aiTimer); aiTimer = null;
      startQueue(options.queueSize);
      return;
    case 'restart':
      if (ctrl && !ctrl.finished && curMatch?.mode === 'ranked') { optionsOpen = false; leaveOpen = true; break; }
      curMatch = null;
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
      sfx.catch(); haptic(20); // 영입 손맛
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
    case 'evolve': ctrl.evolve(d.card); sfx.evolve(); haptic([20, 40, 30]); break;
    case 'skip-evolve': ctrl.skipEvolve(); break;
    case 'pass': ctrl.pass(); break;
    default: return;
  }
  render();
});

// 닉네임 입력 중 Enter = 저장
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;
  const go = { profname: 'profile-save', lobbytitle: 'lobby-create-go', lobbypw: 'lobby-create-go', lobbypwin: 'lobby-pw-go' }[e.target?.id];
  if (go) document.querySelector(`[data-action="${go}"]`)?.click();
});

window.__render = render; // automated tests
window.__chat = chat; // automated tests (screenshots without a server)
render();
registerExistingName();

// 시작 화면: 그림이 다 불러와지면(최소 0.6초) 걷어낸다. 늦어도 4초 뒤에는 무조건 걷는다.
{
  const sp = document.getElementById('splash');
  const t0 = performance.now();
  const hide = () => { if (!sp || sp.classList.contains('hide')) return; sp.classList.add('hide'); setTimeout(() => sp.remove(), 600); };
  const later = () => setTimeout(hide, Math.max(0, 600 - (performance.now() - t0)));
  if (document.readyState === 'complete') later(); else window.addEventListener('load', later, { once: true });
  setTimeout(hide, 4000);
}
