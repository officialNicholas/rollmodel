import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# ---- the quake and the crown of paint ----
rep("function orbReset() {", r"""// the giant slam: the whole stage jolts, and a crown of paint curls up and out of the crater
const quake = { t: 9, amp: 0 };
function startQuake(amp) { if (amp > quake.amp * Math.exp(-quake.t * 3.2)) { quake.amp = amp; quake.t = 0; } }
const crowns = [];
function crownGeo(R0, R1, H, seed) {
  const N = 60, ROWS = 8, r = rng(seed), hk = [];
  for (let k = 0; k < N; k++) hk.push(r());
  for (let pass = 0; pass < 2; pass++) for (let k = 0; k < N; k++) hk[k] = (hk[k] * 2 + hk[(k + 1) % N] + hk[(k + N - 1) % N]) / 4;
  const spike = k => 0.75 + 0.5 * hk[k] + (k % 5 === 0 ? 0.35 * r() : 0);
  const sp = []; for (let k = 0; k < N; k++) sp.push(spike(k));
  const pos = [], idx = [];
  for (let j = 0; j <= ROWS; j++) {
    const v = j / ROWS;
    for (let k = 0; k <= N; k++) {
      const kk = k % N, a = kk / N * 6.2832, top = sp[kk];
      // the wall flares outward as it rises and the rim breaks into points
      const rad = R0 + (R1 - R0) * Math.pow(v, 1.7) * (0.9 + 0.2 * top), y = H * v * (1 + (top - 1) * v * v);
      pos.push(Math.cos(a) * rad, y, Math.sin(a) * rad);
    }
  }
  for (let j = 0; j < ROWS; j++) for (let k = 0; k < N; k++) { const a = j * (N + 1) + k, b = a + N + 1; idx.push(a, b, a + 1, a + 1, b, b + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
function spawnCrown(D, R) {
  const g = new THREE.Group(), geo = crownGeo(R * 0.5, R * 0.95, Math.min(3.4, R * 0.5), (Math.random() * 1e5) | 0);
  const m = new THREE.Mesh(geo, toon(TEAMS[D.team].wet, { side: THREE.DoubleSide, emissive: new THREE.Color(TEAMS[D.team].wet).multiplyScalar(0.18) }));
  const hull = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hull.scale.set(1.03, 1.01, 1.03);
  g.add(m); g.add(hull); g.position.set(D.x, D.y + 0.02, D.z); g.scale.set(0.7, 0.01, 0.7); scene.add(g);
  crowns.push({ g, t: 0, geo, mats: [m.material, hull.material] });
  // thick drops thrown off the rim, arcing up and out
  for (let i = 0; i < 54; i++) { const a = Math.random() * 6.283, rr = R * (0.55 + Math.random() * 0.4), spd = 3 + Math.random() * 6; spawnPart(D.x + Math.cos(a) * rr, D.y + 0.8 + Math.random() * 2, D.z + Math.sin(a) * rr, Math.cos(a) * spd, 5 + Math.random() * 7, Math.sin(a) * spd, 1 + Math.random() * 0.6, tmat(D), 0.8 + Math.random() * 1.1); }
}
function updateCrowns(dt) {
  for (let i = crowns.length - 1; i >= 0; i--) {
    const c = crowns[i]; c.t += dt; const t = c.t;
    const up = 1 - Math.pow(1 - Math.min(1, t / 0.17), 3), fall = t > 0.42 ? Math.min(1, (t - 0.42) / 0.7) : 0;
    const sy = up * (1 - fall * fall), sr = 0.72 + 0.32 * up + 0.3 * fall;
    c.g.scale.set(sr, Math.max(0.01, sy), sr);
    if (t > 1.15) { scene.remove(c.g); c.geo.dispose(); c.mats.forEach(m => m.dispose()); crowns.splice(i, 1); }
  }
}
function orbReset() {""")
rep("    shrink() { tone('triangle', 660, 220, 0.4, 0.12); },", "    shrink() { tone('triangle', 660, 220, 0.4, 0.12); },\n    quake() { noise(1.5, 0.5, 'lowpass', 160, 30); tone('sine', 72, 26, 1.2, 0.38); tone('sine', 110, 40, 0.5, 0.2, 0.05); },")
rep("  updateParts(dt); updateFx(dt); updateConfetti(dt); updateSprinkle(dt); updateDebris(dt);", "  updateParts(dt); updateFx(dt); updateConfetti(dt); updateSprinkle(dt); updateDebris(dt); updateCrowns(dt);")

# the giant slam itself
rep("  if (giant) { D.giantT = 0; D.wob = 1; shockwave(D.x, D.y, D.z, R * 1.15, 0xFFFFFF);",
    """  if (giant) {
    spawnCrown(D, R); startQuake(0.95 * Math.max(0.35, 1 - dp0(D) / 45)); if (hearable(D) || D === P) AU.quake();
    for (const p of pots) p.bounce = 1;
    shockwave(D.x, D.y, D.z, R * 2.6, 0xFFFFFF); shockwave(D.x, D.y, D.z, R * 1.9, TEAMS[D.team].wet);
    // the ground heaves: anyone standing nearby gets bounced off their feet
    const B = other(D), bd = Math.hypot(B.x - D.x, B.z - D.z);
    if (B.st === 'play' && !B.air && B.immuneT <= 0 && B.giantT <= 0 && Math.abs(B.y - D.y) < 3 && bd < 16) { if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); popText('Quake!'); } B.air = true; B.stroke++; B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; }
  }
  if (giant) { D.giantT = 0; D.wob = 1; shockwave(D.x, D.y, D.z, R * 1.15, 0xFFFFFF);""")
rep("function hitStop(t, A, B, x, z) {", "const dp0 = D => Math.hypot(D.x - P.x, D.z - P.z);\nfunction hitStop(t, A, B, x, z) {")
# the stage jolts: the camera bounces against a still sky, heavy and slow, for about a second
rep("  shake *= Math.exp(-rdt * 9); fovKick *= Math.exp(-rdt * 4);",
    """  if (quake.amp > 0) { quake.t += rdt; const q = quake.amp * Math.exp(-quake.t * 3.2); if (!reduceMotion) { camera.position.y += Math.sin(quake.t * 24) * q * 0.85; camera.position.x += Math.sin(quake.t * 17 + 1.3) * q * 0.4; camera.position.z += Math.cos(quake.t * 21) * q * 0.4; camera.rotateZ(Math.sin(quake.t * 13) * q * 0.035); } if (quake.t > 1.8) quake.amp = 0; }
  shake *= Math.exp(-rdt * 9); fovKick *= Math.exp(-rdt * 4);""")
open(F, 'w').write(s)
print('ok')
