#!/usr/bin/env python3
"""v238: five more simple pieces in the Paint Shop, in stock from the start (dabs to pay, nothing to find): a beanie with a pom-pom and a
party hat (headgear), a monocle on its chain and a curly mustache (facial), and a knitted scarf (clothing). Simple shapes with the game's
outline, sized to the head and placed like the pieces already there; each has an icon for the shop and the locker, and the shop shows
its own render of it."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui170_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- the items
rep("{ id: 'glasses', name: 'Glasses', slot: 'eye', stage: 'blank' },",
    "{ id: 'glasses', name: 'Glasses', slot: 'eye', stage: 'blank' }, { id: 'beanie', name: 'Beanie', slot: 'head', stage: 'blank' }, { id: 'party', name: 'Party hat', slot: 'head', stage: 'blank' }, { id: 'monocle', name: 'Monocle', slot: 'eye', stage: 'blank' }, { id: 'stache', name: 'Mustache', slot: 'mouth', stage: 'blank' }, { id: 'scarf', name: 'Scarf', slot: 'neck', stage: 'blank' },")
rep("const PRICES = { sly: 640, flower: 170, pearls: 190, bowtie: 220,", "const PRICES = { sly: 640, flower: 170, pearls: 190, scarf: 210, bowtie: 220, stache: 230, beanie: 240, party: 280, monocle: 340,")
rep("const OUTRIGHT = new Set(['flower', 'lashes', 'bowtie', 'pearls'])", "const OUTRIGHT = new Set(['flower', 'lashes', 'bowtie', 'pearls', 'beanie', 'party', 'monocle', 'stache', 'scarf'])")
# ---- the shapes (unit head: the hats sit on a head about half a unit across, like the witch hat's cone; the face pieces in the glasses' units)
rep("// the everyday set: the two hats and the bow tie from their models, the patch fitted to the head, the flower",
    """// five more everyday pieces, simple shapes: a beanie (a soft dome, a folded band, a pom-pom), a party hat (striped cone, a pom), a scarf
// (a loop round the neck, a tail hanging down with a fringe), a monocle (a gold rim, a glass, a chain), a curly mustache
const knitMat = glossMat(0x2A9D8F, { roughness: 0.75, clearcoat: 0.05, sheen: 0.8, sheenColor: new THREE.Color(0x9FE3D8), sheenRoughness: 0.9 }), creamMat = glossMat(0xF6EBD7, { roughness: 0.8, clearcoat: 0.05, sheen: 0.7, sheenColor: new THREE.Color(0xFFFFFF), sheenRoughness: 0.9 });
const partyAMat = glossMat(0xFF5A8A, { roughness: 0.3, clearcoat: 0.6 }), partyBMat = glossMat(0xFFE066, { roughness: 0.3, clearcoat: 0.6 }), scarfMat = glossMat(0xE3283E, { roughness: 0.78, clearcoat: 0.05, sheen: 0.8, sheenColor: new THREE.Color(0xFF9AA8), sheenRoughness: 0.9 });
const goldMat = HI ? charMat(new THREE.MeshPhysicalMaterial({ color: 0xE8C25A, metalness: 1, roughness: 0.22, clearcoat: 0.5, envMapIntensity: 1.5 })) : glossMat(0xE8C25A, { roughness: 0.25 }), glassMat = new THREE.MeshPhysicalMaterial({ color: 0xBFE6FF, transparent: true, opacity: 0.28, roughness: 0.05, clearcoat: 1, depthWrite: false }), stacheMat = glossMat(0x3B2418, { roughness: 0.45, clearcoat: 0.4 });
const simplePiece = (parts, s) => { const g = new THREE.Group(), gin = new THREE.Group(); g.add(gin); for (const [geo, mat] of parts) { const m = new THREE.Mesh(geo, mat), o = new THREE.Mesh(geo, inkMat); m.renderOrder = 33; o.renderOrder = 32.6; m.add(o); gin.add(m); } gin.scale.setScalar(s || 1); g.userData.gin = gin; return g; };
const beanieParts = (() => { const dome = new THREE.SphereGeometry(0.52, 26, 18, 0, Math.PI * 2, 0, Math.PI * 0.56).scale(1, 1.08, 1); const band = new THREE.TorusGeometry(0.5, 0.1, 12, 36).rotateX(Math.PI / 2).translate(0, -0.08, 0); const pom = new THREE.SphereGeometry(0.15, 16, 12).translate(0, 0.6, 0);
  return [[dome, knitMat], [band, creamMat], [pom, creamMat]]; })();
const partyParts = (() => { const list = [], H = 0.84, N = 5; for (let k = 0; k < N; k++) { const y0 = k / N * H, y1 = (k + 1) / N * H, r = y => 0.3 * (1 - y / H); list.push([new THREE.CylinderGeometry(r(y1) + (k === N - 1 ? 0.01 : 0), r(y0), y1 - y0, 24).translate(0, (y0 + y1) / 2, 0), k % 2 ? partyBMat : partyAMat]); }
  list.push([new THREE.SphereGeometry(0.085, 14, 10).translate(0, H + 0.03, 0), creamMat]); return list; })();
const scarfParts = (() => { const loop = new THREE.TorusGeometry(0.72, 0.19, 12, 36).rotateX(Math.PI / 2).scale(1, 1, 0.92), tail = new THREE.BoxGeometry(0.34, 0.9, 0.11, 1, 6, 1); { const p = tail.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i), u = (y + 0.45) / 0.9; p.setZ(i, p.getZ(i) + 0.09 * Math.sin(u * Math.PI * 1.5)); p.setX(i, p.getX(i) * (0.85 + 0.15 * u)); } tail.computeVertexNormals(); } tail.translate(0.26, -0.6, 0.72);
  const fr = []; for (let k = -2; k <= 2; k++) fr.push(new THREE.CylinderGeometry(0.022, 0.022, 0.2, 6).translate(0.26 + k * 0.065, -1.13, 0.72)); return [[loop, scarfMat], [tail, scarfMat], [mergeGeos(fr), creamMat]]; })();
const monoParts = (() => { const rim = new THREE.TorusGeometry(0.2, 0.028, 10, 40), glass = new THREE.CircleGeometry(0.18, 32); const pts = [[0.17, -0.1, 0], [0.26, -0.3, -0.04], [0.34, -0.52, -0.1], [0.4, -0.72, -0.2]].map(p => new THREE.Vector3(...p)); const chain = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, 0.016, 6);
  return [[rim, goldMat], [chain, goldMat], [glass, glassMat]]; })();
const stacheParts = (() => { const side = m => { const pts = [[0, -0.02, 0], [0.11 * m, -0.04, 0.01], [0.21 * m, -0.01, 0.0], [0.28 * m, 0.07, -0.03], [0.3 * m, 0.13, -0.05]].map(p => new THREE.Vector3(...p)); return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'centripetal'), 20, 0.05, 8); };
  const cap = m => new THREE.SphereGeometry(0.05, 10, 8).translate(0.3 * m, 0.13, -0.05); return [[mergeGeos([side(1), side(-1), new THREE.SphereGeometry(0.058, 12, 10), cap(1), cap(-1)]), stacheMat]]; })();
// how each sits (window.__*Fit: a tuning hook)
const BEANIE_FIT = window.__beanieFit || { s: 1.18, y: -0.36, rx: -0.14, rz: 0.08 }, PARTY_FIT = window.__partyFit || { s: 0.95, y: -0.12, rx: 0.1, rz: 0.4 };
const MONO_FIT = window.__monoFit || { x: 0.2, y: 0.06, z: 0.44, s: 0.62 }, STACHE_FIT = window.__stacheFit || { x: 0, y: -0.11, z: 0.44, s: 0.48 }, SCARF_FIT = window.__scarfFit || { s: 0.4, y: -0.01, z: 0.04 };
// the everyday set: the two hats and the bow tie from their models, the patch fitted to the head, the flower""")
rep("  for (const m of [pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull };",
    "  const beanie = simplePiece(beanieParts, BEANIE_FIT.s), party = simplePiece(partyParts, PARTY_FIT.s), scarf = simplePiece(scarfParts), monocle = simplePiece(monoParts), stache = simplePiece(stacheParts);\n  for (const m of [pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull, beanie, party, scarf, monocle, stache]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull, beanie, party, scarf, monocle, stache };")
# ---- shown, kept, pictured
rep("W.glasses.visible = !off && look.eye === 'glasses'; W.hockey.visible = !off && look.eye === 'hockey'; W.skull.visible = !off && look.head === 'skull';",
    "W.glasses.visible = !off && look.eye === 'glasses'; W.hockey.visible = !off && look.eye === 'hockey'; W.skull.visible = !off && look.head === 'skull';\n  W.beanie.visible = !off && look.head === 'beanie'; W.party.visible = !off && look.head === 'party'; W.scarf.visible = !off && look.neck === 'scarf'; W.monocle.visible = !off && look.eye === 'monocle'; W.stache.visible = !off && look.mouth === 'stache';")
rep("for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.pearls, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }",
    "for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.pearls, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull, W.beanie, W.party, W.scarf, W.monocle, W.stache, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }")
rep("    for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny], [W.skull, HAT_FIT.skull]]) if (o.visible) {",
    "    for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny], [W.skull, HAT_FIT.skull], [W.beanie, BEANIE_FIT], [W.party, PARTY_FIT]]) if (o.visible) {")
rep("    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = false; }",
    "    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = W.scarf.visible = W.monocle.visible = W.stache.visible = false; }")
rep("    if (W.glasses.visible || W.hockey.visible || W.flower.visible) { CH.headTop(SI, wv1, wq1, 0);",
    "    if (W.monocle.visible || W.stache.visible) { CH.headTop(SI, wv1, wq1, 0); /* (on the face, from the head's centre: the monocle over the right eye, the mustache under the nose) */\n      if (W.monocle.visible) { W.monocle.position.copy(wv1).add(wv2.set(MONO_FIT.x, MONO_FIT.y, MONO_FIT.z).multiplyScalar(mk).applyQuaternion(wq1)); W.monocle.quaternion.copy(wq1).multiply(wearQ2.setFromEuler(wearE.set(-0.06 + S.tx * 0.2, 0, S.tz * 0.15))); W.monocle.scale.multiplyScalar(mk * MONO_FIT.s * (CH.faceK || 1)); }\n      if (W.stache.visible) { W.stache.position.copy(wv1).add(wv2.set(STACHE_FIT.x, STACHE_FIT.y, STACHE_FIT.z).multiplyScalar(mk).applyQuaternion(wq1)); W.stache.quaternion.copy(wq1).multiply(wearQ2.setFromEuler(wearE.set(-0.1 + S.tx * 0.2, 0, S.tz * 0.15))); W.stache.scale.multiplyScalar(mk * STACHE_FIT.s * (CH.faceK || 1)); } }\n    if (W.glasses.visible || W.hockey.visible || W.flower.visible) { CH.headTop(SI, wv1, wq1, 0);")
rep("    if (W.pearls.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {",
    "    if (W.scarf.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1)) { W.scarf.position.copy(wv1).add(wv2.set(0, SCARF_FIT.y, SCARF_FIT.z).multiplyScalar(mk).applyQuaternion(wq1)); W.scarf.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.04 + S.tz * 0.5)).premultiply(SI.groups.slime.quaternion); W.scarf.scale.multiplyScalar(mk * SCARF_FIT.s); }\n    if (W.pearls.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {")
rep("  W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = false;\n  for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny], [W.skull, HAT_FIT.skull]]) if (o.visible) {",
    "  W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = W.scarf.visible = W.monocle.visible = W.stache.visible = false;\n  for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny], [W.skull, HAT_FIT.skull], [W.beanie, BEANIE_FIT], [W.party, PARTY_FIT]]) if (o.visible) {")
rep("...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.pearls, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull] : [])]",
    "...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.pearls, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull, W.beanie, W.party, W.scarf, W.monocle, W.stache] : [])]")
rep("hat: () => pWear.hat, halo: () => pWear.halo };", "hat: () => pWear.hat, halo: () => pWear.halo, beanie: () => pWear.beanie, party: () => pWear.party, scarf: () => pWear.scarf, monocle: () => pWear.monocle, stache: () => pWear.stache };")
# ---- the icons
rep("const WEAR_ICON = {", """const WEAR_ICON = {
  beanie: '<path d="M8 25c0-9 5.5-15 12-15s12 6 12 15z" fill="#2A9D8F" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><rect x="6.5" y="23.5" width="27" height="6.5" rx="3" fill="#F6EBD7" stroke="#D9C8FF" stroke-width="1.6"/><circle cx="20" cy="8.5" r="3.6" fill="#F6EBD7" stroke="#D9C8FF" stroke-width="1.6"/>',
  party: '<path d="M20 5l11 27H9z" fill="#FF5A8A" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><path d="M12.8 22.5h14.4l2.6 6.5H10.2zM16.6 13h6.8l1.8 4.5h-10.4z" fill="#FFE066"/><circle cx="20" cy="5.5" r="2.8" fill="#F6EBD7" stroke="#D9C8FF" stroke-width="1.4"/>',
  monocle: '<circle cx="18" cy="16" r="8.5" fill="#BFE6FF" fill-opacity=".35" stroke="#E8C25A" stroke-width="2.6"/><path d="M24.5 21.5c3 3 4.5 7 5.5 11" fill="none" stroke="#E8C25A" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="1.5 2"/>',
  stache: '<path d="M20 19c-2.5-3-6-3.5-9-2-2.4 1.3-3.5 4.2-2.5 6.5 1.6-1.5 4-1.8 6-1 2.2.9 4 .9 5.5-1 1.5 1.9 3.3 1.9 5.5 1 2-.8 4.4-.5 6 1 1-2.3-.1-5.2-2.5-6.5-3-1.5-6.5-1-9 2z" fill="#3B2418" stroke="#D9C8FF" stroke-width="1.4" stroke-linejoin="round"/>',
  scarf: '<path d="M8 15c0-4 5.4-7 12-7s12 3 12 7-5.4 7-12 7S8 19 8 15z" fill="#E3283E" stroke="#D9C8FF" stroke-width="1.6"/><path d="M23 21l2 10h8l-3-11z" fill="#E3283E" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><path d="M26 31v3.5M29 31v3.5M32 31v3.5" stroke="#F6EBD7" stroke-width="1.6" stroke-linecap="round"/>',""")
rep('<p class="ver">Version 237</p>', '<p class="ver">Version 238</p>')
open(DST, 'w').write(s)
print('ui171 ok', n0, '->', len(s))
