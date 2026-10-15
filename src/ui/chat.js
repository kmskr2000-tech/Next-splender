// 멀티플레이 채팅 (대기실·게임 공통, D23 개편).
// "···" 버튼 → 아래에 이모티콘 줄 + 한 줄 입력만 열린다 (대화방 없음).
// 받은 말은 말한 사람 캐릭터 얼굴 옆에 말풍선으로 4초 뜬다:
//   게임 = 오른쪽 플레이어 줄(.rail-item[data-id]), 대기실 = 자리 카드(.slot[data-seat]).
// 이름·메시지는 다른 플레이어가 보낸 값이라 반드시 이스케이프한다.

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const BUBBLE_MS = 4000;
export const QUICK_EMOTES = ['👍', '😂', '😮', '😭', '😡', '🙏', '🎉', '🔥'];
const isEmote = (t) => QUICK_EMOTES.includes(t);

export function createChatWidget(root, { send }) {
  root.innerHTML = `
    <button class="chat-fab" type="button" aria-label="말하기">···</button>
    <form class="chat-bar" hidden autocomplete="off">
      <div class="chat-emos">${QUICK_EMOTES.map((e) => `<button type="button" class="chat-emo" data-emo="${e}" aria-label="이모티콘 ${e}">${e}</button>`).join('')}</div>
      <div class="chat-row">
        <input class="chat-in" maxlength="40" placeholder="한마디 (최대 40자)" enterkeyhint="send">
        <button class="chat-send" type="submit">보내기</button>
        <button class="chat-close" type="button" aria-label="닫기">✕</button>
      </div>
    </form>
    <div class="chat-bubbles" aria-live="polite"></div>`;
  const $ = (s) => root.querySelector(s);
  const fab = $('.chat-fab'), bar = $('.chat-bar'), input = $('.chat-in'), layer = $('.chat-bubbles');
  let open = false, lastMsg = undefined, mode = 'game'; // lastMsg: 마지막으로 띄운 메시지 (기록은 50줄로 잘리므로 개수 대신 객체로 추적)
  const live = []; // [{ seat, el, until }]

  const setOpen = (v) => {
    open = v;
    bar.hidden = !v;
    fab.hidden = v;
    if (v) setTimeout(() => input.focus(), 0);
    else input.blur();
  };
  const submit = (text) => { if (send(text)) { input.value = ''; setOpen(false); } };
  fab.addEventListener('click', () => setOpen(true));
  $('.chat-close').addEventListener('click', () => setOpen(false));
  bar.addEventListener('submit', (e) => { e.preventDefault(); submit(input.value); });
  bar.addEventListener('click', (e) => { const b = e.target.closest('.chat-emo'); if (b) submit(b.dataset.emo); });

  // 말풍선을 해당 좌석의 얼굴 옆에 붙인다 (화면이 다시 그려져도 매번 위치를 다시 잡는다)
  function anchorOf(seat) {
    return mode === 'game'
      ? document.querySelector(`.rail-item[data-id="${seat}"]`)
      : document.querySelector(`.slot[data-seat="${seat}"]`);
  }
  function place(b) {
    const a = anchorOf(b.seat);
    if (!a) { b.el.hidden = true; return; }
    const r = a.getBoundingClientRect();
    b.el.hidden = false;
    if (mode === 'game') { // 오른쪽 줄: 얼굴 왼쪽에, 꼬리는 오른쪽
      b.el.className = `chat-say left ${b.emo ? 'emo' : ''}`;
      b.el.style.left = ''; b.el.style.right = `${window.innerWidth - r.left + 6}px`;
      b.el.style.top = `${r.top + r.height / 2}px`;
    } else { // 대기실 자리 카드: 위쪽 가운데
      b.el.className = `chat-say up ${b.emo ? 'emo' : ''}`;
      b.el.style.right = ''; b.el.style.left = `${r.left + r.width / 2}px`;
      b.el.style.top = `${r.top + 8}px`;
    }
  }
  function say(m) {
    for (let i = live.length - 1; i >= 0; i--) if (live[i].seat === m.from) { live[i].el.remove(); live.splice(i, 1); }
    const el = document.createElement('div');
    const emo = isEmote(m.text);
    el.innerHTML = emo ? esc(m.text) : `<span>${esc(m.text)}</span>`;
    layer.appendChild(el);
    const b = { seat: m.from, el, emo };
    live.push(b);
    place(b);
    setTimeout(() => { el.remove(); const i = live.indexOf(b); if (i >= 0) live.splice(i, 1); }, BUBBLE_MS);
  }

  function update({ visible, log = [], mode: md = 'game' }) {
    mode = md;
    root.hidden = !visible;
    root.dataset.mode = md;
    const newest = log[log.length - 1] || null;
    if (!visible) { if (open) setOpen(false); lastMsg = newest; live.splice(0).forEach((b) => b.el.remove()); return; }
    if (lastMsg === undefined) lastMsg = newest; // 처음 보일 때 지난 말은 다시 띄우지 않음
    if (newest !== lastMsg) {
      const from = lastMsg ? log.indexOf(lastMsg) : -1;
      const start = !lastMsg ? 0 : from >= 0 ? from + 1 : log.length - 1;
      for (let i = start; i < log.length; i++) say(log[i]);
      lastMsg = newest;
    }
    live.forEach(place);
  }
  return { update, isOpen: () => open };
}
