import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
P = S + '/tools/assets/axolife.js'; s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- constants: the stroke cycle's timeline
rep("const SLITHER = { on: 4.4, off: 3.2, after: 0.45, f0: 0.75, f1: 0.3, pw: 0.34, tail: 22 }; // (f0 + f1: strokes a second at cruising speed; pw: the push's share of a stroke)",
"""const SLITHER = { on: 4.4, off: 3.2, after: 0.45, T0: 1.75, T1: 1.4 }; // (T0 / T1: a stroke cycle's length in seconds, just up to speed / at full tilt)
// one stroke cycle, u from 0 to 1: both hands pull it forward (0 to 0.25: the hands sweep back along the ground, the feet kick back), it
// glides with everything along its sides (to 0.55), slows a touch and crawls two steps (a hand and the opposite foot, then the other
// pair, each reaching forward and taking hold), and pulls again. Each limb's marks through the cycle: [u, mark, swing (lifted over)]
const SWK = { arm: { F: [0.26, 0, 0.18, 0], G: [0.27, 0, 0.09, 0], M: [0.28, 0, 0.0, 0], B: [0.2, 0.012, -0.16, 0], T: [0.05, 0.045, -0.25, 1] }, // [out, up, along, tucked]
  leg: { F: [0.17, 0, 0.06, 0], M: [0.18, 0, -0.06, 0], B: [0.1, 0.02, -0.24, 0], T: [0.035, 0.035, -0.28, 1] } };
const SWT = { 'hand.R': [[0, 'M'], [0.15, 'B'], [0.24, 'T'], [0.55, 'T'], [0.68, 'F', 1], [1, 'M']], 'hand.L': [[0, 'G'], [0.17, 'B'], [0.26, 'T'], [0.7, 'T'], [0.83, 'F', 1], [1, 'G']],
  'foot.L': [[0, 'M'], [0.14, 'B'], [0.24, 'T'], [0.56, 'T'], [0.69, 'F', 1], [1, 'M']], 'foot.R': [[0, 'M'], [0.14, 'B'], [0.24, 'T'], [0.71, 'T'], [0.84, 'F', 1], [1, 'M']] };
const swMark = (en, u, arm, out) => { const k = SWT[en], K = SWK[arm ? 'arm' : 'leg']; let i = 0; while (i < k.length - 2 && u >= k[i + 1][0]) i++;
  const a = K[k[i][1]], b = K[k[i + 1][1]], x = clamp01((u - k[i][0]) / (k[i + 1][0] - k[i][0])), e = x * x * (3 - 2 * x), arc = k[i + 1][2] ? Math.sin(Math.PI * x) : 0;
  for (let j = 0; j < 4; j++) out[j] = a[j] + (b[j] - a[j]) * e; out[1] += (arm ? 0.05 : 0.035) * arc; out[4] = arc; return out; };""")
# ---- going in and coming out: in on a reach before a pull; out (slowing) only once it is into its crawl steps
rep("""  const SL = L.sl || (L.sl = { k: 0, on: false, was: false, hold: 0, u: 0, tph: 0, push: 0, reach: 0 });
  { const vc = L.vc, ok = !air && !TR && M.spin === undefined && !((M.climbCurl || 0) > 0) && !((M.ball || 0) > 0.05) && L.ballK < 0.05;
    if (ok && vc > SLITHER.on) SL.hold += dt; else if (!ok || vc < SLITHER.off) SL.hold = 0;
    SL.on = ok && (SL.on ? vc > SLITHER.off : SL.hold > SLITHER.after);
    if (SL.on && !SL.was) SL.u = 0; SL.was = SL.on; // (it goes in on a push)
    SL.k += ((SL.on ? 1 : 0) - SL.k) * Math.min(1, dt * (SL.on ? 4.5 : 6)); }""",
"""  const SL = L.sl || (L.sl = { k: 0, on: false, hold: 0, u: 0, m: new Float32Array(5), g: 0 });
  { const vc = L.vc, ok = !air && !TR && M.spin === undefined && !((M.climbCurl || 0) > 0) && !((M.ball || 0) > 0.05) && L.ballK < 0.05;
    if (ok && vc > SLITHER.on) SL.hold += dt; else if (!ok || vc < SLITHER.off) SL.hold = 0;
    const want = ok && (SL.on ? vc > SLITHER.off : SL.hold > SLITHER.after);
    if (want && !SL.on) { SL.on = true; if (SL.k < 0.05) SL.u = 0.86; } // (in from the crawl: it reaches forward and takes hold, then the first pull)
    else if (!want && SL.on && (!ok || vc < 1.5 || (SL.u > 0.58 && SL.u < 0.9))) SL.on = false; // (slowing: it swims on into its crawl steps, and the crawl takes over from there)
    SL.k += ((SL.on ? 1 : 0) - SL.k) * Math.min(1, dt * (SL.on ? 3.6 : 4.2)); }""")
# ---- turning while it swims: the upper body stays nearly straight, the bend goes low in the trunk and into the tail's C; the arms steer
rep("  const T = 50 * Math.tanh((-amp * c1 + bend * 0.92 + HT * 0.45) / 50);",
    "  const bU = bend * (1 - 0.6 * sl), T = 50 * Math.tanh((-amp * c1 + bU * 0.92 + HT * 0.45 * (1 - 0.5 * sl)) / 50);")
rep("  this.worldTurn(out, I.neck, hs * 0.25 + bend * 0.1 + HT * 0.3, -HT * 0.12);\n  this.worldTurn(out, I.head, hs * 0.25 + bend * 0.07 + HT * 0.25, -HT * 0.3);",
    "  this.worldTurn(out, I.neck, hs * 0.25 + bU * 0.1 + HT * 0.3 * (1 - 0.5 * sl), -HT * 0.12);\n  this.worldTurn(out, I.head, hs * 0.25 + bU * 0.07 + HT * 0.25 * (1 - 0.5 * sl), -HT * 0.3);")
# ---- the body through the stroke
i0 = s.index("  if (sl > 0.001) { // (a stroke: u runs 0 to 1"); i1 = s.index("  // the body over uneven ground (climbing out of a basin)")
s = s[:i0] + """  if (sl > 0.001) {
    const vk = clamp01((L.vc - SLITHER.on) / 3.6), u = SL.u = (SL.u + dt / (SLITHER.T0 + (SLITHER.T1 - SLITHER.T0) * vk)) % 1;
    // how far into the glide it is (the limbs' tuck, all four averaged): the wave is fullest there, smaller through the steps and the pull
    let g = 0; for (const l of L.limbs) g += swMark(l.en, u, l.arm, SL.m)[3] * 0.25; SL.g = g;
    // the wave: the lower and middle trunk and the tail swing most, the chest hardly, the head held to the way it's going. Each part's own
    // heading (degrees) along a wave running back from the shoulders to the tail tip, two to a cycle; each joint turns by the difference
    const th = 4 * Math.PI * u, env = sl * (0.5 + 0.5 * g), AB = [[I.head, 0.3], [I.neck, 0.6], [sp[3], 1.3], [sp[2], 3.4], [sp[1], 6], [I.hips, 8.5]];
    const hd = k => Math.sin(th - k * 0.55); let prev = 0;
    for (let k = AB.length - 1; k >= 0; k--) { const a = AB[k][1] * env * hd(k); this.worldTurn(out, AB[k][0], k === AB.length - 1 ? a : a - prev, 0); prev = k === AB.length - 1 ? a : prev; }
    { let up = AB[AB.length - 1][1] * env * hd(AB.length - 1); for (let k = AB.length - 2; k >= 0; k--) { const a = AB[k][1] * env * hd(k); this.worldTurn(out, AB[k][0], a - up, 0); up = a; } }
    // round a turn, the bend low in the trunk (the tail takes it on in a C; see the secondary motion)
    this.worldTurn(out, sp[1], bend * 0.3 * sl, 0); this.worldTurn(out, sp[2], bend * 0.12 * sl, 0);
    // the surge: forward with the pull, carried through the glide, easing back a touch as it slows into its steps; the belly down on the glide
    const sg = u < 0.22 ? smooth(u / 0.22) : u < 0.55 ? 1 - 0.15 * smooth((u - 0.22) / 0.33) : 0.85 * (1 - smooth((u - 0.55) / 0.45));
    out.root.z += (0.06 * sg - 0.03) * sl; out.root.y -= (0.012 + 0.022 * g) * sl;
    // the head: a little dip into each pull, up and steady through the glide, a small nod with each step; the chest rides it gently
    const hp = (0.07 * Math.sin(Math.PI * clamp01(u / 0.26)) - 0.03 * g + 0.025 * (1 - g) * Math.sin(th + 0.6)) * sl;
    this.pitchTurn(out, sp[3], 0.3 * hp); this.pitchTurn(out, I.neck, 0.5 * hp); this.pitchTurn(out, I.head, 0.45 * hp); }
""" + s[i1:]
# (the pre-pass above sets the hips first; drop the first loop, which was a draft)
s = s.replace("    for (let k = AB.length - 1; k >= 0; k--) { const a = AB[k][1] * env * hd(k); this.worldTurn(out, AB[k][0], k === AB.length - 1 ? a : a - prev, 0); prev = k === AB.length - 1 ? a : prev; }\n", "")
s = s.replace("const hd = k => Math.sin(th - k * 0.55); let prev = 0;", "const hd = k => Math.sin(th - k * 0.55);")
# ---- the limbs on their stroke marks
rep("""    if (sl > 0.001) { // (swimming: the limbs flat along its sides, the arms sweeping back from out ahead on each push, the legs trailing beside the tail with a little kick)
      const pk2 = L.pk2 && L.pk2f === this.t ? L.pk2 : (L.pk2f = this.t, L.pk2 = P.fk('crawl', out)), pr = pk2[l.root], q = l.q || (l.q = new THREE.Vector3()), R = SL.reach, K = SL.push;
      if (l.arm) q.set(pr.x + (0.045 + 0.08 * R) * l.m, l.home.y + 0.04 - 0.02 * R, pr.z - 0.24 + 0.16 * R);
      else q.set(pr.x + (0.035 + 0.02 * K) * l.m, l.home.y + 0.035, pr.z - 0.28 - 0.04 * K);
      q.lerpVectors(l.p, q, sl); tp = q; lift = Math.max(lift, 0.8 * sl); }
    out.contact(l.en, tp, LV2.set(LB.fwd.x * l.m * (1 - sl) + 0.08 * l.m * sl, -0.35 * lift * (1 - sl), LB.fwd.z * (1 - sl) - sl), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1);
    const dig = this.chain[l.arm ? 'fingers' : 'toes'][l.m > 0 ? 0 : 1], ns = 1 - sl; // (swimming: the fingers and toes closed together, nearly straight)""",
"""    let tk = 0;
    if (sl > 0.001) { // (swimming: each limb on its marks through the stroke; round a turn the inside hand reaches out and holds on, the outside one sweeps wide)
      const pk2 = L.pk2 && L.pk2f === this.t ? L.pk2 : (L.pk2f = this.t, L.pk2 = P.fk('crawl', out)), pr = pk2[l.root], q = l.q || (l.q = new THREE.Vector3()), mk = swMark(l.en, SL.u, l.arm, SL.m);
      const tn = Math.max(-1, Math.min(1, bend / 45)) * l.m, inn = Math.max(0, tn), outr = Math.max(0, -tn); // (inn: this is the inside of the turn)
      tk = mk[3] * (l.arm ? 1 - 0.75 * inn : 1);
      const ox = mk[0] + (l.arm ? 0.07 * inn * (1 - mk[3] * 0.5) + 0.06 * outr * (1 - mk[3]) : 0.03 * outr), oz = mk[2] + (l.arm ? 0.08 * inn : 0);
      q.set(pr.x + ox * l.m, l.home.y + mk[1] * (1 - (l.arm ? 0.75 * inn : 0)), pr.z + oz);
      q.lerpVectors(l.p, q, sl); tp = q; lift = lift * (1 - sl) + Math.max(tk, mk[4]) * sl; tk *= sl; }
    out.contact(l.en, tp, LV2.set(LB.fwd.x * l.m * (1 - tk) + 0.08 * l.m * tk, -0.35 * lift * (1 - tk), LB.fwd.z * (1 - tk) - tk), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1);
    const dig = this.chain[l.arm ? 'fingers' : 'toes'][l.m > 0 ? 0 : 1], ns = 1 - tk; const sl0 = sl; { const sl = tk; // (along its sides: the fingers and toes closed together, nearly straight)""")
rep("""      dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0)) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns + 2 * sl, 0, 0); });""".replace('      ', '    ', 1),
"""    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0)) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns + 2 * sl, 0, 0); }); }""")
# ---- the tail: the wave runs on down it, wider toward the tip, the strongest side to side of all
rep("""  this.tailWave(2 * Math.PI * L.ph + Math.PI * 0.85, ((4 + 15 * clamp01(v / 6.5)) * act + 1.5) * (1 - sl), 0.75, air ? -3 : 0);
  if (sl > 0.001) { const tt = this.tailTarget, c = L.ttc || (L.ttc = new Float32Array(tt.length)); c.set(tt); // (the slither's wave carries on down the tail, bigger toward its tip)
    this.tailWave(SL.tph, SLITHER.tail * sl, 0.55, 0); for (let k = 0; k < tt.length; k++) tt[k] += c[k]; } // (the tail sways slowly, once each way every two strokes, steadying it)""",
"""  this.tailWave(2 * Math.PI * L.ph + Math.PI * 0.85, ((4 + 15 * clamp01(v / 6.5)) * act + 1.5), 0.75, air ? -3 : 0);
  if (sl > 0.001) { const tt = this.tailTarget, th = 4 * Math.PI * SL.u, env = 0.6 + 0.4 * SL.g; let up = 8.5 * env * Math.sin(th - 5 * 0.55); // (from the hips' own heading on)
    for (let k = 0; k < 6; k++) { const a = (11 + 5 * k) * env * Math.sin(th - (6 + k) * 0.55); tt[k * 2] = tt[k * 2] * (1 - sl) + (a - up) * sl; tt[k * 2 + 1] *= 1 - sl; up = a; } }""")
# ---- the tail's C round a turn: more of it while swimming; the gills swing out round turns, more than before
rep("if (L && this.state === 'crawl') this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.16)",
    "if (L && this.state === 'crawl') this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.16 + 0.2 * (L.slK || 0))")
rep("add[j * 2 + 1] = swing * 14 * sgn", "add[j * 2 + 1] = swing * 24 * sgn")
assert 'SL.reach' not in s and 'SL.push' not in s and 'SL.tph' not in s
open(P, 'w').write(s); print('swim230 ok')
