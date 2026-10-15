// Test stages in the layout format the game uploads. A small seeded generator in the spirit of the game's own (point
// symmetric, a centrepiece with ramps, walls, blocks, a floating pad, pits, pots, power spots, spawns), plus a few
// hand-made stages for focused tests. Clients "generate" the stage from the seed the server sends, like the game will.
import { rng } from '../../src/util.js';
import { Level } from '../../src/geometry.js';

const q = v => Math.round(v * 20) / 20;

export function genLayout(seed, arena = 26.4, { players = 4 } = {}) {
  const R = rng(seed >>> 0), rr = (a, b) => a + (b - a) * R();
  const A = arena, boxes = [], ramps = [], holes = [], foot = [];
  const free = (r, gap) => r[0] > -A + 2.5 && r[1] < A - 2.5 && r[2] > -A + 2.5 && r[3] < A - 2.5 && !foot.some(f => r[0] < f[1] + gap && r[1] > f[0] - gap && r[2] < f[3] + gap && r[3] > f[2] - gap);
  const spawnClear = r => spawnsOf(A).every(s => Math.max(r[0] - s[0], s[0] - r[1], 0) ** 2 + Math.max(r[2] - s[1], s[1] - r[3], 0) ** 2 > 36);
  const twin = r => [-r[1], -r[0], -r[3], -r[2]];
  const place = (r, gap, fn) => { const t = twin(r); if (!free(r, gap) || !free(t, gap) || !spawnClear(r) || !spawnClear(t)) return false; if (r[0] < t[1] + gap && r[1] > t[0] - gap && r[2] < t[3] + gap && r[3] > t[2] - gap) return false; foot.push(r, t); fn(r); fn(t); return true; };
  // centrepiece: a plateau with ramps on two opposite sides
  { const w = q(rr(5, 7)), d = q(rr(4.4, 6)), h = q(rr(1.2, 1.5)), b = [-w / 2, w / 2, -d / 2, d / 2];
    boxes.push([b[0], b[1], b[2], b[3], 0, h]); const L = q(h / 0.4), rw = q(rr(2.2, 3));
    ramps.push([b[1], q(b[1] + L), -rw / 2, rw / 2, 'x', h, 0], [q(b[0] - L), b[0], -rw / 2, rw / 2, 'x', 0, h]);
    foot.push([q(b[0] - L - 1), q(b[1] + L + 1), b[2] - 0.5, b[3] + 0.5]); }
  const kinds = [
    () => { const L = q(rr(3.3, 6.6)), t = 1.1, h = q(rr(0.85, 0.95)), x = rr(-A + 4, A - 4), z = rr(-A + 4, A - 4), along = R() < 0.5;
      const r = along ? [q(x - L / 2), q(x + L / 2), q(z - t / 2), q(z + t / 2)] : [q(x - t / 2), q(x + t / 2), q(z - L / 2), q(z + L / 2)];
      return place(r, 2.2, k => boxes.push([...k, 0, h])); },
    () => { const s = q(rr(2.2, 4.4)), h = q(rr(0.8, 1.0)), x = rr(-A + 4, A - 4), z = rr(-A + 4, A - 4), r = [q(x - s / 2), q(x + s / 2), q(z - s / 2), q(z + s / 2)], round = R() < 0.4;
      return place(r, 2.2, k => boxes.push(round ? [...k, 0, h, 'c'] : [...k, 0, h])); },
    () => { const s = q(rr(3.3, 5)), y0 = q(rr(0.92, 1.0)), x = rr(-A + 5, A - 5), z = rr(-A + 5, A - 5), r = [q(x - s / 2), q(x + s / 2), q(z - s / 2), q(z + s / 2)];
      return place(r, 2.6, k => boxes.push([...k, y0, q(y0 + 0.3)])); },
    () => { const w = q(rr(3.3, 6)), d = q(rr(3.3, 5)), x = rr(-A + 5, A - 5), z = rr(-A + 5, A - 5), r = [q(x - w / 2), q(x + w / 2), q(z - d / 2), q(z + d / 2)];
      return place(r, 2.6, k => holes.push(k)); },
    () => { const rad = q(rr(1.8, 2.8)), x = q(rr(-A + 5, A - 5)), z = q(rr(-A + 5, A - 5)), r = [x - rad, x + rad, z - rad, z + rad];
      return place(r, 2.6, k => holes.push([...k, 'c'])); },
  ];
  const want = [4, 3, 1, 2, 1];
  want.forEach((n, i) => { let got = 0; for (let t = 0; t < 60 && got < n; t++) if (kinds[i]()) got++; });
  const lv = new Level({ arena: A, boxes, ramps, holes, pots: [[0, 0, 0]], powers: [], spawns: spawnsOf(A) });
  // pots and power spots on open floor, away from the spawns and from each other
  const open = (x, z, m) => { for (let a = 0; a < 8; a++) { const px = x + Math.sin(a * 0.785) * m, pz = z + Math.cos(a * 0.785) * m; if (lv.surfaceUnder(px, pz, 0.3) !== 0 || lv.blockedAt(px, pz, 0)) return false; } return lv.surfaceUnder(x, z, 0.3) === 0 && !lv.onRamp(x, z, 1); };
  const spots = (n, minGap, m) => { const out = []; for (let t = 0; t < 2000 && out.length < n; t++) { const x = q(rr(-A + 3, A - 3)), z = q(rr(-A + 3, A - 3)); if (!open(x, z, m) || !open(-x, -z, m)) continue; if (spawnsOf(A).some(s => Math.hypot(s[0] - x, s[1] - z) < 4 || Math.hypot(s[0] + x, s[1] + z) < 4)) continue; if (out.some(p => Math.hypot(p[0] - x, p[2] - z) < minGap || Math.hypot(p[0] + x, p[2] + z) < minGap)) continue; if (Math.hypot(x, z) < 2) continue; out.push([x, 0, z], [-x, 0, -z]); } return out; };
  const pots = spots(8, 6, 1.2), powers = spots(8, 5, 0.9).map((p, i) => (i < 4 ? [...p, 'roller'] : p));
  return { arena: A, boxes, ramps, holes, pots, powers, spawns: spawnsOf(A).slice(0, Math.max(players, 2)) };
}
// spawn spots facing the middle (like the game's START / CSTART / CSTART2 / CSTART3)
export function spawnsOf(A) {
  const d = A - 6;
  return [[0, -d, 0], [0, d, Math.PI], [d, 0, -Math.PI / 2], [-d, 0, Math.PI / 2]].map(s => [s[0], s[1], +s[2].toFixed(4)]);
}

// an open floor with one wall, one box to climb, a pit, and pots: for focused referee tests
export function flatLayout(arena = 26.4) {
  return {
    arena,
    boxes: [[-1, 1, 4, 10, 0, 0.9], [8, 12, -12, -8, 0, 1.2]], // a wall in front of spawn 0's line, a box to hop on
    ramps: [], holes: [[-14, -10, -2, 2], [14, 18, 10, 14, 'c']],
    pots: [[-6, 0, -6], [6, 0, 6], [-6, 0, 6], [6, 0, -6]], powers: [[0, 0, -4], [0, 0, 4], [10, 0, 0], [-10, 0, 0]],
    spawns: spawnsOf(arena),
  };
}
