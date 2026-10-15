// Ranked rating, tiers, placement, promotion protection, leave handling. Pure functions, no DOM/storage.
// Spec: docs/design/modes-ranked.md (section numbers in comments). All numbers are provisional ("가안").

export const INITIAL_RATING = 1000;
export const PLACEMENT_GAMES = 5;
export const PLACEMENT_MAX_RATING = 1499; // 3.4: placement alone can reach 종5품 at most
export const SHIELD_GAMES = 3; // 3.3-1
export const BUFFER_RP = 50; // 3.3-2
export const LEAVE_PENALTY = 10; // 5.3-1
export const VOID_LEAVE_PENALTY = 15; // 5.3-3
export const VOID_BEFORE_ROUND = 3; // leave before round 3 has finished voids the match

// ---------- tiers (3.1) ----------
// index 0..17 are pure RP bands; 18/19 (영의정/임금) need a server-verified leaderboard and are inactive in stage 1.
const GRADES = [9, 8, 7, 6, 5, 4, 3, 2, 1];
const BASE = [ // rating floor of each of the 18 pure bands
  0, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300,
];

export const TIERS = [
  ...GRADES.flatMap((g, gi) => [
    { id: `t_jong${g}`, name: `종${g}품`, grade: g, half: 'jong', floor: BASE[gi * 2], active: true },
    { id: `t_jeong${g}`, name: `정${g}품`, grade: g, half: 'jeong', floor: BASE[gi * 2 + 1], active: true },
  ]),
  { id: 't_yeongui', name: '영의정', grade: 0, half: null, floor: 2400, active: false },
  { id: 't_king', name: '임금', grade: 0, half: null, floor: 2400, active: false },
].map((t, i) => ({ ...t, index: i }));

export const MAX_ACTIVE_TIER = 17; // 정1품
export const tierById = (id) => TIERS.find((t) => t.id === id) ?? null;

/** Pure band lookup by rating. Stage 1 never returns 영의정/임금. */
export function rpToTier(rp) {
  const r = Math.max(0, Math.floor(Number.isFinite(rp) ? rp : 0));
  let idx = 0;
  for (let i = 0; i <= MAX_ACTIVE_TIER; i++) if (r >= TIERS[i].floor) idx = i;
  return TIERS[idx];
}

export const tierFloor = (idx) => TIERS[idx].floor;
/** Upper bound (exclusive) of a tier's band; Infinity for the top active tier. */
export const tierCeil = (idx) => (idx >= MAX_ACTIVE_TIER ? Infinity : TIERS[idx + 1].floor);

// ---------- K factor (2.4) ----------
export function kFactor(rating, gamesPlayed) {
  if (gamesPlayed < PLACEMENT_GAMES) return 96;
  if (rating >= tierFloor(13)) return 40; // 정3품 and above
  if (gamesPlayed < 30) return 64; // 6th..30th game
  return 48;
}

// ---------- pairwise Elo (2.3) ----------
/**
 * @param {number[]} ratings    rating before the match, per player
 * @param {number[]} ranks      1 = best; equal values are a shared rank (tie -> s = 0.5)
 * @param {number[]} gamesPlayed ranked games played before this match, per player (picks K)
 * @param {{minGain?:number, minLoss?:number}} [opts] optional floors (2.4, open question Q3). Off by default
 *        because they break the zero-sum invariant.
 * @returns {number[]} integer rating deltas, same order. Sum is 0 up to rounding (|sum| <= N).
 */
export function calcRatingDelta(ratings, ranks, gamesPlayed, opts = {}) {
  const n = ratings.length;
  if (n < 2 || ranks.length !== n || gamesPlayed.length !== n) throw new Error('calcRatingDelta: bad input');
  const deltas = ratings.map((ri, i) => {
    let s = 0;
    let e = 0;
    for (let j = 0; j < n; j++) {
      if (j === i) continue;
      e += 1 / (1 + 10 ** ((ratings[j] - ri) / 400));
      s += ranks[i] < ranks[j] ? 1 : ranks[i] === ranks[j] ? 0.5 : 0;
    }
    const k = kFactor(ri, gamesPlayed[i]);
    const d = Math.round(k * ((s - e) / (n - 1)));
    return d === 0 ? 0 : d; // avoid -0
  });
  const { minGain = 0, minLoss = 0 } = opts;
  if (minGain || minLoss) {
    const best = Math.min(...ranks);
    const worst = Math.max(...ranks);
    return deltas.map((d, i) => {
      if (ranks[i] === best && best !== worst) return Math.max(d, minGain);
      if (ranks[i] === worst && best !== worst) return Math.min(d, -minLoss);
      return d;
    });
  }
  return deltas;
}

// ---------- leave handling (5.3) ----------
/**
 * Re-rank so leavers are always below everyone who stayed.
 * @param {number[]} ranks original ranks (1 = best)
 * @param {(number|null)[]} leftAt per player: null if stayed, else a leave timestamp/turn (later = better rank among leavers)
 * @returns {number[]} new ranks: stayers keep their relative order (dense 1..m, ties kept), leavers follow
 */
export function applyLeavers(ranks, leftAt) {
  const stay = ranks.map((r, i) => ({ r, i })).filter((x) => leftAt[x.i] == null);
  const out = ranks.slice();
  const distinct = [...new Set(stay.map((x) => x.r))].sort((a, b) => a - b);
  for (const x of stay) out[x.i] = distinct.indexOf(x.r) + 1;
  const m = distinct.length;
  const leavers = ranks.map((_, i) => i).filter((i) => leftAt[i] != null);
  const times = [...new Set(leavers.map((i) => leftAt[i]))].sort((a, b) => b - a); // later leave = higher rank
  for (const i of leavers) out[i] = m + times.indexOf(leftAt[i]) + 1;
  return out;
}

/** True when a leave at `turn` (engine turn counter, 0-based) happens before round 3 is finished. */
export const isEarlyLeave = (turn, playerCount) => turn < VOID_BEFORE_ROUND * playerCount;

/**
 * Whole-match resolution including leavers.
 * @param {object} m
 * @param {number[]} m.ratings
 * @param {number[]} m.ranks
 * @param {number[]} m.gamesPlayed
 * @param {(number|null)[]} [m.leftAt]  leave marker per player (null = stayed)
 * @param {boolean} [m.early]           any leave happened before round 3 ended -> match void
 * @returns {{voided:boolean, ranks:number[], deltas:number[], penalties:number[]}}
 *   Void: stayers 0, leavers -15. Otherwise normal Elo on adjusted ranks, leavers additionally -10.
 */
export function resolveMatch({ ratings, ranks, gamesPlayed, leftAt = null, early = false }) {
  const n = ratings.length;
  const left = leftAt ?? Array(n).fill(null);
  const anyLeft = left.some((x) => x != null);
  if (anyLeft && early) {
    const penalties = left.map((x) => (x != null ? -VOID_LEAVE_PENALTY : 0));
    return { voided: true, ranks: ranks.slice(), deltas: penalties.slice(), penalties };
  }
  const adj = anyLeft ? applyLeavers(ranks, left) : ranks.slice();
  const base = calcRatingDelta(ratings, adj, gamesPlayed);
  const penalties = left.map((x) => (x != null ? -LEAVE_PENALTY : 0));
  return { voided: false, ranks: adj, deltas: base.map((d, i) => d + penalties[i]), penalties };
}

/**
 * Queue ban after a leave. `leaveLog` = timestamps (ms) of earlier leaves (7-day rolling, 5.3-4).
 * Returns ban end timestamp or null.
 */
export function leaveQueueBan(leaveLog, now, voided) {
  const DAY = 86400000;
  const recent = leaveLog.filter((t) => now - t < 7 * DAY).length + 1;
  let until = null;
  if (voided) until = now + 10 * 60000;
  if (recent >= 3) until = Math.max(until ?? 0, now + DAY);
  return until;
}

// ---------- season (4.2) ----------
export const seasonResetRating = (old) => Math.max(0, Math.round(INITIAL_RATING + (old - INITIAL_RATING) * 0.5));

// ---------- ranked profile state machine (3.2 - 3.4) ----------
/**
 * Fresh ranked block. `rating` is the hidden internal value; `tierIndex` is null during placement.
 */
export function newRanked() {
  return {
    rating: INITIAL_RATING,
    placement: { done: false, gamesPlayed: 0, gamesRequired: PLACEMENT_GAMES },
    tierIndex: null,
    shieldGamesLeft: 0,
    gamesTotal: 0,
    wins: 0,
    top2: 0,
    bestRating: INITIAL_RATING,
    bestTierIndex: null,
  };
}

export const gamesForK = (r) => r.gamesTotal; // ranked games played so far (placement counted)

/** What the UI shows: null tier while placing; RP never below the current tier floor (shield/buffer). */
export function displayOf(r) {
  if (!r.placement.done) return { placing: true, rp: null, tier: null, progress: r.placement.gamesPlayed, of: r.placement.gamesRequired };
  const tier = TIERS[r.tierIndex];
  const rp = Math.max(r.rating, tier.floor);
  const ceil = tierCeil(r.tierIndex);
  const pct = ceil === Infinity ? 100 : Math.max(0, Math.min(100, ((rp - tier.floor) / (ceil - tier.floor)) * 100));
  return { placing: false, rp, tier, pct, shield: r.shieldGamesLeft };
}

/**
 * Apply one finished (non-void) match to the ranked block.
 * Returns { ranked, change } where change = { before, after, delta, promoted, demoted, placementDone, shielded }.
 * Does not mutate its input.
 */
export function applyRankedResult(prev, { delta, rank }) {
  const r = structuredClone(prev);
  const before = displayOf(prev);
  const wasPlacing = !r.placement.done;
  const raw = r.rating + delta;
  r.rating = Math.max(0, raw);
  r.gamesTotal += 1;
  if (rank === 1) r.wins += 1;
  if (rank <= 2) r.top2 += 1;
  let promoted = false;
  let demoted = false;
  let shielded = false;
  let placementDone = false;

  if (wasPlacing) {
    r.placement.gamesPlayed += 1;
    if (r.placement.gamesPlayed >= r.placement.gamesRequired) {
      r.placement.done = true;
      r.rating = Math.min(r.rating, PLACEMENT_MAX_RATING);
      r.tierIndex = rpToTier(r.rating).index;
      r.shieldGamesLeft = 0;
      placementDone = true;
    }
  } else {
    const cand = rpToTier(r.rating).index;
    if (cand > r.tierIndex) {
      r.tierIndex = cand;
      r.shieldGamesLeft = SHIELD_GAMES;
      promoted = true;
    } else if (r.shieldGamesLeft > 0) {
      r.shieldGamesLeft -= 1; // protected game
      shielded = cand < r.tierIndex;
    } else if (cand < r.tierIndex && r.tierIndex > 0) {
      const crossesGrade = TIERS[r.tierIndex].half === 'jong'; // jong -> (lower grade's) jeong
      const t = TIERS[r.tierIndex];
      if (!(crossesGrade && r.rating >= t.floor - BUFFER_RP)) {
        r.tierIndex = cand;
        demoted = true;
      }
    }
  }

  r.bestRating = Math.max(r.bestRating, r.rating);
  if (r.placement.done) r.bestTierIndex = Math.max(r.bestTierIndex ?? 0, r.tierIndex);
  const after = displayOf(r);
  return { ranked: r, change: { before, after, delta, promoted, demoted, placementDone, shielded, wasPlacing } };
}

/** Apply a void-match leave penalty (leaver only): rating shifts, no game counted, no tier change. */
export function applyVoidPenalty(prev, penalty) {
  const r = structuredClone(prev);
  r.rating = Math.max(0, r.rating - Math.abs(penalty));
  return r;
}
