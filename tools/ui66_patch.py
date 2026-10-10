#!/usr/bin/env python3
"""The shop and the locker list each kind of item from cheapest to dearest. Flower, lashes, bow tie and the new pearl necklace are in stock from the start: nothing to find, only dabs to pay. The pearl necklace is a strand of pearls on a dark thread hung at the chest, seated like the bow tie. On top of ui65_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui65_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
big, small = open(S + '/tools/assets/pearl_icons.txt') if False else open('/tmp/pearl_icons.txt').read().split('\n')[:2]

# ---- the item ----
rep("{ id: 'bowtie', name: 'Bow tie', slot: 'neck', stage: 'blank' },", "{ id: 'bowtie', name: 'Bow tie', slot: 'neck', stage: 'blank' }, { id: 'pearls', name: 'Pearl necklace', slot: 'neck', stage: 'blank' },")
rep("const PRICES = { flower: 170, bowtie: 220,", "const PRICES = { flower: 170, pearls: 190, bowtie: 220,")
rep("needFind = w => !!w.season || w.slot === 'head';", "OUTRIGHT = new Set(['flower', 'lashes', 'bowtie', 'pearls']), needFind = w => !OUTRIGHT.has(w.id) && (!!w.season || w.slot === 'head'); // (in stock from the start: nothing to find, only dabs to pay)")
# cheapest first, in the shop and in the locker
rep("const items = ITEMS.filter(w => !bought(w.id) && !done.has(w.id) && (c === 'season' ? !!w.season : w.cat === c)); if (!items.length) continue;",
    "const items = ITEMS.filter(w => !bought(w.id) && !done.has(w.id) && (c === 'season' ? !!w.season : w.cat === c)).sort((a, b) => PRICE(a) - PRICE(b)); if (!items.length) continue;")
rep("const mine = WEAR.filter(w => w.cat === lookCat && bought(w.id)), forSale", "const mine = WEAR.filter(w => w.cat === lookCat && bought(w.id)).sort((a, b) => PRICE(a) - PRICE(b)), forSale")
# the icons: the locker tile, and the little lineup face
rep("bowtie: '<path d=\"M20 20l-12.5-7.5v15zM20 20l12.5-7.5v15z\"", "pearls: '<path d=\"M7.5 14c2.5 8.5 7 12.5 12.5 12.5S30 22.5 32.5 14\" fill=\"none\" stroke=\"#3A2A44\" stroke-width=\"1.4\"/><g fill=\"#F7F1E8\" stroke=\"#D9C8FF\" stroke-width=\"1.2\">" + big + "</g>', bowtie: '<path d=\"M20 20l-12.5-7.5v15zM20 20l12.5-7.5v15z\"")
rep("  if (w.neck === 'bowtie') s += '<g stroke=\"' + O + '\"", "  if (w.neck === 'pearls') s += '<g fill=\"#F7F1E8\" stroke=\"' + O + '\" stroke-width=\"0.7\">" + small + "</g>';\n  if (w.neck === 'bowtie') s += '<g stroke=\"' + O + '\"")
rep("neck: Math.random() < (head === 'tophat' ? 0.6 : 0.15) ? 'bowtie' : null,", "neck: Math.random() < (head === 'tophat' ? 0.6 : 0.15) ? 'bowtie' : Math.random() < 0.14 ? 'pearls' : null,")

# ---- the model: a strand of pearls on a dark thread, built in the bow tie's units and seated where it is ----
rep("// the everyday set: the two hats and the bow tie from their models, the patch fitted to the head, the flower\n", r'''// the pearl necklace: a dark thread hung in a curve at the chest with pearls strung along it, bigger towards the middle (in the bow tie's units)
const pearlG = (() => { const pts = [[-0.9, 0.55, -0.42], [-0.7, 0.1, -0.1], [-0.38, -0.25, 0.08], [0, -0.36, 0.14], [0.38, -0.25, 0.08], [0.7, 0.1, -0.1], [0.9, 0.55, -0.42]].map(p => new THREE.Vector3(p[0], p[1], p[2])), curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal'), parts = [new THREE.TubeGeometry(curve, 24, 0.016, 6)], N = 17;
  for (let i = 0; i <= N; i++) { const u = i / N, p = curve.getPointAt(u), r = 0.052 + 0.03 * Math.sin(u * Math.PI); parts.push(new THREE.SphereGeometry(r, HI ? 14 : 10, HI ? 10 : 8).translate(p.x, p.y, p.z)); }
  return mergeGeos(parts); })();
const pearlMat = glossMat(0xF7F1E8, { roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.05, iridescence: 0.55, iridescenceIOR: 1.3 });
// the everyday set: the two hats and the bow tie from their models, the patch fitted to the head, the flower
''')
rep("  const flower = new THREE.Group(); { const m = new THREE.Mesh(flowerG, flowerMat), o = new THREE.Mesh(flowerG, inkMat); m.renderOrder = 33; o.renderOrder = 32.6; m.add(o); flower.add(m); }\n  for (const m of [pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny, skull]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny, skull };",
    "  const flower = new THREE.Group(); { const m = new THREE.Mesh(flowerG, flowerMat), o = new THREE.Mesh(flowerG, inkMat); m.renderOrder = 33; o.renderOrder = 32.6; m.add(o); flower.add(m); }\n  const pearls = new THREE.Group(); { const m = new THREE.Mesh(pearlG, pearlMat), o = new THREE.Mesh(pearlG, inkMat); m.renderOrder = 33; o.renderOrder = 32.6; m.add(o); pearls.add(m); }\n  for (const m of [pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull };")
rep("W.bow.visible = !off && look.neck === 'bowtie'; W.patch.visible = false;", "W.bow.visible = !off && look.neck === 'bowtie'; W.pearls.visible = !off && look.neck === 'pearls'; W.patch.visible = false;")
rep("W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull, ...W.horns", "W.top, W.bow, W.pearls, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull, ...W.horns")
rep("W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = false;", "W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = false;", 2)
rep("    if (W.bow.visible && SLIME.bodyPoint(SI, 0, -0.03, 0.835, wv1)) { W.bow.position.copy(wv1); W.bow.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.05 + S.tz * 0.5)).premultiply(SI.groups.slime.quaternion); W.bow.scale.multiplyScalar(mk * 0.4); }",
    "    if (W.bow.visible && SLIME.bodyPoint(SI, 0, -0.03, 0.835, wv1)) { W.bow.position.copy(wv1); W.bow.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.05 + S.tz * 0.5)).premultiply(SI.groups.slime.quaternion); W.bow.scale.multiplyScalar(mk * 0.4); }\n    if (W.pearls.visible && SLIME.bodyPoint(SI, 0, -0.03, 0.835, wv1)) { W.pearls.position.copy(wv1); W.pearls.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.04 + S.tz * 0.5)).premultiply(SI.groups.slime.quaternion); W.pearls.scale.multiplyScalar(mk * 0.4); }")
rep("W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull] : [])", "W.top, W.bow, W.pearls, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull] : [])")
rep("pWear.top, pWear.bow, pWear.patch", "pWear.top, pWear.bow, pWear.pearls, pWear.patch")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
