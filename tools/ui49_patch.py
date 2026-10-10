#!/usr/bin/env python3
"""The turret the Splatoon way: a wide brushed-metal base with a beveled rim and bolts, the blob squatting inside a glass dome as the ink, and a short metal nozzle out the front. No more orange. On top of ui48_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui48_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
def cut(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]

cut("const TURRET_RIG = (() => {", "function addTurret(V) {", r'''const TURRET_RIG = (() => {
  const V2 = (x, y) => new THREE.Vector2(x, y), SV = hexC(0xD9DEE6), SVD = hexC(0x8E95A3), SVL = hexC(0xF4F6FA), GR = hexC(0x3D3550), seg = HI ? 48 : 24, L = -0.3;
  // the base: a wide disc, a beveled rim with a groove, a raised collar the dome sits in
  const base = new THREE.LatheGeometry([[0.001, -0.84 + L], [1.3, -0.84 + L], [1.4, -0.78 + L], [1.44, -0.66 + L], [1.4, -0.58 + L], [1.3, -0.55 + L], [1.14, -0.55 + L], [1.1, -0.5 + L], [1.08, -0.45 + L], [0.98, -0.44 + L], [0.9, -0.5 + L], [0.6, -0.52 + L], [0.001, -0.52 + L]].map(q => V2(q[0], q[1])), seg);
  const bolts = []; for (let i = 0; i < 6; i++) { const a = i / 6 * 6.2832 + 0.52, b = new THREE.CylinderGeometry(0.055, 0.065, 0.05, 10); b.translate(Math.sin(a) * 1.24, -0.53 + L, Math.cos(a) * 1.24); bolts.push([b, SVD]); }
  const baseG = vcGeo([[base, (x, y, z, o) => o.copy(y > -0.68 + L && y < -0.6 + L ? SVD : y > -0.5 + L ? SVL : SV)]].concat(bolts));
  // the nozzle: a short fat metal tube out the front, angled up a little, a darker ring round its collar and a lip at the mouth
  const dir = new THREE.Vector3(0, 0.26, 1).normalize(), b0 = new THREE.Vector3(0, -0.12, 0.5), bl = 1.0, br = 0.25, at = t => b0.clone().addScaledVector(dir, t), q = new THREE.Quaternion().setFromUnitVectors(YAX, dir), rot = g => g.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(q));
  const along = (g, t) => { rot(g); const c = at(t); return g.translate(c.x, c.y, c.z); };
  const tube = along(new THREE.CylinderGeometry(br, br * 1.08, bl, seg, 1, true), bl / 2);
  const collar = along(new THREE.CylinderGeometry(br * 1.26, br * 1.3, 0.2, seg), 0.24);
  const muzzle = along(new THREE.LatheGeometry([[br * 0.86, 0.06], [br * 1.3, 0.06], [br * 1.36, 0], [br * 1.3, -0.12], [br * 1.06, -0.14]].map(q => V2(q[0], q[1])), seg), bl - 0.04);
  const inner = along(new THREE.CircleGeometry(br * 0.88, seg).rotateX(-Math.PI / 2), bl - 0.06);
  const barrelG = vcGeo([[tube, (x, y, z, o) => o.copy(SV)], [collar, SVD], [muzzle, SVL], [inner, GR]]);
  // the glass dome the ink sits in: a sphere open at the bottom, meeting the collar
  const domeG = new THREE.SphereGeometry(1.12, HI ? 48 : 28, HI ? 32 : 18, 0, 6.2832, 0, 2.28); domeG.translate(0, -0.1, 0);
  return { baseG, barrelG, domeG, dir, tip: at(bl + 0.05) };
})();
const turDomeM = HI ? charMat(new THREE.MeshPhysicalMaterial({ color: 0xF2F6FF, transparent: true, opacity: 0.2, roughness: 0.04, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 2.4, depthWrite: false })) : new THREE.MeshToonMaterial({ color: 0xE4ECF8, gradientMap: grad, transparent: true, opacity: 0.17, depthWrite: false });
const turMetalM = toon(0xFFFFFF, { vertexColors: true, transparent: true }, { metalness: 0.85, roughness: 0.28, envMapIntensity: 1.3 });
''')
rep("function addTurret(V) { const g = new THREE.Group(); g.visible = false; const a = new THREE.Mesh(TURRET_RIG.baseG, rigSolidM), bg = new THREE.Group(), b = new THREE.Mesh(TURRET_RIG.barrelG, rigSolidM); a.castShadow = b.castShadow = true; a.renderOrder = b.renderOrder = 31; bg.add(b); g.add(a); g.add(bg); V.body.add(g); V.tur = g; V.turBarrel = bg; }",
    "function addTurret(V) { const g = new THREE.Group(); g.visible = false; const a = new THREE.Mesh(TURRET_RIG.baseG, turMetalM), bg = new THREE.Group(), b = new THREE.Mesh(TURRET_RIG.barrelG, turMetalM), d = new THREE.Mesh(TURRET_RIG.domeG, turDomeM); a.castShadow = b.castShadow = true; a.renderOrder = b.renderOrder = 31; d.renderOrder = 44; bg.add(b); g.add(a); g.add(bg); g.add(d); V.body.add(g); V.tur = g; V.turBarrel = bg; }")
# the pick-up on the stage: the same base, nozzle and dome, with a bead of ink inside
rep("  else if (type === 'turret') { const t = new THREE.Group(); t.position.y = -0.12; t.scale.setScalar(0.72); spin.add(t); for (const geo of [TURRET_RIG.baseG, TURRET_RIG.barrelG]) { const o = new THREE.Mesh(geo, rigSolidM); o.castShadow = true; t.add(o); const h = new THREE.Mesh(geo, outlineMat); h.scale.setScalar(1.12); t.add(h); } eyes = t; }",
    "  else if (type === 'turret') { const t = new THREE.Group(); t.position.y = -0.12; t.scale.setScalar(0.72); spin.add(t); for (const geo of [TURRET_RIG.baseG, TURRET_RIG.barrelG]) { const o = new THREE.Mesh(geo, turMetalM); o.castShadow = true; t.add(o); const h = new THREE.Mesh(geo, outlineMat); h.scale.setScalar(1.12); t.add(h); }\n    const ink = new THREE.Mesh(new THREE.SphereGeometry(0.82, 22, 16), puIconMat); ink.position.y = -0.2; ink.scale.set(1, 0.82, 1); t.add(ink); const d = new THREE.Mesh(TURRET_RIG.domeG, turDomeM); d.renderOrder = 44; t.add(d); eyes = t; }")

# with the slime model the rig used to step aside for the pack's own turret form; now the base, dome and nozzle show round it
rep("  if (V.tur) V.tur.visible = false;\n", "  if (V.tur) V.tur.visible = !!D.turret && D.st === 'play' && (V.turK || 0) > 0.02;\n")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
