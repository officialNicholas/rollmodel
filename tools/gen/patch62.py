import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# replace the beam edges with continuous bands: white on the floor and down the wall, a dark hairline outside it
rep("const edgeMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });",
    "const edgeMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF, side: THREE.DoubleSide, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6 });\nconst edgeLineMat = new THREE.MeshBasicMaterial({ color: C.outline, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -5, polygonOffsetUnits: -5 });")
rep("  const EDGE_T = 0.13, edge = (a, b) => { edges.push(beamGeo(a, b, EDGE_T)); hulls.push(beamGeo(a, b, EDGE_T + 0.07)); };",
    """  const EDGE_W = 0.17, EDGE_D = 0.16, EDGE_O = 0.06, edgeLn = [];
  // a flat frame on the floor between two outlines (shape coords are x, -z, like the floor)
  const band = (outer, inner, list) => { const sh = new THREE.Shape(); outer.forEach(([x, z], i) => i ? sh.lineTo(x, -z) : sh.moveTo(x, -z)); const ph = new THREE.Path(); inner.slice().reverse().forEach(([x, z], i) => i ? ph.lineTo(x, -z) : ph.moveTo(x, -z)); sh.holes.push(ph); const g = new THREE.ShapeGeometry(sh); g.rotateX(-Math.PI / 2); g.translate(0, 0.004, 0); list.push(g); };
  const box4 = (x0, x1, z0, z1) => [[x0, z0], [x1, z0], [x1, z1], [x0, z1]], circ = (cx, cz, r) => { const p = []; for (let k = 0; k < 56; k++) { const a = k / 56 * 6.2832; p.push([cx + Math.cos(a) * r, cz + Math.sin(a) * r]); } return p; };
  const lip = pts => { const P2 = []; for (let i = 0; i < pts.length; i++) { const [ax, az] = pts[i], [bx, bz] = pts[(i + 1) % pts.length]; P2.push(ax, 0.004, az, bx, 0.004, bz, bx, -EDGE_D, bz, ax, 0.004, az, bx, -EDGE_D, bz, ax, -EDGE_D, az); } const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P2, 3)); edges.push(g); };
  const holeEdge = h => { if (h[6] === 'c') { const cx = (h[0] + h[1]) / 2, cz = (h[2] + h[3]) / 2, r = (h[1] - h[0]) / 2; band(circ(cx, cz, r + EDGE_W), circ(cx, cz, r), edges); band(circ(cx, cz, r + EDGE_W + EDGE_O), circ(cx, cz, r + EDGE_W), edgeLn); lip(circ(cx, cz, r - 0.012)); }
    else { const [x0, x1, z0, z1] = h, e = EDGE_W, o = EDGE_W + EDGE_O; band(box4(x0 - e, x1 + e, z0 - e, z1 + e), box4(x0, x1, z0, z1), edges); band(box4(x0 - o, x1 + o, z0 - o, z1 + o), box4(x0 - e, x1 + e, z0 - e, z1 + e), edgeLn); lip(box4(x0 + 0.012, x1 - 0.012, z0 + 0.012, z1 - 0.012)); } };
  const rimEdge = () => { const A = ARENA, e = A - EDGE_W, o = A - EDGE_W - EDGE_O; band(box4(-A, A, -A, A), box4(-e, e, -e, e), edges); band(box4(-e, e, -e, e), box4(-o, o, -o, o), edgeLn); lip(box4(-A - 0.012, A + 0.012, -A - 0.012, A + 0.012)); };""")
rep("  const ring = (cx, cz, r, y, t) => { const n = 36; for (let k = 0; k < n; k++) { const a0 = k / n * 6.2832, a1 = (k + 1) / n * 6.2832, p0 = V(cx + Math.cos(a0) * r, y, cz + Math.sin(a0) * r), p1 = V(cx + Math.cos(a1) * r, y, cz + Math.sin(a1) * r); if (t === 'edge') edge(p0, p1); else lines.push(beamGeo(p0, p1, t)); } };",
    "  const ring = (cx, cz, r, y, t) => { const n = 36; for (let k = 0; k < n; k++) { const a0 = k / n * 6.2832, a1 = (k + 1) / n * 6.2832; lines.push(beamGeo(V(cx + Math.cos(a0) * r, y, cz + Math.sin(a0) * r), V(cx + Math.cos(a1) * r, y, cz + Math.sin(a1) * r), t)); } };")
rep("  const rect = (x0, x1, z0, z1, y, t) => { const c = [[x0, z0, x1, z0], [x1, z0, x1, z1], [x1, z1, x0, z1], [x0, z1, x0, z0]]; for (const [ax, az, bx, bz] of c) { if (t === 'edge') edge(V(ax, y, az), V(bx, y, bz)); else lines.push(beamGeo(V(ax, y, az), V(bx, y, bz), t)); } };\n  rect(-ARENA, ARENA, -ARENA, ARENA, 0, 'edge');",
    "  const rect = (x0, x1, z0, z1, y, t) => { lines.push(beamGeo(V(x0, y, z0), V(x1, y, z0), t), beamGeo(V(x1, y, z0), V(x1, y, z1), t), beamGeo(V(x1, y, z1), V(x0, y, z1), t), beamGeo(V(x0, y, z1), V(x0, y, z0), t)); };\n  rimEdge();")
rep("HOLES.forEach(h => h[6] === 'c' ? ring((h[0] + h[1]) / 2, (h[2] + h[3]) / 2, (h[1] - h[0]) / 2, 0, 'edge') : rect(h[0], h[1], h[2], h[3], 0, 'edge'));",
    "HOLES.forEach(holeEdge);")
rep("  if (edges.length) stageGroup.add(new THREE.Mesh(mergeGeos(edges), edgeMat));\n",
    "  if (edges.length) { const em = new THREE.Mesh(mergeGeos(edges), edgeMat), el = new THREE.Mesh(mergeGeos(edgeLn), edgeLineMat); em.renderOrder = 12; el.renderOrder = 11; stageGroup.add(em, el); }\n")
open(F, 'w').write(s)
print('ok')
