#!/usr/bin/env python3
"""Bunny ears for Halloween: the Meshy model packed into the wear pack, worn on the head like the hats, found on the Halloween canvases and sold in the Paint Shop; rivals wear them now and then. On top of ui54_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui54_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

entry = open(S + '/mask/bunny.json').read()
rep('<script type="application/json" id="wearPack">{"hockey":', '<script type="application/json" id="wearPack">{"bunny":' + entry + ',"hockey":')
rep("for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey'])", "for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey', 'bunny'])")
rep("hockey: WEAR_PACK.hockey ? assetMat(WEAR_PACK.hockey, { clearcoat: 0.45, clearcoatRoughness: 0.2 }) : null } : {};", "hockey: WEAR_PACK.hockey ? assetMat(WEAR_PACK.hockey, { clearcoat: 0.45, clearcoatRoughness: 0.2 }) : null, bunny: WEAR_PACK.bunny ? assetMat(WEAR_PACK.bunny, { clearcoat: 0.25, clearcoatRoughness: 0.35 }) : null } : {};")
rep("const HAT_FIT = { witch:", "const HAT_FIT = { bunny: window.__bunnyFit || { s: 0.78, y: -0.12, rx: -0.08, rz: 0.04 }, witch:")
rep("glasses = grp('glasses', 1), hockey = grp('hockey', 1);", "glasses = grp('glasses', 1), hockey = grp('hockey', 1), bunny = grp('bunny', HAT_FIT.bunny.s);")
rep("  for (const m of [pirate, top, bow, patch, flower, tiara, glasses, hockey]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses, hockey };", "  for (const m of [pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny };")
rep("W.tiara.visible = !off && look.head === 'tiara';", "W.tiara.visible = !off && look.head === 'tiara'; W.bunny.visible = !off && look.head === 'bunny';")
rep("for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara]]) if (o.visible)", "for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny]]) if (o.visible)")
rep("for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara]]) if (o.visible)", "for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny]]) if (o.visible)")
rep("for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone());", "for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone());")
rep("...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey] : [])]", "...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny] : [])]")
# the item
rep("{ id: 'hockey', name: 'Hockey mask', slot: 'eye', season: 1, stage: 'halloween' }];", "{ id: 'hockey', name: 'Hockey mask', slot: 'eye', season: 1, stage: 'halloween' }, { id: 'bunny', name: 'Bunny ears', slot: 'head', season: 1, stage: 'halloween' }];")
rep("pirate: 820, hockey: 900, halo: 1000,", "bunny: 760, pirate: 820, hockey: 900, halo: 1000,")
rep("const WEAR_ICON = {\n  hockey:", "const WEAR_ICON = {\n  bunny: '<path d=\"M13 36c-4-9-5-20-1-31 3 1 6 9 7 19M27 36c4-9 5-20 1-31-3 1-6 9-7 19\" fill=\"#F4E8DC\" stroke=\"#171320\" stroke-width=\"2.5\" stroke-linejoin=\"round\"/><path d=\"M14 29c-1.5-6-1.8-13 0-19 1.4 2 2.6 8 3 15M26 29c1.5-6 1.8-13 0-19-1.4 2-2.6 8-3 15\" fill=\"#F58BB0\"/><path d=\"M8 36h24\" stroke=\"#171320\" stroke-width=\"2.5\" stroke-linecap=\"round\"/>',\n  hockey:")
rep("  if (tph) s += '<g stroke=\"' + O + '\" stroke-width=\"2\" stroke-linejoin=\"round\"><path d=\"M17 0.5h14v13H17z\"", "  if (w.head === 'bunny') s += '<g stroke=\"' + O + '\" stroke-width=\"2\" stroke-linejoin=\"round\"><path d=\"M17 14c-2.5-5-2.8-10.5-.5-14.5 2.2 2 4 7.5 4.5 13.5zM31 14c2.5-5 2.8-10.5.5-14.5-2.2 2-4 7.5-4.5 13.5z\" fill=\"#F4E8DC\"/></g><path d=\"M18 11c-1.2-3.5-1.3-7.5-.2-10 1.2 1.5 2.2 5 2.6 9zM30 11c1.2-3.5 1.3-7.5.2-10-1.2 1.5-2.2 5-2.6 9z\" fill=\"#F58BB0\"/>';\n  if (tph) s += '<g stroke=\"' + O + '\" stroke-width=\"2\" stroke-linejoin=\"round\"><path d=\"M17 0.5h14v13H17z\"")
rep("const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat', 'tiara'];", "const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat', 'tiara', 'bunny'];")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
