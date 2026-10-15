// Lag compensation, at 150 ms round trip. The attacker sees the target about 150 to 200 ms in the past; the server
// rewinds the target to exactly what the attacker saw (at most 200 ms back) to judge a pound. A hit that was true on
// the attacker's screen counts; a clear miss does not; a target that rolled in time (on its own screen) is safe.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { performance } from 'node:perf_hooks';
import { G, KO_R } from '../src/constants.js';
import { startServer, makeBots, until, sleep, metric, matchOf } from './helpers/harness.js';
import { spawnsOf } from './helpers/layouts.js';

// an open floor: the attacker stands at the middle, the target runs past along z = 2
const stage = () => ({ arena: 26.4, boxes: [], ramps: [], holes: [], pots: [[-20, 0, -20], [20, 0, 20], [-20, 0, 20], [20, 0, -20]], powers: [], spawns: [[0, 0, 0], [-9, 2, Math.PI / 2], ...spawnsOf(26.4).slice(2)] });

// target: the rendered distance the attacker wants at the moment its pound lands; roll: when the target rolls,
// relative to the moment the pound lands (ms, on the target's own clock), or null
async function scenario({ target, roll = null, claimFar = false }) {
  const srv = await startServer({ matchT: 20, slamFirst: 0.2 });
  const [A, B] = makeBots(srv, 2, { profile: 'rtt150', behavior: 'script', layoutFor: stage, prefix: 'lag' });
  const out = { ko: null, dodged: null, land: null };
  let pounded = false, landAt = null, prevR = null;
  // the attacker: stands still, watches the target, and pounds so that it lands when the target (as drawn on its screen)
  // is at the wanted distance
  A.o.script = (bot, dt, sNow) => {
    bot.input = { speedK: 0 };
    const r = bot.net.remote(B.slot); if (!r) return;
    if (prevR && !pounded && sNow >= bot.startAt + 300) {
      const v = (r.x - prevR.x) / Math.max(1e-3, (r.t - prevR.t) / 1000), x = r.x + v * G.POUND_T, d = Math.hypot(x - bot.body.x, r.z - bot.body.z);
      if (v > 3 && r.x > -6 && d >= target && x > 0) { pounded = true; bot.body.pound(); bot.net.action('pound').then(res => { out.pound = res; }); landAt = sNow + G.POUND_T * 1000; }
    }
    prevR = r;
  };
  A.o.onLand = bot => {
    const r = bot.net.remote(B.slot), now = performance.now();
    out.land = { seen: Math.hypot(r.x - bot.body.x, r.z - bot.body.z), truth: Math.hypot(B.body.x - bot.body.x, B.body.z - bot.body.z), vt: bot.net.renderTime(), ts: bot.net.serverNow(), at: now, extrapolated: r.extrapolated };
    return claimFar ? { x: r.x, y: 0, z: r.z } : null;
  };
  // the target runs along +x; it may roll at a set moment around the landing
  let rolled = false;
  B.o.script = (bot, dt, sNow) => {
    bot.input = { yaw: Math.PI / 2, speedK: 1 };
    if (roll !== null && landAt && !rolled && sNow >= landAt + roll) { rolled = true; if (bot.body.roll()) bot.net.action('roll').then(r => { out.rollOk = r.ok; }); }
  };
  try {
    await Promise.all([A, B].map(b => b.connect()));
    await sleep(1500);
    await A.net.queue('duel'); await B.net.queue('duel');
    A.on('ko', m => { if (m.slot === B.slot) out.ko = m; });
    A.on('dodged', m => { if (m.slot === B.slot) out.dodged = m; });
    await Promise.all([A, B].map(b => b.wait('start')));
    await until(() => out.land, 12000);
    await sleep(900); // the decision waits for the target's own dodge
    const m = matchOf(srv, A.id);
    out.strikesA = m ? m.P[A.slot].strikes : 0; out.violationsA = m ? m.P[A.slot].violations : {};
    out.landResult = await A.lastLand;
    return out;
  } finally { A.close(); B.close(); await srv.close(); }
}

test('a hit that was true on the attacker\'s screen is honoured (150 ms round trip)', async () => {
  const r = await scenario({ target: 2.9 });
  metric('lagcomp.hit.seen', +r.land.seen.toFixed(2), 'm', 'distance on the attacker\'s screen when the pound landed (knock-out radius 3.34)');
  metric('lagcomp.hit.truth', +r.land.truth.toFixed(2), 'm', 'where the target really was at that moment');
  metric('lagcomp.rewind', +(r.land.ts - r.land.vt).toFixed(1), 'ms', 'how far the server rewound the target (view time before the landing)');
  assert.ok(r.land.seen < KO_R, 'on the attacker\'s screen it was a hit (' + r.land.seen.toFixed(2) + ' m)');
  assert.ok(r.land.truth > KO_R, 'and in truth the target had already got away (' + r.land.truth.toFixed(2) + ' m): only lag compensation makes it a hit');
  assert.ok(r.ko, 'the server knocked the target out');
  assert.equal(r.ko.reason, 'pound');
  assert.ok(r.land.ts - r.land.vt <= 200, 'rewind within the 200 ms cap');
});

test('a clear miss is not honoured', async () => {
  const r = await scenario({ target: 4.6 });
  assert.ok(r.land.seen > KO_R + 0.5, 'a clear miss on the attacker\'s screen (' + r.land.seen.toFixed(2) + ' m)');
  assert.equal(r.ko, null, 'no knock-out');
  assert.equal(r.landResult.ok, true); assert.deepEqual(r.landResult.data.candidates, []);
});

test('a target that rolled in time is safe, even though the attacker saw it before the roll', async () => {
  const r = await scenario({ target: 2.4, roll: -120 }); // the target rolls 120 ms before the pound lands
  assert.ok(r.land.seen < KO_R, 'on the attacker\'s screen it was a hit');
  assert.equal(r.rollOk, true);
  assert.equal(r.ko, null, 'not knocked out'); assert.ok(r.dodged, 'a dodge'); assert.equal(r.dodged.how, 'roll');
});

test('a roll that comes too late does not save the target', async () => {
  const r = await scenario({ target: 2.4, roll: 250 }); // 250 ms after the landing
  assert.ok(r.ko, 'knocked out'); assert.equal(r.dodged, null);
});

test('a stomp: landing on a rival flattens it; it cannot move until it pops back up, then it can', async () => {
  const srv = await startServer({ matchT: 20, flatT: 1.2 });
  const [A, B] = makeBots(srv, 2, { profile: 'rtt60', behavior: 'script', layoutFor: stage, prefix: 'stomp' });
  let claimed = null, jumped = false;
  // the victim stands still at (-9, 2)... the stomper starts at (0, 0) and runs at it, hops, and claims the stomp as it
  // comes down on its head
  B.o.script = bot => { bot.input = bot.body.flatT > 0 || !bot.go ? { speedK: 0 } : { yaw: Math.PI / 2, speedK: 1 }; };
  A.o.script = (bot, dt, sNow) => {
    const r = bot.net.remote(B.slot); if (!r || sNow < bot.startAt + 200) { bot.input = { speedK: 0 }; return; }
    const d = Math.hypot(r.x - bot.body.x, r.z - bot.body.z);
    bot.input = { yaw: Math.atan2(r.x - bot.body.x, r.z - bot.body.z), speedK: 1 };
    if (!jumped && !bot.body.air && d < 3.6 && d > 3.0) { jumped = true; if (bot.body.jump()) bot.net.action('jump'); }
    if (jumped && !claimed && bot.body.air && bot.body.vy < -0.5 && d < 2 * G.PR && bot.body.y > r.y + 0.25) {
      claimed = bot.net.action('stomp', { target: B.slot }); bot.body.vy = 6.5; // bounce off its head, like the game
    }
  };
  try {
    await Promise.all([A, B].map(b => b.connect()));
    await A.net.queue('duel'); await B.net.queue('duel');
    await Promise.all([A, B].map(b => b.wait('start')));
    const flat = await B.wait('flat', m => m.slot === B.slot, 12000);
    assert.equal(flat.by, A.slot); assert.ok((await claimed).ok);
    const m = matchOf(srv, A.id), pb = m.P[B.slot];
    assert.ok(pb.flatUntil > 0);
    // flattened: it stays put (its states keep being accepted, standing still)
    const at = { ...pb.mover.last };
    await sleep(600); assert.ok(Math.hypot(pb.mover.last.x - at.x, pb.mover.last.z - at.z) < 0.3);
    // when it pops back up it runs off, and the server follows it (its states carry the new correction id)
    await until(() => performance.now() > flat.until + 300, 4000);
    B.go = true; await sleep(800);
    assert.ok(Math.hypot(pb.mover.last.x - at.x, pb.mover.last.z - at.z) > 2, 'moving again on the server');
    assert.equal(B.stats.corrections, 0, JSON.stringify(B.events)); assert.equal(A.stats.corrections, 0, JSON.stringify(A.events));
  } finally { A.close(); B.close(); await srv.close(); }
});

test('a landing claimed far from where the attacker really was is refused', async () => {
  const r = await scenario({ target: 5.5, claimFar: true });
  assert.equal(r.ko, null);
  assert.equal(r.landResult.ok, false); assert.equal(r.landResult.reason, 'far');
  assert.ok(r.violationsA.pound_far >= 1, 'and it counts as a strike');
});
