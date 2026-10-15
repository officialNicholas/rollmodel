// Movement referee. Each client moves its own blob and reports where it is; this checks every report against what the
// game's physics allows and keeps the last report that passed. It never moves anyone itself.
//
// Horizontal: the distance covered must fit the speed the blob could have had. That allowance starts from the ground
// speed at that spot (base speed x rain x own colour x ramp) and is raised by moves the server accepted (roll, fling,
// a push, items). On the ground extra speed fades at about the game's rate; in the air it carries. Each step adds
// (distance - allowance x time) to a bucket that cannot go below zero, so timing noise between steps cancels out while
// any steady excess piles up; a full bucket, or one step far beyond the allowance, is a violation.
// Solids: the body's centre may not be inside a piece, and a step may not pass through one.
// Vertical: in the air there is a ceiling. Leaving the ground without a launch it sits just above the ground you left;
// a launch (a hop, a fling, a pound, a push) raises it to that launch's peak; after the peak it comes down at 2.5 m/s
// (slower than any real fall, including the slow drop while aiming). Above the ceiling is flying or floating.
import { G, launchSpd } from './constants.js';

export const MOVE = Object.freeze({
  TOL: 0.05, // 5% over the allowance
  BUCKET_MAX: 1.5, // metres of accumulated excess before it counts as a speed violation
  TELEPORT_M: 3.0, // one step this far beyond the allowance is a teleport
  DECAY: 2.0, // per second, how fast extra speed fades on the ground (the game's own rate is 2.6)
  GROUND_GAP: 0.45, // within this of a surface counts as standing on it
  LEDGE: 0.3, // the ceiling above the ground you just left, with no launch
  LEDGE_MS: 250, // ... for this long after you left it
  HOLD_MS: 500, // a launch's ceiling stays at its peak this long after the peak (pound hang, missile hang, aiming, and a
  // phone so slow its game runs in slow motion: the game caps a frame at 50 ms, so below 20 fps time stretches)
  DESCENT: 2.0, // m/s the ceiling comes down afterwards
  HOP_VY: G.JUMP_V * 1.15, // an implied hop: the biggest jump-like launch (pot exits, the countdown leap, assists)
  FALL_Y: -3, // below this with nothing underneath: fallen
  PATH_STEP: 0.25,
  STILL_M: 0.35, // how far a blob that should not move (countdown, flattened) may drift
});
const BASE = G.SPEED * G.MOVE_K;

export class Mover {
  constructor(level) { this.L = level; this.reset({ x: 0, y: 0, z: 0, yaw: 0 }, 0); }
  // put the blob somewhere (spawn, respawn, correction target, out of a pot)
  reset(s, t, { airborne = false, groundY } = {}) {
    let y = s.y;
    if (!Number.isFinite(y)) { const g = this.L.surfaceUnder(s.x, s.z, 50); y = g > -Infinity ? g : 0; } // no height given: on the surface there
    this.last = { x: s.x, y, z: s.z, yaw: s.yaw || 0, t };
    const sup = this.L.supportAt(s.x, s.z, y);
    this.groundY = groundY !== undefined ? groundY : sup > -Infinity ? sup : y;
    this.groundT = t; this.airborne = airborne; this.bucket = 0; this.allow = 0; this.holdUntil = 0; this.dashUsed = false;
    this.ceil = y > this.groundY ? y + 0.15 : -Infinity; this.ceilT = t + MOVE.LEDGE_MS; // (put in the air: that height for a moment)
  }
  groundCap(x, y, z, env) {
    let c = BASE * (env.rainMul || 1);
    if (env.turfOwn && env.turfOwn(x, y, z)) c *= G.TURF_OWN;
    if (this.L.onRamp(x, z, 0.6)) c *= G.SLOPE_MAX;
    if (env.giant) c = Math.min(c * G.GIANT_SPD, G.SPEED * G.GIANT_CAP * G.MOVE_K);
    return c;
  }
  // raise the speed allowance (an accepted roll, fling, push or item) and keep it for holdMs before it may fade
  boost(speed, holdMs, t) { if (speed > this.allow) this.allow = speed; this.holdUntil = Math.max(this.holdUntil, t + holdMs); }
  // a launch upward with speed vy from height y0 (gUp: gravity while rising; a pound rises against 1.7 g; hold: extra
  // time at the top, like the pound's hang)
  launch(vy, t, y0 = this.last.y, gUp = G.GRAV, hold = 0) {
    const peak = y0 + (vy > 0 ? vy * vy / (2 * gUp) : 0) + 0.15, peakT = t + (vy > 0 ? vy / gUp * 1000 : 0) + MOVE.HOLD_MS + hold;
    const now = this.launchCeilAt(t);
    if (peak >= now) { this.ceil = peak; this.ceilT = Math.max(peakT, t); } else this.ceilT = Math.max(this.ceilT, peakT - (this.ceil - peak) / MOVE.DESCENT * 1000);
  }
  launchCeilAt(t) { return t <= this.ceilT ? this.ceil : this.ceil - MOVE.DESCENT * (t - this.ceilT) / 1000; }
  // how high you may be at time t: just above the ground you last touched for a moment after leaving it, or under the
  // arc of the last launch; both come down at DESCENT once their moment is over
  ceilingAt(t) {
    const g = this.groundY + MOVE.LEDGE - (t > this.groundT + MOVE.LEDGE_MS ? MOVE.DESCENT * (t - this.groundT - MOVE.LEDGE_MS) / 1000 : 0);
    return Math.max(g, this.launchCeilAt(t));
  }
  rollSpeed(env) { const b = BASE * (env.rainMul || 1), cur = Math.max(this.allow, this.groundCap(this.last.x, this.last.y, this.last.z, env)); return (Math.max(cur, b) + b * 1.15) * 1.08; }
  flingSpeed(c) { return launchSpd(Math.min(1, Math.max(G.FLING_MIN, c))); }
  // what an accepted move allows (the match calls these, and so do the tests)
  onJump(t) { this.launch(MOVE.HOP_VY, t, Math.max(this.groundY, this.last.y)); }
  onRoll(env, t) { this.boost(this.rollSpeed(env) * 1.05, G.ROLL_DASH * 1000 + 150, t); }
  onDash(t) { this.dashUsed = true; this.boost(11.5, 450, t); this.launch(2.6, t); }
  onFling(c, t, air = false) { this.boost(this.flingSpeed(c) * 1.08 + 0.4, 500, t); this.launch(air ? 1.5 + 3 * c : G.JUMP_V * (0.55 + 0.8 * c) * 0.935, t, air ? this.last.y : Math.max(this.groundY, this.last.y)); }
  onPound(t, air) { this.launch(air ? 3 : 9, t, air ? this.last.y : Math.max(this.groundY, this.last.y), G.GRAV * 1.7, 200); }
  onMissile(t) { this.boost(G.SPEED * G.MISSILE_SPD * 1.25, 2500, t); }
  onPush(spd, vy, t) { this.boost(spd * 1.1, 1500, t); this.launch(vy, t); }
  onPopOut(t, potY, vy = MOVE.HOP_VY) { this.boost(G.SPEED * 1.25, 600, t); this.launch(vy, t, potY + G.POT_POP_Y); }

  // s: { x, y, z, yaw, vy }, t: the client's time for it (ms, server clock), env: { rainMul, turfOwn(x,y,z), giant,
  // still, anchor, ceilExtra }. Returns { ok: true, y, grounded, support, fell } (y may be corrected onto a surface) or
  // { ok: false, reason, hard }.
  check(s, t, env = {}) {
    const L = this.L, P = this.last, dt = (t - P.t) / 1000;
    if (!(dt > 0)) return { ok: false, reason: 'time', silent: true };
    const dtc = Math.min(dt, 1.5), A = L.arena;
    if (Math.abs(s.x) > A + 12 || Math.abs(s.z) > A + 12 || s.y > 60 || s.y < -60) return { ok: false, reason: 'bounds', hard: true };
    const dx = s.x - P.x, dz = s.z - P.z, d = Math.hypot(dx, dz);
    let bucket = this.bucket;
    if (env.still) {
      // not allowed to go anywhere (countdown, flattened): stay near the anchor
      const a = env.anchor || P;
      if (Math.hypot(s.x - a.x, s.z - a.z) > MOVE.STILL_M) return { ok: false, reason: 'moved', hard: false };
    } else {
      const prev = Math.max(this.allow, this.groundCap(P.x, P.y, P.z, env));
      const cap = Math.max(prev, this.groundCap(s.x, s.y, s.z, env)) * (1 + MOVE.TOL), budget = cap * dtc;
      this._prev = prev;
      if (d > budget + MOVE.TELEPORT_M) return { ok: false, reason: 'teleport', hard: true };
      bucket = Math.max(0, bucket + d - budget);
      if (bucket > MOVE.BUCKET_MAX) return { ok: false, reason: 'speed', hard: false };
    }
    // solids. A fast fall can drop through the top of a piece in one frame (the game only looks a step above you when
    // you land); coming down from above, that is a landing on the top, not a wall.
    let y = s.y;
    const where = () => ({ from: [+P.x.toFixed(2), +P.y.toFixed(2), +P.z.toFixed(2)], to: [+s.x.toFixed(2), +s.y.toFixed(2), +s.z.toFixed(2)] });
    // (if the server itself put the blob inside something, say popping it out of a pot under a low deck, it may move out)
    const placedInside = L.insideSolid(P.x, P.z, P.y);
    if (!placedInside && L.insideSolid(s.x, s.z, y)) {
      const top = L.solidTop(s.x, s.z, y);
      if (P.y >= top - G.STEP - 0.15) y = top; else return { ok: false, reason: 'wall', hard: true, detail: where() };
    }
    if (d > MOVE.PATH_STEP && !placedInside) {
      const n = Math.ceil(d / MOVE.PATH_STEP), hy = Math.max(P.y, y);
      for (let i = 1; i < n; i++) if (L.insideSolid(P.x + dx * i / n, P.z + dz * i / n, hy)) return { ok: false, reason: 'wall', hard: true, detail: Object.assign(where(), { path: true }) };
    }
    // vertical
    const support = L.supportAt(s.x, s.z, y), grounded = support > -Infinity && y - support <= MOVE.GROUND_GAP;
    // standing on something much higher than where you just were, with no launch to get you there: a climb the game
    // does not allow (you only roll up a ledge of STEP without jumping)
    if (grounded && support > P.y + G.STEP + 0.12 && support > this.groundY + G.STEP + 0.12 && support > this.ceilingAt(t)) return { ok: false, reason: 'climb', hard: false };
    let fell = false;
    if (!grounded) {
      // leaving the ground going up: a hop (the action may come a moment later; the referee does not need it)
      if (!this.airborne && (s.vy || 0) > 0.5 && t - this.groundT < 250) this.launch(Math.min(s.vy, MOVE.HOP_VY), t, this.groundY);
      if (support === -Infinity && y < MOVE.FALL_Y) fell = true;
      else if (y > this.ceilingAt(t) + (env.ceilExtra || 0)) return { ok: false, reason: y > this.groundY + 2.2 ? 'fly' : 'float', hard: false, detail: { y: +y.toFixed(2), ceil: +this.ceilingAt(t).toFixed(2), groundY: +this.groundY.toFixed(2), airMs: Math.round(t - this.groundT), vy: s.vy } };
    }
    // accepted: move on
    this.bucket = bucket;
    if (!env.still) {
      const g = this.groundCap(s.x, y, s.z, env);
      if (grounded && t > this.holdUntil) {
        const dd = (t - Math.max(P.t, this.holdUntil)) / 1000;
        this.allow = this._prev > g ? g + (this._prev - g) * Math.exp(-MOVE.DECAY * dd) : g;
      } else this.allow = Math.max(this.allow, this._prev);
    }
    if (grounded) { this.groundY = support; this.groundT = t; this.airborne = false; this.dashUsed = false; }
    else this.airborne = true;
    this.last = { x: s.x, y, z: s.z, yaw: s.yaw || 0, t };
    return { ok: true, y, grounded, support, fell };
  }
}
