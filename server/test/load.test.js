// Load: 100 rooms of 4 bots (Showdown, 400 players). The server runs in its own process and the bots in two worker
// processes, so the bots' work does not count against the server. Reports the server's tick time (p50 / p99), how
// busy its event loop was, memory, and the bandwidth each player uses.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, fork } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { performance } from 'node:perf_hooks';
import { sleep, metric, stats } from './helpers/harness.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ROOMS = +(process.env.RM_LOAD_ROOMS || 100), PER = 4, N = ROOMS * PER, SECONDS = +(process.env.RM_LOAD_SECONDS || 10), WORKERS = 2;

function startServer() {
  const env = Object.assign({}, process.env, {
    PORT: '0', HOST: '127.0.0.1', PRINT_PORT: '1', LOG_LEVEL: 'info', DATA_FILE: 'memory', MAX_PER_IP: '5000', MAX_CONNECTIONS: '10000',
    RULES: JSON.stringify({ sdT: SECONDS + 40, countdown: 1, startLead: 0.2, layoutTimeout: 90, weather: false, items: true, afkForfeit: 120, idleForfeit: 300, reconnectWindow: 60 }),
  });
  const child = spawn(process.execPath, ['src/index.js'], { cwd: root, env, stdio: ['ignore', 'pipe', 'inherit'] });
  const warnings = [];
  const port = new Promise((resolve, reject) => {
    let buf = ''; child.stdout.on('data', d => { buf += d; const m = buf.match(/PORT=(\d+)/); if (m) resolve(+m[1]); for (const l of String(d).split('\n')) if (/"level":"(warn|error)"|"msg":"violation"/.test(l)) warnings.push(l); });
    child.on('exit', c => reject(new Error('server exited ' + c)));
  });
  return { child, port, warnings };
}
function startWorker() {
  const w = fork(path.join(root, 'test', 'helpers', 'loadworker.js'), [], { cwd: root, stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
  const waiters = [];
  w.on('message', m => { if (m.t === 'error') console.error('load worker:', m.message); const i = waiters.findIndex(x => x.t === m.t || m.t === 'error'); if (i >= 0) waiters.splice(i, 1)[0].res(m); });
  w.ask = (msg, reply) => new Promise(res => { waiters.push({ t: reply, res }); w.send(msg); });
  w.ready = new Promise(res => waiters.push({ t: 'ready', res }));
  return w;
}
const health = async (port, q = '') => (await fetch('http://127.0.0.1:' + port + '/health' + q)).json();

test('load: ' + ROOMS + ' rooms of ' + PER + ' bots', { timeout: 300000 }, async () => {
  const srv = startServer(), port = await srv.port, url = 'ws://127.0.0.1:' + port + '/ws';
  const workers = Array.from({ length: WORKERS }, startWorker);
  try {
    await Promise.all(workers.map(w => w.ready));
    const t0 = performance.now(), share = Math.ceil(ROOMS / WORKERS);
    const started = await Promise.all(workers.map((w, i) => w.ask({ t: 'setup', url, firstRoom: i * share, rooms: Math.max(0, Math.min(share, ROOMS - i * share)), per: PER, mode: 'ffa' }, 'started')));
    for (const s of started) assert.equal(s.t, 'started', JSON.stringify(s));
    metric('load.setup', Math.round(performance.now() - t0), 'ms', N + ' players connected, in rooms, maps agreed, matches started');
    const h0 = await health(port), m0 = await Promise.all(workers.map(w => w.ask({ t: 'mark' }, 'marked'))), c0 = performance.now();
    await sleep(SECONDS * 1000);
    const secs = (performance.now() - c0) / 1000;
    const h1 = await health(port, '?window=' + Math.round(SECONDS * 30));
    const rep = await Promise.all(workers.map(w => w.ask({ t: 'report' }, 'report')));
    const up = (rep.reduce((a, r) => a + r.bytesOut, 0) - m0.reduce((a, r) => a + r.bytesOut, 0)) / N / secs;
    const down = (h1.stats.bytesOut - h0.stats.bytesOut) / N / secs, frames = (h1.stats.framesOut - h0.stats.framesOut) / N / secs;
    const sr = stats(rep.flatMap(r => r.snapRates)), interp = stats(rep.flatMap(r => r.interp));
    const corrections = rep.reduce((a, r) => a + r.corrections, 0), kicked = rep.flatMap(r => r.kicked);
    metric('load.players', N, '', ROOMS + ' Showdown matches of ' + PER + ', bots in ' + WORKERS + ' processes');
    metric('load.tick.p50', h1.tick.p50, 'ms', 'server tick for all ' + ROOMS + ' matches (timers, snapshots), median, wall clock');
    metric('load.tick.p99', h1.tick.p99, 'ms', 'server tick, 99th percentile, wall clock (one tick is 33 ms; the bots share this 4-core machine)');
    metric('load.tick.cpuP50', h1.tick.cpuP50, 'ms', 'processor time of a tick, median');
    metric('load.tick.cpuP99', h1.tick.cpuP99, 'ms', 'processor time of a tick, 99th percentile');
    metric('load.cpu', +(h1.cpu * 100).toFixed(1), '%', 'server processor time, share of one core (all ' + N + ' players: checking every state, ticks, sockets)'); metric('load.elu', +(h1.elu * 100).toFixed(1), '%', 'server event loop busy (wall clock; includes waiting for a core when the machine is busy)');
    metric('load.mem', h1.memMB, 'MB', 'server memory (resident)');
    metric('load.down', Math.round(down), 'B/s', 'server to each player (WebSocket payload and framing)');
    metric('load.downIp', Math.round(down + frames * 40), 'B/s', 'server to each player with TCP/IP headers (about 40 bytes a packet)');
    metric('load.up', Math.round(up), 'B/s', 'each player to the server');
    const lowest = Math.min(...rep.flatMap(r => r.snapRates));
    metric('load.snapRate', +sr.p50.toFixed(1), '/s', 'snapshots each player received per second (median; lowest player ' + lowest + ')');
    metric('load.interpDelay', +interp.p50.toFixed(1), 'ms', 'interpolation delay the players settled on (median; local network)');
    metric('load.corrections', corrections, '', 'corrections across all ' + N + ' honest bots');
    const why = () => JSON.stringify(kicked) + '\n' + srv.warnings.slice(0, 12).join('\n');
    assert.equal(h1.matches, ROOMS); assert.equal(h1.players, N, 'nobody dropped or kicked: ' + why());
    assert.ok(h1.tick.cpuP99 < 33, 'a tick\'s own work fits in one tick (' + h1.tick.cpuP99 + ' ms)');
    assert.ok(h1.tick.p50 < 33, 'the median tick fits in one tick even on a shared machine (' + h1.tick.p50 + ' ms)');
    assert.ok(sr.p50 >= 27, 'snapshots keep flowing (' + sr.p50 + '/s)');
    assert.equal(corrections, 0, 'honest bots are never corrected: ' + JSON.stringify(rep.flatMap(r => r.events)) + '\n' + why());
  } finally {
    await Promise.all(workers.map(w => new Promise(res => { w.on('exit', res); try { w.send({ t: 'quit' }); } catch (e) { res(); } setTimeout(() => { w.kill(); res(); }, 3000); })));
    srv.child.kill('SIGTERM');
    await new Promise(r => { srv.child.on('exit', r); setTimeout(r, 5000); });
  }
});
