"""v473: a better Paint Bomb. The user: "Make the paint bomb effect better".

- The wind-up: as you swell, a glow of your paint wraps round you and blinks like a fuse, slow at first and faster and whiter right
  up to the blast, so everyone can read the timing.
- The blast: a beat of hit-stop, then a bright fireball of your paint that balloons out to most of the ring and fades, a column of
  paint shooting straight up, the rings racing out across the floor, and the screen flashing and kicking for whoever's close.
- The splash: big blobs of paint fly out in an arc and slap down round the edge of the ring a moment later (the splats used to just
  appear), so the paint visibly lands. What gets knocked out, and the paint left behind, is the same as before.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

FX = r"""
// (v473) the bomb's look: a blinking glow while it swells; a fireball, a column of paint and blobs that land round the ring when it goes
const BOMB_GLOW = new THREE.SphereGeometry(1, 22, 16), bombFx = [];
const bombGlowMat = col => new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
function bombFxTick(dt) {
  for (let i = bombFx.length - 1; i >= 0; i--) { const F = bombFx[i]; F.t += dt;
    if (F.kind === 'ball') { const u = F.t / 0.5; if (u >= 1) { scene.remove(F.m); F.m.material.dispose(); bombFx.splice(i, 1); continue; }
      const g = 1 - Math.pow(1 - Math.min(1, F.t / 0.22), 3); F.m.scale.setScalar(Math.max(0.01, BOMB_R * (0.25 + 0.55 * g))); F.m.material.opacity = 0.85 * (1 - u) * (1 - u); F.m.material.color.copy(F.c).lerp(COL_WHITE, Math.max(0, 0.8 - u * 2)); }
    else if (F.kind === 'blob') { if (F.t >= F.at) { if (F.g > -Infinity) addSplat(F.x, F.g, F.z, F.a, F.r, dryClock, false, true, F.code); for (let k = 0; k < 6; k++) { const a = Math.random() * 6.283, v = 1 + Math.random() * 2; spawnPart(F.x, F.g + 0.2, F.z, Math.cos(a) * v, 1 + Math.random() * 2, Math.sin(a) * v, 0.25 + Math.random() * 0.15, F.mat, 0.35); } bombFx.splice(i, 1); } } }
}
"""

def apply(s):
    s = rep(s, "function bombDrop(B) {", FX.strip() + "\nfunction bombDrop(B) {")
    # the glow, made with the bomb and dropped with it
    s = rep(s, "  const B = { by: D, t: 0, ring, fill, spark: 0, beep: 0, dodge: [] }; bombList.push(B); D.bombK = 1;",
               "  const glow = new THREE.Mesh(BOMB_GLOW, bombGlowMat(TEAMS[D.team].wet)); glow.renderOrder = 8; glow.visible = false; scene.add(glow); // (v473)\n"
               "  const B = { by: D, t: 0, ring, fill, glow, spark: 0, beep: 0, dodge: [] }; bombList.push(B); D.bombK = 1;")
    s = rep(s, "function bombDrop(B) { scene.remove(B.ring, B.fill); B.ring.material.dispose(); B.fill.material.dispose();",
               "function bombDrop(B) { scene.remove(B.ring, B.fill); B.ring.material.dispose(); B.fill.material.dispose(); if (B.glow) { scene.remove(B.glow); B.glow.material.dispose(); }")
    s = rep(s, "function clearBombs() { for (const B of bombList) bombDrop(B); bombList.length = 0; }",
               "function clearBombs() { for (const B of bombList) bombDrop(B); bombList.length = 0; for (const F of bombFx) if (F.m) { scene.remove(F.m); F.m.material.dispose(); } bombFx.length = 0; }")
    s = rep(s, "function bombTick(dt) {\n", "function bombTick(dt) {\n  bombFxTick(dt); // (v473)\n")
    # the glow blinks like a fuse, faster and whiter toward the end
    s = rep(s, "    D.bombK = 1 + (BOMB_K - 1) * e + throb; D.wob = Math.max(D.wob, 0.25);",
               "    D.bombK = 1 + (BOMB_K - 1) * e + throb; D.wob = Math.max(D.wob, 0.25);\n"
               "    { const G = B.glow, blink = Math.sin(B.ph * 6.2832 * 0.5) > 0 ? 1 : 0.35; G.visible = B.t > BOMB_FLASH * 0.5; G.position.set(D.x, D.y + PR * D.bombK, D.z); G.scale.setScalar(PR * D.bombK * (1.3 + 0.12 * blink));\n"
               "      G.material.color.set(TEAMS[D.team].wet).lerp(COL_WHITE, 0.15 + 0.7 * u * u * blink); G.material.opacity = (0.12 + 0.4 * u) * blink; } // (v473)")
    # the blast: hit-stop, a fireball, a column of paint, and blobs that land round the edge
    s = rep(s, "  const n = 12; for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + Math.random() * 0.3, r = BOMB_R * (0.7 + Math.random() * 0.25), px = x + Math.cos(a) * r, pz = z + Math.sin(a) * r, g = surfaceUnder(px, pz, gy + 1.5, true); if (g > -Infinity && Math.abs(g - gy) < 1.5) addSplat(px, g, pz, a, 1.1 + Math.random() * 0.6, dryClock, false, true, tcode(D)); }",
               "  const n = 12; for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + Math.random() * 0.3, r = BOMB_R * (0.7 + Math.random() * 0.25), px = x + Math.cos(a) * r, pz = z + Math.sin(a) * r, g = surfaceUnder(px, pz, gy + 1.5, true); if (g > -Infinity && Math.abs(g - gy) < 1.5) {\n"
               "    const at = 0.28 + Math.random() * 0.22, vy = 4.5 + Math.random() * 2; bombFx.push({ kind: 'blob', t: 0, at, x: px, z: pz, g, a, r: 1.1 + Math.random() * 0.6, code: tcode(D), mat: tmat(D) }); // (v473: flung out, it lands a moment later)\n"
               "    spawnPart(x, gy + 0.8, z, (px - x) / at, vy, (pz - z) / at, at + 0.05, tmat(D), 0.9 + Math.random() * 0.4); } }\n"
               "  { const ball = new THREE.Mesh(BOMB_GLOW, bombGlowMat(TEAMS[D.team].wet)); ball.renderOrder = 9; ball.position.set(x, gy + 0.6, z); scene.add(ball); bombFx.push({ kind: 'ball', t: 0, m: ball, c: new THREE.Color(TEAMS[D.team].wet) }); }\n"
               "  for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283, s = Math.random() * 1.6; spawnPart(x + Math.cos(a) * 0.3, gy + 0.4, z + Math.sin(a) * 0.3, Math.cos(a) * s, 9 + Math.random() * 7, Math.sin(a) * s, 0.7 + Math.random() * 0.4, i % 5 ? tmat(D) : puHaloMat, 0.45 + Math.random() * 0.5); } // (v473: a column of paint)\n"
               "  hitStop(0.07, D); if (dp0(D) < 14) { flashScreen(); fovKick = Math.max(fovKick, 8); }")
    return s
