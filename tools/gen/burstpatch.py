f='/home/claude/paint-the-canvas.html'; s=open(f).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (a[:90], s.count(a)); s=s.replace(a,b)

# ---- button: in a coffin the arrow flips up ----
rep(".slamBtn svg{width:40px;height:40px;fill:var(--white);stroke:var(--outline);stroke-width:2;stroke-linejoin:round}",
    ".slamBtn svg{width:40px;height:40px;fill:var(--white);stroke:var(--outline);stroke-width:2;stroke-linejoin:round}\n.slamBtn svg path:first-child{transition:transform .22s cubic-bezier(.3,1.7,.5,1);transform-box:view-box;transform-origin:20px 16.75px}\n.slamBtn.up svg path:first-child{transform:rotate(180deg)}")
rep("""  if (ready !== wasReady) { b.classList.toggle('off', !ready);""", """  const up = P.st === 'hide';
  if (b._up !== up) { b._up = up; b.classList.toggle('up', up); wasReady = null; }
  if (ready !== wasReady) { b.classList.toggle('off', !ready);""")
rep("b.setAttribute('aria-label', ready ? 'Ground pound' :", "b.setAttribute('aria-label', ready ? (up ? 'Burst out of the coffin' : 'Ground pound') :")

# ---- pounding from inside a coffin bursts out of it ----
rep("  if (D.st === 'hide') exitPot(D);\n  if (D.air) { D.slam = true;", "  if (D.st === 'hide') { burstCoffin(D); return true; }\n  if (D.air) { D.slam = true;")
rep("function startSlam(D) {", """// the coffin burst: blood blasts up out of the coffin, the coffin flies apart, and you rocket up out of it.
// It splats the same circle as a pound, splashes boiling water in it, and knocks out anyone inside that circle.
function burstCoffin(D) {
  const p = D.pot; if (!p) return;
  p.occ = null; D.pot = null; D.st = 'play'; D.stroke++;
  if (D.spawnImm) { D.spawnImm = false; D.immuneT = 1.5; }
  D.air = true; D.y = p.y + 0.35; D.vy = 13.5; D.spd = cfg.speed * 0.55; D.slam = false; D.squash = 0; D.buf = 0; D.freeLand = true; D.turn = 0;
  const hitP = rivals.filter(r => r.on && Math.abs(r.y - p.y) < 0.3 && Math.hypot(r.x - p.x, r.z - p.z) < SLAM_R * 0.5 + r.rad);
  if (hitP.length) { hitP.forEach(splashPuddle); D.inkRush = true; if (hearable(D)) AU.sprinkle(D === P ? 1 : 0.6); }
  addSplat(p.x, p.y, p.z, D.yaw, SLAM_R, dryClock, false, true, D.team);
  shockwave(p.x, p.y, p.z, SLAM_R, D === P ? 0xFFFFFF : 0xBFE3FF); shockwave(p.x, p.y, p.z, SLAM_R * 0.6, TEAMS[D.team].wet);
  breakCoffin(p, D);
  const O = other(D);
  if (O.ai) aiNotePound(O, D);
  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R && Math.abs(O.y - p.y) < 1.4) knockOut(O, O.st === 'hide' ? 'coffin' : 'pound', D);
  const dp = Math.hypot(p.x - P.x, p.z - P.z);
  if (D === P) { shake = 0.6; hold = 0.06; fovKick = 12; AU.burst(1); buzz([20, 20, 45]); flashScreen(); }
  else if (dp < 20) { shake = Math.max(shake, 0.45 * (1 - dp / 20)); AU.burst(0.6); }
}
// the coffin itself: planks and the lid fly off, a column of blood shoots up, and it's gone (a fresh one rises somewhere else later)
const debris = [], geysers = [], plankG = new THREE.BoxGeometry(0.16, 0.07, 0.62), plankHullG = new THREE.BoxGeometry(0.22, 0.13, 0.68), geyserG = new THREE.CylinderGeometry(0.55, 0.85, 1, 18, 1, true).translate(0, 0.5, 0);
function breakCoffin(p, D) {
  p.st = 'down'; p.t = 0; p.g.visible = false; p.ring.visible = false; p.ink = 0; p.next = pickCoffinSpot(p);
  for (let i = 0; i < 12; i++) {
    const a = i / 12 * 6.283 + Math.random() * 0.4, sp = 3 + Math.random() * 4, m = new THREE.Mesh(plankG, i % 3 ? coffinWood : coffinRim);
    const hull = new THREE.Mesh(plankHullG, outlineMat); m.add(hull); m.castShadow = true;
    m.position.set(p.x + Math.cos(a) * 0.4, p.y + 0.3 + Math.random() * 0.3, p.z + Math.sin(a) * 0.4); m.rotation.set(Math.random() * 6, Math.random() * 6, Math.random() * 6); scene.add(m);
    debris.push({ m, v: new THREE.Vector3(Math.cos(a) * sp, 5 + Math.random() * 5, Math.sin(a) * sp), w: new THREE.Vector3((Math.random() - 0.5) * 16, (Math.random() - 0.5) * 16, (Math.random() - 0.5) * 16), life: 1.6 + Math.random() * 0.5 });
  }
  // the lid goes highest, spinning
  const lid = new THREE.Group(); lid.add(new THREE.Mesh(cofLidG, coffinWood)); lid.add(new THREE.Mesh(cofLidHullG, outlineMat)); lid.add(new THREE.Mesh(cofPanelG, coffinRim));
  lid.position.set(p.x, p.y + 0.5, p.z); scene.add(lid);
  const la = Math.random() * 6.283; debris.push({ m: lid, v: new THREE.Vector3(Math.cos(la) * 2.2, 11, Math.sin(la) * 2.2), w: new THREE.Vector3(9, 4, 7), life: 2.2 });
  // the blood blaze: a column that shoots up and fades, and a fountain of drops raining back down
  const gm = new THREE.Mesh(geyserG, new THREE.MeshBasicMaterial({ color: TEAMS[D.team].wet, transparent: true, opacity: 0.9, depthWrite: false, side: THREE.DoubleSide, fog: false }));
  gm.position.set(p.x, p.y + 0.05, p.z); gm.scale.set(0.6, 0.01, 0.6); scene.add(gm); geysers.push({ m: gm, t: 0 });
  for (let i = 0; i < 46; i++) { const a = Math.random() * 6.283, r = Math.random(), sp = 0.6 + r * 2.6; spawnPart(p.x + Math.cos(a) * 0.3, p.y + 0.4, p.z + Math.sin(a) * 0.3, Math.cos(a) * sp, 9 + Math.random() * 9, Math.sin(a) * sp, 1.2 + Math.random() * 0.6, tmat(D), 0.8 + Math.random() * 0.9); }
  for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283; spawnPart(p.x, p.y + 0.3, p.z, Math.cos(a) * 3, 3 + Math.random() * 3, Math.sin(a) * 3, 0.7, dustMat, 0.9 + Math.random() * 0.6, 0.5); }
}
function updateDebris(dt) {
  for (let i = debris.length - 1; i >= 0; i--) {
    const d = debris[i]; d.life -= dt; d.v.y -= 15 * dt; d.m.position.addScaledVector(d.v, dt);
    const g = surfaceUnder(d.m.position.x, d.m.position.z, d.m.position.y + 0.3);
    if (g > -Infinity && d.m.position.y < g + 0.05 && d.v.y < 0) { d.m.position.y = g + 0.05; d.v.y *= -0.3; d.v.x *= 0.5; d.v.z *= 0.5; d.w.multiplyScalar(0.5); }
    d.m.rotation.x += d.w.x * dt; d.m.rotation.y += d.w.y * dt; d.m.rotation.z += d.w.z * dt;
    if (d.life < 0.35) d.m.scale.setScalar(Math.max(0.01, d.life / 0.35));
    if (d.life <= 0 || d.m.position.y < -20) { scene.remove(d.m); debris.splice(i, 1); }
  }
  for (let i = geysers.length - 1; i >= 0; i--) {
    const q = geysers[i]; q.t += dt; const up = Math.min(1, q.t / 0.16), fade = Math.max(0, 1 - Math.max(0, q.t - 0.16) / 0.55);
    q.m.scale.set(0.6 + 0.5 * up, 0.01 + 7.5 * up, 0.6 + 0.5 * up); q.m.position.y += 0; q.m.material.opacity = 0.9 * fade;
    if (fade <= 0) { scene.remove(q.m); q.m.material.dispose(); geysers.splice(i, 1); }
  }
}
function startSlam(D) {""")
rep("  updateParts(dt); updateFx(dt); updateConfetti(dt); updateSprinkle(dt);\n}", "  updateParts(dt); updateFx(dt); updateConfetti(dt); updateSprinkle(dt); updateDebris(dt);\n}")
rep("sprDrops.length = 0; sprJets.length = 0;", "sprDrops.length = 0; sprJets.length = 0; debris.forEach(d => scene.remove(d.m)); debris.length = 0; geysers.forEach(q => scene.remove(q.m)); geysers.length = 0;")
rep("...pots.map(p => p.tele), ...powers", "...pots.map(p => p.tele), ...debris.map(d => d.m), ...geysers.map(q => q.m), ...powers")
# sound
rep("    spot() {", "    burst(v) { v = v || 1; noise(0.55, 0.5 * v, 'bandpass', 380, 3200, 1.1); noise(0.3, 0.4 * v, 'highpass', 2600, 0, 0.9, 0.02); for (let i = 0; i < 7; i++) noise(0.05, 0.22 * v, 'bandpass', 1400 + Math.random() * 2200, 700, 1.2, Math.random() * 0.18); tone('sine', 85, 420, 0.42, 0.3 * v); tone('triangle', 300, 950, 0.26, 0.1 * v, 0.05); },\n    spot() {")
# tip, once
rep("    if (runT > 16 && slamReady(P) && H.st === 'play'", "    if (P.st === 'hide' && slamReady(P)) hint('burst', 'Pound in a coffin to burst out of it', 3);\n    if (runT > 16 && slamReady(P) && H.st === 'play'")
# how to play
rep("Duck behind something tall to shake it.", "Duck behind something tall to shake it.")
rep("A drained one sinks into the ground and a fresh one rises somewhere else.", "A drained one sinks into the ground and a fresh one rises somewhere else. In a coffin the pound button flips to an up arrow: burst out, smash the coffin and splat the same big circle.")

# ---- the CPU bursts too: to blow you out of range when you come for its coffin, or as a big exit ----
rep("  if (threat && ai.flee) { if (!ai.exitPlan || !ai.exitPlan.flee)", """  // you're standing in the circle: burst out and take you with it
  if (AI.model > 0 && slamReady(D) && wxPhase !== 'sun' && wxPhase !== 'warn' && o && o.st === 'play' && runT - o.t < 0.5 && o.imm <= 0.3 && od < KO_R - 0.6 && Math.abs(o.y - D.y) < 1.2 && Math.random() < Math.min(1, dt * AI.pound)) { ai.exitPlan = null; ai.thinkT = 0; useSlam(D); return; }
  if (threat && ai.flee) { if (!ai.exitPlan || !ai.exitPlan.flee)""")
rep("  if (Math.abs(err) < (ep.flee ? 1.3 : 0.35) || ep.t > (ep.flee ? 0.3 : 1.2)) { ai.exitPlan = null; ai.campT = 0; ai.thinkT = ep.flee ? 0 : 0.15; ai.fleeRolled = false; jump(D); }",
    "  if (Math.abs(err) < (ep.flee ? 1.3 : 0.35) || ep.t > (ep.flee ? 0.3 : 1.2)) {\n    ai.exitPlan = null; ai.campT = 0; ai.thinkT = ep.flee ? 0 : 0.15; ai.fleeRolled = false;\n    // a big way out: burst if there's a lot of fresh canvas around the coffin\n    if (AI.plan > 0 && slamReady(D) && !sunny && D.paint - SLAM_COST > 0.45 && localGain(D, 4.2) > AI.covPound * 0.75) useSlam(D); else jump(D);\n  }")
open(f,'w').write(s)
print('patched')
