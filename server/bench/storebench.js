// pn: how long the player store holds up the main thread while a busy server keeps changing it. N players on file,
// CHANGES a second for SECONDS, the longest stall of the event loop measured throughout.
// usage: node bench/storebench.js [players] [changes a second] [seconds] [old]
//   ('old': the store before the journal; first: git show 33d9f9e:server/src/store.js > bench/_oldstore.mjs, with its
//   imports pointed at ../src/)
import { monitorEventLoopDelay } from 'node:perf_hooks';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const [N = 50000, RATE = 20, SECONDS = 6] = process.argv.slice(2, 5).map(Number), OLD = process.argv[5] === 'old';
const { JsonFileStore } = await import(OLD ? './_oldstore.mjs' : '../src/store.js');
const file = path.join(mkdtempSync(path.join(tmpdir(), 'rmsb-')), 'store.json');
const s = new JsonFileStore(file); await s.init();
const ids = []; for (let i = 0; i < N; i++) ids.push((await s.create({ name: 'P' + i, look: { c: 'red', e: 'round', r: 12, w: { head: 'tophat' } } })).player.id);
await s.flush(); if (s._compacting) await s._compacting;
const h = monitorEventLoopDelay({ resolution: 5 }); h.enable();
const t0 = Date.now(); let k = 0;
await new Promise(res => { const iv = setInterval(() => { s.update(ids[(k++ * 7919) % N], { lastSeen: Date.now() }); if (Date.now() - t0 > SECONDS * 1000) { clearInterval(iv); res(); } }, 1000 / RATE); });
h.disable();
console.log((OLD ? 'before' : 'after ') + ': ' + N + ' players, ' + RATE + ' changes/s: event loop stalls p99 ' + (h.percentile(99) / 1e6).toFixed(1) + ' ms, worst ' + (h.max / 1e6).toFixed(1) + ' ms');
process.exit(0);
