import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# ---------- coffins: walls, lid and panel are one mesh (wood tones per vertex), both outlines one more ----------
rep("function makeCoffin(x, y, z, seed) {", """const cofVC = toon(0xFFFFFF, { map: woodTex, vertexColors: true });
const COFM = (() => {
  const m4 = new THREE.Matrix4().compose(new THREE.Vector3(0.76, 0.27, 0.04), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0.08, -0.6)), new THREE.Vector3(1, 1, 1));
  const cW = new THREE.Color(0x9A6A48), cR = new THREE.Color(0xB98458), ni = g => g.index ? g.toNonIndexed() : g;
  const wall = ni(cofWallG), lid = ni(cofLidG.clone().applyMatrix4(m4)), panel = ni(cofPanelG.clone().applyMatrix4(m4));
  const parts = [[wall, v => { for (const gr of wall.groups) if (v >= gr.start && v < gr.start + gr.count) return gr.materialIndex === 0 ? cR : cW; return cW; }], [lid, () => cW], [panel, () => cR]];
  let n = 0; for (const [g] of parts) n += g.attributes.position.count;
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2), col = new Float32Array(n * 3); let o = 0;
  for (const [g, cf] of parts) { const k = g.attributes.position.count; pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3); if (g.attributes.uv) uv.set(g.attributes.uv.array, o * 2); for (let q = 0; q < k; q++) { const c = cf(q); col[(o + q) * 3] = c.r; col[(o + q) * 3 + 1] = c.g; col[(o + q) * 3 + 2] = c.b; } o += k; }
  const wood = new THREE.BufferGeometry(); wood.setAttribute('position', new THREE.BufferAttribute(pos, 3)); wood.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); wood.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); wood.setAttribute('color', new THREE.BufferAttribute(col, 3));
  return { wood, hull: mergeGeos([cofHullG, cofLidHullG.clone().applyMatrix4(m4)]) };
})();
function makeCoffin(x, y, z, seed) {""")
rep("""  const w = new THREE.Mesh(cofWallG, [coffinRim, coffinWood]); inner.add(w); inner.add(shadowOnly(new THREE.Mesh(cofWallG, shadowOnlyMat)));
  inner.add(new THREE.Mesh(cofHullG, outlineMat));""", """  const w = new THREE.Mesh(COFM.wood, cofVC); w.castShadow = true; inner.add(w);
  inner.add(new THREE.Mesh(COFM.hull, outlineMat));""")
rep("""  // the lid, slid off and leaning against one side
  const lid = new THREE.Group(); lid.position.set(0.76, 0.27, 0.04); lid.rotation.set(0, 0.08, -0.6);
  const lm = new THREE.Mesh(cofLidG, coffinWood); lm.castShadow = true; lid.add(lm); lid.add(new THREE.Mesh(cofLidHullG, outlineMat)); lid.add(new THREE.Mesh(cofPanelG, coffinRim)); inner.add(lid);
""", "  // (the lid, slid off and leaning against one side, is part of the wood mesh)\n")
open(F, 'w').write(s)
print('ok')
