// Test plumbing: a server on a random local port with short-match rules, bots, waiting, and the metrics file the
// final summary is printed from.
import { appendFileSync } from 'node:fs';
import { createGameServer } from '../../src/server.js';
import { MemoryStore } from '../../src/store.js';
import { createLogger } from '../../src/log.js';
import { Bot } from './bot.js';
import { netSim, PROFILES } from './netsim.js';

export const FAST_RULES = { matchT: 8, sdT: 25, countdown: 0.6, startLead: 0.1, layoutTimeout: 5, rematchWindow: 4, weather: false, items: false, slamFirst: 0.5, reconnectWindow: 3, afkWarn: 1.5, afkForfeit: 4, idleForfeit: 30, overtime: 0 };

export async function startServer(rules = {}, extra = {}) {
  const srv = await createGameServer(Object.assign({ port: 0, host: '127.0.0.1', store: new MemoryStore(), log: createLogger({ level: process.env.RM_LOG || 'silent' }), rules: Object.assign({}, FAST_RULES, rules), maxPerIp: 2000, maxConnections: 5000, shutdownGraceMs: 200 }, extra));
  srv.url = 'ws://127.0.0.1:' + srv.port + '/ws';
  return srv;
}

export function makeBots(srv, n, opts = {}) {
  const ws = opts.profile ? netSim(PROFILES[opts.profile] || opts.profile) : opts.WebSocket;
  return Array.from({ length: n }, (_, i) => new Bot(Object.assign({ url: srv.url, WebSocket: ws, name: (opts.prefix || 'Bot') + (i + 1) }, opts, { WebSocket: ws })));
}

export const sleep = ms => new Promise(r => setTimeout(r, ms));
export async function until(fn, ms = 10000, step = 20) {
  const t0 = Date.now();
  for (;;) { const v = fn(); if (v) return v; if (Date.now() - t0 > ms) throw new Error('condition not met in ' + ms + ' ms'); await sleep(step); }
}
// the server's match for a player
export const matchOf = (srv, id) => srv.inMatch.get(id) || [...srv.matches].find(m => m.P.some(p => p.id === id)) || null;

// key numbers for the summary printed at the end of `npm test`
export function metric(key, value, unit = '', note = '') {
  const f = process.env.RM_METRICS_FILE; if (!f) return;
  appendFileSync(f, JSON.stringify({ key, value, unit, note }) + '\n');
}
export function stats(arr) {
  const s = Float64Array.from(arr).sort(), n = s.length, at = p => (n ? s[Math.min(n - 1, Math.max(0, Math.ceil(p / 100 * n) - 1))] : 0);
  let sum = 0; for (const v of s) sum += v;
  return { n, mean: n ? sum / n : 0, p50: at(50), p95: at(95), p99: at(99), max: n ? s[n - 1] : 0 };
}
