// Feature flags / constants for the meta layer (ranked mode, shop). Code constants, not UI settings.

// Ranked unlock gate (modes-ranked 1.2). Development default: NOT enforced so the screens can be tried.
// Flip RANKED_UNLOCK.enforce to true (or open the page with ?lock=1) to apply the real conditions.
// NOTE: there is no account-level / social-login system yet, so with enforce=true nobody can unlock.
export const RANKED_UNLOCK = {
  enforce: false,
  minLevel: 10,
  minNormalGames: 10,
  requireSocial: true,
};

export const RANKED = {
  playerCount: 4, // fixed. Ops flag for 3 players is a modes-ranked 1.2.2 open question (Q1); not exposed here.
  turnLimitMs: 25000,
  seasonId: 'S0',
  official: false, // stage 1: client-recorded trial season. Server authority (D8) must exist before this is true.
};

export const SEASON_LABEL = '시범 시즌 0 · 비공식';

/**
 * Ranked unlock check (modes-ranked 1.2 / R-06). Pure.
 * profile: { level, social, normal:{games} }. When `enforce` is false everything counts as unlocked
 * but the item list is still returned so the UI can show progress.
 */
export function rankedUnlockStatus(profile, enforce = RANKED_UNLOCK.enforce) {
  const items = [
    { id: 'level', label: '계정 레벨', cur: profile.level, need: RANKED_UNLOCK.minLevel, ok: profile.level >= RANKED_UNLOCK.minLevel },
    { id: 'normal', label: '일반전 완주', cur: profile.normal.games, need: RANKED_UNLOCK.minNormalGames, ok: profile.normal.games >= RANKED_UNLOCK.minNormalGames },
    { id: 'social', label: '소셜 로그인 연동', cur: profile.social ? 1 : 0, need: 1, ok: !RANKED_UNLOCK.requireSocial || !!profile.social, bool: true },
  ];
  const met = items.every((i) => i.ok);
  return { unlocked: enforce ? met : true, met, enforced: !!enforce, items };
}
