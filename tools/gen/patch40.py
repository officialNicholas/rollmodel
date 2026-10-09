import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:120])); sys.exit(1)
    s = s.replace(a, b)

# ================= tuning =================
rep("const TURN = 3.2;          // rad/s at full steer", "const TURN = 3.4;          // rad/s at full steer (more when slow, and it keeps its arc when fast)")
rep("SELF_RESPAWN_T = 2, RESPAWN_T = 5, FLAT_T = 2,", "SELF_RESPAWN_T = 2, RESPAWN_T = 3.5, FLAT_T = 1.5,")
rep("const OWN_DRAIN = 0.35;", "const TURF_OWN = 1.18, TURF_FOE = 0.86, OWN_REFILL = 0.06; // your own color is a fast lane that slowly refills you; theirs drags a little")

# what's under you: 1 your color, -1 theirs, 0 bare (sampled just past the paint you're laying)
rep("function ownUnder(D) {", "function turfUnder(D) { const x = D.x + Math.sin(D.yaw) * 0.55, z = D.z + Math.cos(D.yaw) * 0.55; let best = 0.2, v = 0; for (const k of grid[cellOf(x, z)]) { const dx = sX[k] - x, dz = sZ[k] - z, d = dx * dx + dz * dz; if (d < best && Math.abs(sY[k] - D.y) < 0.35) { best = d; v = painted[k]; } } return v ? ((v - 1) % 2 === D.team ? 1 : -1) : 0; }\nfunction ownUnder(D) {")

# blobs remember their turf, a smoothed speed factor, and pound timing for the telegraph
rep("dilT: 0, giantT: 0, knockT: 0,", "dilT: 0, giantT: 0, knockT: 0, turf: 0, turfK: 1, slamT: 0, slamEta: 0.6,")

# ================= movement =================
# speed: quick to get going, a little slower to bleed off extra speed; turf sets the cruise
rep("else if (!D.air) { let tgt = cfg.speed * speedMul * slopeK(D) * D.slowK * (D.cpu ? AI.speed : 1) * (D.dry ? DRY_SPD : 1); if (D.giantT > 0) tgt = Math.min(tgt * GIANT_SPD, cfg.speed * 2.8); D.spd += (tgt - D.spd) * Math.min(1, dt * (D.spd > tgt ? (D.slowed ? 9 : D.dry ? 5 : 1.6) : 3.2)); }",
    "else if (!D.air) { let tgt = cfg.speed * speedMul * slopeK(D) * D.slowK * (D.cpu ? AI.speed : 1) * (D.dry ? DRY_SPD : 1) * D.turfK; if (D.giantT > 0) tgt = Math.min(tgt * GIANT_SPD, cfg.speed * 2.8); D.spd += (tgt - D.spd) * Math.min(1, dt * (D.spd > tgt ? (D.slowed ? 9 : D.dry ? 5 : 2.6) : 9)); }")
# turf: own color refills instead of draining
rep("      if (D.giantT <= 0) D.paint -= cfg.drain * dt * (D.charging ? STILL_DRAIN : ownUnder(D) ? OWN_DRAIN : 1); // standing still barely uses any blood, and rolling over your own color uses much less",
    "      D.turf = turfUnder(D); D.turfK += ((D.turf > 0 ? TURF_OWN : D.turf < 0 ? TURF_FOE : 1) - D.turfK) * Math.min(1, dt * 8);\n      if (D.giantT <= 0) { if (D.turf > 0 && !D.charging) D.paint = Math.min(1, D.paint + OWN_REFILL * dt); else D.paint -= cfg.drain * dt * (D.charging ? STILL_DRAIN : 1); } // rolling on your own color tops you up; holding still barely uses any")
# in the air the turf factor eases back to neutral
rep("    D.slowed = false; D.inBoil = false;\n    const prevHead = D.y + 0.8;", "    D.slowed = false; D.inBoil = false; D.turf = 0; D.turfK += (1 - D.turfK) * Math.min(1, dt * 3);\n    const prevHead = D.y + 0.8;")

# turning: snappier for your finger, quick pivots when slow, the same arc when fast
rep("""  if (D === P && !P.ai) { steerS += (input - steerS) * Math.min(1, dt * 30); input = steerS; }""", """  if (D === P && !P.ai) { steerS += (input - steerS) * Math.min(1, dt * 45); input = steerS; }""")
rep("""  D.turn += (input * TURN * scaleBy - D.turn) * Math.min(1, dt * (D === P && !P.ai ? 18 : 14));""",
    """  const sr = D.spd / cfg.speed, agile = D.air ? 1 : sr < 1 ? Math.min(D.charging ? 1.35 : 1.6, 1 + 0.6 * (1 - Math.max(0, sr))) : Math.min(1.3, sr), want = input * TURN * scaleBy * agile;
  D.turn += (want - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (want * D.turn < 0 ? 40 : 28) : 20));""")

# the floating stick: full lock a little before the edge, a gentler start for fine control, a quicker hold
rep("const MAX_DRAG = 70, DEAD = 5, HOLD_MS = 190;", "const MAX_DRAG = 70, DEAD = 6, HOLD_MS = 150;")
rep("""  const a = Math.max(0, Math.abs(dx) - DEAD) / (MAX_DRAG - DEAD);
  steerIn = t.moved ? Math.sign(dx) * Math.pow(a, 1.2) : 0;""", """  const a = Math.min(1, Math.max(0, Math.abs(dx) - DEAD) / (MAX_DRAG * 0.86 - DEAD));
  steerIn = t.moved ? Math.sign(dx) * Math.pow(a, 1.35) : 0;""")

# fewer freezes: none on ordinary landings or splash pushes, they happen all the time
rep(" if (fk > 0.6) hold = Math.max(hold, 0.035); }", " }")
rep("  if (hearable(B)) AU.bonk(0.45);\n  hitStop(0.04, A, B);\n", "  if (hearable(B)) AU.bonk(0.45);\n")

# ================= the chase =================
# the CPU's pound hangs a beat longer at the top so you can read it; both track how far along the pound is
rep("function startSlam(D) { cap(D); D.air = true; D.vy = 9; D.slam = true; D.slamHang = 0.14;", "function startSlam(D) { cap(D); D.air = true; D.vy = 9; D.slam = true; D.slamHang = D.ai ? 0.3 : 0.14; D.slamT = 0; D.slamEta = 0.43 + D.slamHang;")
rep("  else if (D.air) { D.slam = true; D.vy = Math.max(D.vy, 3); D.slamHang = 0.1;", "  else if (D.air) { D.slam = true; D.vy = Math.max(D.vy, 3); D.slamHang = D.ai ? 0.2 : 0.1; D.slamT = 0; D.slamEta = 0.3 + D.slamHang + Math.max(0, D.y - (surfaceUnder(D.x, D.z, D.y, true) > -Infinity ? surfaceUnder(D.x, D.z, D.y, true) : D.y)) / 20;")
rep("  if (D.air && (D.flingC || 0) > 0.15) { D.slam = true; D.missile = true; D.missileHang = 0.08;", "  if (D.air && (D.flingC || 0) > 0.15) { D.slam = true; D.missile = true; D.missileHang = 0.08; D.slamT = 0; D.slamEta = 0.5;")
rep("  if (D.knockT > 0) D.knockT -= dt;\n", "  if (D.knockT > 0) D.knockT -= dt;\n  if (D.slam) D.slamT += dt;\n")

# jump the shockwave: anyone well up in the air when a pound lands rides over it
rep("  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR && Math.abs(O.y - D.y) < 1.4) poundHit(O, D, O.st === 'hide' ? 'coffin' : 'pound');",
    """  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR) {
    const og = O.air ? surfaceUnder(O.x, O.z, O.y + STEP, true) : O.y, base = og > -Infinity ? og : O.y, lift = O.air ? O.y - base : 0;
    if (Math.abs(base - D.y) < 1.4) { if (lift > 0.5) dodgedPound(O, D); else poundHit(O, D, O.st === 'hide' ? 'coffin' : 'pound'); }
  }""")
rep("function poundHit(O, D, reason) {", """function dodgedPound(O, D) {
  O.immuneT = Math.max(O.immuneT, 0.25); O.wob = 1;
  for (let i = 0; i < 10; i++) { const a = i / 10 * 6.283; spawnPart(O.x, O.y, O.z, Math.cos(a) * 2.4, 0.5 + Math.random(), Math.sin(a) * 2.4, 0.35, puHaloMat, 0.5); }
  if (O === P) { popText('Dodged!'); buzz(12); AU.ready(); } else if (D === P) popText('It jumped it!');
}
function poundHit(O, D, reason) {""")

# behind on the canvas: your pound comes back a quarter faster
rep("  if (D.slamCD > 0) { D.slamCD = Math.max(0, D.slamCD - dt);", "  if (D.slamCD > 0) { D.slamCD = Math.max(0, D.slamCD - dt * (teamCov(D.team) + 3 < teamCov(1 - D.team) ? 1.25 : 1));")

# the CPU's pound telegraph: the ring fills in as the pound comes down
rep("const cWarn = new THREE.Mesh(", "const cWarnFill = new THREE.Mesh(new THREE.CircleGeometry(1, 56), new THREE.MeshBasicMaterial({ color: 0x9FD4FF, transparent: true, opacity: 0.24, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -9, polygonOffsetUnits: -9 })); cWarnFill.rotation.x = -Math.PI / 2; cWarnFill.visible = false; scene.add(cWarnFill);\nconst cWarn = new THREE.Mesh(")
rep("cWarn.scale.setScalar((slamRadius(H) + PR) * (0.94 + 0.06 * Math.sin(clock * 20))); } else cWarn.visible = false;\n  } else cWarn.visible = false;",
    "cWarn.scale.setScalar((slamRadius(H) + PR) * (0.94 + 0.06 * Math.sin(clock * 20))); cWarnFill.visible = true; cWarnFill.position.copy(cWarn.position); cWarnFill.position.y += 0.005; cWarnFill.scale.setScalar(Math.max(0.01, (slamRadius(H) + PR) * clamp(H.slamT / Math.max(0.2, H.slamEta), 0, 1))); } else { cWarn.visible = false; cWarnFill.visible = false; }\n  } else { cWarn.visible = false; cWarnFill.visible = false; }")
rep("sky, motes, ...moverMeshes,", "sky, motes, cWarnFill, foeMark, ...moverMeshes,")

# the holy water off screen: a marker on the edge of the screen points at it, and flares when it's coming for you
rep("""  <div class="orbptr" id="orbPtr"><i></i><u><b></b></u></div>""", """  <div class="orbptr" id="orbPtr"><i></i><u><b></b></u></div>
  <div class="foeptr" id="foePtr"><i></i><u><b></b></u></div>""")
rep(".orbptr.edge i{animation:orbspin 1.1s linear infinite,orbpulse .7s ease-in-out infinite alternate}", """.orbptr.edge i{animation:orbspin 1.1s linear infinite,orbpulse .7s ease-in-out infinite alternate}
.foeptr{position:absolute;left:0;top:0;width:34px;height:34px;margin:-17px 0 0 -17px;pointer-events:none;z-index:6;display:none;will-change:transform}
.foeptr.on{display:block}
.foeptr i{position:absolute;inset:8px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid var(--outline);background:#2E9BFF;box-shadow:0 0 0 2px rgba(255,255,255,.55)}
.foeptr u{position:absolute;inset:0}
.foeptr b{position:absolute;left:50%;top:-7px;margin-left:-7px;width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-bottom:10px solid #2E9BFF;filter:drop-shadow(0 0 2px rgba(20,10,40,.9))}
.foeptr.warn i{background:#FF3B5C;animation:foewarn .35s ease-in-out infinite alternate}
.foeptr.warn b{border-bottom-color:#FF3B5C}
@keyframes foewarn{to{box-shadow:0 0 14px 6px rgba(255,59,92,.85)}}""")
rep("  // rain puddles: a soft rim, and steam curling up while one dries\n", """  // the holy water off screen: an edge marker, red when its pound is coming down near you or it's lining up a fling at you
  const fpEl = $('foePtr');
  if (playing && H.st === 'play' && P.st !== 'ko') {
    tv1.set(H.x, H.y + 0.4, H.z).project(camera);
    const W = canvas.clientWidth, Hh = canvas.clientHeight, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;
    if (!behind && Math.abs(x) < 0.94 && Math.abs(y) < 0.82) { if (fpEl._on) { fpEl._on = false; fpEl.classList.remove('on'); } }
    else {
      const m = Math.max(Math.abs(x) / 0.86, Math.abs(y) / 0.7, 1e-3); x /= m; y /= m;
      const px = (x * 0.5 + 0.5) * W, py = (-y * 0.5 + 0.5) * Hh, rot = Math.atan2(x, y) * 180 / Math.PI, dHP = Math.hypot(H.x - P.x, H.z - P.z);
      const warn = (H.slam && dHP < slamRadius(H) + PR + 3) || (H.charging && H.ai && H.ai.plan && (H.ai.plan.kind === 'attack' || H.ai.plan.kind === 'shove') && dHP < 13);
      if (!fpEl._on) { fpEl._on = true; fpEl.classList.add('on'); }
      if (fpEl._warn !== warn) { fpEl._warn = warn; fpEl.classList.toggle('warn', warn); }
      fpEl.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)'; fpEl.children[1].style.transform = 'rotate(' + rot.toFixed(0) + 'deg)';
    }
  } else if (fpEl._on) { fpEl._on = false; fpEl.classList.remove('on'); }
  // rain puddles: a soft rim, and steam curling up while one dries
""")
# a faint marker under the holy water when it's lining up a fling at you (the wind-up you can read)
rep("const cWarnFill = new THREE.Mesh(", "const foeMark = new THREE.Mesh(new THREE.RingGeometry(0.42, 0.56, 32), new THREE.MeshBasicMaterial({ color: 0xFF3B5C, transparent: true, opacity: 0.7, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -8, polygonOffsetUnits: -8 })); foeMark.rotation.x = -Math.PI / 2; foeMark.visible = false; scene.add(foeMark);\nconst cWarnFill = new THREE.Mesh(")
rep("  const al = H.ai && H.ai.alert;", "  { const aim = playing && H.st === 'play' && H.charging && H.ai && H.ai.plan && (H.ai.plan.kind === 'attack' || H.ai.plan.kind === 'shove'); foeMark.visible = !!aim; if (aim) { foeMark.position.set(H.x, H.y + 0.06, H.z); foeMark.scale.setScalar(1 + 0.6 * clamp(H.charge, 0, 1) + 0.08 * Math.sin(clock * 18)); } }\n  const al = H.ai && H.ai.alert;")

# ================= camera =================
# look further ahead at speed, pull back a touch and lean toward the holy water when it's close in front of you, a little more field of view on your own color
rep("const look = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0 }; let shake = 0, camCharge = 0, camYaw = 0, gyCam = 0, lookFlatP = 0;", "const look = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0 }; let shake = 0, camCharge = 0, camYaw = 0, gyCam = 0, lookFlatP = 0, camFoe = 0;")
rep("""    const ko = P.st === 'ko' ? 1 : 0, fx = Math.sin(camYaw), fz = Math.cos(camYaw), h = 7.0 + camCharge * 3 + look.roll * 1.2 + (P.slam ? P.y * 0.6 : 0) + ko * 4 + (VP.gk - 1) * 2.4, back = 6.0 + camCharge * 1.5 + ko * 3 + (VP.gk - 1) * 1.8;
    const by = P.air ? Math.min(P.y, gyCam + 2) : P.y; gyCam += (by - gyCam) * (1 - Math.exp(-rdt * 6));
    dPos.set(P.x - fx * back, gyCam + h, P.z - fz * back);
    dLook.set(P.x + fx * 2.4 + fz * look.lean * -0.5, gyCam - 0.4, P.z + fz * 2.4 - fx * look.lean * -0.5);""",
"""    const fdx = H.x - P.x, fdz = H.z - P.z, fd = Math.hypot(fdx, fdz), foeK = H.st === 'play' && P.st === 'play' ? clamp(1 - (fd - 5) / 9, 0, 1) : 0; camFoe += (foeK - camFoe) * (1 - Math.exp(-rdt * 3));
    const ko = P.st === 'ko' ? 1 : 0, fx = Math.sin(camYaw), fz = Math.cos(camYaw), h = 7.0 + camCharge * 3 + look.roll * 1.2 + (P.slam ? P.y * 0.6 : 0) + ko * 4 + (VP.gk - 1) * 2.4 + camFoe * 0.9, back = 6.0 + camCharge * 1.5 + ko * 3 + (VP.gk - 1) * 1.8 + camFoe * 1.2;
    const by = P.air ? Math.min(P.y, gyCam + 2) : P.y; gyCam += (by - gyCam) * (1 - Math.exp(-rdt * 6));
    const ahead = 2.4 + 0.9 * clamp(P.spd / cfg.speed - 1, 0, 1), inFront = fd > 0.1 && (fdx * fx + fdz * fz) / fd > 0.2 ? camFoe * 0.22 : 0;
    dPos.set(P.x - fx * back, gyCam + h, P.z - fz * back);
    dLook.set(P.x + fx * ahead + fz * look.lean * -0.5 + fdx * inFront, gyCam - 0.4, P.z + fz * ahead - fx * look.lean * -0.5 + fdz * inFront);""")
rep("  const fovT = baseFov + (playing ? (speedMul - 1) * 12 + fovKick : 0);", "  const fovT = baseFov + (playing ? (speedMul - 1) * 12 + fovKick + (P.st === 'play' && !P.air ? clamp((P.spd / (cfg.speed * speedMul) - 1) * 14, 0, 5) : 0) : 0);")
rep("  const spK = playing && P.st === 'play' ? clamp((P.air ? Math.max(0, P.spd - cfg.speed * 1.2) : P.spd - cfg.speed * 1.15) / (cfg.speed * 0.8), 0, 1) : 0;",
    "  const spK = playing && P.st === 'play' ? clamp((P.air ? Math.max(0, P.spd - cfg.speed * 1.2) : P.spd - cfg.speed * 1.08) / (cfg.speed * 0.8), 0, 1) : 0;")

# ================= the CPU =================
rep("AI_LV.hardOld = Object.assign({}, AI_LV.hard, { plan: 0, econ: 0, coffinHunt: 0, coffinFlee: 0, model: 0, flingPaint: 0, missileCov: 0, trap: 0, shove: 0.35, misHold: 1 }); // an older hard CPU, kept for testing\n", "")
rep("AI_LV.hard22 = Object.assign({}, AI_LV.hard, { flingPaint: 0, missileCov: 0, trap: 0, shove: 0.35, misHold: 1, flResMin: 0.18, flResPad: 0.06 }); // hard before slingshot painting, for testing\n", "")
lines = s.split('\n')
for i, l in enumerate(lines):
    if l.startswith('  easy:   { think:'): lines[i] = l.replace('attack: 0.08,', 'attack: 0.12, dodge: 0.08,', 1)
    if l.startswith('  medium: { think:'): lines[i] = l.replace('attack: 0.3,', 'attack: 0.42, dodge: 0.4,', 1)
    if l.startswith('  hard:   { think:'): lines[i] = l.replace('attack: 0.55,', 'attack: 0.72, dodge: 0.8,', 1)
s = '\n'.join(lines)
assert s.count('dodge: 0.08') == 1 and s.count('dodge: 0.4') == 1 and s.count('dodge: 0.8') == 1
# its pound now lands later: lead you by that much, and time the trap on your landing to it
rep("    const T = 0.55, sp = o.flat > 0 || o.st === 'hide' ? 0 : o.spd, px = o.x + Math.sin(o.yaw) * sp * T, pz = o.z + Math.cos(o.yaw) * sp * T;", "    const T = 0.74, sp = o.flat > 0 || o.st === 'hide' ? 0 : o.spd, px = o.x + Math.sin(o.yaw) * sp * T, pz = o.z + Math.cos(o.yaw) * sp * T;")
rep("    if (tl > 0.3 && tl < 0.85 && Math.hypot(lx - D.x, lz - D.z) < KO_R - 0.7", "    if (tl > 0.25 && tl < 0.66 && Math.hypot(lx - D.x, lz - D.z) < KO_R - 0.7")
# and it can jump your pound too, if it's quick enough to read it
rep("""function aiEvade(D, dt) {
  const ai = D.ai, O = other(D), o = ai.o;""", """function aiEvade(D, dt) {
  const ai = D.ai, O = other(D), o = ai.o;
  // your pound is about to land on it: hop it at the last moment (how often it reads it in time depends on the level)
  if (O.slam && O.st === 'play' && !D.air && ai.oVis && AI.dodge > 0) {
    const sc = O.missile ? slamCenter(O) : O, d = Math.hypot(sc.x - D.x, sc.z - D.z), eta = O.slamEta - O.slamT;
    if (d < slamRadius(O) + PR + 0.4 && eta > 0.1 && eta < 0.42) { if (!ai.dodgeRolled) { ai.dodgeRolled = true; ai.dodgeOK = Math.random() < AI.dodge; } if (ai.dodgeOK) { if (D.charging) cancelCharge(D); jump(D); return true; } }
  } else if (!O.slam) ai.dodgeRolled = false;""")
open(F, 'w').write(s)
print('ok')
