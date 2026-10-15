// Operations: /health, graceful shutdown, TCP_NODELAY, the hello timeout, per-address and origin limits, config from
// the environment, and structured logs.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { JsonFileStore } from '../src/store.js';
import { configFromEnv } from '../src/config.js';
import { createLogger } from '../src/log.js';
import { PROTOCOL_VERSION } from '../client/rmnet.js';
import { startServer, makeBots, until, sleep } from './helpers/harness.js';

const httpGet = async (port, p) => { const r = await fetch('http://127.0.0.1:' + port + p); return { status: r.status, body: await r.json().catch(() => null) }; };
// a raw WebSocket upgrade; returns the HTTP status (and keeps the socket open when hold is set)
const held = [];
const upgradeStatus = (port, headers = {}, hold = false) => new Promise(resolve => {
  const s = net.connect(port, '127.0.0.1', () => s.write('GET /ws HTTP/1.1\r\nHost: x\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n' + Object.entries(headers).map(([k, v]) => k + ': ' + v + '\r\n').join('') + '\r\n'));
  let buf = ''; s.on('data', d => { buf += d; const m = buf.match(/^HTTP\/1\.1 (\d+)/); if (m) { resolve(+m[1]); if (hold) held.push(s); else s.destroy(); } }); s.on('error', () => resolve(0));
});

test('/health reports the server state', async () => {
  const srv = await startServer();
  try {
    const h = await httpGet(srv.port, '/health');
    assert.equal(h.status, 200); assert.equal(h.body.ok, true); assert.equal(h.body.proto, PROTOCOL_VERSION);
    for (const k of ['connections', 'players', 'matches', 'queues', 'tick', 'elu', 'memMB', 'stats']) assert.ok(k in h.body, k);
    assert.equal((await httpGet(srv.port, '/health?window=30')).body.tick.n <= 30, true);
    assert.equal((await fetch('http://127.0.0.1:' + srv.port + '/nope')).status, 404);
  } finally { await srv.close(); }
});

test('graceful shutdown: matches are called off, everyone is told, the store is saved', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'rmshut-')), file = path.join(dir, 'store.json');
  const srv = await startServer({ matchT: 60 }, { store: new JsonFileStore(file, { delayMs: 10000 }) }); // a long write delay: only the shutdown flush saves it
  const bots = makeBots(srv, 2, { behavior: 'wander', autoReconnect: false });
  try {
    await Promise.all(bots.map(b => b.connect()));
    for (const b of bots) await b.net.queue('duel');
    await Promise.all(bots.map(b => b.wait('start')));
    const told = bots.map(b => b.wait('server', m => m.msg === 'shutdown')), off = bots.map(b => b.wait('matchCancelled')), closed = bots.map(b => b.wait('close'));
    await srv.close();
    assert.ok((await Promise.all(off)).every(m => m.reason === 'server_shutdown'));
    await Promise.all(told);
    assert.ok((await Promise.all(closed)).every(c => c.code === 1001));
    const saved = JSON.parse(readFileSync(file, 'utf8')); assert.equal(saved.players.length, 2);
    assert.equal(await upgradeStatus(srv.port).catch(() => 0), 0, 'no longer listening');
  } finally { for (const b of bots) b.close(); }
});

test('TCP_NODELAY is on for every game connection', async () => {
  const seen = []; const orig = net.Socket.prototype.setNoDelay;
  net.Socket.prototype.setNoDelay = function (on) { seen.push(on === undefined ? true : on); return orig.call(this, on); };
  const srv = await startServer();
  try {
    const before = seen.length;
    const [b] = makeBots(srv, 1); await b.connect();
    assert.ok(seen.length > before && seen.slice(before).every(v => v === true), 'setNoDelay(true) on the socket');
    b.close();
  } finally { net.Socket.prototype.setNoDelay = orig; await srv.close(); }
});

test('a connection that never says hello is closed; limits per address and by origin', async () => {
  const srv = await startServer({}, { maxPerIp: 3, allowedOrigins: ['rollmodel://localhost', 'https://rollmodel.example'] });
  try {
    const ws = new WebSocket(srv.url); let code = null; ws.onclose = e => { code = e.code; };
    await until(() => code !== null, 7000); assert.equal(code, 4004);
    assert.equal(await upgradeStatus(srv.port, { Origin: 'https://evil.example' }), 403);
    assert.equal(await upgradeStatus(srv.port, { Origin: 'rollmodel://localhost' }), 101, 'the iOS app page');
    assert.equal(await upgradeStatus(srv.port), 101, 'no origin (a native client)');
    await sleep(50);
    const got = []; for (let i = 0; i < 4; i++) got.push(await upgradeStatus(srv.port, {}, true));
    assert.deepEqual(got, [101, 101, 101, 429], 'three connections from one address, then no more');
  } finally { for (const s of held.splice(0)) s.destroy(); await srv.close(); }
});

test('settings come from the environment; logs are one JSON object per line', () => {
  const c = configFromEnv({ PORT: '9001', HOST: '127.0.0.1', DATA_FILE: 'memory', LOG_LEVEL: 'warn', ALLOWED_ORIGINS: 'rollmodel://localhost, https://a.example', MAX_PER_IP: '7', SNAPSHOT_HZ: '20', RULES: '{"matchT":60}' });
  assert.equal(c.port, 9001); assert.equal(c.host, '127.0.0.1'); assert.deepEqual(c.allowedOrigins, ['rollmodel://localhost', 'https://a.example']);
  assert.equal(c.maxPerIp, 7); assert.equal(c.rules.matchT, 60); assert.equal(c.rules.snapshotHz, 20); assert.equal(c.logLevel, 'warn');
  assert.equal(configFromEnv({ PORT: 'abc' }).port, 8080);
  assert.throws(() => configFromEnv({ RULES: '{bad' }));
  const recs = []; const log = createLogger({ level: 'info', base: { svc: 't' }, sink: r => recs.push(r) });
  log.debug('hidden'); log.info('hello', { a: 1 }); log.child({ match: 'm1' }).warn('careful');
  assert.equal(recs.length, 2); assert.equal(recs[0].msg, 'hello'); assert.equal(recs[0].a, 1); assert.equal(recs[1].match, 'm1'); assert.ok(recs[0].ts && recs[0].level === 'info' && recs[0].svc === 't');
});
