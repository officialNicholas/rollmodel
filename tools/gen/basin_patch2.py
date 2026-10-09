# the leap out of the basin: aimed at clear floor just in front of it (never off an edge, into a wall, a hole or a hazard), and only as far
# as that; and the blob starts all the way under the paint
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)
rep("// just up out of the paint: a look one way",
"""// which way to leap out: onto level floor just past the rim, on the basin's open side if it has one, toward the middle otherwise; never
// off an edge, into a hole or a wall, or onto a hazard, another basin or a power-up
const LEAP_D = 2.2, LEAP_VY = JUMP_V * 1.15;
function basinLeap(p) {
  const pref = potYaw(p.x, p.y, p.z), toC = Math.atan2(-p.x, -p.z), want = pref !== null ? pref : toC; let best = null, bs = -Infinity;
  for (let k = 0; k < 32; k++) {
    const a = k / 32 * 6.2832, dx = Math.sin(a), dz = Math.cos(a); let ok = true;
    for (let r = 1.0; r <= LEAP_D + 0.9 && ok; r += 0.3) { const x = p.x + dx * r, z = p.z + dz * r, s = surfaceUnder(x, z, p.y + 0.4); if (s === -Infinity || Math.abs(s - p.y) > 0.2 || blockedAt(x, z, p.y)) ok = false; }
    const lx = p.x + dx * LEAP_D, lz = p.z + dz * LEAP_D;
    if (ok && (rivals.some(q => Math.hypot(q.x - lx, q.z - lz) < q.rad + 0.9) || pots.some(q => q !== p && Math.hypot(q.x - lx, q.z - lz) < 1.4) || powers.some(w => Math.hypot(w.x - lx, w.z - lz) < 1.2))) ok = false;
    if (!ok) continue;
    const v = Math.cos(a - want) * 2 + Math.cos(a - toC) * 0.6; if (v > bs) { bs = v; best = a; }
  }
  return best !== null ? best : want;
}
// just up out of the paint: a look one way""")
rep("const yw = potYaw(p.x, p.y, p.z); D.st = 'hide'; D.pot = p; p.occ = p.lastOcc = D; D.x = p.x; D.z = p.z; D.y = D.introY0 = p.y; D.yaw = yw !== null ? yw : Math.atan2(-p.x, -p.z);",
    "D.st = 'hide'; D.pot = p; p.occ = p.lastOcc = D; D.x = p.x; D.z = p.z; D.y = D.introY0 = p.y; D.yaw = basinLeap(p);")
# the hop: high, and only as far as the floor just past the rim
rep("if (D.pot) { const p = D.pot; exitPot(D); D.vy = JUMP_V * 1.12; D.spd = cfg.speed * 0.72;",
    "if (D.pot) { const p = D.pot; exitPot(D); D.vy = LEAP_VY; D.spd = LEAP_D / ((LEAP_VY + Math.sqrt(LEAP_VY * LEAP_VY + 2 * GRAV * 0.55)) / GRAV);")
rep("BASIN_DEEP = 1.35;", "BASIN_DEEP = 2.4;")
open(P, 'w').write(src)
print('ok')
