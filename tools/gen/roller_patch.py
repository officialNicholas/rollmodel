# the Roller power-up: a paint roller wrapped in drippy pink and orange paint, orange caps and grip on a chrome frame, with a face that turns to you
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
rep("""function makePowerMesh(type) {""", """// the roller: built once and shared. The paint wraps round it in wavy bands (u goes round the roller, v along it), drips running off their edges
const ROLLER = (() => {
  const W = HI ? 512 : 256, Hh = HI ? 256 : 128, k = W / 512, cv = document.createElement('canvas'); cv.width = W; cv.height = Hh; const g = cv.getContext('2d'), r = rng(808);
  g.fillStyle = '#FFFBF4'; g.fillRect(0, 0, W, Hh);
  const band = (y0, y1, cols, a0, a1, ph) => { const gr = g.createLinearGradient(0, y0 * Hh, 0, y1 * Hh); cols.forEach((c, i) => gr.addColorStop(i / (cols.length - 1), c)); g.fillStyle = gr; g.beginPath();
    for (let x = 0; x <= W; x += 8) { const u = x / W * 6.2832, y = (y0 + a0 * Math.sin(u * 3 + ph) + a0 * 0.5 * Math.sin(u * 5 + ph * 2)) * Hh; x ? g.lineTo(x, y) : g.moveTo(x, y); }
    for (let x = W; x >= 0; x -= 8) { const u = x / W * 6.2832, y = (y1 + a1 * Math.sin(u * 2 + ph + 1) + a1 * 0.4 * Math.sin(u * 6 + ph)) * Hh; g.lineTo(x, y); } g.closePath(); g.fill();
    // drips off the band's lower edge
    for (let i = 0; i < 6; i++) { const x = r() * W, u = x / W * 6.2832, yb = (y1 + a1 * Math.sin(u * 2 + ph + 1) + a1 * 0.4 * Math.sin(u * 6 + ph)) * Hh, w = (7 + r() * 9) * k, len = (8 + r() * 22) * k; g.beginPath(); g.moveTo(x - w / 2, yb - 2); g.lineTo(x - w / 2, yb + len); g.arc(x, yb + len, w / 2, Math.PI, 0, true); g.lineTo(x + w / 2, yb - 2); g.fill(); } };
  band(0.04, 0.42, ['#FF2E9A', '#FF4FB0', '#E8208A'], 0.03, 0.05, 0.4);
  band(0.36, 0.7, ['#FF8A1F', '#FF6A12', '#FF9A30'], 0.04, 0.05, 2.1);
  band(0.64, 0.95, ['#FFC21E', '#FFAA14', '#FFD24A'], 0.035, 0.03, 4.3);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.wrapS = THREE.RepeatWrapping; tex.anisotropy = 4;
  const R = 0.165, L = 0.56, seg = HI ? 40 : 20;
  const roll = new THREE.CylinderGeometry(R, R, L, seg, 1, true).rotateZ(Math.PI / 2);
  const V2 = (x, y) => new THREE.Vector2(x, y), OR = hexC(0xFF6A1A), ORD = hexC(0xD9480C), WH = hexC(0xF4F1EA);
  // caps: a rounded orange disc at each end with a little hub; the grip: an orange handle with a dark band and a white collar
  const cap = sd => new THREE.LatheGeometry([[0.001, -0.026], [R * 0.6, -0.026], [R + 0.004, -0.02], [R + 0.016, 0], [R + 0.004, 0.02], [R * 0.55, 0.026], [0.05, 0.03], [0.04, 0.045], [0.001, 0.045]].map(q => V2(q[0], q[1])), seg).rotateZ(-sd * Math.PI / 2).translate(sd * (L / 2 + 0.01), 0, 0);
  const gripDir = new THREE.Vector3(0.42, -0.9, -0.06).normalize(), gripTop = new THREE.Vector3(0.36, -0.27, -0.05), gripEnd = gripTop.clone().addScaledVector(gripDir, 0.24);
  const solid = vcGeo([[cap(1), OR], [cap(-1), OR],
    [new THREE.CapsuleGeometry(0.042, 0.17, 4, HI ? 14 : 8).applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(YAX, gripDir))).translate((gripTop.x + gripEnd.x) / 2, (gripTop.y + gripEnd.y) / 2, (gripTop.z + gripEnd.z) / 2), (x, y, z, o) => { const t = (y - gripTop.y) / (gripEnd.y - gripTop.y); return o.copy(t > 0.62 && t < 0.72 ? ORD : OR); }],
    [tubeBetween(gripTop.clone().addScaledVector(gripDir, -0.03), gripTop.clone().addScaledVector(gripDir, 0.03), 0.034, 0.038, HI ? 14 : 8), WH]]);
  // the frame: a chrome rod out of the right cap, bent round and down into the grip
  const wire = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(L / 2 - 0.02, 0, 0), new THREE.Vector3(L / 2 + 0.07, 0, 0), new THREE.Vector3(L / 2 + 0.11, -0.05, -0.02), new THREE.Vector3(L / 2 + 0.1, -0.16, -0.045), gripTop.clone().addScaledVector(gripDir, -0.02)], false, 'centripetal'), HI ? 28 : 14, 0.013, HI ? 8 : 5);
  // the face, on the roller's front: big eyes with a shine (their own mesh, so they can blink), a smile and rosy cheeks
  const zs = y => Math.sqrt(R * R - y * y), eye = [], mouth = [], ink = hexC(0x23102E);
  for (const sx of [-1, 1]) { const ex = sx * 0.072, ey = 0.035, ez = zs(ey) + 0.004;
    eye.push([new THREE.SphereGeometry(0.046, 16, 12).scale(1, 1.15, 0.45).translate(ex, ey, ez), hexC(0xFFFFFF)]);
    eye.push([new THREE.SphereGeometry(0.028, 14, 10).scale(1, 1.15, 0.5).translate(ex + sx * 0.004, ey - 0.006, ez + 0.012), ink]);
    eye.push([new THREE.SphereGeometry(0.0095, 8, 6).translate(ex - 0.008, ey + 0.012, ez + 0.026), hexC(0xFFFFFF)]);
    mouth.push([new THREE.CircleGeometry(0.022, 14).scale(1.25, 0.75, 1).translate(sx * 0.11, -0.03, zs(-0.03) + 0.003), hexC(0xFF7FB8)]); }
  const smile = new THREE.TorusGeometry(0.028, 0.0075, 6, 16, Math.PI); smile.rotateZ(Math.PI); smile.translate(0, -0.028, zs(-0.03) + 0.006); mouth.push([smile, ink]);
  const hull = mergeGeos([new THREE.CylinderGeometry(R + 0.03, R + 0.03, L + 0.1, 24).rotateZ(Math.PI / 2), new THREE.CapsuleGeometry(0.06, 0.17, 3, 10).applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(YAX, gripDir))).translate((gripTop.x + gripEnd.x) / 2, (gripTop.y + gripEnd.y) / 2, (gripTop.z + gripEnd.z) / 2)]);
  return { roll, solid, wire, eyes: vcGeo(eye), mouth: vcGeo(mouth), hull, rollM: toon(0xFFFFFF, { map: tex }, { roughness: 0.26 }), chromeM: toon(0xE6EAF0, null, { metalness: 1, roughness: 0.16 }), faceM: new THREE.MeshBasicMaterial({ vertexColors: true }) };
})();
function makePowerMesh(type) {""")
rep("""  if (type === 'roller') { add(PU_G.roll, puIconMat, V(0, 0, 0), [0, 0, Math.PI / 2]); add(PU_G.stick, puHaloMat, V(0, 0.26, 0)); }""",
"""  let eyes = null;
  if (type === 'roller') { const K = ROLLER, rl = new THREE.Group(); rl.position.y = 0.05; spin.add(rl); for (const [geo, m] of [[K.roll, K.rollM], [K.solid, stGlossM], [K.wire, K.chromeM], [K.mouth, K.faceM], [K.hull, outlineMat]]) { const o = new THREE.Mesh(geo, m); o.castShadow = m !== outlineMat && m !== K.faceM; rl.add(o); }
    eyes = new THREE.Mesh(K.eyes, K.faceM); rl.add(eyes); }""")
rep("""  const bub = new THREE.Mesh(bubbleG, bubbleMat); bub.renderOrder = 8; g.add(bub);
  scene.add(g); return { g, spin, bub };""", """  const bub = new THREE.Mesh(bubbleG, bubbleMat); bub.renderOrder = 8; g.add(bub);
  scene.add(g); return { g, spin, bub, eyes };""")
rep("Object.assign(pw, { type, x: spot[0], y: spot[1], z: spot[2], g: m.g, spin: m.spin, bub: m.bub, gone: 0, pop: 0 }); }", "Object.assign(pw, { type, x: spot[0], y: spot[1], z: spot[2], g: m.g, spin: m.spin, bub: m.bub, eyes: m.eyes, gone: 0, pop: 0 }); }")
# it turns to look at you, sways and bobs, and blinks now and then
rep("pw.spin.rotation.y = clock * 2.1 + pw.phase; pw.bub.scale.set(", "if (pw.eyes) { const yaw = Math.atan2(camera.position.x - pw.x, camera.position.z - pw.z), bl = (clock * 0.37 + pw.phase * 0.21) % 1; pw.spin.rotation.set(Math.sin(clock * 2.6 + pw.phase) * 0.1, yaw + Math.sin(clock * 1.5 + pw.phase) * 0.42, Math.sin(clock * 2.1 + pw.phase) * 0.16); pw.eyes.scale.y = bl > 0.955 ? Math.max(0.08, Math.abs(bl - 0.9775) / 0.0225) : 1; } else pw.spin.rotation.y = clock * 2.1 + pw.phase; pw.bub.scale.set(")
open(p, 'w').write(s)
print('ok')
