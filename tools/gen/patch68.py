import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# ---------- sky clouds: a handful of shapes drawn as instances (5 draws instead of 30) ----------
rep("""  for (let i = 0; i < 18; i++) { const m = new THREE.Mesh(cloudGeo(4 + (r() * 3 | 0), 5 + r() * 4), cloudMat); m.position.set(-150 + r() * 300, -27 - r() * 10, -150 + r() * 300); m.rotation.y = r() * 6.28; scene.add(m); clouds.push({ m, v: 0.5 + r() * 0.6 }); }
  for (let i = 0; i < 12; i++) { const a = r() * 6.283, d = 62 + r() * 70, m = new THREE.Mesh(cloudGeo(3 + (r() * 3 | 0), 3 + r() * 3), cloudMat); m.position.set(Math.cos(a) * d, -8 + r() * 26, Math.sin(a) * d); m.rotation.y = r() * 6.28; scene.add(m); clouds.push({ m, v: 0.9 + r() * 0.8 }); }""",
"""  const CV = [3, 4, 5, 6, 5].map(n => cloudGeo(n, 1)), cvN = new Array(CV.length).fill(0), pick = [];
  const addCloud = (vi, x, y, z, ry, sc, v) => { const m = new THREE.Object3D(); m.position.set(x, y, z); m.rotation.y = ry; m.scale.setScalar(sc); clouds.push({ m, v, vi, k: cvN[vi]++ }); };
  for (let i = 0; i < 18; i++) { const vi = (r() * CV.length) | 0, sc = 5 + r() * 4; addCloud(vi, -150 + r() * 300, -27 - r() * 10, -150 + r() * 300, r() * 6.28, sc, 0.5 + r() * 0.6); }
  for (let i = 0; i < 12; i++) { const vi = (r() * 4) | 0, a = r() * 6.283, d = 62 + r() * 70, sc = 3 + r() * 3; addCloud(vi, Math.cos(a) * d, -8 + r() * 26, Math.sin(a) * d, r() * 6.28, sc, 0.9 + r() * 0.8); }
  cloudIMs = CV.map((g, vi) => { const im = new THREE.InstancedMesh(g, cloudMat, Math.max(1, cvN[vi])); im.count = cvN[vi]; im.frustumCulled = false; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(im); return im; });
  for (const c of clouds) { c.m.updateMatrix(); cloudIMs[c.vi].setMatrixAt(c.k, c.m.matrix); }""")
rep("const cloudMat = toon(0xD9D4F2), clouds = [], islands = [];", "const cloudMat = toon(0xD9D4F2), clouds = [], islands = []; let cloudIMs = [];")
rep("  for (const c of clouds) { c.m.position.x += c.v * dt; if (c.m.position.x > 160) c.m.position.x -= 320; }",
    "  for (const c of clouds) { c.m.position.x += c.v * dt; if (c.m.position.x > 160) c.m.position.x -= 320; c.m.updateMatrix(); cloudIMs[c.vi].setMatrixAt(c.k, c.m.matrix); }\n  for (const im of cloudIMs) im.instanceMatrix.needsUpdate = true;")
# ---------- far canvases: the box is three draws, and all its splats one (colored per vertex) ----------
rep("    g.add(new THREE.Mesh(bg, [woodMat, woodMat, canvasMat, woodDarkMat, woodMat, woodMat]));",
    "    { const ms = [woodMat, woodMat, canvasMat, woodDarkMat, woodMat, woodMat]; g.add(new THREE.Mesh(bg, regroup(bg, ms))); }")
rep("    for (const col in splatList) g.add(new THREE.Mesh(mergeGeos(splatList[col]), toon(+col)));",
    """    { const parts = []; for (const col in splatList) for (const sg of splatList[col]) parts.push([sg.index ? sg.toNonIndexed() : sg, new THREE.Color(+col)]);
      let n = 0; for (const [sg] of parts) n += sg.attributes.position.count; const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), colA = new Float32Array(n * 3); let o = 0;
      for (const [sg, c] of parts) { const k = sg.attributes.position.count; pos.set(sg.attributes.position.array, o * 3); nor.set(sg.attributes.normal.array, o * 3); for (let q = 0; q < k; q++) { colA[(o + q) * 3] = c.r; colA[(o + q) * 3 + 1] = c.g; colA[(o + q) * 3 + 2] = c.b; } o += k; }
      const mg = new THREE.BufferGeometry(); mg.setAttribute('position', new THREE.BufferAttribute(pos, 3)); mg.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); mg.setAttribute('color', new THREE.BufferAttribute(colA, 3));
      g.add(new THREE.Mesh(mg, toon(0xFFFFFF, { vertexColors: true }))); }""")
open(F, 'w').write(s)
print('ok')
