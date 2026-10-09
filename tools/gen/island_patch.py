# Palette Island, livelier:
#  - sand you can see the grains of: tens of thousands of little grains in a dozen tones, each lit from the top left with its own
#    bump in the relief, the odd glassy one that glints in the sun, softer wind ripples, damp and dry drifts
#  - vines: hanging off the blocks' edges and corners, creeping onto the sand, climbing the palm columns and the rock planters
#  - tropical bushes: leafy clumps with a few broad fronds, at the feet of the blocks and round the planters
#  - the palms and bushes shake: bump into a palm's column, land on top of it, roll through a bush, or pound nearby and they sway
#    back and forth and settle (a small spring per tree, bent in the vertex shader; one draw for all of them), with a breeze always
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# ---------------- sand
i = s.index("  // Palette Island sand: wind ripples you can feel, a few shells\n  sand: () => makeSurf(512,")
j = s.index("  }, 1.6),\n", i) + len("  }, 1.6),\n")
s = s[:i] + r"""  // Palette Island sand: grains you can see (a dozen tones, each a lit bead with its own bump, the odd glassy one that glints),
  // damp and dry drifts, soft wind ripples, a few shells
  sand: () => makeSurf(HI ? 1024 : 512, (c, h, r, S) => {
    const R = rng(141), q = S / 512;
    c.fillStyle = '#E4C994'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.5); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.95); r.fillRect(0, 0, S, S);
    for (let i = 0; i < 26; i++) { const x = R() * S, y = R() * S, rad = S * (0.06 + R() * 0.14), dry = R() < 0.5; wrapAt(S, x, y, rad, (X, Y) => blob(c, X, Y, rad, dry ? 'rgba(248,232,196,0.28)' : 'rgba(184,146,96,0.22)')); }
    for (let i = 0; i < 26; i++) { const y0 = R() * S, a = (3 + R() * 5) * q, k = 1 + (R() * 2 | 0), ph = R() * 6.28, w = (3 + R() * 4) * q;
      for (const [g, col, dy] of [[c, rgbS(176 + R() * 18, 136 + R() * 18, 88 + R() * 12, 0.12 + R() * 0.08), 0], [c, 'rgba(255,247,226,0.16)', -3 * q], [h, grayA(0.38, 0.7), 2 * q], [h, grayA(0.64, 0.7), -2.5 * q]]) {
        g.strokeStyle = col; g.lineWidth = w; for (const off of [-S, 0, S]) { g.beginPath(); for (let x = 0; x <= S; x += 4) { const y = y0 + off + dy + Math.sin(x / S * 6.2832 * k + ph) * a; x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); } } }
    // the grains: little sprites, lighter up and to the left, darker at the far edge; each one a bump in the relief
    const tones = [[[240, 220, 176], 9], [[230, 204, 156], 9], [[218, 188, 138], 8], [[248, 236, 206], 6], [[204, 170, 120], 6], [[252, 246, 230], 3], [[186, 150, 104], 4], [[232, 182, 150], 2], [[214, 196, 172], 3], [[150, 122, 92], 1.4], [[96, 82, 74], 0.6], [[255, 255, 250], 1]];
    const tw = tones.reduce((a, t) => a + t[1], 0), pickTone = () => { let v = R() * tw; for (const t of tones) if ((v -= t[1]) <= 0) return t[0]; return tones[0][0]; };
    const spr = (rad, rgb) => { const n = Math.ceil(rad * 2 + 2), cv = document.createElement('canvas'); cv.width = cv.height = n; const g = cv.getContext('2d'), m = n / 2, gr = g.createRadialGradient(m - rad * 0.35, m - rad * 0.4, rad * 0.1, m, m, rad);
      gr.addColorStop(0, rgbS(Math.min(255, rgb[0] * 1.12 + 14), Math.min(255, rgb[1] * 1.12 + 14), Math.min(255, rgb[2] * 1.12 + 14))); gr.addColorStop(0.6, rgbS(...rgb)); gr.addColorStop(0.92, rgbS(rgb[0] * 0.72, rgb[1] * 0.7, rgb[2] * 0.68)); gr.addColorStop(1, rgbS(rgb[0] * 0.72, rgb[1] * 0.7, rgb[2] * 0.68, 0));
      g.fillStyle = gr; g.beginPath(); g.ellipse(m, m, rad, rad * (0.78 + R() * 0.22), R() * 3, 0, 6.2832); g.fill(); return cv; };
    const bump = (rad, top) => { const n = Math.ceil(rad * 2 + 2), cv = document.createElement('canvas'); cv.width = cv.height = n; const g = cv.getContext('2d'), m = n / 2, gr = g.createRadialGradient(m, m, 0, m, m, rad); gr.addColorStop(0, grayA(top, 1)); gr.addColorStop(0.7, grayA(0.5 + (top - 0.5) * 0.5, 0.8)); gr.addColorStop(1, grayA(0.5, 0)); g.fillStyle = gr; g.fillRect(0, 0, n, n); return cv; };
    const SPR = [], BMP = [], GL = bump(2.2 * q, 0.22), sizes = [1.5, 2, 2.6, 3.3, 4.2].map(v => v * q);
    for (let k = 0; k < 60; k++) SPR.push(spr(sizes[k % sizes.length] * (0.85 + R() * 0.3), pickTone()));
    for (const z of sizes) BMP.push(bump(z, 0.86));
    const N = Math.round(32000 * (S / 1024) * (S / 1024)), put2 = (g, im, x, y) => { const w = im.width; g.drawImage(im, x - w / 2, y - w / 2); if (x < w) g.drawImage(im, x + S - w / 2, y - w / 2); else if (x > S - w) g.drawImage(im, x - S - w / 2, y - w / 2); if (y < w) g.drawImage(im, x - w / 2, y + S - w / 2); else if (y > S - w) g.drawImage(im, x - w / 2, y - S - w / 2); };
    for (let i = 0; i < N; i++) { const k = (R() * SPR.length) | 0, x = R() * S, y = R() * S; put2(c, SPR[k], x, y); if (HI) { put2(h, BMP[k % sizes.length], x, y); if (R() < 0.07) put2(r, GL, x, y); } }
    for (let i = 0; i < 1400 * q * q; i++) { const v = R(); c.fillStyle = v < 0.5 ? `rgba(130,98,62,${0.18 + v * 0.3})` : `rgba(255,252,240,${0.25 + v * 0.3})`; c.fillRect(R() * S, R() * S, q, q); }
    for (let i = 0; i < 30; i++) { const x = R() * S, y = R() * S, col = ['rgba(255,232,224,0.95)', 'rgba(250,246,236,0.95)', 'rgba(205,192,180,0.9)'][i % 3], rx = (2 + R() * 2.4) * q, ry = (1.2 + R() * 1.4) * q, rot = R() * 3;
      wrapAt(S, x, y, 7 * q, (X, Y) => { c.fillStyle = col; c.beginPath(); c.ellipse(X, Y, rx, ry, rot, 0, 6.2832); c.fill(); h.fillStyle = gray(0.9); h.beginPath(); h.ellipse(X, Y, rx, ry, rot, 0, 6.2832); h.fill(); r.fillStyle = gray(0.4); r.beginPath(); r.ellipse(X, Y, rx, ry, rot, 0, 6.2832); r.fill(); }); }
  }, 2.6),
""" + s[j:]

# ---------------- the theme: vines on the blocks, the columns and the planters
rep("ivy: { drum: 0.45, col: 0.4, tint: 0xD8FFC0 }, edge: 0xFFFFFF, edgeK: 1.1, cloud: 0xFFFFFF }",
    "ivy: { edge: 0.55, drum: 0.6, col: 0.55, tint: 0xD8FFC0 }, bushes: true, edge: 0xFFFFFF, edgeK: 1.1, cloud: 0xFFFFFF }")

# ---------------- the swaying module (uniforms, materials, springs, hits)
rep("// ---------- clouds and far-off canvases ----------",
"""// ---------- things that sway: Palette Island's palms and bushes shake when a blob bumps them, lands on them or pounds nearby ----------
// each one is a little spring (how far its top is bent, and how fast); the vertex shader bends its geometry by that, more the higher up
const SWAY_N = 24, swayU = { value: Array.from({ length: SWAY_N }, () => new THREE.Vector3()) }, SWAY_T = { value: 0 }, swayItems = [];
const SWAY_VS = 'attribute vec2 aSway; uniform vec3 uSway[' + SWAY_N + ']; uniform float uSwayT;\\n';
const SWAY_BEND = '#include <begin_vertex>\\nif (aSway.x >= 0.0) { vec3 sw = uSway[int(aSway.x + 0.5)]; vec2 wd = vec2(sin(uSwayT * 1.1 + transformed.x * 0.37 + sw.z), sin(uSwayT * 0.87 + transformed.z * 0.41)) * 0.03; vec2 b = sw.xy + wd; transformed.xz += b * aSway.y; transformed.y -= 0.3 * dot(b, b) * aSway.y; }';
function swayHook(sh) { if (HI) aoHook(sh); sh.uniforms.uSway = swayU; sh.uniforms.uSwayT = SWAY_T; sh.vertexShader = SWAY_VS + sh.vertexShader.replace('#include <begin_vertex>', SWAY_BEND); }
const swayMat = m => { const c = m.clone(); c.onBeforeCompile = swayHook; c.customProgramCacheKey = () => 'sway-' + m.type; return c; };
// a new tree or bush: kind 'palm' (on a column: x, z, its radius r, the column's top y0, the tree's height h) or 'bush' (r its reach)
function addSway(kind, x, z, r, y0, h) { if (swayItems.length >= SWAY_N) return -1; const it = { kind, x, z, r, y0, h, bx: 0, bz: 0, vx: 0, vz: 0, cool: 0, on: 0, ph: Math.random() * 6.28,
  k: kind === 'palm' ? 16 : 85, c: kind === 'palm' ? 1.5 : 7, max: kind === 'palm' ? 0.9 : 0.28 }; swayItems.push(it); return swayItems.length - 1; }
function swayKick(it, dx, dz, k) { const l = Math.hypot(dx, dz) || 1; it.vx += dx / l * k; it.vz += dz / l * k; }
// a pound, a giant slam, an orb going: everything nearby is pushed away from it
function swayBlast(x, z, R) { for (const it of swayItems) { const dx = it.x - x, dz = it.z - z, d = Math.hypot(dx, dz), reach = R * 1.4 + it.r; if (d < reach) swayKick(it, dx || 0.01, dz, (it.kind === 'palm' ? 2.6 : 1.8) * (1 - d / reach) + 0.3); } }
function updateSway(dt) {
  SWAY_T.value = clock; if (!swayItems.length) return; dt = Math.min(dt, 0.05);
  for (let i = 0; i < swayItems.length; i++) {
    const it = swayItems[i]; it.cool = Math.max(0, it.cool - dt);
    if (state === 'play' || state === 'dead') for (let n = 0; n < ACTIVE.length; n++) {
      const D = ACTIVE[n]; if (D.st !== 'play') continue; const rad = PR * (D.giantT > 0 ? GIANT_K : 1), dx = it.x - D.x, dz = it.z - D.z, d = Math.hypot(dx, dz), bit = 1 << n;
      if (it.kind === 'palm') {
        // rolling into its column, or landing on top of it
        if (it.cool <= 0 && d < it.r + rad + 0.18 && D.y < it.y0 - 0.25 && D.spd > 1.6) { swayKick(it, dx, dz, Math.min(2.6, 0.5 + D.spd * 0.22) * (D.giantT > 0 ? 1.6 : 1)); it.cool = 0.4; }
        const on = d < it.r + 0.1 && D.y > it.y0 - 0.15 && D.y < it.y0 + 0.35 && !D.air;
        if (on && !(it.on & bit)) swayKick(it, Math.random() - 0.5, Math.random() - 0.5, 1.8);
        it.on = on ? it.on | bit : it.on & ~bit;
      } else if (it.cool <= 0 && d < it.r + rad * 0.8 && Math.abs(D.y - it.y0) < 0.7 && D.spd > 0.8) {
        // rolling through a bush rustles it the way you're going
        swayKick(it, Math.sin(D.yaw), Math.cos(D.yaw), Math.min(1.8, 0.4 + D.spd * 0.2)); it.cool = 0.22;
      }
    }
    const ax = -it.k * it.bx - it.c * it.vx, az = -it.k * it.bz - it.c * it.vz; it.vx += ax * dt; it.vz += az * dt; it.bx += it.vx * dt; it.bz += it.vz * dt;
    const m = Math.hypot(it.bx, it.bz); if (m > it.max) { it.bx *= it.max / m; it.bz *= it.max / m; }
    swayU.value[i].set(it.bx, it.bz, it.ph);
  }
}
// give a piece of a tree or bush its slot and how much it bends (0 at its foot, up to ~1 at the top, more out at frond tips)
function swayAttr(g, slot, x, z, y0, h) {
  const P = g.attributes.position, a = new Float32Array(P.count * 2);
  for (let i = 0; i < P.count; i++) { const up = clamp((P.getY(i) - y0) / h, 0, 1.25), out = Math.min(1, Math.hypot(P.getX(i) - x, P.getZ(i) - z) / h); a[i * 2] = slot; a[i * 2 + 1] = up * up + 0.35 * out * up; }
  g.setAttribute('aSway', new THREE.BufferAttribute(a, 2)); return g;
}
function mergeSway(list) {
  const m = mergeGeos(list, true); let n = 0; const sw = new Float32Array(m.attributes.position.count * 2);
  for (const g of list) { const ng = g.index ? g.toNonIndexed() : g, a = ng.attributes.aSway.array; sw.set(a, n); n += a.length; }
  m.setAttribute('aSway', new THREE.BufferAttribute(sw, 2)); return m;
}

// ---------- clouds and far-off canvases ----------""")
# pounds and slams (and the orb going) push the trees about
rep("function shockwave(x, y, z, radius, color) {\n", "function shockwave(x, y, z, radius, color) {\n  swayBlast(x, z, radius);\n")
# every frame
rep("  updateSuck(dt); visualBrushes(dt);", "  updateSuck(dt); updateSway(rdt); visualBrushes(dt);")

# ---------------- the stage build: sway materials, palms that sway, bushes, vines
rep("  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0; GLOWS.length = 0; IVY.reset();",
    "  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0; GLOWS.length = 0; IVY.reset(); swayItems.length = 0; for (const v of swayU.value) v.set(0, 0, 0);")
rep("  const put = (mat, g) => { let l = bag.get(mat); if (!l) bag.set(mat, l = []); l.push(g); };",
    """  const put = (mat, g) => { let l = bag.get(mat); if (!l) bag.set(mat, l = []); l.push(g); };
  // swaying pieces go in their own bag (they carry the sway attribute), with the theme's swaying copies of the leaf, trunk and nut materials
  const swayBag = new Map(), putSway = (mat, g, slot, x, z, y0, h) => { if (slot < 0) { put(mat, g); return; } const sm = M.sway && M.sway.get(mat) || mat; let l = swayBag.get(sm); if (!l) swayBag.set(sm, l = []); l.push(swayAttr(g, slot, x, z, y0, h)); };
  const palmAt = (x, y, z, h, s, lean, rot, kind, r) => { const Pm = palmParts(x, y, z, h, s, lean, rot, R), slot = addSway('palm', x, z, kind === 'corner' ? 0.3 : r, y, h + s * 0.6);
    Pm.trunk.forEach(g => putSway(M.palm, g, slot, x, z, y, h)); Pm.fronds.forEach(g => putSway(M.frond, g, slot, x, z, y, h)); Pm.nuts.forEach(g => putSway(M.nut, g, slot, x, z, y, h)); };""")
rep("      else if (T.id === 'island' && kind === 'column') { const Pm = palmParts(cx, top, cz, 2.4 + R() * 1.4, 1.25, 0.18 + R() * 0.25, R() * 6.28, R); Pm.trunk.forEach(g => put(M.palm, g)); Pm.fronds.forEach(g => put(M.frond, g)); Pm.nuts.forEach(g => put(M.nut, g));",
    "      else if (T.id === 'island' && kind === 'column') { if (T.ivy && R() < T.ivy.col) IVY.climb(cx, cz, rad, top - 0.12, R, 0.3); palmAt(cx, top, cz, 2.4 + R() * 1.4, 1.25, 0.18 + R() * 0.25, R() * 6.28, 'column', rad);")
rep("      else if (T.id === 'island' && kind === 'drum') { for (let k = 0; k < 5; k++) {",
    "      else if (T.id === 'island' && kind === 'drum') { if (T.ivy && R() < T.ivy.drum) IVY.climb(cx, cz, rad, top - 0.05, R, 0.2, 3); for (let k = 0; k < 2; k++) { const a = R() * 6.28; bushAt(cx + Math.cos(a) * (rad + 0.45), cz + Math.sin(a) * (rad + 0.45), 0, 0.7 + R() * 0.35); } for (let k = 0; k < 5; k++) {")
rep("      if (corner) { const Pm = palmParts(x, y, z, 3.4 + (i % 2) * 0.8, 1.35, 0.35, i * 1.7 + 0.6, R); Pm.trunk.forEach(g => put(M.palm, g)); Pm.fronds.forEach(g => put(M.frond, g)); Pm.nuts.forEach(g => put(M.nut, g)); }",
    "      if (corner) palmAt(x, y, z, 3.4 + (i % 2) * 0.8, 1.35, 0.35, i * 1.7 + 0.6, 'corner', 0.3);")
# a bush: a few leafy lumps and a couple of broad fronds poking out of it, its own spring if there's a slot left
rep("  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, SEG(16), SEG(12)); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };",
    """  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, SEG(16), SEG(12)); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };
  const bushOK = (x, z) => floorAt(x, z) === 0 && Math.abs(x) < ARENA - 0.5 && Math.abs(z) < ARENA - 0.5 && !BOXES.some(o => o[4] <= 0.05 && inR(x, z, o, 0.12)) && !RAMPS.some(rp => inR(x, z, rp, 0.15)) && !POTS.some(p => Math.hypot(p[0] - x, p[2] - z) < 1.3) && !POWER_SPOTS.some(p => Math.hypot(p[0] - x, p[2] - z) < 1.1) && Math.hypot(START.x - x, START.z - z) > 2;
  const bushAt = (x, z, y, sz) => { if (!T.bushes || !bushOK(x, z)) return; const slot = addSway('bush', x, z, 0.45 * sz, y, 0.9 * sz), bm = HI && M.canopy ? M.canopy : M.leaf;
    for (let k = 0, n = 3 + (R() * 3 | 0); k < n; k++) { const a = R() * 6.28, rr = R() * 0.32 * sz, br = (0.24 + R() * 0.18) * sz, bx = x + Math.cos(a) * rr, bz = z + Math.sin(a) * rr, by = y + br * (0.55 + R() * 0.3);
      putSway(k % 2 && !HI ? M.leaf2 : bm, HI ? lumpBall(br, bx, by, bz, 0.85, R) : ball(br, bx, by, bz, 0.85), slot, x, z, y, 0.9 * sz); }
    for (let k = 0, n = 2 + (R() * 3 | 0); k < n; k++) putSway(M.frond, frondGeo(new THREE.Vector3(x + (R() - 0.5) * 0.2 * sz, y + 0.32 * sz, z + (R() - 0.5) * 0.2 * sz), R() * 6.28, (0.55 + R() * 0.3) * sz, 0.16 * sz, 0.8), slot, x, z, y, 0.9 * sz); };""")
# bushes at the feet of the blocks (island), after the blocks are laid out
rep("  // ramps: a sloped top, walled sides, inked edges\n  for (const r of RAMPS) {",
    """  // tropical bushes at the feet of the blocks
  if (T.bushes) for (const b of BOXES) { if (b[4] > 0.05 || b[5] - b[4] < 0.35 || R() > 0.6) continue; const f = (R() * 4) | 0, u = R(), off = 0.55 + R() * 0.2;
    const x = f === 2 ? b[0] - off : f === 3 ? b[1] + off : b[0] + (b[1] - b[0]) * u, z = f === 0 ? b[2] - off : f === 1 ? b[3] + off : b[2] + (b[3] - b[2]) * u; bushAt(x, z, 0, 0.8 + R() * 0.45); }
  // ramps: a sloped top, walled sides, inked edges
  for (const r of RAMPS) {""")
# merge the swaying pieces (one mesh per material), casting with the rest of the stage
rep("  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat);",
    "  for (const [mat, list] of swayBag) { const m = new THREE.Mesh(mergeSway(list), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); shadowG.push(m.geometry); }\n  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat);")
# the materials: swaying copies of the palm's, the fronds', the nuts' and the bushes' (made after the stage patch, so it isn't overwritten)
rep("    for (const k in T.mats) [].concat(T.mats[k]).forEach(aoPatch);\n  } else T.mats.iron = T.mats.dark;",
    """    if (T.bushes) T.mats.canopy = toon(0xC8F0B4, { map: leafTex }, { normalMap: normalFrom(leafTex, 1.3), normalScale: new THREE.Vector2(1.1, 1.1), roughness: 0.6 });
    for (const k in T.mats) [].concat(T.mats[k]).forEach(aoPatch);
  } else T.mats.iron = T.mats.dark;
  if (T.id === 'island') T.mats.sway = new Map(['palm', 'frond', 'nut', 'leaf', 'leaf2', 'canopy'].filter(k => T.mats[k]).map(k => [T.mats[k], swayMat(T.mats[k])]));""")
open(p, 'w').write(s)
print('ok')
