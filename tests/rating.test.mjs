// node tests/rating.test.mjs  -- rating / tier / placement / leave tests (modes-ranked 7.3: R-01..R-04, R-07..R-10, R-14)
import assert from 'node:assert/strict';
import {
  calcRatingDelta, rpToTier, TIERS, kFactor, applyLeavers, resolveMatch, isEarlyLeave, leaveQueueBan,
  seasonResetRating, newRanked, applyRankedResult, applyVoidPenalty, displayOf,
} from '../src/meta/rating.js';

let pass = 0;
const t = (name, fn) => { try { fn(); pass++; console.log('ok   ' + name); } catch (e) { console.log('FAIL ' + name + '\n     ' + e.message); process.exitCode = 1; } };
const sum = (a) => a.reduce((x, y) => x + y, 0);

// ----- R-01 / R-02 / R-03 / R-04 -----
t('R-01 four equal 1500 (K=64): +32/+11/-11/-32', () => {
  assert.deepEqual(calcRatingDelta([1500, 1500, 1500, 1500], [1, 2, 3, 4], [10, 10, 10, 10]), [32, 11, -11, -32]);
});
t('R-02 example 2: B +32, A -9, D +9, C -32', () => {
  // order A,B,C,D ; ranks: B1 A2 D3 C4 ; A=1700 K=64 (below 정3품)
  const d = calcRatingDelta([1700, 1500, 1500, 1300], [2, 1, 4, 3], [10, 10, 10, 10]);
  assert.deepEqual(d, [-9, 32, -32, 9]);
  assert.equal(sum(d), 0);
});
t('example 3 tie for 1st: both +21, 3rd -11, 4th -32, sum -1', () => {
  const d = calcRatingDelta([1500, 1500, 1500, 1500], [1, 1, 3, 4], [10, 10, 10, 10]);
  assert.deepEqual(d, [21, 21, -11, -32]);
  assert.equal(sum(d), -1);
});
t('R-04 tie gives identical deltas for equal ratings', () => {
  const d = calcRatingDelta([1400, 1400, 1600, 1200], [2, 2, 1, 4], [40, 40, 40, 40]);
  assert.equal(d[0], d[1]);
});
t('R-03 |sum| <= N over 5000 random matches (N=2,3,4, ties; same K for all seats)', () => {
  let seed = 12345;
  const rnd = () => (seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0) / 4294967296;
  for (let m = 0; m < 5000; m++) {
    const n = 2 + Math.floor(rnd() * 3);
    // Equal K for every seat: ratings < 1900 and one shared games bucket. (Mixed K seats are NOT zero-sum by design.)
    const ratings = Array.from({ length: n }, () => Math.floor(rnd() * 1900));
    const ranks = Array.from({ length: n }, () => 1 + Math.floor(rnd() * n));
    const g = Math.floor(rnd() * 60);
    const gp = Array(n).fill(g);
    const d = calcRatingDelta(ratings, ranks, gp);
    assert.ok(Math.abs(sum(d)) <= n, `sum ${sum(d)} for ${JSON.stringify({ ratings, ranks, gp })}`);
    assert.ok(d.every(Number.isInteger));
  }
});
t('zero-sum is exact when all K equal and no rounding (symmetrical pair, N=2)', () => {
  assert.deepEqual(calcRatingDelta([1500, 1500], [1, 2], [10, 10]), [32, -32]);
});
t('rank order is monotonic for equal ratings', () => {
  const d = calcRatingDelta([1500, 1500, 1500, 1500], [1, 2, 3, 4], [10, 10, 10, 10]);
  for (let i = 1; i < d.length; i++) assert.ok(d[i - 1] > d[i]);
});
t('weak winner gains more than strong winner', () => {
  const weak = calcRatingDelta([1000, 1800, 1800, 1800], [1, 2, 3, 4], [40, 40, 40, 40])[0];
  const strong = calcRatingDelta([1800, 1000, 1000, 1000], [1, 2, 3, 4], [40, 40, 40, 40])[0];
  assert.ok(weak > strong);
});
t('bad input throws', () => {
  assert.throws(() => calcRatingDelta([1500], [1], [0]));
  assert.throws(() => calcRatingDelta([1500, 1500], [1], [0, 0]));
});
t('optional min gain/loss floors', () => {
  const d = calcRatingDelta([2400, 600, 600, 600], [1, 2, 3, 4], [40, 40, 40, 40], { minGain: 8, minLoss: 8 });
  assert.ok(d[0] >= 8 && d[3] <= -8);
});

// ----- K factor -----
t('K: placement 96, 6-30 games 64, 31+ 48, 정3품+ 40', () => {
  assert.equal(kFactor(1000, 0), 96);
  assert.equal(kFactor(1000, 4), 96);
  assert.equal(kFactor(1000, 5), 64);
  assert.equal(kFactor(1000, 29), 64);
  assert.equal(kFactor(1000, 30), 48);
  assert.equal(kFactor(1899, 50), 48);
  assert.equal(kFactor(1900, 50), 40);
  assert.equal(kFactor(1900, 2), 96);
});

// ----- tiers -----
t('tier table: 20 entries, ids ordered, last two inactive', () => {
  assert.equal(TIERS.length, 20);
  assert.equal(TIERS[0].id, 't_jong9');
  assert.equal(TIERS[17].id, 't_jeong1');
  assert.equal(TIERS[18].id, 't_yeongui');
  assert.equal(TIERS[19].id, 't_king');
  assert.equal(TIERS.filter((x) => x.active).length, 18);
});
t('rpToTier boundaries', () => {
  const id = (rp) => rpToTier(rp).id;
  assert.equal(id(0), 't_jong9');
  assert.equal(id(699), 't_jong9');
  assert.equal(id(700), 't_jeong9');
  assert.equal(id(799), 't_jeong9');
  assert.equal(id(800), 't_jong8');
  assert.equal(id(1000), 't_jong7');
  assert.equal(id(1499), 't_jong5');
  assert.equal(id(1500), 't_jeong5');
  assert.equal(id(1900), 't_jeong3');
  assert.equal(id(2299), 't_jong1');
  assert.equal(id(2300), 't_jeong1');
  assert.equal(id(9999), 't_jeong1'); // 영의정/임금 never returned in stage 1
  assert.equal(id(-5), 't_jong9');
  assert.equal(id(NaN), 't_jong9');
});
t('R-14 season reset: 2200->1600, 1000->1000, 800->900, 0->500', () => {
  assert.equal(seasonResetRating(2200), 1600);
  assert.equal(seasonResetRating(1000), 1000);
  assert.equal(seasonResetRating(800), 900);
  assert.equal(seasonResetRating(0), 500);
  assert.equal(seasonResetRating(1001), 1001); // 1000.5 -> 1001
});

// ----- placement (R-07) -----
const play = (r, delta, rank = 1) => applyRankedResult(r, { delta, rank });
t('R-07 placement: tier hidden for 5 games, start tier clamped to 1499 (종5품)', () => {
  let r = newRanked();
  for (let i = 0; i < 4; i++) {
    const o = play(r, 120);
    r = o.ranked;
    assert.equal(displayOf(r).placing, true);
    assert.equal(r.tierIndex, null);
  }
  const last = play(r, 120);
  assert.equal(last.change.placementDone, true);
  assert.equal(last.ranked.rating, 1499); // 1000 + 5*120 = 1600 clamped
  assert.equal(TIERS[last.ranked.tierIndex].id, 't_jong5');
  assert.equal(last.ranked.placement.done, true);
});
t('placement all losses: rating floors at 0, tier 종9품', () => {
  let r = newRanked();
  for (let i = 0; i < 5; i++) r = play(r, -250, 4).ranked;
  assert.equal(r.rating, 0);
  assert.equal(r.tierIndex, 0);
});
t('placement does not demote/promote during games (no tier)', () => {
  const o = play(newRanked(), 50);
  assert.equal(o.change.promoted, false);
  assert.equal(o.change.demoted, false);
  assert.equal(o.change.wasPlacing, true);
});

// helper: a placed player at given rating/tier
const placed = (rating, shield = 0) => {
  const r = newRanked();
  r.placement = { done: true, gamesPlayed: 5, gamesRequired: 5 };
  r.rating = rating;
  r.tierIndex = rpToTier(rating).index;
  r.gamesTotal = 10;
  r.shieldGamesLeft = shield;
  return r;
};

t('promotion on crossing a floor, sets shield 3', () => {
  const o = play(placed(1090), 20);
  assert.equal(o.change.promoted, true);
  assert.equal(TIERS[o.ranked.tierIndex].id, 't_jeong7');
  assert.equal(o.ranked.shieldGamesLeft, 3);
});
t('R-08 no demotion for 3 games after promotion, display RP pinned to floor', () => {
  let r = play(placed(1090), 20).ranked; // now 1110 jeong7, shield 3
  for (let i = 0; i < 3; i++) {
    const o = play(r, -40, 4);
    r = o.ranked;
    assert.equal(TIERS[r.tierIndex].id, 't_jeong7', `game ${i + 1}`);
    assert.ok(r.rating < 1100 || i === 0);
    assert.ok(displayOf(r).rp >= 1100);
  }
  assert.equal(r.shieldGamesLeft, 0);
  const o4 = play(r, -5, 4); // 4th game: internal rating still below floor -> demote
  assert.equal(o4.change.demoted, true);
  assert.equal(o4.ranked.tierIndex, rpToTier(o4.ranked.rating).index); // jeong7 -> same-grade/lower: no buffer, lands on true band
});
t('shield ends and rating recovered -> stays', () => {
  let r = play(placed(1090), 20).ranked;
  r = play(r, -40, 4).ranked; // 1070
  r = play(r, 30, 1).ranked; // 1100
  r = play(r, 10, 1).ranked; // 1110
  const o = play(r, 10, 1);
  assert.equal(TIERS[o.ranked.tierIndex].id, 't_jeong7');
  assert.equal(o.change.demoted, false);
});
t('grade-boundary buffer: 종7품 holds down to 950, demotes below', () => {
  // 종7품 floor 1000; dropping into 정8품 band (900s) needs rating < 950
  const hold = play(placed(1010), -55, 4); // 955
  assert.equal(hold.change.demoted, false);
  assert.equal(TIERS[hold.ranked.tierIndex].id, 't_jong7');
  assert.equal(displayOf(hold.ranked).rp, 1000);
  const drop = play(placed(1010), -61, 4); // 949
  assert.equal(drop.change.demoted, true);
  assert.equal(TIERS[drop.ranked.tierIndex].id, 't_jeong8');
});
t('same-grade 정 -> 종 has no buffer', () => {
  const o = play(placed(1105), -10, 4); // 1095 < 1100
  assert.equal(o.change.demoted, true);
  assert.equal(TIERS[o.ranked.tierIndex].id, 't_jong7');
});
t('종9품 never demoted, rating floor 0', () => {
  const o = play(placed(20), -64, 4);
  assert.equal(o.ranked.rating, 0);
  assert.equal(o.ranked.tierIndex, 0);
  assert.equal(o.change.demoted, false);
});
t('top tier capped at 정1품 (no 영의정/임금 in stage 1)', () => {
  const o = play(placed(2390), 40, 1);
  assert.equal(TIERS[o.ranked.tierIndex].id, 't_jeong1');
});
t('stats: wins / top2 / gamesTotal / best', () => {
  let r = placed(1500);
  r = play(r, 30, 1).ranked;
  r = play(r, 5, 2).ranked;
  r = play(r, -20, 3).ranked;
  assert.equal(r.gamesTotal, 13);
  assert.equal(r.wins, 1);
  assert.equal(r.top2, 2);
  assert.equal(r.bestRating, 1535);
});
t('applyRankedResult does not mutate input', () => {
  const r = placed(1500);
  const snap = JSON.stringify(r);
  play(r, 30, 1);
  assert.equal(JSON.stringify(r), snap);
});

// ----- leave handling (R-09 / R-10) -----
t('applyLeavers: single leaver is always last, stayers keep order', () => {
  assert.deepEqual(applyLeavers([1, 2, 3, 4], [null, null, null, 5]), [1, 2, 3, 4]);
  assert.deepEqual(applyLeavers([1, 2, 3, 4], [5, null, null, null]), [4, 1, 2, 3]); // winner left
});
t('applyLeavers: two leavers, later leaver ranks higher; same time ties', () => {
  assert.deepEqual(applyLeavers([1, 2, 3, 4], [10, 20, null, null]), [4, 3, 1, 2]);
  assert.deepEqual(applyLeavers([1, 2, 3, 4], [10, 10, null, null]), [3, 3, 1, 2]);
});
t('R-09 leaver is last and takes extra -10', () => {
  const base = calcRatingDelta([1500, 1500, 1500, 1500], [1, 2, 3, 4], [10, 10, 10, 10]);
  const res = resolveMatch({ ratings: [1500, 1500, 1500, 1500], ranks: [4, 1, 2, 3], gamesPlayed: [10, 10, 10, 10], leftAt: [99, null, null, null] });
  assert.equal(res.voided, false);
  assert.equal(res.ranks[0], 4);
  assert.equal(res.deltas[0], base[3] - 10);
  assert.deepEqual(res.deltas.slice(1), [32, 11, -11]);
});
t('R-10 early leave voids the match: stayers 0, leaver -15', () => {
  assert.equal(isEarlyLeave(11, 4), true); // turn 11 of 4 players = still in round 3
  assert.equal(isEarlyLeave(12, 4), false);
  const res = resolveMatch({ ratings: [1500, 1500, 1500, 1500], ranks: [1, 2, 3, 4], gamesPlayed: [10, 10, 10, 10], leftAt: [null, null, 3, null], early: true });
  assert.equal(res.voided, true);
  assert.deepEqual(res.deltas, [0, 0, -15, 0]);
});
t('void penalty keeps game count and tier', () => {
  const r = applyVoidPenalty(placed(1500), -15);
  assert.equal(r.rating, 1485);
  assert.equal(r.gamesTotal, 10);
});
t('no leavers -> resolveMatch equals calcRatingDelta', () => {
  const a = resolveMatch({ ratings: [1500, 1500, 1500, 1500], ranks: [1, 2, 3, 4], gamesPlayed: [10, 10, 10, 10] });
  assert.deepEqual(a.deltas, [32, 11, -11, -32]);
});
t('queue ban: void 10 min; 3 leaves in 7 days 24h', () => {
  const now = 1_000_000_000_000;
  assert.equal(leaveQueueBan([], now, true), now + 600000);
  assert.equal(leaveQueueBan([], now, false), null);
  assert.equal(leaveQueueBan([now - 1000, now - 2000], now, false), now + 86400000);
  assert.equal(leaveQueueBan([now - 8 * 86400000, now - 9 * 86400000], now, false), null);
});

console.log(`\n${pass} passed${process.exitCode ? ', with FAILURES' : ''}`);
