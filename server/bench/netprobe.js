// pn: the network probe. A local server and two bots (the SDK plus a body that moves like the game) play duels over a
// simulated link, and this prints what a player would feel:
//   round trip, how far in the past the rival is drawn, how far that is from where the rival really was, how often the
//   rival had to be extrapolated or froze, corrections of your own blob (count and size), and messages and bytes per
//   second each way.
// Then the dropped connection: a clean close, and a link that goes silent without closing (a phone in a tunnel, Wi-Fi
// handing over to 4G), timing when each side notices and when play resumes.
//
// TCP never loses a message, so "loss" here is what TCP turns it into: the lost segment and everything after it wait
// for a retransmission (about one round trip plus the 200 ms minimum timer).
//
// usage: node bench/netprobe.js [profiles] [seconds]   e.g. node bench/netprobe.js lan,rtt120,loss2 8
//        node bench/netprobe.js drop
import { performance } from 'node:perf_hooks';
import { startServer, makeBots, until, sleep, stats, matchOf } from '../test/helpers/harness.js';
import { Link } from '../test/helpers/netsim.js';

// a link that can also lose messages (as TCP delays them) and go silent
class LossyLink extends Link {
  constructor(cfg, seed) { super(cfg, seed); this.loss = cfg.loss || 0; this.rto = cfg.rto || 200; this.silent = false; this.losses = 0; }
  arrival(size, now = performance.now()) {
    let at = super.arrival(size, now);
    if (this.loss && this.R() < this.loss) { at += this.rto + 2 * this.c.latency; this.losses++; this.lastAt = at; }
    return at;
  }
}
function lossySim({ up = {}, down = {} } = {}) {
  let seq = 1;
  const Cls = class LossyWebSocket {
    constructor(url) {
      this.url = url; this.readyState = 0; this.binaryType = 'arraybuffer'; this.onopen = this.onmessage = this.onclose = this.onerror = null;
      this.up = new LossyLink(up, seq++ * 7919); this.down = new LossyLink(down, seq++ * 104729);
      this.count = { in: 0, out: 0, bin: 0, binOut: 0, json: 0, jsonOut: 0, bytesIn: 0, bytesOut: 0 }; Cls.all.push(this);
      const ws = this._ws = new globalThis.WebSocket(url); ws.binaryType = 'arraybuffer';
      ws.onopen = () => this.down.deliver(0, () => { if (this.readyState === 0) { this.readyState = 1; this.onopen && this.onopen({ type: 'open' }); } });
      ws.onmessage = ev => {
        if (this.down.silent) return;
        const d = ev.data, s = typeof d === 'string', n = s ? d.length : d.byteLength;
        this.down.deliver(n, () => { if (this.readyState !== 1 && this.readyState !== 2) return; const c = this.count; c.in++; c.bytesIn += n; if (s) c.json++; else c.bin++; this.onmessage && this.onmessage({ data: d }); });
      };
      ws.onclose = ev => { const e = { code: ev.code, reason: ev.reason }; this.down.deliver(0, () => { this.readyState = 3; this.onclose && this.onclose(e); }); };
      ws.onerror = ev => { this.onerror && this.onerror(ev); };
    }
    get bufferedAmount() { return this._ws.bufferedAmount; }
    send(data) {
      if (this.readyState !== 1) throw new Error('not open');
      if (this.up.silent) return;
      const s = typeof data === 'string', n = s ? data.length : data.byteLength, c = this.count; c.out++; c.bytesOut += n; if (s) c.jsonOut++; else c.binOut++;
      this.up.deliver(n, () => { if (this._ws.readyState === 1) this._ws.send(data); });
    }
    close(code, reason) { if (this.readyState >= 2) return; this.readyState = 2; this.up.deliver(0, () => { try { this._ws.close(code, reason); } catch (e) { /* closing */ } }); }
    kill() { try { this._ws.close(); } catch (e) { /* gone */ } }
    // the link goes dead both ways, but nobody closes it
    blackhole() { this.up.silent = true; this.down.silent = true; }
  };
  Cls.all = [];
  return Cls;
}

const L = (lat, jit = 0, extra = {}) => Object.assign({ latency: lat, jitter: jit }, extra);
const both = o => ({ up: o, down: o });
export const NET = {
  lan: both(L(1)),
  rtt60: both(L(30, 5)),
  rtt120: both(L(60, 15)),
  rtt200: both(L(100, 20)),
  jitter: both(L(40, 35)), // 80 ms round trip, +/- 70 ms
  mobile: both(L(60, 20, { spikeEvery: 4000, spikeMs: [120, 250] })),
  loss1: both(L(40, 10, { loss: 0.01 })),
  loss3: both(L(40, 10, { loss: 0.03 })),
  bad: both(L(70, 30, { loss: 0.02, spikeEvery: 5000, spikeMs: [150, 400] })), // a poor 4G cell
};

function clientTimeAt(p, R) {
  const h = p.vhist; if (h.length < 2) return null;
  let lo = 0, hi = h.length - 1;
  if (R <= h[0].tau || R >= h[hi].tau) return null;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (h[m].tau <= R) lo = m; else hi = m; }
  const a = h[lo], b = h[hi]; return a.tc + (b.tc - a.tc) * (R - a.tau) / (b.tau - a.tau);
}

async function duel(name, seconds) {
  const srv = await startServer({ matchT: seconds + 6 });
  const WS = lossySim(NET[name]);
  const bots = makeBots(srv, 2, { WebSocket: WS, behavior: 'wander', record: true, prefix: name });
  const corr = [];
  for (const b of bots) b.on('correction', m => { const t = b.trace, n = t.length; corr.push(n >= 4 ? Math.hypot(t[n - 3] - m.x, t[n - 1] - m.z) : 0); if (process.env.WHY) console.log('  correction', m.reason, (corr[corr.length - 1] * 100).toFixed(0) + ' cm'); }); // (the trace's last frame: where it was before the correction)
  try {
    await Promise.all(bots.map(b => b.connect()));
    await sleep(2500);
    for (const b of bots) await b.net.queue('duel');
    const starts = await Promise.all(bots.map(b => b.wait('start')));
    const startAt = starts[0].startAt;
    await until(() => performance.now() > startAt + 1500, 20000);
    const m = matchOf(srv, bots[0].id), errs = [], late = [];
    let extrap = 0, held = 0, samples = 0, frozen = 0, frozenMax = 0, lastPos = null, lastMoveT = performance.now();
    // pops: the drawn rival moving further in one frame than anyone can (a leap back after a stall), raw and as drawn
    const pop = { raw: { n: 0, max: 0, prev: null }, drawn: { n: 0, max: 0, prev: null } }, errsDrawn = [];
    const popAt = (P, r, now) => { if (P.prev) { const dt = (now - P.prev.t) / 1000, d = Math.hypot(r.x - P.prev.x, r.z - P.prev.z), ex = d - (0.04 + 16 * dt); if (ex > 0.1 && d < 5) { P.n++; P.max = Math.max(P.max, ex); } } P.prev = { x: r.x, z: r.z, t: now }; };
    const c0 = WS.all.map(w => Object.assign({}, w.count)), t0 = performance.now(), corr0 = corr.length;
    const t1 = t0 + seconds * 1000;
    while (performance.now() < t1) {
      const now = performance.now(), obs = bots[0], o = bots[1], R = obs.net.renderTime(), r = obs.net.remote(o.slot, R), rd = obs.net.remote(o.slot);
      if (r && !o.dead && o.hidden < 0) {
        popAt(pop.raw, r, now); popAt(pop.drawn, rd, now);
        samples++; if (r.extrapolated) extrap++; if (r.held) held++;
        // the rival looks stuck: it should be moving (it always is, wandering) but the drawn position has not changed
        if (lastPos && Math.hypot(r.x - lastPos.x, r.z - lastPos.z) < 1e-4) { frozen = now - lastMoveT; frozenMax = Math.max(frozenMax, frozen); } else lastMoveT = now;
        lastPos = { x: r.x, z: r.z };
        const p = m.P[o.slot], tc = clientTimeAt(p, R);
        if (tc !== null) { const real = tc - o.net._clock.offset, truth = o.truthAt(real); if (truth && Math.abs(truth.y - r.y) < 3) { errs.push(Math.hypot(r.x - truth.x, r.z - truth.z)); errsDrawn.push(Math.hypot(rd.x - truth.x, rd.z - truth.z)); late.push(now - real); } }
      } else { lastPos = null; lastMoveT = now; pop.raw.prev = pop.drawn.prev = null; }
      await sleep(16);
    }
    const dt = (performance.now() - t0) / 1000, w = WS.all[0], c = w.count, a = c0[0];
    const st = bots[0].net.stats(), e = stats(errs), lt = stats(late);
    return {
      name, rtt: st.rtt, jitter: st.jitter, interpDelay: st.interpDelay, visual: lt.p50, errP50: e.p50 * 100, errP95: e.p95 * 100, errMax: e.max * 100,
      extrap: 100 * extrap / Math.max(1, samples), held: 100 * held / Math.max(1, samples), frozenMax,
      corrections: corr.length - corr0, corrPerMin: (corr.length - corr0) / dt * 60, corrSize: stats(corr.slice(corr0)),
      msgsIn: (c.in - a.in) / dt, msgsOut: (c.out - a.out) / dt, bytesIn: (c.bytesIn - a.bytesIn) / dt, bytesOut: (c.bytesOut - a.bytesOut) / dt,
      jsonIn: (c.json - a.json) / dt, losses: w.up.losses + w.down.losses, n: e.n, pop, ed: stats(errsDrawn),
    };
  } finally { for (const b of bots) b.close(); await srv.close(); }
}

// a player's connection drops mid-match: once closed cleanly, once gone silent. When does each side know, and when is
// play back?
async function drop(kind) {
  const srv = await startServer({ matchT: 40, reconnectWindow: 20, afkWarn: 5, afkForfeit: 15 });
  const WS = lossySim(NET.rtt60);
  const bots = makeBots(srv, 2, { WebSocket: WS, behavior: 'wander', prefix: 'drop' });
  const out = { kind };
  try {
    await Promise.all(bots.map(b => b.connect()));
    await sleep(1500);
    for (const b of bots) await b.net.queue('duel');
    await Promise.all(bots.map(b => b.wait('start')));
    await sleep(2500);
    const [A, B] = bots, m = matchOf(srv, A.id), pA = m.P[A.slot], t0 = performance.now(), T = () => Math.round(performance.now() - t0);
    const seen = {};
    A.on('close', () => { seen.clientClose ??= T(); });
    A.on('resume', () => { seen.resumed ??= T(); });
    B.on('playerAway', x => { if (x.slot === A.slot) seen.rivalToldAway ??= T(); });
    B.on('afk', x => { if (x.slot === A.slot && x.on) seen.rivalSawAfk ??= T(); });
    B.on('matchEnd', x => { seen.matchEnded ??= T() + ' (' + (x.reason || '') + ')'; });
    const iv = setInterval(() => { if (!pA.connected) seen.serverNoticed ??= T(); const r = B.net.remote(A.slot); if (r && r.held) seen.rivalHeld ??= T(); }, 10);
    const ws = A.net.ws;
    if (kind === 'close') ws.kill(); else ws.blackhole();
    try { await until(() => seen.resumed !== undefined || seen.matchEnded !== undefined, 30000, 50); } catch (e) { seen.timeout = T(); }
    clearInterval(iv);
    Object.assign(out, seen);
  } finally { for (const b of bots) b.close(); await srv.close(); }
  return out;
}

const f1 = v => (typeof v === 'number' ? v.toFixed(1) : v);
const args = process.argv.slice(2), which = (args[0] || 'lan,rtt60,rtt120,rtt200,jitter,mobile,loss1,loss3,bad').split(','), secs = +(args[1] || 8);
for (const w of which) {
  if (w === 'drop') { for (const k of ['close', 'silent']) console.log('drop/' + k, JSON.stringify(await drop(k))); continue; }
  const r = await duel(w, secs);
  console.log([r.name.padEnd(7), 'rtt', f1(r.rtt), 'jit', f1(r.jitter), '| interp', f1(r.interpDelay), 'drawn', f1(r.visual), 'ms behind | err p50/p95/max', f1(r.errP50), f1(r.errP95), f1(r.errMax), 'cm | extrap', f1(r.extrap) + '%', 'held', f1(r.held) + '%', '| pops raw', r.pop.raw.n, 'max', f1(r.pop.raw.max * 100), 'cm, drawn', r.pop.drawn.n, 'max', f1(r.pop.drawn.max * 100), 'cm (drawn err p95/max', f1(r.ed.p95 * 100), f1(r.ed.max * 100), ') | corr', r.corrections, '(' + f1(r.corrPerMin) + '/min, size p50 ' + f1(r.corrSize.p50 * 100) + ' cm max ' + f1(r.corrSize.max * 100) + ')',
    '| in', f1(r.msgsIn), 'msg/s', Math.round(r.bytesIn), 'B/s (json', f1(r.jsonIn) + '/s) out', f1(r.msgsOut), 'msg/s', Math.round(r.bytesOut), 'B/s | lost', r.losses].join(' '));
}
process.exit(0);
