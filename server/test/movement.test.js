// The movement referee on its own, fed by a blob moving with the game's physics. Honest play of every kind must
// never be flagged; each kind of cheating must be.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Mover, MOVE } from '../src/movement.js';
import { Level } from '../src/geometry.js';
import { G } from '../src/constants.js';
import { rng } from '../src/util.js';
import { Body } from './helpers/body.js';
import { genLayout, flatLayout } from './helpers/layouts.js';
import { metric } from './helpers/harness.js';

// Drive a blob for `seconds` with uneven frames (12 to 22 ms) and report at about 30 Hz, the way the SDK does.
// mind(ctx) steers and acts; the referee is told about every accepted move like the match tells it.
function drive(level, { seconds = 30, seed = 1, rain = 1, mind, start, cheat, frames = [12, 22], hitch = 0, sendEvery = 33.33 } = {}) {
  const R = rng(seed), sp = start || level.spawns[0], body = new Body(level, sp); body.rain = rain;
  const mover = new Mover(level); let t = 10000; mover.reset(sp, t);
  const env = { rainMul: rain, turfOwn: () => false };
  const out = { violations: [], fell: 0, states: 0, maxSpeed: 0, actions: {} };
  let nextSend = t, lastSent = { x: sp.x, z: sp.z, t };
  const ctx = { body, level, R, mover, env, t: 0, act: (a, fn) => { const air = body.air, r = fn(); if (r) { out.actions[a] = (out.actions[a] || 0) + 1; tell(a, r, air); } return r; } };
  // what the match does when it accepts each action
  const tell = (a, r, air) => {
    if (a === 'jump') mover.onJump(t);
    if (a === 'roll') { if (r === 'dash') mover.onDash(t); else mover.onRoll(env, t); }
    if (a === 'fling') mover.onFling(body.flingC, t, air);
    if (a === 'pound') { if (body.slam && body.slam.missile) mover.onMissile(t); else mover.onPound(t, air); }
  };
  for (let el = 0; el < seconds * 1000;) {
    const dt = R() < hitch ? 60 + R() * 120 : frames[0] + R() * (frames[1] - frames[0]); el += dt; t += dt; ctx.t = el;
    const input = mind ? mind(ctx) : {};
    body.step(dt / 1000, input || {});
    if (t >= nextSend) {
      nextSend = nextSend + sendEvery > t ? nextSend + sendEvery : t + sendEvery;
      const st = cheat ? cheat(body.state(), ctx) : body.state();
      const r = mover.check(st, t, env); out.states++;
      if (!r.ok) { out.violations.push({ t: el, reason: r.reason, x: st.x, y: st.y, z: st.z }); body.place(mover.last); mover.last.t = t; mover.bucket = 0; }
      else {
        const v = Math.hypot(st.x - lastSent.x, st.z - lastSent.z) / ((t - lastSent.t) / 1000); if (v > out.maxSpeed) out.maxSpeed = v;
        lastSent = { x: st.x, z: st.z, t };
        if (r.fell) { out.fell++; body.place(sp); mover.reset(sp, t); lastSent = { x: sp.x, z: sp.z, t }; }
      }
    }
    if (body.fell) { body.place(sp); mover.reset(sp, t); lastSent = { x: sp.x, z: sp.z, t }; }
  }
  return out;
}

// an honest player: wanders, avoids walls and holes, and does everything the game lets you do
function wander(ctx) {
  const { body: b, level: L, R } = ctx, A = L.arena;
  const danger = (yaw, reach = 2) => { for (const d of [0.7, reach]) { const px = b.x + Math.sin(yaw) * d, pz = b.z + Math.cos(yaw) * d; if (Math.abs(px) > A - 1.5 || Math.abs(pz) > A - 1.5 || L.blockedAt(px, pz, b.y)) return true; const g = L.surfaceUnder(px, pz, b.y + G.STEP); if (g === -Infinity || b.y - g > 0.5) return true; } return false; };
  if (!ctx.tg || Math.hypot(ctx.tg.x - b.x, ctx.tg.z - b.z) < 2) ctx.tg = { x: (R() * 2 - 1) * (A - 4), z: (R() * 2 - 1) * (A - 4) };
  let yaw = Math.atan2(ctx.tg.x - b.x, ctx.tg.z - b.z);
  if (!b.air && danger(b.yaw)) { for (const o of [0.7, -0.7, 1.4, -1.4, 2.2, -2.2, 3.1]) if (!danger(b.yaw + o)) { yaw = b.yaw + o; break; } ctx.tg = null; }
  const p = R();
  if (!b.air && !b.slam && p < 0.012) ctx.act('jump', () => b.jump());
  else if (!b.slam && p < 0.02) ctx.act('roll', () => b.roll());
  else if (!b.air && !b.slam && p < 0.026 && !danger(b.yaw, 7)) ctx.act('fling', () => b.fling(0.08 + R() * 0.92));
  else if (!b.slam && p < 0.03) ctx.act('pound', () => b.pound());
  else if (b.air && !b.slam && p < 0.04) ctx.act('fling', () => b.fling(R()));
  if (!b.air && p > 0.995) b.charging = true; else if (b.charging && p > 0.9) b.charging = false;
  return { yaw };
}

test('honest play is never flagged (many stages, every move, uneven frames, hitches)', () => {
  let states = 0, total = 0; const acts = {}; let maxSpeed = 0;
  const profiles = [{ frames: [12, 22] }, { frames: [7, 9] }, { frames: [30, 36] }, { frames: [12, 22], hitch: 0.02 }];
  for (const A of [26.4, 33]) for (let s = 0; s < 8; s++) {
    const L = new Level(genLayout(7000 + s, A));
    const r = drive(L, Object.assign({ seconds: 40, seed: 100 + s, mind: wander }, profiles[s % profiles.length]));
    total += r.violations.length; states += r.states; maxSpeed = Math.max(maxSpeed, r.maxSpeed);
    for (const [k, v] of Object.entries(r.actions)) acts[k] = (acts[k] || 0) + v;
    assert.deepEqual(r.violations, [], 'stage ' + A + '/' + s);
  }
  for (const a of ['jump', 'roll', 'fling', 'pound']) assert.ok(acts[a] > 20, 'did plenty of ' + a + ' (' + acts[a] + ')');
  metric('move.honest.states', states, 'states', 'honest states checked offline, ' + total + ' flagged');
  metric('move.honest.maxSpeed', +maxSpeed.toFixed(2), 'm/s', 'fastest honest step seen');
});

test('honest play in the rain (double speed) is not flagged, and the same speed without rain is', () => {
  const L = new Level(genLayout(4242, 33));
  const wet = drive(L, { seconds: 30, seed: 9, rain: 2, mind: wander });
  assert.deepEqual(wet.violations, []);
  // a client that moves at rain speed when it is not raining
  const lie = drive(L, { seconds: 10, seed: 9, rain: 1, mind: ctx => { ctx.body.rain = 2; return wander(ctx); } });
  assert.ok(lie.violations.some(v => v.reason === 'speed'), 'rain speed in dry weather is a speed hack');
});

test('ramps, ledges, decks: legal ups and downs pass', () => {
  // a deck at 2.3 to 2.7 m reached by a ramp, and a box to hop onto
  const L = new Level({ arena: 26.4, boxes: [[-3, 3, 0, 6, 2.3, 2.7], [8, 10, 0, 2, 0, 0.9]], ramps: [[-2, 2, -10, 0, 'z', 0, 2.7]], holes: [], pots: [[0, 0, -15]], powers: [], spawns: [[0, -16, 0], [9, -6, 0]] });
  // up the ramp, across the deck, off the far edge (a 2.7 m drop), with a roll down the ramp on the way
  const up = drive(L, { seconds: 7, mind: ctx => { if (ctx.t > 1000 && ctx.t < 1100) ctx.act('roll', () => ctx.body.roll()); return { yaw: 0 }; } });
  assert.deepEqual(up.violations, []);
  // jump onto the box from a run
  const hop = drive(L, { seconds: 3, start: { x: 9, z: -6, yaw: 0 }, mind: ctx => { if (ctx.t > 650 && !ctx.done) { ctx.done = ctx.act('jump', () => ctx.body.jump()); } return { yaw: 0 }; } });
  assert.deepEqual(hop.violations, []);
  // a slow phone (four reports a second) walking up a steeper ramp (like the game's): each report is a long stride up
  // it, 0.6 m higher, not a climb
  const steep = new Level({ arena: 26.4, boxes: [[-3, 3, 0, 6, 2.3, 2.7]], ramps: [[-2, 2, -6, 0, 'z', 0, 2.7]], holes: [], pots: [[0, 0, -15]], powers: [], spawns: [[0, -16, 0], [9, -6, 0]] });
  const slow = drive(steep, { seconds: 6, sendEvery: 250, mind: () => ({ yaw: 0 }) });
  assert.deepEqual(slow.violations, []);
});

const flat = () => new Level(flatLayout(26.4));
const straight = { yaw: 0 };

test('speed hacks are caught', () => {
  const L = flat();
  for (const k of [1.25, 1.5, 3]) {
    const r = drive(L, { seconds: 6, start: { x: -20, z: -20, yaw: 0 }, mind: ctx => ({ yaw: 0, speedK: k }) });
    assert.ok(r.violations.length > 0 && r.violations[0].reason === 'speed', k + 'x');
    metric('move.speedhack.' + k, +(r.violations[0].t / 1000).toFixed(2), 's', 'time to catch a ' + k + 'x speed hack');
  }
  const ok = drive(L, { seconds: 6, start: { x: -20, z: -20, yaw: 0 }, mind: () => straight });
  assert.deepEqual(ok.violations, [], 'normal speed is fine');
});

test('teleports, walls, flying and floating are caught', () => {
  const L = flat();
  const tele = drive(L, { seconds: 2, start: { x: -20, z: -20, yaw: 0 }, mind: () => straight, cheat: (s, c) => (c.t > 1000 && !c.did ? (c.did = 1, Object.assign(s, { x: s.x + 8 })) : s) });
  assert.equal(tele.violations[0].reason, 'teleport');
  // stand inside the wall at (-1..1, 4..10)
  const inWall = drive(L, { seconds: 1, start: { x: -20, z: -20, yaw: 0 }, mind: () => straight, cheat: (s, c) => (c.t > 500 ? Object.assign(s, { x: 0, z: 7, y: 0 }) : s) });
  assert.ok(inWall.violations.some(v => v.reason === 'wall' || v.reason === 'teleport'));
  // walk straight through the wall (no hop): the referee stops it at the wall
  const thru = drive(L, { seconds: 4, start: { x: 0, z: 0, yaw: 0 }, mind: () => straight, cheat: (s, c) => Object.assign(s, { x: 0, y: 0, z: G.SPEED * c.t / 1000 }) }); // a client that ignores walls
  assert.ok(thru.violations.some(v => v.reason === 'wall'), JSON.stringify(thru.violations.slice(0, 2)));
  // the honest blob bumps the wall instead
  assert.deepEqual(drive(L, { seconds: 4, start: { x: 0, z: 0, yaw: 0 }, mind: () => straight }).violations, []);
  // flying: 3 m up out of nowhere
  const fly = drive(L, { seconds: 2, start: { x: -20, z: -20, yaw: 0 }, mind: () => straight, cheat: (s, c) => (c.t > 500 ? Object.assign(s, { y: Math.min(3, (c.t - 500) / 100) }) : s) });
  assert.ok(fly.violations.some(v => v.reason === 'fly' || v.reason === 'float'), JSON.stringify(fly).slice(0, 600));
  // floating: hold 1.2 m up for seconds
  const hover = drive(L, { seconds: 5, start: { x: -20, z: -20, yaw: 0 }, mind: () => straight, cheat: (s, c) => (c.t > 500 ? Object.assign(s, { y: 1.2 }) : s) });
  assert.ok(hover.violations.some(v => v.reason === 'float'));
  // climbing onto a 1.2 m box without a hop (the box at 8..12, -12..-8)
  const climb = drive(L, { seconds: 4, start: { x: 10, z: -15, yaw: 0 }, mind: () => straight, cheat: s => (s.z > -12.5 ? Object.assign(s, { z: s.z + 1.2, y: 1.2 }) : s) });
  assert.ok(climb.violations.some(v => v.reason === 'climb'), JSON.stringify(climb.violations.slice(0, 2)));
  // walking on air over a hole is a fall, not a way across
  const air = drive(L, { seconds: 5, start: { x: -12, z: -8, yaw: 0 }, mind: () => straight, cheat: s => Object.assign(s, { y: 0 }) });
  assert.ok(air.fell > 0 || air.violations.length > 0, 'over the pit with y = 0');
  // under the floor
  const under = drive(L, { seconds: 4, start: { x: -20, z: -20, yaw: 0 }, mind: () => straight, cheat: (s, c) => (c.t > 300 ? Object.assign(s, { y: -1 }) : s) });
  assert.ok(under.fell > 0 || under.violations.length > 0);
});

test('a blob that must stay put (countdown, flattened) may not move', () => {
  const L = flat(), m = new Mover(L); m.reset({ x: 0, y: 0, z: -20, yaw: 0 }, 0);
  const env = { still: true, anchor: { x: 0, z: -20 } };
  assert.equal(m.check({ x: 0.2, y: 0, z: -20, yaw: 0 }, 33, env).ok, true, 'a little wobble is fine');
  const r = m.check({ x: 0, y: 0, z: -19, yaw: 0 }, 66, env); assert.equal(r.ok, false); assert.equal(r.reason, 'moved');
  assert.equal(m.check({ x: 0, y: 0, z: -20, yaw: 0 }, 50, env).ok, true, 'back where it should be');
  assert.equal(m.check({ x: 0, y: 0, z: -20, yaw: 0 }, 40, env).reason, 'time', 'older than the last report: ignored');
  assert.equal(MOVE.TOL, 0.05);
});
