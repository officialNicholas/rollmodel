import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# also warn when the missile's path runs over you, since it can still bend in
rep("if (F.missile && F.slam) { const c = missileHit(F); if (c && Math.hypot(c.x - P.x, c.z - P.z) < MISSILE_R + PR + 1.2) { threat = { F, k: 'missile' }; return; } }",
    "if (F.missile && F.slam) { const c = missileHit(F); if (c && (Math.hypot(c.x - P.x, c.z - P.z) < MISSILE_R + PR + 1.2 || segDist(P.x, P.z, F.x, F.z, c.x, c.z) < MISSILE_R + PR)) { threat = { F, k: 'missile' }; return; } }")
rep("let threat = null, threatShown = '', threatOn = false;",
    "let threat = null, threatShown = '', threatOn = false;\nfunction segDist(px, pz, ax, az, bx, bz) { const vx = bx - ax, vz = bz - az, l = vx * vx + vz * vz, t = l > 0 ? clamp(((px - ax) * vx + (pz - az) * vz) / l, 0, 1) : 0; return Math.hypot(px - ax - vx * t, pz - az - vz * t); }")
open(F, 'w').write(s)
print('ok')
