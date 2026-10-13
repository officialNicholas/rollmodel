"""v252: the character, more alive.
 - the ears: they curve through a turn (the tips trail the roots on a slower spring of their own, and swing further), lift back and out
   like wings through a hop, flop about through a shake, and twitch now and then on their own
 - the face: a held face that beats the game's per-frame one (a shake's screwed-up face, an idle's mood), and new faces drawn into the
   face sheets (sleepy, wink, worried and determined eyes; a smile, a blep, a frown and a :3 mouth); a determined squint swimming flat
   out, a smirk when ahead
 - the locker's crawl-out: it climbs out of a hole in the paint (the hole is ground for its hands and feet, as the basin's tub is),
   instead of being raised up out of it; its eyes come up first and look about; out, it shakes itself off
 - the home screen's moods: dozing off and jolting awake, a sneeze, a wet-dog shake, a proud wink, a blep, a wave, peekaboo behind its
   ears; faces for the old ones (vibing to the beat, gleeful hops, a curious look); a sniff now and then
 - the swim: a clean stroke (reach, pull, tuck and glide, slide forward, reach) with no crawl steps in the middle of it; into it sooner
   once up to speed, the scurry before it calmer
"""
def apply(s):
    a0 = s.index('const AXO = '); a1 = s.index('const AXOC = '); c1 = s.index("return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, headR0: HEAD_R0, faceK: 1.18 };", a1)
    A, C, G0, G1 = s[a0:a1], s[a1:c1], s[:a0], s[c1:]
    def rep(t, old, new, count=1):
        c = t.count(old); assert c == count, f'expected {count}, found {c}: {old[:100]!r}'
        return t.replace(old, new)
    # ================= the ears =================
    # (the tips on their own slower spring, trailing the roots: a stalk curves through a swing; the tips take more of it)
    A = rep(A, "for (let j = 0; j < 6; j++) { const a = gs[j * 2] * stalkAmp[j], b = gs[j * 2 + 1] * stalkAmp[j]; rot(pose, g[j * 2], a * 0.55, 0, b * 0.55); rot(pose, g[j * 2 + 1], a * 0.7, 0, b * 0.7); }",
        "const gt = this.gsTip || gs; for (let j = 0; j < 6; j++) { const m = stalkAmp[j], a = gs[j * 2] * m, b = gs[j * 2 + 1] * m, a2 = gt[j * 2] * m, b2 = gt[j * 2 + 1] * m; rot(pose, g[j * 2], a * 0.5, 0, b * 0.42); rot(pose, g[j * 2 + 1], a2 * 0.8, 0, b2 * 0.98); } // (v252: the tips trail the roots on a slower spring of their own, so a stalk curves through a swing instead of turning stiff)")
    A = rep(A, """    if (L) { const swing = Math.max(-1, Math.min(1, -(L.yr * Math.max(1.5, L.v) * 0.12 + L.ht.v * 0.012))), fl = (this.breath - 0.5) * 2;
      const add = this.gillAdd || (this.gillAdd = new Float32Array(12));
      for (let j = 0; j < 6; j++) { add[j * 2] = -fl * 1.0 * (1 - L.act) + Math.min(1, L.v / 4) * 9; add[j * 2 + 1] = -swing * 24 + fl * 2 * (1 - L.act); } this.gillAddOn = true; }""",
"""    if (L) { const swing = Math.max(-1.25, Math.min(1.25, -(L.yr * Math.max(1.5, L.v) * 0.14 + L.ht.v * 0.014))), fl = (this.breath - 0.5) * 2, M = this.motion;
      // (v252) a hop: the ears lift back and out like wings from the push-off on, highest as it comes down; let go on landing, they slap down
      const air = !!(M && M.air) && !(this.ballOn > 0.2), lift = (this.earUpF || (this.earUpF = new Follow(13))).step(air ? (M.vy || 0) < 0 ? 1.2 : 0.8 : 0, dt);
      // (v252) shy: both ears swung forward and in over the eyes
      const cov = (this.earCovF || (this.earCovF = new Follow(9))).step(clamp01(this.earCover || 0), dt);
      const add = this.gillAdd || (this.gillAdd = new Float32Array(12));
      for (let j = 0; j < 6; j++) { const sd = j < 3 ? -1 : 1; add[j * 2] = -fl * 1.0 * (1 - L.act) + Math.min(1, L.v / 4) * 9 + 34 * lift - 62 * cov; add[j * 2 + 1] = -swing * 34 + fl * 2 * (1 - L.act) + sd * 24 * lift - sd * 30 * cov; } this.gillAddOn = true;
      // (v252) now and then, still or strolling, one ear twitches: a quick flick up and out, and back
      this.twT = (this.twT === undefined ? 2 + Math.random() * 4 : this.twT) - dt * (L.v < 2.5 ? 1 : 0.25);
      if (this.twT <= 0) { this.twT = 2.2 + Math.random() * 5; const o = Math.random() < 0.5 ? 0 : 3, k = 0.55 + 0.45 * Math.random(); for (let j = o; j < o + 3; j++) { this.gillPush[j * 2] += 70 * k; this.gillPush[j * 2 + 1] += (o ? 1 : -1) * 80 * k; } } }""")
    A = rep(A, """    ss0.call(this, dt);
    // the tail follows the body's bend round a turn""",
"""    ss0.call(this, dt);
    // (v252) the tips' own spring, slower than the roots': they trail a swing and run on past it
    if (dt > 0) { const T = this.gsTip || (this.gsTip = Float32Array.from(this.gs)), V = this.gsTipV || (this.gsTipV = new Float32Array(12)), h = Math.min(dt, 1 / 30); for (let i = 0; i < 12; i++) { V[i] += (46 * (this.gs[i] - T[i]) - 4.6 * V[i]) * h; T[i] += V[i] * h; } }
    // the tail follows the body's bend round a turn""")
    # (a hop's push-off flings the ears up; landing they slap down and forward, and bounce)
    A = rep(A, "L.arch.v += 60; }", "L.arch.v += 60; if (!(this.ballOn > 0.2)) this.kickGills(0, 0.55); }")
    A = rep(A, "this.kickGills(0, 0.6 * k); /* (the ears slap down on landing) */", "this.kickGills(0, -0.55 * k); /* (the ears slap down on landing) */")
    # the shake: the ears flop about with it, and the face screws up; then they drop, and it looks pleased with itself
    A = rep(A, "Animator.prototype.shake = function (k) { const L = this.loco || this.initLoco(); L.shk = { t: 0, k: k === undefined ? 1 : k }; };",
        "Animator.prototype.shake = function (k) { const L = this.loco || this.initLoco(); L.shk = { t: 0, k: k === undefined ? 1 : k }; if (this.look2 && this.look2.face) this.look2.face('shake', 0.92); };")
    A = rep(A, "  const L = this.loco, K = L && L.shk; if (!K) return; K.t += dt; const T = 0.9; if (K.t >= T) { L.shk = null; return; }",
        "  const L = this.loco, K = L && L.shk; if (!K) return; K.t += dt; const T = 0.9; if (K.t >= T) { L.shk = null; this.kickGills(0, -0.45); if (this.look2 && this.look2.face) this.look2.face('content', 0.75); return; }")
    A = rep(A, "  out.root.y -= 0.03 * env; // (it drops a touch into it)",
"""  out.root.y -= 0.03 * env; // (it drops a touch into it)
  // (v252) the ears flop about with it: whipped round after the head, the tips furthest and latest, flapping up and back twice as fast
  { const g = this.chain.gills; for (let j = 0; j < 6; j++) { const sd = j < 3 ? -1 : 1, m = j % 3 === 2 ? 0.55 : 1, s1 = Math.sin(w - 1.3), s2 = Math.sin(w - 2.1), f2 = Math.sin(2 * w - 0.9);
      rot(out, g[j * 2], (16 + 14 * f2) * env * m, 0, (30 * s1 + sd * 12 * Math.abs(s1)) * env * m); rot(out, g[j * 2 + 1], (12 + 22 * f2) * env * m, 0, (44 * s2) * env * m); } }""")
    # ================= the face =================
    A = rep(A, "const EXPR = { neutral: [0, 8], happy: [1, 9], angry: [2, 10], hurt: [3, 11], glee: [4, 12], scared: [5, 13], yawn: [6, 13], dizzy: [7, 11], peek: [5, 13], leap: [5, 9], brace: [7, 11] };",
        "const EXPR = { neutral: [0, 8], happy: [1, 9], angry: [2, 10], hurt: [3, 11], glee: [4, 12], scared: [5, 13], yawn: [6, 13], dizzy: [7, 11], peek: [5, 13], leap: [5, 9], brace: [7, 11],\n"
        "  shake: [7, 11], content: [4, 24], sleepy: [20, 8], doze: [6, 24], smirk: [21, 24], blep: [1, 25], sad: [22, 26], focus: [23, 8], cute: [1, 27], curious: [5, 27], sneeze: [7, 13], pout: [22, 27], startle: [5, 13] }; // (v252: new eyes in cells 20-23, new mouths in 24-27, those with fangs in 28-31)")
    A = rep(A, "const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 } };", "const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 }, curious: { pu: 1.14, py: 0.04 }, startle: { pu: 0.7, py: 0 }, smirk: { pu: 1, py: -0.06 } };")
    A = rep(A, "const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 };", "const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1, shake: 1, content: 1, doze: 1, smirk: 1, sneeze: 1 };")
    A = rep(A, "  scared: { h: 0.86, k: 0.08, c: 0.06, ch: -0.97, pu: 0.62, py: -0.02 },\n};",
"""  scared: { h: 0.86, k: 0.08, c: 0.06, ch: -0.97, pu: 0.62, py: -0.02 },
  // (v252) heavy lids; a wink (one eye a happy arc); worried, the outer corners drooping, big pupils; a determined squint
  sleepy: { h: -0.4, k: 0.06, c: 0.1, ch: -0.78, chc: 0.16, pu: 0.96, py: -0.16 },
  wink: { L: { h: 0.4, k: 0.04, c: 0.16, ch: -0.46, chc: 0.32, pu: 1.0, py: -0.04 }, R: { shut: 'arc' }, blush: 0.7 },
  sad: { h: 0.22, k: 0.44, c: 0.02, ch: -0.82, chc: 0.08, pu: 1.14, py: 0.02 },
  focus: { h: 0.0, k: -0.22, c: 0.05, ch: -0.56, chc: 0.24, pu: 0.92, py: -0.04 },
};
const FACE_X = [['sleepy', 20], ['wink', 21], ['sad', 22], ['focus', 23]], FACE_MX = [['smile', 24], ['blep', 25], ['frown', 26], ['cat', 27]];""")
    A = rep(A, "  const W = C * 4, H = C * 5, col = document.createElement('canvas')", "  const W = C * 4, H = C * 8, col = document.createElement('canvas')")
    A = rep(A, "  for (const sd of [-1, 1]) { shutEye(6, sd, 'closed'); shutEye(7, sd, 'squeeze'); }",
        "  for (const sd of [-1, 1]) { shutEye(6, sd, 'closed'); shutEye(7, sd, 'squeeze'); }\n"
        "  for (const [k, cell] of FACE_X) { const F = FACE_LIDS[k]; for (const sd of [-1, 1]) { const L = F.L ? (sd < 0 ? F.L : F.R) : F; if (L.shut || F.shut) shutEye(cell, sd, L.shut || F.shut); else openEye(cell, L, sd); } if (F.blush) blush(cell, F.blush); }")
    A = rep(A, "  for (const sd of [-1, 1]) { lashCell(6, sd, ctx => lashShut(ctx, 'closed')); lashCell(7, sd, ctx => lashShut(ctx, 'squeeze')); }",
        "  for (const sd of [-1, 1]) { lashCell(6, sd, ctx => lashShut(ctx, 'closed')); lashCell(7, sd, ctx => lashShut(ctx, 'squeeze')); }\n"
        "  for (const [k, cell] of FACE_X) { const F = FACE_LIDS[k]; for (const sd of [-1, 1]) { const L = F.L ? (sd < 0 ? F.L : F.R) : F; lashCell(cell, sd, ctx => L.shut || F.shut ? lashShut(ctx, L.shut || F.shut) : lashOpen(ctx, L)); } }")
    A = rep(A, "  FACE_KINDS.forEach((k, i) => { at(g, 8 + i, ctx => big(ctx, () => MOUTHS[k](ctx, false))); at(g, 14 + i, ctx => big(ctx, () => MOUTHS[k](ctx, true))); });\n  return { col, msk };",
"""  FACE_KINDS.forEach((k, i) => { at(g, 8 + i, ctx => big(ctx, () => MOUTHS[k](ctx, false))); at(g, 14 + i, ctx => big(ctx, () => MOUTHS[k](ctx, true))); });
  // (v252) a closed smile with dimples, the same with the tip of a tongue poking out, a frown, a :3
  const curveAt = (w, d, x) => { const u = x / w; return d * Math.cos(u * Math.PI / 2); };
  const MOUTHS2 = {
    smile: (ctx, f) => { line(ctx, Array.from({ length: 25 }, (_, i) => { const x = (i / 24 - 0.5) * 0.3; return [x, MY + 0.035 - curveAt(0.15, 0.065, x)]; }), 0.038);
      for (const sd of [-1, 1]) line(ctx, [[sd * 0.16, MY + 0.05], [sd * 0.145, MY + 0.03]], 0.026); if (f) { fang(ctx, -0.07, MY - 0.005, 0.8); fang(ctx, 0.07, MY - 0.005, 0.8); } },
    blep: (ctx, f) => { ctx.save(); const tx = 0.025, ty = MY - 0.07, tg = ctx.createRadialGradient(tx - 0.012, ty + 0.01, 0, tx, ty, 0.075); tg.addColorStop(0, '#FF9DB0'); tg.addColorStop(0.65, '#F0607E'); tg.addColorStop(1, '#C23A58');
      ctx.fillStyle = tg; ctx.beginPath(); ctx.moveTo(tx - 0.058, MY - 0.02); ctx.lineTo(tx - 0.058, ty); ctx.arc(tx, ty, 0.058, Math.PI, 0, false); ctx.lineTo(tx + 0.058, MY - 0.02); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(40,6,18,0.8)'; ctx.lineWidth = 0.022; ctx.stroke(); ctx.strokeStyle = 'rgba(150,30,60,0.55)'; ctx.lineWidth = 0.012; ctx.beginPath(); ctx.moveTo(tx, MY - 0.03); ctx.lineTo(tx, ty - 0.012); ctx.stroke(); ctx.restore();
      line(ctx, Array.from({ length: 25 }, (_, i) => { const x = (i / 24 - 0.5) * 0.26; return [x, MY + 0.03 - curveAt(0.13, 0.05, x)]; }), 0.036); if (f) { fang(ctx, -0.075, MY + 0.0, 0.75); fang(ctx, 0.085, MY + 0.0, 0.75); } },
    frown: (ctx, f) => { line(ctx, Array.from({ length: 25 }, (_, i) => { const x = (i / 24 - 0.5) * 0.22; return [x, MY - 0.035 + curveAt(0.11, 0.05, x)]; }), 0.036); if (f) { fang(ctx, -0.05, MY + 0.005, 0.7); fang(ctx, 0.05, MY + 0.005, 0.7); } },
    cat: (ctx, f) => { line(ctx, Array.from({ length: 33 }, (_, i) => { const x = (i / 32 - 0.5) * 0.24, u = Math.abs(x) / 0.12; return [x, MY + 0.025 - 0.05 * Math.sin(Math.PI * u)]; }), 0.034); if (f) { fang(ctx, -0.06, MY - 0.02, 0.7); fang(ctx, 0.06, MY - 0.02, 0.7); } },
  };
  FACE_MX.forEach(([k, cell]) => { at(g, cell, ctx => big(ctx, () => MOUTHS2[k](ctx, false))); at(g, cell + 4, ctx => big(ctx, () => MOUTHS2[k](ctx, true))); });
  return { col, msk };""")
    A = rep(A, "vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.2); }",
        "vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.125); }")
    A = rep(A, "    U.fCells.value.set(ea[0], ea[1] + fang, eb[0], eb[1] + fang);", "    const fm = c => fang ? c + (c >= 24 ? 4 : 6) : c; U.fCells.value.set(ea[0], fm(ea[1]), eb[0], fm(eb[1]));")
    A = rep(A, "  setExpression(name) { if (!(name in EXPR)) name = 'neutral'; if (name === this.exprB) return this; if (this.exprK < 1) this.expr = this.exprK > 0.5 ? this.exprB : this.expr; this.exprB = name; this.exprK = 0; return this; }",
"""  setExpression(name) { if (!(name in EXPR)) name = 'neutral'; this.want = name; return this.ovr ? this : this.setExpr0(name); }
  setExpr0(name) { if (name === this.exprB) return this; if (this.exprK < 1) this.expr = this.exprK > 0.5 ? this.exprB : this.expr; this.exprB = name; this.exprK = 0; return this; }
  // (v252) a face held for a while over whatever the game asks for each frame (a shake's screwed-up face, an idle's mood), then back to that
  face(name, dur = 0.8) { if (!(name in EXPR)) return this; this.ovr = { t: dur, name }; return this.setExpr0(name); }""")
    A = rep(A, "    if (this.emote) { this.emote.t -= dt;", "    if (this.ovr) { this.ovr.t -= dt; if (this.ovr.t <= 0) { this.ovr = null; this.setExpr0(this.want || 'neutral'); } }\n    if (this.emote) { this.emote.t -= dt;")
    A = rep(A, "return { FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, pupilOf,", "return { FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, FACE_X, FACE_MX, pupilOf,")
    # ================= the wrapper =================
    C = rep(C, "    I.setExpression = name => look.setExpression(name);", "    I.setExpression = name => look.setExpression(name);\n    I.face = (name, dur) => look.face(name, dur); // (v252: a face held over the game's own for a while)")
    # (the menu's hops: the crawl's own take-off and landing kicks do the ears now)
    C = rep(C, "if (up && !X.hopUp) { A.sqPush[0] -= 2; A.kickGills(0, -0.5); X.hopT = 0; }", "if (up && !X.hopUp) { A.sqPush[0] -= 2; X.hopT = 0; }")
    C = rep(C, "else if (X.hopUp && X.hopT > 0.1) { A.sqPush[0] += 4; A.kickGills(0, 0.9); for (let i = 0; i < 6; i++) A.tailPush[i * 2 + 1] -= 40; }", "else if (X.hopUp && X.hopT > 0.1) { A.sqPush[0] += 4; A.kickGills(0, -0.3); for (let i = 0; i < 6; i++) A.tailPush[i * 2 + 1] -= 40; }")
    C = rep(C, "    A.motion.turn = clamp(-(o.lean || 0) * 1.2, -1, 1);", "    A.motion.turn = clamp(-(o.lean || 0) * 1.2, -1, 1); A.earCover = o.earCover || 0; // (v252: shy, its ears over its eyes)")
    # ================= the locker's crawl-out =================
    i0 = G1.index("const CR = { pool: 0.42"); i1 = G1.index("  if (t >= CR.end) endIntro();\n}\n", i0) + len("  if (t >= CR.end) endIntro();\n}\n")
    G1 = G1[:i0] + r"""// (v252) the locker's crawl-out: it climbs out of a hole in the paint. The pool opens behind its spot; its eyes come up out of the paint
// first and look about; then it hauls itself up the bank and out over the lip on all fours, hands reaching up onto the floor, its body
// pitched up the slope, its hips and tail out last; out, it shakes itself off. The hole is ground for its hands and feet (the basin's
// crawl-out does the same with its tub): deep under the pool and on back under the floor, out of sight
const CR = { pool: 0.42, rise0: 0.5, rise1: 0.95, go: 0.8, land: 2.55, end: 3.45, back: 1.6, poolBack: 1.12, lip: 0.64, ramp: 0.34, deep: 0.4, sink: 0.55, side: 0.62 };
// how far along its way out it is (0 to 1) by the share of the climb's time gone: slow to start, slowest as its chest goes over the lip,
// easing to a stop on the floor
const crPath = (() => { const N = 96, xs = [], ts = [0], sm = smoothstep, v = x => (0.32 + 0.68 * sm(0, 0.22, x)) * (0.14 + 0.86 * (1 - sm(0.72, 1, x))) * (1 - 0.5 * Math.exp(-Math.pow((x - 0.62) / 0.16, 2)));
  for (let i = 0; i <= N; i++) xs.push(i / N); let tt = 0; for (let i = 1; i <= N; i++) { tt += (xs[i] - xs[i - 1]) / v((xs[i] + xs[i - 1]) / 2); ts.push(tt); } for (let i = 0; i <= N; i++) ts[i] /= tt;
  return u => { if (u <= 0) return 0; if (u >= 1) return 1; let lo = 0, hi = N; while (hi - lo > 1) { const k = (lo + hi) >> 1; if (ts[k] <= u) lo = k; else hi = k; } return xs[lo] + (xs[hi] - xs[lo]) * (u - ts[lo]) / (ts[hi] - ts[lo]); }; })();
function startIntro() { const I = VP && VP.slime; lookIntro = reduceMotion ? { t: IN_LAND, landed: true } : I && I.kind === 'axo' ? { t: 0, crawl: true, land: CR.land, vis: CR.rise0 - 0.08, sink: 0, back: CR.back, cl: null, pose: { pitch: 0, sq: 0, rise: 0 } } : { t: 0 }; }
// the crawl-out, frame by frame: the pool, how far it still has to go, the ground the hole makes under it, its face, the splashes
function crawlFrame(I) {
  const t = I.t, pool = dipPool, U = pool.userData.U, V = VP, S = V && V.slime;
  const R = 0.82, yw = V.yawDraw || 0, fx = Math.sin(yw), fz = Math.cos(yw);
  const open = t < CR.land ? easeBack(Math.min(1, t / CR.pool)) : 1 - dipEase((t - CR.land - 0.3) / (CR.end - CR.land - 0.3));
  const cx = P.x - fx * CR.poolBack, cz = P.z - fz * CR.poolBack; // (the pool sits behind its spot: it comes up out of it and onto the floor)
  pool.visible = pool.userData.mask.visible = open > 0.01; pool.position.set(cx, 0.006, cz); pool.scale.setScalar(Math.max(0.01, open) * R); pool.userData.mask.position.set(P.x, 0, P.z);
  U.uT.value = t; U.uCol.value.setHex(TEAMS[0].wet); U.uRip.value = Math.max(0, (I.rip || 0) - 0.016); I.rip = U.uRip.value; U.uHole.value = 0;
  // its eyes come up out of the paint (the bottom of the hole rising under it), then it sets off up the bank
  const ur = clamp((t - CR.rise0) / (CR.rise1 - CR.rise0), 0, 1), sk = CR.sink * Math.pow(1 - ur, 3), u = crPath((t - CR.go) / (CR.land - CR.go));
  I.back = CR.back * (1 - u); I.sink = 0; I.pose.pitch = 0;
  const cl = I.cl || (I.cl = { inv: new THREE.Matrix4(), floor: 0, tailK: 0.6, curl: 0, fn: null, D: 0 });
  cl.inv.makeRotationY(yw).setPosition(cx, P.y, cz).invert(); cl.floor = P.y; cl.D = (CR.deep + sk) * clamp(open * 1.4, 0, 1);
  cl.fn = cl.fn || ((x, z) => { if (z >= CR.lip) return 0; const a = Math.abs(x), k = smoothstep(CR.lip, CR.lip - CR.ramp, z) * (a < CR.side ? 1 : Math.max(0, 1 - (a - CR.side) / 0.12)); return -cl.D * k; });
  // its face: eyes shut down in the paint, opening as they come out for a look round, then set on the climb (the shake does its own)
  if (S && S.face) S.face(t < CR.rise1 - 0.12 ? 'doze' : t < CR.go + 0.4 ? 'curious' : t < CR.land ? 'focus' : null, 0.12);
  if (t >= CR.rise0 && !I.rose) { I.rose = true; AU.pop(); I.rip = 1; dipCrown(8, 0.25, 1.6, 0.9, 0.45, cx + fx * 0.15, cz + fz * 0.15); }
  if (t >= CR.go && !I.set) { I.set = true; AU.vox('hup', 0.7); I.rip = Math.max(I.rip, 0.7); }
  if (u > 0.55 && !I.mid) { I.mid = true; I.rip = 0.8; dipCrown(10, 0.3, 1.5, 1.2, 0.45, cx + fx * CR.lip, cz + fz * CR.lip); }
  if (t >= CR.land && !I.landed) { I.landed = true; I.rip = 0.6; buzz(10); }
  if (t >= CR.land + 0.18 && !I.shook) { I.shook = true; shake = Math.max(shake, 0.03); if (S && S.shake) S.shake(1); }
  { const k = Math.max(0, t - CR.land), osc = 0.32 * Math.exp(-k * 6) * Math.cos(k * 15); I.pose.sq = Math.max(0, osc); I.pose.rise = Math.max(0, -osc) * 0.6; }
  const kf = easeOut((t - CR.rise1) / 0.32), kw = clamp((t - CR.land + 0.1) / 0.34, 0, 1);
  introFade(kf, kw);
  const eo = Math.max(0.02, easeOut((t - CR.rise1) / 0.26));
  for (const it of eyes) { it.e.scale.y *= eo; it.pu.scale.multiplyScalar(eo); }
  for (const a of pArcs) if (a.visible) a.scale.y *= eo;
  if (t >= CR.end) endIntro();
}
""" + G1[i1:]
    G1 = rep(G1, "function dipCrown(n, r, up, out, life) { for (let i = 0; i < n; i++) {", "function dipCrown(n, r, up, out, life, x0, z0) { const X0 = x0 === undefined ? P.x : x0, Z0 = z0 === undefined ? P.z : z0; for (let i = 0; i < n; i++) {")
    G1 = rep(G1, "  spawnPart(P.x + c * r, 0.06, P.z + sn * r, c * sp, up * (0.75 + 0.5 * Math.random()), sn * sp, life, teamMats[0], 0.55 + 0.45 * Math.random()); } }",
                 "  spawnPart(X0 + c * r, 0.06, Z0 + sn * r, c * sp, up * (0.75 + 0.5 * Math.random()), sn * sp, life, teamMats[0], 0.55 + 0.45 * Math.random()); } }")
    G1 = rep(G1, "  o.climb = I.kind === 'axo' && D.introCrawl && D.introCrawl.path ? climbOf(D) : null;",
                 "  o.climb = I.kind === 'axo' && D.introCrawl && D.introCrawl.path ? climbOf(D) : I.kind === 'axo' && D === P && lookIntro && lookIntro.cl && state === 'menu' ? lookIntro.cl : null; // (v252: the locker's crawl-out climbs its own hole)")
    C = rep(C, "v.applyMatrix4(c.inv);", "v.applyMatrix4(c.inv); if (c.fn) return (c.floor + c.fn(v.x, v.z) - wy) / T.sy; // (v252: a climb with its own ground, the locker's hole)")
    G1 = rep(G1, "  { const bk = D === P && lookIntro && lookIntro.crawl ? lookIntro.back : 0, yw = V.yawDraw || 0; I.root.position.x = -Math.sin(yw) * bk; I.root.position.z = -Math.cos(yw) * bk; } // (the locker's crawl-out: still back in the pool by this much)",
        "  { const bk = D === P && lookIntro && lookIntro.crawl ? lookIntro.back : 0, ps = I.root.parent ? I.root.parent.scale.z || 1 : 1; I.root.position.x = 0; I.root.position.z = -bk / ps; } // (the locker's crawl-out: still back in the pool by this much, in metres; its parent is already turned its way and scaled)")
    # ================= the home screen's moods =================
    G1 = rep(G1, "const IDLE_ACTS = [['listen', 3.4, 3], ['bounce', 2.1, 2], ['still', 2.6, 3], ['hands', 2.6, 2], ['wag', 1.6, 2], ['peek', 2.6, 1], ['face', 2.0, 2], ['look', 1.7, 2], ['yawn', 1.9, 1], ['shimmy', 1.2, 2], ['wiggle', 1.3, 1]];",
        "// (v252) moods with a face and a body to go with them: dozing off and jolting awake, a sneeze, a wet-dog shake, a proud chin up and a wink, a\n"
        "// blep, a wave; and the old ones with faces (the slime's fallback keeps its own list)\n"
        "const IDLE_ACTS0 = [['listen', 3.4, 3], ['bounce', 2.1, 2], ['still', 2.6, 3], ['hands', 2.6, 2], ['wag', 1.6, 2], ['peek', 2.6, 1], ['face', 2.0, 2], ['look', 1.7, 2], ['yawn', 1.9, 1], ['shimmy', 1.2, 2], ['wiggle', 1.3, 1]];\n"
        "const IDLE_AXO = [['listen', 3.4, 3], ['bounce', 2.1, 2], ['still', 2.6, 2], ['wag', 1.6, 2], ['peek', 2.8, 1], ['look', 2.0, 2], ['yawn', 2.3, 1], ['shimmy', 1.2, 2], ['wiggle', 1.3, 1], ['doze', 4.6, 2], ['sneeze', 2.3, 1], ['shake', 1.4, 2], ['proud', 2.2, 2], ['blep', 2.3, 2], ['wave', 2.5, 2]];\n"
        "const ACT_FACE = { listen: 'content', bounce: 'glee', wag: 'happy', wiggle: 'cute', look: 'curious', tilt: 'curious', still: null };\n"
        "let IDLE_ACTS = IDLE_ACTS0;")
    G1 = rep(G1, "function pickIdle() {", "function pickIdle() { IDLE_ACTS = AXOC.S.ready ? IDLE_AXO : IDLE_ACTS0;")
    G1 = rep(G1, "  idle.sway = idle.push = idle.hop = idle.spin = idle.sq = idle.rise = idle.roll = idle.pitch = idle.bank = idle.hand = idle.earCover = 0;",
        "  idle.sway = idle.push = idle.hop = idle.spin = idle.sq = idle.rise = idle.roll = idle.pitch = idle.bank = idle.hand = idle.earCover = idle.wave = 0; idle.face = null;")
    G1 = rep(G1, "if (idle.act === 'yawn') emote(P, 'yawn', a[1]); if (idle.act === 'face') emote(P, ['glee', 'smug', 'ouch', 'bonk'][(Math.random() * 4) | 0], a[1] * 0.8);",
        "idle.f1 = idle.f2 = false; idle.side = Math.random() < 0.5 ? -1 : 1; if (idle.act === 'yawn') emote(P, 'yawn', a[1] * 0.8); if (idle.act === 'face') emote(P, ['glee', 'smug', 'ouch', 'bonk'][(Math.random() * 4) | 0], a[1] * 0.8);")
    G1 = rep(G1, "      else if (idle.act === 'peek') { const k = smoothstep(0.08, 0.3, u) * (1 - smoothstep(0.7, 0.92, u)); idle.earCover = k; idle.pitch = 0.07 * k; idle.sq = 0.06 * k; }",
        "      else if (idle.act === 'peek') { const k = smoothstep(0.08, 0.3, u) * (1 - smoothstep(0.7, 0.92, u)); idle.earCover = k; idle.pitch = 0.07 * k; idle.sq = 0.06 * k; idle.face = k > 0.45 ? 'doze' : u > 0.7 ? 'glee' : null; // (v252: peekaboo, eyes shut behind its ears, then a grin)\n"
        "        if (u > 0.74 && !idle.f1) { idle.f1 = true; if (AXOC.S.ready) AU.vox('giggle', 0.55); } }")
    G1 = rep(G1, "      else if (idle.act === 'look') { lxT = u < 0.42 ? -0.085 : u < 0.88 ? 0.085 : 0; lyT = 0.025; }",
        "      else if (idle.act === 'look') { lxT = u < 0.42 ? -0.085 : u < 0.88 ? 0.085 : 0; lyT = 0.025; idle.roll = (u < 0.42 ? 0.1 : u < 0.88 ? -0.1 : 0) * env; // (v252: a tilt of the head with each look, an ear twitching at the first)\n"
        "        if (u > 0.1 && !idle.f1) { idle.f1 = true; const A = VP.slime && VP.slime.ax && VP.slime.ax.A; if (A) A.twT = 0; } }")
    G1 = rep(G1, "      else if (idle.act === 'yawn') { idle.rise = 0.32 * Math.sin(u * Math.PI); lyT = 0.045; }",
        r"""      else if (idle.act === 'yawn') { idle.rise = 0.32 * Math.sin(u * Math.PI); lyT = 0.045; idle.pitch = 0.17 * Math.sin(Math.min(1, u * 1.15) * Math.PI); if (u > 0.86) idle.face = 'content'; } // (v252: its head tipping back with it, a contented smile after)
      // (v252) dozing off: the eyes go heavy and shut, the head sinks, catches itself once, sinks again; then it jolts awake (ears up, a hop, a
      // squeak), looks about, and smiles it off
      else if (idle.act === 'doze') { const fall = u < 0.68 ? smoothstep(0.04, 0.42, u) - 0.5 * Math.sin(clamp((u - 0.44) / 0.1, 0, 1) * Math.PI) * smoothstep(0.4, 0.44, u) : 0, up = u >= 0.68 ? Math.sin(clamp((u - 0.68) / 0.08, 0, 1) * Math.PI / 2) * (1 - smoothstep(0.84, 1, u)) : 0;
        idle.pitch = -0.34 * fall + 0.1 * up; idle.sq = 0.1 * fall; idle.earCover = 0.3 * fall; idle.roll = 0.06 * fall * idle.side; lyT = -0.05 * fall; idle.face = u < 0.2 ? 'sleepy' : u < 0.68 ? 'doze' : u < 0.84 ? 'startle' : 'cute';
        if (u >= 0.68) { idle.hop = 0.2 * Math.sin(clamp((u - 0.68) / 0.07, 0, 1) * Math.PI); lxT = u < 0.75 ? -0.08 : u < 0.83 ? 0.08 : 0; }
        if (u >= 0.68 && !idle.f1) { idle.f1 = true; AU.vox('eep', 0.6); const A = VP.slime && VP.slime.ax && VP.slime.ax.A; if (A) A.kickGills(0, 1.0); } }
      // (v252) a sneeze: ah.. ah.. the head lifting in two hitches, eyes screwing up; CHOO, the head snapping down, ears flung forward, a puff of
      // paint; a dazed moment, then a sheepish smile
      else if (idle.act === 'sneeze') { const pre = (0.55 * smoothstep(0.08, 0.2, u) + 0.45 * smoothstep(0.27, 0.4, u)) * (u < 0.45 ? 1 : 0), hit = u >= 0.45 ? Math.exp(-(u - 0.45) * 12) : 0;
        idle.pitch = 0.2 * pre - 0.32 * hit; idle.rise = 0.16 * pre; idle.sq = 0.42 * hit; lyT = 0.06 * pre; idle.face = u < 0.08 ? null : u < 0.45 ? 'sneeze' : u < 0.62 ? 'dizzy' : 'cute';
        if (u >= 0.45 && !idle.f1) { idle.f1 = true; AU.pop(); const A = VP.slime && VP.slime.ax && VP.slime.ax.A; if (A) { A.kickGills(0, -1.3); A.sqPush[0] += 3; }
          const S = VP.slime, yw = VP.yawDraw || 0, fx = Math.sin(yw), fz = Math.cos(yw), h = new THREE.Vector3(); if (S && S.ax) S.ax.P.jointWorld('crawl', 'head', h); else h.set(P.x, 0.4, P.z);
          const sc = S && S.root.parent ? new THREE.Vector3().setFromMatrixScale(S.root.parent.matrixWorld).x / PR : 1; AU.splat(0.3);
          for (let i = 0; i < 9; i++) spawnPart(h.x + fx * 0.3 * sc, h.y - 0.06 * sc, h.z + fz * 0.3 * sc, (fx * (1.6 + Math.random()) + (Math.random() - 0.5)) * sc, (0.5 + Math.random() * 0.8) * sc, (fz * (1.6 + Math.random()) + (Math.random() - 0.5)) * sc, 0.32, teamMats[0], (0.12 + Math.random() * 0.1) * sc); } } // (a puff of paint from its nose)
      // (v252) a wet-dog shake, for no reason at all (its ears flop, its face screws up; the animator does those)
      else if (idle.act === 'shake') { if (!idle.f1) { idle.f1 = true; if (VP.slime && VP.slime.shake) VP.slime.shake(0.9); AU.vox('brr', 0.55); } }
      // (v252) pleased with itself: chin up, a wink and a smile, a little sway
      else if (idle.act === 'proud') { const k = smoothstep(0.05, 0.25, u) * (1 - smoothstep(0.8, 1, u)); idle.pitch = 0.2 * k; idle.rise = 0.1 * k; idle.roll = 0.05 * Math.sin(u * Math.PI * 4) * k; idle.face = k > 0.3 ? 'smirk' : null; lyT = 0.04 * k; }
      // (v252) a blep: the head tipped to one side, the tip of its tongue out, an ear twitching
      else if (idle.act === 'blep') { const k = smoothstep(0.06, 0.22, u) * (1 - smoothstep(0.78, 0.95, u)); idle.roll = 0.2 * idle.side * k; idle.pitch = 0.05 * k; idle.face = k > 0.25 ? 'blep' : null;
        if (u > 0.12 && !idle.f1) { idle.f1 = true; const A = VP.slime && VP.slime.ax && VP.slime.ax.A; if (A) A.twT = 0; } }
      // (v252) a wave: one hand up off the floor, waving at you, a happy face
      else if (idle.act === 'wave') { const k = smoothstep(0.04, 0.2, u) * (1 - smoothstep(0.78, 0.96, u)); idle.wave = k; idle.face = k > 0.2 ? 'happy' : null; idle.roll = -0.06 * k; lyT = 0.03 * k; }""")
    G1 = rep(G1, "      if (u >= 1) { idle.act = null; idle.t = 1.4 + Math.random() * 2.6; } }",
        "      if (!idle.face && ACT_FACE[idle.act] && env > 0.3) idle.face = ACT_FACE[idle.act]; // (v252: a face to go with it)\n"
        "      if (u >= 1) { idle.act = null; idle.t = 1.4 + Math.random() * 2.6; } }")
    G1 = rep(G1, "  idleLook.x += (lxT - idleLook.x) * Math.min(1, rdt * 10); idleLook.y += (lyT - idleLook.y) * Math.min(1, rdt * 10);",
        "  idleLook.x += (lxT - idleLook.x) * Math.min(1, rdt * 10); idleLook.y += (lyT - idleLook.y) * Math.min(1, rdt * 10);\n"
        "  if (idle.face && VP.slime && VP.slime.face) VP.slime.face(idle.face, 0.15); // (v252: the mood's face, held over the usual one while it lasts)")
    G1 = rep(G1, "o.wave = IPo ? IPo.wave : 0;", "o.wave = IPo ? IPo.wave : showK ? idle.wave || 0 : 0;")
    C = rep(C, "A.earCover = o.earCover || 0; // (v252: shy, its ears over its eyes)", "A.earCover = o.earCover || 0; A.motion.wave = o.wave || 0; // (v252: shy, its ears over its eyes; a wave of one hand)")
    # ================= moods in play =================
    G1 = rep(G1, "  if (F === MOOD.smug) return 'happy';", "  if (F === MOOD.smug) return 'smirk'; // (v252: a wink and a smile)")
    G1 = rep(G1, "  if (smug) return 'happy';", "  if (smug) return 'smirk';\n  { const V = vOf(D), A = V && V.slime && V.slime.ax && V.slime.ax.A; if (D.st === 'play' && state === 'play' && A && A.loco && (A.loco.slK || 0) > 0.6) return 'focus'; } // (v252: swimming flat out, a determined squint)")
    # ================= the animator: the wave, the sniff =================
    A = rep(A, "  // ---- the limbs on their marks (in the air the same marks steer them, with no ground under them)\n  for (const l of L.limbs) {",
        "  // ---- the limbs on their marks (in the air the same marks steer them, with no ground under them)\n"
        "  // (v252) a wave: the right hand up off the floor beside the head, waving; the body leaning back off it onto the other three\n"
        "  const wv = L.wv = spr(L.wvS || (L.wvS = { x: 0, v: 0 }), air || sl > 0.1 ? 0 : clamp01(M.wave || 0), 120, 20, dt);\n"
        "  if (wv > 0.002) { out.root.x += 0.025 * wv; out.root.z -= 0.02 * wv; out.root.y += 0.012 * wv; this.pitchTurn(out, sp[3], -0.1 * wv); this.worldTurn(out, sp[2], 0, 4 * wv); }\n"
        "  for (const l of L.limbs) {")
    A = rep(A, "    { const r = Math.hypot(LB.fwd.x, LB.fwd.z), a0 = Math.atan2(LB.fwd.x, LB.fwd.z), a = a0 + (Math.PI - 0.08 - a0) * tk; out.contact(l.en, tp, LV2.set(l.m * Math.sin(a) * r, -0.35 * lift * (1 - tk), Math.cos(a) * r), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1); }",
        "    const wvk = l.en === 'hand.R' ? wv : 0; if (wvk > 0.002) { const pk = P.fk('crawl', out), sh = pk[l.root], q = l.wq || (l.wq = new THREE.Vector3()), sw = Math.sin(this.t * 2 * Math.PI * 2.4);\n"
        "      q.set(sh.x + l.m * (0.1 + 0.07 * sw), sh.y + 0.17 + 0.02 * Math.abs(sw), sh.z + 0.2); q.lerpVectors(tp, q, wvk); tp = q; lift = Math.max(lift, wvk); }\n"
        "    { const r = Math.hypot(LB.fwd.x, LB.fwd.z), a0 = Math.atan2(LB.fwd.x, LB.fwd.z), a = a0 + (Math.PI - 0.08 - a0) * tk; out.contact(l.en, tp, LV2.set(l.m * Math.sin(a) * r * (1 - wvk) + l.m * 0.2 * wvk, -0.35 * lift * (1 - tk) * (1 - wvk) + 0.85 * wvk, Math.cos(a) * r * (1 - wvk) + 0.5 * wvk), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1); }")
    A = rep(A, "    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0)) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns + 2 * sl, 0, 0); }); }",
        "    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns * (1 - wvk) + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0) + 12 * wvk) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns * (1 - wvk) + 2 * sl, 0, 0); }); } // (v252: waving, the fingers spread and straight)")
    # (a sniff now and then, standing still: three quick small nods of the nose)
    A = rep(A, "// the shake, laid over the crawl's finished pose",
        "// (v252) standing still now and then it sniffs: three quick little nods of the nose\n"
        "{ const an0 = Animator.prototype.applyNeck;\n"
        "  Animator.prototype.applyNeck = function (pose) { an0.call(this, pose); const N = this.neck, dt = this.dt || 0;\n"
        "    N.snT = (N.snT === undefined ? 4 + Math.random() * 6 : N.snT) - (this.speedS < 0.2 && this.state === 'crawl' ? dt : 0); if (N.snT <= 0) { N.snT = 6 + Math.random() * 9; N.snU = 0; }\n"
        "    if (N.snU !== undefined && N.snU < 1) { N.snU += dt / 0.55; const u = Math.min(1, N.snU), a = 3.2 * Math.sin(u * Math.PI) * Math.sin(u * 3 * 2 * Math.PI); rot(pose, this.I.head, a, 0, 0); } };\n"
        "}\n"
        "// the shake, laid over the crawl's finished pose")
    # ================= the swim =================
    # (a clean stroke: all four reach forward together, pull back and tuck along the sides, glide, then slide forward again close under the
    # body and reach; no crawl steps in the middle of a stroke any more. The crawl at the top of its speed calmer, and over sooner)
    A = rep(A, "const SWK = { arm: { F: [0.26, 0, 0.18, 0], G: [0.27, 0, 0.09, 0], M: [0.28, 0, 0.0, 0], B: [0.2, 0.012, -0.16, 0], T: [0.05, 0.045, -0.25, 1] }, // [out, up, along, tucked]",
        "const SWK = { arm: { R: [0.25, 0, 0.17, 0], P: [0.31, 0, -0.01, 0], B: [0.18, 0.012, -0.17, 0], T: [0.05, 0.045, -0.25, 1], C: [0.09, 0.03, 0.03, 0.45] }, // [out, up, along, tucked] (v252: reach, pull, back, tucked, coming forward)")
    A = rep(A, "  leg: { F: [0.17, 0, 0.06, 0], M: [0.18, 0, -0.06, 0], B: [0.1, 0.02, -0.24, 0], T: [0.035, 0.035, -0.28, 1] } };",
        "  leg: { R: [0.17, 0, 0.05, 0], P: [0.2, 0, -0.1, 0], B: [0.1, 0.02, -0.24, 0], T: [0.035, 0.035, -0.28, 1], C: [0.08, 0.03, -0.07, 0.45] } };")
    A = rep(A, "const SWT = { 'hand.R': [[0, 'M', 0, 1], [0.15, 'B', 0, 1], [0.25, 'T'], [0.55, 'T'], [0.68, 'F', 1], [1, 'M', 0, 1]], 'hand.L': [[0, 'G', 0, 1], [0.17, 'B', 0, 1], [0.27, 'T'], [0.7, 'T'], [0.83, 'F', 1], [1, 'G', 0, 1]],",
        "const SWT = { 'hand.R': [[0, 'R', 0, 1], [0.12, 'P', 0, 1], [0.22, 'B', 0, 1], [0.3, 'T'], [0.64, 'T'], [0.84, 'C', 1, 1], [1, 'R', 0, 1]], 'hand.L': [[0, 'R', 0, 1], [0.13, 'P', 0, 1], [0.23, 'B', 0, 1], [0.31, 'T'], [0.65, 'T'], [0.85, 'C', 1, 1], [1, 'R', 0, 1]],")
    A = rep(A, "  'foot.L': [[0, 'M', 0, 1], [0.14, 'B', 0, 1], [0.25, 'T'], [0.56, 'T'], [0.69, 'F', 1], [1, 'M', 0, 1]], 'foot.R': [[0, 'M', 0, 1], [0.14, 'B', 0, 1], [0.25, 'T'], [0.71, 'T'], [0.84, 'F', 1], [1, 'M', 0, 1]] };",
        "  'foot.L': [[0, 'R', 0, 1], [0.1, 'P', 0, 1], [0.2, 'B', 0, 1], [0.29, 'T'], [0.68, 'T'], [0.87, 'C', 1, 1], [1, 'R', 0, 1]], 'foot.R': [[0, 'R', 0, 1], [0.11, 'P', 0, 1], [0.21, 'B', 0, 1], [0.3, 'T'], [0.69, 'T'], [0.88, 'C', 1, 1], [1, 'R', 0, 1]] };")
    A = rep(A, "const SLITHER = { on: 3.8, off: 2.8, after: 0.35, T0: 1.75, T1: 1.4 };", "const SLITHER = { on: 3.5, off: 2.6, after: 0.14, T0: 1.6, T1: 1.3 }; // (v252: into the swim sooner once up to speed, the scurry before it short)")
    A = rep(A, "  const amp = (12 + 28 * clamp01(v / 6.5)) * act * (1 - sl)", "  const amp = (12 + 18 * clamp01(v / 6.5)) * act * (1 - sl)")
    A = rep(A, "    SL.k += ((SL.on ? 1 : 0) - SL.k) * Math.min(1, dt * (SL.on ? 3.6 : 4.2)); }", "    SL.k += ((SL.on ? 1 : 0) - SL.k) * Math.min(1, dt * (SL.on ? 4.6 : 4.2)); }")
    # (the tail through the swim: a smooth S that grows gently to the tip, instead of whipping into a hook; and the body's own side-slide
    # through the stroke no longer lashes it on top of that, the wave already carries it)
    A = rep(A, "const a = (18 + 7 * k) * env * Math.sin(th - (6 + k) * 0.55);", "const a = (15 + 4.5 * k) * env * Math.sin(th - (6 + k) * 0.55);")
    A = rep(A, "    if (L && this.state === 'crawl') this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.22 + 0.2 * (L.slK || 0)) + (this.motion.spin !== undefined ? L.tlg * 0.27 : 0);",
        "    if (L && this.state === 'crawl') this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.22 + 0.2 * (L.slK || 0)) + (this.motion.spin !== undefined ? L.tlg * 0.27 : 0) + this.rootVel.x * 40 * 0.8 * (L.slK || 0);")
    return G0 + A + C + G1
