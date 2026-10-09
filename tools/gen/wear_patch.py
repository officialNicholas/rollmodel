# Graphics mode accessories rebuilt in detail, each with a lighter copy for when its blob is small on screen, and a level-of-detail
# system for the blobs themselves (their jelly is the heaviest mesh in the game: a 96x72 sphere run through the goo shader 4 times a
# vertex, in up to five passes). Thresholds sit well below the point where the lighter mesh could show.
#  - witch hat: one smooth cone that bends over at the top with soft fabric ripples, a brim that curls up at the edge and waves a
#    little, a rounded band, a gold buckle
#  - horns: tapered, ridged at the base, curving back in to the tip (a mirrored pair)
#  - bat wings: a membrane with thickness and rounded edges, ribs on both faces
#  - halo: smooth, and bright enough to bloom
#  - fangs: curved, smooth; angry brows: rounded; happy-eye arcs: smooth
#  - a thin ink outline on the hat, horns and wings, the same width as the body's
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

BUILD = r"""
// ---------- Graphics mode accessories: smooth, detailed shapes, each with a lighter copy (swapped in when the blob is small on screen)
// rings round a spine in the xy plane: the ring radius is rad(t), the spine's heading turns by ang(t) (0 = straight up, + leans to +x)
function bentTube(len, rad, ang, nr, nl) {
  const pos = [], idx = []; let x = 0, y = 0; const ds = len / nl;
  for (let j = 0; j <= nl; j++) {
    const t = j / nl, a = ang(t), r = rad(t), nx = Math.cos(a), ny = -Math.sin(a);
    for (let i = 0; i < nr; i++) { const th = i / nr * Math.PI * 2, c = Math.cos(th), sn = Math.sin(th); pos.push(x + r * c * nx, y + r * c * ny, r * sn); }
    const am = ang(Math.min(1, t + 0.5 / nl)); x += Math.sin(am) * ds; y += Math.cos(am) * ds;
  }
  for (let j = 0; j < nl; j++) for (let i = 0; i < nr; i++) { const a = j * nr + i, a1 = j * nr + (i + 1) % nr, b = a + nr, b1 = a1 + nr; idx.push(a, b, a1, a1, b, b1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
// a profile [r, y] turned round the y axis, the seam welded so it shades smoothly; out = which way the first segment's normal should face
function latheW(prof, nr, out) {
  const pos = [], idx = [];
  for (const [r, y] of prof) for (let i = 0; i < nr; i++) { const th = i / nr * Math.PI * 2; pos.push(r * Math.cos(th), y, r * Math.sin(th)); }
  for (let j = 0; j < prof.length - 1; j++) for (let i = 0; i < nr; i++) { const a = j * nr + i, a1 = j * nr + (i + 1) % nr, b = a + nr, b1 = a1 + nr; idx.push(a, a1, b, a1, b1, b); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  if (out) { const n = g.attributes.normal; if (n.getX(0) * out[0] + n.getY(0) * out[1] + n.getZ(0) * out[2] < 0) { const ix = g.index.array; for (let k = 0; k < ix.length; k += 3) { const t = ix[k + 1]; ix[k + 1] = ix[k + 2]; ix[k + 2] = t; } g.computeVertexNormals(); } }
  return g;
}
const mirrorX = g => { const c = g.clone(); c.scale(-1, 1, 1); const ix = c.index.array; for (let k = 0; k < ix.length; k += 3) { const t = ix[k + 1]; ix[k + 1] = ix[k + 2]; ix[k + 2] = t; } c.computeVertexNormals(); return c; };
const HAT_L = 1.12, hatR = t => 0.405 * Math.pow(Math.max(0, 1 - t), 1.12) + 0.006, hatA = t => t < 0.42 ? 0 : 1.5 * Math.pow((t - 0.42) / 0.58, 1.7);
const hatRy = y => hatR(clamp((y - 0.04) / HAT_L, 0, 1));
const WEAR_G = HI ? (() => {
  const L = [0, 1].map(lo => {
    const q = lo ? 0.5 : 1, N = n => Math.max(6, Math.round(n * q));
    const cone = bentTube(HAT_L, t => hatR(t) * (1 + 0.035 * Math.sin(t * 21) * t * (1 - t) * 4), hatA, N(56), N(44)).translate(0, 0.04, 0);
    const brimP = [[0.33, 0.035], [0.45, 0.037], [0.58, 0.034], [0.68, 0.037], [0.745, 0.046], [0.79, 0.064], [0.812, 0.058], [0.818, 0.04], [0.806, 0.018], [0.78, 0.006], [0.68, 0.0], [0.5, 0.003], [0.33, 0.006]];
    const brim = latheW(brimP, N(96), [0, 1, 0]); { const P = brim.attributes.position; for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i), r = Math.hypot(x, z), th = Math.atan2(z, x), k = clamp((r - 0.42) / 0.4, 0, 1); P.setY(i, P.getY(i) + 0.03 * Math.sin(th * 3 + 0.6) * k * k); } brim.computeVertexNormals(); }
    const bandP = []; for (let k = 0; k <= 10; k++) { const u = k / 10, y = 0.045 + u * 0.145, e = Math.sin(u * Math.PI); bandP.push([hatRy(y) + 0.004 + 0.011 * Math.pow(e, 0.35), y]); }
    const band = latheW(bandP, N(56), [1, 0, 0]);
    const halo = new THREE.TorusGeometry(0.47, 0.058, N(24), N(128)).rotateX(Math.PI / 2);
    const horn = bentTube(0.4, t => 0.112 * Math.pow(Math.max(0, 1 - t), 0.85) * (1 + 0.06 * Math.cos(t * 30) * (1 - t) * (1 - t)) + 0.003, t => -0.85 * Math.pow(t, 1.5), N(28), N(26)).translate(0, -0.04, 0);
    const fang = latheW([[0.0005, -0.088], [0.007, -0.079], [0.014, -0.063], [0.02, -0.044], [0.026, -0.022], [0.03, 0]], N(20), [1, 0, 0]);
    return { cone, brim, band, halo, horn: [mirrorX(horn), horn], fang };
  });
  // the buckle: a rounded gold frame on the band's front, tipped back with the cone's slope
  const bk = new THREE.Shape(), hole = new THREE.Path(), rr = (p, w, h, r) => { p.moveTo(-w + r, -h); p.lineTo(w - r, -h); p.quadraticCurveTo(w, -h, w, -h + r); p.lineTo(w, h - r); p.quadraticCurveTo(w, h, w - r, h); p.lineTo(-w + r, h); p.quadraticCurveTo(-w, h, -w, h - r); p.lineTo(-w, -h + r); p.quadraticCurveTo(-w, -h, -w + r, -h); };
  rr(bk, 0.078, 0.066, 0.02); rr(hole, 0.042, 0.032, 0.01); bk.holes.push(hole);
  const buckle = new THREE.ExtrudeGeometry(bk, { depth: 0.018, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.006, bevelSegments: 2, curveSegments: 6 }); buckle.translate(0, 0, -0.009); buckle.rotateX(-Math.atan(0.405)); buckle.translate(0, 0.118, hatRy(0.118) + 0.024);
  // the wing: the old outline, given thickness and rounded edges; ribs on both faces
  const wsh = new THREE.Shape(); wsh.moveTo(0, 0.16); wsh.quadraticCurveTo(0.32, 0.6, 0.86, 0.52); wsh.lineTo(0.98, 0.4); wsh.quadraticCurveTo(0.86, 0.3, 0.8, 0.12); wsh.quadraticCurveTo(0.7, 0.26, 0.56, 0.06); wsh.quadraticCurveTo(0.44, 0.22, 0.3, 0.0); wsh.quadraticCurveTo(0.16, 0.14, 0, 0.0); wsh.closePath();
  const wing = [new THREE.ExtrudeGeometry(wsh, { depth: 0.014, bevelEnabled: true, bevelThickness: 0.009, bevelSize: 0.009, bevelSegments: 2, curveSegments: 20 }).translate(0, 0, -0.007), new THREE.ExtrudeGeometry(wsh, { depth: 0.02, bevelEnabled: false, curveSegments: 7 }).translate(0, 0, -0.01)];
  const ribs = [0, 1].map(lo => { const list = [], A = new THREE.Vector3(0.04, 0.1, 0); for (const [x, y] of [[0.86, 0.52], [0.8, 0.12], [0.56, 0.06], [0.3, 0.0]]) for (const z of [0.017, -0.017]) { const B = new THREE.Vector3(x, y, 0), d = B.clone().sub(A), Ln = d.length(), g = new THREE.CylinderGeometry(0.009, 0.019, Ln, lo ? 5 : 10, 1, true); g.rotateZ(-Math.atan2(d.x, d.y)); g.translate((A.x + B.x) / 2, (A.y + B.y) / 2, z); list.push(g); } return mergeGeos(list); });
  return { L, buckle, wing, ribs, brow: [new THREE.CapsuleGeometry(0.034, 0.23, 6, 16).rotateZ(Math.PI / 2), new THREE.CapsuleGeometry(0.034, 0.23, 3, 8).rotateZ(Math.PI / 2)], arc: [new THREE.TorusGeometry(0.125, 0.044, 16, 48, Math.PI), new THREE.TorusGeometry(0.125, 0.044, 8, 20, Math.PI)] };
})() : null;
// an ink outline for an accessory: its back faces pushed out along the normals, as wide as the body's outline at any distance
const inkMat = (() => { const m = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });
  m.onBeforeCompile = sh => { sh.uniforms.gLine = GLINE; sh.vertexShader = 'uniform float gLine;\n' + sh.vertexShader.replace('#include <begin_vertex>', 'vec3 transformed = position; { float iD = -(modelViewMatrix * vec4(position, 1.0)).z, iS = length(modelMatrix[0].xyz); transformed += normal * clamp(gLine * iD / max(iS, 1e-3), 0.0, 0.05); }'); };
  m.customProgramCacheKey = () => 'wear-ink'; return m; })();
// a mesh with both levels of detail on it (and its outline, if it has one)
function lodMesh(pair, mat, ink, order) { const m = new THREE.Mesh(pair[0], mat); m.userData.lod = pair; m.renderOrder = order || 33; if (ink) { const o = new THREE.Mesh(pair[0], inkMat); o.userData.lod = pair; o.renderOrder = 32.6; m.add(o); } return m; }
"""
rep("function makeWear(body) {", BUILD + "function makeWear(body) {")

# Graphics mode: build the accessories from the detailed shapes
rep("""function makeWear(body) {
  const ro = m => { m.renderOrder = 33; return m; };""",
"""function makeWear(body) {
  const ro = m => { m.renderOrder = 33; return m; };
  if (HI) {
    const G = WEAR_G, P2 = k => [G.L[0][k], G.L[1][k]];
    const hat = new THREE.Group(), hatIn = new THREE.Group(); hatIn.scale.setScalar(1.3); hat.add(hatIn);
    hatIn.add(lodMesh(P2('cone'), WM.hat, true), lodMesh(P2('brim'), WM.hat, true), lodMesh(P2('band'), WM.band, false), lodMesh([G.buckle, G.buckle], WM.buckle, false));
    const halo = new THREE.Group(); halo.add(lodMesh(P2('halo'), WM.haloHi, false));
    const horns = [-1, 1].map(sd => { const h = lodMesh([G.L[0].horn[sd > 0 ? 1 : 0], G.L[1].horn[sd > 0 ? 1 : 0]], WM.horn, true); h.userData.sd = sd; return h; });
    const wings = [-1, 1].map(sd => { const g = new THREE.Group(); g.add(lodMesh(G.wing, WM.wing, true), lodMesh(G.ribs, WM.rib, false)); g.scale.set(sd * WING_K, WING_K, WING_K); g.userData.sd = sd; return g; });
    const fangs = [-1, 1].map(sd => { const f = lodMesh(P2('fang'), fangM, false, 35); f.userData.sd = sd; return f; });
    const all = [hat, halo, ...horns, ...wings, ...fangs]; for (const m of all) { m.visible = false; body.add(m); }
    return { hat, halo, horns, wings, fangs };
  }""")
# materials: a gold buckle, a halo bright enough to bloom, wings that only need their front faces now they're solid
rep("rib: glossMat(0x150B26, { roughness: 0.4 }) };",
    "rib: glossMat(0x150B26, { roughness: 0.4 }) };\nif (HI) { WM.buckle = charMat(new THREE.MeshPhysicalMaterial({ color: 0xF2C14E, metalness: 1, roughness: 0.24, clearcoat: 0.6, envMapIntensity: 1.5 })); WM.haloHi = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xFFE27A).multiplyScalar(2.3), transparent: true }); WM.wing.side = THREE.FrontSide; }")
# the face's own extras: smooth fangs, rounded brows, smooth arcs (Graphics mode)
rep("function makeWear(body) {\n  const ro = m => { m.renderOrder = 33; return m; };\n  if (HI) {",
    "if (HI) { for (const b of pBrows) b.geometry = WEAR_G.brow[0]; for (const a of pArcs) a.geometry = WEAR_G.arc[0]; for (const f of fangs) f.geometry = WEAR_G.L[0].fang; }\nfunction makeWear(body) {\n  const ro = m => { m.renderOrder = 33; return m; };\n  if (HI) {")
rep("  const br = new THREE.Mesh(new THREE.BoxGeometry(0.29, 0.068, 0.05), eyeB); br.renderOrder = 34; cBody.add(br);",
    "  const br = new THREE.Mesh(HI ? WEAR_G.brow[0] : new THREE.BoxGeometry(0.29, 0.068, 0.05), eyeB); br.renderOrder = 34; cBody.add(br);")
# fading your accessories clones their materials: keep the shader tweaks (the ink outline's push) on the copies
rep("let c = seen.get(m.material); if (!c) { c = m.material.clone(); c.transparent = true;",
    "let c = seen.get(m.material); if (!c) { c = m.material.clone(); c.onBeforeCompile = m.material.onBeforeCompile; c.customProgramCacheKey = m.material.customProgramCacheKey; c.transparent = true;")
# ---------- level of detail for the blobs
rep("const blobG = HI ? new THREE.SphereGeometry(1, 96, 72) : new THREE.SphereGeometry(1, 48, 40);",
    """const blobG = HI ? new THREE.SphereGeometry(1, 96, 72) : new THREE.SphereGeometry(1, 48, 40);
// lighter jelly for a blob that's small on screen (Graphics mode): at the sizes these switch, the extra triangles were under a pixel
const BLOB_LODS = HI ? [blobG, new THREE.SphereGeometry(1, 64, 48), new THREE.SphereGeometry(1, 44, 34)] : null;""")
rep("function renderFrame() {\n  if (vic) return renderVictory();",
    """// pick each blob's detail from how big it is on screen (radius in pixels), with a margin either side so it never flickers
const lodV = new THREE.Vector3(), lodS = new THREE.Vector3(), LOD_PX = [230, 95];
function blobLOD(b) {
  if (!BLOB_LODS || !b.parent || !b.parent.visible) return;
  b.getWorldPosition(lodV); lodS.setFromMatrixScale(b.matrixWorld);
  const d = Math.max(0.3, lodV.distanceTo(camera.position)), rpx = Math.abs(lodS.y) * 1.25 / (d * Math.tan(camera.fov * Math.PI / 360)) * renderer.domElement.height * 0.5;
  let L = b.userData.lodL || 0;
  if (L === 0 && rpx < LOD_PX[0] * 0.9) L = 1; else if (L === 1 && rpx > LOD_PX[0] * 1.1) L = 0;
  if (L === 1 && rpx < LOD_PX[1] * 0.9) L = 2; else if (L === 2 && rpx > LOD_PX[1] * 1.1) L = 1;
  b.userData.rpx = rpx; if (L === b.userData.lodL) return; b.userData.lodL = L;
  b.traverse(m => { if (!m.isMesh) return; if (BLOB_LODS.includes(m.geometry)) m.geometry = BLOB_LODS[L]; else if (m.userData.lod) m.geometry = m.userData.lod[L >= 2 ? 1 : 0]; });
}
function lodPass() { blobLOD(body); blobLOD(cBody); blobLOD(L2.body); }
function renderFrame() {
  lodPass();
  if (vic) return renderVictory();""")
open(p, 'w').write(s)
print('ok')
