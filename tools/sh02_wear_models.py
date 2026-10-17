"""sh02: a sculpted mustache and fuzzy antennae, made on Ludo.ai (an image of each, then image to 3D), in place of the tube-and-ball builds.

- The models are in models/shop/ (the GLBs as they came, and their pack entries made with tools/glb2pack.py: 256px color maps). They
  go in the page's wear pack beside the hockey mask, the bunny ears and the skull, and are drawn like them (their own color and
  metal-rough maps; the smoothed-normal shell for the outline).
- The mustache: a full handlebar with hair grooves and curled tips (about 2,400 triangles). It's scaled to the old one's width and
  bent round to follow the face, and it keeps the old one's place under the nose (STACHE_FIT) and its tilt with the head.
- The antennae: each one a smooth curved stalk on a little round base with a fuzzy pink pom-pom (about 1,400 triangles each), no
  more coil. Still two of them, mirrored, and they bob, splay and lag behind exactly as before (the same pivots and motion).
- If the pack is missing, the old builds are used."""
import os, json

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HERE = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(os.path.dirname(HERE), 'models', 'shop')
# how the new pieces fit (tuned on the character in the locker)
STACHE = dict(s=0.74, bend=0.7, y=0.0, z=0.0)   # (scale from the model's unit width, how far the tips curve back to follow the face)
ANT = dict(h=0.66, ry=0.0)                      # (each antenna's height in the old piece's units, its turn about its stalk)

def apply(s):
    pk = {k: json.load(open(os.path.join(M, k + '.json'))) for k in ('stache', 'antenna')}
    s = rep(s, '<script type="application/json" id="wearPack">{"skull":', '<script type="application/json" id="wearPack">{"stache":' + json.dumps(pk['stache'], separators=(',', ':')) + ',"antenna":' + json.dumps(pk['antenna'], separators=(',', ':')) + ',"skull":')
    s = rep(s, "for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey', 'bunny', 'skull'])", "for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey', 'bunny', 'skull', 'stache', 'antenna'])")
    s = rep(s, "// the patch and its strap: dark leather, a little sheen\n",
        "if (WEAR_PACK && WEAR_PACK.stache) WEAR_AM.stache = assetMat(WEAR_PACK.stache, { clearcoat: 0.35, clearcoatRoughness: 0.3 }); // (sh02: the sculpted mustache)\n"
        "if (WEAR_PACK && WEAR_PACK.antenna) WEAR_AM.antenna = assetMat(WEAR_PACK.antenna, { clearcoat: 0.3, clearcoatRoughness: 0.35 }); // (sh02: the fuzzy antennae)\n"
        "// the patch and its strap: dark leather, a little sheen\n")
    # a packed piece brings its own outline shell (smoothed normals)
    s = rep(s, "const m = new THREE.Mesh(geo, mat), o = new THREE.Mesh(geo, inkMat);", "const m = new THREE.Mesh(geo, mat), o = new THREE.Mesh(geo.userData.ink || geo, inkMat);")
    # (the packed positions are shared by the model and its shell, so reshaping them once reshapes both)
    s = rep(s, "const stacheParts = (() => {", "const stacheOld = (() => {")
    s = rep(s, "cap(1), cap(-1)]), stacheMat]]; })();",
        "cap(1), cap(-1)]), stacheMat]]; })();\n"
        "const stacheParts = WEAR_A.stache && WEAR_AM.stache ? (() => { const A = WEAR_A.stache, p = A.g.attributes.position, k = %(s)s, bend = %(bend)s; // (sh02: scaled to the old one's width, the tips bent back round the face)\n"
        "  for (let i = 0; i < p.count; i++) { const x = p.getX(i) * k; p.setXYZ(i, x, p.getY(i) * k + %(y)s, p.getZ(i) * k + %(z)s - bend * x * x); } p.needsUpdate = true; A.g.computeBoundingSphere(); A.ink.boundingSphere = A.g.boundingSphere;\n"
        "  A.g.userData.ink = A.ink; return [[A.g, WEAR_AM.stache]]; })() : stacheOld;" % STACHE)
    s = rep(s, "const antennaParts = (() => {", "const antennaOld = (() => {")
    s = rep(s, "glossMat(0xFF5DA2, { roughness: 0.3, clearcoat: 0.8 })]]; })();",
        "glossMat(0xFF5DA2, { roughness: 0.3, clearcoat: 0.8 })]]; })();\n"
        "const antennaParts = WEAR_A.antenna && WEAR_AM.antenna ? (() => { const A = WEAR_A.antenna, p = A.g.attributes.position, k = %(h)s / 1.0014, c = Math.cos(%(ry)s), sn = Math.sin(%(ry)s); // (sh02: standing on its base where the old stalk began)\n"
        "  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setXYZ(i, (x * c + z * sn) * k, p.getY(i) * k, (z * c - x * sn) * k); } p.needsUpdate = true; A.g.computeBoundingSphere(); A.ink.boundingSphere = A.g.boundingSphere;\n"
        "  A.g.userData.ink = A.ink; return [[A.g, WEAR_AM.antenna]]; })() : antennaOld;" % ANT)
    return s
