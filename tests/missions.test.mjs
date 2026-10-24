// node tests/missions.test.mjs -- 오늘의 과제: 진행 누적, 날짜 초기화, 보상 지급(중복 불가)
import assert from 'node:assert/strict';
import { loadMissions, recordGameForMissions, missionRows, claimMission } from '../src/meta/missions.js?v=1792846825';
import { loadInventory } from '../src/storage/store.js?v=1792846825';
let pass = 0;
const t = (n, f) => { try { f(); pass++; console.log('ok   ' + n); } catch (e) { console.log('FAIL ' + n + '\n     ' + e.message); process.exitCode = 1; } };
const mem = () => { const m = new Map(); return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) }; };
const d1 = new Date(2026, 9, 24, 10), d2 = new Date(2026, 9, 25, 1);
t('progress accumulates across games and caps in rows', () => {
  const s = mem();
  recordGameForMissions(s, { won: false, recruited: 5, evolved: 1 }, d1);
  recordGameForMissions(s, { won: true, recruited: 6, evolved: 0 }, d1);
  const rows = Object.fromEntries(missionRows(loadMissions(s, d1)).map((r) => [r.id, r]));
  assert.equal(rows.play1.cur, 1); assert.equal(rows.play1.done, true);
  assert.equal(rows.recruit8.cur, 8); assert.equal(rows.recruit8.claimable, true);
  assert.equal(rows.evolve2.cur, 1); assert.equal(rows.evolve2.claimable, false);
  assert.equal(rows.win1.claimable, true);
});
t('claim pays yeopjeon once; unfinished mission cannot be claimed', () => {
  const s = mem();
  recordGameForMissions(s, { won: true, recruited: 2, evolved: 0 }, d1);
  assert.equal(claimMission(s, 'win1', d1).ok, true);
  assert.equal(loadInventory(s).wallet.yeopjeon, 50);
  assert.equal(claimMission(s, 'win1', d1).ok, false, 'no double claim');
  assert.equal(claimMission(s, 'recruit8', d1).ok, false, 'not finished');
  assert.equal(loadInventory(s).wallet.yeopjeon, 50);
});
t('a new day resets progress and claims', () => {
  const s = mem();
  recordGameForMissions(s, { won: true, recruited: 9, evolved: 2 }, d1);
  claimMission(s, 'play1', d1);
  const m = loadMissions(s, d2);
  assert.deepEqual(m.prog, {}); assert.deepEqual(m.claimed, []);
});
console.log(`\n${pass} passed`);
