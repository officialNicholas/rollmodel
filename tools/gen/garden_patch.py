# The Night Garden: the lawn is a raised bed walled in clipped hedge, standing in a garden of its own six meters down (hedge rings, trees,
# lamp posts with warm pools of light), the plinths on stone pillars down to it. Cool moonlight over warm lamps, amber rims on every drop,
# lamp posts, lanterns and uplights, path lights along the hedges, ivy up the columns, mowing stripes on the lawn, fog closer in.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

i = s.index("  { id: 'garden', label: 'The Night Garden',"); j = s.index('\n', i)
old = s[i:j]; kit = old[old.index('kit: '):old.index(", fill: 'drum'")]
s = s[:i] + ("  { id: 'garden', label: 'The Night Garden', sf: ['moss', 'hedge'], uv: 0.25, ft: 0xE4E4E4, st: 0xD8D8D8, dt: 0x8A9A8A, hor: 0x0C2430, sky: [0x02060E, 0x0A1C30, 0x1A3E52], low: 0x0C2430, hemi: [0x86B4D8, 0x16281E], "
    + kit + ", fill: 'drum', foot: { c: 0x8E8B84, m: 0, r: 0.82 }, lamps: { post: 0.34, wall: 0.46, up: 0.44, col: 0xFFC46A }, strips: 0.3, edge: 0xFFC772, edgeK: 2.4, rimLights: 0.5,"
    " ivy: { edge: 0.25, col: 0.9, drum: 0.35, prop: 0.8, tint: 0xF0FFF0 }, terrace: true, stripes: 1, fog: [36, 150], pond: true, lk: { hemi: 0.36, key: 1.3 }, base: { hemiI: 0.62, key: 0xBFD4FF, keyI: 0.62 },"
    " env: { top: 0x1A3450, hor: 0x2E5462, gnd: 0x1A2A1C, sun: 0xBFD4FF, sunK: 0.5 }, grade: { sat: 1.12, con: 1.08, vig: 0.26, bloom: 0.62, expo: 1.14 } },") + s[j:]

# fog per theme, islands away when the stage has its own ground
rep("  TH = T; HOR.set(T.hor);", "  TH = T; HOR.set(T.hor); scene.fog.near = T.fog ? T.fog[0] : 70; scene.fog.far = T.fog ? T.fog[1] : 200;")
rep("  for (const it of islands) it.g.visible = !T.day;", "  for (const it of islands) it.g.visible = !T.day && !T.terrace; aoU.uStripe.value = T.stripes || 0;")
# mowing stripes on a lawn: broad bands of lighter and darker green across the stage
rep("uMirK: { value: 0 } };", "uMirK: { value: 0 }, uStripe: { value: 0 } };")
rep("sh.uniforms.uMacro = aoU.uMacro;\n  if (sh.defines && sh.defines.MIRROR)", "sh.uniforms.uMacro = aoU.uMacro; sh.uniforms.uStripe = aoU.uStripe;\n  if (sh.defines && sh.defines.MIRROR)")
rep("const AO_GLSL = `uniform sampler2D uAOMap, uLitMap; uniform vec4 uAORect; uniform float uMacro;", "const AO_GLSL = `uniform sampler2D uAOMap, uLitMap; uniform vec4 uAORect; uniform float uMacro, uStripe;")
rep("{ float mz = macroN(vAOw) - 0.5; diffuseColor.rgb *= 1.0 + uMacro * mz * 1.6; }", "{ float mz = macroN(vAOw) - 0.5; diffuseColor.rgb *= 1.0 + uMacro * mz * 1.6; if (uStripe > 0.0 && vAOn.y > 0.7) diffuseColor.rgb *= 1.0 + uStripe * 0.1 * smoothstep(-0.25, 0.25, sin(vAOw.x * 0.5236)); }")

# the garden down below, and the raised bed's hedge walls; the plinths on stone pillars
rep("  if (HI && T.lip) {", """  if (T.terrace) {
    const GY = -6.2, A = ARENA, GR = 175;
    const gnd = new THREE.PlaneGeometry(2 * GR, 2 * GR, 1, 1); gnd.rotateX(-Math.PI / 2); gnd.translate(0, GY, 0); worldUV(gnd, us); put(M.lawn, gnd);
    // the bed's walls: clipped hedge from the lawn's edge down to the garden
    for (const [w2, d2, x, z] of [[2 * A + 1.0, 0.5, 0, -A - 0.25], [2 * A + 1.0, 0.5, 0, A + 0.25], [0.5, 2 * A, -A - 0.25, 0], [0.5, 2 * A, A + 0.25, 0]]) { const g = new THREE.BoxGeometry(w2, -GY - 0.55, d2); g.translate(x, (GY - 0.55) / 2, z); worldUV(g, us); put(M.side, g); }
    // hedge rings with gaps, trees, lamp posts with pools of warm light on the grass
    const Rg = rng(((GEN.seed || 1) * 11 + 3) >>> 0), pools = [];
    for (const [ring, hh] of [[A + 7, 1.1], [A + 16, 1.4], [A + 27, 1.6]]) {
      const segs = [[-ring, -ring, ring, -ring], [ring, -ring, ring, ring], [ring, ring, -ring, ring], [-ring, ring, -ring, -ring]];
      for (const [ax, az, bx, bz] of segs) { const L = Math.hypot(bx - ax, bz - az), n = 3; for (let k = 0; k < n; k++) { const t0 = k / n + 0.05, t1 = (k + 1) / n - 0.05; if (Rg() < 0.12) continue;
        const x0 = ax + (bx - ax) * t0, z0 = az + (bz - az) * t0, x1 = ax + (bx - ax) * t1, z1 = az + (bz - az) * t1, cx = (x0 + x1) / 2, cz = (z0 + z1) / 2, len = Math.hypot(x1 - x0, z1 - z0);
        const g = HI ? rbox(Math.abs(x1 - x0) + 1.1, hh, Math.abs(z1 - z0) + 1.1, 0.25) : new THREE.BoxGeometry(Math.abs(x1 - x0) + 1.1, hh, Math.abs(z1 - z0) + 1.1); g.translate(cx, GY + hh / 2, cz); worldUV(g, us); put(M.side, g);
        // a lamp post at each gap, its pool of light on the grass
        const lx = x0 + (ax === bx ? 1.4 : 0) * Math.sign(-ax || 1), lz = z0 + (az === bz ? 1.4 : 0) * Math.sign(-az || 1);
        if (Rg() < 0.7) { const H = 2.1; put(M.iron, cyl(0.05, 0.07, H, 8, lx, GY + H / 2, lz)); put(M.iron, at(new THREE.ConeGeometry(0.24, 0.18, SEG(8)), lx, GY + H + 0.4, lz)); put(M.glowY, at(new THREE.BoxGeometry(0.17, 0.3, 0.17), lx, GY + H + 0.17, lz)); GLOWS.push([lx, GY + H + 0.17, lz, 1.1, 0xFFC46A]); pools.push([lx, lz, 3.2 + Rg() * 0.8]); } } }
    }
    for (let k = 0; k < 26; k++) { const a = Rg() * 6.2832, r = A + 9 + Rg() * 26, x = Math.cos(a) * r, z = Math.sin(a) * r; if (Math.abs(Math.abs(x) - (A + 16)) < 2 || Math.abs(Math.abs(z) - (A + 16)) < 2) continue;
      const th = 1.6 + Rg() * 1.4, cr = 1.3 + Rg() * 1.1; put(M.bark, cyl(0.16, 0.24, th, 8, x, GY + th / 2, z)); const cg = new THREE.SphereGeometry(cr, 18, 12), P = cg.attributes.position, o1 = Rg() * 6;
      for (let q = 0; q < P.count; q++) { const px = P.getX(q) / cr, py = P.getY(q) / cr, pz = P.getZ(q) / cr, kk = 1 + 0.12 * Math.sin(px * 3.3 + o1) * Math.sin(py * 3.1) * Math.sin(pz * 3.5 + 1.3); P.setXYZ(q, P.getX(q) * kk, P.getY(q) * kk * 0.85, P.getZ(q) * kk); } cg.computeVertexNormals();
      put(HI ? M.canopy : M.leaf, at(cg, x, GY + th + cr * 0.6, z)); }
    if (pools.length) { const pg = pools.map(([x, z, r]) => { const g = new THREE.PlaneGeometry(2 * r, 2 * r); g.rotateX(-Math.PI / 2); g.translate(x, GY + 0.02, z); return g; }); const m = new THREE.Mesh(mergeGeos(pg, true), poolMat); m.renderOrder = 3; stageGroup.add(m); }
  }
  if (HI && T.lip) {""")
rep("    put(M.dark, HI ? worldUV(at(rbox(2.6, 0.7, 2.6, 0.12), x, -0.6, z), us) : at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push(at(new THREE.BoxGeometry(2.74, 0.84, 2.74), x, -0.6, z));",
    "    put(M.dark, HI ? worldUV(at(rbox(2.6, 0.7, 2.6, 0.12), x, -0.6, z), us) : at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push(at(new THREE.BoxGeometry(2.74, 0.84, 2.74), x, -0.6, z));\n"
    "    if (T.terrace) { const pg = HI ? rbox(1.9, 5.3, 1.9, 0.1) : new THREE.BoxGeometry(1.9, 5.3, 1.9); pg.translate(x, -0.95 - 2.65, z); worldUV(pg, us); put(M.pillar, pg); }")
# materials: a darker lawn for the garden below, stone for the pillars; the pools of lamplight
rep("  if (HI && T.mirror) { T.mats.floor.defines", "  T.mats.lawn = toon(lighten(T.ft, 0.62), { map: fl }, fp); T.mats.pillar = toon(0x9A968E, null, { roughness: 0.85 });\n  if (HI && T.mirror) { T.mats.floor.defines")
rep("const decalOf = tex => aoPatch(", """const poolMat = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 128; const g = cv.getContext('2d'), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,200,120,0.55)'); gr.addColorStop(0.4, 'rgba(255,170,90,0.22)'); gr.addColorStop(1, 'rgba(255,150,70,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: new THREE.Color(HI ? 1.6 : 1, HI ? 1.6 : 1, HI ? 1.6 : 1) }); })();
const decalOf = tex => aoPatch(""")
open(p, 'w').write(s)
print('ok')
