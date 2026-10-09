P = '/home/claude/paint-the-canvas.html'
s = open(P).read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:150]); s = s.replace(old, new)
rep("    stone: toon(0x9A9EAA), gold: toon(0xE2B356), bark: toon(0x5A3A28), leaf: toon(0x2F7A42), leaf2: toon(0x3E9550), metal: toon(0xD6DAE2), cream: toon(0xF2E8D2),",
    "    stone: toon(0x9A9EAA, null, { roughness: 0.86 }), gold: toon(0xE2B356, null, { metalness: 0.85, roughness: 0.3 }), bark: toon(0x5A3A28, null, { roughness: 0.92 }), leaf: toon(0x2F7A42, null, { roughness: 0.62 }), leaf2: toon(0x3E9550, null, { roughness: 0.62 }), metal: toon(0xD6DAE2, null, { metalness: 0.7, roughness: 0.3 }), cream: toon(0xF2E8D2, null, { roughness: 0.55 }),")
rep("const cloudMat = toon(0xD9D4F2), clouds = []", "const cloudMat = toon(0xD9D4F2, null, { roughness: 1 }), clouds = []")
# the blobs: glossy jelly with a clear coat in Graphics mode
rep("const dropMat = gooify(toon(C.ink, { transparent: true }));", "const dropMat = gooify(blobMat(C.ink));")
rep("const cMat = gooify(toon(TEAMS[1].wet, { transparent: true }), false, undefined, gooU2);", "const cMat = gooify(blobMat(TEAMS[1].wet), false, undefined, gooU2);")
rep("  const mat = gooify(toon(color, { transparent: true }), false, undefined, U);", "  const mat = gooify(blobMat(color), false, undefined, U);")
rep("const blobG = new THREE.SphereGeometry(1, 48, 32);", """const blobG = HI ? new THREE.SphereGeometry(1, 80, 56) : new THREE.SphereGeometry(1, 40, 28);
// a blob's body: candy-glossy jelly under a clear coat in Graphics mode
const blobMat = c => HI ? new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.34, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 1.1 }) : toon(c, { transparent: true });""")
rep("metalMat = toon(C.metal), ringG", "metalMat = toon(C.metal, null, { metalness: 0.7, roughness: 0.3 }), ringG")
rep("const canMat = toon(0xFFFFFF, { vertexColors: true });", "const canMat = toon(0xFFFFFF, { vertexColors: true }, { roughness: 0.32, metalness: 0.12 });")
rep("splashMat = toon(C.ink), teamMats = TEAMS.map(t => toon(t.wet)),", "splashMat = toon(C.ink, null, { roughness: 0.25 }), teamMats = TEAMS.map(t => toon(t.wet, null, { roughness: 0.25 })),")
open(P, 'w').write(s); print('ok')
