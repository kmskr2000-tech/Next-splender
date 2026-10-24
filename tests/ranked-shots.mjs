// Playwright smoke + screenshots for ranked / shop / cosmetics.
// usage: node tests/ranked-shots.mjs   (serves the repo on :8123; needs playwright + chromium)
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
const require = createRequire('/opt/node-tools/node_modules/');
const { chromium } = require('playwright');

const PORT = 8123;
const OUT = new URL('../docs/qa/', import.meta.url).pathname;
const ROOT = new URL('../', import.meta.url).pathname;
const BASE = `http://127.0.0.1:${PORT}/index.html`;
const srv = spawn('/opt/node-tools/node_modules/.bin/http-server', [ROOT, '-p', String(PORT), '-c-1', '-s'], { stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 1200));

const errors = [];
const browser = await chromium.launch({ executablePath: process.env.CHROME || undefined });
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, locale: 'ko-KR' });
const page = await ctx.newPage();
page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
page.on('console', (m) => { if (m.type() === 'error' && !/firebase|gstatic|ERR_|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
const shot = (name) => page.screenshot({ path: `${OUT}ranked-${name}.png` });
const click = (sel) => page.click(sel);
const wait = (ms) => page.waitForTimeout(ms);
let checks = 0;
const ok = (cond, msg) => { checks++; if (!cond) { errors.push('check failed: ' + msg); } };

// play the human seat with the AI heuristic until the game ends
async function playOut() {
  await page.evaluate(async () => {
    const { chooseAction } = await import('/src/ai/heuristic.js?v=' + window.__V);
    const c = window.__ctrl;
    for (let i = 0; i < 3000 && !c.finished; i++) {
      if (c.game.players[c.game.current].isAI && c.game.current !== c.human) c.stepAI(Math.random);
      else c.dispatch(chooseAction(c.game, Math.random, 'hard', 'balanced'));
    }
    window.__render();
  });
}
// 로비 v3: 모드는 모드 선택 시트에서 고른다 (가운데 모드 카드는 떠다니는 애니메이션이라 force 클릭)
async function setMode(m, keepOpen = false) {
  await page.click('.mode-card', { force: true });
  await page.waitForSelector('.mode-opt');
  await page.click(`.mode-opt[data-mode="${m}"]`);
  if (!keepOpen) await page.click('[data-action="mode-close"]');
  await page.waitForTimeout(120);
}
async function startRankedGame() {
  await setMode('ranked');
  await click('[data-action="match"]');
  await page.waitForSelector('#header .topbar', { timeout: 15000 });
}

// 1. home, normal tab
await page.goto(BASE + '?sim=1&fast=1');
// 0. first visit: nickname prompt blocks the home until a name is saved
await page.waitForSelector('#profname');
ok((await page.textContent('.overlay .panel .title')).includes('어서 오세요'), 'first-run nickname prompt');
await shot('0-first-nickname');
await click('[data-action="profile-save"]');
ok((await page.textContent('.overlay:not(.home) .panel, .overlay .panel')).includes('닉네임을 입력해 주세요'), 'empty nickname rejected');
await page.fill('#profname', '테스터');
await page.press('#profname', 'Enter');
await page.waitForSelector('.home');
await wait(300);
await shot('1-home-normal');
ok(await page.locator('.lobby-v3 .mode-card').count() === 1, 'lobby v3 mode card');
await page.click('.mode-card', { force: true }); await page.waitForSelector('.mode-opt');
ok(await page.locator('.mode-opt').count() === 3, 'three modes (normal / ranked / friendly)');
await page.click('[data-action="mode-close"]');
ok(await page.locator('[data-action="room-join"]').count() === 0, 'join-by-code removed');

// 1b. friendly lobby (sim shows sample rooms)
await setMode('friendly');
await click('.cta-main[data-action="rooms-open"]');
await wait(200);
await shot('1b-home-friendly');
ok((await page.textContent('.nonrank')).includes('랭크 점수 변동 없음'), 'friendly labelled non-ranked');
ok(await page.locator('.lobby-room').count() === 3, 'lobby lists rooms');
ok(await page.locator('.lobby-room .lr-lock').count() === 1, 'locked room shows lock');
ok(await page.locator('.lobby-room.full[disabled]').count() === 1, 'full room disabled');
await click('.lobby-room:has(.lr-lock)');
await page.waitForSelector('#lobbypwin');
await page.fill('#lobbypwin', 'wrong');
await page.press('#lobbypwin', 'Enter');
await wait(200);
ok((await page.textContent('.overlay:not(.home) .panel, .overlay .panel')).includes('비밀번호가 맞지 않아요'), 'wrong password rejected');
await shot('1c-lobby-password');
await click('[data-action="lobby-pw-close"]');
await click('[data-action="lobby-create"]');
await page.waitForSelector('#lobbytitle');
await shot('1d-lobby-create');
await click('[data-action="lobby-create-close"]');
await click('[data-action="rooms-close"]');
await setMode('normal');

// 2. ranked tab
await setMode('ranked', true);
await wait(200);
await shot('2-home-ranked');
ok((await page.textContent('.rk-card')).includes('시범 시즌 0 · 비공식'), 'season label on ranked card');
ok((await page.textContent('.rk-card')).includes('봇 채움 없음'), 'no bot fill text');
await click('[data-action="mode-close"]');
ok(await page.locator('.bigstart.ranked:not([disabled])').count() === 1, 'ranked start enabled by default flag');

// 3. queue (2 of 4 seats filled, no bots)
await click('[data-action="match"]');
// sim users join on the 500ms tick after SIM_JOIN_MS; wait for one instead of a fixed 700ms (was flaky)
await page.waitForSelector('.queue .botmark.sim', { timeout: 3000 }).catch(() => {});
await shot('3-queue');
ok(await page.locator('.queue .botmark:not(.sim)').count() === 0, 'no BOT marks in ranked queue');
ok(await page.locator('.queue .botmark.sim').count() >= 1, 'sim user label present');
ok(await page.locator('.slot').count() === 4, '4 slots');

// cancel works
await click('[data-action="queue-cancel"]');
await page.waitForSelector('.home');

// 4. full game 1 (placement) -> result without RP numbers
await startRankedGame();
ok(await page.evaluate(() => window.__ctrl.game.players.length === 4), 'ranked game has 4 players');
ok(await page.locator('#rail .botmark:not(.sim)').count() === 0, 'rail has no BOT marks in ranked sim');
await playOut();
await page.waitForSelector('.result .rpblock');
await wait(1000);
await shot('4-result-placement');
ok((await page.textContent('.rpblock')).includes('배치고사 1/5'), 'placement progress shown');
let prof = await page.evaluate(() => JSON.parse(localStorage.getItem('ohsp-profile-v1')));
ok(prof.ranked.placement.gamesPlayed === 1 && prof.ranked.official === false, 'profile placement=1, unofficial');
await click('[data-action="restart"]');
await page.waitForSelector('.home');

// 5. seeded placed profile -> result with RP numbers / bar / promo. Retry seeds until the human finishes top 2.
let got = false;
for (const seed of [11, 12, 13, 14, 15, 16, 17, 18]) {
  await page.goto(BASE + `?sim=1&fast=1&seed=${seed}`);
  await page.evaluate(() => {
    const p = JSON.parse(localStorage.getItem('ohsp-profile-v1'));
    Object.assign(p.ranked, { rating: 1490, gamesTotal: 12, tierIndex: 8, shieldGamesLeft: 0, wins: 4, top2: 7, bestRating: 1490, bestTierIndex: 8 });
    p.ranked.placement = { done: true, gamesPlayed: 5, gamesRequired: 5 };
    localStorage.setItem('ohsp-profile-v1', JSON.stringify(p));
  });
  await page.reload();
  await page.waitForSelector('.home');
  if (seed === 11) { await setMode('ranked'); await wait(150); await shot('2b-home-ranked-tier'); }
  await startRankedGame();
  await playOut();
  await page.waitForSelector('.result .rpblock');
  await wait(1000);
  const txt = await page.textContent('.rpblock');
  const promoted = txt.includes('승급');
  if (promoted || seed === 18) { await shot('5-result-rp'); got = true; ok(txt.includes('RP'), 'RP shown'); ok(await page.locator('.rpbar').count() === 1, 'rp bar'); if (promoted) ok(txt.includes('종5품 → '), 'promotion text'); break; }
}
ok(got, 'rp result screenshot taken');
prof = await page.evaluate(() => JSON.parse(localStorage.getItem('ohsp-profile-v1')));
ok(prof.ranked.gamesTotal === 13, 'game counted in profile');

// 6. leave confirm (ranked in-game) and penalty
await page.goto(BASE + '?sim=1&fast=1');
await page.waitForSelector('.home');
await startRankedGame();
await click('.iconbtn[data-action="options"]');
await click('[data-action="restart"]');
await page.waitForSelector('[data-action="leave-confirm"]');
await shot('8-leave-confirm');
ok((await page.textContent('.panel')).includes('-15 RP'), 'void-leave text early in game');
const before = await page.evaluate(() => JSON.parse(localStorage.getItem('ohsp-profile-v1')).ranked.rating);
await click('[data-action="leave-confirm"]');
await page.waitForSelector('.home');
const after = await page.evaluate(() => JSON.parse(localStorage.getItem('ohsp-profile-v1')).ranked.rating);
ok(before - after === 15, `void leave -15 (was ${before} now ${after})`);
await wait(100);
ok(await page.locator('.lobby-v3').count() === 1, 'home after leave');

// 7. shop
await click('[data-action="shop"]');
await page.waitForSelector('.shoppanel');
await click('[data-action="shop-claim"][data-item="frame_dancheong"]');
await click('[data-action="shop-equip"][data-item="frame_dancheong"]');
await shot('6-shop');
ok(await page.locator('.shopitem .btn[disabled]:has-text("준비 중")').count() >= 1, 'paid item disabled "준비 중"');
ok((await page.textContent('.shoplist')).includes('엽전 150'), 'paid price label');
await click('[data-action="shop-tab"][data-tab="cardFrame"]');
await click('[data-action="shop-claim"][data-item="cf_ink"]');
await click('[data-action="shop-equip"][data-item="cf_ink"]');
await click('[data-action="shop-tab"][data-tab="title"]');
await click('[data-action="shop-claim"][data-item="title_hanyang"]');
await click('[data-action="shop-equip"][data-item="title_hanyang"]');
await shot('6b-shop-title');
await click('[data-action="shop-close"]');
await page.waitForSelector('.home');
await shot('2c-home-equipped');

// 8. equipped cosmetics in-game (normal mode, sim)
await setMode('normal');
await click('[data-action="match"]');
await page.waitForSelector('#header .topbar', { timeout: 20000 });
await page.evaluate(() => {
  const c = window.__ctrl;
  const t = c.game.table;
  const pick = [...(t['1'] || []), ...(t['2'] || [])].filter(Boolean).slice(0, 3);
  c.me.tableau.push(...pick);
  c.me.hand.push(...(t['3'] || []).filter(Boolean).slice(0, 1));
  window.__render();
});
await wait(300);
await shot('7-ingame-equipped-top');
await page.locator('#me').scrollIntoViewIfNeeded();
await wait(200);
await shot('7-ingame-equipped');
ok(await page.locator('.av.fr-dancheong').count() >= 1, 'avatar frame class rendered');
ok(await page.locator('.mp.cf-ink').count() >= 1, 'card frame class rendered on own cards');
ok((await page.textContent('#me')).includes('한양 나그네'), 'title rendered');
// default sprite path fallback (no skin equipped)
ok(await page.locator('.mp img.tiny[src^="assets/creatures/"]').count() >= 1, 'default sprite path');

// 9. lock flag: ?lock=1 shows locked ranked
await page.goto(BASE + '?sim=1&fast=1&lock=1');
await page.waitForSelector('.home');
await setMode('ranked');
await wait(150);
await shot('9-ranked-locked');
ok(await page.locator('.bigstart.ranked[disabled]').count() === 1, 'locked start disabled with lock flag');

await browser.close();
srv.kill();
console.log(`checks: ${checks}, problems: ${errors.length}`);
for (const e of errors) console.log(' - ' + e);
process.exit(errors.length ? 1 : 0);
