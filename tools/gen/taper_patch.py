# the trail's newest stretch tapers in toward the blob laying it, so the paint looks like it flows out from under it
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

OLD = src[src.index('function addPoint(x, y, z, yaw, t, stroke, wmul, team, rb) {'):src.index('// landing splats, projected onto whatever surface is under each point')]
NEW = r"""// the newest stretch of a trail tapers in toward the blob laying it, so the paint looks like it's flowing out from under it rather than
// starting from nowhere: each point remembers where its edges sit at full width, the last few are drawn pulled in toward the middle (the
// newest most), and each lets out a notch as the next is laid ahead of it. A roller or a giant lays its full width straight away
const TAPER_N = 9, TAPER_TIP = 0.3; let trailGen = 0;
const taperF = (a, k) => 1 - (1 - TAPER_TIP) * k * Math.pow(Math.max(0, 1 - a / TAPER_N), 2);
const taperV = (o, k, v) => { const j = (o + k) * 3; vPos[j] = v[0]; vPos[j + 1] = v[1]; vPos[j + 2] = v[2]; };
function taperPut(h, f) {
  h.f = f; const w = h.hw * f, L = h.L, R = h.R;
  L[0] = h.x - h.rx * w; L[1] = h.yC + (h.yL - h.yC) * f; L[2] = h.z - h.rz * w;
  R[0] = h.x + h.rx * w; R[1] = h.yC + (h.yR - h.yC) * f; R[2] = h.z + h.rz * w;
  // in the segment that ends at it, its left edge is vertex 2 and 5, its right 10; in the one that starts from it, left 0, right 7 and 9
  if (h.o >= 0) { taperV(h.o, 2, L); taperV(h.o, 5, L); taperV(h.o, 10, R); }
  if (h.o2 >= 0) { taperV(h.o2, 0, L); taperV(h.o2, 7, R); taperV(h.o2, 9, R); }
}
function addPoint(x, y, z, yaw, t, stroke, wmul, team, rb) {
  if (nP >= MAXP) return;
  team = team || 0; rb = rb || RB0;
  const W = TW * (wmul || 1), d = nP * SPACING, lift = nextLift(1);
  pX[nP] = x; pY[nP] = y; pZ[nP] = z; pT[nP] = t; pR[nP] = W / 2 * 0.85 + PR * 0.3; pTeam[nP] = team % 3; nP++;
  const hw = (W / 2) * 1.16 * (0.86 + 0.28 * (0.5 + 0.5 * Math.sin(d * 1.9 + 2 * Math.sin(d * 0.57))));
  const rx = -Math.cos(yaw), rz = Math.sin(yaw), yC = y + 0.016 + lift;
  const h = { x, z, rx, rz, hw, yC, yL: hugY(x - rx * hw, z - rz * hw, y) + 0.008 + lift, yR: hugY(x + rx * hw, z + rz * hw, y) + 0.008 + lift, L: [x, yC, z], C: [x, yC, z], R: [x, yC, z], o: -1, o2: -1, f: -1, k: (wmul || 1) > 1.5 ? 0 : 1 };
  if (stroke !== rb.stroke || rb.gen !== trailGen || !rb.hist) { rb.hist = []; rb.gen = trailGen; }
  const Hs = rb.hist, p = Hs.length ? Hs[Hs.length - 1] : null;
  if (p && nV + VPS <= MAXV) {
    // the segment from the last point to this one (its edges are filled in just below, where the taper puts them)
    const o = nV, E = [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0];
    for (let k = 0; k < VPS; k++) { vEdge[o + k] = E[k]; vBirth[o + k] = t; vTeamA[o + k] = team; }
    for (const k of [1, 3, 6]) taperV(o, k, p.C); for (const k of [4, 8, 11]) taperV(o, k, h.C);
    p.o2 = o; h.o = o; nV += VPS;
  }
  Hs.push(h); if (Hs.length > TAPER_N + 1) Hs.shift();
  let lo = dirtyV;
  for (let a = 0; a < Hs.length; a++) { const q = Hs[Hs.length - 1 - a], f = taperF(a, q.k); if (f === q.f && q !== p) continue; taperPut(q, f); if (q.o >= 0 && q.o < lo) lo = q.o; else if (q.o < 0 && q.o2 >= 0 && q.o2 < lo) lo = q.o2; }
  dirtyV = lo; rb.stroke = stroke;
  stamp(x, y, z, W / 2, team);
  if (nP === 1) addSplat(x, y, z, yaw, TW * 0.52, t, true, false, team);
}
"""
src = src.replace(OLD, NEW)
rep("const RB0 = { L: null, C: null, R: null, stroke: -1 }; // each blob keeps its own ribbon so two trails never stitch together",
    "const RB0 = { stroke: -1 }; // each blob keeps its own ribbon so two trails never stitch together")
rep("  clearSplashes(); nP = 0; dryP = 0; nV = 0; dirtyV = 0; RB0.stroke = -1;", "  clearSplashes(); nP = 0; dryP = 0; nV = 0; dirtyV = 0; RB0.stroke = -1; trailGen++;")
rep("rb: { L: null, C: null, R: null, stroke: -1 },", "rb: { stroke: -1 },")
open(P, 'w').write(src)
print('ok')
