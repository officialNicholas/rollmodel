#!/usr/bin/env python3
"""A hockey mask for Halloween: the Meshy model packed into the wear pack, worn over the face (the eye slot, like the glasses), found on the Halloween canvases and sold in the Paint Shop; rivals wear it now and then. On top of ui52_patch."""
import subprocess, re, json
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui52_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

entry = open(S + '/mask/hockey.json').read()
rep('<script type="application/json" id="wearPack">{', '<script type="application/json" id="wearPack">{"hockey":' + entry + ',')
rep("for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses']) if (WEAR_PACK[k]) o[k] = assetGeo(WEAR_PACK[k]);", "for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey']) if (WEAR_PACK[k]) o[k] = assetGeo(WEAR_PACK[k]);")
rep("tiara: WEAR_PACK.tiara ? assetMat(WEAR_PACK.tiara, { clearcoat: 0.8, clearcoatRoughness: 0.12, envMapIntensity: 1.6 }) : null } : {};", "tiara: WEAR_PACK.tiara ? assetMat(WEAR_PACK.tiara, { clearcoat: 0.8, clearcoatRoughness: 0.12, envMapIntensity: 1.6 }) : null, hockey: WEAR_PACK.hockey ? assetMat(WEAR_PACK.hockey, { clearcoat: 0.45, clearcoatRoughness: 0.2 }) : null } : {};")
rep("tiara = grp('tiara', HAT_FIT.tiara.s), glasses = grp('glasses', 1);", "tiara = grp('tiara', HAT_FIT.tiara.s), glasses = grp('glasses', 1), hockey = grp('hockey', 1);")
rep("  for (const m of [pirate, top, bow, patch, flower, tiara, glasses]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses };", "  for (const m of [pirate, top, bow, patch, flower, tiara, glasses, hockey]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses, hockey };")
rep("W.glasses.visible = !off && look.eye === 'glasses';", "W.glasses.visible = !off && look.eye === 'glasses'; W.hockey.visible = !off && look.eye === 'hockey';")
rep("for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone());", "for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone());")
rep("W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = false;", "W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = W.hockey.visible = false;", 2)
rep("    if (W.glasses.visible || W.flower.visible) { SLIME.headTop(SI, wv1, wq1, 0);", "    if (W.glasses.visible || W.hockey.visible || W.flower.visible) { SLIME.headTop(SI, wv1, wq1, 0);\n      if (W.hockey.visible) { W.hockey.position.copy(wv1).add(wv2.set(0, HOCKEY_FIT.y, HOCKEY_FIT.z).multiplyScalar(mk).applyQuaternion(wq1)); W.hockey.quaternion.copy(wq1).multiply(wearQ2.setFromEuler(wearE.set(HOCKEY_FIT.rx + S.tx * 0.2, 0, S.tz * 0.15))); W.hockey.scale.multiplyScalar(mk * HOCKEY_FIT.s); }")
rep("const HAT_FIT = {", "const HOCKEY_FIT = window.__hockeyFit || { s: 0.36, y: -0.13, z: 0.43, rx: -0.04 }; // (the mask over the face: scale, down and forward from the top of the head, tilt)\nconst HAT_FIT = {")
rep("...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses] : [])]", "...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey] : [])]")
# the item
rep("{ id: 'fangs', name: 'Fangs', slot: 'mouth', season: 1, stage: 'halloween' }];", "{ id: 'fangs', name: 'Fangs', slot: 'mouth', season: 1, stage: 'halloween' }, { id: 'hockey', name: 'Hockey mask', slot: 'eye', season: 1, stage: 'halloween' }];")
rep("pirate: 820, halo: 1000, zombie: 1150, hat: 1300 };", "pirate: 820, hockey: 900, halo: 1000, zombie: 1150, hat: 1300 };")
rep("const WEAR_ICON = {\n  zombie:", "const WEAR_ICON = {\n  hockey: '<path d=\"M20 4c8 0 13 6 13 15 0 9-5 17-13 17S7 28 7 19C7 10 12 4 20 4z\" fill=\"#F1E6CF\" stroke=\"#171320\" stroke-width=\"2.5\" stroke-linejoin=\"round\"/><path d=\"M11 17c2-2 4.5-2 6.5 0M22.5 17c2-2 4.5-2 6.5 0\" fill=\"none\" stroke=\"#171320\" stroke-width=\"2.6\" stroke-linecap=\"round\"/><g fill=\"#171320\"><circle cx=\"20\" cy=\"23\" r=\"1.4\"/><circle cx=\"16\" cy=\"26.5\" r=\"1.3\"/><circle cx=\"24\" cy=\"26.5\" r=\"1.3\"/><circle cx=\"18\" cy=\"30.5\" r=\"1.2\"/><circle cx=\"22\" cy=\"30.5\" r=\"1.2\"/><circle cx=\"13\" cy=\"22\" r=\"1.1\"/><circle cx=\"27\" cy=\"22\" r=\"1.1\"/></g><path d=\"M12 10l3 3M28 10l-3 3\" stroke=\"#C8303A\" stroke-width=\"2\" stroke-linecap=\"round\"/>',\n  zombie:")
rep("  if (w.eye === 'patch') s += '<path d=\"M15 16.5l18 6\"", "  if (w.eye === 'hockey') s += '<path d=\"M24 12.5c6.2 0 9.8 4.6 9.8 11.2 0 6.8-3.8 12.3-9.8 12.3S14.2 30.5 14.2 23.7c0-6.6 3.6-11.2 9.8-11.2z\" fill=\"#F1E6CF\"/><path d=\"M17.6 21.2c1.4-1.5 3.3-1.5 4.8 0M25.6 21.2c1.4-1.5 3.3-1.5 4.8 0\" fill=\"none\" stroke=\"' + O + '\" stroke-width=\"1.7\"/><g fill=\"' + O + '\" stroke=\"none\"><circle cx=\"24\" cy=\"25.4\" r=\"1\"/><circle cx=\"21\" cy=\"28\" r=\".9\"/><circle cx=\"27\" cy=\"28\" r=\".9\"/><circle cx=\"22.6\" cy=\"31\" r=\".8\"/><circle cx=\"25.4\" cy=\"31\" r=\".8\"/></g>';\n  if (w.eye === 'patch') s += '<path d=\"M15 16.5l18 6\"")
rep("eye: Math.random() < (head === 'pirate' ? 0.6 : 0.12) ? 'patch' : Math.random() < 0.14 ? 'glasses' : null,", "eye: Math.random() < (head === 'pirate' ? 0.6 : 0.12) ? 'patch' : Math.random() < 0.14 ? 'glasses' : Math.random() < 0.1 ? 'hockey' : null,")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
