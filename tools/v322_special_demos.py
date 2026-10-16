"""v322: the 3D demos for the Specials.

The Transforms tab's demo (v313: your own axolotl against a rival on a paper pad, looping, drawn with the game's own character code)
now plays for each Special stroke too:
- Rocket: up off the pad and out of sight on its paint jet, its target mark sliding over the rival (who backs away, and the mark
  follows), then the dive and the splash that knocks them out. The rocket pack, the mark and its beam are the match's own.
- Giant: grows (twice the size here, three times in a match: the window can't hold that) and the camera eases back to take it in;
  a wide stripe down the pad toward you, the rival cowering across it, then a giant's pound whose splash reaches them. It flickers as
  it runs out, as in a match, and shrinks back. A match's giant is untouched (gkMax is only set on the demo's two).
- Flash Freeze: a wind-up of frost rings, the flash (white-blue over the window), the rival frozen mid-stride in the match's ice shell,
  a full ring of paint round them, a grin at you while they tap at the ice, then the thaw.
The specials' places are set in the window's own terms (across it, and toward you, as the camera first sits), so everyone stays in
view. The pad shakes with the big landings. Test (the button by the demo) shows each special's own three lines as it plays them, as it
does for the transforms. In landscape the Specials tab now has the transforms' layout, with the demo beside the cards. Skills keep
their picture."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

BUILD = r"""  // (v322) the specials' own pieces: the rocket's mark on the pad (the match's own ring, fill and beam) and the frozen rival's ice
  SGD.mk = new THREE.Mesh(rocketMark.m.geometry, rocketMark.m.material.clone()); SGD.mkF = new THREE.Mesh(rocketMark.fill.geometry, rocketMark.fill.material.clone()); SGD.mkB = new THREE.Mesh(rocketMark.beam.geometry, rocketMark.beam.material.clone());
  SGD.mk.rotation.x = SGD.mkF.rotation.x = -Math.PI / 2; SGD.mk.renderOrder = 7; SGD.mkF.renderOrder = 6; SGD.mkB.renderOrder = 8; for (const m of [SGD.mk, SGD.mkF, SGD.mkB]) { m.visible = false; root.add(m); }
  SGD.ice = new THREE.Mesh(ICE_G, iceShellM); SGD.ice.renderOrder = 9; SGD.ice.visible = false; root.add(SGD.ice); SGD.iceK = 0; SGD.sp = {}; SGD.shk = 0;
"""

FNS = r"""// ---- (v322) the specials
const sgShk = k => { SGD.shk = Math.max(SGD.shk || 0, k); };
// (the specials' places are in the window's own terms, as the camera first sits: u across it, w toward you; s flips u)
const sgCS = (u, w) => [Math.cos(SG_YAW0) * u + Math.sin(SG_YAW0) * w, Math.cos(SG_YAW0) * w - Math.sin(SG_YAW0) * u];
const sgAtC = (A, u, w) => { const p = sgCS(u, w); sgAt(A, p[0], p[1]); };
function sgFlash(kind) { const f = $('sgFlash'); if (!f) return; f.className = 'sgflash ' + kind; void f.offsetWidth; f.classList.add('on'); }
// the rocket's paint jet, from the pack on its back: down on the way up, up on the way down
function sgJet(A, dir, k, dt) { const D = A.D, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), sc = PR * 1.25, bx = sgLX(A) - fx * sc, bz = sgLZ(A) - fz * sc, by = D.y + PR * (dir > 0 ? 1.9 : 0.35);
  SGD.jet = (SGD.jet || 0) + dt * 70 * k; while (SGD.jet >= 1) { SGD.jet -= 1; const a = Math.random() * 6.2832, sp = Math.random() * 1.2; sgPart(bx + Math.cos(a) * 0.06, by, bz + Math.sin(a) * 0.06, Math.cos(a) * sp, dir * (4 + Math.random() * 4) + D.vy * 0.3, Math.sin(a) * sp, 0.2 + Math.random() * 0.15, A.col, 0.35 + Math.random() * 0.35); } }
// Rocket: up off the pad and out of sight, its mark sliding over the rival (who backs off, and the mark follows), the dive, the splash
const SG_RK_TOP = 3.4;
function sgRocket(dt, t, s) {
  const A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, R = SGD.sp;
  if (t < 0.55) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; }
  else if (sgOnce('up')) { const x = sgLX(A), z = sgLZ(A); DA.rocket = { ph: 'up', t: 0, slow: false }; DA.air = true; DA.squash = 0.9; DA.wob = 1; emote(DA, 'glee', 1); sgSplat(x, z, 0.3, cA); sgRing(x, z, 1.2, 0xFFFFFF); sgBurst(x, z, A.col, 14, 2.2, 2.6); sgShk(0.35); }
  const K = DA.rocket;
  if (K) { K.t += dt;
    if (K.ph === 'up') { const u = Math.min(1, K.t / 0.6), y0 = DA.y; DA.y = SG_RK_TOP * (1 - Math.pow(1 - u, 3)); DA.vy = (DA.y - y0) / Math.max(dt, 1e-3); sgJet(A, -1, 1, dt); if (u >= 1) { K.ph = 'hover'; K.t = 0; DA.vy = 0; } }
    else if (K.ph === 'hover') { const k = Math.min(1, dt * 2.6); DA.x += (SG_X + sgLX(B) - DA.x) * k; DA.z += (SG_Z + sgLZ(B) - DA.z) * k; DA.y = SG_RK_TOP + Math.sin(K.t * 2.6) * 0.08; DA.vy = 0; DA.spd = 0; sgJet(A, -1, 0.3, dt);
      if (K.t >= 1.35) { K.ph = 'dive'; K.t = 0; DA.vy = -14; DA.squash = 0.6; DA.wob = 1; } }
    else { DA.vy = Math.max(-26, DA.vy - 90 * dt); DA.y += DA.vy * dt; sgJet(A, 1, 1.1, dt);
      if (DA.y <= 0) { const x = sgLX(A), z = sgLZ(A); DA.y = 0; DA.rocket = null; DA.air = false; DA.vy = 0; DA.squash = 1; DA.wob = 1; emote(DA, 'glee', 1.4);
        sgSplat(x, z, 0.95, cA); sgRing(x, z, 2.3, 0xFFFFFF); sgRing(x, z, 1.5, TEAMS[0].wet); sgRing(x, z, 0.9, 0xFFFFFF); sgBurst(x, z, A.col, 24, 4.6, 3.6); sgBurst(x, z, COL_WHITE, 8, 3, 2.4); sgShk(1); sgFlash('w');
        if (B.show && Math.hypot(sgLX(B) - x, sgLZ(B) - z) < 1.0) sgKO(B, cA); } } }
  // the mark: where it'll come down, turning, growing as it does, and a faint beam up to the rocket
  const M = SGD.mk;
  if (K) { const k = K.ph === 'dive' ? clamp(1 - DA.y / SG_RK_TOP, 0, 1) : 0, inK = K.ph === 'up' ? clamp((K.t - 0.25) / 0.35, 0, 1) : 1, rr = 0.95 * (0.62 + 0.38 * k) * (0.6 + 0.4 * easeBack(inK)), pulse = 0.5 + 0.5 * Math.sin(t * (8 + 14 * k)), x = sgLX(A), z = sgLZ(A);
    M.visible = SGD.mkF.visible = inK > 0; M.position.set(x, 0.05, z); SGD.mkF.position.set(x, 0.045, z); M.scale.setScalar(Math.max(0.01, rr)); M.rotation.z += dt * (0.8 + 3.2 * k); SGD.mkF.scale.setScalar(Math.max(0.01, rr * (0.15 + 0.85 * k)));
    M.material.color.set(TEAMS[0].wet).lerp(COL_WHITE, 0.1 + 0.25 * pulse); M.material.opacity = inK * (0.8 + 0.2 * pulse); SGD.mkF.material.color.set(TEAMS[0].wet); SGD.mkF.material.opacity = inK * (0.14 + 0.26 * k);
    const bh = DA.y, b = SGD.mkB; b.visible = inK > 0 && bh > 0.6; if (b.visible) { b.position.set(x, 0, z); b.scale.set(1 + 2 * k, bh, 1 + 2 * k); b.material.color.set(TEAMS[0].wet); b.material.opacity = inK * (0.22 + 0.2 * pulse); } }
  else M.visible = SGD.mkF.visible = SGD.mkB.visible = false;
  // the rival: a look up at it, and a few steps back that the mark follows
  if (B.show && K && (K.ph !== 'up' || K.t > 0.3)) { DB.ip.expr = 'scared'; if (K.ph === 'hover' && K.t > 0.25) { if (R.bx === undefined) { const d = sgCS(0.45 * s, -0.3); R.bx = sgLX(B) + d[0]; R.bz = sgLZ(B) + d[1]; } sgGo(B, R.bx, R.bz, 0.85, dt); } }
  if (t >= 3.3 && !DA.rocket) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'glee'; }
  if (t >= 4.5 && sgOnce('back')) { const p = sgCS(-0.75 * s, -0.1); sgBack(B, p[0], p[1], sgYawTo(B, A)); }
}
// Giant: twice the size here (three times in a match: the window can't hold that), a wide stripe down the pad, then a giant's pound
// whose splash reaches the rival cowering across it. It flickers as it runs out, as in a match, and shrinks back.
const SG_GK = 2.1;
function sgGiant(dt, t, s) {
  const A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, G = SGD.sp;
  if (t < 0.5) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; }
  else if (sgOnce('grow')) { const x = sgLX(A), z = sgLZ(A); DA.giantT = 3.0; DA.wob = 1; DA.squash = 0.8; emote(DA, 'glee', 1.1); sgRing(x, z, 1.7, TEAMS[0].wet); sgRing(x, z, 1.1, 0xFFFFFF); sgBurst(x, z, A.col, 16, 3.2, 2.6); sgShk(0.4); }
  if (DA.giantT > 0 && t > 0.5) { DA.giantT = Math.max(0, DA.giantT - dt); if (DA.giantT <= 0) { const x = sgLX(A), z = sgLZ(A); DA.wob = 1; DA.squash = 0.6; sgRing(x, z, 1.0, 0xFFFFFF); sgBurst(x, z, A.col, 10, 2.4, 2); } }
  if (t >= 0.5 && t < 1.0) { sgWatch(A, B); DA.ip.expr = 'menace'; }
  if (t >= 1.0 && t < 1.95) { const p = sgCS(0, 0.45), lx = sgLX(A), lz = sgLZ(A); sgGo(A, p[0], p[1], 1.4, dt); sgStripe(lx, lz, sgLX(A), sgLZ(A), 1.1, cA); sgWatch(A, null); DA.ip.expr = 'menace'; }
  if (t >= 2.0 && sgOnce('hop')) { G.hop = 0; DA.air = true; DA.vy = 5; DA.squash = 0.5; DA.spd = 0; }
  if (G.hop >= 0) { G.hop += dt; const u = G.hop;
    if (u < 0.32) { DA.y = 0.75 * Math.sin(Math.PI / 2 * u / 0.32); DA.vy = 2; DA.ip.expr = 'focus'; }
    else { DA.slam = true; const v = (u - 0.32) / 0.14; DA.y = Math.max(0, 0.75 * (1 - v * v)); DA.vy = -14;
      if (DA.y <= 0) { const x = sgLX(A), z = sgLZ(A); G.hop = -1; DA.slam = false; DA.air = false; DA.vy = 0; DA.y = 0; DA.squash = 1; DA.wob = 1; emote(DA, 'glee', 1.3);
        sgSplat(x, z, 0.9, cA); sgRing(x, z, 2.6, 0xFFFFFF); sgRing(x, z, 1.8, TEAMS[0].wet); sgRing(x, z, 1.1, 0xFFFFFF); sgBurst(x, z, A.col, 26, 4.8, 3.8); sgShk(1);
        if (B.show && Math.hypot(sgLX(B) - x, sgLZ(B) - z) < 1.85) sgKO(B, cA); } } }
  // the rival: cowering, eyes on the giant, from the moment it grows
  if (B.show && DB.st === 'play') { sgFace(B, sgYawTo(B, A), dt, 5); if (DA.giantT > 0) { DB.ip.expr = 'scared'; sgWatch(B, A); } }
  if (t >= 2.65 && !(G.hop >= 0)) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'glee'; }
  if (t >= 4.3 && sgOnce('back')) { const p = sgCS(1.15 * s, -0.75); sgBack(B, p[0], p[1], sgYawTo(B, A)); }
}
// Flash Freeze: a wind-up of frost, the flash, the rival frozen mid-stride, a ring of paint all round them, a grin at you while they
// tap at the ice, then the thaw
function sgFreeze(dt, t, s) {
  const A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, F = SGD.sp;
  if (t < 1.3 && B.show) { const p = sgCS(-0.1 * s, -0.2); sgGo(B, p[0], p[1], 0.8, dt); DB.ip.expr = 'content'; }
  if (t < 0.4) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; }
  else if (t < 1.3) { if (sgOnce('wind')) { DA.squash = 0.7; DA.wob = 1; emote(DA, 'glee', 0.8); F.fx = 0; }
    sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, B); DA.ip.expr = 'focus';
    F.fx -= dt; if (F.fx <= 0) { F.fx = 0.14; const u = (t - 0.4) / 0.9, x = sgLX(A), z = sgLZ(A); sgRing(x, z, 0.5 + 1.4 * u, 0xBFE9FF); for (let i = 0; i < 3; i++) { const a = Math.random() * 6.2832; sgPart(x + Math.cos(a) * 0.3, 0.25, z + Math.sin(a) * 0.3, Math.cos(a) * 0.5, 1.6 + Math.random(), Math.sin(a) * 0.5, 0.35, COL_ICE, 0.45); } } }
  else if (sgOnce('flash')) { const x = sgLX(A), z = sgLZ(A); sgRing(x, z, 3.2, 0xDDF3FF); sgRing(x, z, 1.9, 0xFFFFFF); sgFlash('ice'); sgShk(0.5); emote(DA, 'glee', 1.2);
    for (let i = 0; i < 26; i++) { const a = Math.random() * 6.2832, r = Math.random() * SG_R * 0.95; sgPart(Math.cos(a) * r, 0.1 + Math.random() * 0.5, Math.sin(a) * r, 0, 1.2 + Math.random() * 1.6, 0, 0.5 + Math.random() * 0.4, i % 2 ? COL_ICE : COL_WHITE, 0.35 + Math.random() * 0.3); }
    if (B.show) { const bx = sgLX(B), bz = sgLZ(B); DB.frozenT = 9; DB.spd = 0; DB.turn = 0; DB.wob = 1; DB.ip.expr = 'startle'; for (let i = 0; i < 10; i++) { const a = Math.random() * 6.2832; sgPart(bx, 0.4, bz, Math.cos(a) * 2, 1 + Math.random() * 2, Math.sin(a) * 2, 0.3, i % 2 ? COL_ICE : COL_WHITE, 0.5); } } }
  // a ring of paint all round them while they're stuck, starting the near way round (across the front)
  if (t >= 1.55 && t < 4.4) {
    if (!F.path) { const bx = sgLX(B), bz = sgLZ(B), a0 = Math.atan2(sgLZ(A) - bz, sgLX(A) - bx), e = sgCS(-1.0 * s, 0.6), dir = -s; let tot = ((Math.atan2(e[1], e[0]) - a0) * dir) % 6.2832; if (tot < 0) tot += 6.2832; if (tot < 3.1416) tot += 6.2832;
      const n = Math.ceil(tot / 0.67); F.path = []; F.pi = 0; for (let i = 1; i <= n; i++) { const a = a0 + dir * tot * i / n; F.path.push([bx + Math.cos(a) * 1.15, bz + Math.sin(a) * 1.15]); } }
    let p = F.path[F.pi]; if (Math.hypot(p[0] - sgLX(A), p[1] - sgLZ(A)) < 0.2 && F.pi < F.path.length - 1) p = F.path[++F.pi];
    const lx = sgLX(A), lz = sgLZ(A); sgGo(A, p[0], p[1], 2.9, dt); sgStripe(lx, lz, sgLX(A), sgLZ(A), 0.62, cA); sgWatch(A, B); DA.ip.expr = 'glee'; }
  // the frozen rival: shakes as they tap their way out, then the thaw
  if (DB.frozenT > 0) { if ((t > 4.2 && sgOnce('tap1')) || (t > 4.45 && sgOnce('tap2')) || (t > 4.65 && sgOnce('tap3'))) DB.iceShk = 1;
    if (t >= 4.8) { const bx = sgLX(B), bz = sgLZ(B); DB.frozenT = 0; DB.stunT = 0.9; DB.squash = 0.8; DB.wob = 1; sgRing(bx, bz, 1.0, 0xFFFFFF);
      for (let i = 0; i < 16; i++) { const a = Math.random() * 6.2832, v = 1.5 + Math.random() * 2.2; sgPart(bx, 0.45, bz, Math.cos(a) * v, 1.5 + Math.random() * 2.2, Math.sin(a) * v, 0.35 + Math.random() * 0.2, i % 2 ? COL_ICE : COL_WHITE, 0.4 + Math.random() * 0.3); } } }
  // done: a grin at you, the rival still stuck behind; a laugh when they thaw
  if (t >= 4.4) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = DB.frozenT > 0 ? 'smirk' : 'glee'; }
}
"""

VIS = r"""  // (v322) a giant: the camera eases back to take it in
  { const on = SGD.kind === 'giant' && SGD.A.D.giantT > 0; SGD.zk = (SGD.zk || 0) + ((on ? 1 : 0) - (SGD.zk || 0)) * Math.min(1, dt * 2.5); }
  // (v322) the frozen rival's shell of ice, as in a match: it grows in, shakes when they tap, and melts away
  { const B = SGD.B, D = B.D, on = B.show && D.frozenT > 0, m = SGD.ice; SGD.iceK += ((on ? 1 : 0) - SGD.iceK) * Math.min(1, dt * (on ? 16 : 22)); m.visible = SGD.iceK > 0.02;
    if (m.visible) { const gk = B.V.gk || 1, k = gk * (0.6 + 0.4 * SGD.iceK), sh = D.iceShk || 0; if (sh > 0) D.iceShk = Math.max(0, sh - dt * 5); const jx = sh * 0.07 * Math.sin(SGD.t * 97), jz = sh * 0.07 * Math.cos(SGD.t * 83);
      m.position.set(sgLX(B) + jx, 0.28 * gk, sgLZ(B) + jz); m.rotation.set(0.15 + sh * 0.14 * Math.sin(SGD.t * 71), D.yaw + 0.4, 0.1 + sh * 0.14 * Math.cos(SGD.t * 89)); m.scale.set(k * (1 + 0.05 * sh), 0.66 * k, 1.35 * k); } }
"""

CSS = r"""
/* (v322) the specials' demo: the flash of a Flash Freeze (or a rocket's landing) over the window */
#mStrokes .sgflash{position:absolute;inset:0;z-index:1;pointer-events:none;opacity:0}
#mStrokes .sgflash.ice{background:radial-gradient(ellipse at 50% 60%,rgba(255,255,255,.96) 0,rgba(214,242,255,.82) 40%,rgba(207,239,255,0) 78%)}
#mStrokes .sgflash.w{background:radial-gradient(ellipse at 50% 64%,rgba(255,255,255,.8) 0,rgba(255,255,255,.3) 36%,rgba(255,255,255,0) 66%)}
#mStrokes .sgflash.on{animation:sgflash .75s ease-out both}
@keyframes sgflash{0%{opacity:0}10%{opacity:1}100%{opacity:0}}
@keyframes sgflashq{0%{opacity:0}20%{opacity:.4}100%{opacity:0}}
@media (prefers-reduced-motion:reduce){#mStrokes .sgflash.on{animation-name:sgflashq}}
"""

def apply(s):
    # the specials' timings and Test lines
    s = rep(s, "boom: [[0.7, 0], [1.3, 1], [2.3, 2]] };", "boom: [[0.7, 0], [1.3, 1], [2.3, 2]], rocket: [[0.55, 0], [1.3, 1], [2.7, 2]], giant: [[0.5, 0], [1.05, 1], [2.4, 2]], freeze: [[1.3, 0], [1.9, 1], [3.2, 2]] };")
    s = rep(s, "const SG_T = { roller: 6.2, turret: 5.6, trap: 6.4, whirl: 6.0, boom: 5.4 };", "const SG_T = { roller: 6.2, turret: 5.6, trap: 6.4, whirl: 6.0, boom: 5.4, rocket: 5.8, giant: 5.8, freeze: 6.6 }; // (v322: the specials too)")
    # their pieces, made with the rest (and their shaders with the rest's)
    s = rep(s, "  sgLayer(root);\n", BUILD + "  sgLayer(root);\n")
    s = rep(s, "SGD.trap.visible = SGD.wg.visible = SGD.boom.visible = SGD.lane.visible = true;", "SGD.trap.visible = SGD.wg.visible = SGD.boom.visible = SGD.lane.visible = true; SGD.mk.visible = SGD.mkF.visible = SGD.mkB.visible = SGD.ice.visible = true; for (const A of SGD.AB) if (A.V.rk) A.V.rk.visible = true;")
    s = rep(s, "SGD.trap.visible = SGD.wg.visible = SGD.boom.visible = SGD.lane.visible = false;", "SGD.trap.visible = SGD.wg.visible = SGD.boom.visible = SGD.lane.visible = false; SGD.mk.visible = SGD.mkF.visible = SGD.mkB.visible = SGD.ice.visible = false; for (const A of SGD.AB) if (A.V.rk) A.V.rk.visible = false;")
    # each loop starts clean of them
    s = rep(s, "D.air = false; D.vy = 0; D.emoT = 0; A.show = true; A.ko = 0; ipReset(D); }", "D.air = false; D.vy = 0; D.emoT = 0; D.rocket = null; D.giantT = 0; D.frozenT = 0; D.slam = false; D.y = 0; D.iceShk = 0; D.gkMax = SG_GK; A.V.gk = 1; A.show = true; A.ko = 0; ipReset(D); }")
    s = rep(s, "  sgReset(A); sgReset(B); SGD.trap.visible = SGD.wg.visible = SGD.lane.visible = SGD.boom.visible = false;", "  sgReset(A); sgReset(B); SGD.trap.visible = SGD.wg.visible = SGD.lane.visible = SGD.boom.visible = false; SGD.mk.visible = SGD.mkF.visible = SGD.mkB.visible = SGD.ice.visible = false; SGD.iceK = 0; SGD.sp = {}; SGD.zk = 0;")
    s = rep(s, "  else { sgAt(A, -1.1 * s, 0.33); sgAt(B, 0.9 * s, -0.25); }", "  else if (k === 'rocket') { sgAtC(A, -0.85 * s, 0.35); sgAtC(B, 0.4 * s, -0.3); }\n  else if (k === 'giant') { sgAtC(A, -0.75 * s, -0.35); sgAtC(B, 1.15 * s, -0.75); }\n  else if (k === 'freeze') { sgAtC(A, -0.9 * s, 0.45); sgAtC(B, 0.85 * s, -0.75); }\n  else { sgAt(A, -1.1 * s, 0.33); sgAt(B, 0.9 * s, -0.25); }")
    # a frozen rival keeps its face and its look; the pad's shake settles
    s = rep(s, "function sgStep(dt) {\n  SGD.t += dt;", "function sgStep(dt) {\n  if (SGD.shk > 0) SGD.shk = Math.max(0, SGD.shk - dt * 3);\n  SGD.t += dt;")
    s = rep(s, "  DA.ip.expr = null; DB.ip.expr = null; DA.ip.watch = DB.ip.watch = null;", "  DA.ip.expr = null; DA.ip.watch = null; if (!(DB.frozenT > 0)) { DB.ip.expr = null; DB.ip.watch = null; }")
    s = rep(s, "  if (B.show && DB.st === 'play') { if (!(DB.stunT > 0) && DB.spd < 0.1)", "  if (B.show && DB.st === 'play' && !(DB.frozenT > 0)) { if (!(DB.stunT > 0) && DB.spd < 0.1)")
    s = rep(s, "  } else {\n    const BM = SGD.bm || (SGD.bm = {", "  } else if (k === 'rocket') sgRocket(dt, t, s);\n  else if (k === 'giant') sgGiant(dt, t, s);\n  else if (k === 'freeze') sgFreeze(dt, t, s);\n  else {\n    const BM = SGD.bm || (SGD.bm = {")
    s = rep(s, "// the whirlwind's lane: a strip on the pad", FNS + "// the whirlwind's lane: a strip on the pad")
    # the drawing: the frozen rival's colour and ice, shadows that grow with a giant and shrink under a rocket, the pad's shake
    s = rep(s, "if (D.stunT > 0) sgCol.lerp(COL_WHITE, 0.12 + 0.1 * Math.sin(SGD.t * 30));\n", "if (D.stunT > 0) sgCol.lerp(COL_WHITE, 0.12 + 0.1 * Math.sin(SGD.t * 30)); if (A === SGD.B && SGD.iceK > 0.01) sgCol.lerp(COL_ICE, 0.8 * SGD.iceK);\n")
    s = rep(s, "      const sk = 0.95 + 0.25 * (A.V.turK || 0); A.sh.visible = true;", "      const sk = (0.95 + 0.25 * (A.V.turK || 0)) * (A.V.gk || 1) / (1 + Math.max(0, D.y) * 0.35); A.sh.visible = true;")
    s = rep(s, "  sgShots(dt); sgFx(dt);\n}", VIS + "  sgShots(dt); sgFx(dt);\n}")
    s = rep(s, "C.up.set(0, 1, 0); C.lookAt(SG_X, 0.2, SG_Z);", "if (SGD.shk > 0 && !reduceMotion) { const a = SGD.shk * 0.09; C.position.x += (Math.random() - 0.5) * a; C.position.y += (Math.random() - 0.5) * a; C.position.z += (Math.random() - 0.5) * a; } C.up.set(0, 1, 0); C.lookAt(SG_X, 0.2 + 0.3 * (SGD.zk || 0), SG_Z);")
    s = rep(s, "(0.9 * vt * fh / r.h)), cy = Math.sin(el) * dist", "(0.9 * vt * fh / r.h)) * (1 + 0.14 * (SGD.zk || 0)), cy = Math.sin(el) * dist")
    # the demo's giant is twice the size, not three times (the window can't hold that); a match's giant is as it was
    s = rep(s, "const gt = D.giantT > 0 ? (D.giantT < 0.9 && !D.slam && Math.sin(clock * 40) > 0 ? GIANT_K * 0.75 : GIANT_K) : 1;", "const gkTo = D.gkMax || GIANT_K, gt = D.giantT > 0 ? (D.giantT < 0.9 && !D.slam && Math.sin(clock * 40) > 0 ? gkTo * 0.75 : gkTo) : 1; /* (v322: gkMax, the Strokes demo's smaller giant) */")
    # the Specials tab gets the demo, its Test, and (in landscape) the transforms' layout; skills keep their picture
    s = rep(s, "pg.classList.toggle('sgx', cat === 'item');", "pg.classList.toggle('sgx', cat !== 'skill');")
    s = rep(s, "  $('sgTest').hidden = cat !== 'item'; SGD.rectDirty = true;\n  sgDemoPick(cat === 'item' ? id : null);", "  $('sgTest').hidden = cat === 'skill'; SGD.rectDirty = true;\n  sgDemoPick(cat !== 'skill' ? id : null); // (v322: specials too)")
    s = rep(s, "const sgWant = () => strokesOpen() && stCat === 'item' && !!SGD.kind", "const sgWant = () => strokesOpen() && stCat !== 'skill' && !!SGD.kind")
    s = rep(s, "function sgTestStart() { if (stCat !== 'item' || !SGD.kind) return;", "function sgTestStart() { if (stCat === 'skill' || !SGD.kind) return;")
    s = rep(s, "  /* (specials and skills: no demo, everything centred) */", "  /* (skills: no demo, everything centred) */")
    s = rep(s, '<p class="sgcap" id="sgCap" aria-live="polite"></p></div>', '<p class="sgcap" id="sgCap" aria-live="polite"></p><i class="sgflash" id="sgFlash" aria-hidden="true"></i></div>')
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
