// A headless blob that moves the way the game's does (game/index.html: stepBlob, moveFlat, jump, dodgeRoll, fling,
// startSlam), on the same stage queries the server uses. Bots drive it; tests can also drive it directly.
import { G, launchSpd, launchV } from '../../src/constants.js';
import { inR } from '../../src/geometry.js';

const BASE = G.SPEED * G.MOVE_K, TURN = 3.9 * 0.89 * 0.8; // full steer with the game's default turning
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
export const wrapA = a => { a = (a + Math.PI) % (Math.PI * 2); if (a < 0) a += Math.PI * 2; return a - Math.PI; };

export class Body {
  constructor(level, at) { this.L = level; this.place(at); }
  place({ x, y, z, yaw = 0 }) {
    const g = this.L.surfaceUnder(x, z, (y ?? 0) + 5);
    Object.assign(this, { rain: this.rain || 1, x, y: y ?? (g > -Infinity ? g : 0), z, yaw, spd: 0, vy: 0, air: false, rollT: 0, rollCD: 0, rollV: 0, dashT: 0, dashUsed: false, charging: false, aim: 0, slam: null, flung: false, flingC: 0, flatT: 0, kx: 0, kz: 0, fell: false, landed: false });
  }
  get grounded() { return !this.air; }
  // a frame, like the game's: at most 50 ms of simulated time, in steps of at most 12 ms
  step(dt, input = {}) {
    dt = Math.min(dt, 0.05);
    const n = Math.max(1, Math.ceil(dt / 0.012)); let hit = false, slamLanded = false, landed = false;
    for (let i = 0; i < n; i++) { const r = this._step(dt / n, input); hit = hit || r.hit; slamLanded = slamLanded || r.slamLanded; landed = landed || this.landed; }
    this.landed = landed;
    return { hit, slamLanded };
  }
  _step(dt, input) {
    const L = this.L; this.landed = false; let slamLanded = false;
    if (this.rollT > 0) this.rollT = Math.max(0, this.rollT - dt);
    if (this.rollCD > 0) this.rollCD = Math.max(0, this.rollCD - dt);
    if (this.dashT > 0) this.dashT -= dt;
    // steering
    const turnK = this.slam ? 0 : this.air ? 0.65 : this.charging ? 0.75 : this.rollT > G.ROLL_T - G.ROLL_DASH ? 0.4 : 1;
    if (this.flatT <= 0) {
      if (input.yaw !== undefined) this.yaw += clamp(wrapA(input.yaw - this.yaw), -TURN * turnK * dt, TURN * turnK * dt);
      else if (input.steer) this.yaw += clamp(input.steer, -1, 1) * TURN * turnK * dt;
    }
    // speed
    if (this.flatT > 0) { this.flatT -= dt; this.spd = 0; }
    else if (this.slam && !this.slam.missile) this.spd = 0;
    else if (this.charging) this.spd += (0 - this.spd) * Math.min(1, dt * 16);
    else if (!this.air && this.rollT > G.ROLL_T - G.ROLL_DASH) this.spd = this.rollV * (0.62 + 0.38 * (this.rollT - G.ROLL_T + G.ROLL_DASH) / G.ROLL_DASH);
    else if (!this.air) { const tgt = BASE * this.rain * (input.speedK ?? 1) * this.slopeK(); this.spd += (tgt - this.spd) * Math.min(1, dt * (this.spd > tgt ? 2.6 : 9)); }
    // horizontal, one axis at a time, like the game
    const fx = Math.sin(this.yaw), fz = Math.cos(this.yaw), d = this.spd * dt;
    let hit = false;
    const nx = this.x + fx * d + this.kx * dt; if (!L.blockedAt(nx, this.z, this.y)) this.x = nx; else { hit = true; this.kx = 0; }
    const nz = this.z + fz * d + this.kz * dt; if (!L.blockedAt(this.x, nz, this.y)) this.z = nz; else { hit = true; this.kz = 0; }
    if (this.kx || this.kz) { const f = Math.exp(-dt * (this.air ? 1.2 : 5)); this.kx *= f; this.kz *= f; if (this.kx * this.kx + this.kz * this.kz < 0.01) this.kx = this.kz = 0; }
    // vertical
    if (this.air) {
      const s = this.slam;
      if (s && s.missile) { this.vy = -Math.max(3, this.spd * 0.3); this.y += this.vy * dt; }
      else if (s && this.vy <= 0 && s.hang > 0) { s.hang -= dt; this.vy = 0; if (s.hang <= 0) this.vy = -20; }
      else {
        const prevHead = this.y + 0.8;
        this.y += this.vy * dt; this.vy -= G.GRAV * (s ? (this.vy < 0 ? 3 : 1.7) : (this.vy < 0 ? G.FALL_K : 1)) * dt; if (this.charging && this.vy < -3) this.vy = -3;
        // the head bumps the underside of a floating piece (the game's bonk)
        if (this.vy > 0) for (const b of L._cell(L.qgB, this.x, this.z)) if (b[4] > 0 && prevHead <= b[4] && this.y + 0.8 > b[4] && inR(this.x, this.z, b)) { this.y = b[4] - 0.8; this.vy = 0; }
      }
      const g = L.surfaceUnder(this.x, this.z, this.y + G.STEP);
      if (this.vy <= 0 && g > -Infinity && this.y <= g) {
        this.y = g; this.vy = 0; this.air = false; this.dashUsed = false; this.landed = true;
        if (this.slam) { slamLanded = true; this.slam = null; } this.flung = false;
      }
      if (this.y < -5) this.fell = true;
    } else {
      const g = L.surfaceUnder(this.x, this.z, this.y + G.STEP);
      if (g === -Infinity || this.y - g > 0.35) { this.air = true; this.vy = 0; } else this.y = g;
    }
    return { hit, slamLanded };
  }
  // the game's slopeK: faster down a ramp (up to 1.4x), slower up it
  slopeK() {
    const fx = Math.sin(this.yaw), fz = Math.cos(this.yaw), a = this.L.surfaceUnder(this.x + fx * 0.45, this.z + fz * 0.45, this.y + 0.6), b = this.L.surfaceUnder(this.x - fx * 0.45, this.z - fz * 0.45, this.y + 0.6);
    if (a === -Infinity || b === -Infinity || Math.abs(a - b) > 0.45) return 1;
    return clamp(1 - (a - b) / 0.9 * 0.9, 0.7, 1.4);
  }
  jump() { if (this.air || this.flatT > 0 || this.slam || this.charging) return false; this.air = true; this.vy = G.JUMP_V; return true; }
  // a roll on the ground, an air dash in the air (once per hop)
  roll() {
    if (this.flatT > 0 || this.slam) return null;
    if (this.air) { if (this.dashUsed) return null; this.dashUsed = true; this.dashT = G.DASH_T; this.vy = 2.6; this.spd = Math.min(Math.max(this.spd, 7), 10); return 'dash'; }
    if (this.rollCD > 0) return null;
    const base = BASE * this.rain;
    this.rollV = (Math.max(this.spd, base) + base * 1.15) * 1.08; this.rollT = G.ROLL_T; this.rollCD = G.ROLL_CD; this.spd = this.rollV;
    return 'roll';
  }
  fling(c) {
    c = clamp(c, G.FLING_MIN, 1); this.charging = false;
    if (this.flatT > 0 || this.slam) return false;
    if (this.air) { if (this.dashUsed) return false; this.dashUsed = true; this.vy = 1.5 + 3 * c; this.spd = Math.min(launchSpd(c), 8); this.flung = true; this.flingC = c; return true; }
    this.air = true; this.vy = launchV(c); this.spd = launchSpd(c); this.flung = true; this.flingC = c; return true;
  }
  pound() {
    if (this.flatT > 0 || this.slam) return false;
    if (this.air) { const missile = this.flung && this.flingC > 0.15; this.slam = { hang: 0.1, missile }; if (missile) this.spd = Math.max(this.spd, G.SPEED * G.MISSILE_SPD); else { this.vy = Math.max(this.vy, 3); this.spd = 0; } return true; }
    this.slam = { hang: 0.14, missile: false }; this.air = true; this.vy = 9; this.spd = 0; return true;
  }
  state(extra = {}) {
    return Object.assign({ x: this.x, y: this.y, z: this.z, yaw: this.yaw, spd: this.spd, vy: this.vy, air: this.air, rolling: this.rollT > 0, charging: this.charging, slam: !!this.slam, flung: this.flung, aim: this.aim }, extra);
  }
}
