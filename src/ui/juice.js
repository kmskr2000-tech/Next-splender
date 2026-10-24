// 게임 주스: 차례 배너, 점수 팝업, 범프, 마지막 라운드 알림.
// main.js 의 render() 끝에서 afterRender(ctrl) 만 호출하면 된다. 모든 오버레이는 pointer-events:none 이며 스스로 제거된다.
import { getPoints } from '../core/engine.js?v=1792061648';

const REDUCED = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

let prevCtrl = null;
let prevPts = null; // 좌석별 이전 점수
let prevTokens = null; // 내 토큰 개수 (표시 순서대로)
let lastRoundShown = false;

export function resetJuice() {
  prevPts = null;
  prevTokens = null;
  lastRoundShown = false;
  document.querySelectorAll('.juice-fx').forEach((n) => n.remove());
}

function spawn(cls, html, ms, parent = document.body) {
  const el = document.createElement('div');
  el.className = `juice-fx ${cls}`;
  el.innerHTML = html;
  parent.appendChild(el);
  setTimeout(() => el.remove(), ms);
  return el;
}

function bump(el) {
  if (!el || REDUCED()) return;
  el.classList.remove('juice-bump');
  void el.offsetWidth; // 애니메이션 재시작
  el.classList.add('juice-bump');
  setTimeout(() => el.classList.remove('juice-bump'), 450);
}

function popup(anchor, text) {
  if (!anchor) return;
  const r = anchor.getBoundingClientRect();
  if (!r.width && !r.height) return;
  const el = spawn('juice-pop', text, REDUCED() ? 500 : 1100);
  el.style.left = `${r.left + r.width / 2}px`;
  el.style.top = `${r.top + r.height / 2}px`;
}

export function myTurnBanner() {
  if (!document.getElementById('header')) return;
  document.querySelectorAll('.juice-banner').forEach((n) => n.remove());
  const board = document.getElementById('board');
  const r = board ? board.getBoundingClientRect() : { top: 90, left: 0, width: innerWidth };
  const el = spawn('juice-banner', '<span>내 차례!</span>', REDUCED() ? 700 : 1300);
  el.style.top = `${Math.round(r.top + 14)}px`;
}

function lastRoundToast() {
  spawn('juice-toast', '<span>마지막 라운드!</span>', REDUCED() ? 1000 : 1600);
}

export function afterRender(ctrl) {
  if (!ctrl) { if (prevCtrl) resetJuice(); prevCtrl = null; return; }
  if (ctrl !== prevCtrl) { resetJuice(); prevCtrl = ctrl; }
  // 게임이 끝나면 결과 화면 위에 팝업이 남지 않게 지우고 더 띄우지 않는다
  if (ctrl.finished) { document.querySelectorAll('.juice-fx').forEach((el) => el.remove()); return; }
  const players = ctrl.game.players;

  // 점수 변화
  const pts = players.map((p) => getPoints(p));
  if (prevPts && prevPts.length === pts.length) {
    pts.forEach((v, i) => {
      const d = v - prevPts[i];
      if (d <= 0) return;
      const rail = document.querySelector(`.rail-item[data-id="${i}"]`);
      popup(rail, `+${d}`);
      bump(rail?.querySelector('.rsc'));
      if (i === ctrl.human) {
        const sc = document.querySelector('.dock-sc');
        popup(sc, `+${d}`);
        bump(sc?.querySelector('b'));
      }
    });
  }
  prevPts = pts;

  // 내 토큰 개수 변화 (.mytk 순서 = TOKEN_KEYS 순서)
  const me = ctrl.me;
  const cells = [...document.querySelectorAll('.mytokens .mytk .tkn')];
  const counts = cells.map((c) => Number(c.textContent) || 0);
  if (me && prevTokens && prevTokens.length === counts.length) {
    counts.forEach((v, i) => { if (v !== prevTokens[i]) bump(cells[i]); });
  }
  prevTokens = counts;

  // 마지막 라운드 (최초 1회)
  if (ctrl.lastRound && !lastRoundShown) {
    lastRoundShown = true;
    lastRoundToast();
  }
}
