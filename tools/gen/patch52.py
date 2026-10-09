import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:140])); sys.exit(1)
    s = s.replace(a, b)

# ---------- roll: the whole half-second roll is the untouchable window, and it works on an empty tank ----------
rep("const ROLL_T = 0.32, ROLL_CD = 1.3, ROLL_COST = 0.04;", "const ROLL_T = 0.5, ROLL_DASH = 0.32, ROLL_CD = 1.5, ROLL_COST = 0.04; // untouchable for half a second; the tumble and its burst of speed are the first third of a second of that")
rep("  if (D.dry) { if (D === P) { kick($('ttrack'), 'nope'); AU.nope(); popText('No blood'); } return false; }\n  if (D.charging) clearCharge(D);\n  const base = cfg.speed * speedMul * (D.cpu ? AI.speed : 1);",
    "  if (D.charging) clearCharge(D);\n  const base = cfg.speed * speedMul * (D.cpu ? AI.speed : 1) * (D.dry ? 0.7 : 1); // out of blood you can still roll, just not as far")
rep("D.rollV = Math.max(D.spd, base) + base * 1.15;", "D.rollV = (Math.max(D.spd, base) + base * 1.15) * 1.08;")
rep("  if (D.giantT <= 0) D.paint = Math.max(0.001, D.paint - ROLL_COST);", "  if (D.giantT <= 0 && !D.dry) D.paint = Math.max(0.001, D.paint - ROLL_COST);")
rep("D.charging ? 0.75 : D.rollT > 0 ? 0.4 : 1);", "D.charging ? 0.75 : D.rollT > ROLL_T - ROLL_DASH ? 0.4 : 1);")
rep("  else if (!D.air && D.rollT > 0) D.spd = D.rollV * (0.62 + 0.38 * D.rollT / ROLL_T);", "  else if (!D.air && D.rollT > ROLL_T - ROLL_DASH) D.spd = D.rollV * (0.62 + 0.38 * (D.rollT - ROLL_T + ROLL_DASH) / ROLL_DASH);")
rep("U.gSpd.value = D.rollT > 0 ? 0.2 : L.spd;", "U.gSpd.value = D.rollT > ROLL_T - ROLL_DASH ? 0.2 : L.spd;")
rep("(D.rollT > 0 ? 6.2832 * (1 - Math.pow(D.rollT / ROLL_T, 2)) : 0)", "(D.rollT > ROLL_T - ROLL_DASH ? 6.2832 * (1 - Math.pow((D.rollT - ROLL_T + ROLL_DASH) / ROLL_DASH, 2)) : 0)")
rep("if (away && D.rollCD <= 0 && !D.dry && rollSafe(D)) { if (eta > 0.28) return false;", "if (away && D.rollCD <= 0 && rollSafe(D)) { if (eta > 0.44) return false;")
rep("hint('roll', say('Swipe up to roll clear', 'Shift to roll clear'), 2.4);", "hint('roll', say('Swipe up just before it lands', 'Shift just before it lands'), 2.4);")
rep("Jump or roll to dodge one coming at you.</span>", "Jump it, or time a roll: rolling makes you untouchable for half a second.</span>")
# you can see the untouchable window: a bright shimmer and a sparkle trail for exactly as long as it lasts
rep("  if (D.rollBuf > 0) { D.rollBuf -= dt;", "  if (D.rollT > 0 && D.st === 'play' && Math.random() < dt * 45) spawnPart(D.x + (Math.random() - 0.5) * 0.4, D.y + 0.2 + Math.random() * 0.4, D.z + (Math.random() - 0.5) * 0.4, (Math.random() - 0.5) * 0.6, 0.6 + Math.random() * 0.8, (Math.random() - 0.5) * 0.6, 0.35, puHaloMat, 0.35, 0.2);\n  if (D.rollBuf > 0) { D.rollBuf -= dt;")
rep("    if (P.dry && P.st === 'play') tmpCol.lerp(COL_DULL, 0.74);", "    if (P.dry && P.st === 'play') tmpCol.lerp(COL_DULL, 0.74);\n    if (P.rollT > 0 && P.st === 'play') tmpCol.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));")
rep("    if (H.dry && H.st === 'play') tmpCol2.lerp(COL_DULL, 0.74);", "    if (H.dry && H.st === 'play') tmpCol2.lerp(COL_DULL, 0.74);\n    if (H.rollT > 0 && H.st === 'play') tmpCol2.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));")
# a dodge that came from a well-timed roll lands with a little punch
rep("  if (O === P) { popText('Dodged!'); buzz(12); AU.ready(); } else if (D === P) popText('It dodged!');",
    "  if (O.rollT > 0) { shockwave(O.x, O.y, O.z, 1.4, 0xFFFFFF); hitStop(0.06, O, D); }\n  if (O === P) { popText('Dodged!'); buzz(12); AU.ready(); } else if (D === P) popText('It dodged!');")

# ---------- giant: rainbow like the orb, and a fast strobe as it runs out ----------
rep("function placeFace(dt) {", """// giant: the blob cycles through the orb's rainbow; in its last second and a bit it strobes, faster and faster, so you see it running out
function giantTint(D, c) {
  if (D.giantT <= 0) return;
  if (D.giantT < 1.2) { const f = 6 + (1.2 - D.giantT) * 8; if (Math.sin(clock * 6.2832 * f) > 0) c.setHSL((clock * 2.5) % 1, 0.95, 0.6); }
  else c.setHSL((clock * 0.55) % 1, 0.9, 0.6);
}
function placeFace(dt) {""")
rep("    tmpCol.copy(teamCol);\n", "    tmpCol.copy(teamCol); giantTint(P, tmpCol);\n")
rep("    tmpCol2.copy(COL_HOLY);", "    tmpCol2.copy(COL_HOLY); giantTint(H, tmpCol2);")

# ---------- the missile: a real rocket ----------
rep("const MISSILE_DIVE = 0.58, MISSILE_SPD = 2.0; // drop per unit forward (about 30 degrees), and it flies at twice your rolling speed",
    "const MISSILE_DIVE = 0.3, MISSILE_SPD = 2.6, MISSILE_VMIN = 3; // a shallow dive (about 17 degrees) at more than twice your rolling speed")
rep("const sx = Math.sin(yaw), sz = Math.cos(yaw), v = Math.max(5, h * k);", "const sx = Math.sin(yaw), sz = Math.cos(yaw), v = Math.max(MISSILE_VMIN, h * k);")
rep("if (D.missile && D.slam) { if (D.missileHang > 0) { D.missileHang -= dt; D.vy = 0; } else D.vy = -Math.max(5, D.spd * (D.diveK || MISSILE_DIVE)); D.y += D.vy * dt; missileSeek(D, dt); }",
    "if (D.missile && D.slam) { if (D.missileHang > 0) { D.missileHang -= dt; D.vy = 0; } else { if (blockedAt(D.x + Math.sin(D.yaw) * 0.4, D.z + Math.cos(D.yaw) * 0.4, D.y)) D.diveK = 6; D.vy = -Math.min(26, Math.max(MISSILE_VMIN, D.spd * (D.diveK || MISSILE_DIVE))); } D.y += D.vy * dt; missileSeek(D, dt); } // hits a wall: it comes straight down there")
rep("D.missile = true; D.missileHang = 0.08; D.slamT = 0; D.slamEta = 0.5;", "D.missile = true; D.missileHang = 0.1; D.slamT = 0; D.slamEta = 0.5;")
rep("if (!D.ai) missileAssist(D); if (hearable(D)) { AU.whoosh(); AU.fling(1); }", "if (!D.ai) missileAssist(D); missileLaunch(D);")
rep("k = clamp(ht / reach, 0.4, 1.3);", "k = clamp(ht / reach, 0.2, 1.3);")
rep("function missileAssist(D) {", """// ignition: smoke and sparks out the back, a rocket roar, and it never fires itself off the canvas
function missileLaunch(D) {
  if (!missileHit(D)) for (const k of [0.45, 0.65, 0.9, 1.3, 2]) { D.diveK = Math.max(D.diveK, k); if (missileHit(D)) break; }
  const mh = missileHit(D); D.slamEta = D.missileHang + (mh ? Math.max(0.12, (D.y - mh.y) / Math.max(MISSILE_VMIN, D.spd * D.diveK)) : 0.5);
  const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);
  for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283, sp = 0.6 + Math.random(); spawnPart(D.x - fx * 0.4, D.y + 0.3, D.z - fz * 0.4, -fx * 2.6 + Math.cos(a) * sp, 0.3 + Math.random() * 0.8, -fz * 2.6 + Math.sin(a) * sp, 0.5 + Math.random() * 0.3, i % 3 ? smokeMat : emberMat, 1 + Math.random() * 0.6, -0.05); }
  if (hearable(D)) { AU.rocket(); AU.fling(0.8); }
}
function missileAssist(D) {""")
# exhaust: a flame at the tail as well as the smoke
rep("if (D.missile && D.slam && D.missileHang <= 0 && Math.random() < dt * 40) {",
    "if (D.missile && D.slam && D.missileHang <= 0) { const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw); for (let q = 0; q < 2; q++) if (Math.random() < dt * 40) spawnPart(D.x - fx * 0.6, D.y + 0.32, D.z - fz * 0.6, -fx * 3 + (Math.random() - 0.5), (Math.random() - 0.5) * 0.6, -fz * 3 + (Math.random() - 0.5), 0.16 + Math.random() * 0.1, emberMat, 0.7 + Math.random() * 0.5, 0); }\n    if (D.missile && D.slam && D.missileHang <= 0 && Math.random() < dt * 40) {")
# the body flies nose first, stretched into a bullet, pitched along its path
rep("U.gDrop.value = L.drop;", "U.gDrop.value = D.missile && D.slam ? 0 : L.drop;")
rep("V.root.rotation.set(-0.85 * V.misK + ", "V.root.rotation.set(V.misK * (D.missile && D.slam ? clamp(Math.atan2(-D.vy, Math.max(1, D.spd)), 0, 1.2) : 0.25) + ")
rep("  V.body.scale.set(rad * (1 + 0.65 * fk), rad * (1 - 0.7 * fk), rad * (1 + 0.65 * fk));",
    "  const mk = V.misK || 0; V.body.scale.set(rad * (1 + 0.65 * fk) * (1 - 0.2 * mk), rad * (1 - 0.7 * fk) * (1 - 0.2 * mk), rad * (1 + 0.65 * fk) * (1 + 0.85 * mk));")
# impact: an explosion with momentum, not a pound
rep("  D.slam = false; D.missile = false; D.flingC = 0; D.squash = 1; D.spd = 0;", "  D.slam = false; D.missile = false; D.flingC = 0; D.squash = 1; D.spd = missile ? cfg.speed * 0.85 : 0; // a missile skids on out of its blast")
rep("  if (missile) { shockwave(D.x, D.y, D.z, R * 0.82, TEAMS[D.team].wet); burst(D, TEAMS[D.team].wet, 30); }",
    "  if (missile) { missileBoom(D, R); burst(D, TEAMS[D.team].wet, 30); const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), ax = D.x + fx * 2.4, az = D.z + fz * 2.4; if (Math.abs(surfaceUnder(ax, az, D.y + 0.3) - D.y) < 0.05) addSplat(ax, D.y, az, D.yaw, R * 0.5, dryClock, false, true, tcode(D)); }")
rep("function updateFx(dt) {", """// the missile's fireball: a hot flash that swells and cools, a ring of smoke rolling out, sparks thrown up
const boomM = new THREE.MeshBasicMaterial({ color: 0xFFF1B8, transparent: true, opacity: 0, depthWrite: false, fog: false }), boom = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), boomM), boomC = new THREE.Color();
boom.visible = false; boom.renderOrder = 9; scene.add(boom); let boomT = 1;
function missileBoom(D, R) {
  boom.position.set(D.x, D.y + 0.4, D.z); boomT = 0; boom.visible = true;
  for (let i = 0; i < 22; i++) { const a = i / 22 * 6.283 + Math.random() * 0.2, sp = 4 + Math.random() * 3; spawnPart(D.x + Math.cos(a) * 0.6, D.y + 0.25, D.z + Math.sin(a) * 0.6, Math.cos(a) * sp, 0.6 + Math.random() * 1.2, Math.sin(a) * sp, 0.6 + Math.random() * 0.4, smokeMat, 1.3 + Math.random() * 0.8, -0.02); }
  for (let i = 0; i < 16; i++) { const a = Math.random() * 6.283, sp = 2 + Math.random() * 5; spawnPart(D.x, D.y + 0.4, D.z, Math.cos(a) * sp, 3 + Math.random() * 5, Math.sin(a) * sp, 0.5 + Math.random() * 0.4, emberMat, 0.6 + Math.random() * 0.5); }
  shockwave(D.x, D.y, D.z, R * 0.82, TEAMS[D.team].wet); shockwave(D.x, D.y, D.z, R * 1.25, 0xFFD27A);
}
function updateBoom(dt) { if (boomT >= 1) return; boomT = Math.min(1, boomT + dt / 0.38); const e = 1 - Math.pow(1 - boomT, 3); boom.scale.setScalar(0.5 + 2.6 * e); boomM.opacity = 0.9 * Math.pow(1 - boomT, 1.4); boomM.color.setHex(0xFFF1B8).lerp(boomC.setHex(0xFF7A2E), Math.min(1, boomT * 1.6)); if (boomT >= 1) boom.visible = false; }
function updateFx(dt) {""")
rep("updateParts(dt); updateFx(dt);", "updateParts(dt); updateFx(dt); updateBoom(dt);")
rep("...fxRings.map(f => f.m), ...suck.map(q => q.s)];", "...fxRings.map(f => f.m), ...suck.map(q => q.s), boom];")
rep("flip: 2, flipBack: 2, dash: 2.4 };", "flip: 2, flipBack: 2, dash: 2.4, rocket: 2.6 };")
rep("    dash() {", "    rocket() { hiss({ k: 'p', type: 'lowpass', f: 900, f1: 380, dur: 0.5, v: 0.22 }); hiss({ k: 'w', type: 'bandpass', f: 600, f1: 4200, glide: 0.35, q: 1.4, dur: 0.45, v: 0.14 }); tone({ type: 'sawtooth', f: 90, f1: 230, glide: 0.4, dur: 0.45, v: 0.06, lp: [500, 1800, 1] }); },\n    dash() {")
# rolling lays a thinner line: less paint, more ground covered
rep("D.giantT > 0 ? GIANT_K : D.power && D.power.type === 'roller' ? 2.6 : 1, tcode(D), D.rb)", "(D.giantT > 0 ? GIANT_K : D.power && D.power.type === 'roller' ? 2.6 : 1) * (D.rollT > ROLL_T - ROLL_DASH ? 0.45 : 1), tcode(D), D.rb)")
# a giant, or a blob with the Roller, that rolls into the other one knocks it out
rep("if (d < PR * GIANT_K + PR + 0.1 && Math.abs(dy) < 1.6 && B.flatT <= 0 && B.immuneT <= 0 && !(B.rollT > 0)) flatten(B, A, 'giant'); return; }",
    "if (d < PR * GIANT_K + PR + 0.1 && Math.abs(dy) < 1.6 && B.immuneT <= 0 && !(B.rollT > 0)) { if (A.rollT > 0) knockOut(B, 'crush', A); else if (B.flatT <= 0) flatten(B, A, 'giant'); } return; }")
rep("  if (d > PR * 2 + 0.15 || Math.abs(dy) > 1.0) return;\n", "  if (d > PR * 2 + 0.15 || Math.abs(dy) > 1.0) return;\n  for (const [A, B] of [[P, H], [H, P]]) if (A.rollT > 0 && (A.giantT > 0 || (A.power && A.power.type === 'roller')) && B.immuneT <= 0 && !(B.rollT > 0)) return knockOut(B, 'crush', A);\n")
rep("const KO_MSG = { pound: 'Pounded!', coffin: 'Staked!', fall: 'Fell off', sun: 'Sunburnt' };", "const KO_MSG = { pound: 'Pounded!', coffin: 'Staked!', fall: 'Fell off', sun: 'Sunburnt', crush: 'Crushed!' };")
rep("const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Staked it!', fall: 'It fell off', sun: 'Evaporated!' };", "const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Staked it!', fall: 'It fell off', sun: 'Evaporated!', crush: 'Crushed it!' };")
rep("AU.die(reason === 'coffin' ? 'pound' : reason)", "AU.die(reason === 'coffin' || reason === 'crush' ? 'pound' : reason)")
rep("<span>Grab the glowing orb to go giant for 5 seconds.</span>", "<span>Grab the glowing orb to go giant for 5 seconds. Roll into the holy water while you're giant and it's out.</span>")
# the holy water knows the trick too: giant or holding the Roller, with you right in front, it rolls at you (more often the smarter it is)
rep("function aiEvade(D, dt) {\n  const ai = D.ai, O = other(D), o = ai.o;", """function aiEvade(D, dt) {
  const ai = D.ai, O = other(D), o = ai.o;
  if ((D.giantT > 0.4 || (D.power && D.power.type === 'roller')) && D.rollCD <= 0 && !D.air && O.st === 'play' && O.immuneT <= 0 && !(O.rollT > 0) && Math.abs(O.y - D.y) < 0.8) {
    const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz), err = Math.abs(wrapA(Math.atan2(dx, dz) - D.yaw));
    if (d < (D.giantT > 0 ? 3.6 : 2.6) && err < 0.4 && rollSafe(D) && Math.random() < dt * 4 * AI.ram) { if (D.charging) cancelCharge(D); if (dodgeRoll(D)) return true; }
  }""")
open(F, 'w').write(s)
print('ok')
