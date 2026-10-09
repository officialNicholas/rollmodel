# Stage look like the garden reference: baked warm light pools, lanterns and uplights, trims, richer foliage, leafy trees, pond water, tilt-shift blur
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:100], c)
    s = s.replace(a, b)

# ---------- A. baked local light ----------
rep("""const aoU = { uAOMap: { value: aoTex }, uAORect: { value: new THREE.Vector4(-30, -30, 1 / 60, 0) } };""",
"""// and a second map of warm light from the stage's own lamps, candles and torches, with walls casting their shade across it
const litTex = HI ? new THREE.DataTexture(new Uint8Array(AO_N * AO_N * 4), AO_N, AO_N, THREE.RGBAFormat) : null;
if (litTex) { litTex.magFilter = litTex.minFilter = THREE.LinearFilter; litTex.generateMipmaps = false; litTex.needsUpdate = true; }
const aoU = { uAOMap: { value: aoTex }, uLitMap: { value: litTex }, uAORect: { value: new THREE.Vector4(-30, -30, 1 / 60, 0) } };
const LIGHTS = []; // { x, y, z, r, c: Color, k }: each stage's light sources, gathered while it's built""")
rep("""const AO_GLSL = `uniform sampler2D uAOMap; uniform vec4 uAORect;
float stageAO(vec3 w, vec3 n){
  vec2 uv = (w.xz + n.xz * 0.3 - uAORect.xy) * uAORect.z;
  if (uv.x <= 0.0 || uv.y <= 0.0 || uv.x >= 1.0 || uv.y >= 1.0) return 1.0;
  vec4 t = texture2D(uAOMap, uv); float dy = w.y - (t.g * 12.0 - 3.0);
  return mix(t.r, 1.0, smoothstep(0.0, 1.3, dy)) * (1.0 - 0.42 * smoothstep(-0.2, -0.6, dy));
}`;""", """const AO_GLSL = `uniform sampler2D uAOMap, uLitMap; uniform vec4 uAORect;
float stageAO(vec3 w, vec3 n){
  vec2 uv = (w.xz + n.xz * 0.3 - uAORect.xy) * uAORect.z;
  if (uv.x <= 0.0 || uv.y <= 0.0 || uv.x >= 1.0 || uv.y >= 1.0) return 1.0;
  vec4 t = texture2D(uAOMap, uv); float dy = w.y - (t.g * 12.0 - 3.0);
  return mix(t.r, 1.0, smoothstep(0.0, 1.3, dy)) * (1.0 - 0.42 * smoothstep(-0.2, -0.6, dy));
}
// the lamps' light where this surface is: full on tops and floors, fading up a wall's face, dim under a slab
vec3 stageLit(vec3 w, vec3 n){
  vec2 uv = (w.xz + n.xz * 0.3 - uAORect.xy) * uAORect.z;
  if (uv.x <= 0.0 || uv.y <= 0.0 || uv.x >= 1.0 || uv.y >= 1.0) return vec3(0.0);
  float dy = w.y - (texture2D(uAOMap, uv).g * 12.0 - 3.0);
  return texture2D(uLitMap, uv).rgb * 2.0 * (1.0 - smoothstep(0.6, 3.4, dy)) * (dy < -0.4 ? 0.3 : 1.0);
}`;""")
rep("""function aoHook(sh) {
  sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uAORect = aoU.uAORect;""", """function aoHook(sh) {
  sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect;""")
rep("""reflectedLight.directDiffuse *= mix(1.0, sao, 0.55); reflectedLight.directSpecular *= sao; }');""",
    """reflectedLight.directDiffuse *= mix(1.0, sao, 0.55); reflectedLight.directSpecular *= sao; reflectedLight.directDiffuse += diffuseColor.rgb * stageLit(vAOw, normalize(vAOn)) * (0.6 + 0.4 * sao); }');""")
rep("""  aoTex.needsUpdate = true; aoU.uAORect.value.set(-A, -A, 1 / (2 * A), 0);
}""", """  aoTex.needsUpdate = true; aoU.uAORect.value.set(-A, -A, 1 / (2 * A), 0);
  // warm light: each source lights what it can see within its reach, softly falling off; walls and pieces in between shade it
  const L = new Float32Array(N * N * 3), ld = litTex.image.data, Hat = (x, z) => { const i = Math.floor((x + A) / cs), j = Math.floor((z + A) / cs); return i < 0 || j < 0 || i >= N || j >= N ? -3 : Hm[j * N + i]; };
  for (const s of LIGHTS) {
    const i0 = Math.max(0, Math.floor((s.x - s.r + A) / cs)), i1 = Math.min(N - 1, Math.ceil((s.x + s.r + A) / cs)), j0 = Math.max(0, Math.floor((s.z - s.r + A) / cs)), j1 = Math.min(N - 1, Math.ceil((s.z + s.r + A) / cs));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
      const h0 = Hm[j * N + i]; if (h0 <= -3) continue;
      const x = -A + (i + 0.5) * cs, z = -A + (j + 0.5) * cs, dx = s.x - x, dy = s.y - h0, dz = s.z - z, d = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (d >= s.r) continue;
      let f = (1 - d / s.r); f = f * f * s.k / (1 + d * 0.25);
      if (dy > 0) { let vis = 1; for (let k = 1; k <= 8; k++) { const t = k / 9, hx = x + dx * t, hz = z + dz * t, hy = h0 + 0.05 + dy * t; if (Hat(hx, hz) > hy + 0.04) { vis = 0.12; break; } } f *= vis; }
      else f *= 0.35; // a light below the surface only grazes it
      const o = (j * N + i) * 3; L[o] += s.c.r * f; L[o + 1] += s.c.g * f; L[o + 2] += s.c.b * f;
    }
  }
  for (let i = 0, n = N * N; i < n; i++) { ld[i * 4] = Math.min(255, L[i * 3] * 127.5); ld[i * 4 + 1] = Math.min(255, L[i * 3 + 1] * 127.5); ld[i * 4 + 2] = Math.min(255, L[i * 3 + 2] * 127.5); ld[i * 4 + 3] = 255; }
  litTex.needsUpdate = true;
}""")
# every flame on the stage is also a light; the stage's light list is rebuilt with it
rep("""  const flame = (x, y, z, sz, col) => { const sp = glowSprite(sz); sp.material.color.set(col || 0xFFB04A); sp.position.set(x, y, z); stageGroup.add(sp); flames.push({ s: sp, base: sz }); };""",
    """  const flame = (x, y, z, sz, col, reach) => { const sp = glowSprite(sz); sp.material.color.set(col || 0xFFB04A); sp.position.set(x, y, z); stageGroup.add(sp); flames.push({ s: sp, base: sz }); LIGHTS.push({ x, y, z, r: reach || 2.4 + sz * 2.4, c: new THREE.Color(col || 0xFFB04A), k: 0.55 + 0.35 * sz }); };""")
rep("""  floaters.length = 0; flames.length = 0; treeTops.length = 0;""", """  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0;""")

# ---------- B. paint takes the lamps' light ----------
rep("""  vec3 litK = mix(uShK, vec3(1.0), shade * clamp(dot(nb, L) / max(L.y, 0.3), 0.0, 1.3)) * mix(1.0, ao, 0.75);
  gl_FragColor = vec4(col * litK + gloss * glossK * mix(1.0, ao, 0.6), dilA);""",
    """  vec3 litK = mix(uShK, vec3(1.0), shade * clamp(dot(nb, L) / max(L.y, 0.3), 0.0, 1.3)) * mix(1.0, ao, 0.75) + stageLit(vW, vec3(0.0, 1.0, 0.0)) * 0.8;
  gl_FragColor = vec4(col * litK + gloss * glossK * mix(1.0, ao, 0.6), dilA);""")

# ---------- C. so does the jelly ----------
rep("""    let vs = GOO_GLSL + '\\nvarying float vGooY;\\n' + sh.vertexShader;""", """    let vs = GOO_GLSL + '\\nvarying float vGooY; varying vec3 vGooW;\\n' + sh.vertexShader;""")
rep("""    sh.vertexShader = vs;
    if (jelly) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying float vGooY; uniform float gGlow;').replace('#include <aomap_fragment>', '#include <aomap_fragment>' + JELLY_FS);""",
"""    if (jelly) { vs = vs.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\\nvGooW = (modelMatrix * vec4(transformed, 1.0)).xyz;'); sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect; }
    sh.vertexShader = vs;
    if (jelly) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying float vGooY; varying vec3 vGooW; uniform float gGlow;\\n' + AO_GLSL).replace('#include <aomap_fragment>', '#include <aomap_fragment>' + JELLY_FS + '\\ntotalEmissiveRadiance += diffuseColor.rgb * stageLit(vGooW, vec3(0.0, 1.0, 0.0)) * 0.45;');""")

# ---------- D/E/F. lanterns, uplights, trims, leafy trees ----------
rep("""    putAll(g, mats); hulls.push(o);
    // the theme dresses the round pieces
    if (circ) {""", """    putAll(g, mats); hulls.push(o);
    // Graphics mode: a trim along the top edge, the way a planter or a plinth is finished (left open where a ramp comes up)
    if (HI && T.trim && !grave) {
      const tw = 0.15, th = 0.09, ov = 0.02, ty = b[5] + th / 2 - 0.025, near = (a, c) => Math.abs(a - c) < 0.2, ovl = (a0, a1, c0, c1) => a0 < c1 - 0.05 && a1 > c0 + 0.05;
      if (circ) { if (!RAMPS.some(rp => rectHit(rp, b, 0.3))) { const tr = new THREE.TorusGeometry(rad - tw * 0.4, th * 0.6, SEG(8), SEG(48)); tr.rotateX(Math.PI / 2); put(M.trim, at(tr, cx, b[5] + 0.02, cz)); } }
      else {
        const sideFree = (k) => !RAMPS.some(rp => k === 0 ? near(rp[3], b[2]) && ovl(rp[0], rp[1], b[0], b[1]) : k === 1 ? near(rp[2], b[3]) && ovl(rp[0], rp[1], b[0], b[1]) : k === 2 ? near(rp[1], b[0]) && ovl(rp[2], rp[3], b[2], b[3]) : near(rp[0], b[1]) && ovl(rp[2], rp[3], b[2], b[3]));
        if (sideFree(0)) put(M.trim, at(rbox(w + 2 * ov, th, tw, 0.03), cx, ty, b[2] + tw / 2 - ov));
        if (sideFree(1)) put(M.trim, at(rbox(w + 2 * ov, th, tw, 0.03), cx, ty, b[3] - tw / 2 + ov));
        if (sideFree(2)) put(M.trim, at(rbox(tw, th, Math.max(0.1, d - 2 * tw + 2 * ov), 0.03), b[0] + tw / 2 - ov, ty, cz));
        if (sideFree(3)) put(M.trim, at(rbox(tw, th, Math.max(0.1, d - 2 * tw + 2 * ov), 0.03), b[1] - tw / 2 + ov, ty, cz));
      }
    }
    // the garden lights its hedges: a lantern on the face of some, a warm uplight at the foot of others
    if (T.id === 'garden' && !circ && !grave && h > 0.7) {
      const faces = [[cx, b[2] - 0.13, 0, -1, w], [cx, b[3] + 0.13, 0, 1, w], [b[0] - 0.13, cz, -1, 0, d], [b[1] + 0.13, cz, 1, 0, d]].filter(f => Math.abs(f[0]) < ARENA - 0.6 && Math.abs(f[1]) < ARENA - 0.6 && floorAt(f[0] + f[2] * 0.3, f[1] + f[3] * 0.3) === 0);
      if (faces.length && R() < 0.7) {
        const f = faces[(R() * faces.length) | 0], off = (R() - 0.5) * Math.max(0, f[4] - 1.2), lx = f[0] + (f[2] ? 0 : off), lz = f[1] + (f[3] ? 0 : off), ly = Math.min(h - 0.18, 1.05);
        put(M.iron, at(new THREE.BoxGeometry(0.24, 0.05, 0.24), lx, ly + 0.19, lz)); put(M.iron, at(new THREE.BoxGeometry(0.2, 0.04, 0.2), lx, ly - 0.17, lz)); put(M.glowY, at(new THREE.BoxGeometry(0.16, 0.3, 0.16), lx, ly, lz));
        put(M.iron, at(new THREE.BoxGeometry(f[2] ? 0.16 : 0.04, 0.04, f[3] ? 0.16 : 0.04), lx - f[2] * 0.09, ly + 0.12, lz - f[3] * 0.09));
        flame(lx, ly, lz, 0.55, 0xFFC46A, 3.6);
      } else if (faces.length && R() < 0.6) {
        const f = faces[(R() * faces.length) | 0], off = (R() - 0.5) * Math.max(0, f[4] - 1.0), lx = f[0] + (f[2] ? f[2] * 0.06 : off), lz = f[1] + (f[3] ? f[3] * 0.06 : off);
        put(M.glowY, at(new THREE.CylinderGeometry(0.09, 0.11, 0.05, 12), lx, 0.025, lz)); LIGHTS.push({ x: lx + f[2] * 0.25, y: 0.35, z: lz + f[3] * 0.25, r: 2.2, c: new THREE.Color(0xFFB45A), k: 0.75 });
        const sp = glowSprite(0.5); sp.material.color.set(0xFFC46A); sp.position.set(lx, 0.12, lz); stageGroup.add(sp); flames.push({ s: sp, base: 0.5 });
      }
    }
    // the theme dresses the round pieces
    if (circ) {""")
# leafy canopies and bushes in Graphics mode, and a warm uplight under each garden tree
rep("""      else if (T.id === 'garden' && kind === 'column') { put(M.bark, cyl(rad * 0.98, rad * 1.05, h, 18, cx, h / 2, cz)); for (let k = 0; k < 3; k++) { const a = R() * 6.28, rr = rad * 0.9; const br = rad * (2.1 + R() * 0.6), bx = cx + Math.cos(a) * rr, by = top + 0.5 + k * 0.55, bz = cz + Math.sin(a) * rr; put(k % 2 ? M.leaf : M.leaf2, ball(br, bx, by, bz, 0.8)); treeTops.push({ x: bx, y: by, z: bz, r: br }); } }""",
    """      else if (T.id === 'garden' && kind === 'column') { put(M.bark, cyl(rad * 0.98, rad * 1.05, h, 18, cx, h / 2, cz)); for (let k = 0; k < 3; k++) { const a = R() * 6.28, rr = rad * 0.9; const br = rad * (2.1 + R() * 0.6), bx = cx + Math.cos(a) * rr, by = top + 0.5 + k * 0.55, bz = cz + Math.sin(a) * rr; put(HI ? M.canopy : k % 2 ? M.leaf : M.leaf2, HI ? lumpBall(br, bx, by, bz, 0.8, R) : ball(br, bx, by, bz, 0.8)); treeTops.push({ x: bx, y: by, z: bz, r: br }); }
        if (HI) { const a = R() * 6.28, ux = cx + Math.cos(a) * (rad + 0.35), uz = cz + Math.sin(a) * (rad + 0.35); if (floorAt(ux, uz) === 0) { put(M.glowY, at(new THREE.CylinderGeometry(0.1, 0.12, 0.06, 12), ux, 0.03, uz)); LIGHTS.push({ x: ux, y: 0.45, z: uz, r: 3.0, c: new THREE.Color(0xFFB45A), k: 1.0 }); } } }""")
rep("""      else if (T.id === 'garden' && kind === 'drum') { for (let k = 0; k < 6; k++) { const a = k / 6 * 6.28 + R(); put(k % 2 ? M.leaf : M.leaf2, ball(0.32 + R() * 0.16, cx + Math.cos(a) * rad * 0.98, h * (0.3 + R() * 0.5), cz + Math.sin(a) * rad * 0.98)); } }""",
    """      else if (T.id === 'garden' && kind === 'drum') { for (let k = 0; k < 6; k++) { const a = k / 6 * 6.28 + R(), br = 0.32 + R() * 0.16, bx = cx + Math.cos(a) * rad * 0.98, by = h * (0.3 + R() * 0.5), bz = cz + Math.sin(a) * rad * 0.98; put(HI ? M.canopy : k % 2 ? M.leaf : M.leaf2, HI ? lumpBall(br, bx, by, bz, 1, R) : ball(br, bx, by, bz)); } }""")
rep("""  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, SEG(16), SEG(12)); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };""",
    """  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, SEG(16), SEG(12)); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };
  // a leafy clump: a ball pushed in and out in soft lumps, so a canopy reads as bunches of leaves
  const lumpBall = (r, x, y, z, sy, Rg) => { const g = new THREE.SphereGeometry(r, 36, 26), P = g.attributes.position, o1 = Rg() * 6, o2 = Rg() * 6; for (let i = 0; i < P.count; i++) { const px = P.getX(i) / r, py = P.getY(i) / r, pz = P.getZ(i) / r, k = 1 + 0.11 * Math.sin(px * 3.3 + o1) * Math.sin(py * 3.1 + o2) * Math.sin(pz * 3.5 + 1.3) + 0.07 * Math.sin(px * 6.7 + py * 5.3 + o2) * Math.sin(pz * 6.1 - px * 2.0 + o1); P.setXYZ(i, P.getX(i) * k, P.getY(i) * k * (sy || 1), P.getZ(i) * k); } g.computeVertexNormals(); return at(g, x, y, z); };""")

# ---------- F. richer garden textures, leaves for canopies, bark ----------
import re
m = re.search(r"const mossTex = makeTex\(256, .*?\n.*?\n.*?\nconst hedgeTex = makeTex\(256, .*?\n.*?\n", s, re.S); assert m
s = s.replace(m.group(0), """// night garden: leafy groundcover and clipped hedge, drawn leaf by leaf (their normal maps give every leaf an edge)
const leafAt = (g, X, Y, L, W, a, col, rib) => { g.save(); g.translate(X, Y); g.rotate(a); g.fillStyle = col; g.beginPath(); g.moveTo(-L, 0); g.quadraticCurveTo(0, -W, L, 0); g.quadraticCurveTo(0, W, -L, 0); g.fill(); if (rib) { g.strokeStyle = rib; g.lineWidth = 0.9; g.beginPath(); g.moveTo(-L * 0.8, 0); g.lineTo(L * 0.8, 0); g.stroke(); } g.restore(); };
const mossTex = makeTex(512, (g, S) => { const r = rng(37); g.fillStyle = '#284427'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 70; i++) { const pts = lumpy(r, 30 + r() * 60, 24 + r() * 50, 10), x = r() * S, y = r() * S, col = r() < 0.5 ? 'rgba(70,108,60,0.4)' : 'rgba(22,44,26,0.45)'; wrapAt(S, x, y, 90, (X, Y) => { polyAt(g, pts, X, Y, r() * 3); g.fillStyle = col; g.fill(); }); }
  for (let i = 0; i < 2600; i++) { const x = r() * S, y = r() * S, L = 5 + r() * 7, W = L * (0.38 + r() * 0.2), a = r() * 6.283, l = r(), col = `rgb(${40 + l * 56 | 0},${82 + l * 76 | 0},${38 + l * 36 | 0})`; wrapAt(S, x, y, 14, (X, Y) => leafAt(g, X, Y, L, W, a, col, 'rgba(16,34,16,0.4)')); }
  for (let i = 0; i < 90; i++) { const x = r() * S, y = r() * S, a = r() * 6.283; wrapAt(S, x, y, 12, (X, Y) => { for (let k = 0; k < 3; k++) { const b = a + k * 2.094; g.fillStyle = 'rgba(96,160,78,0.9)'; g.beginPath(); g.arc(X + Math.cos(b) * 3.2, Y + Math.sin(b) * 3.2, 3.4, 0, 6.2832); g.fill(); } }); }
  for (let i = 0; i < 70; i++) { const x = r() * S, y = r() * S; wrapAt(S, x, y, 4, (X, Y) => { g.fillStyle = r() < 0.5 ? 'rgba(250,246,230,0.9)' : 'rgba(255,222,120,0.85)'; g.beginPath(); g.arc(X, Y, 1.5, 0, 6.2832); g.fill(); }); } });
const hedgeTex = makeTex(512, (g, S) => { const r = rng(38); g.fillStyle = '#12301A'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 4400; i++) { const x = r() * S, y = r() * S, L = 4 + r() * 6, W = L * (0.45 + r() * 0.2), a = r() * 6.283, l = r(), col = `rgb(${22 + l * 48 | 0},${62 + l * 82 | 0},${26 + l * 32 | 0})`; wrapAt(S, x, y, 12, (X, Y) => leafAt(g, X, Y, L, W, a, col, l > 0.6 ? 'rgba(10,30,14,0.35)' : null)); } });
// leaves for canopies and bushes, and a bark for trunks (Graphics mode)
const leafTex = makeTex(512, (g, S) => { const r = rng(39); g.fillStyle = '#1E4A22'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 3400; i++) { const x = r() * S, y = r() * S, L = 6 + r() * 8, W = L * (0.42 + r() * 0.2), a = r() * 6.283, l = r(), col = `rgb(${36 + l * 60 | 0},${86 + l * 90 | 0},${36 + l * 40 | 0})`; wrapAt(S, x, y, 16, (X, Y) => leafAt(g, X, Y, L, W, a, col, 'rgba(14,36,16,0.35)')); } });
const barkTex = makeTex(256, (g, S) => { const r = rng(40); g.fillStyle = '#4E3322'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 70; i++) { const x0 = r() * S, a = 2 + r() * 5, ph = r() * 6.28, w = 1.5 + r() * 4, l = r(); g.strokeStyle = l < 0.5 ? `rgba(30,18,10,${0.35 + r() * 0.3})` : `rgba(120,88,60,${0.2 + r() * 0.2})`; g.lineWidth = w; for (const off of [-S, 0, S]) { g.beginPath(); for (let y = 0; y <= S; y += 6) { const x = x0 + off + Math.sin(y / S * 6.2832 * 2 + ph) * a; y ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); } } });
""")
# theme materials: trims, iron, canopy, bark
rep("""  if (HI) for (const k in T.mats) [].concat(T.mats[k]).forEach(aoPatch);
  return T.mats;""", """  if (HI) {
    const tr = T.trim || { c: 0x2C2F3B, m: 0.5, r: 0.4 };
    T.mats.trim = toon(tr.c, null, { metalness: tr.m, roughness: tr.r }); T.mats.iron = toon(0x22252E, null, { metalness: 0.6, roughness: 0.4 });
    if (T.id === 'garden') { T.mats.canopy = toon(0xBDBDBD, { map: leafTex }, { normalMap: normalFrom(leafTex, 1.3), normalScale: new THREE.Vector2(1.1, 1.1), roughness: 0.62 }); T.mats.bark = toon(0xC8C8C8, { map: barkTex }, { normalMap: normalFrom(barkTex, 1.3), normalScale: new THREE.Vector2(1.2, 1.2), roughness: 0.9 }); }
    for (const k in T.mats) [].concat(T.mats[k]).forEach(aoPatch);
  } else T.mats.iron = T.mats.dark;
  return T.mats;""")
# per-theme trim colors (Graphics mode): dark iron for the garden, wood for the studio, stone for the crypt, gold for the cathedral and manor
rep("""kit: { drum: [1, 3], column: [0, 1], rpad: [0, 1], rotunda: [0, 1], rpit: [0, 1] }, fill: 'drum', pot: 'can' },""", """kit: { drum: [1, 3], column: [0, 1], rpad: [0, 1], rotunda: [0, 1], rpit: [0, 1] }, fill: 'drum', pot: 'can', trim: { c: 0x4A2E1C, m: 0.05, r: 0.55 } },""")
rep("""kit: { tombs: [2, 4], column: [1, 2], rpit: [0, 1], drum: [0, 1] }, fill: 'tombs' },""", """kit: { tombs: [2, 4], column: [1, 2], rpit: [0, 1], drum: [0, 1] }, fill: 'tombs', trim: { c: 0x7E8392, m: 0, r: 0.8 } },""")
rep("""kit: { column: [2, 4], rotunda: [0, 1], rpad: [1, 1], drum: [0, 1] }, fill: 'column' },""", """kit: { column: [2, 4], rotunda: [0, 1], rpad: [1, 1], drum: [0, 1] }, fill: 'column', trim: { c: 0xD9A94A, m: 0.85, r: 0.32 } },""")
rep("""kit: { rpad: [1, 2], drum: [1, 2], rotunda: [0, 1], column: [0, 1] }, fill: 'rpad' },""", """kit: { rpad: [1, 2], drum: [1, 2], rotunda: [0, 1], column: [0, 1] }, fill: 'rpad', trim: { c: 0xC99A44, m: 0.8, r: 0.35 } },""")
rep("""kit: { drum: [2, 3], column: [1, 2], rpit: [0, 1], rpad: [0, 1] }, fill: 'drum' },""", """kit: { drum: [2, 3], column: [1, 2], rpit: [0, 1], rpad: [0, 1] }, fill: 'drum', trim: { c: 0x262A36, m: 0.55, r: 0.38 }, pond: true, nrm: [1.0, 1.1], rough: [0.8, 0.75] },""")

# ---------- G. water in the garden's holes ----------
rep("""const stageGroup = new THREE.Group(); scene.add(stageGroup);""", """const stageGroup = new THREE.Group(); scene.add(stageGroup);
// a dark, glassy pond under the floor, seen only through its holes (the night garden)
const pond = new THREE.Mesh(new THREE.PlaneGeometry(2, 2).rotateX(-Math.PI / 2), HI ? new THREE.MeshStandardMaterial({ color: 0x0A2226, roughness: 0.06, metalness: 0.25, envMapIntensity: 1.7 }) : new THREE.MeshBasicMaterial({ color: 0x103238 }));
pond.position.y = -0.42; pond.visible = false; scene.add(pond);""")
rep("""  bakeAO();
}""", """  pond.visible = !!T.pond && HOLES.length > 0; pond.scale.set(ARENA, 1, ARENA);
  bakeAO();
}""")

# ---------- H. tilt-shift blur in the post pass ----------
rep("""  const rt = () => new THREE.WebGLRenderTarget(4, 4, opt), A = rt(), B = rt(), C2 = rt(), D = rt(), E = rt();""",
    """  const rt = () => new THREE.WebGLRenderTarget(4, 4, opt), A = rt(), B = rt(), C2 = rt(), D = rt(), E = rt(), F = rt(), G = rt(), Hh = rt();""")
rep("""  const cu = { tScene: { value: null }, tB1: { value: null }, tB2: { value: null }, uBloom: { value: 0.55 },""",
    """  const down = sm({ tSrc: { value: null }, uPx: { value: new THREE.Vector2() } }, `uniform sampler2D tSrc; uniform vec2 uPx; varying vec2 vUv;
    void main(){ gl_FragColor = vec4((texture2D(tSrc, vUv + uPx * vec2(-0.5, -0.5)).rgb + texture2D(tSrc, vUv + uPx * vec2(0.5, -0.5)).rgb + texture2D(tSrc, vUv + uPx * vec2(-0.5, 0.5)).rgb + texture2D(tSrc, vUv + uPx * vec2(0.5, 0.5)).rgb) * 0.25, 1.0); }`);
  const cu = { tScene: { value: null }, tB1: { value: null }, tB2: { value: null }, tDof: { value: null }, uDof: { value: new THREE.Vector4(0.74, 1.0, 0.8, 0.07) }, uBloom: { value: 0.55 },""")
rep("""  const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime; uniform vec3 uLift, uTint; varying vec2 vUv;
    void main(){ vec2 uv = vUv;
      if (uHeat > 0.01) { float k = uHeat * (0.6 + 0.4 * vUv.y); uv.x += (sin(uv.y * 42.0 + uTime * 5.2) * 0.0026 + sin(uv.y * 97.0 - uTime * 7.7) * 0.0012) * k; uv.y += cos(uv.x * 33.0 + uTime * 4.3) * 0.0016 * k; }
      vec3 c = texture2D(tScene, uv).rgb;""", """  const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2, tDof; uniform vec4 uDof; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime; uniform vec3 uLift, uTint; varying vec2 vUv;
    void main(){ vec2 uv = vUv;
      if (uHeat > 0.01) { float k = uHeat * (0.6 + 0.4 * vUv.y); uv.x += (sin(uv.y * 42.0 + uTime * 5.2) * 0.0026 + sin(uv.y * 97.0 - uTime * 7.7) * 0.0012) * k; uv.y += cos(uv.x * 33.0 + uTime * 4.3) * 0.0016 * k; }
      vec3 c = texture2D(tScene, uv).rgb;
      // tilt-shift: the far edge of the view (and a touch of the near edge) goes soft, like a miniature
      float dk = (smoothstep(uDof.x, uDof.y, vUv.y) + 0.6 * smoothstep(uDof.w, 0.0, vUv.y)) * uDof.z;
      if (dk > 0.003) c = mix(c, texture2D(tDof, uv).rgb, clamp(dk, 0.0, 1.0));""")
rep("""  const P0 = { bloom: true, resize() { renderer.getDrawingBufferSize(sz); const w = Math.max(4, sz.x | 0), h = Math.max(4, sz.y | 0); main.setSize(w, h); A.setSize(w >> 1, h >> 1); B.setSize(w >> 2, h >> 2); C2.setSize(w >> 2, h >> 2); D.setSize(w >> 3, h >> 3); E.setSize(w >> 3, h >> 3); },""",
    """  const P0 = { bloom: true, dof: true, dofK: new THREE.Vector4(0.74, 1.0, 0.8, 0.07), resize() { renderer.getDrawingBufferSize(sz); const w = Math.max(4, sz.x | 0), h = Math.max(4, sz.y | 0); main.setSize(w, h); A.setSize(w >> 1, h >> 1); B.setSize(w >> 2, h >> 2); C2.setSize(w >> 2, h >> 2); D.setSize(w >> 3, h >> 3); E.setSize(w >> 3, h >> 3); F.setSize(w >> 1, h >> 1); G.setSize(w >> 2, h >> 2); Hh.setSize(w >> 2, h >> 2); },""")
rep("""      cu.tScene.value = main.texture; cu.tB1.value = C2.texture; cu.tB2.value = E.texture; cu.uHeat.value = heatK; cu.uTime.value = clock;""",
    """      if (P0.dof && P0.dofK.z > 0.01) {
        down.uniforms.uPx.value.set(1 / main.width, 1 / main.height); pass(down, main, F);
        blur.uniforms.uDir.value.set(1.6 / G.width, 0); pass(blur, F, G); blur.uniforms.uDir.value.set(0, 1.6 / Hh.height); pass(blur, G, Hh);
        cu.uDof.value.copy(P0.dofK);
      } else cu.uDof.value.z = 0;
      cu.tScene.value = main.texture; cu.tB1.value = C2.texture; cu.tB2.value = E.texture; cu.tDof.value = Hh.texture; cu.uHeat.value = heatK; cu.uTime.value = clock;""")
# the menu shot focuses on the blobs (soft above and below them); play softens just the far edge
rep("""function renderFrame() {
  if (vic) return renderVictory();
  if (post) return post.render();""", """const DOF_PLAY = new THREE.Vector4(0.8, 1.02, 0.75, 0.05), DOF_MENU = new THREE.Vector4(0.6, 0.92, 0.9, 0.14), DOF_LOOK = new THREE.Vector4(0.66, 0.98, 0.7, 0.12);
function renderFrame() {
  if (vic) return renderVictory();
  if (post) { post.dofK.copy(state !== 'menu' ? DOF_PLAY : lookOpen ? DOF_LOOK : DOF_MENU); return post.render(); }""")
# when frames run long, the blur goes right after the glow
rep("""  if (avg > 0.0205 && post && post.bloom) { post.bloom = false; perfGood = 0; }""", """  if (avg > 0.0205 && post && post.bloom) { post.bloom = false; perfGood = 0; }
  else if (avg > 0.0205 && post && post.dof) { post.dof = false; perfGood = 0; }""")
rep("""else if (curPR < maxPR) { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); } else post.bloom = true; perfGood = 0; } }""",
    """else if (curPR < maxPR) { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); } else if (!post.dof) post.dof = true; else post.bloom = true; perfGood = 0; } }""")
rep("""  else if (avg < 0.0135 && (shadowLite > 0 || curPR < maxPR || (post && !post.bloom))) {""", """  else if (avg < 0.0135 && (shadowLite > 0 || curPR < maxPR || (post && (!post.bloom || !post.dof)))) {""")
open(p,'w').write(s); print('gfx patch 9 ok')
