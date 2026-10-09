# the turret: a little faster, more shots, and the shots are blobs of paint in flight (a round front, a tail breaking up into little
# spikes behind it), all drawn in two calls however many are flying
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

rep("const TURRET_T = 7, TURRET_RATE = 0.16, TURRET_NEAR = 4, TURRET_FAR = 19, SHOT_V = 15,", "const TURRET_T = 7, TURRET_RATE = 0.12, TURRET_NEAR = 4, TURRET_FAR = 19, SHOT_V = 16.5,")

OLD = src[src.index("// paint shots: glossy globs in the shooter's color, a few of each made up front so nothing compiles mid-match"):src.index("// where a rocket will come down: a target on the ground everyone can see")]
NEW = r"""// paint shots: blobs of paint in flight, in the shooter's color. Each is a round front with a tail tapering behind it that breaks up into
// little spikes; all of them are drawn in one go (and their outlines in another), however many are flying
const SHOT_N = 72, SHOT_SC = 0.2, shots = [];
const shotGeo = (() => {
  const prof = [], NR = HI ? 14 : 10, R = rng(77);
  for (let i = 0; i <= 8; i++) { const a = i / 8 * Math.PI / 2; prof.push(new THREE.Vector2(Math.sin(a) * 1.0, Math.cos(a) * 1.0)); } // the round front (+y here, ahead once turned)
  for (let i = 1; i <= 9; i++) { const u = i / 9; prof.push(new THREE.Vector2(Math.max(0.001, Math.pow(1 - u, 1.35) * (1 - 0.15 * u)), -u * 1.75)); } // the tail, to a point
  const parts = [new THREE.LatheGeometry(prof.reverse(), NR)];
  // the spikes: thin cones off the back half, swept back and out like paint tearing away
  for (let k = 0; k < 7; k++) { const a = k / 7 * 6.2832 + R() * 0.5, back = 0.25 + R() * 0.65, len = 0.5 + R() * 0.55, rb = 0.1 + R() * 0.08;
    const g = new THREE.ConeGeometry(rb, len, HI ? 6 : 5, 1, true); g.translate(0, len / 2, 0);
    const dir = new THREE.Vector3(Math.cos(a) * (0.55 + R() * 0.35), -1, Math.sin(a) * (0.55 + R() * 0.35)).normalize(); g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(YAX, dir));
    const r0 = Math.max(0.12, Math.pow(1 - back / 1.75, 1.35) * 0.8); g.translate(Math.cos(a) * r0, -back, Math.sin(a) * r0); parts.push(g); }
  // and two drops come loose behind it
  for (let k = 0; k < 2; k++) { const g = new THREE.IcosahedronGeometry(0.16 - k * 0.04, 0), a = 1 + k * 2.6; g.translate(Math.cos(a) * 0.35, -2.05 - k * 0.45, Math.sin(a) * 0.35); parts.push(g); }
  const g = mergeGeos(parts.map(p => { const q = p.index ? p.toNonIndexed() : p; q.deleteAttribute('uv'); q.computeVertexNormals(); return q; }));
  return g.rotateX(Math.PI / 2); // nose along +z
})();
const shotIM = new THREE.InstancedMesh(shotGeo, glossMat(0xFFFFFF), SHOT_N), shotInkM = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });
shotInkM.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <begin_vertex>', 'vec3 transformed = position + normal * 0.2;'); }; shotInkM.customProgramCacheKey = () => 'shot-ink';
const shotInk = new THREE.InstancedMesh(shotGeo, shotInkM, SHOT_N);
for (const im of [shotIM, shotInk]) { im.frustumCulled = false; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); im.count = 1; im.visible = false; im.renderOrder = im === shotIM ? 33 : 32.6; scene.add(im); }
shotIM.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(SHOT_N * 3).fill(1), 3); shotIM.instanceColor.setUsage(THREE.DynamicDrawUsage); shotIM.castShadow = true;
{ const z = new THREE.Matrix4().makeScale(0, 0, 0); shotIM.setMatrixAt(0, z); shotInk.setMatrixAt(0, z); } // (one hidden one, so the shaders are made with everything else)
const shotDummy = new THREE.Object3D();
function drawShots() {
  const n = Math.min(SHOT_N, shots.length), ca = shotIM.instanceColor.array;
  for (let i = 0; i < n; i++) {
    const s = shots[i], v = Math.hypot(s.vx, s.vy, s.vz), w = 1 + 0.13 * Math.sin(clock * 34 + s.ph), st = 1 + Math.min(0.5, v * 0.022);
    shotDummy.position.set(s.x, s.y, s.z); tv1.set(s.x + s.vx, s.y + s.vy, s.z + s.vz); shotDummy.lookAt(tv1); shotDummy.rotateZ(s.ph + clock * s.spin);
    shotDummy.scale.set(SHOT_SC * w, SHOT_SC / w, SHOT_SC * st); shotDummy.updateMatrix(); shotIM.setMatrixAt(i, shotDummy.matrix); shotInk.setMatrixAt(i, shotDummy.matrix);
    const c = TEAM_COLS[s.team]; ca[i * 3] = c.r; ca[i * 3 + 1] = c.g; ca[i * 3 + 2] = c.b;
  }
  const on = n > 0; shotIM.visible = shotInk.visible = on; if (!on) return;
  shotIM.count = shotInk.count = n; shotIM.instanceMatrix.needsUpdate = shotInk.instanceMatrix.needsUpdate = true; shotIM.instanceColor.needsUpdate = true;
}
"""
src = src.replace(OLD, NEW)
# firing: no mesh per shot, a spin and a wobble of its own; fewer sparks at the mouth now it fires faster
rep("  const hv = d / tf, m = shotMesh(D.team); m.visible = true;\n  shots.push({ x: x0, y: y0, z: z0, vx: Math.sin(a) * hv, vy, vz: Math.cos(a) * hv, by: D, m, life: 4, acc: 0 });",
    "  const hv = d / tf;\n  shots.push({ x: x0, y: y0, z: z0, vx: Math.sin(a) * hv, vy, vz: Math.cos(a) * hv, by: D, team: D.team, life: 4, acc: 0, ph: Math.random() * 6.28, spin: (Math.random() < 0.5 ? -1 : 1) * (3 + Math.random() * 4) });")
rep("  for (let i = 0; i < 5; i++) spawnPart(x0, y0, z0, Math.sin(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.5 + Math.random() * 1.5, Math.cos(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.22, tmat(D), 0.45);",
    "  for (let i = 0; i < 3; i++) spawnPart(x0, y0, z0, Math.sin(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.5 + Math.random() * 1.5, Math.cos(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.22, tmat(D), 0.4);")
# in flight: a drop shed now and then (the blob's own shape does most of the work now)
rep("    s.acc += dt; if (s.acc > 0.035) { s.acc = 0; spawnPart(s.x, s.y, s.z, s.vx * 0.05 + (Math.random() - 0.5), s.vy * 0.05, s.vz * 0.05 + (Math.random() - 0.5), 0.28, tmat(s.by), 0.32); }",
    "    s.acc += dt; if (s.acc > 0.075) { s.acc = 0; spawnPart(s.x - s.vx * 0.02, s.y - s.vy * 0.02, s.z - s.vz * 0.02, s.vx * 0.05 + (Math.random() - 0.5), s.vy * 0.05, s.vz * 0.05 + (Math.random() - 0.5), 0.26, tmat(s.by), 0.26); }")
rep("    if (gone) { s.m.visible = false; shots.splice(i, 1); }", "    if (gone) shots.splice(i, 1);")
rep("  for (const sh of shots) sh.m.visible = false; shots.length = 0;", "  shots.length = 0; drawShots();")
rep("  for (const sh of shots) { const m = sh.m, v = Math.hypot(sh.vx, sh.vy, sh.vz), w = 1 + 0.1 * Math.sin(clock * 40 + sh.life * 9); m.position.set(sh.x, sh.y, sh.z); tv1.set(sh.x + sh.vx, sh.y + sh.vy, sh.z + sh.vz); m.lookAt(tv1); m.scale.set(0.24 * w, 0.24 / w, 0.24 * (1 + v * 0.028)); }",
    "  drawShots();")
open(P, 'w').write(src)
print('ok')
