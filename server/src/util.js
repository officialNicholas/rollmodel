import { randomBytes, createHash, randomInt } from 'node:crypto';
import { performance } from 'node:perf_hooks';
import { isMainThread, workerData } from 'node:worker_threads';

export const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
export const fin = v => typeof v === 'number' && Number.isFinite(v);
// one clock for the whole process: a match worker thread counts from the main thread's start, not its own, so every time
// a client sees (pongs from the main thread, snapshots from a worker) is on the same clock
const CLOCK_BASE = !isMainThread && workerData && Number.isFinite(workerData.timeOrigin) ? performance.timeOrigin - workerData.timeOrigin : 0;
export const nowMs = () => performance.now() + CLOCK_BASE;

// the game's own seeded generator (mulberry32), so a seed means the same thing on both sides
export const rng = a => () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

const B32 = 'abcdefghijkmnpqrstuvwxyz23456789';
export function randomId(prefix, n = 12) { const b = randomBytes(n); let s = prefix; for (let i = 0; i < n; i++) s += B32[b[i] & 31]; return s; }
export const newToken = () => randomBytes(24).toString('base64url');
export const tokenKey = t => createHash('sha256').update(String(t)).digest('base64url');
// private room codes: 5 characters without look-alikes (no 0/O, 1/I/L)
export const CODE_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
export function roomCode() { let s = ''; for (let i = 0; i < 5; i++) s += CODE_ALPHABET[randomInt(CODE_ALPHABET.length)]; return s; }
export const seed32 = () => randomBytes(4).readUInt32LE(0);

export function percentile(sorted, p) {
  if (!sorted.length) return 0;
  const i = Math.min(sorted.length - 1, Math.max(0, Math.ceil(p / 100 * sorted.length) - 1));
  return sorted[i];
}
export function summarize(values) {
  const s = Float64Array.from(values).sort();
  let sum = 0; for (const v of s) sum += v;
  return { n: s.length, mean: s.length ? sum / s.length : 0, p50: percentile(s, 50), p95: percentile(s, 95), p99: percentile(s, 99), max: s.length ? s[s.length - 1] : 0 };
}

// fixed-size window of recent samples for percentiles (tick times and the like)
export class Window {
  constructor(n = 2048) { this.a = new Float64Array(n); this.n = 0; this.i = 0; }
  push(v) { this.a[this.i] = v; this.i = (this.i + 1) % this.a.length; if (this.n < this.a.length) this.n++; }
  values() { return Array.from(this.a.subarray(0, this.n)); }
  summary() { return summarize(this.values()); }
}

// a leaky "min" tracker: drops at once to a new low, creeps back up slowly (for one-way delay estimates)
export class LeakyMin {
  constructor(risePerSec = 20) { this.v = null; this.rise = risePerSec; this.t = 0; }
  add(x, tMs) {
    if (this.v === null) { this.v = x; this.t = tMs; return this.v; }
    const dt = Math.max(0, tMs - this.t) / 1000; this.t = tMs;
    this.v = Math.min(x, this.v + this.rise * dt);
    return this.v;
  }
}
