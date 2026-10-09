# The orb floats at head height, so on the ground you had to jump into it (and with an empty tank you can't). Now rolling up next to
# it is enough: within reach, on your level, nothing in between, it's drawn into you (faster as it comes, a stream of sparks behind
# it, a little smaller as it goes) and you go giant. Works for anyone, the CPUs too.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("""  orb.y = orb.base + 1.15 + Math.sin(runT * 2.2 + orb.ph) * 0.12;
  if (orb.k < 0.5) return;""",
"""  orb.y = orb.base + 1.15 + Math.sin(runT * 2.2 + orb.ph) * 0.12;
  if (orb.k < 0.5) return;
  // roll up next to it and it's drawn in: no jump (or paint) needed. The nearest blob in reach, on its level, with nothing between
  let puller = null, pd = ORB_PULL_R;
  for (const D of ACTIVE) { if (D.st !== 'play' || D.giantT > 0) continue; const h = Math.hypot(D.x - orb.x, D.z - orb.z), dy = orb.base - D.y;
    if (h < pd && dy > -1.1 && dy < 1.3 && !blockedAt((D.x + orb.x) / 2, (D.z + orb.z) / 2, Math.max(D.y, orb.base) + 0.5)) { pd = h; puller = D; } }
  if (puller) {
    if (!orb.pull) AU.pop && AU.pop();
    orb.pull = Math.min(1, (orb.pull || 0) + dt * 2.6); orb.by = puller;
    const tx = puller.x, ty = puller.y + 0.45, tz = puller.z, k = Math.min(1, dt * (1.5 + 13 * orb.pull * orb.pull));
    orb.x += (tx - orb.x) * k; orb.z += (tz - orb.z) * k; orb.tx = orb.x; orb.tz = orb.z;
    orb.y += (ty - orb.y) * Math.min(1, orb.pull * 1.4);
    orb.sparkT = (orb.sparkT || 0) + dt * 40;
    while (orb.sparkT >= 1) { orb.sparkT -= 1; const a = Math.random() * 6.283, r = 0.3 + Math.random() * 0.25; spawnPart(orb.x + Math.cos(a) * r, orb.y + (Math.random() - 0.5) * 0.4, orb.z + Math.sin(a) * r, (tx - orb.x) * 4.5, (ty - orb.y) * 4.5 + 0.4, (tz - orb.z) * 4.5, 0.32, orbPartMats[(Math.random() * orbPartMats.length) | 0], 0.28); }
  } else if (orb.pull) { orb.pull = Math.max(0, orb.pull - dt * 3); if (!orb.pull) orbPickTarget(); }""")
rep("const GIANT_T = 5, GIANT_K = 3, GIANT_SPD = 1.75, GIANT_SLAM = 1.5, ORB_R = 0.42;",
    "const GIANT_T = 5, GIANT_K = 3, GIANT_SPD = 1.75, GIANT_SLAM = 1.5, ORB_R = 0.42, ORB_PULL_R = 2.4; // ORB_PULL_R: how close you roll before it's drawn in;")
# touching it at the end of the pull (it's centred on you by then) takes it; the pull state clears with it
rep("function takeOrb(D) {\n  orb.on = false;", "function takeOrb(D) {\n  orb.on = false; orb.pull = 0;")
rep("orb.on = true; orb.k = 0; orb.x = c[0];", "orb.on = true; orb.k = 0; orb.pull = 0; orb.x = c[0];")
# a little smaller and quicker-spinning while it's being drawn in
rep("const sc = 1 - Math.pow(1 - orb.k, 3); orb.g.position.set(orb.x, orb.y, orb.z);",
    "const sc = (1 - Math.pow(1 - orb.k, 3)) * (1 - 0.35 * (orb.pull || 0)); orb.g.position.set(orb.x, orb.y, orb.z);")
rep("hint('orb', 'Touch the orb to go giant', 2.8);", "hint('orb', 'Roll up to the orb to go giant', 2.8);")
rep("$('howOrb').textContent = 'Grab the glowing orb to go giant for 5 seconds.", "$('howOrb').textContent = 'Roll up to the glowing orb (or jump into it) to go giant for 5 seconds.")
open(p, 'w').write(s)
print('ok')
