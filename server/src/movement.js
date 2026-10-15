// Movement referee. Each client moves its own blob and reports where it is; this checks every report against what the
// game's physics allows and keeps the last report that passed. It never moves anyone itself.
//
// Horizontal: the step must fit the speed the blob could have had. That allowance starts from the ground speed at that
// spot (base speed x rain x own colour x ramp) and is raised by moves the server accepted (roll, fling, a push, items).
// On the ground extra speed fades at about the game's rate; in the air it carries. Small excesses (network jitter,
// rounding) go into a leaky bucket; a full bucket, or one step far beyond the allowance, is a violation.
// Solids: the body's centre may not sit inside a piece, and a step may not pass through one.
// Vertical: in the air you can be at most APEX above the last ground you touched, and only for so long.
import { G, launchSpd } from './constants.js';

export const MOVE = Object.freeze({
  TOL: 0.10, // 10% over the allowance
  SLACK_M: 0.10, // and 10 cm per step
  BUCKET_MAX: 1.6, // metres of excess before it counts as a speed violation
  BUCKET_LEAK: 1.2, // metres per second drained from the bucket
  TELEPORT_M: 3.0, // one step this far beyond the allowance is a teleport
  DECAY: 2.0, // per second, how fast extra speed fades on the ground (the game's own rate is 2.6)
  APEX: 2.05, // metres above the last ground (the biggest launch in the game is about 1.9)
  AIR_T: 2.3, // seconds in the air before you must have landed (slow descents while aiming included)
  GROUND_GAP: 0.45, // within this of a surface counts as standing on it
  FALL_Y: -3, // below this with nothing underneath: fallen
  PATH_STEP: 0.25,
  STILL_M: 0.35, // how far a blob that should not move (countdown, flattened) may drift
});
const BASE = G.SPEED * G.MOVE_K;

export class Mover {
  constructor(level) { this.L = level; this.reset({ x: 0, y: 0, z: 0, yaw: 0 }, 0); }
  // put the blob somewhere (spawn, respawn, correction target, out of a pot)
  reset(s, t, { airborne = false, groundY } = {}) {
    this.last = { x: s.x, y: s.y, z: s.z, yaw: s.yaw || 0, t };
    const sup = this.L.supportAt(s.x, s.z, s.y);
    this.groundY = groundY !== undefined ? groundY : sup > -Infinity ? sup : s.y;
    this.groundT = t; this.airborne = airborne; this.bucket = 0; this.allow = 0; this.holdUntil = 0; this.dashUsed = false;
  }
  groundCap(x, y, z, env) {
    let c = BASE * (env.rainMul || 1);
    if (env.turfOwn && env.turfOwn(x, y, z)) c *= G.TURF_OWN;
    if (this.L.onRamp(x, z, 0.6)) c *= G.SLOPE_MAX;
    if (env.giant) c = Math.min(c * G.GIANT_SPD, G.SPEED * G.GIANT_CAP * G.MOVE_K);
    return c;
  }
  // raise the allowance (an accepted roll, fling, push or item) and keep it for holdMs before it may fade
  boost(speed, holdMs, t) { if (speed > this.allow) this.allow = speed; this.holdUntil = Math.max(this.holdUntil, t + holdMs); }
  rollSpeed(env) { const b = BASE * (env.rainMul || 1), cur = Math.max(this.allow, this.groundCap(this.last.x, this.last.y, this.last.z, env)); return (Math.max(cur, b) + b * 1.15) * 1.08; }
  flingSpeed(c) { return launchSpd(Math.min(1, Math.max(G.FLING_MIN, c))); }

  // s: { x, y, z, yaw }, t: the client's time for it (ms, server clock), env: { rainMul, turfOwn(x,y,z), giant, still,
  // apexExtra, airExtra }. Returns { ok: true, grounded, support, fell } or { ok: false, reason, hard }.
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
      // horizontal speed
      const prev = Math.max(this.allow, this.groundCap(P.x, P.y, P.z, env));
      const cap = Math.max(prev, this.groundCap(s.x, s.y, s.z, env)) * (1 + MOVE.TOL), budget = cap * dtc + MOVE.SLACK_M;
      this._prev = prev;
      if (d > budget + MOVE.TELEPORT_M) return { ok: false, reason: 'teleport', hard: true };
      bucket = Math.max(0, bucket - MOVE.BUCKET_LEAK * dt) + Math.max(0, d - budget);
      if (bucket > MOVE.BUCKET_MAX) return { ok: false, reason: 'speed', hard: false };
    }
    // solids: where you are, and the way you came (at the higher of the two heights, so hopping onto a piece is fine)
    if (L.insideSolid(s.x, s.z, s.y)) return { ok: false, reason: 'wall', hard: true };
    if (d > MOVE.PATH_STEP) {
      const n = Math.ceil(d / MOVE.PATH_STEP), y = Math.max(P.y, s.y);
      for (let i = 1; i < n; i++) if (L.insideSolid(P.x + dx * i / n, P.z + dz * i / n, y)) return { ok: false, reason: 'wall', hard: true };
    }
    // vertical
    const support = L.supportAt(s.x, s.z, s.y), grounded = support > -Infinity && s.y - support <= MOVE.GROUND_GAP;
    let fell = false;
    if (!grounded) {
      const airT = (t - this.groundT) / 1000;
      if (support === -Infinity && (s.y < MOVE.FALL_Y || airT > MOVE.AIR_T + (env.airExtra || 0))) fell = true;
      else {
        if (s.y > this.groundY + MOVE.APEX + (env.apexExtra || 0)) return { ok: false, reason: 'fly', hard: false };
        if (airT > MOVE.AIR_T + (env.airExtra || 0) + Math.max(0, this.groundY - s.y) / 3) return { ok: false, reason: 'float', hard: false };
      }
    }
    // accepted: move on
    this.bucket = bucket;
    if (!env.still) {
      const g = this.groundCap(s.x, s.y, s.z, env);
      if (grounded && t > this.holdUntil) {
        const dd = (t - Math.max(P.t, this.holdUntil)) / 1000;
        this.allow = this._prev > g ? g + (this._prev - g) * Math.exp(-MOVE.DECAY * dd) : g;
      } else this.allow = Math.max(this.allow, this._prev);
    }
    if (grounded) { this.groundY = support; this.groundT = t; this.airborne = false; this.dashUsed = false; }
    else this.airborne = true;
    this.last = { x: s.x, y: s.y, z: s.z, yaw: s.yaw || 0, t };
    return { ok: true, grounded, support, fell };
  }
}
