import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# drop-off edges (the canvas rim and every hole) are white with a dark outline, so you can see where you'd roll off
rep("const lineMat = new THREE.MeshBasicMaterial({ color: C.outline });",
    "const lineMat = new THREE.MeshBasicMaterial({ color: C.outline });\nconst edgeMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });")
rep("const V = (x, y, z) => new THREE.Vector3(x, y, z), lines = [], hulls = [], frame = [], bag = new Map();",
    "const V = (x, y, z) => new THREE.Vector3(x, y, z), lines = [], hulls = [], frame = [], edges = [], bag = new Map();\n  const EDGE_T = 0.13, edge = (a, b) => { edges.push(beamGeo(a, b, EDGE_T)); hulls.push(beamGeo(a, b, EDGE_T + 0.07)); };")
rep("  const ring = (cx, cz, r, y, t) => { const n = 36; for (let k = 0; k < n; k++) { const a0 = k / n * 6.2832, a1 = (k + 1) / n * 6.2832; lines.push(beamGeo(V(cx + Math.cos(a0) * r, y, cz + Math.sin(a0) * r), V(cx + Math.cos(a1) * r, y, cz + Math.sin(a1) * r), t)); } };",
    "  const ring = (cx, cz, r, y, t) => { const n = 36; for (let k = 0; k < n; k++) { const a0 = k / n * 6.2832, a1 = (k + 1) / n * 6.2832, p0 = V(cx + Math.cos(a0) * r, y, cz + Math.sin(a0) * r), p1 = V(cx + Math.cos(a1) * r, y, cz + Math.sin(a1) * r); if (t === 'edge') edge(p0, p1); else lines.push(beamGeo(p0, p1, t)); } };")
rep("  const rect = (x0, x1, z0, z1, y, t) => { lines.push(beamGeo(V(x0, y, z0), V(x1, y, z0), t), beamGeo(V(x1, y, z0), V(x1, y, z1), t), beamGeo(V(x1, y, z1), V(x0, y, z1), t), beamGeo(V(x0, y, z1), V(x0, y, z0), t)); };\n  rect(-ARENA, ARENA, -ARENA, ARENA, 0, 0.09);",
    "  const rect = (x0, x1, z0, z1, y, t) => { const c = [[x0, z0, x1, z0], [x1, z0, x1, z1], [x1, z1, x0, z1], [x0, z1, x0, z0]]; for (const [ax, az, bx, bz] of c) { if (t === 'edge') edge(V(ax, y, az), V(bx, y, bz)); else lines.push(beamGeo(V(ax, y, az), V(bx, y, bz), t)); } };\n  rect(-ARENA, ARENA, -ARENA, ARENA, 0, 'edge');")
rep("HOLES.forEach(h => h[6] === 'c' ? ring((h[0] + h[1]) / 2, (h[2] + h[3]) / 2, (h[1] - h[0]) / 2, 0, 0.09) : rect(h[0], h[1], h[2], h[3], 0, 0.09));",
    "HOLES.forEach(h => h[6] === 'c' ? ring((h[0] + h[1]) / 2, (h[2] + h[3]) / 2, (h[1] - h[0]) / 2, 0, 'edge') : rect(h[0], h[1], h[2], h[3], 0, 'edge'));")
rep("  stageGroup.add(new THREE.Mesh(mergeGeos(lines), lineMat));\n",
    "  stageGroup.add(new THREE.Mesh(mergeGeos(lines), lineMat));\n  if (edges.length) stageGroup.add(new THREE.Mesh(mergeGeos(edges), edgeMat));\n")
open(F, 'w').write(s)
print('ok')
