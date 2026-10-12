S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
P = S + '/tools/assets/axolife.js'; s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- the strokes flow through their marks: the sweep back runs on up into the tuck in one motion, the slide back of a planted hand runs on
# into the pull (a mark flagged 'pass' is passed through, not stopped at; a touchdown and a hold still come to rest)
rep("""const SWT = { 'hand.R': [[0, 'M'], [0.15, 'B'], [0.24, 'T'], [0.55, 'T'], [0.68, 'F', 1], [1, 'M']], 'hand.L': [[0, 'G'], [0.17, 'B'], [0.26, 'T'], [0.7, 'T'], [0.83, 'F', 1], [1, 'G']],
  'foot.L': [[0, 'M'], [0.14, 'B'], [0.24, 'T'], [0.56, 'T'], [0.69, 'F', 1], [1, 'M']], 'foot.R': [[0, 'M'], [0.14, 'B'], [0.24, 'T'], [0.71, 'T'], [0.84, 'F', 1], [1, 'M']] };""",
"""const SWT = { 'hand.R': [[0, 'M', 0, 1], [0.15, 'B', 0, 1], [0.25, 'T'], [0.55, 'T'], [0.68, 'F', 1], [1, 'M', 0, 1]], 'hand.L': [[0, 'G', 0, 1], [0.17, 'B', 0, 1], [0.27, 'T'], [0.7, 'T'], [0.83, 'F', 1], [1, 'G', 0, 1]],
  'foot.L': [[0, 'M', 0, 1], [0.14, 'B', 0, 1], [0.25, 'T'], [0.56, 'T'], [0.69, 'F', 1], [1, 'M', 0, 1]], 'foot.R': [[0, 'M', 0, 1], [0.14, 'B', 0, 1], [0.25, 'T'], [0.71, 'T'], [0.84, 'F', 1], [1, 'M', 0, 1]] };""")
rep("""const swMark = (en, u, arm, out) => { const k = SWT[en], K = SWK[arm ? 'arm' : 'leg']; let i = 0; while (i < k.length - 2 && u >= k[i + 1][0]) i++;
  const a = K[k[i][1]], b = K[k[i + 1][1]], x = clamp01((u - k[i][0]) / (k[i + 1][0] - k[i][0])), e = x * x * (3 - 2 * x), arc = k[i + 1][2] ? Math.sin(Math.PI * x) : 0;
  for (let j = 0; j < 4; j++) out[j] = a[j] + (b[j] - a[j]) * e; out[1] += (arm ? 0.05 : 0.035) * arc; out[4] = arc; return out; };""",
"""const swTan = (k, K, j, c) => { const n = k.length - 1; if (!k[j][3]) return 0; // (a mark passed through: its pace from the marks either side, round the cycle's end)
  const jp = j > 0 ? j - 1 : n - 1, jn = j < n ? j + 1 : 1, up = j > 0 ? k[jp][0] : k[jp][0] - 1, un = j < n ? k[jn][0] : k[jn][0] + 1;
  return 0.85 * (K[k[jn][1]][c] - K[k[jp][1]][c]) / (un - up); };
const swMark = (en, u, arm, out) => { const k = SWT[en], K = SWK[arm ? 'arm' : 'leg']; let i = 0; while (i < k.length - 2 && u >= k[i + 1][0]) i++;
  const a = K[k[i][1]], b = K[k[i + 1][1]], d = k[i + 1][0] - k[i][0], x = clamp01((u - k[i][0]) / d), arc = k[i + 1][2] ? Math.sin(Math.PI * x) : 0;
  const x2 = x * x, x3 = x2 * x, h00 = 2 * x3 - 3 * x2 + 1, h10 = x3 - 2 * x2 + x, h01 = 3 * x2 - 2 * x3, h11 = x3 - x2;
  for (let j = 0; j < 4; j++) out[j] = h00 * a[j] + h10 * d * swTan(k, K, i, j) + h01 * b[j] + h11 * d * swTan(k, K, i + 1, j);
  out[3] = clamp01(out[3]); out[1] += (arm ? 0.05 : 0.035) * arc; out[4] = arc; return out; };""")
# ---- the pull carries it forward: the body lunges ahead as the hands and feet drive back, then eases back to its place
rep("""    const sg = u < 0.22 ? smooth(u / 0.22) : u < 0.55 ? 1 - 0.15 * smooth((u - 0.22) / 0.33) : 0.85 * (1 - smooth((u - 0.55) / 0.45));
    out.root.z += (0.06 * sg - 0.03) * sl; out.root.y -= (0.012 + 0.022 * g) * sl;""",
"""    // (the pull carries it ahead in the world, quickest mid-pull; then it eases back to its place over the glide and the steps, slowly at
    // first, carrying the speed it got; and it gathers a touch as the hands reach for the next one)
    const lg = u < 0.26 ? (x => x * x * x * (10 - 15 * x + 6 * x * x))(u / 0.26) : 1 - smooth((u - 0.26) / 0.74), gat = u > 0.86 ? Math.sin(Math.PI * (u - 0.86) / 0.14) : 0;
    out.root.z += (0.2 * lg - 0.03 * gat) * sl; out.root.y -= (0.012 + 0.022 * g) * sl;
    if (u < (SL.pu === undefined ? 1 : SL.pu) && sl > 0.5) this.kickGills(0, -0.28 * sl); SL.pu = u; // (each pull: the gills swept back by the lunge, then springing out again)""")
# ---- the head's bob a little more: down into the pull, up through the glide, a nod with each step
rep("const hp = (0.07 * Math.sin(Math.PI * clamp01(u / 0.26)) - 0.03 * g + 0.025 * (1 - g) * Math.sin(th + 0.6)) * sl;",
    "const hp = (0.1 * Math.sin(Math.PI * clamp01(u / 0.26)) - 0.05 * g + 0.035 * (1 - g) * Math.sin(th + 0.6)) * sl;")
open(P, 'w').write(s); print('swim231 ok')
