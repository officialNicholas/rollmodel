#!/usr/bin/env python3
"""Two things. A jump earns the mid-air dash a pot burst did: swipe up or down while airborne to dash forward or back. And the turret is a machine with a face: a steel pod on the bolted base with two big blinking eyes, the barrel out of its front for a mouth, a band in your colour, and a clear tank on top where your paint drains as you fire. The pick-up is the same machine, small, and the roller pick-up gets the face it was always built with. On top of ui63_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui63_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the air dash off a jump ----
rep("D.air = true; D.vy = JUMP_V; D.stroke++;", "D.air = true; D.vy = JUMP_V; D.airSling = true; D.stroke++;")
rep("Tap to jump, swipe up to roll. Hold to stop", "Tap to jump, swipe up to roll, swipe up or down mid-jump to dash. Hold to stop", 2)
rep("Burst out of it, then swipe up or down in mid-air to dash forward or back.", "Jump, or burst out of it, then swipe up or down in mid-air to dash forward or back.")

# ---- the turret machine ----
a = s.index("  // the glass dome the ink sits in: a sphere open at the bottom, meeting the collar"); b = s.index("return { baseG, barrelG, domeG, inkG, inkY: -1.08, dir, tip: at(bl + 0.05) };") + len("return { baseG, barrelG, domeG, inkG, inkY: -1.08, dir, tip: at(bl + 0.05) };")
s = s[:a] + r'''  // the pod: a steel ball on a short neck in the collar, a seam round its crown, a bolted joint on each side; the barrel comes out of its front for a mouth
  const podR = 0.95, podC = 0.05, pod = new THREE.SphereGeometry(podR, seg, HI ? 32 : 18).translate(0, podC, 0), neck = new THREE.CylinderGeometry(0.6, 0.68, 0.5, seg).translate(0, -0.62, 0);
  const ear = sd => new THREE.CylinderGeometry(0.2, 0.2, 0.1, 16).rotateZ(Math.PI / 2).translate(sd * 0.93, podC + 0.02, 0), earBolt = sd => new THREE.CylinderGeometry(0.07, 0.07, 0.05, 10).rotateZ(Math.PI / 2).translate(sd * 0.99, podC + 0.02, 0);
  const podG = vcGeo([[pod, (x, y, z, o) => o.copy(y > podC + 0.27 && y < podC + 0.34 ? SVD : y > podC + 0.34 ? SVL : SV)], [neck, SVD], [ear(1), SVD], [ear(-1), SVD], [earBolt(1), SVL], [earBolt(-1), SVL]]);
  // the face: two big eyes on the front of the pod, each a white with a dark pupil and a shine, set along the pod's surface (their own mesh, so they can blink)
  const WH = hexC(0xFFFFFF), INK = hexC(0x23102E), EY = 0.4, EX = 0.34, eye = [];
  for (const sx of [-1, 1]) { const ex = sx * EX, ly = EY - podC, ez = Math.sqrt(podR * podR - ex * ex - ly * ly), n = new THREE.Vector3(ex, ly, ez).normalize(), q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), n), place = (g, fwd) => g.applyQuaternion(q).translate(ex + n.x * fwd, EY + n.y * fwd, ez + n.z * fwd);
    eye.push([place(new THREE.SphereGeometry(0.21, 18, 14).scale(1, 1.2, 0.42), 0), WH]);
    eye.push([place(new THREE.SphereGeometry(0.115, 16, 12).scale(1, 1.15, 0.5), 0.06), INK]);
    eye.push([place(new THREE.SphereGeometry(0.042, 10, 8).translate(-0.04, 0.05, 0), 0.115), WH]); }
  const eyesG = vcGeo(eye); eyesG.translate(0, -EY, 0); // (pivots on the eye line, so a blink closes them in place)
  // the band round the pod in the team's colour, and the tank on top: a clear drum between two steel rings, with the paint in it
  const bandG = new THREE.TorusGeometry(0.885, 0.06, 10, seg).rotateX(Math.PI / 2).translate(0, podC - 0.35, 0);
  const tankY = podC + podR - 0.08, tankGlassG = new THREE.CylinderGeometry(0.3, 0.3, 0.6, seg, 1, true).translate(0, tankY + 0.3, 0);
  const tankMetalG = vcGeo([[new THREE.CylinderGeometry(0.35, 0.35, 0.1, seg).translate(0, tankY + 0.62, 0), SVD], [new THREE.CylinderGeometry(0.36, 0.33, 0.12, seg).translate(0, tankY + 0.04, 0), SVD], [new THREE.CylinderGeometry(0.05, 0.05, 0.12, 8).translate(0, tankY + 0.72, 0), SVL]]);
  const tankInkG = new THREE.CylinderGeometry(0.26, 0.26, 0.5, seg).translate(0, 0.25, 0); // (its base at the bottom, so it can drain)
  const hullG = mergeGeos([new THREE.SphereGeometry(podR, 24, 16).translate(0, podC, 0), new THREE.CylinderGeometry(0.34, 0.34, 0.76, 20).translate(0, tankY + 0.36, 0)]);
  return { baseG, barrelG, podG, eyesG, eyeY: EY, bandG, tankGlassG, tankMetalG, tankInkG, tankInkY: tankY + 0.08, hullG, dir, tip: at(bl + 0.05) };''' + s[b:]
rep("const turMetalM = toon(0xFFFFFF, { vertexColors: true, transparent: true }, { metalness: 0.85, roughness: 0.28, envMapIntensity: 1.3 });",
    "const turMetalM = toon(0xFFFFFF, { vertexColors: true, transparent: true }, { metalness: 0.85, roughness: 0.28, envMapIntensity: 1.3 }), turFaceM = new THREE.MeshBasicMaterial({ vertexColors: true });")
a = s.index("function addTurret(V) {"); b = s.index("\n", a)
s = s[:a] + r'''function addTurret(V) { const R = TURRET_RIG, g = new THREE.Group(); g.visible = false; const a = new THREE.Mesh(R.baseG, turMetalM), bg = new THREE.Group(), b = new THREE.Mesh(R.barrelG, turMetalM), pod = new THREE.Mesh(R.podG, turMetalM), tm = new THREE.Mesh(R.tankMetalG, turMetalM), band = new THREE.Mesh(R.bandG, toon(0xE3122F)), ink = new THREE.Mesh(R.tankInkG, toon(0xE3122F, { transparent: true })), glass = new THREE.Mesh(R.tankGlassG, turDomeM), eyes = new THREE.Mesh(R.eyesG, turFaceM);
  for (const m of [a, b, pod, tm, band]) { m.castShadow = true; m.renderOrder = 31; } ink.renderOrder = 33; ink.position.y = R.tankInkY; glass.renderOrder = 44; eyes.renderOrder = 34; eyes.position.y = R.eyeY;
  if (!HI) { const o = new THREE.Mesh(R.hullG, outlineMat); o.scale.setScalar(1.05); o.renderOrder = 30.5; g.add(o); }
  bg.add(b); g.add(a, bg, pod, tm, band, ink, glass, eyes); g.userData.ink = ink; g.userData.band = band; g.userData.eyes = eyes; V.body.add(g); V.tur = g; V.turBarrel = bg; }''' + s[b:]
# the pick-up: the same machine, small, and the roller gets its face
rep("""  else if (type === 'turret') { const t = new THREE.Group(); t.position.y = -0.12; t.scale.setScalar(0.42); spin.add(t); for (const geo of [TURRET_RIG.baseG, TURRET_RIG.barrelG]) { const o = new THREE.Mesh(geo, turMetalM); o.castShadow = true; t.add(o); const h = new THREE.Mesh(geo, outlineMat); h.scale.setScalar(1.12); t.add(h); }
    const ink = new THREE.Mesh(new THREE.SphereGeometry(0.82, 22, 16), puIconMat); ink.position.y = -0.2; ink.scale.set(1, 0.82, 1); t.add(ink); const d = new THREE.Mesh(TURRET_RIG.domeG, turDomeM); d.renderOrder = 44; t.add(d); eyes = t; }""",
    """  else if (type === 'turret') { const R = TURRET_RIG, t = new THREE.Group(); t.position.y = -0.2; t.scale.setScalar(0.4); spin.add(t); for (const [geo, m] of [[R.baseG, turMetalM], [R.barrelG, turMetalM], [R.podG, turMetalM], [R.tankMetalG, turMetalM], [R.bandG, puIconMat]]) { const o = new THREE.Mesh(geo, m); o.castShadow = true; t.add(o); } for (const geo of [R.baseG, R.barrelG, R.hullG]) { const h = new THREE.Mesh(geo, outlineMat); h.scale.setScalar(1.08); t.add(h); }
    const ink = new THREE.Mesh(R.tankInkG, puIconMat); ink.position.y = R.tankInkY; t.add(ink); const gl = new THREE.Mesh(R.tankGlassG, turDomeM); gl.renderOrder = 44; t.add(gl); const ey = new THREE.Mesh(R.eyesG, turFaceM); ey.position.y = R.eyeY; ey.renderOrder = 34; t.add(ey); eyes = t; }""")
rep("for (const [geo, m] of [[K.roll, K.rollM], [K.solid, stGlossM], [K.wire, K.chromeM], [K.hull, outlineMat]]) { const o = new THREE.Mesh(geo, m); o.castShadow = m !== outlineMat; rl.add(o); } eyes = rl; }",
    "for (const [geo, m] of [[K.roll, K.rollM], [K.solid, stGlossM], [K.wire, K.chromeM], [K.hull, outlineMat]]) { const o = new THREE.Mesh(geo, m); o.castShadow = m !== outlineMat; rl.add(o); } const fe = new THREE.Mesh(K.eyes, K.faceM); fe.position.y = 0.035; fe.renderOrder = 34; rl.add(fe); const fm = new THREE.Mesh(K.mouth, K.faceM); fm.renderOrder = 34; rl.add(fm); eyes = rl; }")
# each frame: the paint in the tank, the band's colour, and the eyes blinking (and squinting with the kick of each shot)
rep("const ink = V.tur.userData.ink; if (ink) { const col = TEAMS[D.team].wet; if (V.turCol !== col) { V.turCol = col; ink.material.color.setHex(col); } const lv = D.turret ? clamp(D.turret.t / TURRET_T, 0, 1) : (V.turLv === undefined ? 1 : V.turLv); V.turLv = V.turLv === undefined ? lv : V.turLv + (lv - V.turLv) * Math.min(1, dt * 8); ink.scale.set(1 - 0.08 * (1 - V.turLv), Math.max(0.05, V.turLv), 1 - 0.08 * (1 - V.turLv)); } } }",
    "const ink = V.tur.userData.ink; if (ink) { const col = TEAMS[D.team].wet; if (V.turCol !== col) { V.turCol = col; ink.material.color.setHex(col); const bd = V.tur.userData.band; if (bd) bd.material.color.setHex(col); } const lv = D.turret ? clamp(D.turret.t / TURRET_T, 0, 1) : (V.turLv === undefined ? 1 : V.turLv); V.turLv = V.turLv === undefined ? lv : V.turLv + (lv - V.turLv) * Math.min(1, dt * 8); ink.scale.set(1, Math.max(0.03, V.turLv), 1); }\n      const ey = V.tur.userData.eyes; if (ey) { V.turBT = (V.turBT === undefined ? 1.5 : V.turBT) - dt; if (V.turBT <= 0) { V.turBK = 0.12; V.turBT = 1.8 + Math.random() * 3; } if (V.turBK > 0) V.turBK -= dt; ey.scale.set(1, Math.min(V.turBK > 0 ? 0.1 : 1, 1 - 0.4 * (D.turret ? D.turret.kick : 0)), 1); } } }")
assert 'TURRET_RIG.domeG' not in s and 'TURRET_RIG.inkG' not in s
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
