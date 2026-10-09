import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# ---------- particles: every plain solid color shares one instanced draw (colored per instance) ----------
rep("""const PART_CAP = 480, partPools = new Map(), partDummy = new THREE.Object3D();
function partPool(mat) {
  let pl = partPools.get(mat); if (pl) return pl;
  const im = new THREE.InstancedMesh(partG, mat, PART_CAP); im.count = 0; im.frustumCulled = false; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); if (mat.transparent) im.renderOrder = 8; scene.add(im);
  pl = { im, items: [] }; partPools.set(mat, pl); return pl;
}
function spawnPart(x, y, z, vx, vy, vz, life, mat, sz, grav) {
  const pl = partPool(mat || splashMat); if (pl.items.length >= PART_CAP) pl.items.shift();
  pl.items.push({ x, y, z, vx, vy, vz, life, sz: sz || 1, grav: grav === undefined ? 1 : grav, rest: false });
}""", """const PART_CAP = 480, partPools = new Map(), poolList = [], partDummy = new THREE.Object3D();
function newPool(mat, cap, shared) {
  const im = new THREE.InstancedMesh(partG, mat, cap); im.count = 0; im.visible = false; im.frustumCulled = false; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); if (mat.transparent) im.renderOrder = 8;
  if (shared) { im.instanceColor = new THREE.BufferAttribute(new Float32Array(cap * 3), 3); im.instanceColor.setUsage(THREE.DynamicDrawUsage); }
  scene.add(im); const pl = { im, items: [], cap, shared }; poolList.push(pl); return pl;
}
function partPool(mat) {
  let pl = partPools.get(mat); if (pl) return pl;
  const key = !mat.transparent && !mat.map ? (mat.isMeshToonMaterial ? 'toon' : mat.isMeshBasicMaterial ? 'basic' : null) : null;
  if (key) { pl = partPools.get(key); if (!pl) { pl = newPool(key === 'toon' ? toon(0xFFFFFF) : new THREE.MeshBasicMaterial({ color: 0xFFFFFF }), PART_CAP * 3, true); partPools.set(key, pl); } }
  else pl = newPool(mat, PART_CAP, false);
  partPools.set(mat, pl); return pl;
}
function spawnPart(x, y, z, vx, vy, vz, life, mat, sz, grav) {
  const m = mat || splashMat, pl = partPool(m); if (pl.items.length >= pl.cap) pl.items.shift();
  pl.items.push({ x, y, z, vx, vy, vz, life, sz: sz || 1, grav: grav === undefined ? 1 : grav, rest: false, col: m.color });
}""")
rep("  for (const pl of partPools.values()) {\n    const it = pl.items; let n = 0;", "  for (const pl of poolList) {\n    const it = pl.items, ca = pl.shared ? pl.im.instanceColor.array : null; let n = 0;")
rep("      partDummy.updateMatrix(); pl.im.setMatrixAt(n, partDummy.matrix); it[n++] = p;\n    }\n    it.length = n; pl.im.count = n; pl.im.visible = n > 0; if (n) pl.im.instanceMatrix.needsUpdate = true;",
    "      partDummy.updateMatrix(); pl.im.setMatrixAt(n, partDummy.matrix); if (ca) { ca[n * 3] = p.col.r; ca[n * 3 + 1] = p.col.g; ca[n * 3 + 2] = p.col.b; } it[n++] = p;\n    }\n    it.length = n; pl.im.count = n; pl.im.visible = n > 0;\n    if (n) { const mA = pl.im.instanceMatrix; mA.updateRange.offset = 0; mA.updateRange.count = n * 16; mA.needsUpdate = true; if (ca) { const cA = pl.im.instanceColor; cA.updateRange.offset = 0; cA.updateRange.count = n * 3; cA.needsUpdate = true; } }")
rep("partPools.forEach(pl => { pl.items.length = 0; pl.im.count = 0; })", "poolList.forEach(pl => { pl.items.length = 0; pl.im.count = 0; pl.im.visible = false; })")
rep("...[...partPools.values()].map(pl => pl.im)", "...poolList.map(pl => pl.im)")
open(F, 'w').write(s)
print('ok')
