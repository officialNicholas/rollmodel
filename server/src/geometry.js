// The stage as the server sees it, built from a validated layout. The queries mirror the game's own (game/index.html:
// inR, rampH, floorAt, surfaceUnder, blockedAt), including the coarse lookup grid, so the server and the game agree.
import { G } from './constants.js';

const QG_C = 2, QG_O = 44, QG_N = 44, QG_M = 0.75, EMPTY = Object.freeze([]);
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);

// r[6] === 'c' marks a round piece inscribed in its square (boxes and holes; a ramp's r[6] is its height, never 'c')
export const inR = (x, z, r, m = 0) => (r[6] === 'c'
  ? (x - (r[0] + r[1]) * 0.5) ** 2 + (z - (r[2] + r[3]) * 0.5) ** 2 < Math.max(0, (r[1] - r[0]) * 0.5 + m) ** 2
  : x > r[0] - m && x < r[1] + m && z > r[2] - m && z < r[3] + m);
export const rampH = (r, x, z) => { const t = r[4] === 'x' ? (x - r[0]) / (r[1] - r[0]) : (z - r[2]) / (r[3] - r[2]); return r[5] + (r[6] - r[5]) * clamp(t, 0, 1); };

export class Level {
  // layout: a layout that passed validateLayout (layout.js)
  constructor(layout) {
    this.arena = layout.arena;
    this.boxes = layout.boxes.map(b => [b[0], b[1], b[2], b[3], b[4], b[5], b[6] === 'c' ? 'c' : 0]);
    this.ramps = layout.ramps.map(r => [r[0], r[1], r[2], r[3], r[4], r[5], r[6]]);
    this.holes = layout.holes.map(h => [h[0], h[1], h[2], h[3], 0, 0, h[4] === 'c' ? 'c' : 0]); // the game's own hole format
    this.pots = layout.pots.map(p => ({ x: p[0], y: p[1], z: p[2] }));
    this.powers = layout.powers.map(p => ({ x: p[0], y: p[1], z: p[2], kind: typeof p[3] === 'string' ? p[3] : null }));
    this.spawns = layout.spawns.map(s => ({ x: s[0], z: s[1], yaw: s[2], y: 0 }));
    this._build();
    for (const s of this.spawns) { const g = this.surfaceUnder(s.x, s.z, 50); s.y = g > -Infinity ? g : 0; }
  }
  _build() {
    const mk = () => { const g = new Array(QG_N * QG_N); for (let i = 0; i < g.length; i++) g[i] = EMPTY; return g; };
    this.qgB = mk(); this.qgR = mk(); this.qgH = mk();
    const add = (g, r) => {
      const i0 = Math.max(0, Math.floor((r[0] - QG_M + QG_O) / QG_C)), i1 = Math.min(QG_N - 1, Math.floor((r[1] + QG_M + QG_O) / QG_C));
      const j0 = Math.max(0, Math.floor((r[2] - QG_M + QG_O) / QG_C)), j1 = Math.min(QG_N - 1, Math.floor((r[3] + QG_M + QG_O) / QG_C));
      for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const k = j * QG_N + i; if (g[k] === EMPTY) g[k] = []; g[k].push(r); }
    };
    for (const b of this.boxes) add(this.qgB, b);
    for (const r of this.ramps) add(this.qgR, r);
    for (const h of this.holes) add(this.qgH, h);
  }
  _cell(g, x, z) { const i = Math.floor((x + QG_O) / QG_C), j = Math.floor((z + QG_O) / QG_C); return i < 0 || j < 0 || i >= QG_N || j >= QG_N ? EMPTY : g[j * QG_N + i]; }
  inArena(x, z) { return Math.abs(x) <= this.arena && Math.abs(z) <= this.arena; }
  floorAt(x, z) {
    if (Math.abs(x) > this.arena || Math.abs(z) > this.arena) return -Infinity;
    for (const h of this._cell(this.qgH, x, z)) if (inR(x, z, h)) return -Infinity;
    return 0;
  }
  // the highest walkable surface at (x, z) at or below maxY (-Infinity when there is none)
  surfaceUnder(x, z, maxY) {
    let best = -Infinity; const f = this.floorAt(x, z); if (f <= maxY) best = f;
    for (const b of this._cell(this.qgB, x, z)) if (b[5] <= maxY && b[5] > best && inR(x, z, b)) best = b[5];
    for (const r of this._cell(this.qgR, x, z)) if (inR(x, z, r)) { const h = rampH(r, x, z); if (h <= maxY && h > best) best = h; }
    return best;
  }
  // the game's own test: is a solid at body height here (used for movement, with the body's margin)
  blockedAt(x, z, y) {
    const m = G.PR * 0.9;
    for (const b of this._cell(this.qgB, x, z)) if (y < b[5] - G.STEP && y + 0.8 > b[4] && inR(x, z, b, m)) return true;
    for (const r of this._cell(this.qgR, x, z)) if (inR(x, z, r, m * 0.3)) { const h = rampH(r, clamp(x, r[0], r[1]), clamp(z, r[2], r[3])); if (y < h - G.STEP) return true; }
    return false;
  }
  // stricter test for the referee: is the centre of the body clearly inside a solid? A player the game moved legally
  // never is (the game keeps the centre at least 0.3 m from a wall), so this has no false alarms from rounding.
  insideSolid(x, z, y) {
    for (const b of this._cell(this.qgB, x, z)) if (y < b[5] - G.STEP - 0.12 && y + 0.8 > b[4] + 0.1 && inR(x, z, b, -0.06)) return true;
    for (const r of this._cell(this.qgR, x, z)) if (inR(x, z, r, -0.06) && y < rampH(r, x, z) - G.STEP - 0.12) return true;
    return false;
  }
  onRamp(x, z, m = 0.5) { for (const r of this._cell(this.qgR, x, z)) if (inR(x, z, r, m)) return true; return false; }
  // the surface you would be standing on at height y, or -Infinity when you are in the air over nothing
  supportAt(x, z, y) { return this.surfaceUnder(x, z, y + G.STEP + 0.05); }
}
