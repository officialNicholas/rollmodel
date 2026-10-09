import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# remember where the canopies (and the little bushes around drums) are, so splashes can land on them
rep("const floaters = [];", "const floaters = [], treeTops = []; // treeTops: {x, y, z, r} of each leafy ball (flattened to 0.8 tall)")
rep("  floaters.length = 0; flames.length = 0;", "  floaters.length = 0; flames.length = 0; treeTops.length = 0;")
rep("put(k % 2 ? M.leaf : M.leaf2, ball(rad * (2.1 + R() * 0.6), cx + Math.cos(a) * rr, top + 0.5 + k * 0.55, cz + Math.sin(a) * rr, 0.8)); } }",
    "const br = rad * (2.1 + R() * 0.6), bx = cx + Math.cos(a) * rr, by = top + 0.5 + k * 0.55, bz = cz + Math.sin(a) * rr; put(k % 2 ? M.leaf : M.leaf2, ball(br, bx, by, bz, 0.8)); treeTops.push({ x: bx, y: by, z: bz, r: br }); } }")
# splash decal with any facing (for round canopies)
rep("function recolorSplashes() {", """function putSplashN(x, y, z, nx, ny, nz, sc, t) {
  const i = splHead; splHead = (splHead + 1) % SPL_MAX; if (splN < SPL_MAX) splN++;
  splDummy.position.set(x + nx * 0.03, y + ny * 0.03, z + nz * 0.03); splDummy.rotation.set(0, 0, 0); splDummy.lookAt(x + nx * 2, y + ny * 2, z + nz * 2); splDummy.rotateZ((Math.random() - 0.5) * 0.6);
  splDummy.scale.set(sc * (Math.random() < 0.5 ? -1 : 1) * (0.85 + Math.random() * 0.3), sc * (0.85 + Math.random() * 0.3), 1); splDummy.updateMatrix();
  splIM.setMatrixAt(i, splDummy.matrix); splTeam[i] = t; splCol(t).toArray(splIM.instanceColor.array, i * 3);
  splIM.count = splN; splIM.instanceMatrix.needsUpdate = true; splIM.instanceColor.needsUpdate = true;
}
function recolorSplashes() {""")
# canopies within reach and low enough for the splash to fly up to
rep("""  for (let gx = cx - reach; gx <= cx + reach + QG_C; gx += QG_C) for (let gz = cz - reach; gz <= cz + reach + QG_C; gz += QG_C) for (const b of qcell(qgB, Math.min(gx, cx + reach), Math.min(gz, cz + reach))) {
    if (seen.has(b)) continue; seen.add(b);
    if (b[4] > 0.05 || b[5] < cy + 0.25) continue; // standing pieces with some wall above the splash""",
"""  for (const tt of treeTops) {
    const dx = cx - tt.x, dz = cz - tt.z, dh = Math.hypot(dx, dz), dist = dh - tt.r;
    if (dist > reach || tt.y - tt.r * 0.8 - cy > up * 1.1 || tt.y + tt.r * 0.8 < cy) continue;
    const k = 1 - Math.max(0, dist) / reach, n = Math.round((1 + R * 1.7) * k * (0.8 + 0.4 * Math.random())), az0 = Math.atan2(dx, dz);
    for (let i = 0; i < n; i++) {
      // a point on the canopy facing the splash, mostly around its middle and underside where the paint flies up to
      const az = az0 + (Math.random() - 0.5) * 2.1, el = -0.45 + Math.random() * 0.85, ux = Math.sin(az) * Math.cos(el), uy = Math.sin(el), uz = Math.cos(az) * Math.cos(el);
      const t2 = 1 / Math.sqrt((ux / tt.r) ** 2 + (uy / (tt.r * 0.8)) ** 2 + (uz / tt.r) ** 2), px = ux * t2, py = uy * t2, pz = uz * t2;
      let nx = px / (tt.r * tt.r), ny = py / (0.64 * tt.r * tt.r), nz = pz / (tt.r * tt.r); const nl = Math.hypot(nx, ny, nz); nx /= nl; ny /= nl; nz /= nl;
      if (tt.y + py - cy > up * 1.15) continue;
      putSplashN(tt.x + px, tt.y + py, tt.z + pz, nx, ny, nz, Math.min(tt.r * 0.55, (0.35 + 0.35 * Math.random()) * Math.min(1.6, 0.6 + R * 0.25)), t);
    }
  }
  for (let gx = cx - reach; gx <= cx + reach + QG_C; gx += QG_C) for (let gz = cz - reach; gz <= cz + reach + QG_C; gz += QG_C) for (const b of qcell(qgB, Math.min(gx, cx + reach), Math.min(gz, cz + reach))) {
    if (seen.has(b)) continue; seen.add(b);
    if (b[4] > 0.05 || b[5] < cy + 0.25) continue; // standing pieces with some wall above the splash""")
open(F, 'w').write(s)
print('ok')
