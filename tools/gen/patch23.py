import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# ---- scoring: diluted paint is stored as its own value and counts half ----
rep("""function stamp(x, y, z, rad, team) {
  const v = (team || 0) + 1, r2 = rad * rad,""",
"""// team codes 0/1 paint full strength, 2/3 are the same colors watered down by a puddle (half opacity, half score)
const tcode = D => D.team + (D.dilT > 0 ? 2 : 0);
function stamp(x, y, z, rad, team) {
  const tm = (team || 0) & 1, dil = (team || 0) >= 2, full = tm + 1, v = full + (dil ? 2 : 0), r2 = rad * rad,""")
rep("    if (painted[k] === v) continue; const dx = sX[k] - x, dz = sZ[k] - z;",
    "    if (painted[k] === v || (dil && painted[k] === full)) continue; const dx = sX[k] - x, dz = sZ[k] - z; // watered-down paint never weakens your own full paint")
rep("// 0 bare canvas, otherwise the color (team + 1) that painted it last; every color is yours and counts\nlet NS = 1, painted = new Uint8Array(1), paintedN = 0; const teamN = [0, 0, 0];",
    "// 0 bare canvas, 1/2 full blood/holy water, 3/4 the watered-down versions (worth half)\nlet NS = 1, painted = new Uint8Array(1), paintedN = 0; const teamN = [0, 0, 0, 0, 0];")
rep("const teamCov = t => teamN[t + 1] / NS * 100; // exact share of the canvas held by a side",
    "const teamCov = t => (teamN[t + 1] + 0.5 * teamN[t + 3]) / NS * 100; // share of the canvas held by a side (watered-down paint counts half)\nconst cellGain = (v, me, steal) => v === me ? 0 : !v ? 1 : v === me + 2 ? 0.5 : v === 5 - me ? (1 + steal) * 0.5 : steal;")
# shader: color from team & 1, half alpha when watered down
rep("  vec3 wetC = vTeam < 0.5 ? uWetA[0] : uWetA[1];\n  vec3 dryC = vTeam < 0.5 ? uDryA[0] : uDryA[1];",
    "  float tm = mod(vTeam + 0.25, 2.0), dilA = vTeam > 1.5 ? 0.5 : 1.0;\n  vec3 wetC = tm < 0.75 ? uWetA[0] : uWetA[1];\n  vec3 dryC = tm < 0.75 ? uDryA[0] : uDryA[1];")
rep("  gl_FragColor = vec4(col * lit, 1.0);\n}`;\nconst paintUniforms",
    "  gl_FragColor = vec4(col * lit, dilA);\n}`;\nconst paintUniforms")
# blended but still drawn in the opaque pass, so paint keeps its painted-last-on-top order
rep("const paintMat = new THREE.ShaderMaterial({ uniforms: paintUniforms, vertexShader: PAINT_VS, fragmentShader: PAINT_FS, side: THREE.DoubleSide, depthWrite: false,",
    "const paintMat = new THREE.ShaderMaterial({ uniforms: paintUniforms, vertexShader: PAINT_VS, fragmentShader: PAINT_FS, side: THREE.DoubleSide, depthWrite: false, blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor,")
rep("pR[nP] = W / 2 * 0.85 + PR * 0.3; pTeam[nP] = team; nP++;", "pR[nP] = W / 2 * 0.85 + PR * 0.3; pTeam[nP] = team & 1; nP++;")
rep("  splats.push({ mesh, x: cx, y: cy, z: cz, t, w: 1, hr: R * 0.78 + PR * 0.3, team });", "  splats.push({ mesh, x: cx, y: cy, z: cz, t, w: 1, hr: R * 0.78 + PR * 0.3, team: team & 1 });")
# paint calls use the team code
rep("function cap(D) { if (nP > 0 && !D.air) addSplat(D.x, D.y, D.z, D.yaw, TW * 0.52, dryClock, true, false, D.team); }",
    "function cap(D) { if (nP > 0 && !D.air) addSplat(D.x, D.y, D.z, D.yaw, TW * 0.52, dryClock, true, false, tcode(D)); }")
rep("  addSplat(p.x, p.y, p.z, D.yaw, SLAM_R, dryClock, false, true, D.team);", "  addSplat(p.x, p.y, p.z, D.yaw, SLAM_R, dryClock, false, true, tcode(D));")
rep("  addSplat(D.x, D.y, D.z, D.yaw, R, dryClock, false, true, D.team); shockwave(D.x, D.y, D.z, R,", "  addSplat(D.x, D.y, D.z, D.yaw, R, dryClock, false, true, tcode(D)); shockwave(D.x, D.y, D.z, R,")
rep("  addSplat(B.x, B.y, B.z, A.yaw, 0.95, dryClock, false, false, A.team);", "  addSplat(B.x, B.y, B.z, A.yaw, 0.95, dryClock, false, false, tcode(A));")
rep("addSplat(D.x, D.y, D.z, D.yaw, SPLAT_R * 1.15, dryClock, false, false, D.team);", "addSplat(D.x, D.y, D.z, D.yaw, SPLAT_R * 1.15, dryClock, false, false, tcode(D));")
rep("addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, D.team);", "addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, tcode(D));")
rep("D.power && D.power.type === 'roller' ? 2.6 : 1, D.team, D.rb); } }", "D.power && D.power.type === 'roller' ? 2.6 : 1, tcode(D), D.rb); } }")
# CPU's sense of what's worth painting
rep("const v = painted[k]; g += v === me ? 0 : v ? AI.steal : 1; }", "g += cellGain(painted[k], me, AI.steal); }")
rep("let g = 0, own = 0; for (const k of n.smp) { const v = painted[k]; if (v === me) own++; else g += v ? stealW : 1; }",
    "let g = 0, own = 0; for (const k of n.smp) { const v = painted[k]; if (v === me) own++; else { if (v === me + 2) own += 0.5; g += cellGain(v, me, stealW); } }")
rep("for (const r of rivals) if (r.on && !(Math.random() < AI.slip)) NAV.near(r.x, r.z, r.y, r.hit + 0.55, n => { nMult[n.id] += 7; });",
    "for (const r of rivals) if (r.on && !(Math.random() < AI.slip)) NAV.near(r.x, r.z, r.y, r.hit + 0.55, n => { nMult[n.id] += 4; });")

# ---- the character: a puddle waters you down for a couple of seconds instead of slowing you ----
rep("reason: null, spawnImm: false, knockT: 0,", "reason: null, spawnImm: false, dilT: 0, knockT: 0,")
rep("      // slow zones: hard paint of either color, and boiling water\n      D.inBoil = rivals.some(r => r.on && Math.abs(D.y - r.y) < 0.3 && Math.hypot(D.x - r.x, D.z - r.z) < r.hit);\n      D.slowed = D.inBoil || (hardPhase && dryAt(D.x, D.z, D.y, 0, -1));",
    """      // rain puddles water your blood down; hard paint of either color slows you
      D.inBoil = rivals.some(r => r.on && Math.abs(D.y - r.y) < 0.3 && Math.hypot(D.x - r.x, D.z - r.z) < r.hit);
      if (D.inBoil) { if (D.dilT <= 0) dilute(D); D.dilT = DIL_T; }
      D.slowed = hardPhase && dryAt(D.x, D.z, D.y, 0, -1);""")
rep("  if (D.knockT > 0) D.knockT -= dt;\n", "  if (D.knockT > 0) D.knockT -= dt;\n  if (D.dilT > 0) { D.dilT -= dt; if (D.spd > 1 && Math.random() < dt * 10) { const a = Math.random() * 6.283; spawnPart(D.x + Math.cos(a) * 0.3, D.y + 0.35, D.z + Math.sin(a) * 0.3, Math.cos(a) * 1.2, 1.5 + Math.random(), Math.sin(a) * 1.2, 0.3, boilPartMat, 0.45); } }\n")
rep("D.st = 'ko'; D.lastHit = null;", "D.st = 'ko'; D.dilT = 0; D.lastHit = null;")
rep("function splashPuddle(r) {",
    """const DIL_T = 2;
function dilute(D) {
  for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283; spawnPart(D.x, D.y + 0.2, D.z, Math.cos(a) * 2.4, 1.8 + Math.random() * 1.6, Math.sin(a) * 2.4, 0.35, boilPartMat, 0.6); }
  if (hearable(D)) AU.splat(0.4);
  if (D === P) { popText('Watered down!'); buzz(8); hint('dilute', 'Puddles water you down: half-strength paint for 2 seconds', 3); }
}
function splashPuddle(r) {""")
rep("  r.on = false; r.k = 0; r.target = 0; r.regrow = 15; r.g.visible = false;", "  r.on = false; r.k = 0; r.target = 0; r.delay = 0; r.g.visible = false;")
# a watered-down blob looks pale
rep("    if (P.exposed && P.st === 'play') tmpCol.lerp(COL_BURN, 0.3 + 0.3 * Math.sin(clock * 28));",
    "    if (P.exposed && P.st === 'play') tmpCol.lerp(COL_BURN, 0.3 + 0.3 * Math.sin(clock * 28));\n    if (P.dilT > 0) tmpCol.lerp(COL_WHITE, 0.5 * Math.min(1, P.dilT * 2));")
rep("    tmpCol2.copy(COL_HOLY); if (H.exposed && H.st === 'play') tmpCol2.lerp(COL_WHITE, 0.35 + 0.3 * Math.sin(clock * 28));",
    "    tmpCol2.copy(COL_HOLY); if (H.exposed && H.st === 'play') tmpCol2.lerp(COL_WHITE, 0.35 + 0.3 * Math.sin(clock * 28));\n    if (H.dilT > 0) tmpCol2.lerp(COL_WHITE, 0.5 * Math.min(1, H.dilT * 2));")

# ---- puddles: none at the start, rain leaves a few, they dry up over time and all at once under the sun ----
rep("  return { g, glow, x, y, z, rad: R, hit: R * 0.82 + PR * 0.25, on: true, k: 1, target: 1, regrow: 0, ph: rng(seed + 9)() * 6.28 };",
    "  g.visible = false; g.scale.setScalar(0.02);\n  return { g, glow, x, y, z, rad: R, hit: R * 0.82 + PR * 0.25, on: false, k: 0, target: 0, delay: 0, life: 0, ph: rng(seed + 9)() * 6.28 };")
rep("new THREE.MeshBasicMaterial({ color: 0xFF7A45, transparent: true, opacity: 0.25,", "new THREE.MeshBasicMaterial({ color: 0x9FD8FF, transparent: true, opacity: 0.25,")
rep("// a ground pound splashes the water away; it fills back up a while later",
    """const PUD_ADD = 4, PUD_MAX = 6, PUD_LIFE = 20;
function rainPuddles() {
  const live = rivals.filter(r => r.on || r.target === 1).length, free = rivals.filter(r => !r.on && r.target === 0 && r.k < 0.05 && ![P, H].some(D => D.st !== 'ko' && Math.hypot(D.x - r.x, D.z - r.z) < r.rad + 1.6));
  for (let n = Math.min(PUD_ADD, PUD_MAX - live); n > 0 && free.length; n--) { const r = free.splice(Math.random() * free.length | 0, 1)[0]; r.delay = 0.6 + Math.random() * (RAIN_TIME - 1.5); }
}
function dryPuddles() { for (const r of rivals) { r.delay = 0; if (r.on || r.target === 1) { r.on = false; r.target = 0; r.steam = 1.5; } } }
// a ground pound splashes the water away for good""")
rep("""    if (!r.on && r.target === 0 && r.regrow > 0) { r.regrow -= dt; if (r.regrow <= 0) r.target = 1; } // splashed water fills back in
    if (r.k === r.target && (r.target === 0 || r.on)) continue;
    r.k += (r.target - r.k) * Math.min(1, dt * (r.target > r.k ? 1.5 : 2.4)); if (Math.abs(r.k - r.target) < 0.01) r.k = r.target;
    if (r.target === 1 && !r.on && r.k > 0.92) r.on = true;""",
"""    if (r.delay > 0) { r.delay -= dt; if (r.delay <= 0) r.target = 1; } // rain fills a puddle in
    if (r.on) { r.life -= dt; if (r.life <= 0) { r.on = false; r.target = 0; r.steam = 0.6; } } // and over time it dries up
    if (r.steam > 0) r.steam -= dt;
    if (r.k === r.target && (r.target === 0 || r.on)) continue;
    r.k += (r.target - r.k) * Math.min(1, dt * (r.target > r.k ? 1.2 : 1.1)); if (Math.abs(r.k - r.target) < 0.01) r.k = r.target;
    if (r.target === 1 && !r.on && r.k > 0.7) { r.on = true; r.life = PUD_LIFE + Math.random() * 8; }""")
# steam only while one dries up
rep("    r.glow.material.opacity = (0.18 + 0.12 * Math.sin(clock * 5 + r.ph)) * r.k;\n    if (dt > 0 && Math.random() < dt * 5 &&",
    "    r.glow.material.opacity = (0.18 + 0.12 * Math.sin(clock * 5 + r.ph)) * r.k;\n    if (dt > 0 && r.steam > 0 && Math.random() < dt * 14 &&")
rep("  // boiling water: a pulsing hot rim and steam curling up", "  // rain puddles: a soft rim, and steam curling up while one dries")
# weather hooks
rep("banner('Rain!', 'Everyone speeds up.'); }", "banner('Rain!', 'Puddles are forming. Everyone speeds up.'); rainPuddles(); }")
rep("else if (wxPhase === 'warn') { setWx('sun', SUN_TIME); sunsSeen++;", "else if (wxPhase === 'warn') { setWx('sun', SUN_TIME); dryPuddles(); sunsSeen++;")
rep("banner('Rain!', 'Paint softens and everyone speeds up.'); }", "banner('Rain!', 'Paint softens and puddles form.'); rainPuddles(); }")
# how to play
rep("""<li><span class="dot boil"></span>Hard paint and boiling water won't kill you, but they slow you way down. Pound boiling water to refill your blood.</li>""",
    """<li><span class="dot boil"></span>Rain leaves a few puddles. Roll through one and your blood gets watered down for 2 seconds: it paints faint and only counts half. Puddles dry up after a while, and all at once when the sun comes out. Pound one to splash it away and refill your blood.</li>
        <li><span class="dot sun"></span>Hard paint won't kill you, but it slows you way down until the rain softens it.</li>""")
open(F, 'w').write(s)
print('ok')
