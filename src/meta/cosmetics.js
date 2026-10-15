// Inventory / equip logic and render hooks for cosmetics. Pure functions: no DOM, no storage.
// Payment is intentionally absent: claimItem only accepts price.amount === 0 items.

import { CATALOG, itemById, isFree, slotGroup } from './catalog.js?v=1792047695';
import { ROSTER } from '../data/roster.js?v=1792047695';

export const EMOTE_SLOTS = 6;
export const BASE_SPRITE_DIR = 'assets/creatures';
export const SKIN_DIR = 'assets/skins';

export function defaultEquipped() {
  return { avatarFrame: null, cardFrame: null, orbSkin: null, tableTheme: null, evolveFx: null, title: null, emotes: Array(EMOTE_SLOTS).fill(null), cardSkins: {} };
}

/** New inventory: default items owned and equipped. */
export function newInventory(now = 0, catalog = CATALOG) {
  const inv = { version: 1, wallet: { yeopjeon: 0, pun: 0 }, inventory: [], equipped: defaultEquipped() };
  for (const it of catalog.filter((i) => i.default)) {
    inv.inventory.push({ itemId: it.id, acquiredAt: now, source: 'reward', orderId: null });
    inv.equipped[it.slot] = it.id;
  }
  return inv;
}

export const owns = (inv, itemId) => inv.inventory.some((e) => e.itemId === itemId);

export function isEquipped(inv, item) {
  const e = inv.equipped;
  if (item.slot === 'emote') return e.emotes.includes(item.id);
  if (item.slot.startsWith('cardSkin:')) return e.cardSkins[item.slot.split(':')[1]] === item.id;
  return e[item.slot] === item.id;
}

/** Claim a free item. Paid items are rejected (no payment path in this stage). Returns {ok, inv, error}. */
export function claimItem(inv, itemId, now = Date.now(), catalog = CATALOG) {
  const item = itemById(itemId, catalog);
  if (!item) return { ok: false, inv, error: 'unknown_item' };
  if (owns(inv, itemId)) return { ok: false, inv, error: 'already_owned' };
  if (!isFree(item)) return { ok: false, inv, error: 'not_available' };
  const next = structuredClone(inv);
  next.inventory.push({ itemId, acquiredAt: now, source: 'reward', orderId: null });
  return { ok: true, inv: next, error: null };
}

/** Equip (or toggle off for emotes / titles-less slots) an owned item. */
export function equipItem(inv, itemId, catalog = CATALOG) {
  const item = itemById(itemId, catalog);
  if (!item) return { ok: false, inv, error: 'unknown_item' };
  if (!owns(inv, itemId)) return { ok: false, inv, error: 'not_owned' };
  const next = structuredClone(inv);
  const e = next.equipped;
  if (item.slot === 'emote') {
    const at = e.emotes.indexOf(itemId);
    if (at >= 0) e.emotes[at] = null;
    else {
      const free = e.emotes.indexOf(null);
      if (free < 0) return { ok: false, inv, error: 'emote_slots_full' };
      e.emotes[free] = itemId;
    }
  } else if (item.slot.startsWith('cardSkin:')) {
    const line = item.slot.split(':')[1];
    e.cardSkins[line] = e.cardSkins[line] === itemId ? null : itemId;
  } else {
    e[item.slot] = itemId;
  }
  return { ok: true, inv: next, error: null };
}

/** Drop anything unowned / unknown (storage hardening). */
export function sanitizeInventory(raw, now = 0, catalog = CATALOG) {
  const base = newInventory(now, catalog);
  if (!raw || typeof raw !== 'object' || !Array.isArray(raw.inventory)) return base;
  const inv = { version: 1, wallet: { yeopjeon: 0, pun: 0 }, inventory: [], equipped: defaultEquipped() };
  const w = raw.wallet || {};
  inv.wallet = { yeopjeon: Math.max(0, w.yeopjeon | 0), pun: Math.max(0, w.pun | 0) };
  const ids = new Set();
  for (const e of raw.inventory) {
    if (e && itemById(e.itemId, catalog) && !ids.has(e.itemId)) {
      ids.add(e.itemId);
      inv.inventory.push({ itemId: e.itemId, acquiredAt: Number(e.acquiredAt) || 0, source: String(e.source || 'reward'), orderId: e.orderId ?? null });
    }
  }
  for (const it of catalog.filter((i) => i.default)) if (!ids.has(it.id)) inv.inventory.push({ itemId: it.id, acquiredAt: now, source: 'reward', orderId: null });
  const eq = raw.equipped || {};
  for (const slot of ['avatarFrame', 'cardFrame', 'title']) {
    const id = eq[slot];
    const it = id && itemById(id, catalog);
    inv.equipped[slot] = it && it.slot === slot && owns(inv, id) ? id : (catalog.find((i) => i.default && i.slot === slot)?.id ?? null);
  }
  const em = Array.isArray(eq.emotes) ? eq.emotes : [];
  inv.equipped.emotes = Array.from({ length: EMOTE_SLOTS }, (_, i) => {
    const it = em[i] && itemById(em[i], catalog);
    return it && it.slot === 'emote' && owns(inv, em[i]) ? em[i] : null;
  });
  if (eq.cardSkins && typeof eq.cardSkins === 'object') {
    for (const [line, id] of Object.entries(eq.cardSkins)) {
      const it = id && itemById(id, catalog);
      if (it && it.slot === `cardSkin:${line}` && owns(inv, id)) inv.equipped.cardSkins[line] = id;
    }
  }
  return inv;
}

// ---------- render hooks ----------

/**
 * Sprite path for a card shown for an owner (monetization 5.3).
 * 1. line_id from the roster  2. owner's equipped skin for that line (must exist in catalog)
 * 3. skin ships a sprite for this card (item.files)  4. otherwise the default path.
 */
export function resolveCardSprite(cardId, equipped, { catalog = CATALOG, roster = ROSTER } = {}) {
  const base = `${BASE_SPRITE_DIR}/${cardId}.png`;
  try {
    const line = roster[cardId]?.line_id;
    const skinId = line && equipped?.cardSkins?.[line];
    if (!skinId) return base;
    const skin = itemById(skinId, catalog);
    if (!skin || skin.slot !== `cardSkin:${line}` || !Array.isArray(skin.files) || !skin.files.includes(cardId)) return base;
    return `${SKIN_DIR}/${skinId}/${cardId}.png`;
  } catch {
    return base; // never break rendering over a cosmetic
  }
}

const cssOf = (id) => (id ? itemById(id)?.css ?? '' : '');
export const avatarFrameClass = (equipped) => cssOf(equipped?.avatarFrame);
export const cardFrameClass = (equipped) => cssOf(equipped?.cardFrame);
export const titleOf = (equipped) => {
  const it = equipped?.title ? itemById(equipped.title) : null;
  return it ? { text: it.name.ko, css: it.css || '' } : null;
};

/**
 * Cosmetics other players see (monetization 5.4 SeatCosmetics subset). Display-only.
 * TODO(net): this is the payload to attach per seat in the START / seat info message once the protocol is extended
 * (src/net/protocol.js + session.js hostStart). Do not trust it for rules; stage 1 values are self-reported.
 */
export function seatCosmetics(equipped, tierId = null) {
  return { avatarFrame: equipped?.avatarFrame ?? null, title: equipped?.title ?? null, cardFrame: equipped?.cardFrame ?? null, tierId };
}

export { slotGroup };
