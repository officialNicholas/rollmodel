# Character v2c: a ball-like body settling into its puddle (round belly, curving under, a meniscus melting out), eyes set
# into the surface, the hat seated on the rounder head, a less milky puddle, and Customize framing that fits the whole blob
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:100]); s = s.replace(old, new)

OLD = [(1.045, -0.16), (1.075, -0.31), (1.082, -0.45), (1.058, -0.58), (1.012, -0.684), (1.06, -0.755), (1.30, -0.79), (1.56, -0.785), (1.70, -0.812)]
NEW = [(1.04, -0.15), (1.055, -0.30), (1.035, -0.44), (0.975, -0.565), (0.905, -0.665), (0.90, -0.745), (1.12, -0.785), (1.42, -0.79), (1.62, -0.812)]
for i, (o, n) in enumerate(zip(OLD, NEW)):
    rep(f"if (i == {i + 1}) return vec2({o[0]}, {o[1]});", f"if (i == {i + 1}) return vec2({n[0]}, {n[1]});")
rep("[1.0, 0], " + ", ".join(f"[{r}, {y}]" for r, y in OLD) + ", [0, -0.82]", "[1.0, 0], " + ", ".join(f"[{r}, {y}]" for r, y in NEW) + ", [0, -0.82]")

# eyes set into the face: the body hides the part of each eye behind its surface, so a far eye tucks round the curve
rep("it.e.position.copy(p).multiplyScalar(0.995)", "it.e.position.copy(p).multiplyScalar(0.965)", count=3)
rep("it.pu.position.copy(p).multiplyScalar(1.035)", "it.pu.position.copy(p).multiplyScalar(1.0)", count=3)
rep("it.e.scale.set(s, sy * s, 0.45);", "it.e.scale.set(s, sy * s, 0.5);")
rep("it.e.scale.set(1, sy, 0.45);", "it.e.scale.set(1, sy, 0.5);", count=2)

# the hat on the rounder head
rep("W.hat.position.copy(gooJS(tv2.set(0, 1, 0), U)).add(tv1.set(0.03, HI ? -0.17 : -0.1, -0.03));", "W.hat.position.copy(gooJS(tv2.set(0, 1, 0), U)).add(tv1.set(0.03, HI ? -0.27 : -0.2, -0.03));")

# the melted-out puddle reflects less of the sky, so it stays the jelly's own color
rep("  reflectedLight.directDiffuse *= 0.5;\n", "  reflectedLight.directDiffuse *= 0.5; reflectedLight.indirectSpecular *= 1.0 - 0.45 * pud;\n")

# Customize: aim at the middle of the blob, and fit the puddle (and wings) as well as the body
rep("const a = hero.yaw, ly = 0.62; dPos.set(hero.mx + Math.sin(a) * dist, ly + 0.02 + dist * 0.2 + Math.sin(clock * 0.47) * 0.04, hero.mz + Math.cos(a) * dist);",
    "const a = hero.yaw, ly = myLook.head === 'hat' ? 0.44 : 0.36; dPos.set(hero.mx + Math.sin(a) * dist, ly + 0.06 + dist * 0.16 + Math.sin(clock * 0.47) * 0.04, hero.mz + Math.cos(a) * dist);")
rep("wide = myLook.back === 'wings' ? 1.75 : 1.15, tall = myLook.head === 'hat' ? 1.35 : myLook.head ? 1.15 : 0.95;\n  heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.62 * fh), wide * W / (2 * tv * asp * 0.72 * fw)), 1.8, 9);",
    "wide = myLook.back === 'wings' ? 1.95 : 1.55, tall = myLook.head === 'hat' ? 1.25 : myLook.head ? 1.05 : 0.88;\n  heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.6 * fh), wide * W / (2 * tv * asp * 0.7 * fw)), 2.3, 9);")
open(p, 'w').write(s)
print('ok')
