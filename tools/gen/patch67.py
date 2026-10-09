import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# ---------- shadow-only stand-ins: drawn into the shadow map in one go, skipped in the normal pass ----------
rep("function splitGroups(g) {", """const shadowOnlyMat = new THREE.MeshBasicMaterial({ colorWrite: false });
function shadowOnly(m) { m.castShadow = true; m.receiveShadow = false; m.onBeforeRender = (r, sc, c, g) => { g.drawRange.count = 0; }; m.onAfterRender = (r, sc, c, g) => { g.drawRange.count = Infinity; }; return m; }
// merge a geometry's groups that share a material, so each material is one draw instead of one per face
function regroup(g, mats) {
  const uniq = [...new Set(mats)], idx = g.index.array, out = [], groups = [];
  for (let u = 0; u < uniq.length; u++) { const st = out.length; for (const gr of g.groups) if (mats[gr.materialIndex] === uniq[u]) for (let k = gr.start; k < gr.start + gr.count; k++) out.push(idx[k]); groups.push([st, out.length - st, u]); }
  g.setIndex(out); g.clearGroups(); for (const [st, c, u] of groups) g.addGroup(st, c, u); return uniq;
}
function splitGroups(g) {""")
rep("  const V = (x, y, z) => new THREE.Vector3(x, y, z), lines = [], hulls = [], frame = [], edges = [], bag = new Map();",
    "  const V = (x, y, z) => new THREE.Vector3(x, y, z), lines = [], hulls = [], frame = [], edges = [], bag = new Map(), shadowG = [];")
rep("      const own = mats.map(mm => mm.clone()), m = new THREE.Mesh(g, own); m.castShadow = true; m.receiveShadow = true; m.userData.ownMats = own; stageGroup.add(m);",
    "      const own = regroup(g, mats).map(mm => mm.clone()), m = new THREE.Mesh(g, own); m.receiveShadow = true; m.userData.ownMats = own; stageGroup.add(m); shadowG.push(g);")
rep("  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat); m.castShadow = true; m.receiveShadow = true; stageGroup.add(m); }",
    "  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat); m.receiveShadow = true; stageGroup.add(m); shadowG.push(m.geometry); }\n  if (shadowG.length) stageGroup.add(shadowOnly(new THREE.Mesh(mergeGeos(shadowG), shadowOnlyMat))); // the whole stage casts in one draw")
# coffins: one shadow draw for the body instead of one per material
rep("  const w = new THREE.Mesh(cofWallG, [coffinRim, coffinWood]); w.castShadow = true; inner.add(w);",
    "  const w = new THREE.Mesh(cofWallG, [coffinRim, coffinWood]); inner.add(w); inner.add(shadowOnly(new THREE.Mesh(cofWallG, shadowOnlyMat)));")
# empty particle pools aren't drawn at all
rep("    it.length = n; pl.im.count = n; if (n) pl.im.instanceMatrix.needsUpdate = true;", "    it.length = n; pl.im.count = n; pl.im.visible = n > 0; if (n) pl.im.instanceMatrix.needsUpdate = true;")
open(F, 'w').write(s)
print('ok')
