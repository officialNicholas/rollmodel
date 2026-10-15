"""v296: characters get two levels of detail, standard and distant, so far-off rivals cost much less to draw and animate.

- Distant body: the axolotl's crawl body (14,608 triangles) has a distant version of 5,112 (35%), made offline with meshoptimizer's
  simplifier over the same vertices (tools/axo_lod_make.mjs -> tools/data/axo_lod_250.json, keyed to the pack's vertex and index counts).
  Because it reuses the same vertices, skinning, face, paint and UVs carry over untouched; only the triangle list is shorter. A distant
  character draws its body, its ink outline, its see-through silhouette and its shadow from it.
- Distant animation: a distant character's pose is worked out 30 times a second instead of every frame (its position and heading still
  move every frame, so it slides smoothly; only the limbs, ears and face step at 30). That covers its gait, its ears and tail, its face
  and its skinning upload.
- Which is which: by how big the character is on screen. A rival under about 52 CSS pixels per metre of body (in portrait, about 12
  metres from the camera) goes distant, and comes back to standard a little closer than that (no flicker at the line). Your own
  character is always standard, and so is everyone outside a match (menus, the locker, versus portraits, the victory screen, the kill cam).
- If a pack ever doesn't match the stored counts, nothing changes: every character just stays standard."""
import json, os
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HERE = os.path.dirname(os.path.abspath(__file__))
LOD = json.load(open(os.path.join(HERE, 'data', 'axo_lod_250.json')))

HELPERS = r"""
  // (v296) two levels of detail: standard, and distant (a 35% body over the same vertices, the pose at 30 a second)
  const AXO_LOD = __LOD__, LOD_FAR_PX = 52, LOD_K = 0.163, ANIM_FAR = 1 / 30, _lv = new THREE.Vector3(), _ls = new THREE.Vector3();
  function lodGeo(M) {
    const full = M.full || (M.full = M.mesh.geometry); if (full.userData.lodTry) return full.userData.lod || null; full.userData.lodTry = true;
    const d = AXO_LOD[M.meta && M.meta.name]; if (!d || !full.index || full.attributes.position.count !== d.n || full.index.count !== d.ni) return null;
    const g = new THREE.BufferGeometry(); for (const k in full.attributes) g.setAttribute(k, full.attributes[k]);
    g.setIndex(new THREE.BufferAttribute(new Uint16Array(fromB64(d.b64)), 1)); g.userData = { tex: full.userData.tex }; if (full.boundingSphere) g.boundingSphere = full.boundingSphere;
    full.userData.lod = g; return g;
  }
  function lodFar(I, D) {
    if (!D || D === P || vic || kcam || window.__noLod || (state !== 'play' && state !== 'paused' && state !== 'intro' && state !== 'dead')) return false;
    I.root.getWorldPosition(_lv); _ls.setFromMatrixScale(I.root.matrixWorld);
    const d = Math.max(0.5, _lv.distanceTo(camera.position)), px = viewH * 0.5 / (d * Math.tan(camera.fov * Math.PI / 360)) * Math.abs(_ls.y) / (SC * LOD_K); // (CSS pixels a metre, for a blob of the usual size: a giant counts bigger)
    I.lodPx = px; return I.lodFar ? px < LOD_FAR_PX * 1.12 : px < LOD_FAR_PX * 0.9;
  }
  function lodSet(I, far) {
    if (!!I.lodFar === far && I.lodSet) return; I.lodFar = far; I.lodSet = true;
    for (const M of [I.ax.S, I.ax.C]) { const full = M.full || (M.full = M.mesh.geometry), g = far ? lodGeo(M) || full : full;
      if (M.mesh.geometry !== g) { M.mesh.geometry = g; if (M.ink) M.ink.geometry = g; if (M.ghost) M.ghost.geometry = g; } }
  }
"""

def apply(s):
    s = rep(s, "  function stateFor(I, o) { return 'crawl'; }", HELPERS.replace('__LOD__', json.dumps(LOD, separators=(',', ':'))).lstrip('\n') + "  function stateFor(I, o) { return 'crawl'; }")
    s = rep(s, "const X = I.ax, A = X.A, look = X.look, D = o.D, dt = Math.min(0.05, o.dt || 0); I.st.t += dt;",
               "const X = I.ax, A = X.A, look = X.look, D = o.D, dt = Math.min(0.05, o.dt || 0); I.st.t += dt; lodSet(I, lodFar(I, D)); // (v296)")
    s = rep(s, "A.update(D && D.frozenT > 0 ? 0 : dt); if (D) D.strokeK",
               "{ const adt = D && D.frozenT > 0 ? 0 : dt; if (!I.lodFar) { X.aAcc = 0; A.update(adt); } else { X.aAcc = (X.aAcc || 0) + adt; if (X.aAcc >= ANIM_FAR - 0.003) { A.update(Math.min(0.05, X.aAcc)); X.aAcc = 0; } } } /* (v296: far off, the pose at 30 a second) */ if (D) D.strokeK")
    return s
