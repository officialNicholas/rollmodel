// A server spread over several machines (docs/net-scale.md): one keeps the player store and serves it to the others
// on the private network; Fly's proxy (here a stand-in, helpers/flyproxy.js) spreads new connections and follows a
// machine's fly-replay. Players sign in on any machine with the same account; a room is joined from any machine; a
// dropped connection gets back to the machine running its match; results land in the one store.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, makeBots, until, sleep } from './helpers/harness.js';
import { flyProxy } from './helpers/flyproxy.js';
import { MemoryStore } from '../src/store.js';
import { RMNet } from '../client/rmnet.js';

const KEY = 'test-internal-key-0123456789';
async function cluster(n = 3, rules = {}, extra = {}) {
  const home = await startServer(rules, Object.assign({ store: new MemoryStore(), shardId: 'm0', flyReplay: true, internalKey: KEY, internalPort: 0, internalHost: '127.0.0.1' }, extra));
  const url = 'http://127.0.0.1:' + home.internalPort, all = [home];
  for (let i = 1; i < n; i++) all.push(await startServer(rules, Object.assign({ store: null, storeUrl: url, internalKey: KEY, shardId: 'm' + i, flyReplay: true }, extra)));
  const proxy = await flyProxy(all.map(s => ({ id: s.shardId, port: s.port })));
  return { all, home, proxy, storeUrl: url, close: async () => { await proxy.close(); for (const s of all) await s.close(); } };
}

test('several machines, one store: the same account on any machine, its results saved once', async () => {
  const c = await cluster(3, { matchT: 3 });
  const bots = makeBots(c.home, 6, { url: c.proxy.url, behavior: 'wander', prefix: 'sh' });
  try {
    const w = await Promise.all(bots.map(b => b.connect()));
    assert.equal(new Set(w.map(x => x.shard)).size, 3, 'new connections spread over the three machines');
    // the same player on another machine: same account
    const p = bots[0], tok = p.token, other = c.all.find(s => s.shardId !== w[0].shard);
    const direct = new RMNet({ url: other.url, token: tok, autoReconnect: false });
    const again = await direct.connect(); assert.equal(again.id, p.id, 'signed in as the same player on ' + other.shardId); direct.close();
    // a queue match on one machine: the result reaches the shared store
    const pair = bots.filter((b, i) => w[i].shard === w[0].shard).slice(0, 2);
    if (pair.length === 2) {
      for (const b of pair) await b.net.queue('duel');
      const end = await pair[0].wait('matchEnd', () => true, 15000);
      await until(async () => true, 100);
      await sleep(300);
      const saved = await c.home.store.get(pair[0].id); assert.equal(saved.stats.matches, 1, 'saved in the one store');
      assert.equal(Math.round(saved.ratings.duel.r), end.results.find(r => r.id === pair[0].id).rating.after);
    }
  } finally { for (const b of bots) b.close(); await c.close(); }
});

test('a room on one machine, joined from another: the joiner is moved there quietly and they play', async () => {
  const c = await cluster(2, { matchT: 2.5 });
  let H = null, G = null;
  try {
    // two players on different machines
    H = makeBots(c.home, 1, { url: c.proxy.url, behavior: 'wander', prefix: 'host' })[0]; const wh = await H.connect();
    let wg = null;
    for (let i = 0; i < 6 && (!wg || wg.shard === wh.shard); i++) { if (G) G.close(); G = makeBots(c.home, 1, { url: c.proxy.url, behavior: 'wander', prefix: 'guest' })[0]; wg = await G.connect(); }
    assert.notEqual(wg.shard, wh.shard, 'the guest started on the other machine');
    let closes = 0; G.on('close', () => closes++);
    await assert.rejects(G.net.joinRoom('ZZZZZ'), e => e.code === 'not_found', 'a code nobody has');
    const code = await H.net.createRoom('duel');
    const joined = await G.net.joinRoom(code);
    assert.equal(joined.code, code); assert.equal(G.net._shard, wh.shard, 'moved to the room\'s machine');
    assert.equal(closes, 0, 'the game was never told the connection dropped');
    H.net.ready(true); G.net.ready(true);
    const end = await G.wait('matchEnd', () => true, 15000); assert.equal(end.results.length, 2);
  } finally { if (H) H.close(); if (G) G.close(); await c.close(); }
});

test('a dropped connection gets back to the machine running its match', async () => {
  const c = await cluster(3, { matchT: 10, reconnectWindow: 20 });
  const bots = makeBots(c.home, 2, { url: c.proxy.url, behavior: 'wander', prefix: 'rs' });
  try {
    const w = await Promise.all(bots.map(b => b.connect()));
    // both into one room on the first one's machine
    const code = await bots[0].net.createRoom('duel'); await bots[1].net.joinRoom(code);
    bots[0].net.ready(true); bots[1].net.ready(true);
    await Promise.all(bots.map(b => b.wait('start')));
    const shard = bots[1].net._shard; assert.equal(shard, w[0].shard);
    const resumed = bots[1].wait('resume', () => true, 10000);
    bots[1].net.ws.close(); // (dropped; the proxy alone would send a new connection anywhere)
    const r = await resumed; assert.equal(bots[1].net._shard, shard, 'back on the same machine'); assert.equal(r.you, bots[1].slot);
    const end = await bots[0].wait('matchEnd', () => true, 20000); assert.ok(end.results.every(x => !x.left));
  } finally { for (const b of bots) b.close(); await c.close(); }
});

test('room codes are unique across machines, and a store that cannot be reached is not fatal', async () => {
  const s = new MemoryStore();
  assert.equal(await s.claimRoom('ABCDE', 'm1'), true); assert.equal(await s.claimRoom('ABCDE', 'm2'), false);
  assert.equal(await s.findRoom('ABCDE'), 'm1'); await s.releaseRoom('ABCDE', 'm2'); assert.equal(await s.findRoom('ABCDE'), 'm1', 'only its own machine frees it');
  await s.releaseRoom('ABCDE', 'm1'); assert.equal(await s.findRoom('ABCDE'), null);
  // a machine whose store is down: the player is told to wait, and the phone keeps trying (not a fatal error)
  const lone = await startServer({}, { store: null, storeUrl: 'http://127.0.0.1:9', internalKey: KEY, shardId: 'mx' });
  const net = new RMNet({ url: lone.url, autoReconnect: false });
  try {
    const err = new Promise(res => net.on('error', res)); let fatal = false; net.on('fatal', () => { fatal = true; });
    net.connect().catch(() => {});
    const e = await err; assert.equal(e.code, 'busy'); await sleep(200); assert.equal(fatal, false);
  } finally { net.close(); await lone.close(); }
  // the store's API refuses anyone without the key; and a connection asking for a machine (?s=) is handed to it
  const c = await cluster(2);
  try {
    const px = await flyProxy(c.all.map(x => ({ id: x.shardId, port: x.port })), { first: true });
    const a = new RMNet({ url: px.url, autoReconnect: false }); assert.equal((await a.connect()).shard, 'm0', 'the proxy\'s pick'); a.close();
    const b = new RMNet({ url: px.url + '?s=m1', autoReconnect: false }); assert.equal((await b.connect()).shard, 'm1', 'handed to the machine asked for'); b.close();
    assert.equal(px.stats.replays, 1); await px.close();
    const r = await fetch(c.storeUrl + '/internal/store', { method: 'POST', body: JSON.stringify({ op: 'get', args: ['x'] }) }); assert.equal(r.status, 403);
    const r2 = await fetch(c.storeUrl + '/internal/store', { method: 'POST', headers: { 'x-rm-internal': KEY }, body: JSON.stringify({ op: 'players', args: [] }) }); assert.equal(r2.status, 400, 'only the store\'s own operations');
  } finally { await c.close(); }
});
