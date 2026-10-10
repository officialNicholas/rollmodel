#!/usr/bin/env python3
"""The turret is the glass dome: on the mount the blob itself is hidden and the dome shows its paint draining as it fires; the pick-up shrinks to the roller's bubble. A skull mask for Halloween, canvas finds half again as frequent, the bunny ears' band round the head, the simple items for sale outright, and the new sounds for the tally and the knock-out. On top of ui57_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui57_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the sounds ----
rep("    at,\n    mood(late", """    // the tally and the knock-out flood (their recordings, or the nearest synthesized sound while those load)
    tpour() { P_('tpour', { vary: 0.02, v: 0.9 }); },
    ttick(i) { if (!P_('ttick', { rate: Math.pow(2, ((i | 0) % 12) / 30), vary: 0.01 })) api.tick(i); },
    tslice() { if (!P_('tslice', { vary: 0.06 })) api.splat(0.6); },
    tsplash() { if (!P_('tsplash', { vary: 0.03 })) api.splat(1.3); },
    tsettle() { if (!P_('tsettle', { v: 0.8 })) api.pop(); },
    kflood() { if (!P_('kflood', { vary: 0.03 })) api.splat(1.1); },
    kpart() { if (!P_('kpart', { vary: 0.03 })) api.whoosh(); },
    at,
    mood(late""")

# ---- the turret: the dome of paint, not the morph ----
rep("  return { baseG, barrelG, domeG, dir, tip: at(bl + 0.05) };", "  const inkG = new THREE.SphereGeometry(0.98, 26, 18); inkG.translate(0, 0.98, 0); // (its base at the bottom, so it can be drained)\n  return { baseG, barrelG, domeG, inkG, inkY: -1.08, dir, tip: at(bl + 0.05) };")
rep("d = new THREE.Mesh(TURRET_RIG.domeG, turDomeM); a.castShadow = b.castShadow = true; a.renderOrder = b.renderOrder = 31; d.renderOrder = 44; bg.add(b); g.add(a); g.add(bg); g.add(d); V.body.add(g); V.tur = g; V.turBarrel = bg; }",
    "d = new THREE.Mesh(TURRET_RIG.domeG, turDomeM), ink = new THREE.Mesh(TURRET_RIG.inkG, toon(0xE3122F, { transparent: true })); a.castShadow = b.castShadow = true; a.renderOrder = b.renderOrder = 31; d.renderOrder = 44; ink.renderOrder = 33; ink.position.y = TURRET_RIG.inkY; bg.add(b); g.add(a); g.add(bg); g.add(ink); g.add(d); g.userData.ink = ink; V.body.add(g); V.tur = g; V.turBarrel = bg; }")
rep("V.turPitch = (V.turPitch || 0) + (-(aimT - 0.4) * 0.6 - (V.turPitch || 0)) * Math.min(1, dt * 12); V.turBarrel.rotation.x = V.turPitch; } }",
    "V.turPitch = (V.turPitch || 0) + (-(aimT - 0.4) * 0.6 - (V.turPitch || 0)) * Math.min(1, dt * 12); V.turBarrel.rotation.x = V.turPitch;\n      const ink = V.tur.userData.ink; if (ink) { const col = TEAMS[D.team].wet; if (V.turCol !== col) { V.turCol = col; ink.material.color.setHex(col); } const lv = D.turret ? clamp(D.turret.t / TURRET_T, 0, 1) : (V.turLv === undefined ? 1 : V.turLv); V.turLv = V.turLv === undefined ? lv : V.turLv + (lv - V.turLv) * Math.min(1, dt * 8); ink.scale.set(1 - 0.08 * (1 - V.turLv), Math.max(0.05, V.turLv), 1 - 0.08 * (1 - V.turLv)); } } }")
rep("  const on = L.roll < 0.5 && !(D === P && lookIntro && lookIntro.t < IN_LAND), was = I.root.visible;\n  I.root.visible = on; V.oldBlob.visible = !on; if (!on) return;",
    "  const tur = !!D.turret && D.st === 'play', on = L.roll < 0.5 && !tur && !(D === P && lookIntro && lookIntro.t < IN_LAND), was = I.root.visible; // (on the mount the blob is the paint in the dome: hidden)\n  I.root.visible = on; V.oldBlob.visible = !on && !tur; if (!on) return;")
rep("  I.setForm(D.giantT > 0 ? 'giant' : D.turret && D.st === 'play' ? 'turret' : 'slime');", "  I.setForm(D.giantT > 0 ? 'giant' : 'slime');")
rep("  else if (type === 'turret') { const t = new THREE.Group(); t.position.y = -0.12; t.scale.setScalar(0.72); spin.add(t);", "  else if (type === 'turret') { const t = new THREE.Group(); t.position.y = -0.12; t.scale.setScalar(0.42); spin.add(t);")

# ---- the skull ----
entry = open(S + '/mask/skull.json').read()
rep('<script type="application/json" id="wearPack">{"bunny":', '<script type="application/json" id="wearPack">{"skull":' + entry + ',"bunny":')
rep("for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey', 'bunny'])", "for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses', 'hockey', 'bunny', 'skull'])")
rep("bunny: WEAR_PACK.bunny ? assetMat(WEAR_PACK.bunny, { clearcoat: 0.25, clearcoatRoughness: 0.35 }) : null } : {};", "bunny: WEAR_PACK.bunny ? assetMat(WEAR_PACK.bunny, { clearcoat: 0.25, clearcoatRoughness: 0.35 }) : null, skull: WEAR_PACK.skull ? assetMat(WEAR_PACK.skull, { clearcoat: 0.4, clearcoatRoughness: 0.25 }) : null } : {};")
rep("const HAT_FIT = { bunny:", "const HAT_FIT = { skull: window.__skullFit || { s: 0.58, y: -0.34, rx: 0.12, rz: 0.55 }, bunny:") # (the skull bow: up on the head, cocked to one side)
rep("hockey = grp('hockey', 1), bunny = grp('bunny', HAT_FIT.bunny.s);", "hockey = grp('hockey', 1), bunny = grp('bunny', HAT_FIT.bunny.s), skull = grp('skull', HAT_FIT.skull.s);")
rep("  for (const m of [pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny };", "  for (const m of [pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny, skull]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses, hockey, bunny, skull };")
rep("W.hockey.visible = !off && look.eye === 'hockey';", "W.hockey.visible = !off && look.eye === 'hockey'; W.skull.visible = !off && look.head === 'skull';")
rep("[W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny]]) if (o.visible)", "[W.tiara, HAT_FIT.tiara], [W.bunny, HAT_FIT.bunny], [W.skull, HAT_FIT.skull]]) if (o.visible)", 2)
rep("W.glasses, W.hockey, W.bunny, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone());", "W.glasses, W.hockey, W.bunny, W.skull, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone());")
rep("W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = W.hockey.visible = false;", "W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = false;", 2)
rep("...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny] : [])]", "...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, W.hockey, W.bunny, W.skull] : [])]")
rep("{ id: 'bunny', name: 'Bunny ears', slot: 'head', season: 1, stage: 'halloween' }];", "{ id: 'bunny', name: 'Bunny ears', slot: 'head', season: 1, stage: 'halloween' }, { id: 'skull', name: 'Skull bow', slot: 'head', season: 1, stage: 'halloween' }];")
rep("bunny: 760, pirate: 820, hockey: 900, halo: 1000,", "bunny: 760, pirate: 820, hockey: 900, skull: 980, halo: 1000,")
rep("const WEAR_ICON = {\n  bunny:", "const WEAR_ICON = {\n  skull: '<path d=\"M6 18c5-6 11-4 14 1 3-5 9-7 14-1 2 5-3 10-9 10-1 0-3-.3-5-1-2 .7-4 1-5 1-6 0-11-5-9-10z\" fill=\"#FF7A1A\" stroke=\"#171320\" stroke-width=\"2.5\" stroke-linejoin=\"round\"/><path d=\"M12 20c3 2 5 2 8-1M28 20c-3 2-5 2-8-1\" fill=\"none\" stroke=\"#C84F0E\" stroke-width=\"1.5\" stroke-linecap=\"round\"/><circle cx=\"20\" cy=\"19.5\" r=\"5\" fill=\"#F2E8D8\" stroke=\"#171320\" stroke-width=\"2\"/><circle cx=\"18.2\" cy=\"18.8\" r=\"1.1\" fill=\"#171320\"/><circle cx=\"21.8\" cy=\"18.8\" r=\"1.1\" fill=\"#171320\"/><path d=\"M18.5 22.5h3\" stroke=\"#171320\" stroke-width=\"1.2\"/>',\n  bunny:")
rep("  if (w.eye === 'patch') s += '<path d=\"M15 16.5l18 6\"", "  if (w.head === 'skull') s += '<path d=\"M14 9c3-3 7-2 9 1 2-3 6-4 9-1 1 3-2 6-6 6 0 0-2 0-3-.6-1 .6-3 .6-3 .6-4 0-7-3-6-6z\" fill=\"#FF7A1A\" stroke=\"' + O + '\" stroke-width=\"1.6\" stroke-linejoin=\"round\"/><circle cx=\"23\" cy=\"10.5\" r=\"3\" fill=\"#F2E8D8\" stroke=\"' + O + '\" stroke-width=\"1.2\"/><circle cx=\"22\" cy=\"10\" r=\".7\" fill=\"' + O + '\"/><circle cx=\"24\" cy=\"10\" r=\".7\" fill=\"' + O + '\"/>'; if (false) s += '<path d=\"M24 12.5c6.4 0 10.4 4.4 10.4 10.3 0 3.8-1.8 6.4-3.8 8V35H17.4v-4.2c-2-1.6-3.8-4.2-3.8-8 0-5.9 4-10.3 10.4-10.3z\" fill=\"#F2E8D8\"/><ellipse cx=\"19.6\" cy=\"23\" rx=\"2.6\" ry=\"2.9\" fill=\"' + O + '\"/><ellipse cx=\"28.4\" cy=\"23\" rx=\"2.6\" ry=\"2.9\" fill=\"' + O + '\"/><path d=\"M24 25.5l-1.4 2.8h2.8z\" fill=\"' + O + '\"/><path d=\"M20.5 31v3M23 31v3.5M25.5 31v3.5M28 31v3\" stroke=\"' + O + '\" stroke-width=\"1.3\" stroke-linecap=\"round\"/>';\n  if (w.eye === 'patch') s += '<path d=\"M15 16.5l18 6\"")
rep("Math.random() < 0.14 ? 'glasses' : Math.random() < 0.1 ? 'hockey' : null,", "Math.random() < 0.14 ? 'glasses' : Math.random() < 0.1 ? 'hockey' : null,")

rep("const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat', 'tiara', 'bunny'];", "const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat', 'tiara', 'bunny', 'skull'];")
# ---- the bunny ears' band round the head ----
rep("bunny: window.__bunnyFit || { s: 0.78, y: -0.12, rx: -0.08, rz: 0.04 },", "bunny: window.__bunnyFit || { s: 0.92, y: -0.42, rx: -0.06, rz: 0.03 },")

# ---- finds come half again as often ----
rep("unlockItem(gift.id); store.itemIn = 4 + Math.floor(Math.random() * 5); save();", "unlockItem(gift.id); store.itemIn = 2 + Math.floor(Math.random() * 4); save();")

# ---- the simple things are for sale outright; the hats and the season's finds must be found first ----
rep("const PRICE = w => PRICES[w.id] ||", "const needFind = w => !!w.season || w.slot === 'head'; // (what has to be found on a canvas before it is for sale)\nconst PRICE = w => PRICES[w.id] ||")
rep("const items = ITEMS.filter(w => w.cat === c && !bought(w.id)); if (!items.length) continue; any = true;\n    h += '<p class=\"shcat\">' + label + '</p>' + items.map(w => { const found = owns(w.id), broke = found && n < PRICE(w), where = WEAR_WHERE[w.stage];",
    "const items = ITEMS.filter(w => w.cat === c && !bought(w.id)); if (!items.length) continue; any = true;\n    h += '<p class=\"shcat\">' + label + '</p>' + items.map(w => { const found = owns(w.id) || !needFind(w), broke = found && n < PRICE(w), where = WEAR_WHERE[w.stage];")
rep("  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); shopNote('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + ' first.'); return; }", "  if (!owns(w.id) && needFind(w)) { AU.nope(); kick(b, 'nope'); shopNote('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + ' first.'); return; }")
rep("function buyItem(id) { const w = ITEMS.find(x => x.id === id); if (!w || !OWNED.has(id) || BOUGHT.has(id) || store.drops < PRICE(w)) return false; store.drops -= PRICE(w); BOUGHT.add(id);", "function buyItem(id) { const w = ITEMS.find(x => x.id === id); if (!w || (!OWNED.has(id) && needFind(w)) || BOUGHT.has(id) || store.drops < PRICE(w)) return false; store.drops -= PRICE(w); OWNED.add(id); store.owned = [...OWNED]; BOUGHT.add(id);")
rep("const left = ITEMS.filter(w => w.stage === stageSet() && !owns(w.id)); if (!left.length) return;", "const left = ITEMS.filter(w => needFind(w) && w.stage === stageSet() && !owns(w.id)); if (!left.length) return;")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
