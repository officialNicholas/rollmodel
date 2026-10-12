#!/usr/bin/env python3
"""v246: two new stages from the user's concept art: the Sludge Sewer (a steel platform in a flooded chamber, glowing slime pouring from tunnel
mouths, hazard paint, vents, manhole drums, a glowing drain) and the Fishing Raft (a plank raft at sea: crates under nets, floats, spools,
cargo lifted by buoys, a mast, a crane, a bait shack, a fish on a pole). Each with its own basin (a toxic drum, a barrel with a hand pump),
floor markings, motes, sky, music, a gallery painting and a place in the vote."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui184_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
J = lambda n: open(S + '/tools/stage/' + n).read()
# ---- code: surfaces, themes, the stage engine and the two stages' dressing, the two basins
rep("const surf = id => SURF[id] || (SURF[id] = SURF_PAINT[id]());", "const surf = id => SURF[id] || (SURF[id] = SURF_PAINT[id]());\n" + J('surfaces.js'))
rep("const THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));", J('themes.js') + "const THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));")
rep("// ---------- build the stage ----------", J('engine.js') + J('sewer.js') + J('raft.js') + "// ---------- build the stage ----------")
rep("// turn a station's tall back (spout, lid, dispenser) toward the nearest wall or drop", J('pots.js') + "// turn a station's tall back (spout, lid, dispenser) toward the nearest wall or drop")
rep("  if (T.sand) { sandMat(T.mats.floor); sandMat(T.mats.top); }", "  if (T.mkMats) T.mkMats(T.mats, T);\n  if (T.sand) { sandMat(T.mats.floor); sandMat(T.mats.top); }")
# ---- the look: no sky (stars, moon, sunrise) in an enclosed stage, its floating far canvases and clouds and bats off; slime in place of the sea
rep("for (const it of islands) it.g.visible = !T.day && !T.terrace;", "for (const it of islands) it.g.visible = !T.day && !T.terrace && !T.enclosed; skyU.noSky.value = T.enclosed ? 1 : 0;")
rep("farIsles.visible = T.id === 'island';", "farIsles.visible = T.id === 'island' || !!T.farIsles;")
rep("sea.visible = !!T.sea;", "sea.visible = !!(T.sea || T.slime); seaU.uSlime.value = T.slime ? 1 : 0; seaU.uDeep.value.set(T.seaCol ? T.seaCol[0] : 0x0C6A9A); seaU.uShal.value.set(T.seaCol ? T.seaCol[1] : 0x3CCFD2);")
rep("starK: { value: 1 }, duskK: { value: 0 } };", "starK: { value: 1 }, duskK: { value: 0 }, noSky: { value: 0 } };")
rep("uniform float rain, heat, day, uTime, dayBase, sunAmt, starK, duskK;", "uniform float rain, heat, day, uTime, dayBase, sunAmt, starK, duskK, noSky;")
rep("* (1.0 - rain) * (1.0 - dayBase) * starK;", "* (1.0 - rain) * (1.0 - dayBase) * starK * (1.0 - noSky);")
rep("c += vec3(0.78, 0.74, 1.0) * glow * night;", "c += vec3(0.78, 0.74, 1.0) * glow * night * (1.0 - noSky);")
rep("c = mix(c, moonC, disc * (1.0 - day * 0.85) * (1.0 - rain * 0.6) * (1.0 - dayBase));", "c = mix(c, moonC, disc * (1.0 - day * 0.85) * (1.0 - rain * 0.6) * (1.0 - dayBase) * (1.0 - noSky));")
rep("    c = mix(c, cd, day);", "    c = mix(c, cd, day * (1.0 - noSky));")
rep("* 0.6) * day;", "* 0.6) * day * (1.0 - noSky);")
rep("  for (const c of clouds) { if (c.layer) {", "  if (!TH.enclosed) for (const c of clouds) { if (c.layer) {")
rep("const on = TH.day ? (TH.sea ? 1 : 0) : 1 - Math.min(1, dayK * 1.6);", "const on = TH.enclosed ? 0 : TH.day ? (TH.sea ? 1 : 0) : 1 - Math.min(1, dayK * 1.6);")
rep("uPl: { value: Array.from({ length: 8 }, () => new THREE.Vector2(999, 999)) } });", "uPl: { value: Array.from({ length: 8 }, () => new THREE.Vector2(999, 999)) }, uSlime: { value: 0 } });")
rep("uniform vec2 uPl[8]; varying vec3 vW;", """uniform vec2 uPl[8]; uniform float uSlime; varying vec3 vW;""")
rep("  float boxD(vec2 p, vec2 c, float h){ vec2 d = abs(p - c) - h; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }\n  void main(){\n    vec2 p = vW.xz; float t = uTime;",
"""  float boxD(vec2 p, vec2 c, float h){ vec2 d = abs(p - c) - h; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
  // the Sludge Sewer's pool: thick glowing slime, slow swells of brighter green, a darker skin drifting on it, bubbles swelling and
  // bursting into rings, a wet sheen, froth where it laps against the platform and whatever stands in it
  vec3 slimeCol(vec2 p, float t, float d, float calm, vec3 V){
    float n1 = svn(p * 0.32 + vec2(t * 0.05, -t * 0.035)), n2 = svn(p * 0.9 - vec2(t * 0.09, t * 0.07)), n3 = svn(p * 2.2 + t * 0.15);
    vec3 col = mix(vec3(0.07, 0.42, 0.04), vec3(0.46, 1.15, 0.14), smoothstep(0.15, 0.95, n1 * 0.7 + n2 * 0.3)) * (0.9 + 0.2 * n3);
    float sk = smoothstep(0.58, 0.72, svn(p * 0.45 + vec2(t * 0.02, t * 0.01)) * 0.65 + n2 * 0.35); col = mix(col, vec3(0.16, 0.3, 0.05), sk * 0.55);
    vec2 bc = p * 1.25, bi = floor(bc), bf = fract(bc) - 0.5 - (vec2(sh2(bi + 3.1), sh2(bi + 7.7)) - 0.5) * 0.5;
    float h = sh2(bi), ph = fract(t * (0.18 + h * 0.3) + h * 9.0), on = step(0.62, h), br = (0.1 + 0.16 * h) * smoothstep(0.0, 0.7, ph);
    float bub = on * (1.0 - smoothstep(br - 0.03, br, length(bf))) * step(ph, 0.8);
    float rg = on * step(0.8, ph) * (1.0 - smoothstep(0.0, 0.025, abs(length(bf) - br * (1.0 + (ph - 0.8) * 8.0)))) * (1.0 - (ph - 0.8) * 5.0);
    col = mix(col, vec3(0.62, 1.2, 0.3), bub * 0.6); col += vec3(0.5, 0.9, 0.3) * rg * 0.8;
    col += vec3(0.12, 0.2, 0.08) * pow(1.0 - clamp(V.y, 0.0, 1.0), 3.0);
    float foam = smoothstep(0.65, 0.0, d + (n3 - 0.5) * 0.45) * (1.0 - calm); col = mix(col, vec3(0.78, 1.15, 0.5), clamp(foam * 0.75, 0.0, 1.0));
    return col;
  }
  void main(){
    vec2 p = vW.xz; float t = uTime;""")
rep("    col += calm * uSunC * 0.08 * rl * rl;\n    gl_FragColor = vec4(col, 1.0);", "    col += calm * uSunC * 0.08 * rl * rl;\n    if (uSlime > 0.5) col = slimeCol(p, t, d, calm, V);\n    gl_FragColor = vec4(col, 1.0);")
# ---- the stage builder: hand the theme its tools and call its hooks as each part is built
rep("  floaters.length = 0; flames.length = 0;", "  floaters.length = 0; flames.length = 0; STAGE_ANIM.length = 0; coneReset(); steamReset();")
rep("  // floor: one panel with holes (square or round), edged in the theme's wall material",
"""  // a theme that dresses itself (the sewer, the raft): its tools, and the hooks it hands back
  const DXB = vcBag(), DX = T.dress ? T.dress({ T, M, R, put, us, ARENA, vc: (mat, g, c) => DXB.add(mat, g, c), glow: (x, y, z, sz, c) => GLOWS.push([x, y, z, sz, c]), light: (x, y, z, r, c, k) => LIGHTS.push({ x, y, z, r, c: new THREE.Color(c), k }),
    add: o => stageGroup.add(o), anim: a => STAGE_ANIM.push(a), hull: g => hulls.push(g), cone: coneAdd, steam: steamAdd, prop: knAdd,
    // a block's faces that stand on open floor (not against another block, a ramp, a hole or the edge): where they are, which way they face, their length
    faces: b => { const w = b[1] - b[0], d = b[3] - b[2], cx = (b[0] + b[1]) / 2, cz = (b[2] + b[3]) / 2, out = [];
      for (const [fx, fz, nx, nz, L] of [[cx, b[2], 0, -1, w], [cx, b[3], 0, 1, w], [b[0], cz, -1, 0, d], [b[1], cz, 1, 0, d]]) { const px = fx + nx * 0.35, pz = fz + nz * 0.35;
        if (L < 0.5 || floorAt(px, pz) !== 0 || Math.abs(px) > ARENA - 0.25 || Math.abs(pz) > ARENA - 0.25 || BOXES.some(o => o !== b && o[4] <= 0.05 && inR(px, pz, o, 0.02)) || RAMPS.some(rp => inR(px, pz, rp, 0.05))) continue;
        out.push({ fx, fz, nx, nz, L, tx: nz ? 1 : 0, tz: nx ? 1 : 0 }); } return out; } }) : null;
  // floor: one panel with holes (square or round), edged in the theme's wall material""")
rep("  HOLES.forEach(holeEdge);", "  HOLES.forEach(holeEdge); if (DX && DX.hole) HOLES.forEach(hh => DX.hole(hh));")
rep("    const mats = circ ? [T.id === 'island'", "    const mats = (circ && DX && DX.roundMats && DX.roundMats(b, kind)) || (circ ? [T.id === 'island'")
rep("M.side, M.top, M.dark] : [M.side, M.side, M.top, M.dark, M.side, M.side];", "M.side, M.top, M.dark] : [M.side, M.side, M.top, M.dark, M.side, M.side]);")
rep("      floaters.push({ b, mats: own, hull: hm, k: 1, last: 1 });\n      continue;", "      floaters.push({ b, mats: own, hull: hm, k: 1, last: 1 });\n      if (DX) { if (circ && DX.round) DX.round(b, kind, cx, cz, rad, h, b[5]); else if (!circ && DX.float) DX.float(b, { w, d, h, cx, cz }); }\n      continue;")
rep("    if (!planter) { putAll(g, mats); hulls.push(o); }", "    if (!planter && !(DX && DX.skipBody && DX.skipBody(b, kind))) { putAll(g, mats); hulls.push(o); }")
rep("    // the theme dresses the round pieces", "    if (DX && DX.box && !grave && !circ) DX.box(b, { w, d, h, cx, cz });\n    // the theme dresses the round pieces")
rep("      if (T.id === 'studio' && kind === 'drum') {", "      if (DX && DX.round) DX.round(b, kind, cx, cz, rad, h, top);\n      else if (T.id === 'studio' && kind === 'drum') {")
rep("    tg.setIndex([0, 2, 1, 0, 3, 2]); tg.computeVertexNormals(); put(M.top, tg);", "    tg.setIndex([0, 2, 1, 0, 3, 2]); tg.computeVertexNormals(); put(DX && DX.rampTop || M.top, tg);")
rep("    const lowAtStart = r[5] < r[6];", "    if (DX && DX.ramp) DX.ramp(r, h);\n    const lowAtStart = r[5] < r[6];")
rep("    put(M.dark, HI ? worldUV(at(rbox(2.6, 0.7, 2.6, 0.12), x, -0.6, z), us) : at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push(at(new THREE.BoxGeometry(2.74, 0.84, 2.74), x, -0.6, z));",
    "    if (!(DX && DX.noPlinth)) { put(M.dark, HI ? worldUV(at(rbox(2.6, 0.7, 2.6, 0.12), x, -0.6, z), us) : at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push(at(new THREE.BoxGeometry(2.74, 0.84, 2.74), x, -0.6, z)); }")
rep("    if (T.id === 'studio') {", "    if (DX && DX.spot) DX.spot(x, z, i, corner, y);\n    else if (T.id === 'studio') {")
rep("  setMotes(T); glowBatch.set(GLOWS);", "  if (DX && DX.outer) DX.outer(); if (DX && DX.props) DX.props(); DXB.flush(stageGroup, shadowG);\n  setMotes(T); glowBatch.set(GLOWS);")
rep("g.clearRect(0, 0, S, S); g.lineCap = 'round';\n    if (T.id === 'crypt')", "g.clearRect(0, 0, S, S); g.lineCap = 'round';\n    if (T.decalDraw) T.decalDraw(g, S, c, r);\n    else if (T.id === 'crypt')")
rep("    if (id === 'studio') {\n      // a pencil sketch", "    if (T.scatDraw) T.scatDraw(cell, g, r, { blob, disc, crack, star, leaf, flower });\n    else if (id === 'studio') {\n      // a pencil sketch")
rep("  SWAY_T.value = clock; sandT.value = clock;", "  SWAY_T.value = clock; sandT.value = clock; stageTick(dt);")
# ---- a theme can name its centerpiece (the sewer's great drain) and keep the drifting clouds out (they make no sense underground)
rep("  const arch = pick(EZ ? ['plaza', 'plaza', 'spire', 'open', 'open', 'rotunda'] : ['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);",
    "  const arch = theme.arch || pick(EZ ? ['plaza', 'plaza', 'spire', 'open', 'open', 'rotunda'] : ['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);")
rep("  const clouds = [], nC = sym === 'free' ? ri(2, 4) : ri(1, 2), hw = 1.35;", "  const clouds = [], nC = theme.noClouds ? 0 : sym === 'free' ? ri(2, 4) : ri(1, 2), hw = 1.35;")
# ---- a pound throws the cones about; a splash into slime is green
rep("  const missile = !!D.missile, giant = D.giantT > 0, R = slamRadius(D), koR = R + PR;\n", "  const missile = !!D.missile, giant = D.giantT > 0, R = slamRadius(D), koR = R + PR;\n  coneBlast(D.x, D.y, D.z, R);\n")
rep("  waterDrop = waterDrop || colMat(0xEAF8FF);\n  for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283, sp = 1.5 + Math.random() * 3.5; spawnPart(x, WATER_Y + 0.1, z, Math.cos(a) * sp, 4 + Math.random() * 4, Math.sin(a) * sp, 0.6 + Math.random() * 0.4, waterDrop,",
    "  waterDrop = waterDrop || colMat(0xEAF8FF); const dropM = TH.slime ? (coneDrop = coneDrop || colMat(0x9CFF4A)) : waterDrop;\n  for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283, sp = 1.5 + Math.random() * 3.5; spawnPart(x, WATER_Y + 0.1, z, Math.cos(a) * sp, 4 + Math.random() * 4, Math.sin(a) * sp, 0.6 + Math.random() * 0.4, dropM,")
# ---- a theme can keep the scattered markings off a piece of its own (the sewer's drain grate)
rep("    if (!ok) continue;\n    const pg = new THREE.PlaneGeometry(sz, sz), uv = pg.attributes.uv,", "    if (ok && DX && DX.noScatter && DX.noScatter(x, z, y)) ok = false;\n    if (!ok) continue;\n    const pg = new THREE.PlaneGeometry(sz, sz), uv = pg.attributes.uv,")
# ---- motes, cloud tint, music
rep("  blank: { cols: [0x9FD8FF, 0xFFC0E0, 0xFFE38A], size: 0.26, rise: 0.06, blink: 0.4, sway: 0.7 },", "  blank: { cols: [0x9FD8FF, 0xFFC0E0, 0xFFE38A], size: 0.26, rise: 0.06, blink: 0.4, sway: 0.7 },\n  sewer: { cols: [0x9CFF5A, 0x6AE84A, 0xD8FF8A], size: 0.42, rise: 0.22, blink: 0.5, sway: 0.5 },\n  raft: { cols: [0xFFFFFF, 0xE6F6FF], size: 0.2, rise: 0.05, blink: 0.55, sway: 0.9 },")
rep("island: 0xFFFFFF, blank: 0xF4F5F8 };", "island: 0xFFFFFF, blank: 0xF4F5F8, sewer: 0x8EA090, raft: 0xFFFFFF };")
rep("const musicStyleOf = id => id === 'island' ? 'tropical' : ['crypt', 'cathedral', 'manor'].includes(id) ? 'spooky' : 'pop';", "const musicStyleOf = id => id === 'island' || id === 'raft' ? 'tropical' : ['crypt', 'cathedral', 'manor', 'sewer'].includes(id) ? 'spooky' : 'pop';")
rep("const stageSet = () => !TH ? null : TH.id === 'island' ? 'island' : TH.id === 'blank' ? 'blank' : ['crypt', 'cathedral', 'manor'].includes(TH.id) ? 'halloween' : null;", "const stageSet = () => !TH ? null : TH.id === 'island' || TH.id === 'raft' ? 'island' : TH.id === 'blank' ? 'blank' : ['crypt', 'cathedral', 'manor', 'sewer'].includes(TH.id) ? 'halloween' : null;")
# ---- the basins
rep("const potWord = () => TH.pot === 'can' ? 'paint can' : TH.pot === 'tiki' || TH.pot === 'tank' ? 'paint tub' : 'coffin';", "const potWord = () => TH.pot === 'can' ? 'paint can' : TH.pot === 'tiki' || TH.pot === 'tank' ? 'paint tub' : TH.pot === 'drum' ? 'paint drum' : TH.pot === 'barrel' ? 'barrel' : 'coffin';")
rep("reason === 'coffin' && (TH.pot === 'tiki' || TH.pot === 'tank') ?", "reason === 'coffin' && (TH.pot === 'tiki' || TH.pot === 'tank' || TH.pot === 'drum' || TH.pot === 'barrel') ?")
rep("const makePot = TH.pot === 'can' ? makePaintCan : TH.pot === 'tiki' ? makeTiki : TH.pot === 'tank' ? makeTank : makeCoffin;", "const makePot = TH.pot === 'can' ? makePaintCan : TH.pot === 'tiki' ? makeTiki : TH.pot === 'tank' ? makeTank : TH.pot === 'drum' ? makeDrum : TH.pot === 'barrel' ? makeBarrel : makeCoffin;")
# ---- the stage list, the vote, the gallery
rep("const STAGE_THEMES = { island: ['island'], blank: ['blank'], crypt: ['crypt'], cathedral: ['cathedral'], manor: ['manor'] }, STAGE_KEY = { island: 'isl', blank: 'blk', crypt: 'cry', cathedral: 'cat', manor: 'man' };",
    "const STAGE_THEMES = { island: ['island'], blank: ['blank'], sewer: ['sewer'], raft: ['raft'], crypt: ['crypt'], cathedral: ['cathedral'], manor: ['manor'] }, STAGE_KEY = { island: 'isl', blank: 'blk', sewer: 'sew', raft: 'raf', crypt: 'cry', cathedral: 'cat', manor: 'man' };")
rep("let stageSel = ['island', 'blank', 'crypt', 'cathedral', 'manor'].includes(store.stage) ? store.stage : 'season';", "let stageSel = ['island', 'blank', 'sewer', 'raft', 'crypt', 'cathedral', 'manor'].includes(store.stage) ? store.stage : 'season';")
rep("const VOTE_STAGES = ['island', 'blank', 'crypt', 'cathedral', 'manor'];", "const VOTE_STAGES = ['island', 'blank', 'sewer', 'raft', 'crypt', 'cathedral', 'manor'];")
art = {k: open(S + '/tools/stage/art/' + k + '.b64').read().strip() for k in ('sewer', 'raft')}
tile = lambda k, name: '\n        <button class="world" type="button" data-s="' + k + '"><span class="frame"><img class="art" src="data:image/webp;base64,' + art[k] + '" alt="" width="720" height="495" decoding="async"><i class="wcheck" aria-hidden="true"></i></span><span class="plaque"><b class="wn">' + name + '</b></span></button>'
rep('<span class="plaque"><b class="wn">Blank Canvas</b></span></button>', '<span class="plaque"><b class="wn">Blank Canvas</b></span></button>' + tile('sewer', 'Sludge Sewer') + tile('raft', 'Fishing Raft'))
rep('<div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i></div>', '<div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>')
rep('<p class="ver">Version 245</p>', '<p class="ver">Version 246</p>')
open(DST, 'w').write(s)
print('ui185 ok', n0, '->', len(s))
