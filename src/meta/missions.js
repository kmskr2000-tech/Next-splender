// 오늘의 과제 (D25): 날마다 3개, 완료하면 엽전. 로비 화면의 되돌아올 이유.
// 저장: localStorage 'ohsp-missions-v1' = { day: 'YYYY-MM-DD', prog: { id: n }, claimed: [id] }
// 진행은 판이 끝날 때(모든 모드) recordGameForMissions 로 한 번에 더한다.
import { loadInventory, saveInventory } from '../storage/store.js?v=1792061648';

export const MISSIONS_KEY = 'ohsp-missions-v1';
export const DAILY_MISSIONS = [
  { id: 'play1', label: '대전 1판 끝까지 하기', need: 1, reward: 20, icon: '⚔️' },
  { id: 'recruit8', label: '인물 8명 영입하기', need: 8, reward: 30, icon: '🎴' },
  { id: 'evolve2', label: '인물 2번 성장시키기', need: 2, reward: 30, icon: '✨' },
  { id: 'win1', label: '1번 우승하기', need: 1, reward: 50, icon: '🏆' },
];
const todayKey = (now = new Date()) => `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

function read(storage, key) { try { const r = storage?.getItem(key); return r ? JSON.parse(r) : null; } catch { return null; } }
function write(storage, key, v) { try { storage.setItem(key, JSON.stringify(v)); } catch { /* 저장 불가 */ } }

/** Today's state; a new day resets progress (returns a fresh object, saved). */
export function loadMissions(storage, now = new Date()) {
  const day = todayKey(now);
  const raw = read(storage, MISSIONS_KEY);
  if (raw && raw.day === day && raw.prog && Array.isArray(raw.claimed)) return raw;
  const fresh = { day, prog: {}, claimed: [] };
  write(storage, MISSIONS_KEY, fresh);
  return fresh;
}

/** Add one finished game. counts = { won, recruited, evolved } */
export function recordGameForMissions(storage, { won = false, recruited = 0, evolved = 0 } = {}, now = new Date()) {
  const m = loadMissions(storage, now);
  const add = (id, n) => { if (n > 0) m.prog[id] = (m.prog[id] || 0) + n; };
  add('play1', 1); add('recruit8', recruited); add('evolve2', evolved); add('win1', won ? 1 : 0);
  write(storage, MISSIONS_KEY, m);
  return m;
}

/** View rows for the lobby. */
export function missionRows(m) {
  return DAILY_MISSIONS.map((d) => {
    const cur = Math.min(d.need, m.prog[d.id] || 0);
    const claimed = m.claimed.includes(d.id);
    return { ...d, cur, done: cur >= d.need, claimed, claimable: cur >= d.need && !claimed };
  });
}

/** Claim a finished mission: pays yeopjeon into the inventory wallet. Returns { ok, reward }. */
export function claimMission(storage, id, now = new Date()) {
  const m = loadMissions(storage, now);
  const d = DAILY_MISSIONS.find((x) => x.id === id);
  if (!d || m.claimed.includes(id) || (m.prog[id] || 0) < d.need) return { ok: false };
  m.claimed.push(id);
  write(storage, MISSIONS_KEY, m);
  const inv = loadInventory(storage);
  inv.wallet.yeopjeon += d.reward;
  saveInventory(storage, inv);
  return { ok: true, reward: d.reward };
}
