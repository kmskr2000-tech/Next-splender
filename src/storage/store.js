// localStorage persistence: Shinsu-rok (collection log) (cumulative caught record) and the in-progress game save.
// Storage is injected so tests can use a Map-backed fake; every access is try/catch'd because
// localStorage can throw (private mode, blocked site data) and the game must still run without it.

export const DEX_KEY = 'ohsp-dex-v1';
export const SAVE_KEY = 'ohsp-save-v1';
export const OPTS_KEY = 'ohsp-opts-v1';
export const ACHV_KEY = 'ohsp-achv-v1';
export const RECORDS_KEY = 'ohsp-records-v1';
export const PROFILE_KEY = 'ohsp-profile-v1';
export const INV_KEY = 'ohsp-inv-v1';

import { newRanked, applyRankedResult, applyVoidPenalty, TIERS, displayOf, leaveQueueBan } from '../meta/rating.js?v=1791962003';
import { RANKED } from '../meta/config.js?v=1791962003';
import { newInventory, sanitizeInventory, claimItem, equipItem } from '../meta/cosmetics.js?v=1791962003';

export function browserStorage() {
  try { return globalThis.localStorage ?? null; } catch { return null; }
}

function readJSON(storage, key) {
  try {
    const raw = storage?.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function writeJSON(storage, key, value) {
  try { storage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
}

const isObj = (x) => x !== null && typeof x === 'object' && !Array.isArray(x);

// ---------- Shinsu-rok (collection log) ----------
// { v:1, caught: { [cardId]: { n, first, last, evolved } }, games: { played, won } }

const emptyDex = () => ({ v: 1, caught: {}, games: { played: 0, won: 0 } });

export function loadDex(storage) {
  const d = readJSON(storage, DEX_KEY);
  if (!isObj(d) || d.v !== 1 || !isObj(d.caught)) return emptyDex();
  const dex = emptyDex();
  for (const [id, e] of Object.entries(d.caught)) {
    if (isObj(e) && Number.isInteger(e.n) && e.n > 0) {
      dex.caught[id] = { n: e.n, first: Number(e.first) || 0, last: Number(e.last) || 0, evolved: Math.max(0, e.evolved | 0) };
    }
  }
  if (isObj(d.games)) dex.games = { played: Math.max(0, d.games.played | 0), won: Math.max(0, d.games.won | 0) };
  return dex;
}

// kind: 'buy' (captured) | 'evolve' (obtained by evolution). Both count as "caught".
export function recordCatch(storage, cardId, kind = 'buy', now = Date.now()) {
  const dex = loadDex(storage);
  const e = dex.caught[cardId] ?? { n: 0, first: now, last: now, evolved: 0 };
  e.n += 1;
  e.last = now;
  if (kind === 'evolve') e.evolved += 1;
  dex.caught[cardId] = e;
  writeJSON(storage, DEX_KEY, dex);
  return dex;
}

export function recordGame(storage, won) {
  const dex = loadDex(storage);
  dex.games.played += 1;
  if (won) dex.games.won += 1;
  writeJSON(storage, DEX_KEY, dex);
  return dex;
}

export function dexSummary(dex, cards) {
  const ids = new Set(cards.map((c) => c.id));
  const caught = Object.keys(dex.caught).filter((id) => ids.has(id)).length;
  return { caught, total: cards.length };
}

// ---------- game save ----------
// { v:1, savedAt, seed, humanName, aiNames, log, game }  — game is the engine's plain-JSON state.

export function saveGame(storage, snap, now = Date.now()) {
  return writeJSON(storage, SAVE_KEY, { v: 1, savedAt: now, ...snap });
}

export function clearSave(storage) {
  try { storage?.removeItem(SAVE_KEY); } catch { /* ignore */ }
}

// Returns the save only when it is structurally sound AND resumable; anything else is dropped
// (a corrupt save must never brick the start screen).
export function loadSave(storage, cards) {
  const s = readJSON(storage, SAVE_KEY);
  if (!isObj(s) || s.v !== 1 || !isObj(s.game) || typeof s.humanName !== 'string' || !Array.isArray(s.aiNames)) return null;
  const g = s.game;
  if (!Array.isArray(g.players) || g.players.length < 2 || g.players.length > 4) return null;
  if (!isObj(g.supply) || !isObj(g.table) || !isObj(g.decks) || typeof g.rng !== 'number') return null;
  if (g.phase === 'finished' || g.ranking) return null;
  const ids = new Set(cards.map((c) => c.id));
  const known = (c) => isObj(c) && ids.has(c.id);
  for (const p of g.players) {
    if (!Array.isArray(p.tableau) || !Array.isArray(p.hand) || !Array.isArray(p.evolved) || !isObj(p.tokens)) return null;
    if (![...p.tableau, ...p.hand, ...p.evolved].every(known)) return null;
  }
  for (const k of Object.keys(g.table)) if (!Array.isArray(g.table[k]) || !g.table[k].every((c) => c === null || known(c))) return null;
  for (const k of Object.keys(g.decks)) if (!Array.isArray(g.decks[k]) || !g.decks[k].every(known)) return null;
  return s;
}

// ---------- Options ----------
// { v:1, beginnerHelp: bool }

const defaultOptions = () => ({ v: 1, beginnerHelp: true, difficulty: 'normal', personality: 'random', playerName: '', avatar: '하늘', queueSize: 4, fillBots: true, bgm: true, sfx: true, mode: 'normal' });

const AVATARS = new Set(['하늘', '솔이', '바우', '달래']); // representative character = trainer portrait name
const DIFFS = new Set(['easy', 'normal', 'hard']);
const PERSS = new Set(['random', 'specialized', 'opportunistic', 'balanced']);

export function loadOptions(storage) {
  const o = readJSON(storage, OPTS_KEY);
  if (!isObj(o)) return defaultOptions();
  return {
    v: 1,
    beginnerHelp: o.beginnerHelp !== false,
    difficulty: DIFFS.has(o.difficulty) ? o.difficulty : 'normal',
    personality: PERSS.has(o.personality) ? o.personality : 'random',
    playerName: typeof o.playerName === 'string' ? o.playerName.slice(0, 12) : '',
    avatar: AVATARS.has(o.avatar) ? o.avatar : '하늘',
    queueSize: [2, 3, 4].includes(o.queueSize) ? o.queueSize : 4,
    fillBots: o.fillBots !== false,
    bgm: o.bgm !== false,
    sfx: o.sfx !== false,
    mode: o.mode === 'ranked' ? 'ranked' : 'normal',
  };
}

export function saveOptions(storage, opts) {
  writeJSON(storage, OPTS_KEY, {
    v: 1,
    beginnerHelp: !!opts.beginnerHelp,
    difficulty: DIFFS.has(opts.difficulty) ? opts.difficulty : 'normal',
    personality: PERSS.has(opts.personality) ? opts.personality : 'random',
    playerName: typeof opts.playerName === 'string' ? opts.playerName.slice(0, 12) : '',
    avatar: AVATARS.has(opts.avatar) ? opts.avatar : '하늘',
    queueSize: [2, 3, 4].includes(opts.queueSize) ? opts.queueSize : 4,
    fillBots: opts.fillBots !== false,
    bgm: !!opts.bgm,
    sfx: !!opts.sfx,
    mode: opts.mode === 'ranked' ? 'ranked' : 'normal',
  });
}

// ---------- Achievements ----------
// { v:1, unlocked: { [id]: timestamp } }

export function loadAchv(storage) {
  const o = readJSON(storage, ACHV_KEY);
  if (!isObj(o) || !isObj(o.unlocked)) return { v: 1, unlocked: {} };
  return { v: 1, unlocked: o.unlocked };
}

export function unlockAchv(storage, ids, now = Date.now()) {
  const a = loadAchv(storage);
  let changed = false;
  for (const id of ids) {
    if (!a.unlocked[id]) { a.unlocked[id] = now; changed = true; }
  }
  if (changed) writeJSON(storage, ACHV_KEY, a);
  return changed;
}

// ---------- Records ----------
// Victory score: win ? 1000 + points*10 + max(0, 60-turns)*5 + diffBonus : points*10
// { v:1, best: number, games: number, wins: number, history: [{score, won, points, turns, difficulty, date}] }

const DIFF_BONUS = { easy: 0, normal: 100, hard: 200 };

export function victoryScore({ won, points, turns, difficulty }) {
  const base = points * 10 + Math.max(0, 60 - turns) * 5 + (DIFF_BONUS[difficulty] ?? 0);
  return won ? 1000 + base : base;
}

export function loadRecords(storage) {
  const o = readJSON(storage, RECORDS_KEY);
  if (!isObj(o)) return { v: 1, best: 0, games: 0, wins: 0, history: [] };
  return {
    v: 1,
    best: typeof o.best === 'number' ? o.best : 0,
    games: typeof o.games === 'number' ? o.games : 0,
    wins: typeof o.wins === 'number' ? o.wins : 0,
    history: Array.isArray(o.history) ? o.history.slice(-20) : [],
  };
}

export function recordResult(storage, result, now = Date.now()) {
  const r = loadRecords(storage);
  const score = victoryScore(result);
  r.games += 1;
  if (result.won) r.wins += 1;
  r.best = Math.max(r.best, score);
  r.history.push({ score, ...result, date: now });
  r.history = r.history.slice(-20);
  writeJSON(storage, RECORDS_KEY, r);
  return { score, isBest: score >= r.best && score > 0 };
}

// ---------- Challenges ----------
// { v:1, completed: { [id]: timestamp } }

export const CHAL_KEY = 'ohsp-chal-v1';

export function loadChal(storage) {
  const o = readJSON(storage, CHAL_KEY);
  if (!isObj(o) || !isObj(o.completed)) return { v: 1, completed: {} };
  return { v: 1, completed: o.completed };
}

export function completeChal(storage, id, now = Date.now()) {
  const c = loadChal(storage);
  if (!c.completed[id]) {
    c.completed[id] = now;
    writeJSON(storage, CHAL_KEY, c);
    return true;
  }
  return false;
}

// ---------- Profile (ranked / season / normal stats) ----------
// Schema follows modes-ranked 7.1 (flattened internal form). Stage 1: client-recorded, official:false.
// { v:1, uid, level, social,
//   ranked: { ...rating.newRanked(), queueBanUntil, leaveLog:[ms], official:false },
//   season: { seasonId:'S0', startedAt, bestRating, bestTierId },
//   seasonHistory: [], normal: { games, wins }, matches: [last 20 match results] }

const newUid = () => {
  try { return 'u' + [...crypto.getRandomValues(new Uint8Array(8))].map((b) => b.toString(16).padStart(2, '0')).join(''); } catch { return 'u' + Date.now().toString(16); }
};

function emptyProfile(now = Date.now()) {
  return {
    v: 1,
    uid: newUid(),
    level: 1, // TODO: no account-level system yet; used only by the (default off) ranked unlock gate
    social: false, // TODO: social login not implemented
    ranked: { ...newRanked(), queueBanUntil: null, leaveLog: [], official: RANKED.official },
    season: { seasonId: RANKED.seasonId, startedAt: now, bestRating: 1000, bestTierId: null },
    seasonHistory: [],
    normal: { games: 0, wins: 0 },
    matches: [],
  };
}

export function loadProfile(storage) {
  const p = readJSON(storage, PROFILE_KEY);
  const base = emptyProfile();
  if (!isObj(p) || p.v !== 1 || !isObj(p.ranked) || !isObj(p.ranked.placement)) return base;
  const r = p.ranked;
  const num = (x, d) => (Number.isFinite(x) ? x : d);
  const done = !!r.placement.done;
  const ranked = {
    ...base.ranked,
    rating: Math.max(0, num(r.rating, 1000)),
    placement: { done, gamesPlayed: Math.max(0, num(r.placement.gamesPlayed, 0) | 0), gamesRequired: 5 },
    tierIndex: done && Number.isInteger(r.tierIndex) && r.tierIndex >= 0 && r.tierIndex <= 17 ? r.tierIndex : null,
    shieldGamesLeft: Math.max(0, num(r.shieldGamesLeft, 0) | 0),
    gamesTotal: Math.max(0, num(r.gamesTotal, 0) | 0),
    wins: Math.max(0, num(r.wins, 0) | 0),
    top2: Math.max(0, num(r.top2, 0) | 0),
    bestRating: num(r.bestRating, 1000),
    bestTierIndex: Number.isInteger(r.bestTierIndex) ? r.bestTierIndex : null,
    queueBanUntil: num(r.queueBanUntil, null),
    leaveLog: Array.isArray(r.leaveLog) ? r.leaveLog.filter(Number.isFinite).slice(-10) : [],
    official: false, // stage 1: never official, whatever is stored
  };
  if (done && ranked.tierIndex === null) ranked.placement.done = false;
  return {
    ...base,
    uid: typeof p.uid === 'string' ? p.uid : base.uid,
    level: Math.max(1, num(p.level, 1) | 0),
    social: !!p.social,
    ranked,
    season: isObj(p.season) ? { seasonId: String(p.season.seasonId || RANKED.seasonId), startedAt: num(p.season.startedAt, base.season.startedAt), bestRating: num(p.season.bestRating, 1000), bestTierId: typeof p.season.bestTierId === 'string' ? p.season.bestTierId : null } : base.season,
    seasonHistory: Array.isArray(p.seasonHistory) ? p.seasonHistory.slice(-20) : [],
    normal: isObj(p.normal) ? { games: Math.max(0, num(p.normal.games, 0) | 0), wins: Math.max(0, num(p.normal.wins, 0) | 0) } : base.normal,
    matches: Array.isArray(p.matches) ? p.matches.slice(-20) : [],
  };
}

export function saveProfile(storage, profile) { return writeJSON(storage, PROFILE_KEY, profile); }

function syncSeason(p) {
  const r = p.ranked;
  p.season.bestRating = Math.max(p.season.bestRating, r.bestRating);
  if (r.bestTierIndex !== null) p.season.bestTierId = TIERS[r.bestTierIndex].id;
}

/** Normal / friend-room finished game (bots allowed, no rating change). */
export function recordNormalGame(storage, won) {
  const p = loadProfile(storage);
  p.normal.games += 1;
  if (won) p.normal.wins += 1;
  saveProfile(storage, p);
  return p;
}

/**
 * Finished ranked match. `delta` computed by the caller via rating.resolveMatch.
 * match = { matchId, seed, playerCount, rank, points, delta, ratingBefore, sim, players:[{name,rank,points,isBot}] }
 * Returns { profile, change } (change from rating.applyRankedResult).
 */
export function recordRankedMatch(storage, match, now = Date.now()) {
  const p = loadProfile(storage);
  const { ranked, change } = applyRankedResult(p.ranked, { delta: match.delta, rank: match.rank });
  p.ranked = { ...p.ranked, ...ranked };
  syncSeason(p);
  p.matches.push({
    matchId: match.matchId, mode: 'ranked', playerCount: match.playerCount, seasonId: p.season.seasonId, seed: match.seed,
    endedAt: now, official: false, voided: false, sim: !!match.sim,
    // TODO: stage-1 consensus record (all uids + action log) is not stored; only the local result.
    players: match.players, rank: match.rank, ratingBefore: match.ratingBefore, ratingAfter: ranked.rating, delta: match.delta,
  });
  p.matches = p.matches.slice(-20);
  saveProfile(storage, p);
  return { profile: p, change };
}

/** Leaving a ranked match. voided = left before round 3 ended (no game counted, flat -15). */
export function recordRankedLeave(storage, { voided, delta, rank, matchId, seed, playerCount, ratingBefore, sim = false }, now = Date.now()) {
  const p = loadProfile(storage);
  let change = null;
  if (voided) {
    p.ranked = { ...p.ranked, ...applyVoidPenalty(p.ranked, delta) };
  } else {
    const o = applyRankedResult(p.ranked, { delta, rank });
    p.ranked = { ...p.ranked, ...o.ranked };
    change = o.change;
  }
  p.ranked.queueBanUntil = leaveQueueBan(p.ranked.leaveLog, now, voided) ?? p.ranked.queueBanUntil;
  p.ranked.leaveLog = [...p.ranked.leaveLog, now].slice(-10);
  syncSeason(p);
  p.matches.push({ matchId, mode: 'ranked', playerCount, seasonId: p.season.seasonId, seed, endedAt: now, official: false, voided, voidReason: voided ? 'early_leave' : null, left: true, sim, rank, ratingBefore, ratingAfter: p.ranked.rating, delta });
  p.matches = p.matches.slice(-20);
  saveProfile(storage, p);
  return { profile: p, change };
}

export const rankedDisplay = (profile) => displayOf(profile.ranked);

// ---------- Inventory / equipped (cosmetics) ----------

export function loadInventory(storage) {
  return sanitizeInventory(readJSON(storage, INV_KEY), 0);
}

export function saveInventory(storage, inv) { return writeJSON(storage, INV_KEY, inv); }

export function claimFreeItem(storage, itemId, now = Date.now()) {
  const r = claimItem(loadInventory(storage), itemId, now);
  if (r.ok) saveInventory(storage, r.inv);
  return r;
}

export function equipOwnedItem(storage, itemId) {
  const r = equipItem(loadInventory(storage), itemId);
  if (r.ok) saveInventory(storage, r.inv);
  return r;
}

export { newInventory };
