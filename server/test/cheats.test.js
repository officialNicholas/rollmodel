// "No cheating": every kind of cheat attempt is refused, corrected, or gets the cheater kicked and flagged, and the
// server keeps running for everyone else.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { codec, PROTOCOL_VERSION } from '../client/rmnet.js';
import { G } from '../src/constants.js';
import { startServer, makeBots, until, sleep, matchOf, metric } from './helpers/harness.js';
import { flatLayout } from './helpers/layouts.js';

// the flat test stage plus a box right next to the first spawn
const stage = () => { const L = flatLayout(26.4); L.boxes.push([1, 3, -21.4, -19.4, 0, 1.0]); return L; };

async function duel(rules = {}) {
  const srv = await startServer(Object.assign({ matchT: 40, slamFirst: 0.2 }, rules));
  const [A, B] = makeBots(srv, 2, { behavior: 'script', layoutFor: stage, prefix: 'ch' });
  A.o.script = bot => { bot.input = { speedK: 0 }; }; B.o.script = bot => { bot.input = { speedK: 0 }; };
  await Promise.all([A, B].map(b => b.connect()));
  await A.net.queue('duel'); await B.net.queue('duel');
  await Promise.all([A, B].map(b => b.wait('start')));
  await until(() => A.net.serverNow() > A.startAt + 300 && B.net.serverNow() > B.startAt + 300);
  const m = matchOf(srv, A.id), pa = m.P[A.slot], pb = m.P[B.slot];
  return { srv, A, B, m, pa, pb, close: async () => { A.close(); B.close(); await srv.close(); } };
}

// a bare WebSocket client that can send anything at all
class Raw {
  constructor(url) {
    this.msgs = []; this.closed = null; this.ws = new WebSocket(url); this.ws.binaryType = 'arraybuffer';
    this.ws.onmessage = e => { if (typeof e.data === 'string') this.msgs.push(JSON.parse(e.data)); };
    this.ws.onclose = e => { this.closed = { code: e.code, reason: e.reason }; };
    this.opened = new Promise((res, rej) => { this.ws.onopen = res; this.ws.onerror = rej; });
  }
  send(o) { this.ws.send(typeof o === 'string' || o instanceof ArrayBuffer || ArrayBuffer.isView(o) ? o : JSON.stringify(o)); }
  wait(pred, ms = 5000) { return until(() => this.msgs.find(pred), ms); }
  async hello(extra = {}) { await this.opened; this.send(Object.assign({ t: 'hello', v: PROTOCOL_VERSION, name: 'Raw' }, extra)); return this.wait(m => m.t === 'welcome' || m.t === 'error'); }
}

test('speed hack: corrected every time, then kicked and flagged; the honest player wins by forfeit', async () => {
  const c = await duel();
  try {
    c.A.o.script = bot => { bot.input = { steer: 1, speedK: 1.6 }; };
    const kicked = c.A.wait('kicked', () => true, 20000), end = c.B.wait('matchEnd', () => true, 20000);
    const t0 = Date.now();
    assert.equal((await kicked).reason, 'cheating');
    metric('cheat.speedhack.kickedAfter', Date.now() - t0, 'ms', 'a 1.6x speed hack: corrected each time, kicked after this long');
    assert.ok(c.A.stats.corrections >= 3, 'corrected first (' + c.A.stats.corrections + ')');
    assert.ok(c.A.events.every(e => e[1] === 'speed'));
    const e = await end; assert.equal(e.reason, 'forfeit'); assert.equal(e.winner, c.pb.side);
    assert.equal(e.results.find(r => r.slot === c.A.slot).left, true);
    await sleep(50); const rec = await c.srv.store.get(c.A.id); assert.ok(rec.flags.some(f => f.reason === 'cheating'));
  } finally { await c.close(); }
});

test('teleport, standing inside a solid, and flying are corrected back to the last good spot', async () => {
  const c = await duel({ strikesToKick: 100 }); // (watch every correction here; kicking has its own test)
  try {
    const corr = () => c.A.wait('correction', () => true, 4000);
    // teleport 10 m
    let w = corr(); c.A.o.script = bot => { if (!bot.did) { bot.did = 1; bot.body.x += 10; } bot.input = { speedK: 0 }; };
    let m = await w; assert.equal(m.reason, 'teleport'); assert.ok(Math.abs(m.x - c.pa.spawn.x) < 1, 'back near the start');
    await sleep(300);
    // walk into the box next to the spawn (1..3, -21.4..-19.4)
    w = corr(); c.A.o.script = (bot, dt) => { bot.body.x += 5 * dt; bot.body.y = 0; bot.input = { speedK: 0 }; }; // walks right into it, ignoring the collision
    m = await w; assert.equal(m.reason, 'wall');
    await sleep(300);
    // fly straight up
    c.A.o.script = bot => { bot.input = { speedK: 0 }; }; await sleep(300); let fy = 0; w = corr(); c.A.o.cheat = st => Object.assign(st, { y: (fy = Math.min(4, fy + 0.04)) }); // reports rising into the air
    m = await w; assert.ok(m.reason === 'fly' || m.reason === 'float', m.reason); assert.ok(m.y < 0.6, 'put back on the floor');
    // the server never showed it anywhere it was not allowed to be
    const s = c.B.net.remote(c.A.slot); assert.ok(s.y < 0.6);
    assert.equal(c.pb.strikes, 0, 'the honest player has no strikes');
  } finally { await c.close(); }
});

test('pound during cooldown and pound without paint are refused', async () => {
  const c = await duel({ slamCd: 6 });
  try {
    const pound = async () => { c.A.body.pound(); const r = await c.A.net.action('pound'); await until(() => !c.A.body.slam, 3000); await sleep(100); return r; };
    assert.equal((await pound()).ok, true);
    await sleep(800);
    const again = await pound(); assert.equal(again.ok, false); assert.equal(again.reason, 'cooldown');
  } finally { await c.close(); }
  const d = await duel({ slamCd: 0.3 });
  try {
    // the cheater always claims a full tank; the server keeps its own meter
    d.A.o.script = bot => { bot.paint = 1; bot.input = { speedK: 0 }; };
    const results = [];
    for (let i = 0; i < 6; i++) { d.A.body.pound(); results.push(await d.A.net.action('pound')); await until(() => !d.A.body.slam, 3000); await sleep(150); }
    const firstNo = results.findIndex(r => !r.ok);
    assert.ok(firstNo >= 3 && firstNo <= 5, 'a few pounds, then out of paint (' + JSON.stringify(results.map(r => r.reason || 'ok')) + ')');
    assert.equal(results[firstNo].reason, 'no_paint');
    assert.ok(d.pa.paint < G.POUND_MIN);
  } finally { await d.close(); }
});

test('knock-outs, coverage and other players cannot be claimed or spoofed', async () => {
  const c = await duel();
  try {
    // a fake knock-out message: not a thing a client can send
    let err = c.A.wait('error', m => m.code === 'bad_message');
    c.A.net._sendJ({ t: 'ko', slot: c.B.slot, by: c.A.slot, reason: 'pound' }); await err;
    assert.equal((await c.A.net.action('ko', { target: c.B.slot })).reason, 'unknown');
    // claiming coverage
    const before = c.m.cov.colors()[c.A.slot];
    err = c.A.wait('error', m => m.code === 'bad_message');
    c.A.net._sendJ({ t: 'cov', s: [100, 0], c: [100, 0] }); await err;
    assert.equal((await c.A.net.action('paint', { x: 0, z: 0, r: 30 })).reason, 'unknown');
    assert.equal(c.m.cov.colors()[c.A.slot], before, 'coverage is only what the server painted');
    // acting as someone else: the id is ignored, the action is the sender's own
    const r = await c.A.net.action('selfKo', { reason: 'fall', id: c.B.id, slot: c.B.slot });
    assert.equal(r.ok, true);
    await sleep(100);
    assert.equal(c.pa.st, 'ko', 'the sender is the one knocked out'); assert.equal(c.pb.st, 'play', 'not the player it pretended to be');
    assert.equal(c.pb.deaths, 0);
  } finally { await c.close(); }
});

test('action times cannot be backdated past the sender\'s own measured delay', async () => {
  const c = await duel();
  try {
    const now = c.A.net.serverNow();
    assert.equal((await c.A.net.action('roll', { ts: now - 5000 })).ok, true);
    assert.ok(c.pa.rollStart > now - 300, 'a roll claimed 5 s ago is placed at most a moment back (' + (now - c.pa.rollStart).toFixed(0) + ' ms)');
    await sleep(1700);
    assert.equal((await c.A.net.action('roll', { ts: now + 60000 })).ok, true);
    assert.ok(c.pa.rollStart < c.A.net.serverNow() + 100, 'nor in the future');
  } finally { await c.close(); }
});

test('flooding gets you kicked; everyone else is fine', async () => {
  const srv = await startServer();
  try {
    const r = new Raw(srv.url); await r.hello();
    for (let i = 0; i < 600; i++) r.send({ t: 'cancelQueue' });
    await r.wait(m => m.t === 'kicked'); assert.equal(r.msgs.find(m => m.t === 'kicked').reason, 'flood');
    await until(() => r.closed, 3000); assert.equal(r.closed.code, 4003);
    const s = new Raw(srv.url); await s.hello();
    const st = new Uint8Array(codec.encodeState({ x: 0, y: 0, z: 0 }, 1, 1, 0));
    for (let i = 0; i < 1000; i++) s.send(st);
    await s.wait(m => m.t === 'kicked'); assert.equal(s.msgs.find(m => m.t === 'kicked').reason, 'flood');
    // a well-behaved client is unaffected
    const ok = new Raw(srv.url); const w = await ok.hello(); assert.equal(w.t, 'welcome');
    assert.equal(srv.health().ok, true);
  } finally { await srv.close(); }
});

test('oversized and malformed messages are refused without hurting the server', async () => {
  const srv = await startServer();
  try {
    const big = new Raw(srv.url); await big.hello();
    big.send('x'.repeat(100 * 1024)); // above the 64 KB cap: the socket is closed
    await until(() => big.closed, 3000); assert.equal(big.closed.code, 1009);
    const r = new Raw(srv.url); await r.hello();
    r.send(JSON.stringify({ t: 'queue', mode: 'duel', pad: 'y'.repeat(4000) })); await r.wait(m => m.t === 'error' && /large/.test(m.message));
    r.send('not json at all'); r.send('[1,2,3]'); r.send('{"t":42}'); r.send(JSON.stringify({ t: 'queue', mode: 'nope' }));
    r.send(new Uint8Array([0xff, 1, 2])); // unknown binary type
    const nan = new Uint8Array(codec.encodeState({ x: 0, y: 0, z: 0 }, 1, 1, 0)); new DataView(nan.buffer).setFloat32(12, NaN, true); r.send(nan);
    r.send(new Uint8Array(12)); // wrong size
    await r.wait(m => m.t === 'error' && m.code === 'bad_mode');
    assert.ok(r.msgs.filter(m => m.code === 'bad_message').length >= 3);
    for (let i = 0; i < 30; i++) r.send('garbage ' + i);
    await r.wait(m => m.t === 'kicked'); assert.equal(r.msgs.find(m => m.t === 'kicked').reason, 'protocol');
    assert.equal(srv.health().ok, true);
  } finally { await srv.close(); }
});

test('a client on the wrong protocol version is told and turned away', async () => {
  const srv = await startServer();
  try {
    const r = new Raw(srv.url); const m = await r.hello({ v: PROTOCOL_VERSION + 1 });
    assert.equal(m.t, 'error'); assert.equal(m.code, 'version'); assert.equal(m.fatal, true); assert.equal(m.server, PROTOCOL_VERSION);
    await until(() => r.closed, 3000); assert.equal(r.closed.code, 4000);
    // nothing works before a hello
    const n = new Raw(srv.url); await n.opened; n.send({ t: 'queue', mode: 'duel' }); await n.wait(x => x.t === 'error' && x.code === 'no_hello');
  } finally { await srv.close(); }
});

test('a private room cannot be joined without its code, and guessing is rate limited', async () => {
  const srv = await startServer();
  try {
    const host = new Raw(srv.url); await host.hello(); host.send({ t: 'createRoom', mode: 'duel', r: 1 });
    const room = await host.wait(m => m.t === 'room'); assert.match(room.code, /^[A-Z0-9]{5}$/);
    const g = new Raw(srv.url); await g.hello();
    const codes = ['AAAAA', 'BBBBB', 'CCCCC', 'DDDDD', 'EEEEE', 'FFFFF', 'GGGGG', 'HHHHH'].filter(x => x !== room.code);
    for (const [i, code] of codes.entries()) g.send({ t: 'joinRoom', code, r: 10 + i });
    await g.wait(m => m.r === 10 + codes.length - 1);
    const answers = g.msgs.filter(m => m.r >= 10).map(m => m.code);
    assert.equal(answers.filter(a => a === 'not_found').length, 6); assert.ok(answers.slice(6).every(a => a === 'rate'), JSON.stringify(answers));
    // and acting in a match you are not in does nothing
    g.send({ t: 'act', a: 'pound', n: 1 }); const ack = await g.wait(m => m.t === 'ack'); assert.equal(ack.reason, 'not_in_match');
  } finally { await srv.close(); }
});
