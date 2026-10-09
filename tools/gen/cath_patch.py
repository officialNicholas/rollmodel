# The Cathedral at dusk: a low warm sun under a violet sky, brighter ambient, thick polished gold trims and dark skirting,
# glowing rims around every drop, warm light strips along block bases and ramps, candles, and all the stage's flames in one draw.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# ---- the theme ----
i = s.index("  { id: 'cathedral', label: 'The Cathedral',"); j = s.index('\n', i)
old = s[i:j]
kit = old[old.index('kit: '):old.index(", fill: 'column'")]
new = ("  { id: 'cathedral', label: 'The Cathedral', sf: ['marble', 'ashlar'], uv: 0.25, ft: 0xD4D4D4, st: 0xCCC6BC, dt: 0x9E978C, hor: 0x4E3C6C, sky: [0x12143C, 0x342C6C, 0xB97A72], low: 0x261E4C, hemi: [0xA8A2EE, 0x3C2C48], "
       + kit + ", fill: 'column', trim: { c: 0xF2C060, m: 1, r: 0.2, w: 0.22, h: 0.16 }, foot: { c: 0x2A2632, m: 0.35, r: 0.3 }, lamps: { wall: 0.45, up: 0.25, kind: 'torch', col: 0xFFC27A },"
       " strips: 0.5, candles: 0.42, edge: 0xFFC872, edgeK: 2.6, rimLights: 0.5, lip: true, mirror: true,"
       " dusk: { sun: [-20, 15, -13], skySun: [-0.77, 0.06, -0.63], sunC: 0xFFB27A, amt: 0.8, stars: 0.3, band: 0.9 }, base: { hemiI: 0.74, key: 0xFFB884, keyI: 0.95 },"
       " env: { top: 0x343A86, hor: 0xD49A86, gnd: 0x4A3448, sun: 0xFFB070, sunK: 0.8 }, lk: { hemi: 0.3, key: 1.25 }, grade: { sat: 1.1, con: 1.07, vig: 0.24, bloom: 0.6, expo: 1.08, tint: [1.02, 1.0, 0.99] } },")
s = s[:i] + new + s[j:]
rep("const CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xC2CAF0,", "const CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xE6C4D8,")

# ---- the sky: a low sun's color, its warmth along the horizon, fewer stars at dusk ----
rep("sunHi: { value: new THREE.Vector3(16, 30, 9).normalize() } };", "sunHi: { value: new THREE.Vector3(16, 30, 9).normalize() }, sunC: { value: new THREE.Color(1, 0.97, 0.88) }, starK: { value: 1 }, duskK: { value: 0 } };")
rep("fragmentShader: `uniform vec3 top, mid, hor, low, moonDir, sunDir, sunHi; uniform float rain, heat, day, uTime, dayBase, sunAmt; varying vec3 vD;",
    "fragmentShader: `uniform vec3 top, mid, hor, low, moonDir, sunDir, sunHi, sunC; uniform float rain, heat, day, uTime, dayBase, sunAmt, starK, duskK; varying vec3 vD;")
rep("c += vec3(1.0, 0.94, 0.86) * st * (0.6 + 0.8 * step(0.996, h)) * (1.0 - smoothstep(0.0, 0.6, day)) * (1.0 - rain) * (1.0 - dayBase);",
    "c += vec3(1.0, 0.94, 0.86) * st * (0.6 + 0.8 * step(0.996, h)) * (1.0 - smoothstep(0.0, 0.6, day)) * (1.0 - rain) * (1.0 - dayBase) * starK;")
rep("float sh = dot(d, sunHi); c += vec3(1.0, 0.97, 0.88) * (smoothstep(0.9992, 0.9995, sh) * 1.6 + pow(max(sh, 0.0), 60.0) * 0.32 + pow(max(sh, 0.0), 6.0) * 0.1) * sunAmt * (1.0 - rain);",
    "float sh = dot(d, sunHi); c += sunC * (smoothstep(0.9992, 0.9995, sh) * 1.6 + pow(max(sh, 0.0), 60.0) * 0.32 + pow(max(sh, 0.0), 6.0) * 0.1) * sunAmt * (1.0 - rain);\n"
    "    // dusk: the low sun's warmth spreads along the horizon on its side of the sky and rises a little way up into it\n"
    "    vec2 dh = normalize(d.xz + 1e-5), sh2 = normalize(sunHi.xz + 1e-5); float side = max(dot(dh, sh2), 0.0);\n"
    "    c += sunC * duskK * (exp(-abs(y - 0.02) * 9.0) * (0.12 + 0.55 * side * side) + pow(max(sh, 0.0), 4.0) * 0.45 + exp(-abs(y) * 3.0) * 0.06) * (1.0 - rain) * (1.0 - day);")

# ---- per-theme sun: direction, and the sky's sun and dusk glow ----
rep("  JGLOW.value = T.jglow != null ? T.jglow : 1; if (HI) Object.assign(LK, T.lk || LK0); themeEnv(T); if (post) post.grade(T);",
    "  const DK = T.dusk; sun.position.fromArray(DK ? DK.sun : [16, 30, 9]); paintUniforms.uLight.value.copy(sun.position).normalize(); envU.sunDir.value.copy(sun.position).normalize();\n"
    "  skyU.sunC.value.set(DK ? DK.sunC : 0xFFF7E0); skyU.starK.value = DK ? DK.stars : 1; skyU.duskK.value = DK ? DK.band : 0;\n"
    "  JGLOW.value = T.jglow != null ? T.jglow : 1; if (HI) Object.assign(LK, T.lk || LK0); themeEnv(T); if (post) post.grade(T);")
rep("  skyU.dayBase.value = T.day ? 1 : 0; skyU.sunAmt.value = T.sun || 0; skyU.low.value.set(T.low || 0x150D33);",
    "  skyU.dayBase.value = T.day ? 1 : 0; skyU.sunAmt.value = DK ? DK.amt : T.sun || 0; skyU.low.value.set(T.low || 0x150D33);\n"
    "  if (DK) skyU.sunHi.value.fromArray(DK.skySun).normalize(); else skyU.sunHi.value.set(16, 30, 9).normalize();\n"
    "  // drops glow in the theme's color (white by default); Graphics mode pushes them past white so they bloom\n"
    "  edgeMat.color.set(T.edge || 0xFFFFFF); if (HI && T.edgeK) edgeMat.color.multiplyScalar(T.edgeK); edgeLineMat.color.set(HI && T.edge ? 0x3A2614 : C.outline);")

# ---- all the stage's glows (flames, lamps, candles) in one instanced draw, each flickering on its own in the shader ----
rep("const flames = [];",
"""const flames = [], GLOWS = [];
const glowBatch = (() => {
  const base = new THREE.PlaneGeometry(1, 1), g = new THREE.InstancedBufferGeometry(); g.index = base.index; g.setAttribute('position', base.attributes.position); g.setAttribute('uv', base.attributes.uv); g.instanceCount = 0;
  const mat = new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 }, uK: { value: HI ? 1.7 : 1 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute vec4 aPos, aCol; uniform float uTime; varying vec2 vUv; varying vec3 vCol;
      void main(){ vUv = uv; vCol = aCol.rgb; float ph = aCol.a, s = aPos.w * (0.86 + 0.12 * sin(uTime * 11.0 + ph) + 0.06 * sin(uTime * 23.0 + ph * 1.83));
        vec4 mv = modelViewMatrix * vec4(aPos.xyz, 1.0); mv.xy += position.xy * s; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform float uK; varying vec2 vUv; varying vec3 vCol;
      void main(){ float r = length(vUv - 0.5) * 2.0, a = r < 0.22 ? mix(1.0, 0.6, r / 0.22) : 0.6 * max(0.0, 1.0 - (r - 0.22) / 0.78); a *= a * 0.35 + 0.65;
        gl_FragColor = vec4(vCol * uK, a);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }` });
  const m = new THREE.Mesh(g, mat); m.frustumCulled = false; m.renderOrder = 9; scene.add(m);
  const col = new THREE.Color();
  return { mat, set(list) { const P = new Float32Array(Math.max(1, list.length) * 4), Cc = new Float32Array(Math.max(1, list.length) * 4);
    list.forEach((q, i) => { col.set(q[4]); P.set([q[0], q[1], q[2], q[3]], i * 4); Cc.set([col.r, col.g, col.b, i * 1.7], i * 4); });
    g.setAttribute('aPos', new THREE.InstancedBufferAttribute(P, 4)); g.setAttribute('aCol', new THREE.InstancedBufferAttribute(Cc, 4)); g.instanceCount = list.length; } };
})();""")
rep("  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0;", "  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0; GLOWS.length = 0;")
rep("  const flame = (x, y, z, sz, col, reach) => { const sp = glowSprite(sz); sp.material.color.set(col || 0xFFB04A); sp.position.set(x, y, z); stageGroup.add(sp); flames.push({ s: sp, base: sz }); LIGHTS.push(",
    "  const flame = (x, y, z, sz, col, reach) => { GLOWS.push([x, y, z, sz, col || 0xFFB04A]); if (HI) put(M.flameCore, at(flameCoreG(sz), x, y - sz * 0.08, z)); LIGHTS.push(")
rep("        const sp = glowSprite(0.5); sp.material.color.set(LMP.col || 0xFFC46A); sp.position.set(lx, 0.12, lz); stageGroup.add(sp); flames.push({ s: sp, base: 0.5 });",
    "        GLOWS.push([lx, 0.12, lz, 0.5, LMP.col || 0xFFC46A]);")
rep("  for (let i = 0; i < flames.length; i++) { const f = flames[i]; f.s.scale.setScalar(", "  glowBatch.mat.uniforms.uTime.value = clock; for (let i = 0; i < flames.length; i++) { const f = flames[i]; f.s.scale.setScalar(")
# a flame's bright core, a little teardrop (Graphics mode)
rep("const shadowOnlyMat = new THREE.MeshBasicMaterial({ colorWrite: false });",
    "const flameCoreG = sz => { const k = Math.min(1, 0.35 + sz * 0.3), pts = []; for (let i = 0; i <= 8; i++) { const t = i / 8, r = Math.sin(Math.PI * Math.pow(t, 0.7)) * (1 - t * 0.55) * 0.045 * k; pts.push(new THREE.Vector2(Math.max(0.0005, r), (t - 0.3) * 0.2 * k)); } return new THREE.LatheGeometry(pts, 8); };\n"
    "const shadowOnlyMat = new THREE.MeshBasicMaterial({ colorWrite: false });")

# ---- materials the dressing needs ----
rep("    T.mats.trim = toon(tr.c, null, { metalness: tr.m, roughness: tr.r }); T.mats.iron = toon(0x22252E, null, { metalness: 0.6, roughness: 0.4 });",
    "    T.mats.trim = toon(tr.c, null, { metalness: tr.m, roughness: tr.r }); T.mats.iron = toon(0x22252E, null, { metalness: 0.6, roughness: 0.4 });\n"
    "    if (T.foot) T.mats.foot = toon(T.foot.c, null, { metalness: T.foot.m, roughness: T.foot.r });\n"
    "    T.mats.strip = new THREE.MeshBasicMaterial({ color: new THREE.Color(T.edge || 0xFFC872).multiplyScalar(2.4) }); T.mats.flameCore = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xFFE2A8).multiplyScalar(3.2) });")

# ---- trims: thicker, wrapping the top edge (proud of the face and a little above the top), per-theme size ----
rep("      const tw = 0.15, th = 0.09, ov = 0.02, ty = b[5] + th / 2 - 0.025, near = (a, c) => Math.abs(a - c) < 0.2, ovl = (a0, a1, c0, c1) => a0 < c1 - 0.05 && a1 > c0 + 0.05;",
    "      const tw = T.trim.w || 0.15, th = T.trim.h || 0.09, ov = T.trim.w ? tw * 0.28 : 0.02, ty = b[5] + th / 2 - (T.trim.w ? th - 0.035 : 0.025), near = (a, c) => Math.abs(a - c) < 0.2, ovl = (a0, a1, c0, c1) => a0 < c1 - 0.05 && a1 > c0 + 0.05;")
rep("      if (circ) { if (!RAMPS.some(rp => rectHit(rp, b, 0.3))) { const tr = new THREE.TorusGeometry(rad - tw * 0.4, th * 0.6, SEG(8), SEG(48)); tr.rotateX(Math.PI / 2); put(M.trim, at(tr, cx, b[5] + 0.02, cz)); } }",
    "      if (circ) { if (!RAMPS.some(rp => rectHit(rp, b, 0.3))) { const tr = new THREE.TorusGeometry(rad - tw * (T.trim.w ? 0.12 : 0.4), th * (T.trim.w ? 0.5 : 0.6), SEG(8), SEG(48)); tr.rotateX(Math.PI / 2); put(M.trim, at(tr, cx, b[5] + (T.trim.w ? -0.01 : 0.02), cz)); } }")

# ---- block dressing: skirting with a light strip, candles ----
rep("    // lamps: a lantern or a torch on the face of some walls, a warm uplight at the foot of others, and in the garden a lamp post on some corners\n    const LMP = T.lamps;",
"""    // the foot of each open face: a dark skirting, and on some of them a warm light strip along its top that lights the floor
    if (HI && !grave && !circ && (T.foot || T.strips)) {
      const open = (px, pz) => floorAt(px, pz) === 0 && !BOXES.some(o => o !== b && o[4] <= 0.05 && inR(px, pz, o, 0.02)) && !RAMPS.some(rp => inR(px, pz, rp, 0.02));
      for (const [fx, fz, nx, nz, L] of [[cx, b[2], 0, -1, w], [cx, b[3], 0, 1, w], [b[0], cz, -1, 0, d], [b[1], cz, 1, 0, d]]) {
        if (L < 0.6 || !open(fx + nx * 0.3, fz + nz * 0.3) || Math.abs(fx + nx * 0.3) > ARENA - 0.2 || Math.abs(fz + nz * 0.3) > ARENA - 0.2) continue;
        const fh = Math.min(0.15, h * 0.3), lx = nx ? 0.08 : L + 0.08, lz = nx ? L + 0.08 : 0.08;
        if (T.foot) put(M.foot, at(rbox(lx, fh, lz, 0.025), fx + nx * 0.02, fh / 2, fz + nz * 0.02));
        if (T.strips && R() < T.strips) {
          const sl = L - 0.16, sx = nx ? 0.03 : sl, sz = nx ? sl : 0.03; put(M.strip, at(new THREE.BoxGeometry(sx, 0.022, sz), fx + nx * 0.05, fh + 0.008, fz + nz * 0.05));
          const n = Math.max(1, Math.round(sl / 0.8)); for (let k = 0; k < n; k++) { const u = (k + 0.5) / n - 0.5; LIGHTS.push({ x: fx + nx * 0.3 + (nx ? 0 : u * sl), y: 0.14, z: fz + nz * 0.3 + (nx ? u * sl : 0), r: 1.35, c: new THREE.Color(T.edge || 0xFFC872), k: 0.42 }); }
        }
      }
    }
    // candles: a little cluster on a corner of some block tops
    if (T.candles && !grave && !circ && h > 0.6 && w > 1.1 && d > 1.1 && R() < T.candles) {
      const ix = R() < 0.5 ? 1 : -1, iz = R() < 0.5 ? 1 : -1, ox = cx + ix * (w / 2 - 0.42), oz = cz + iz * (d / 2 - 0.42), n = 2 + (R() * 2 | 0);
      for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + R(), rr = 0.1 + R() * 0.04, px = ox + Math.cos(a) * rr, pz = oz + Math.sin(a) * rr, hh = 0.14 + R() * 0.22, cr = 0.038 + R() * 0.018;
        put(M.cream, cyl(cr, cr * 1.06, hh, 10, px, b[5] + hh / 2, pz)); GLOWS.push([px, b[5] + hh + 0.06, pz, 0.34, 0xFFC27A]); if (HI) put(M.flameCore, at(flameCoreG(0.34), px, b[5] + hh + 0.035, pz)); }
      LIGHTS.push({ x: ox, y: b[5] + 0.45, z: oz, r: 2.6, c: new THREE.Color(0xFFB45A), k: 0.75 });
    }
    // lamps: a lantern or a torch on the face of some walls, a warm uplight at the foot of others, and in the garden a lamp post on some corners
    const LMP = T.lamps;""")

# ---- ramps: a light strip along the foot of each open side ----
rep("    const lowAtStart = r[5] < r[6];",
"""    if (HI && T.strips) for (const [fx0, fz0, fx1, fz1, nx, nz] of r[4] === 'z' ? [[x0, z0, x0, z1, -1, 0], [x1, z0, x1, z1, 1, 0]] : [[x0, z0, x1, z0, 0, -1], [x0, z1, x1, z1, 0, 1]]) {
      const mx = (fx0 + fx1) / 2, mz = (fz0 + fz1) / 2, L = Math.hypot(fx1 - fx0, fz1 - fz0) - 0.1; if (floorAt(mx + nx * 0.3, mz + nz * 0.3) !== 0 || BOXES.some(o => o[4] <= 0.05 && inR(mx + nx * 0.3, mz + nz * 0.3, o, 0.02))) continue;
      put(M.strip, at(new THREE.BoxGeometry(nx ? 0.03 : L, 0.022, nx ? L : 0.03), mx + nx * 0.016, 0.03, mz + nz * 0.016));
      const n = Math.max(1, Math.round(L / 0.8)); for (let k = 0; k < n; k++) { const u = (k + 0.5) / n - 0.5; LIGHTS.push({ x: mx + nx * 0.28 + (nx ? 0 : u * L), y: 0.12, z: mz + nz * 0.28 + (nx ? u * L : 0), r: 1.3, c: new THREE.Color(T.edge || 0xFFC872), k: 0.4 }); }
    }
    const lowAtStart = r[5] < r[6];""")

# ---- the drops: rims lit in the theme's color, a polished lip around the canvas ----
rep("  HOLES.forEach(holeEdge);",
"""  HOLES.forEach(holeEdge);
  if (HI && T.rimLights) {
    const rc = new THREE.Color(T.edge || 0xFFC872), lt = (x, z) => LIGHTS.push({ x, y: 0.07, z, r: 1.5, c: rc, k: T.rimLights });
    for (const hh of HOLES) { if (hh[6] === 'c') { const cx = (hh[0] + hh[1]) / 2, cz = (hh[2] + hh[3]) / 2, r = (hh[1] - hh[0]) / 2 + EDGE_W, n = Math.max(6, Math.round(6.2832 * r / 1.0)); for (let k = 0; k < n; k++) { const a = k / n * 6.2832; lt(cx + Math.cos(a) * r, cz + Math.sin(a) * r); } }
      else { const [x0, x1, z0, z1] = hh, e = EDGE_W; for (const [ax, az, bx, bz] of [[x0 - e, z0 - e, x1 + e, z0 - e], [x1 + e, z0 - e, x1 + e, z1 + e], [x1 + e, z1 + e, x0 - e, z1 + e], [x0 - e, z1 + e, x0 - e, z0 - e]]) { const L = Math.hypot(bx - ax, bz - az), n = Math.max(1, Math.round(L / 1.0)); for (let k = 0; k < n; k++) { const t = (k + 0.5) / n; lt(ax + (bx - ax) * t, az + (bz - az) * t); } } } }
    const A = ARENA - EDGE_W, n = Math.round(2 * A / 1.3); for (let k = 0; k < n; k++) { const u = -A + (k + 0.5) / n * 2 * A; lt(u, -A); lt(u, A); lt(-A, u); lt(A, u); }
  }
  if (HI && T.lip) { const A = ARENA, t = 0.13; for (const [w2, d2, x, z] of [[2 * A + 2 * t, t, 0, -A - t / 2], [2 * A + 2 * t, t, 0, A + t / 2], [t, 2 * A, -A - t / 2, 0], [t, 2 * A, A + t / 2, 0]]) put(M.trim, at(rbox(w2, 0.17, d2, 0.045), x, -0.065, z)); }""")

# ---- build the glow batch with the stage ----
rep("  setMotes(T);\n  for (const [mat, list] of bag)", "  setMotes(T); glowBatch.set(GLOWS);\n  for (const [mat, list] of bag)")
open(p, 'w').write(s)
print('ok')
