"""v236 animator and adapter changes: the swim stroke drives the blob's real pace (a short slow beat as the limbs come out to reach, a surge
through the pull, a touch fast through the glide, a touch slow through the steps; averaging exactly 1 over the cycle, so the distance it
covers is unchanged); the body's own lunge on top of it smaller now the whole blob surges; and the gill spring back as it was for the
upright gills (the floppy settings wait for the new ears)."""
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
def edit(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:80]); s = s.replace(a, b)
    open(path, 'w').write(s)
edit(S + '/tools/assets/axolife.js', [
  ("if (!this.gillSpring2) { this.gillSpring2 = 1; this.gillSpring.k = 110; this.gillSpring.c = 7.5; } // (the gills hang like floppy ears: a slower, looser spring that lags, swings and settles)",
   "if (!this.gillSpring2) { this.gillSpring2 = 1; this.gillSpring.k = 230; this.gillSpring.c = 10; }"),
  ("add[j * 2] = -fl * 1.0 * (1 - L.act); add[j * 2 + 1] = swing * 40 * sgn + fl * 3 * (1 - L.act);",
   "add[j * 2] = -fl * 2.5 * (1 - L.act); add[j * 2 + 1] = swing * 24 * sgn + fl * 7 * (1 - L.act);"),
  ("    out.root.z += (0.2 * lg - 0.03 * gat) * sl;", "    out.root.z += (0.1 * lg - 0.03 * gat) * sl; /* (a smaller lunge of the body: the whole blob surges with the pull now, see strokeMul) */"),
  ("const swTan = (k, K, j, c) => {",
   """// the stroke's pace, for the game to move the blob by: a short slow beat as the limbs come out to reach, a surge through the pull, a touch
// fast through the glide, a touch slow through the steps; scaled to average exactly 1 over the cycle, so the distance covered is unchanged
const SWP = (() => { const k = [[0, 0.8], [0.12, 1.38], [0.26, 1.15], [0.45, 1.03], [0.6, 0.95], [0.82, 0.93], [0.92, 0.72]], n = k.length;
  const at = i => { const j = ((i % n) + n) % n, w = Math.floor(i / n); return [k[j][0] + w, k[j][1]]; }, tan = i => { const a = at(i - 1), b = at(i + 1); return (b[1] - a[1]) / (b[0] - a[0]); };
  const f = u => { u -= Math.floor(u); let i = n - 1; for (let j = 0; j < n - 1; j++) if (u >= k[j][0] && u < k[j + 1][0]) { i = j; break; } if (u < k[0][0]) i = -1;
    const a = at(i), b = at(i + 1), d = b[0] - a[0], uu = u < a[0] ? u + 1 : u, x = (uu - a[0]) / d, x2 = x * x, x3 = x2 * x;
    return (2 * x3 - 3 * x2 + 1) * a[1] + (x3 - 2 * x2 + x) * d * tan(i) + (3 * x2 - 2 * x3) * b[1] + (x3 - x2) * d * tan(i + 1); };
  let m = 0; for (let i = 0; i < 1000; i++) m += f(i / 1000); m /= 1000; return u => f(u) / m; })();
Animator.prototype.strokeMul = function () { const L = this.loco, Q = L && L.sl; return Q && L.slK > 0.001 ? 1 + (SWP(Q.u) - 1) * L.slK : 1; };
const swTan = (k, K, j, c) => {"""),
])
edit(S + '/tools/assets/axoc.js', [
  ("    A.update(dt);\n    // curled into a ball in flight it rolls over",
   "    A.update(dt); if (D) D.strokeK = A.strokeMul ? A.strokeMul() : 1; // (swimming: the blob's pace follows the stroke; the game moves it by this)\n    // curled into a ball in flight it rolls over"),
])
print('swim236 ok')
