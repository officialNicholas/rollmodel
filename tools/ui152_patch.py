#!/usr/bin/env python3
"""v224: the axolotl's climb out of the basin at the start, made for its hands and its lizard's body (tools/assets/axolife.js: the body and
its steps follow the ground under them; tools/assets/axoc.js: the basin's shape as that ground). It comes up out of the paint low, its tail
curled round inside the tub; its head comes over the rim and one hand reaches over and down the outside to the floor, then the other; its
body drapes over the rim as it hauls itself out, slowing for the effort, the hind feet stepping up onto the rim and over; its tail lifts over
the rim behind it and comes down off it. The tub's real shape (it's oval) is read off its meshes; the climb takes two seconds, starting a
little sooner so it's out before Go."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui151_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'M.terrain' in s and 'o.climb' in s, 'the climbing runtime is not in the build'
HELP = r"""
// ---------- the axolotl's climb out: the tub's own shape (an oval: its outside, the paint inside, the rim's height, read off its meshes in
// its own frame), how far out its rim is along the way out, and the way out itself: up out of the paint toward the rim, slow while it hauls
// itself over, easing off onto the floor ----------
function tubDims(p) {
  if (p.tubD) return p.tubD; const g = p.g; g.updateMatrixWorld(true); const inv = new THREE.Matrix4().copy(g.matrixWorld).invert(), m = new THREE.Matrix4(), b = new THREE.Box3();
  let ao = 0, bo = 0, ox = 0, oz = 0, top = 0, ai = 0, bi = 0, liq = 0;
  g.traverse(o => { if (!o.isMesh || !o.geometry) return; if (!o.geometry.boundingBox) o.geometry.computeBoundingBox(); b.copy(o.geometry.boundingBox).applyMatrix4(m.multiplyMatrices(inv, o.matrixWorld)); const hx = (b.max.x - b.min.x) / 2, hz = (b.max.z - b.min.z) / 2;
    if (o === p.liq) { ai = hx; bi = hz; liq = (b.max.y + b.min.y) / 2; return; }
    if (b.min.y < 0.12 && b.max.y > 0.35 && b.max.y < 0.9 && hx < 0.95 && hz < 0.95 && hx > 0.3) { if (hx > ao) { ao = hx; ox = (b.max.x + b.min.x) / 2; } if (hz > bo) { bo = hz; oz = (b.max.z + b.min.z) / 2; } top = Math.max(top, b.max.y); } });
  return (p.tubD = { ao: ao || 0.62, bo: bo || 0.77, ox, oz, ai: (ai || 0.46) + 0.02, bi: (bi || 0.61) + 0.02, top: top || 0.5, liq: liq || 0.42 });
}
function tubExit(p, fx, fz) { const d = tubDims(p), q = new THREE.Quaternion(); p.g.getWorldQuaternion(q); const v = new THREE.Vector3(fx, 0, fz).applyQuaternion(q.invert()); return { rw: 1 / Math.hypot(v.x / d.ao, v.z / d.bo), rin: 1 / Math.hypot(v.x / d.ai, v.z / d.bi) }; }
function crawlTable(s0, rw, s1, T) {
  const N = 96, ss = [], ts = [0], sm = smoothstep; let tt = 0;
  const v = x => (0.3 + 0.7 * sm(s0, s0 + 0.5, x)) * (0.12 + 0.88 * (1 - sm(s1 - 1.0, s1, x))) * (1 - 0.7 * Math.exp(-Math.pow((x - (rw - 0.3)) / 0.45, 2)));
  for (let i = 0; i <= N; i++) ss.push(s0 + (s1 - s0) * i / N);
  for (let i = 1; i <= N; i++) { tt += (ss[i] - ss[i - 1]) / v((ss[i] + ss[i - 1]) / 2); ts.push(tt); }
  for (let i = 0; i <= N; i++) ts[i] *= T / tt;
  return t => { if (t <= 0) return s0; if (t >= T) return s1; let lo = 0, hi = N; while (hi - lo > 1) { const k = (lo + hi) >> 1; if (ts[k] <= t) lo = k; else hi = k; } return ss[lo] + (ss[hi] - ss[lo]) * (t - ts[lo]) / (ts[hi] - ts[lo]); };
}
// what the axolotl's body is told of the ground under it, this frame
function climbOf(D) {
  const C = D.introCrawl, p = C.p, d = tubDims(p); p.g.updateMatrixWorld(true); const inv = C.inv || (C.inv = new THREE.Matrix4()); inv.copy(p.g.matrixWorld).invert(); const gy = p.g.matrixWorld.elements[13];
  const c = C.cl || (C.cl = {}); c.inv = inv; c.ao = d.ao; c.bo = d.bo; c.ox = d.ox; c.oz = d.oz; c.ai = d.ai; c.bi = d.bi; c.top = gy + d.top; c.liq = gy + d.liq; c.deep = 0.3; c.sink = C.sink; c.floor = D.y;
  c.tailK = smoothstep(C.rw2 - 0.45, C.rw2 - 0.05, C.s); c.curl = 1 - smoothstep(C.rw2 - 0.9, C.rw2 - 0.3, C.s); return c;
}
"""
rep("function introCrawl(D) {", HELP.lstrip('\n') + "function introCrawl(D) {")
rep("  D.introCrawl = { t: 0, p, cx: p.x, cz: p.z, fx, fz, rw: R.rw, rimH: R.h, lq: R.lq, s0: -0.35, s1, s: -0.35, sink: 1.3, rim: [0, R.h / K, 0.42, 1], popped: false, liz: 0, curl: 0 };",
    "  D.introCrawl = { t: 0, p, cx: p.x, cz: p.z, fx, fz, rw: R.rw, rimH: R.h, lq: R.lq, s0: -0.35, s1, s: -0.35, sink: 1.3, rim: [0, R.h / K, 0.42, 1], popped: false, liz: 0, curl: 0 };\n"
    "  { const V = vOf(D); if (V && V.slime && V.slime.kind === 'axo') { const E = tubExit(p, fx, fz), C = D.introCrawl; C.rw2 = E.rw; C.s0 = C.s = 0.37 - E.rin; C.s1 = E.rw + CRAWL_PAST; C.T = 1.85; C.path = crawlTable(C.s0, E.rw, C.s1, C.T);\n"
    "    D.y = Math.max(0, surfaceUnder(p.x + fx * C.s1, p.z + fz * C.s1, p.y + 1, true)); } } // (the axolotl: the tub's own shape, its hips just inside the back of the paint to start)")
rep("  D.x = p.x - fx * 0.35; D.z = p.z - fz * 0.35;", "  D.x = p.x + fx * D.introCrawl.s0; D.z = p.z + fz * D.introCrawl.s0;")
rep("e = uc * uc * uc * (uc * (6 * uc - 15) + 10), sPrev = C.s; C.s = C.s0 + (C.s1 - C.s0) * e;",
    "e = uc * uc * uc * (uc * (6 * uc - 15) + 10), sPrev = C.s; C.s = C.path ? C.path(C.t - CRAWL_RISE * 0.45) : C.s0 + (C.s1 - C.s0) * e;")
rep("  if (!C.popped && C.s > C.rw - 0.1) {", "  if (!C.popped && C.s > (C.rw2 || C.rw) - 0.1) {")
rep("  if (C.s > C.rw + 0.25) { D.dist", "  if (C.s > (C.rw2 || C.rw) + 0.25) { D.dist")
rep("  if (C.t < CRAWL_RISE * 0.45 + CRAWL_T) return;", "  if (C.t < CRAWL_RISE * 0.45 + (C.T || CRAWL_T)) return;")
rep("  else if (D.introCrawl) V.sink = D.introCrawl.sink;", "  else if (D.introCrawl) V.sink = I.kind === 'axo' && D.introCrawl.path ? 0 : D.introCrawl.sink; // (the axolotl: down in the paint by its own climb, not lowered whole)")
rep("  o.lizard = D.introCrawl ? D.introCrawl.liz : 0;", "  o.climb = I.kind === 'axo' && D.introCrawl && D.introCrawl.path ? climbOf(D) : null;\n  o.lizard = D.introCrawl ? D.introCrawl.liz : 0;")
rep("D.leapAt = D.popAt + (D === P ? 0.85 : 0.8 + Math.random() * 0.08);", "D.leapAt = D.popAt + (D === P ? 0.85 : 0.8 + Math.random() * 0.08) - (D.introKind === 'climb' ? 0.2 : 0); /* (the climb takes longer now: it starts a little sooner) */")
rep('<p class="ver">Version 223</p>', '<p class="ver">Version 224</p>')
open(DST, 'w').write(s)
print('ui152 ok', n0, '->', len(s))
