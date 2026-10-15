// node tests/lobby.test.mjs -- 친목전 로비: 방 메타(kind/size/pwHash) 저장·목록 노출, 게스트 입장, 매칭 방과 구분
// Firebase 대신 메모리 RTDB 목(아래 MockDb)으로 FirebaseRoom + NetSession 흐름을 돌린다.
import assert from 'node:assert/strict';
import { __setMockDb, listRooms, claimName, nameKey } from '../src/net/fireroom.js?v=1792061648';
import { NetSession } from '../src/net/session.js?v=1792061648';
import { encodeLook, decodeLook, sanitizeLook } from '../src/ui/look.js?v=1792061648';

// ---- tiny in-memory RTDB (only what fireroom.js uses) ----
class MockDb {
  constructor() { this.data = {}; this.listeners = []; this.n = 0; }
  get(path) { let o = this.data; for (const k of parts(path)) { if (o == null || typeof o !== 'object') return null; o = o[k]; } return o ?? null; }
  write(path, val) {
    const ks = parts(path);
    if (!ks.length) { this.data = val ?? {}; } else {
      let o = this.data;
      for (const k of ks.slice(0, -1)) { if (o[k] == null || typeof o[k] !== 'object') o[k] = {}; o = o[k]; }
      if (val == null) delete o[ks.at(-1)]; else o[ks.at(-1)] = clone(val);
    }
    this.fire(path);
  }
  fire(path) {
    const p = parts(path).join('/');
    for (const l of [...this.listeners]) {
      const lp = parts(l.path).join('/');
      if (p === lp || p.startsWith(lp + '/') || lp.startsWith(p + '/') || lp === '' || p === '') queueMicrotask(() => l.cb(snap(this, l.path)));
    }
  }
  ref(path = '') { return new Ref(this, path); }
}
const parts = (p) => String(p).split('/').filter(Boolean);
const clone = (v) => (v == null ? v : JSON.parse(JSON.stringify(v)));
function snap(db, path) {
  const v = path === '.info/connected' ? true : clone(db.get(path));
  return {
    key: parts(path).at(-1) ?? null,
    ref: new Ref(db, path),
    exists: () => v != null,
    val: () => v,
    forEach: (fn) => { if (v && typeof v === 'object') for (const k of Object.keys(v)) { if (fn(snap(db, `${path}/${k}`)) === true) break; } },
  };
}
class Ref {
  constructor(db, path) { this.db = db; this.path = path; this.key = parts(path).at(-1) ?? null; }
  child(k) { return new Ref(this.db, `${this.path}/${k}`); }
  async once() { return snap(this.db, this.path); }
  async set(v) { this.db.write(this.path, v); }
  async update(obj) { for (const [k, v] of Object.entries(obj)) this.db.write(`${this.path}/${k}`, v); }
  async remove() { this.db.write(this.path, null); }
  push(v) { const r = this.child(`p${String(++this.db.n).padStart(6, '0')}`); const pr = v === undefined ? Promise.resolve() : r.set(v); r.then = pr.then.bind(pr); r.catch = pr.catch.bind(pr); return r; }
  async transaction(fn) { const nv = fn(clone(this.db.get(this.path))); if (nv !== undefined) this.db.write(this.path, nv); return { committed: nv !== undefined, snapshot: snap(this.db, this.path) }; }
  on(_ev, cb) { this.db.listeners.push({ path: this.path, cb }); queueMicrotask(() => cb(snap(this.db, this.path))); return cb; }
  off(_ev, cb) { this.db.listeners = this.db.listeners.filter((l) => !(l.path === this.path && (!cb || l.cb === cb))); }
  onDisconnect() { return { set: async () => {}, remove: async () => {}, cancel: async () => {}, update: async () => {} }; }
}

let pass = 0;
const t = async (name, fn) => { try { await fn(); pass++; console.log('ok   ' + name); } catch (e) { console.log('FAIL ' + name + '\n     ' + (e.stack || e.message)); process.exitCode = 1; } };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const cb = () => ({ onRender() {}, onGameStart() {}, onGameEnd() {}, onNotice() {} });

const db = new MockDb();
__setMockDb(db);

const host = new NetSession(cb());
const guest = new NetSession(cb());
host.myLook = encodeLook({ hat: 'gat', hair: 'sangtu', cloth: 'dopo', tint: 'blue' });
guest.myLook = encodeLook({ hat: 'hwagwan', hair: 'twin', face: 'grin', bg: 'peach' });

await t('host creates a lobby room with title/size/password hash', async () => {
  await host.hostCreate('방장', '퇴근 후 한 판', 45000, { kind: 'lobby', size: 3, pwHash: 'abc123' });
  assert.equal(host.phase, 'hostlobby');
  const r = db.get(`ohsp-rooms/${host.shortCode}`);
  assert.equal(r.title, '퇴근 후 한 판');
  assert.equal(r.kind, 'lobby');
  assert.equal(r.size, 3);
  assert.equal(r.pwHash, 'abc123');
});

await t('matchmaking rooms carry no lobby meta', async () => {
  const m = new NetSession(cb());
  await m.hostCreate('매칭', '빠른대전 4인', 45000);
  const r = db.get(`ohsp-rooms/${m.shortCode}`);
  assert.equal(r.kind, undefined);
  const listed = (await listRooms()).find((x) => x.code === m.shortCode);
  assert.equal(listed.kind, 'match');
  m.end();
});

await t('listRooms exposes lobby fields (kind/size/locked/pwHash)', async () => {
  const rooms = await listRooms();
  const r = rooms.find((x) => x.code === host.shortCode);
  assert.ok(r, 'room listed');
  assert.equal(r.kind, 'lobby');
  assert.equal(r.size, 3);
  assert.equal(r.locked, true);
  assert.equal(r.pwHash, 'abc123');
  assert.equal(r.playerCount, 1);
});

await t('guest joins the lobby room and both see 2 players', async () => {
  await guest.guestJoin('손님', host.shortCode);
  for (let i = 0; i < 50 && (host.names.length < 2 || guest.phase !== 'guestlobby'); i++) await sleep(10);
  assert.deepEqual(host.names, ['방장', '손님']);
  assert.equal(guest.phase, 'guestlobby');
  const r = (await listRooms()).find((x) => x.code === host.shortCode);
  assert.equal(r.playerCount, 2);
});

await t('looks: room roster carries every seat look code', async () => {
  for (let i = 0; i < 50 && guest.looks.length < 2; i++) await sleep(10);
  assert.equal(decodeLook(host.looks[1]).hat, 'hwagwan');
  assert.equal(decodeLook(guest.looks[0]).hat, 'gat');
  assert.equal(decodeLook(guest.looks[0]).tint, 'blue');
});
await t('looks: sanitize/encode round trip, junk falls back to defaults', () => {
  const l = sanitizeLook({ hair: 'jjok', hat: 'nope', face: 'wink', cloth: 'armor', tint: 'ink', bg: 'sky', extra: 1 });
  assert.equal(l.hat, 'none');
  assert.deepEqual(decodeLook(encodeLook(l)), l);
  assert.equal(decodeLook('<script>').hair, 'base');
});

await t('chat: guest line is relayed by host to everyone with sender name', async () => {
  assert.equal(guest.sendChat('  안녕하세요   <b>반가워요</b>  '), true);
  for (let i = 0; i < 50 && (host.chatLog.length < 1 || guest.chatLog.length < 1); i++) await sleep(10);
  assert.equal(host.chatLog.at(-1).name, '손님');
  assert.equal(host.chatLog.at(-1).text, '안녕하세요 <b>반가워요</b>', 'trimmed; escaping is the UI job');
  assert.equal(guest.chatLog.at(-1).text, host.chatLog.at(-1).text);
  assert.equal(guest.chatLog.at(-1).from, 1);
});
await t('chat: host line reaches guest; 40-char cap; empty and rapid lines dropped', async () => {
  assert.equal(host.sendChat('가'.repeat(60)), true);
  assert.equal(host.sendChat('너무 빨리'), false, 'rate limited');
  assert.equal(guest.sendChat('   '), false, 'empty');
  for (let i = 0; i < 50 && guest.chatLog.length < 2; i++) await sleep(10);
  assert.equal(guest.chatLog.at(-1).name, '방장');
  assert.equal(guest.chatLog.at(-1).text.length, 40);
});

await t('same name in one room gets a number suffix', async () => {
  const g2 = new NetSession(cb());
  await g2.guestJoin('방장', host.shortCode);
  for (let i = 0; i < 50 && host.names.length < 3; i++) await sleep(10);
  assert.deepEqual(host.names, ['방장', '손님', '방장2']);
  g2.end();
});

await t('nickname: first claim ok, other device taken (case-insensitive)', async () => {
  assert.equal(await claimName('도사', 'devA'), 'ok');
  assert.equal(await claimName('도사', 'devB'), 'taken');
  assert.equal(await claimName('Tiger', 'devA'), 'ok');
  assert.equal(await claimName(' tiger ', 'devB'), 'taken');
  assert.equal(await claimName('도사', 'devA'), 'ok', 'same device can re-claim');
});
await t('nickname: rename releases the old name', async () => {
  assert.equal(await claimName('홍길동', 'devA', '도사'), 'ok');
  assert.equal(db.get(`ohsp-names/${nameKey('도사')}`).released, true);
  assert.equal(await claimName('도사', 'devB'), 'ok', 'released name is free');
});
await t('nickname key is RTDB-safe', () => {
  assert.ok(!/[.$#\[\]/]/.test(nameKey('a.b$c#d[e]/f')));
});

host.end(); guest.end();
console.log(`\n${pass} passed`);
setTimeout(() => process.exit(process.exitCode || 0), 50);
