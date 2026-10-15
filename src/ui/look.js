// 내 캐릭터 꾸미기 (D22): 기본 몸체 + 파츠 레이어(옷 → 얼굴 → 머리 → 모자)를 겹쳐 그린다.
// 파츠 PNG는 모두 같은 64x64 기본 몸체 위에 PixelLab 영역 다시 그리기로 만들어 위치가 정확히 맞는다.
// 옷 색은 붉은 옷을 hue-rotate 로 돌려 만들고, 배경은 CSS 색이다. 다른 플레이어에게는 짧은 코드로 보낸다.

const DIR = 'assets/avatar';

export const LOOK_PARTS = {
  hair: { label: '머리', items: [['base', '짧은 머리'], ['sangtu', '상투'], ['daenggi', '댕기머리'], ['jjok', '쪽머리'], ['twin', '양갈래'], ['messy', '더벅머리']] },
  hat: { label: '모자', items: [['none', '없음'], ['gat', '갓'], ['jokduri', '족두리'], ['bokgeon', '복건'], ['paraengi', '패랭이'], ['hwagwan', '화관'], ['horns', '도깨비 뿔']] },
  face: { label: '표정', items: [['base', '미소'], ['grin', '활짝'], ['wink', '윙크'], ['brave', '씩씩'], ['shock', '깜짝'], ['sleepy', '졸림']] },
  cloth: { label: '옷', items: [['base', '흰 저고리'], ['hanbok', '꽃 저고리'], ['saekdong', '색동'], ['dopo', '도포'], ['gwanbok', '관복'], ['armor', '갑옷']] },
  tint: { label: '옷 색', items: [['red', '적'], ['gold', '황'], ['jade', '청록'], ['blue', '남'], ['plum', '자'], ['ink', '흑']] },
  bg: { label: '배경', items: [['hanji', '한지'], ['peach', '복숭아'], ['sky', '하늘'], ['mint', '쑥'], ['lilac', '보라'], ['night', '밤']] },
};
const TINT = { red: '', gold: 'hue-rotate(42deg) saturate(1.1)', jade: 'hue-rotate(150deg)', blue: 'hue-rotate(215deg)', plum: 'hue-rotate(285deg)', ink: 'grayscale(1) brightness(.5)' };
const BG = { hanji: '#F3E7CF', peach: '#F8D3C2', sky: '#CFE3F2', mint: '#D3EBD5', lilac: '#E2D6F0', night: '#2B3448' };
const KEYS = ['hair', 'hat', 'face', 'cloth', 'tint', 'bg'];

export const DEFAULT_LOOK = { hair: 'base', hat: 'none', face: 'base', cloth: 'base', tint: 'red', bg: 'hanji' };

/** Keep only known part ids (unknown -> default). Accepts anything (saved data, network). */
export function sanitizeLook(o) {
  const out = { ...DEFAULT_LOOK };
  if (o && typeof o === 'object') {
    for (const k of KEYS) if (LOOK_PARTS[k].items.some(([id]) => id === o[k])) out[k] = o[k];
  }
  return out;
}
/** Short wire code, e.g. "1.2.0.3.0.5" (indices per part). */
export function encodeLook(look) {
  const l = sanitizeLook(look);
  return KEYS.map((k) => LOOK_PARTS[k].items.findIndex(([id]) => id === l[k])).join('.');
}
export function decodeLook(code) {
  const idx = String(code || '').split('.').map(Number);
  const o = {};
  KEYS.forEach((k, i) => { const it = LOOK_PARTS[k].items[idx[i]]; if (it) o[k] = it[0]; });
  return sanitizeLook(o);
}
export function randomLook(rnd = Math.random) {
  const pick = (k) => { const it = LOOK_PARTS[k].items; return it[Math.floor(rnd() * it.length)][0]; };
  return sanitizeLook({ hair: pick('hair'), hat: rnd() < 0.5 ? 'none' : pick('hat'), face: pick('face'), cloth: pick('cloth'), tint: pick('tint'), bg: pick('bg') });
}

/** Layered avatar. `cls` adds the usual .av size classes (sm/md/lg) and frame classes. */
export function lookHTML(look, cls = '') {
  const l = sanitizeLook(look);
  const layer = (src, style = '') => `<img src="${DIR}/${src}.png" alt=""${style ? ` style="${style}"` : ''}>`;
  return `<span class="av look ${cls}" style="--bg:${BG[l.bg]}">`
    + layer('base')
    + (l.cloth !== 'base' ? layer(`cloth_${l.cloth}`, TINT[l.tint] ? `filter:${TINT[l.tint]}` : '') : '')
    + (l.face !== 'base' ? layer(`face_${l.face}`) : '')
    + (l.hair !== 'base' ? layer(`hair_${l.hair}`) : '')
    + (l.hat !== 'none' ? layer(`hat_${l.hat}`) : '')
    + '</span>';
}
