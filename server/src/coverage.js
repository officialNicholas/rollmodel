// Coverage: the server's own paint grid. Like the game it counts paint on every walkable surface: the floor (minus holes,
// pieces standing on it and ramps), the tops of pieces, and ramps. Floor cells are a dense grid; tops and ramps are a
// short list of samples with a coarse index. Each sample remembers the colour that painted it last.
import { inR, rampH } from './geometry.js';

const BARE = 0, NONE = 255, DY = 0.35, BUCKET = 1;

export class Coverage {
  // level: geometry.Level, sides: side of each colour (colour = player slot), cell: sample spacing in metres
  constructor(level, sides, cell = 0.25) {
    this.L = level; this.A = level.arena; this.S = cell; this.sides = sides.slice(); this.nColors = sides.length;
    const A = this.A, S = cell, N = this.N = Math.ceil(2 * A / S);
    this.floor = new Uint8Array(N * N);
    let paintable = 0;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const x = -A + (i + 0.5) * S, z = -A + (j + 0.5) * S;
      let ok = level.floorAt(x, z) === 0;
      if (ok) for (const b of level._cell(level.qgB, x, z)) if (b[4] === 0 && inR(x, z, b)) { ok = false; break; }
      if (ok) for (const r of level._cell(level.qgR, x, z)) if (inR(x, z, r)) { ok = false; break; }
      this.floor[j * N + i] = ok ? BARE : NONE; if (ok) paintable++;
    }
    // tops and ramps
    const ex = [], ey = [], ez = [];
    for (const b of level.boxes) for (let x = b[0] + S / 2; x < b[1]; x += S) for (let z = b[2] + S / 2; z < b[3]; z += S) if (b[6] !== 'c' || inR(x, z, b)) { ex.push(x); ey.push(b[5]); ez.push(z); }
    for (const r of level.ramps) for (let x = r[0] + S / 2; x < r[1]; x += S) for (let z = r[2] + S / 2; z < r[3]; z += S) { ex.push(x); ey.push(rampH(r, x, z)); ez.push(z); }
    this.ex = Float32Array.from(ex); this.ey = Float32Array.from(ey); this.ez = Float32Array.from(ez); this.eo = new Uint8Array(ex.length);
    const M = this.M = Math.ceil(2 * (A + 2) / BUCKET), buckets = Array.from({ length: M * M }, () => []);
    for (let k = 0; k < ex.length; k++) buckets[this._b(ex[k], ez[k])].push(k);
    this.bk = buckets.map(b => (b.length ? Int32Array.from(b) : null));
    this.total = paintable + ex.length;
    this.count = new Int32Array(this.nColors);
  }
  _b(x, z) { const M = this.M, o = this.A + 2, i = Math.min(M - 1, Math.max(0, Math.floor((x + o) / BUCKET))), j = Math.min(M - 1, Math.max(0, Math.floor((z + o) / BUCKET))); return j * M + i; }
  _set(arr, k, v) { const o = arr[k]; if (o === v) return 0; if (o !== BARE) this.count[o - 1]--; arr[k] = v; this.count[v - 1]++; return 1; }
  // paint a disc of radius r around (x, z) on surfaces within 0.35 m of height y. Returns how many samples changed.
  stamp(x, y, z, r, color) {
    if (!(color >= 0 && color < this.nColors) || !(r > 0)) return 0;
    const v = color + 1, r2 = r * r, A = this.A, S = this.S, N = this.N; let changed = 0;
    if (Math.abs(y) < DY) {
      const i0 = Math.max(0, Math.floor((x - r + A) / S)), i1 = Math.min(N - 1, Math.floor((x + r + A) / S));
      const j0 = Math.max(0, Math.floor((z - r + A) / S)), j1 = Math.min(N - 1, Math.floor((z + r + A) / S));
      for (let j = j0; j <= j1; j++) {
        const cz = -A + (j + 0.5) * S - z, row = j * N;
        for (let i = i0; i <= i1; i++) {
          const k = row + i, o = this.floor[k]; if (o === NONE || o === v) continue;
          const cx = -A + (i + 0.5) * S - x; if (cx * cx + cz * cz < r2) changed += this._set(this.floor, k, v);
        }
      }
    }
    const M = this.M, o = A + 2;
    const bi0 = Math.max(0, Math.floor((x - r + o) / BUCKET)), bi1 = Math.min(M - 1, Math.floor((x + r + o) / BUCKET));
    const bj0 = Math.max(0, Math.floor((z - r + o) / BUCKET)), bj1 = Math.min(M - 1, Math.floor((z + r + o) / BUCKET));
    for (let j = bj0; j <= bj1; j++) for (let i = bi0; i <= bi1; i++) {
      const list = this.bk[j * M + i]; if (!list) continue;
      for (const k of list) {
        if (this.eo[k] === v || Math.abs(this.ey[k] - y) >= DY) continue;
        const dx = this.ex[k] - x, dz = this.ez[k] - z; if (dx * dx + dz * dz < r2) changed += this._set(this.eo, k, v);
      }
    }
    return changed;
  }
  // a trail: stamps every `spacing` metres along the segment, like the game's trail points
  stampPath(x0, y0, z0, x1, y1, z1, r, color, spacing = 0.12) {
    const d = Math.hypot(x1 - x0, z1 - z0), n = Math.max(1, Math.ceil(d / spacing)); let changed = 0;
    for (let s = 1; s <= n; s++) { const k = s / n; changed += this.stamp(x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, z0 + (z1 - z0) * k, r, color); }
    return changed;
  }
  // the colour of the surface right at (x, y, z), -1 when bare or nothing paintable is there
  colorAt(x, y, z) {
    const A = this.A, S = this.S, N = this.N;
    if (Math.abs(y) < DY) {
      const i = Math.floor((x + A) / S), j = Math.floor((z + A) / S);
      if (i >= 0 && j >= 0 && i < N && j < N) { const o = this.floor[j * N + i]; if (o !== NONE) return o === BARE ? -1 : o - 1; }
    }
    const list = this.bk[this._b(x, z)]; let best = 0.3 * 0.3, c = -1;
    if (list) for (const k of list) { if (Math.abs(this.ey[k] - y) >= DY) continue; const dx = this.ex[k] - x, dz = this.ez[k] - z, d = dx * dx + dz * dz; if (d < best) { best = d; c = this.eo[k] ? this.eo[k] - 1 : -1; } }
    return c;
  }
  sideAt(x, y, z) { const c = this.colorAt(x, y, z); return c < 0 ? -1 : this.sides[c]; }
  // coverage in percent: by colour (player slot) and by side (team)
  colors() { return Array.from(this.count, n => (this.total ? n / this.total * 100 : 0)); }
  bySide() {
    const n = Math.max(...this.sides) + 1, out = new Array(n).fill(0);
    for (let c = 0; c < this.nColors; c++) out[this.sides[c]] += this.total ? this.count[c] / this.total * 100 : 0;
    return out;
  }
}
