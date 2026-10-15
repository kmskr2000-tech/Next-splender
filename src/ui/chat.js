// 멀티플레이 채팅 위젯 (대기실·게임 공통).
// 화면은 자주 다시 그려지므로 입력창은 한 번만 만들고, 메시지 목록만 바꿔 타이핑이 지워지지 않게 한다.
// 이름·메시지는 다른 플레이어가 보낸 값이라 반드시 이스케이프한다.

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const BUBBLE_MS = 4000;

export function createChatWidget(root, { send }) {
  root.innerHTML = `
    <div class="chat-bubble" hidden></div>
    <button class="chat-fab" type="button" aria-label="채팅 열기">💬<i class="chat-badge" hidden></i></button>
    <div class="chat-panel" hidden role="dialog" aria-label="채팅">
      <div class="chat-head"><b>채팅</b><button class="chat-close" type="button" aria-label="채팅 닫기">✕</button></div>
      <div class="chat-list" aria-live="polite"></div>
      <form class="chat-form" autocomplete="off">
        <input class="chat-in" maxlength="40" placeholder="메시지 (최대 40자)" enterkeyhint="send">
        <button class="chat-send" type="submit">보내기</button>
      </form>
    </div>`;
  const $ = (s) => root.querySelector(s);
  const fab = $('.chat-fab'), badge = $('.chat-badge'), panel = $('.chat-panel'), list = $('.chat-list'), input = $('.chat-in'), bubble = $('.chat-bubble');
  let open = false, seen = 0, shown = -1, bubbleTimer = null, last = { log: [], myIndex: -1 };

  const setOpen = (v) => {
    open = v;
    panel.hidden = !v;
    fab.hidden = v;
    bubble.hidden = true;
    if (v) { seen = last.log.length; paintBadge(); list.scrollTop = list.scrollHeight; setTimeout(() => input.focus(), 0); }
  };
  const paintBadge = () => {
    const n = Math.max(0, last.log.length - seen);
    badge.hidden = n === 0 || open;
    badge.textContent = n > 9 ? '9+' : String(n);
  };
  fab.addEventListener('click', () => setOpen(true));
  $('.chat-close').addEventListener('click', () => setOpen(false));
  $('.chat-form').addEventListener('submit', (e) => {
    e.preventDefault();
    if (send(input.value)) input.value = '';
  });

  function update({ visible, log = [], myIndex = -1 }) {
    root.hidden = !visible;
    if (!visible) { if (open) setOpen(false); seen = log.length; shown = log.length; last = { log, myIndex }; return; }
    const grew = log.length !== shown;
    last = { log, myIndex };
    if (grew) {
      const atBottom = list.scrollHeight - list.scrollTop - list.clientHeight < 24;
      list.innerHTML = log.length
        ? log.map((m) => `<div class="chat-line ${m.from === myIndex ? 'me' : ''}"><b>${esc(m.name)}</b><span>${esc(m.text)}</span></div>`).join('')
        : '<p class="chat-empty">아직 대화가 없어요. 먼저 인사해 보세요!</p>';
      if (atBottom || open) list.scrollTop = list.scrollHeight;
      const newest = log[log.length - 1];
      if (!open && shown >= 0 && newest && newest.from !== myIndex) {
        bubble.innerHTML = `<b>${esc(newest.name)}</b> ${esc(newest.text)}`;
        bubble.hidden = false;
        clearTimeout(bubbleTimer);
        bubbleTimer = setTimeout(() => { bubble.hidden = true; }, BUBBLE_MS);
      }
      shown = log.length;
    }
    if (open) seen = log.length;
    paintBadge();
  }
  return { update, isOpen: () => open };
}
