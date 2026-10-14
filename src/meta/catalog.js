// Cosmetic item catalog (monetization.md 5.1 schema). Pure data, no gameplay effect (gameplayEffect is always 'none').
// Stage 0: free items are claimable; paid items are display-only ("준비 중"). No payment code exists.
// `css` = class applied by the renderer; `glyph` = emote face; `files` = card ids a skin actually ships sprites for
// (stand-in for assets/skins/{skinId}/manifest.json until a real manifest loader exists).

const FREE = { currency: 'yeopjeon', amount: 0 };
const ver = 1;

export const SLOT_LABELS = {
  avatarFrame: '프로필 테두리',
  cardFrame: '카드 프레임',
  title: '칭호',
  emote: '이모트',
  cardSkin: '인물 스킨',
};

// Shop category tabs, in display order.
export const CATEGORIES = [
  { id: 'avatarFrame', label: '테두리' },
  { id: 'cardFrame', label: '카드 틀' },
  { id: 'title', label: '칭호' },
  { id: 'emote', label: '이모트' },
  { id: 'cardSkin', label: '스킨' },
];

export const CATALOG = [
  // ----- avatar frames -----
  { id: 'frame_basic', type: 'avatarFrame', slot: 'avatarFrame', name: { ko: '기본 테두리' }, description: { ko: '먹색 기본 테두리' },
    price: FREE, rarity: 'common', acquire: 'shop', default: true, css: 'fr-basic', gameplayEffect: 'none', version: ver },
  { id: 'frame_dancheong', type: 'avatarFrame', slot: 'avatarFrame', name: { ko: '단청 테두리' }, description: { ko: '붉은색과 노란색 단청 무늬' },
    price: FREE, rarity: 'common', acquire: 'shop', css: 'fr-dancheong', gameplayEffect: 'none', version: ver },
  { id: 'frame_royal', type: 'avatarFrame', slot: 'avatarFrame', name: { ko: '어좌 금테' }, description: { ko: '금빛 이중 테두리' },
    price: { currency: 'yeopjeon', amount: 150 }, rarity: 'rare', acquire: 'shop', css: 'fr-royal', gameplayEffect: 'none', version: ver },
  // ----- card frames -----
  { id: 'cf_hanji', type: 'cardFrame', slot: 'cardFrame', name: { ko: '한지 프레임' }, description: { ko: '기본 한지 느낌의 틀' },
    price: FREE, rarity: 'common', acquire: 'shop', default: true, css: 'cf-hanji', gameplayEffect: 'none', version: ver },
  { id: 'cf_ink', type: 'cardFrame', slot: 'cardFrame', name: { ko: '먹선 프레임' }, description: { ko: '굵은 먹선으로 두른 틀' },
    price: FREE, rarity: 'common', acquire: 'shop', css: 'cf-ink', gameplayEffect: 'none', version: ver },
  { id: 'cf_gold', type: 'cardFrame', slot: 'cardFrame', name: { ko: '금박 프레임' }, description: { ko: '금박을 입힌 틀' },
    price: { currency: 'yeopjeon', amount: 100 }, rarity: 'rare', acquire: 'shop', css: 'cf-gold', gameplayEffect: 'none', version: ver },
  // ----- titles -----
  { id: 'title_newbie', type: 'title', slot: 'title', name: { ko: '새내기 도사' }, description: { ko: '처음 온 도사' },
    price: FREE, rarity: 'common', acquire: 'shop', default: true, css: 'tt-basic', gameplayEffect: 'none', version: ver },
  { id: 'title_hanyang', type: 'title', slot: 'title', name: { ko: '한양 나그네' }, description: { ko: '한양을 오가는 길손' },
    price: FREE, rarity: 'common', acquire: 'shop', css: 'tt-basic', gameplayEffect: 'none', version: ver },
  { id: 'title_tongjesa', type: 'title', slot: 'title', name: { ko: '삼도수군통제사' }, description: { ko: '이순신 팬 전용 칭호 (가안)' },
    price: { currency: 'yeopjeon', amount: 50 }, rarity: 'rare', acquire: 'shop', css: 'tt-rare', gameplayEffect: 'none', version: ver },
  // ----- emotes (display slot only; sending needs a net event, see TODO in docs) -----
  { id: 'emo_thumb', type: 'emote', slot: 'emote', name: { ko: '엄지척' }, description: { ko: '잘했다는 인사' },
    price: FREE, rarity: 'common', acquire: 'shop', glyph: '👍', gameplayEffect: 'none', version: ver },
  { id: 'emo_tiger', type: 'emote', slot: 'emote', name: { ko: '호랑이 울음' }, description: { ko: '어흥!' },
    price: FREE, rarity: 'common', acquire: 'shop', glyph: '🐯', gameplayEffect: 'none', version: ver },
  { id: 'emo_bangmang', type: 'emote', slot: 'emote', name: { ko: '도깨비 방망이' }, description: { ko: '뚝딱!' },
    price: { currency: 'yeopjeon', amount: 100 }, rarity: 'rare', acquire: 'shop', glyph: '👹', gameplayEffect: 'none', version: ver },
  // ----- card skin (paid placeholder; no sprites shipped yet -> always falls back) -----
  { id: 'skin_yisunsin_battle', type: 'cardSkin', slot: 'cardSkin:yisunsin', target: { line_id: 'yisunsin', card_ids: ['t1-002', 't2-002', 't3-002'] },
    name: { ko: '이순신 전투복' }, description: { ko: '삼도수군통제사의 갑주 복장' },
    price: { currency: 'yeopjeon', amount: 250 }, rarity: 'epic', acquire: 'shop', assetPath: 'assets/skins/skin_yisunsin_battle/', files: [],
    gameplayEffect: 'none', version: ver },
];

export const itemById = (id, catalog = CATALOG) => catalog.find((i) => i.id === id) ?? null;
export const isFree = (item) => item.price.amount === 0;
export const slotGroup = (item) => item.slot.split(':')[0];
export const itemName = (item) => item.name.ko;

/** CI-style check (monetization 5.1): every item must declare gameplayEffect "none" and unique ids. */
export function validateCatalog(catalog = CATALOG) {
  const errors = [];
  const seen = new Set();
  for (const it of catalog) {
    if (seen.has(it.id)) errors.push(`dup id ${it.id}`);
    seen.add(it.id);
    if (it.gameplayEffect !== 'none') errors.push(`${it.id}: gameplayEffect must be none`);
    if (!(it.price && it.price.amount >= 0)) errors.push(`${it.id}: bad price`);
    if (!it.slot || !it.type) errors.push(`${it.id}: missing slot/type`);
  }
  return errors;
}
