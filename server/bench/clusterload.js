// pn: load across several machines, all on this computer: a store machine and GAMES game machines (each its own
// process, as on Fly), a stand-in for Fly's proxy in front (test/helpers/flyproxy.js), and bots in BOTPROCS processes.
// The bots form rooms, so most guests start on another machine than their room and are moved there (fly-replay).
// Prints each machine's players, main-thread and worker CPU and tick, and the bots' snapshot rate and corrections.
// usage: node bench/clusterload.js [game machines 3] [rooms 300] [players a room 4] [seconds 20] [bot processes 3]
import { spawn, fork } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { flyProxy } from '../test/helpers/flyproxy.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [GAMES = 3, ROOMS = 300, PER = 4, SECONDS = 20, BOTPROCS = 3] = process.argv.slice(2).map(Number);
const KEY = 'clusterload-internal-key-0123', STORE_PORT = 18000 + Math.floor(Math.random() * 1000), MODE = PER === 2 ? 'duel' : 'ffa';
const RULES = JSON.stringify({ sdT: SECONDS + 90, matchT: SECONDS + 90, countdown: 1, startLead: 0.2, layoutTimeout: 120, weather: false, items: false, afkForfeit: 180, idleForfeit: 300, reconnectWindow: 60, rematchWindow: 5 });
const procs = [];
function machine(id, env) {
  const c = spawn(process.execPath, ['src/index.js'], { cwd: root, env: Object.assign({}, process.env, { PORT: '0', HOST: '127.0.0.1', PRINT_PORT: '1', LOG_LEVEL: 'warn', MAX_PER_IP: '100000', MAX_CONNECTIONS: '100000', RULES, SHARD_ID: id, FLY_REPLAY: '1', INTERNAL_KEY: KEY, MATCH_WORKERS: '1', DATA_FILE: 'memory' }, env), stdio: ['ignore', 'pipe', 'inherit'] });
  procs.push(c);
  return new Promise((res, rej) => { let b = ''; c.stdout.on('data', d => { b += d; const m = b.match(/PORT=(\d+)/); if (m) res({ id, port: +m[1] }); }); c.on('exit', code => rej(new Error(id + ' exited ' + code))); });
}
function botProc() {
  const w = fork(path.join(root, 'test', 'helpers', 'loadworker.js'), [], { cwd: root, stdio: ['ignore', 'inherit', 'inherit', 'ipc'] }); procs.push(w);
  const waiters = []; w.on('message', m => { if (m.t === 'error') console.error('bots:', m.message); const i = waiters.findIndex(x => x.t === m.t || m.t === 'error'); if (i >= 0) waiters.splice(i, 1)[0].res(m); });
  w.ask = (msg, reply) => new Promise(res => { waiters.push({ t: reply, res }); w.send(msg); }); w.ready = new Promise(res => waiters.push({ t: 'ready', res }));
  return w;
}
const health = async port => (await fetch('http://127.0.0.1:' + port + '/health')).json();
let proxy = null;
try {
  await machine('store', { INTERNAL_PORT: String(STORE_PORT), INTERNAL_HOST: '127.0.0.1' });
  const games = []; for (let i = 0; i < GAMES; i++) games.push(await machine('g' + i, { STORE_URL: 'http://127.0.0.1:' + STORE_PORT }));
  proxy = await flyProxy(games);
  const bots = Array.from({ length: BOTPROCS }, botProc); await Promise.all(bots.map(b => b.ready));
  const t0 = Date.now(), share = Math.ceil(ROOMS / BOTPROCS);
  const st = await Promise.all(bots.map((w, i) => w.ask({ t: 'setup', url: proxy.url, firstRoom: i * share, rooms: Math.max(0, Math.min(share, ROOMS - i * share)), per: PER, mode: MODE }, 'started')));
  if (st.some(s => s.t !== 'started')) throw new Error('setup failed');
  console.log(ROOMS * PER + ' players in ' + ROOMS + ' rooms of ' + PER + ' on ' + GAMES + ' machines, all playing after ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s; fly-replays: ' + proxy.stats.replays);
  for (const g of games) await health(g.port); // (start the CPU windows)
  await new Promise(r => setTimeout(r, SECONDS * 1000));
  for (const g of games) {
    const h = await health(g.port), w = h.workers && h.workers[0];
    console.log('  ' + g.id + ': ' + h.players + ' players, ' + h.matches + ' matches; main thread ' + (h.mainCpu * 100).toFixed(0) + '% of a core, worker ' + (w ? (w.cpu * 100).toFixed(0) : '-') + '%, worker tick p99 ' + (w && w.tick ? w.tick.p99.toFixed(1) : '-') + ' ms');
  }
  const rep = await Promise.all(bots.map(w => w.ask({ t: 'report' }, 'report')));
  const rates = rep.flatMap(r => r.snapRates).sort((a, b) => a - b), corr = rep.reduce((a, r) => a + r.corrections, 0), kicked = rep.flatMap(r => r.kicked);
  console.log('  snapshots a second per player: median ' + rates[rates.length >> 1] + ', lowest ' + rates[0] + '; corrections ' + corr + '; kicked ' + kicked.length);
  const why = {}; for (const r of rep) for (const w of r.why || []) why[w] = (why[w] || 0) + 1;
  console.log('  under 20 snapshots a second: ' + rates.filter(x => x < 20).length + ' players ' + JSON.stringify(rep.flatMap(r => r.zero || []).slice(0, 4)) + '; corrections by reason ' + JSON.stringify(why));
  for (const w of bots) w.send({ t: 'quit' });
  await new Promise(r => setTimeout(r, 500));
} catch (e) { console.error(e.stack || e.message); process.exitCode = 1; }
finally { if (proxy) await proxy.close(); for (const p of procs) try { p.kill('SIGTERM'); } catch (e) { /* gone */ } setTimeout(() => process.exit(), 1500); }
