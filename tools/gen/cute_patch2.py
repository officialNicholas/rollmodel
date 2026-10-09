# Eyes, properly: each eye sits square on the face (turned to the surface), and the iris lives inside the eye (a child of it), so it
# always shows as a big round disc centred in the white whatever the face's angle; the gaze is a small shift inside the eye.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, vertexColors: true, depthWrite: false }),",
    "const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, vertexColors: true }),")
rep("const IRIS_R = 0.158, pupG", "const IRIS_R = 0.165, IRIS_Z = 0.138, pupG")
rep("const pupilG = new THREE.SphereGeometry(0.097, 24, 18), shineG = new THREE.SphereGeometry(0.068, 18, 12), shine2G = new THREE.SphereGeometry(0.032, 12, 8);",
    "const pupilG = new THREE.SphereGeometry(0.1, 24, 18), shineG = new THREE.SphereGeometry(0.072, 18, 12), shine2G = new THREE.SphereGeometry(0.034, 12, 8);")
rep("""  const pu = new THREE.Mesh(pupG, irisM); pu.renderOrder = 34; parent.add(pu);
  const pl = new THREE.Mesh(pupilG, pupilM); pl.renderOrder = 34.5; pl.position.set(0, 0.006, 0.08); pu.add(pl);
  const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.06, 0.068, 0.132); pu.add(sh);
  const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.066, -0.058, 0.128); pu.add(sh2);""",
"""  // the iris is part of the eye: a lens just proud of the white's front, so a round disc of it always shows, centred
  const pu = new THREE.Mesh(pupG, irisM); pu.renderOrder = 34; pu.position.z = IRIS_Z; e.add(pu);
  const pl = new THREE.Mesh(pupilG, pupilM); pl.renderOrder = 34.5; pl.position.set(0, -0.004, 0.104); pu.add(pl);
  const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.066, 0.074, 0.14); pu.add(sh);
  const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.072, -0.064, 0.142); pu.add(sh2);""")
# where the iris sits inside the eye: x, y a small gaze shift (a touch in toward the nose and down, so it looks at you), k its size
rep("const EYE_BASE = sd => new THREE.Vector3(sd * 0.33, 0.39, 0.86).normalize();",
    """const EYE_BASE = sd => new THREE.Vector3(sd * 0.33, 0.39, 0.86).normalize();
function aimEye(it, p, sd, gx, gy, k) { it.e.position.copy(p).multiplyScalar(0.965); faceQ(it.e, p); it.pu.position.set(gx - sd * 0.03, gy - 0.025, IRIS_Z + IRIS_R * (1 - k)); it.pu.scale.setScalar(k); }""")
# the player
rep("    const p = gooJS(cyc ? tv3.set(0, 0.47, 0.88).normalize() : it.base); it.e.position.copy(p).multiplyScalar(0.965);",
    "    const p = gooJS(cyc ? tv3.set(0, 0.47, 0.88).normalize() : it.base, gooU);")
rep("    const pd = ES === 'googly' ? tv1.set(lx + Math.sin(clock * 9 + i * 2.1) * 0.035 * wig, ly - 0.07 + Math.cos(clock * 7.3 + i) * 0.02 * wig, 0.065) : ES === 'sleepy' ? tv1.set(lx, ly - 0.085, 0.035) : tv1.set(lx, ly - 0.065, 0.035 + (cyc ? 0.04 : 0));\n    it.pu.position.copy(p).multiplyScalar(0.965).add(pd);\n    { const k = (scared ? 0.72 : strain ? 0.85 : 1) * (ES === 'googly' ? 0.62 : cyc ? 1.4 : ES === 'sleepy' ? 0.85 : 1); it.pu.scale.set(k, k, k * 0.62); }",
    "    const k = (scared ? 0.72 : strain ? 0.85 : 1) * (ES === 'googly' ? 0.62 : cyc ? 1.4 : ES === 'sleepy' ? 0.85 : 1), sd = cyc ? 0 : i ? 1 : -1;\n    if (ES === 'googly') aimEye(it, p, 0, lx * 1.4 + Math.sin(clock * 9 + i * 2.1) * 0.08 * wig, ly - 0.07 + Math.cos(clock * 7.3 + i) * 0.05 * wig, k); else aimEye(it, p, sd, lx * 1.4, ly * 1.2 - (ES === 'sleepy' ? 0.05 : 0), k);")
# the holy water and the CPU rivals
rep("    const p = gooJS(it.base, gooU2); it.e.position.copy(p).multiplyScalar(0.965);", "    const p = gooJS(it.base, gooU2);")
rep("    it.pu.position.copy(p).multiplyScalar(0.965).add(tv1.set(-lookC.lean * 0.07, -0.065, 0.035)); { const k = scared ? 0.7 : 1; it.pu.scale.set(k, k, k * 0.62); }",
    "    aimEye(it, p, it.sd, -lookC.lean * 0.1, 0, scared ? 0.7 : 1);")
rep("    const p = gooJS(it.base, U); it.e.position.copy(p).multiplyScalar(0.965);", "    const p = gooJS(it.base, U);")
rep("    it.pu.position.copy(p).multiplyScalar(0.965).add(tv1.set(-L.look.lean * 0.07, -0.065, 0.035)); { const k = scared ? 0.7 : 1; it.pu.scale.set(k, k, k * 0.62); }",
    "    aimEye(it, p, it.sd, -L.look.lean * 0.1, 0, scared ? 0.7 : 1);")
# the iris is inside the eye now: listing it again would clone its material twice
rep("const pFaceParts = [...eyes.flatMap(it => [it.e, it.pu]),", "const pFaceParts = [...eyes.map(it => it.e),")
open(p, 'w').write(s)
print('ok')
