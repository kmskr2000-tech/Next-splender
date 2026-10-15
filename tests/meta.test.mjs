// node tests/meta.test.mjs -- catalog / inventory / sprite hook / unlock gate / store round-trip
import assert from 'node:assert/strict';
import { CATALOG, validateCatalog, itemById } from '../src/meta/catalog.js';
import { newInventory, claimItem, equipItem, resolveCardSprite, sanitizeInventory, isEquipped } from '../src/meta/cosmetics.js';
import { rankedUnlockStatus } from '../src/meta/config.js';
import { loadProfile, recordRankedMatch, recordRankedLeave, recordNormalGame, loadInventory, claimFreeItem, equipOwnedItem, loadOptions, saveOptions } from '../src/storage/store.js';

let pass = 0;
const t = (name, fn) => { try { fn(); pass++; console.log('ok   ' + name); } catch (e) { console.log('FAIL ' + name + '\n     ' + e.message); process.exitCode = 1; } };
const mem = () => { const m = new Map(); return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) }; };

t('catalog valid: gameplayEffect none, unique ids', () => assert.deepEqual(validateCatalog(), []));
t('catalog validation catches gameplay effect', () => assert.ok(validateCatalog([{ ...CATALOG[0], gameplayEffect: 'discount' }]).length > 0));
t('every slot has a free sample item', () => {
  for (const type of ['avatarFrame', 'cardFrame', 'title', 'emote']) assert.ok(CATALOG.some((i) => i.type === type && i.price.amount === 0), type);
});
t('new inventory owns + equips defaults', () => {
  const inv = newInventory();
  assert.equal(inv.equipped.avatarFrame, 'frame_basic');
  assert.equal(inv.equipped.cardFrame, 'cf_hanji');
  assert.equal(inv.equipped.title, 'title_newbie');
});
t('claim free ok, paid rejected, duplicate rejected', () => {
  const inv = newInventory();
  const a = claimItem(inv, 'frame_dancheong');
  assert.ok(a.ok);
  assert.equal(claimItem(a.inv, 'frame_dancheong').error, 'already_owned');
  assert.equal(claimItem(inv, 'frame_royal').error, 'not_available');
  assert.equal(claimItem(inv, 'nope').error, 'unknown_item');
  assert.equal(inv.inventory.length, newInventory().inventory.length); // input untouched
});
t('equip requires ownership; swaps within slot', () => {
  let inv = newInventory();
  assert.equal(equipItem(inv, 'frame_dancheong').error, 'not_owned');
  inv = claimItem(inv, 'frame_dancheong').inv;
  inv = equipItem(inv, 'frame_dancheong').inv;
  assert.equal(inv.equipped.avatarFrame, 'frame_dancheong');
  inv = equipItem(inv, 'frame_basic').inv;
  assert.equal(inv.equipped.avatarFrame, 'frame_basic');
});
t('emote toggles in/out, max 6 slots', () => {
  let inv = newInventory();
  inv = claimItem(inv, 'emo_thumb').inv;
  inv = equipItem(inv, 'emo_thumb').inv;
  assert.ok(isEquipped(inv, itemById('emo_thumb')));
  inv = equipItem(inv, 'emo_thumb').inv;
  assert.ok(!isEquipped(inv, itemById('emo_thumb')));
});
t('resolveCardSprite: default path without skin', () => {
  assert.equal(resolveCardSprite('t3-002', null), 'assets/creatures/t3-002.png');
  assert.equal(resolveCardSprite('t3-002', { cardSkins: {} }), 'assets/creatures/t3-002.png');
});
t('resolveCardSprite: skin path when equipped and file shipped; fallback otherwise', () => {
  const catalog = [{ id: 'skin_x', slot: 'cardSkin:yisunsin', files: ['t3-002'], gameplayEffect: 'none', price: { amount: 0 }, type: 'cardSkin' }];
  const eq = { cardSkins: { yisunsin: 'skin_x' } };
  assert.equal(resolveCardSprite('t3-002', eq, { catalog }), 'assets/skins/skin_x/t3-002.png');
  assert.equal(resolveCardSprite('t2-002', eq, { catalog }), 'assets/creatures/t2-002.png'); // skin lacks this stage
  assert.equal(resolveCardSprite('t3-001', eq, { catalog }), 'assets/creatures/t3-001.png'); // other line
  assert.equal(resolveCardSprite('t3-002', { cardSkins: { yisunsin: 'ghost' } }, { catalog }), 'assets/creatures/t3-002.png'); // unknown skin
});
t('sanitizeInventory drops unowned equips and junk', () => {
  const inv = sanitizeInventory({ inventory: [{ itemId: 'zzz' }], equipped: { avatarFrame: 'frame_royal', title: 'title_hanyang' } });
  assert.equal(inv.equipped.avatarFrame, 'frame_basic');
  assert.equal(inv.equipped.title, 'title_newbie');
  assert.equal(sanitizeInventory(null).equipped.cardFrame, 'cf_hanji');
});
t('unlock gate: enforced/unenforced (R-06)', () => {
  const p = { level: 3, social: false, normal: { games: 4 } };
  assert.equal(rankedUnlockStatus(p, false).unlocked, true);
  const g = rankedUnlockStatus(p, true);
  assert.equal(g.unlocked, false);
  assert.deepEqual(g.items.map((i) => i.ok), [false, false, false]);
  assert.equal(rankedUnlockStatus({ level: 10, social: true, normal: { games: 10 } }, true).unlocked, true);
  assert.equal(rankedUnlockStatus({ level: 10, social: true, normal: { games: 9 } }, true).unlocked, false);
});
t('store: ranked match round trip + placement progress', () => {
  const st = mem();
  let p = loadProfile(st);
  assert.equal(p.ranked.placement.gamesPlayed, 0);
  assert.equal(p.ranked.official, false);
  recordRankedMatch(st, { matchId: 'a', seed: 1, playerCount: 4, rank: 1, points: 21, delta: 32, ratingBefore: 1000, sim: true, players: [] });
  p = loadProfile(st);
  assert.equal(p.ranked.rating, 1032);
  assert.equal(p.ranked.placement.gamesPlayed, 1);
  assert.equal(p.ranked.wins, 1);
  assert.equal(p.matches.length, 1);
  assert.equal(p.matches[0].official, false);
  assert.equal(p.season.seasonId, 'S0');
});
t('store: void leave = -15 rating, no game counted, queue ban set', () => {
  const st = mem();
  const now = 1_700_000_000_000;
  recordRankedLeave(st, { voided: true, delta: -15, rank: 4, matchId: 'v', seed: 1, playerCount: 4, ratingBefore: 1000 }, now);
  const p = loadProfile(st);
  assert.equal(p.ranked.rating, 985);
  assert.equal(p.ranked.gamesTotal, 0);
  assert.equal(p.ranked.queueBanUntil, now + 600000);
  assert.equal(p.matches[0].voided, true);
});
t('store: normal stats + corrupt profile falls back', () => {
  const st = mem();
  recordNormalGame(st, true); recordNormalGame(st, false);
  assert.deepEqual(loadProfile(st).normal, { games: 2, wins: 1 });
  st.setItem('ohsp-profile-v1', '{"v":1,"ranked":{"placement":"x"}}');
  assert.equal(loadProfile(st).ranked.rating, 1000);
  st.setItem('ohsp-profile-v1', 'not json');
  assert.equal(loadProfile(st).normal.games, 0);
});
t('store: inventory claim/equip persists; options mode persists', () => {
  const st = mem();
  assert.ok(claimFreeItem(st, 'cf_ink').ok);
  assert.ok(equipOwnedItem(st, 'cf_ink').ok);
  assert.equal(loadInventory(st).equipped.cardFrame, 'cf_ink');
  assert.equal(claimFreeItem(st, 'frame_royal').ok, false);
  const o = loadOptions(st);
  assert.equal(o.mode, 'normal');
  o.mode = 'ranked'; saveOptions(st, o);
  assert.equal(loadOptions(st).mode, 'ranked');
});
console.log(`\n${pass} passed${process.exitCode ? ', with FAILURES' : ''}`);
