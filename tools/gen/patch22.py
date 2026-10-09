import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:100])); sys.exit(1)
    s = s.replace(a, b)

# helpers: diagonal missile path, aim assist, homing
rep("// the mid-air sling after a coffin burst:",
    """// the missile: a pound out of a fling dives at an angle along your heading instead of dropping straight down
const MISSILE_DIVE = 0.7; // drop per unit forward (about 35 degrees)
function missileHit(D) {
  const sx = Math.sin(D.yaw), sz = Math.cos(D.yaw), h = D.missile ? D.spd : Math.max(D.spd, cfg.speed * 1.7), v = Math.max(5, h * (D.missile ? D.diveK || MISSILE_DIVE : MISSILE_DIVE)), hang = D.missile ? Math.max(0, D.missileHang || 0) : 0.08;
  let x = D.x + sx * h * hang, z = D.z + sz * h * hang, y = D.y;
  for (let t = 0; t < 2; t += 0.02) {
    const g = surfaceUnder(x, z, y + STEP, true); if (g > -Infinity && y <= g) return { x, z, y: g };
    const nx = x + sx * h * 0.02, nz = z + sz * h * 0.02; if (!blockedAt(nx, z, y)) x = nx; if (!blockedAt(x, nz, y)) z = nz; y -= v * 0.02; if (y < -5) return null;
  }
  return null;
}
const slamCenter = D => (D.missile && missileHit(D)) || D;
// aim assist (your shots only): a fling or missile pointed roughly at the holy water gets bent part of the way onto it
function assistTarget(D, cone, maxD) {
  const O = other(D); if (D.ai || O.st !== 'play' || O.immuneT > 0.3) return null;
  const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz); if (d < 1.2 || d > maxD) return null;
  const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) > cone) return null;
  return { O, d, err };
}
function assistShot(D, yaw, c) {
  const O = other(D), no = { yaw, c, lock: false }; if (D.ai || O.st !== 'play' || O.immuneT > 0.3) return no;
  const f0 = flightFor(c, D.y - O.y), lead = O.flatT > 0 || O.air ? 0 : O.spd * Math.min(f0.T, 1) * 0.5;
  const tx = O.x + Math.sin(O.yaw) * lead, tz = O.z + Math.cos(O.yaw) * lead, d = Math.hypot(tx - D.x, tz - D.z);
  if (d < 1.5 || d > 18) return no;
  const a = Math.atan2(tx - D.x, tz - D.z), err = wrapA(a - yaw);
  if (Math.abs(err) > 0.42 || Math.abs(f0.d - d) > Math.max(3.5, d * 0.4)) return no;
  const want = solveFling(Math.max(0.5, d - 0.2), D.y - O.y);
  return { yaw: yaw + err * 0.6, c: want > 0 ? clamp(c + (want - c) * 0.45, FLING_MIN, 1) : c, lock: true };
}
function missileAssist(D) {
  const t = assistTarget(D, 0.6, 16); if (!t) return;
  const h = D.spd, before = missileHit(D); if (!before || Math.hypot(before.x - t.O.x, before.z - t.O.z) > MISSILE_R + 3.5) return;
  D.yaw += t.err * 0.6;
  // a steeper or flatter dive moves where it lands: lean it part of the way toward the holy water
  const ht = Math.max(0.3, D.y - (before.y > -Infinity ? before.y : D.y - 1)), reach = Math.max(0.6, t.d - h * D.missileHang), k = clamp(ht / reach, 0.4, 1.3);
  D.diveK = MISSILE_DIVE + (k - MISSILE_DIVE) * 0.5;
}
function homeIn(D, dt, rate, cone) { const t = assistTarget(D, cone, 14); if (t) D.yaw += clamp(t.err, -rate * dt, rate * dt); }
// the mid-air sling after a coffin burst:""")

# missile start
rep("D.slam = true; D.missile = true; D.vy = Math.min(D.vy, -5); D.slamHang = 0; D.spd = Math.max(D.spd * 0.95, cfg.speed * 1.3); D.turn = 0; D.buf = 0;",
    "D.slam = true; D.missile = true; D.missileHang = 0.08; D.diveK = MISSILE_DIVE; D.vy = 0; D.slamHang = 0; D.spd = Math.max(D.spd, cfg.speed * 1.7); D.turn = 0; D.buf = 0; if (!D.ai) missileAssist(D);")
# missile flight: straight line along the dive, with a gentle pull toward the target
rep("    if (D.slam && D.vy <= 0 && D.slamHang > 0) { D.slamHang -= dt; D.vy = 0; if (D.slamHang <= 0) D.vy = -20; }",
    "    if (D.missile && D.slam) { if (D.missileHang > 0) { D.missileHang -= dt; D.vy = 0; } else D.vy = -Math.max(5, D.spd * (D.diveK || MISSILE_DIVE)); D.y += D.vy * dt; if (!D.ai) homeIn(D, dt, 1.0, 0.6); }\n    else if (D.slam && D.vy <= 0 && D.slamHang > 0) { D.slamHang -= dt; D.vy = 0; if (D.slamHang <= 0) D.vy = -20; }")
rep("if (D.charging && D.vy < -3) D.vy = -3; }",
    "if (D.charging && D.vy < -3) D.vy = -3; if (!D.ai && D.flung && !D.slam) homeIn(D, dt, 0.5, 0.35); }")
# fling: assist on release
rep("  const c = cIn !== undefined ? cIn : D.charge; clearCharge(D);", "  let c = cIn !== undefined ? cIn : D.charge; clearCharge(D);")
rep("  if (D.st === 'hide') exitPot(D); else if (!canAct(D) || D.air) return; else { cap(D); D.stroke++; }\n",
    "  if (D.st === 'hide') exitPot(D); else if (!canAct(D) || D.air) return; else { cap(D); D.stroke++; }\n  if (!D.ai) { const as = assistShot(D, D.yaw, c); D.yaw = as.yaw; c = as.c; }\n")
# aim ring follows the assist and turns gold when it's locked on
rep("    } else if (aiming) {\n      const c = Math.max(FLING_MIN, P.charge), v0 = launchV(c)",
    "    } else if (aiming) {\n      const as = assistShot(P, P.yaw, Math.max(FLING_MIN, P.charge)), c = as.c, v0 = launchV(c)")
rep("dist = hs * T, fx = fwdX(), fz = fwdZ(),", "dist = hs * T, fx = Math.sin(as.yaw), fz = Math.cos(as.yaw),")
rep("      const pop = Math.min(1, P.charge / 0.12);\n      aimRing.position.set(lx,",
    "      const pop = Math.min(1, P.charge / 0.12); aimIn.material.color.setHex(as.lock ? 0xFFD23F : 0xFFFFFF);\n      aimRing.position.set(lx,")
rep("    if (aiming && P.air && P.airSling) {\n", "    if (aiming && P.air && P.airSling) {\n      aimIn.material.color.setHex(0xFFFFFF);\n")
rep("    if (!aiming && P.slam) { aimRing.position.set(P.x, (gy > -Infinity ? gy : 0) + 0.11, P.z); aimRing.scale.setScalar(SLAM_R / 0.84 * (0.94 + 0.06 * Math.sin(clock * 14))); aimRing.visible = true; }",
    "    if (!aiming && P.slam) { aimIn.material.color.setHex(0xFFFFFF); const mh = P.missile ? missileHit(P) : null; if (mh) aimRing.position.set(mh.x, mh.y + 0.11, mh.z); else aimRing.position.set(P.x, (gy > -Infinity ? gy : 0) + 0.11, P.z); aimRing.scale.setScalar((P.missile ? MISSILE_R : SLAM_R) / 0.84 * (0.94 + 0.06 * Math.sin(clock * 14))); aimRing.visible = !P.missile || !!mh; }")
# the holy water's warning ring and your danger vignette sit where its missile will land
rep("    if (H.slam) { cWarn.visible = true; const gy = surfaceUnder(H.x, H.z, H.y + 0.3, true); cWarn.position.set(H.x, (gy > -Infinity ? gy : 0) + 0.12, H.z);",
    "    if (H.slam) { cWarn.visible = true; const hc = slamCenter(H), gy = hc.y !== undefined && hc !== H ? hc.y : surfaceUnder(H.x, H.z, H.y + 0.3, true); cWarn.position.set(hc.x, (gy > -Infinity ? gy : 0) + 0.12, hc.z);")
rep("(H.slam && Math.hypot(H.x - P.x, H.z - P.z) < (H.missile ? MISSILE_R + PR : KO_R) + 1)",
    "(H.slam && (hc => Math.hypot(hc.x - P.x, hc.z - P.z))(slamCenter(H)) < (H.missile ? MISSILE_R + PR : KO_R) + 1)")
# CPU: aim missiles by where the dive lands, and dodge where yours lands
rep("d < ((D.flingC || 0) > 0.15 ? MISSILE_R + PR - 1.2 : AI.poundR * 0.85)",
    "((D.flingC || 0) > 0.15 ? (mh => !!mh && Math.hypot(mh.x - o.x, mh.z - o.z) < MISSILE_R + PR - 1.2)(missileHit(D)) : d < AI.poundR * 0.85)")
rep("    const d = Math.hypot(o.x - D.x, o.z - D.z);\n    if (d < KO_R + 1.3 && !ai.evadeRolled) { ai.evadeRolled = true; if (Math.random() < AI.evade) { ai.evadeT = 0.7; ai.evX = o.x; ai.evZ = o.z; return true; } }",
    "    const sc = O.missile ? slamCenter(O) : o, d = Math.hypot(sc.x - D.x, sc.z - D.z);\n    if (d < (O.missile ? MISSILE_R + PR : KO_R) + 1.3 && !ai.evadeRolled) { ai.evadeRolled = true; if (Math.random() < AI.evade) { ai.evadeT = 0.7; ai.evX = sc.x; ai.evZ = sc.z; return true; } }")
# body tilts into the dive
rep("V.root.rotation.set(0, D.yaw + (D === P && celebrating ? clock * 3 : 0), 0);",
    "V.misK = (V.misK || 0) + (((D.missile && D.slam) ? 1 : 0) - (V.misK || 0)) * Math.min(1, dt * 14); if (V.root.rotation.order !== 'YXZ') V.root.rotation.order = 'YXZ';\n  V.root.rotation.set(-0.85 * V.misK, D.yaw + (D === P && celebrating ? clock * 3 : 0), 0);")
open(F, 'w').write(s)
print('ok')
