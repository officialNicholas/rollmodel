# the refill stations: a look for each stage, wired into placement, the visuals, the burst, the blobs (bat wings) and the words
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
ST = open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/gen/stations.js').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
# the old coffin goes; the stations come in its place
a = s.index('function makeCoffin(x, y, z, seed) {'); b = s.index('// boiling water: pale, churning, steaming.')
s = s[:a] + ST.rstrip('\n') + '\n' + s[b:]
# which station a stage gets, turned to stand against a wall
rep("  const makePot = TH.pot === 'can' ? makePaintCan : makeCoffin;\n  POTS.slice(0, cfg.pots).forEach(([x, y, z], i) => { const c = makePot(x, y, z, 200 + i); Object.assign(c, {",
    "  const makePot = TH.pot === 'can' ? makePaintCan : TH.pot === 'tiki' ? makeTiki : TH.pot === 'tank' ? makeTank : makeCoffin;\n  POTS.slice(0, cfg.pots).forEach(([x, y, z], i) => { const c = makePot(x, y, z, 200 + i), yw = potYaw(x, y, z); if (yw !== null) c.g.rotation.y = yw; Object.assign(c, {")
rep("  p.x = x; p.y = y; p.z = z; p.g.position.set(x, y, z); p.g.rotation.y = Math.random() * 6.28; p.ink = 1; p.cool = 0; p.occ = null; p.next = null;",
    "  const yw = potYaw(x, y, z); p.x = x; p.y = y; p.z = z; p.g.position.set(x, y, z); p.g.rotation.y = yw !== null ? yw : Math.random() * 6.28; p.ink = 1; p.cool = 0; p.occ = null; p.next = null; p.lastOcc = null; p.crT = p.jtT = 9; p.dripT = 0;")
# a burst station throws its own kind of planks and its telling piece (a coffin also gives the blob its bat wings)
rep("  p.st = 'down'; p.t = 0; p.g.visible = false; p.ring.visible = false; p.ink = 0; p.next = pickCoffinSpot(p);\n  for (let i = 0; i < 12; i++) {\n    const a = i / 12 * 6.283 + Math.random() * 0.4, sp = 3 + Math.random() * 4, m = new THREE.Mesh(plankG, i % 3 ? coffinWood : coffinRim);",
    "  p.st = 'down'; p.t = 0; p.g.visible = false; p.ring.visible = false; p.ink = 0; p.next = pickCoffinSpot(p); p.lastOcc = null;\n  const DB = p.deb || null; if (p.kind === 'coffin') D.batT = 1.4;\n  for (let i = 0; i < 12; i++) {\n    const a = i / 12 * 6.283 + Math.random() * 0.4, sp = 3 + Math.random() * 4, m = new THREE.Mesh(plankG, i % 3 ? (DB ? DB.a : coffinWood) : (DB ? DB.b : coffinRim));")
rep("  const lid = new THREE.Group(); lid.add(new THREE.Mesh(cofLidG, coffinWood)); lid.add(new THREE.Mesh(cofLidHullG, outlineMat)); lid.add(new THREE.Mesh(cofPanelG, coffinRim));",
    "  let lid; if (DB) lid = DB.lid(); else { lid = new THREE.Group(); lid.add(new THREE.Mesh(cofLidG, coffinWood)); lid.add(new THREE.Mesh(cofLidHullG, outlineMat)); lid.add(new THREE.Mesh(cofPanelG, coffinRim)); }")
# the visuals: the vessel breathes and squashes, the rest stands still; the paint level, the pour, the splash, the jet, each station's own motion, a deeper sink for the tall ones
rep("""    const bs = Math.sin(bo * 9) * bo * 0.22;
    p.inner.scale.set(pulse * pop * (1 + bs), pop * (draining ? 1 - Math.sin(clock * 22) * 0.025 : 1) * (1 - bs), pulse * pop * (1 + bs));
    p.bm.color.copy(CAN_EMPTY).lerp(CAN_INK, p.ink); p.tm.color.copy(CAN_EMPTY_TOP).lerp(CAN_INK_TOP, p.ink); if (p.lm) p.lm.color.copy(p.tm.color);""",
"""    const bs = Math.sin(bo * 9) * bo * 0.22, body = p.tub || p.inner;
    body.scale.set(pulse * (1 + bs), (draining ? 1 - Math.sin(clock * 22) * 0.025 : 1) * (1 - bs), pulse * (1 + bs));
    if (p.tub) p.inner.scale.setScalar(pop); else body.scale.multiplyScalar(pop);
    p.bm.color.copy(CAN_EMPTY).lerp(CAN_INK, p.ink); p.tm.color.copy(CAN_EMPTY_TOP).lerp(CAN_INK_TOP, p.ink); if (p.lm) p.lm.color.copy(p.tm.color); if (p.sm) p.sm.color.copy(p.tm.color);""")
rep("""    p.liq.position.y = 0.07 + 0.32 * p.ink; p.liq.rotation.z = Math.sin(clock * 3 + p.phase) * 0.05 + bs * 0.4; p.drips.scale.y = Math.max(0.01, p.ink);""",
"""    const lv = (p.lv0 === undefined ? 0.07 : p.lv0) + (p.lvK === undefined ? 0.32 : p.lvK) * p.ink;
    p.liq.position.y = lv; p.liq.rotation.z = Math.sin(clock * 3 + p.phase) * 0.05 + bs * 0.4; p.drips.scale.y = Math.max(0.01, p.ink);
    if (p.liqR) { const k = p.liqR(lv); p.liq.scale.set(k, 1, k); }
    if (p.stream) potPour(p, lv, rdt);
    if (p.occ !== p.lastOcc) { if (p.occ) potDive(p, p.occ, lv); if (p.lastOcc) potLeap(p, p.lastOcc); p.lastOcc = p.occ; }
    if (p.crown) potFx(p, lv, rdt);
    if (p.deco) p.deco(p, rdt, bo);""")
rep("    const sp = Math.max(0, sk); p.inner.position.y = -0.78 * sk;", "    const sp = Math.max(0, sk); p.inner.position.y = -(p.sinkD || 0.78) * sk;")
# a blob in a station sits a little higher in the taller ones; bat wings when it flies out of a coffin
rep("V.root.position.set(D.x, D.y + rad * isc * (0.82 + 0.18 * (1 - L.flat)) * (1 - 0.68 * fk) + (hidden ? 0.3 : 0) + hop, D.z);",
    "V.root.position.set(D.x, D.y + rad * isc * (0.82 + 0.18 * (1 - L.flat)) * (1 - 0.68 * fk) + (hidden ? 0.3 + (D.pot && D.pot.lift || 0) : 0) + hop, D.z);")
rep("""  const mk = V.misK || 0; V.body.scale.set(""", """  if (V.bat) { if (D.batT > 0) D.batT = Math.max(0, D.batT - dt); const bt = D.batT || 0; V.bat.visible = bt > 0 && D.st !== 'ko' && D.st !== 'hide';
    if (V.bat.visible) { const env = Math.min(1, (1.4 - bt) / 0.12, bt / 0.22), fl = Math.sin(clock * 34), up = 0.3 + 0.62 * fl; V.bat.scale.setScalar(rad * 1.55 * Math.max(0.01, env)); V.bat.position.set(0, rad * 0.3, -rad * 0.2); V.bat.children[0].rotation.set(0, -0.4, -up); V.bat.children[1].rotation.set(0, 0.4, up); } }
  const mk = V.misK || 0; V.body.scale.set(""")
rep("""const LH = { D: H, drop: cDrop,""", """addBat(VP); addBat(VC);
const LH = { D: H, drop: cDrop,""")
rep("""  return { D, drop, body, mat, xrayMat, U, eyes, mouth, glint, glint2, shadow, look, blinkT: 1.7, blinkK: 0, V: { root: drop, body, mat, hull, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) }, stars: makeStars(), warn, warnFill, foeMark: fm, mark, col: new THREE.Color(color) };""",
"""  const V = { root: drop, body, mat, hull, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) }; addBat(V);
  return { D, drop, body, mat, xrayMat, U, eyes, mouth, glint, glint2, shadow, look, blinkT: 1.7, blinkK: 0, V, stars: makeStars(), warn, warnFill, foeMark: fm, mark, col: new THREE.Color(color) };""")
# the stages' stations, and what they're called
rep("kit: { column: [1, 3], drum: [1, 2], rpad: [0, 1], rotunda: [0, 1] }, fill: 'drum', pot: 'can',", "kit: { column: [1, 3], drum: [1, 2], rpad: [0, 1], rotunda: [0, 1] }, fill: 'drum', pot: 'tiki',")
i = s.index("{ id: 'blank', label: 'Blank Canvas'"); j = s.index("pot: 'can'", i); s = s[:j] + "pot: 'tank'" + s[j + len("pot: 'can'"):]
rep("const potWord = () => TH.pot === 'can' ? 'paint can' : 'coffin';", "const potWord = () => TH.pot === 'can' ? 'paint can' : TH.pot === 'tiki' || TH.pot === 'tank' ? 'paint tub' : 'coffin';")
rep("const koLine = (reason, mine) => reason === 'coffin' && TH.pot === 'can' ? (mine ? 'Canned!' : 'Canned it!') : (mine ? KO_MSG : CPU_KO_MSG)[reason];",
    "const koLine = (reason, mine) => reason === 'coffin' && TH.pot === 'can' ? (mine ? 'Canned!' : 'Canned it!') : reason === 'coffin' && (TH.pot === 'tiki' || TH.pot === 'tank') ? (mine ? 'Dunked!' : 'Dunked it!') : (mine ? KO_MSG : CPU_KO_MSG)[reason];")
# the paint drops' particle pool is made up front with the rest
rep("colMat(0xDDEEFF), colMat(0x4A4052)].forEach(m => partPool(m));", "colMat(0xDDEEFF), colMat(0x4A4052), potDrop()].forEach(m => partPool(m));")
open(p, 'w').write(s)
print('ok')
