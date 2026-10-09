import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
rep("function addSplat(cx, cy, cz, yaw, R, t, small, round, team, stretch) {\n  team = team || 0; stretch = stretch || 0;",
r"""// ---------- splashes up the sides of trees, pillars, walls and gravestones: just for looks, they never count as coverage ----------
const SPL_MAX = 700, splTeam = new Uint8Array(SPL_MAX), splDummy = new THREE.Object3D(), splTmp = new THREE.Color();
const splG = (() => {
  const sh = new THREE.Shape(), n = 28;
  for (let i = 0; i <= n; i++) { const a = i / n * 6.2832, r = 0.5 * (0.8 + 0.16 * Math.sin(a * 5 + 1.3) + 0.07 * Math.sin(a * 11 + 0.4)); i ? sh.lineTo(Math.cos(a) * r, Math.sin(a) * r) : sh.moveTo(Math.cos(a) * r, Math.sin(a) * r); }
  const parts = [new THREE.ShapeGeometry(sh)];
  for (const [x, len, w] of [[-0.17, 0.5, 0.075], [0.1, 0.32, 0.06], [0.26, 0.18, 0.05]]) { parts.push(new THREE.PlaneGeometry(w, len).translate(x, -0.32 - len / 2, 0), new THREE.CircleGeometry(w * 0.72, 10).translate(x, -0.32 - len, 0)); }
  for (const [x, y, r] of [[0.48, 0.22, 0.07], [-0.5, 0.12, 0.05], [0.12, 0.56, 0.06]]) parts.push(new THREE.CircleGeometry(r, 10).translate(x, y, 0)); // a few flecks thrown past the edge
  return mergeGeos(parts);
})();
const splIM = new THREE.InstancedMesh(splG, toon(0xFFFFFF, { side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 }), SPL_MAX);
splIM.count = 0; splIM.frustumCulled = false; splIM.receiveShadow = true; splIM.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
splIM.instanceColor = new THREE.BufferAttribute(new Float32Array(SPL_MAX * 3), 3); splIM.instanceColor.setUsage(THREE.DynamicDrawUsage); scene.add(splIM);
let splN = 0, splHead = 0;
const splCol = t => { splTmp.set(TEAMS[t % 3].wet); if (t >= 3) splTmp.lerp(COLW, 0.45); return splTmp; }, COLW = new THREE.Color(0xFFFFFF);
function putSplash(x, y, z, nx, nz, sc, t) {
  const i = splHead; splHead = (splHead + 1) % SPL_MAX; if (splN < SPL_MAX) splN++;
  splDummy.position.set(x + nx * 0.014, y, z + nz * 0.014); splDummy.rotation.set(0, Math.atan2(nx, nz), (Math.random() - 0.5) * 0.45);
  splDummy.scale.set(sc * (Math.random() < 0.5 ? -1 : 1) * (0.85 + Math.random() * 0.3), sc * (0.85 + Math.random() * 0.3), 1); splDummy.updateMatrix();
  splIM.setMatrixAt(i, splDummy.matrix); splTeam[i] = t; splCol(t).toArray(splIM.instanceColor.array, i * 3);
  splIM.count = splN; splIM.instanceMatrix.needsUpdate = true; splIM.instanceColor.needsUpdate = true;
}
function recolorSplashes() { for (let i = 0; i < splN; i++) splCol(splTeam[i]).toArray(splIM.instanceColor.array, i * 3); splIM.instanceColor.needsUpdate = true; }
function clearSplashes() { splN = 0; splHead = 0; splIM.count = 0; }
function splashObjects(cx, cy, cz, R, t) {
  const reach = R + 0.55, seen = new Set(), tree = TH && TH.id === 'garden';
  for (let gx = cx - reach; gx <= cx + reach + QG_C; gx += QG_C) for (let gz = cz - reach; gz <= cz + reach + QG_C; gz += QG_C) for (const b of qcell(qgB, Math.min(gx, cx + reach), Math.min(gz, cz + reach))) {
    if (seen.has(b)) continue; seen.add(b);
    if (b[4] > 0.05 || b[5] < cy + 0.25) continue; // standing pieces with some wall above the splash
    const circ = b[6] === 'c'; let px, pz, nx, nz, dist, rr = 0, ox = 0, oz = 0;
    if (circ) { ox = (b[0] + b[1]) / 2; oz = (b[2] + b[3]) / 2; rr = (b[1] - b[0]) / 2; const dx = cx - ox, dz = cz - oz, d = Math.hypot(dx, dz) || 1e-3; nx = dx / d; nz = dz / d; px = ox + nx * rr; pz = oz + nz * rr; dist = d - rr; }
    else { const qx = clamp(cx, b[0], b[1]), qz = clamp(cz, b[2], b[3]), dx = cx - qx, dz = cz - qz; dist = Math.hypot(dx, dz); if (dist < 1e-3) continue; if (Math.abs(dx) > Math.abs(dz)) { nx = Math.sign(dx); nz = 0; } else { nx = 0; nz = Math.sign(dz); } px = qx; pz = qz; }
    if (dist > reach || dist < -0.05) continue;
    const k = 1 - Math.max(0, dist) / reach, n = Math.max(1, Math.round((0.6 + R * 0.8) * k)), wallTop = b[6] === 'g' ? b[5] - Math.max(b[1] - b[0], b[3] - b[2]) / 2 : b[5] - 0.12;
    for (let i = 0; i < n; i++) {
      const along = (Math.random() - 0.5) * Math.min(R * 1.3, 1.8);
      let x, z, fx = nx, fz = nz;
      if (circ) { const a = Math.atan2(nx, nz) + along / Math.max(0.3, rr); fx = Math.sin(a); fz = Math.cos(a); x = ox + fx * rr; z = oz + fz * rr; }
      else { x = clamp(px - nz * along, b[0], b[1]); z = clamp(pz + nx * along, b[2], b[3]); }
      const y = Math.min(wallTop - 0.1, cy + 0.2 + Math.random() * (0.35 + 0.45 * R * k));
      if (y < cy + 0.12) continue;
      putSplash(x, y, z, fx, fz, (0.28 + 0.32 * Math.random()) * (0.65 + 0.5 * k) * Math.min(1.5, 0.55 + R * 0.25), t);
    }
    // a big splash reaches the leaves of a tree too
    if (tree && b[7] === 'column' && R > 2 && dist < R * 0.8) for (let i = 0; i < 2; i++) { const a = Math.atan2(nx, nz) + (Math.random() - 0.5) * 1.2, fr = rr * 2.1; putSplash(ox + Math.sin(a) * fr, b[5] + 0.35 + Math.random() * 0.4, oz + Math.cos(a) * fr, Math.sin(a), Math.cos(a), 0.4 + 0.25 * Math.random(), t); }
  }
}
function addSplat(cx, cy, cz, yaw, R, t, small, round, team, stretch) {
  team = team || 0; stretch = stretch || 0;
  if (!small) splashObjects(cx, cy, cz, R, team);""")
rep("function clearTrail() {\n  nP = 0;", "function clearTrail() {\n  clearSplashes(); nP = 0;")
open(F, 'w').write(s)
print('ok')
