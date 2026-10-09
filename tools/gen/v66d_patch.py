# V66: the tumble flips about any level axis (head over heels along whatever pushed it), so a blob popped up by a pound beside it or blown
# back by a hard splash goes over the way it's thrown. The drawn heading is kept on its own (a flip no longer has to live in the root's
# Euler angles), and everything that reads the drawn heading reads that
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:160])
    src = src.replace(old, new)
# the request carries the way it's thrown (world x, z); by default the way it now faces
rep("function fxTumble(D, k, side) { if (k > D.fxT) { D.fxT = k; D.fxSide = side >= 0 ? 1 : -1; } }",
    "function fxTumble(D, k, side, dx, dz) { if (k > D.fxT) { D.fxT = k; D.fxSide = side >= 0 ? 1 : -1; const l = dx === undefined ? 0 : Math.hypot(dx, dz); if (l > 1e-4) { D.fxDX = dx / l; D.fxDZ = dz / l; } else { D.fxDX = Math.sin(D.yaw); D.fxDZ = Math.cos(D.yaw); } } }")
rep("look: null, wearOff: false, wearPop: 1,", "fxDX: 0, fxDZ: 1, look: null, wearOff: false, wearPop: 1,")
# the tumble's state: the throw's direction in the world
rep("V.tum = { t: 0, T: clamp(flightTime(D) - 0.1, 0.42, 1.25), side: D.fxSide, k: Math.min(1, fxT), fin: -1, a: a0, a0, aEnd: a0 < 0.01 ? 6.2832 : 6.2832 * Math.ceil((a0 + 3.8) / 6.2832) }; }",
    "V.tum = { t: 0, T: clamp(flightTime(D) - 0.1, 0.42, 1.25), side: D.fxSide, k: Math.min(1, fxT), fin: -1, a: a0, a0, aEnd: a0 < 0.01 ? 6.2832 : 6.2832 * Math.ceil((a0 + 3.8) / 6.2832), wx: D.fxDX, wz: D.fxDZ }; }")
# the root: heading and the small tilts as Euler angles, the flip on top as a turn about its own level axis
rep("+ V.pullLean + tumX, yawD + spinY, (D === P && idle.sway ? idle.sway * 0.06 : 0) + (D.shimNow ? D.shimNow.shove * 0.05 : 0) + tumZ);",
    "+ V.pullLean, yawD + spinY, (D === P && idle.sway ? idle.sway * 0.06 : 0) + (D.shimNow ? D.shimNow.shove * 0.05 : 0));\n"
    "  V.yawDraw = V.root.userData.yawDraw = yawD + spinY;\n"
    "  if (V.tum && (tumX || tumZ)) { const c = Math.cos(V.yawDraw), s = Math.sin(V.yawDraw), lx = V.tum.wx * c - V.tum.wz * s, lz = V.tum.wx * s + V.tum.wz * c;\n"
    "    tumQ.setFromAxisAngle(tumA.set(lz, 0, -lx), tumX); V.root.quaternion.multiply(tumQ); tumQ.setFromAxisAngle(tumA.set(lx, 0, lz), tumZ); V.root.quaternion.multiply(tumQ); }")
rep("function flightTime(D) {", "const tumQ = new THREE.Quaternion(), tumA = new THREE.Vector3();\nfunction flightTime(D) {")
# everything that reads the drawn heading
rep("  let rel = Math.atan2(best.x - D.x, best.z - D.z) - V.root.rotation.y; rel = Math.atan2(Math.sin(rel), Math.cos(rel));",
    "  let rel = Math.atan2(best.x - D.x, best.z - D.z) - (V.yawDraw === undefined ? V.root.rotation.y : V.yawDraw); rel = Math.atan2(Math.sin(rel), Math.cos(rel));")
rep("W = V.slimeWatchT, wy = W ? V.root.rotation.y + W.yaw : D.yaw;", "W = V.slimeWatchT, wy = W ? (V.yawDraw === undefined ? V.root.rotation.y : V.yawDraw) + W.yaw : D.yaw;")
rep("  if (fxK > 0) { const ry = V.root.rotation.y, c = Math.cos(ry), s = Math.sin(ry);", "  if (fxK > 0) { const ry = V.yawDraw, c = Math.cos(ry), s = Math.sin(ry);")
rep("const r = wrapA(Math.atan2(O.x - D.x, O.z - D.z) - V.root.rotation.y);", "const r = wrapA(Math.atan2(O.x - D.x, O.z - D.z) - V.yawDraw);")
rep("  o.yaw = V.root.rotation.y; o.aimPitch", "  o.yaw = V.yawDraw; o.aimPitch")
rep("yaw = root.rotation.y, c0 = Math.cos(yaw), s0 = Math.sin(yaw), lx = ox * c0 - oz * s0, lz = ox * s0 + oz * c0;",
    "yaw = root.userData.yawDraw === undefined ? root.rotation.y : root.userData.yawDraw, c0 = Math.cos(yaw), s0 = Math.sin(yaw), lx = ox * c0 - oz * s0, lz = ox * s0 + oz * c0;")
# a pound's shockwave close by throws you over; so does a full-power splash right beside you
rep("B.air = true; B.stroke++; B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; fxKnock(B, B.x - D.x, B.z - D.z, 0.35 + 0.35 * (1 - bd / 16)); } }",
    "B.air = true; B.stroke++; B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; fxKnock(B, B.x - D.x, B.z - D.z, 0.35 + 0.35 * (1 - bd / 16)); if (bd < 7) fxTumble(B, 0.75, Math.random() - 0.5, B.x - D.x, B.z - D.z); } }", 2)
rep("  if (!B.air) { B.air = true; B.stroke++; B.vy = 2.4 + 1.2 * fk; } else B.vy = Math.max(B.vy, 1.5);",
    "  if (!B.air) { B.air = true; B.stroke++; B.vy = 2.4 + 1.2 * fk; } else B.vy = Math.max(B.vy, 1.5);\n  if (fk > 0.7 && k > 0.8) fxTumble(B, 0.6, Math.random() - 0.5, nx, nz);")
open(P, 'w').write(src)
print('ok', len(src))
