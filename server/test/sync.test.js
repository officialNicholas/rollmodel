// "No lagging": the shared clock, a start everyone sees at the same moment, the snapshot rate, and how close the
// interpolated remote players are to where they really were, on a 120 ms (+/- 30 ms) network and on a mobile one with
// delay spikes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { performance } from 'node:perf_hooks';
import { startServer, makeBots, until, sleep, metric, stats, matchOf } from './helpers/harness.js';
import { PROFILES } from './helpers/netsim.js';

// the server-timeline time R maps to the client's own clock through the server's record of that player's states
function clientTimeAt(p, R) {
  const h = p.vhist; if (h.length < 2) return null;
  let lo = 0, hi = h.length - 1;
  if (R <= h[0].tau || R >= h[hi].tau) return null;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (h[m].tau <= R) lo = m; else hi = m; }
  const a = h[lo], b = h[hi]; return a.tc + (b.tc - a.tc) * (R - a.tau) / (b.tau - a.tau);
}

async function measure(profile, label, { seconds = 6, players = 4 } = {}) {
  const srv = await startServer({ matchT: seconds + 4, sdT: seconds + 4 });
  const mode = players === 2 ? 'duel' : 'ffa';
  const bots = makeBots(srv, players, { profile, behavior: 'wander', record: true, prefix: label });
  bots[0].o.behavior = 'still'; // the observer stands still; everyone else moves (and jumps, rolls, flings)
  try {
    await Promise.all(bots.map(b => b.connect()));
    await sleep(3000); // a few seconds in the lobby: pings for the clock
    for (const b of bots) await b.net.queue(mode);
    const starts = await Promise.all(bots.map(b => b.wait('start')));
    const startAt = starts[0].startAt;
    // when does each client think the countdown ends? (same process, so true server time is our own clock)
    const startErr = bots.map(b => (startAt - b.net._clock.offset) - startAt);
    const offsets = bots.map(b => b.net._clock.offset);
    await until(() => performance.now() > startAt + 1500, 15000);
    const m = matchOf(srv, bots[0].id), obs = bots[0], errs = [], lateness = [];
    let extrap = 0, samples = 0, snaps0 = obs.net._st.snapshots; const tSnap0 = performance.now();
    const t1 = performance.now() + seconds * 1000;
    while (performance.now() < t1) {
      const R = obs.net.renderTime();
      for (const b of bots.slice(1)) {
        const r = obs.net.remote(b.slot, R); if (!r || b.dead || b.hidden >= 0) continue;
        const p = m.P[b.slot], tc = clientTimeAt(p, R); if (tc === null) continue;
        const real = tc - b.net._clock.offset, truth = b.truthAt(real); if (!truth) continue;
        if (Math.abs(truth.y - r.y) > 3) continue; // a respawn in between
        errs.push(Math.hypot(r.x - truth.x, r.z - truth.z)); lateness.push(performance.now() - real);
        samples++; if (r.extrapolated) extrap++;
      }
      await sleep(16);
    }
    const snapRate = (obs.net._st.snapshots - snaps0) / ((performance.now() - tSnap0) / 1000);
    const st = obs.net.stats(), e = stats(errs), late = stats(lateness);
    const corrections = bots.reduce((a, b) => a + b.stats.corrections, 0);
    return { startErr, offsets, snapRate, e, late, extrapShare: extrap / Math.max(1, samples), st, corrections, srv, bots };
  } catch (err) { for (const b of bots) b.close(); await srv.close(); throw err; }
}
const cleanup = async r => { for (const b of r.bots) b.close(); await r.srv.close(); };

test('120 ms round trip (+/- 30 ms): synced start, 30 snapshots a second, small interpolation error', async () => {
  const r = await measure('rtt120', 'r120');
  try {
    const spread = Math.max(...r.startErr) - Math.min(...r.startErr), worst = Math.max(...r.startErr.map(Math.abs));
    metric('sync.rtt120.startSpread', +spread.toFixed(2), 'ms', 'spread of the moment 4 clients start the match');
    metric('sync.rtt120.startError', +worst.toFixed(2), 'ms', 'worst start error against the true server time');
    metric('sync.rtt120.snapshotRate', +r.snapRate.toFixed(1), '/s', 'snapshots received per second');
    metric('sync.rtt120.interp.p50', +(r.e.p50 * 100).toFixed(1), 'cm', 'interpolated remote position vs truth, median');
    metric('sync.rtt120.interp.p95', +(r.e.p95 * 100).toFixed(1), 'cm', 'interpolated remote position vs truth, 95th percentile');
    metric('sync.rtt120.interp.max', +(r.e.max * 100).toFixed(1), 'cm', 'interpolated remote position vs truth, worst');
    metric('sync.rtt120.interpDelay', +r.st.interpDelay.toFixed(1), 'ms', 'adaptive interpolation delay');
    metric('sync.rtt120.visualDelay', +r.late.p50.toFixed(1), 'ms', 'how far in the past remote players are drawn (median)');
    metric('sync.rtt120.extrapolated', +(r.extrapShare * 100).toFixed(2), '%', 'share of samples that had to extrapolate');
    metric('sync.rtt120.rtt', +r.st.rtt.toFixed(1), 'ms', 'measured round trip');
    assert.ok(worst < 10, 'every client starts within 10 ms of the server (worst ' + worst.toFixed(2) + ')');
    assert.ok(r.snapRate > 27 && r.snapRate < 33, 'snapshot rate ' + r.snapRate);
    assert.ok(r.e.n > 500, 'enough samples (' + r.e.n + ')');
    assert.ok(r.e.p95 < 0.1, 'p95 error under 10 cm (' + r.e.p95 + ')');
    assert.ok(r.e.max < 0.6, 'worst error under 60 cm (' + r.e.max + ')');
    assert.ok(r.st.interpDelay >= 60 && r.st.interpDelay <= 200);
    assert.equal(r.corrections, 0, 'honest bots are never corrected');
  } finally { await cleanup(r); }
});

test('a mobile network with delay spikes: still smooth, extrapolation bounded', async () => {
  const r = await measure('mobile', 'mob', { seconds: 8 });
  try {
    metric('sync.mobile.interp.p95', +(r.e.p95 * 100).toFixed(1), 'cm', 'mobile profile (spikes of 120-250 ms): p95 error');
    metric('sync.mobile.interp.max', +(r.e.max * 100).toFixed(1), 'cm', 'mobile profile: worst error');
    metric('sync.mobile.extrapolated', +(r.extrapShare * 100).toFixed(2), '%', 'mobile profile: samples extrapolated');
    metric('sync.mobile.interpDelay', +r.st.interpDelay.toFixed(1), 'ms', 'mobile profile: interpolation delay');
    const worst = Math.max(...r.startErr.map(Math.abs));
    metric('sync.mobile.startError', +worst.toFixed(2), 'ms', 'mobile profile: worst start error');
    assert.ok(r.e.p95 < 0.35, 'p95 ' + r.e.p95);
    assert.ok(r.e.max < 2.5, 'even in a spike, no wild jumps (worst ' + r.e.max + ')');
    assert.equal(r.corrections, 0);
  } finally { await cleanup(r); }
});

test('clock sync converges and reports jitter', async () => {
  const srv = await startServer();
  const [b] = makeBots(srv, 1, { profile: PROFILES.rtt120 });
  try {
    await b.connect(); await sleep(2500);
    const s = b.net.stats();
    assert.ok(Math.abs(s.offset) < 6, 'offset error ' + s.offset);
    assert.ok(s.rtt > 100 && s.rtt < 160, 'rtt ' + s.rtt); assert.ok(s.minRtt >= 90 && s.minRtt < 130);
    assert.ok(s.jitter > 0 && s.jitter < 40, 'jitter ' + s.jitter);
    metric('sync.clockError', +Math.abs(s.offset).toFixed(2), 'ms', 'clock offset error after 2.5 s at 120 ms RTT');
  } finally { b.close(); await srv.close(); }
});
