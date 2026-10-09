# the pickup loses its face; a blob that grabs it becomes the roller: its own jelly, in its own color, is the roller's cover, with orange caps,
# a chrome frame and grip added round it, and its face and props stay on
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
rep("""  if (type === 'roller') { const K = ROLLER, rl = new THREE.Group(); rl.position.y = 0.05; spin.add(rl); for (const [geo, m] of [[K.roll, K.rollM], [K.solid, stGlossM], [K.wire, K.chromeM], [K.mouth, K.faceM], [K.hull, outlineMat]]) { const o = new THREE.Mesh(geo, m); o.castShadow = m !== outlineMat && m !== K.faceM; rl.add(o); }
    eyes = new THREE.Mesh(K.eyes, K.faceM); eyes.position.y = 0.035; rl.add(eyes); }""",
"""  if (type === 'roller') { const K = ROLLER, rl = new THREE.Group(); rl.position.y = 0.05; spin.add(rl); for (const [geo, m] of [[K.roll, K.rollM], [K.solid, stGlossM], [K.wire, K.chromeM], [K.hull, outlineMat]]) { const o = new THREE.Mesh(geo, m); o.castShadow = m !== outlineMat; rl.add(o); } eyes = rl; }""")
rep("if (pw.eyes) { const yaw = Math.atan2(camera.position.x - pw.x, camera.position.z - pw.z), bl = (clock * 0.37 + pw.phase * 0.21) % 1; pw.spin.rotation.set(Math.sin(clock * 2.6 + pw.phase) * 0.1, yaw + Math.sin(clock * 1.5 + pw.phase) * 0.42, Math.sin(clock * 2.1 + pw.phase) * 0.16); pw.eyes.scale.y = bl > 0.955 ? Math.max(0.08, Math.abs(bl - 0.9775) / 0.0225) : 1; }",
    "if (pw.eyes) { const yaw = Math.atan2(camera.position.x - pw.x, camera.position.z - pw.z); pw.spin.rotation.set(Math.sin(clock * 2.6 + pw.phase) * 0.1, yaw + Math.sin(clock * 1.5 + pw.phase) * 0.5, Math.sin(clock * 2.1 + pw.phase) * 0.16); }")
# the rig a blob wears as the roller, in body units (the jelly stretches 2.25 wide when it rolls)
rep("""function makePowerMesh(type) {""", """// the roller a blob turns into: orange caps on its ends, a chrome arm from one of them over its back to an orange grip (in body units)
const ROLL_RIG = (() => {
  const V3 = (x, y, z) => new THREE.Vector3(x, y, z), V2 = (x, y) => new THREE.Vector2(x, y), OR = hexC(0xFF6A1A), ORD = hexC(0xCC4410), WH = hexC(0xF4F1EA), seg = HI ? 28 : 16;
  const cap = sd => new THREE.LatheGeometry([[0.001, -0.07], [0.62, -0.07], [0.94, -0.05], [1.0, 0], [0.94, 0.05], [0.6, 0.08], [0.22, 0.09], [0.2, 0.16], [0.001, 0.16]].map(q => V2(q[0], q[1])), seg).rotateZ(-sd * Math.PI / 2).translate(sd * 2.2, 0, 0);
  const g0 = V3(0.9, 1.45, -1.25), gd = V3(-0.28, 0.42, -0.86).normalize(), g1 = g0.clone().addScaledVector(gd, 1.25), mid = g0.clone().add(g1).multiplyScalar(0.5);
  const solid = vcGeo([[cap(1), OR], [cap(-1), OR],
    [new THREE.CapsuleGeometry(0.17, 0.95, 4, HI ? 14 : 8).applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(YAX, gd))).translate(mid.x, mid.y, mid.z), (x, y, z, o) => { const t = (x - g0.x) * gd.x + (y - g0.y) * gd.y + (z - g0.z) * gd.z; return o.copy(t > 0.78 && t < 0.92 ? ORD : OR); }],
    [tubeBetween(g0.clone().addScaledVector(gd, -0.12), g0.clone().addScaledVector(gd, 0.1), 0.15, 0.16, HI ? 14 : 8), WH]]);
  const wire = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V3(2.25, 0, 0), V3(2.62, 0, 0), V3(2.78, 0.45, -0.36), V3(2.25, 1.12, -0.95), V3(1.25, 1.42, -1.2), g0.clone().addScaledVector(gd, -0.05)], false, 'centripetal'), HI ? 32 : 16, 0.07, HI ? 8 : 5);
  return { solid, wire };
})();
function addRig(V) { const g = new THREE.Group(); g.visible = false; const a = new THREE.Mesh(ROLL_RIG.solid, stGlossM), b = new THREE.Mesh(ROLL_RIG.wire, ROLLER.chromeM); a.castShadow = b.castShadow = true; g.add(a); g.add(b); V.body.add(g); V.rig = g; }
function makePowerMesh(type) {""")
# every blob gets one (hidden until it rolls), next to its bat wings
rep("addBat(VP); addBat(VC);", "addBat(VP); addBat(VC); addRig(VP); addRig(VC);")
rep("  const V = { root: drop, body, mat, hull, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) }; addBat(V);", "  const V = { root: drop, body, mat, hull, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) }; addBat(V); addRig(V);")
# it fades in with the morph, rides the body's scale (the rig lives in the body group), and the caps spin as it rolls
rep("""  if (V.bat) { if (D.batT > 0)""", """  if (V.rig) { const k = L.roll; V.rig.visible = k > 0.05 && D.st !== 'ko'; if (V.rig.visible) { const e = Math.min(1, (k - 0.05) / 0.6); V.rig.scale.set(e, e, e); } }
  if (V.bat) { if (D.batT > 0)""")
open(p, 'w').write(s)
print('ok')
