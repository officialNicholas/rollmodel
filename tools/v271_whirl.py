"""v271: a new item, the Whirlwind (after the user's clip of a charge that wraps the character in a sideways tornado of paint).

Tap it: a short wind-up (the tornado spins up round you), then you charge forward at about two and a half times your pace for a
little over a second, wrapped in spiralling ribbons of your own paint with white speed streaks and droplets flung off them. You can
steer a little, and it leans toward a rival just ahead. It paints a wide trail as it goes; any rival it touches is splatted (knocked
out), and it ends in a burst of paint that splats anyone close. You can't be hurt while it spins. It stops short of a drop instead of
flying off the edge.

It spawns on the canvas like the others, CPUs use theirs when a rival is lined up, and it's a fourth choice for the item you start
with under Abilities (painted icon from Ludo.ai: tools/assets/item_whirl_256.webp)."""
import base64, os, re
A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CORE = r"""
// ---------- v271: the Whirlwind: a wind-up, then a charge wrapped in a sideways tornado of your paint. It paints a wide trail, splats any
// rival it runs into and ends in a burst; you're untouchable while it spins, and it stops short of a drop ----------
const WHIRL_WIND = 0.3, WHIRL_DASH = 1.1, WHIRL_END = 0.4, WHIRL_R = 1.75, WHIRL_TRAIL = 1.9, WHIRL_STEP = 0.7, WHIRL_BURST = 2.4;
const whirlV = () => cfg.speed * MOVE_K * 2.5;
// the tornado: strips spiralling round the forward axis (+z), narrow at the nose and flaring wide behind (u: tail 0 to nose 1, v across)
const WHIRL_G = (() => {
  const strip = (L, turns, ph, r0, r1, z0, z1, w, tilt) => { const N = 56, base = L.pos.length / 3, at = u => { const a = ph + turns * 6.2832 * u, r = r0 + (r1 - r0) * u; return [Math.cos(a) * r, Math.sin(a) * r, z0 + (z1 - z0) * u]; };
    for (let i = 0; i <= N; i++) { const u = i / N, p = at(u), q = at(Math.min(1, u + 0.01)), o = at(Math.max(0, u - 0.01)), hw = w * 0.5 * Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.12)), 0.6) + 0.002;
      // across the band: in the tornado's surface, square to the way it runs (outward x along), turned a little by tilt
      const tx = q[0] - o[0], ty = q[1] - o[1], tz = q[2] - o[2], rl = Math.hypot(p[0], p[1]) || 1, rx = p[0] / rl, ry = p[1] / rl;
      let cx = ry * tz, cy = -rx * tz, cz = rx * ty - ry * tx; const cl = Math.hypot(cx, cy, cz) || 1; cx /= cl; cy /= cl; cz /= cl;
      const ax = cx + rx * tilt * 0.35, ay = cy + ry * tilt * 0.35, az = cz, al = Math.hypot(ax, ay, az);
      for (const s of [-1, 1]) { L.pos.push(p[0] + s * hw * ax / al, p[1] + s * hw * ay / al, p[2] + s * hw * az / al); L.uv.push(u, s < 0 ? 0 : 1); }
      if (i < N) { const k = base + i * 2; L.idx.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); } } };
  const mk = f => { const L = { pos: [], uv: [], idx: [] }; f(L); const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(L.pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(L.uv, 2)); g.setIndex(L.idx); g.computeVertexNormals(); return g; };
  return { paint: mk(L => { for (let k = 0; k < 3; k++) strip(L, 1.1, k * 2.0944, 1.05, 0.32, -2.8, 0.8, 0.8, 0.45); for (let k = 0; k < 2; k++) strip(L, -0.85, 0.8 + k * 3.1416, 0.66, 0.26, -1.9, 0.6, 0.46, -0.35); }),
    streak: mk(L => { for (let k = 0; k < 4; k++) strip(L, 0.6, 0.5 + k * 1.5708, 1.18, 0.6, -3.0, 0.3, 0.09, 0.15); }) };
})();
const WHIRL_VS = 'varying vec2 vUv; varying vec3 vN; varying vec3 vV; void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position, 1.0); vN = normalize(normalMatrix * normal); vV = -mv.xyz; gl_Position = projectionMatrix * mv; }';
// glossy paint: lit, a hard highlight and a rim, light streaks running along it; fading out at the tail, the nose and the edges
const whirlPaintM = new THREE.ShaderMaterial({ uniforms: { uCol: { value: new THREE.Color(0xE3122F) }, uA: { value: 1 }, uT: { value: 0 } }, vertexShader: WHIRL_VS,
  fragmentShader: `uniform vec3 uCol; uniform float uA, uT; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
    void main(){ float u = vUv.x, v = vUv.y, a = smoothstep(0.0, 0.2, u) * smoothstep(1.0, 0.86, u) * (1.0 - pow(abs(v * 2.0 - 1.0), 5.0));
      vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n; vec3 V = normalize(vV), L = normalize(vec3(0.35, 0.85, 0.4)), H = normalize(L + V);
      float d = max(dot(n, L), 0.0), sp = pow(max(dot(n, H), 0.0), 40.0), rim = pow(1.0 - abs(dot(n, V)), 2.5), fl = 0.5 + 0.5 * sin(u * 26.0 - uT * 1.4 + v * 2.0);
      float band = exp(-pow((v - 0.5) * 3.6, 2.0)), edge = smoothstep(0.0, 0.18, v) * smoothstep(1.0, 0.82, v);
      vec3 base = mix(uCol * 0.5, mix(uCol, vec3(1.0), 0.26 * band * (0.6 + 0.4 * fl)), edge); /* (a lighter band down each ribbon, darker at its edges, so the spiral reads over paint of the same colour) */
      vec3 c = base * (0.7 + 0.45 * d) + vec3(1.0) * (0.8 * sp + 0.12 * rim);
      gl_FragColor = vec4(c, clamp(a * uA * 0.95, 0.0, 1.0)); }`,
  transparent: true, depthWrite: false, side: THREE.DoubleSide });
const whirlStreakM = new THREE.ShaderMaterial({ uniforms: { uA: { value: 1 } }, vertexShader: WHIRL_VS,
  fragmentShader: `uniform float uA; varying vec2 vUv; void main(){ float u = vUv.x, a = smoothstep(0.0, 0.6, u) * smoothstep(1.0, 0.8, u) * (1.0 - pow(abs(vUv.y * 2.0 - 1.0), 2.0)); gl_FragColor = vec4(vec3(1.0), a * 0.85 * uA); }`,
  transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending });
const whirlPickM = whirlPaintM.clone(); whirlPickM.uniforms.uCol.value.set(0xE3122F);
// (one kept in the scene, hidden, so the warm-up builds its shaders before a match needs them)
{ const g = new THREE.Group(); g.add(new THREE.Mesh(WHIRL_G.paint, whirlPaintM), new THREE.Mesh(WHIRL_G.streak, whirlStreakM)); g.visible = false; scene.add(g); }
function whirlFx(D) {
  if (D.wfx) return D.wfx;
  const g = new THREE.Group(), spin = new THREE.Group(); g.add(spin);
  const pm = whirlPaintM.clone(), sm = whirlStreakM.clone(), a = new THREE.Mesh(WHIRL_G.paint, pm), b = new THREE.Mesh(WHIRL_G.streak, sm);
  a.renderOrder = 36; b.renderOrder = 37; a.frustumCulled = b.frustumCulled = false; spin.add(a, b); g.visible = false; scene.add(g);
  return (D.wfx = { g, spin, pm, sm });
}
function startWhirl(D) {
  if (D.charging) clearCharge(D); if (D === P) { holdCharge = false; slingOff(); }
  if (D.ai) { let best = null, bd = 14; for (const O of foes(D)) if (O.st === 'play') { const d = Math.hypot(O.x - D.x, O.z - D.z); if (d < bd) { bd = d; best = O; } } if (best) D.yaw = Math.atan2(best.x - D.x, best.z - D.z); } // (a CPU squares up to the nearest rival)
  D.whirl = { ph: 'wind', t: 0, spinA: 0, k: 0, swT: 0, lx: D.x, lz: D.z };
  const fx = whirlFx(D); fx.pm.uniforms.uCol.value.copy(tmat(D).color); fx.g.visible = true;
  emote(D, 'glee', 1.2);
  if (D === P) { AU.rise(); buzz(10); banner('Whirlwind!', 'Steer it into a rival'); } else if (hearable(D)) AU.rise();
}
function endWhirl(D) { D.whirl = null; if (D.wfx) D.wfx.g.visible = false; }
// the end: a burst of paint round you, and anyone close splatted
function whirlBurst(D) {
  addSplat(D.x, D.y, D.z, D.yaw, WHIRL_TRAIL * 1.45, dryClock, false, false, tcode(D), 0.15); splash(D, 2.2); shockwave(D.x, D.y, D.z, 2.8, TEAMS[D.team].wet);
  for (const O of foes(D)) if (O.st === 'play' && !safe(O) && !(O.immuneT > 0) && Math.abs(O.y - D.y) < 1.4 && Math.hypot(O.x - D.x, O.z - D.z) < WHIRL_BURST) knockOut(O, 'crush', D);
  if (D === P) { shake = Math.max(shake, 0.25); fovKick = Math.max(fovKick, 9); buzz([15, 20, 30]); AU.burst(1); AU.splat(1.3); } else if (hearable(D)) { AU.burst(0.6); AU.splat(1); }
}
function whirlTick(D, dt) {
  const W = D.whirl, fx = whirlFx(D); W.t += dt;
  const fwx = Math.sin(D.yaw), fwz = Math.cos(D.yaw);
  if (W.ph === 'wind') { W.k = Math.min(1, W.t / WHIRL_WIND); W.spinA += dt * (8 + 24 * W.k);
    if (Math.random() < dt * 40) { const a = Math.random() * 6.283, r = 1.3; spawnPart(D.x + Math.cos(a) * r, D.y + 0.4 + Math.sin(a) * 0.5, D.z + Math.sin(a) * r, -Math.cos(a) * 3, 0.4, -Math.sin(a) * 3, 0.3, puHaloMat, 0.35, 0); } // (sparks drawn in)
    if (W.t >= WHIRL_WIND) { W.ph = 'dash'; W.t = 0; W.lx = D.x; W.lz = D.z; if (D === P) { AU.boost(); AU.dash(); shake = Math.max(shake, 0.12); buzz(14); } else if (hearable(D)) AU.dash(); } }
  else if (W.ph === 'dash') {
    W.spinA += dt * 22;
    // leans toward a rival just ahead (inside a narrow cone), so a fair aim lands
    let tg = null, tb = 0.55; for (const O of foes(D)) if (O.st === 'play' && !safe(O)) { const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz); if (d > 9 || d < 0.5) continue; const da = Math.abs(wrapA(Math.atan2(dx, dz) - D.yaw)); if (da < tb) { tb = da; tg = O; } }
    if (tg) D.yaw += clamp(wrapA(Math.atan2(tg.x - D.x, tg.z - D.z) - D.yaw), -1.6 * dt, 1.6 * dt);
    // the trail: a wide splat every so often
    if (Math.hypot(D.x - W.lx, D.z - W.lz) >= WHIRL_STEP) { W.lx = D.x; W.lz = D.z; addSplat(D.x, D.y, D.z, D.yaw, WHIRL_TRAIL, dryClock, false, false, tcode(D), 0.25); }
    // anyone in its path
    for (const O of foes(D)) if (O.st === 'play' && !safe(O) && !(O.immuneT > 0) && Math.abs(O.y - D.y) < 1.4 && Math.hypot(O.x - D.x, O.z - D.z) < WHIRL_R) { knockOut(O, 'crush', D); if (D === P) { shake = Math.max(shake, 0.2); buzz([12, 20, 12]); } }
    // droplets flung off the spiral
    for (let n = Math.random() < dt * 70 ? 1 + (Math.random() < 0.5 ? 1 : 0) : 0; n > 0; n--) { const a = W.spinA + Math.random() * 6.283, rx = Math.cos(D.yaw), rz = -Math.sin(D.yaw), ca = Math.cos(a), sa = Math.sin(a);
      spawnPart(D.x - fwx * 0.6 + rx * ca * 0.95, D.y + 0.42 + Math.max(-0.3, sa * 0.95), D.z - fwz * 0.6 + rz * ca * 0.95, rx * -sa * 4.5 - fwx * 2.5, 1.2 + ca * 4.5, rz * -sa * 4.5 - fwz * 2.5, 0.5, tmat(D), 0.6 + Math.random() * 0.5); }
    if (D === P) { fovKick = Math.max(fovKick, 7); shake = Math.max(shake, 0.04); }
    W.swT -= dt; if (W.swT <= 0) { W.swT = 0.26; if (D === P || hearable(D)) AU.swish(); }
    // done, or about to run off a drop or into a wall: it ends here
    const g = surfaceUnder(D.x + fwx * 0.9, D.z + fwz * 0.9, D.y + STEP, true);
    if (W.t >= WHIRL_DASH || g === -Infinity || g < D.y - 0.6 || (W.t > 0.2 && D.spd < 1)) { if (W.t < WHIRL_DASH) D.spd = 0; W.ph = 'end'; W.t = 0; whirlBurst(D); } }
  else { W.spinA += dt * 12; W.k = W.t / WHIRL_END; if (W.t >= WHIRL_END) return endWhirl(D); }
  // the tornado: on you, along your heading, spinning; it spins up and swells in, and the burst throws it wide as it fades
  fx.g.position.set(D.x, D.y + 0.55, D.z); fx.g.rotation.set(0, D.yaw, 0); fx.spin.rotation.z = W.spinA;
  const s = 1.15 * (W.ph === 'wind' ? 0.35 + 0.6 * W.k : W.ph === 'dash' ? 1 + 0.05 * Math.sin(W.t * 30) : 1 + 0.7 * W.k);
  fx.g.scale.set(s, s * 0.8, W.ph === 'wind' ? 0.45 + 0.4 * W.k : W.ph === 'end' ? 1 - 0.3 * W.k : 1);
  const a = W.ph === 'end' ? Math.max(0, 1 - W.k) : W.ph === 'wind' ? 0.4 + 0.6 * W.k : 1;
  fx.pm.uniforms.uA.value = a; fx.pm.uniforms.uT.value = W.spinA; fx.sm.uniforms.uA.value = a * (W.ph === 'dash' ? 1 : 0.5);
}
"""

ICON = """ITEM_ICON.whirl = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M4 9c4-3 28-3 32 0-3 3.6-29 3.6-32 0z"/><path d="M8 16.5c3.5-2.6 20.5-2.6 24 0-3 3.1-21 3.1-24 0z"/><path d="M11.5 23.5c3-2.1 14-2.1 17 0-2.6 2.7-14.4 2.7-17 0z"/><path d="M15.5 30c2-1.5 7-1.5 9 0-2 2.3-7 2.3-9 0z"/><path d="M18.5 35.5c1-.9 2.6-.9 3.6 0-1 1.5-2.6 1.5-3.6 0z"/></svg>'; // (v271)
"""

def apply(s):
    # the item itself
    s = rep(s, "  trap: { name: 'Paint Trap', dur: 0,", "  whirl: { name: 'Whirlwind', dur: 0, tip: 'Whirlwind! Charge ahead in a tornado of paint.' },\n  trap: { name: 'Paint Trap', dur: 0,")
    s = rep(s, "const puIconMat = toon(0xE3122F), puHaloMat = toon(0xFFFFFF);\n", "const puIconMat = toon(0xE3122F), puHaloMat = toon(0xFFFFFF);\n" + CORE.lstrip('\n'))
    m = re.search(r"\nITEM_ICON\.trap = '.*?';\n", s); assert m; s = s[:m.end()] + ICON + s[m.end():]
    # its pick-up: a little tornado standing in the bubble
    s = rep(s, "  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]);",
            "  else if (type === 'whirl') { const t = new THREE.Group(); t.rotation.x = Math.PI / 2; t.scale.setScalar(0.24); t.position.y = -0.17; spin.add(t); const a = new THREE.Mesh(WHIRL_G.paint, whirlPickM), b = new THREE.Mesh(WHIRL_G.streak, whirlStreakM); a.renderOrder = b.renderOrder = 9; t.add(a, b); }\n"
            "  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]);")
    s = rep(s, "for (const t of ['roller', 'turret']) try { makePowerMesh(t).g.visible = false; } catch (e) {}", "for (const t of ['roller', 'turret', 'whirl']) try { makePowerMesh(t).g.visible = false; } catch (e) {}")
    # on the canvas: in the mix with the others (outside the lessons)
    s = rep(s, "const w = { roller: 0.42, turret: 0.3, trap: 0.28 };", "const w = { roller: 0.42, turret: 0.3, trap: 0.28, whirl: 0.3 };")
    s = rep(s, "let r = Math.random() * (w.roller + w.turret + w.trap); for (const k of ['roller', 'turret', 'trap']) if ((r -= w[k]) <= 0) return k; return 'roller';",
            "const ks = Object.keys(w); let r = Math.random() * ks.reduce((q, k) => q + w[k], 0); for (const k of ks) if ((r -= w[k]) <= 0) return k; return 'roller';")
    # using it
    s = rep(s, "  if (!D.held || (D === P && tut && tut.hideItem) || D.st !== 'play' || D.flatT > 0",
            "  if (!D.held || D.whirl || (D === P && tut && tut.hideItem) || D.st !== 'play' || D.flatT > 0")
    s = rep(s, "const type = D.held; if (type === 'turret' && D.air) return false;",
            "const type = D.held; if ((type === 'turret' || type === 'whirl') && D.air) return false;")
    s = rep(s, "  if (type === 'trap') { dropTrap(D);", "  if (type === 'whirl') { startWhirl(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return true; }\n  if (type === 'trap') { dropTrap(D);")
    # while it spins: untouchable, no jumping, rolling or pounding, no ducking into a basin; its pace, a little less steering
    s = rep(s, "const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0) && !D.rocket && !D.turret;",
            "const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0) && !D.rocket && !D.turret && !D.whirl;")
    s = rep(s, "const safe = D => D.rollT > 0 || D.dashT > 0;", "const safe = D => D.rollT > 0 || D.dashT > 0 || !!D.whirl;")
    s = rep(s, "function stepBlob(D, dt) {\n  if (D.st === 'out') return;\n",
            "function stepBlob(D, dt) {\n  if (D.whirl && (D.st !== 'play' || D.rocket || D.turret || state !== 'play')) endWhirl(D); // (v271: knocked out, out, or the match over: it stops)\n  if (D.st === 'out') return;\n")
    s = rep(s, "  else if ((D.slam && !D.missile) || D.flatT > 0 || D.stunT > 0) D.spd = 0;\n",
            "  else if ((D.slam && !D.missile) || D.flatT > 0 || D.stunT > 0) D.spd = 0;\n"
            "  else if (!D.air && D.whirl) D.spd = D.whirl.ph === 'wind' ? D.spd * Math.exp(-dt * 12) : D.whirl.ph === 'dash' ? whirlV() : D.spd + (cfg.speed * spdK(D) - D.spd) * Math.min(1, dt * 4);\n")
    s = rep(s, "D.charging ? 0.75 : D.rollT > ROLL_T - ROLL_DASH ? 0.4 : 1);", "D.whirl ? 0.5 : D.charging ? 0.75 : D.rollT > ROLL_T - ROLL_DASH ? 0.4 : 1);")
    s = rep(s, "  if (!D.ai && D.flung && D.air) ledgeNudge(D, dt);\n  moveFlat(D, dt);\n", "  if (D.whirl) whirlTick(D, dt);\n  if (!D.ai && D.flung && D.air) ledgeNudge(D, dt);\n  moveFlat(D, dt);\n")
    s = rep(s, "  if (D.giantT <= 0) for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0", "  if (D.giantT <= 0 && !D.whirl) for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0")
    s = rep(s, "D.held = null; D.heldT = 0; D.held2 = null; D.orbSaved = null; D.frozenT = 0; }", "D.held = null; D.heldT = 0; D.held2 = null; D.orbSaved = null; D.frozenT = 0; if (D.whirl) endWhirl(D); }")
    # a CPU lets it go when a rival is lined up in front, not too far (or after a while)
    s = rep(s, ": D.heldT > 1 + Math.random() * 1.5)) useHeld(D); }",
            ": D.held === 'whirl' ? (O && O.st === 'play' && Math.hypot(O.x - D.x, O.z - D.z) < 10 && Math.hypot(O.x - D.x, O.z - D.z) > 2 && Math.abs(wrapA(Math.atan2(O.x - D.x, O.z - D.z) - D.yaw)) < 0.7 && D.heldT > 0.5) || D.heldT > 8 : D.heldT > 1 + Math.random() * 1.5)) useHeld(D); }")
    # Abilities: a fourth item to start with; CPUs start with it now and then too
    s = rep(s, "cpuItem = () => { const r = Math.random(); return r < 0.4 ? 'roller' : r < 0.7 ? 'turret' : 'trap'; };",
            "cpuItem = () => { const r = Math.random(); return r < 0.32 ? 'roller' : r < 0.56 ? 'turret' : r < 0.78 ? 'trap' : 'whirl'; };\n"
            "ST_ITEMS.push({ id: 'whirl', name: 'Whirlwind', desc: 'Charge ahead in a tornado of paint.', does: ['Tap it: you wind up, then charge ahead wrapped in a tornado of your paint', 'Any rival in its path is splatted and knocked out', 'Leaves a wide trail and ends in a burst. Steer as you go'] }); // (v271)")
    img = 'data:image/webp;base64,' + base64.b64encode(open(A + 'item_whirl_256.webp', 'rb').read()).decode()
    s = rep(s, "for (const k of ['roller', 'trap', 'turret']) STROKE_ICON[k] = stImg(k);\n",
            "for (const k of ['roller', 'trap', 'turret']) STROKE_ICON[k] = stImg(k);\nST_IMG.whirl = '" + img + "'; STROKE_ICON.whirl = stImg('whirl'); // (v271)\n")
    return s
