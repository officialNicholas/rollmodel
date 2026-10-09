# Graphics mode geometry and surface detail: rounded boxes, lipped drums, more segments, baked AO, normal maps
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:90], c)
    s = s.replace(a, b)

rep("const SEG = n => Math.max(6, Math.round(n * (HI ? 1.5 : 0.75))); // how round round things are",
    "const SEG = n => HI ? Math.round(n * 1.6) : n; // how round round things are")

# worldUV: rounded boxes carry their face axis, so the bevel keeps its face's projection
rep("""function worldUV(g, s) {
  const p = g.attributes.position, n = g.attributes.normal, uv = new Float32Array(p.count * 2);
  for (let i = 0; i < p.count; i++) {
    const ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i)), az = Math.abs(n.getZ(i)), x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    if (ay >= ax && ay >= az) { uv[i * 2] = x * s; uv[i * 2 + 1] = -z * s; } else if (ax >= az) { uv[i * 2] = z * s; uv[i * 2 + 1] = y * s; } else { uv[i * 2] = x * s; uv[i * 2 + 1] = y * s; }
  }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); return g;
}""", """function worldUV(g, s) {
  const p = g.attributes.position, n = g.attributes.normal, f = g.attributes.fax, uv = new Float32Array(p.count * 2);
  for (let i = 0; i < p.count; i++) {
    const ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i)), az = Math.abs(n.getZ(i)), x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const k = f ? f.getX(i) : (ay >= ax && ay >= az) ? 1 : ax >= az ? 0 : 2;
    if (k === 1) { uv[i * 2] = x * s; uv[i * 2 + 1] = -z * s; } else if (k === 0) { uv[i * 2] = z * s; uv[i * 2 + 1] = y * s; } else { uv[i * 2] = x * s; uv[i * 2 + 1] = y * s; }
  }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); if (f) g.deleteAttribute('fax'); return g;
}""")

# geometry helpers after beamGeo
rep("""function beamGeo(a, b, t) { const d = tv1.subVectors(b, a), len = d.length(); const g = new THREE.BoxGeometry(len + t, t, t); g.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(XA, d.normalize()))); g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2); return g; }
""", """function beamGeo(a, b, t) { const d = tv1.subVectors(b, a), len = d.length(); const g = new THREE.BoxGeometry(len + t, t, t); g.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(XA, d.normalize()))); g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2); return g; }
// Graphics mode shapes: edges rounded so they catch the light, where Performance mode draws an ink outline instead.
// a box with rounded edges, its faces grouped like BoxGeometry's (+x, -x, +y, -y, +z, -z) so the same material lists apply
function rbox(w, h, d, r, s) {
  r = Math.min(r, w / 2 - 0.005, h / 2 - 0.005, d / 2 - 0.005);
  if (r < 0.02) return new THREE.BoxGeometry(w, h, d);
  const N = (s || 2) * 2 + 1, g = new THREE.BoxGeometry(1, 1, 1, N, N, N), p = g.attributes.position, nr = g.attributes.normal, hs = 0.5 / N, v = new THREE.Vector3();
  const bx = w / 2 - r, by = h / 2 - r, bz = d / 2 - r, fax = new Float32Array(p.count);
  for (const gr of g.groups) for (let k = gr.start; k < gr.start + gr.count; k++) fax[g.index.array[k]] = gr.materialIndex >> 1;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i), sx = Math.sign(x), sy = Math.sign(y), sz = Math.sign(z);
    v.set(x - sx * hs, y - sy * hs, z - sz * hs).normalize();
    p.setXYZ(i, bx * sx + v.x * r, by * sy + v.y * r, bz * sz + v.z * r); nr.setXYZ(i, v.x, v.y, v.z);
  }
  g.setAttribute('fax', new THREE.BufferAttribute(fax, 1)); return g;
}
// sort an indexed geometry's faces into groups by which way they face (pick gets the face normal's y)
function groupByNormal(g, pick) {
  const idx = g.index.array, p = g.attributes.position, out = [[], [], []], a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  for (let t = 0; t < idx.length; t += 3) { a.fromBufferAttribute(p, idx[t]); b.fromBufferAttribute(p, idx[t + 1]).sub(a); c.fromBufferAttribute(p, idx[t + 2]).sub(a); b.cross(c); const l = b.length(); if (l < 1e-10) continue; out[pick(b.y / l)].push(idx[t], idx[t + 1], idx[t + 2]); }
  g.setIndex([...out[0], ...out[1], ...out[2]]); g.clearGroups(); let st = 0; out.forEach((l, i) => { if (l.length) g.addGroup(st, l.length, i); st += l.length; }); return g;
}
// a drum with a rounded top lip, grouped like CylinderGeometry (side, top, bottom)
function bcyl(r, h, b, n) {
  b = Math.min(b, r * 0.45, h * 0.45); const y0 = -h / 2, y1 = h / 2, V2 = (x, y) => new THREE.Vector2(x, y), pts = [V2(0, y0), V2(r, y0), V2(r, y0)];
  for (let k = 0; k <= 6; k++) { const a = k / 6 * Math.PI / 2; pts.push(V2(r - b + Math.cos(a) * b, y1 - b + Math.sin(a) * b)); }
  pts.push(V2(0, y1));
  return groupByNormal(new THREE.LatheGeometry(pts, n), ny => ny > 0.55 ? 1 : ny < -0.55 ? 2 : 0);
}
""")

# AO, normal maps: after the toon factory
rep("""const toon = (c, extra, pbr) => HI ? new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.78, metalness: 0 }, extra || {}, pbr || {})) : new THREE.MeshToonMaterial(Object.assign({ color: c, gradientMap: grad }, extra || {}));
""", """const toon = (c, extra, pbr) => HI ? new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.78, metalness: 0 }, extra || {}, pbr || {})) : new THREE.MeshToonMaterial(Object.assign({ color: c, gradientMap: grad }, extra || {}));
// ---------- Graphics mode ambient occlusion, baked for each stage from a top-down height map ----------
// R: how much open sky each spot sees (walls, pieces and slabs close by shut some of it out). G: the height of the top surface there
const AO_N = 256, aoTex = HI ? new THREE.DataTexture(new Uint8Array(AO_N * AO_N * 4).fill(255), AO_N, AO_N, THREE.RGBAFormat) : null;
if (aoTex) { aoTex.magFilter = aoTex.minFilter = THREE.LinearFilter; aoTex.generateMipmaps = false; aoTex.needsUpdate = true; }
const aoU = { uAOMap: { value: aoTex }, uAORect: { value: new THREE.Vector4(-30, -30, 1 / 60, 0) } };
// surfaces facing sideways look just outside themselves: dark at the foot of a wall, fading out up its face; anything under a slab is shaded
const AO_GLSL = `uniform sampler2D uAOMap; uniform vec4 uAORect;
float stageAO(vec3 w, vec3 n){
  vec2 uv = (w.xz + n.xz * 0.3 - uAORect.xy) * uAORect.z;
  if (uv.x <= 0.0 || uv.y <= 0.0 || uv.x >= 1.0 || uv.y >= 1.0) return 1.0;
  vec4 t = texture2D(uAOMap, uv); float dy = w.y - (t.g * 12.0 - 3.0);
  return mix(t.r, 1.0, smoothstep(0.0, 1.3, dy)) * (1.0 - 0.42 * smoothstep(-0.2, -0.6, dy));
}`;
function aoHook(sh) {
  sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uAORect = aoU.uAORect;
  sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\\nvarying vec3 vAOw, vAOn;').replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\\nvAOw = (modelMatrix * vec4(transformed, 1.0)).xyz; vAOn = normalize(mat3(modelMatrix) * objectNormal);');
  sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying vec3 vAOw, vAOn;\\n' + AO_GLSL).replace('#include <aomap_fragment>', '#include <aomap_fragment>\\n{ float sao = stageAO(vAOw, normalize(vAOn)); reflectedLight.indirectDiffuse *= sao; reflectedLight.indirectSpecular *= sao; reflectedLight.directDiffuse *= mix(1.0, sao, 0.55); reflectedLight.directSpecular *= sao; }');
}
const aoPatch = m => { if (HI && m && m.isMeshStandardMaterial && m.onBeforeCompile !== aoHook) m.onBeforeCompile = aoHook; return m; };
function bakeAO() {
  if (!HI) return;
  const N = AO_N, A = ARENA + 1.5, cs = 2 * A / N, Hm = new Float32Array(N * N), ao = new Float32Array(N * N), data = aoTex.image.data;
  for (let j = 0; j < N; j++) { const z = -A + (j + 0.5) * cs; for (let i = 0; i < N; i++) { const h = surfaceUnder(-A + (i + 0.5) * cs, z, 60); Hm[j * N + i] = h < -3 ? -3 : h; } }
  const DIRS = 8, RS = [0.3, 0.62, 1.0, 1.55, 2.3], R2 = 2.6 * 2.6, dx = [], dz = [];
  for (let k = 0; k < DIRS; k++) { const a = k / DIRS * Math.PI * 2 + 0.2; dx.push(Math.cos(a) / cs); dz.push(Math.sin(a) / cs); }
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const h0 = Hm[j * N + i]; if (h0 <= -3) { ao[j * N + i] = 1; continue; }
    let occ = 0;
    for (let k = 0; k < DIRS; k++) {
      let best = 0;
      for (const r of RS) {
        const ii = Math.round(i + dx[k] * r), jj = Math.round(j + dz[k] * r);
        if (ii < 0 || jj < 0 || ii >= N || jj >= N) break;
        const sl = (Hm[jj * N + ii] - h0) / r; if (sl > 0) { const sn = sl / Math.sqrt(1 + sl * sl) * (1 - r * r / R2 * 0.6); if (sn > best) best = sn; }
      }
      occ += best;
    }
    ao[j * N + i] = Math.max(0, 1 - occ / DIRS * 1.25);
  }
  // a light blur that keeps to one level (a box top never borrows the floor's shade), then pack
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    let sum = 0, c = 0; const h0 = Hm[j * N + i];
    for (let v = -1; v <= 1; v++) for (let u = -1; u <= 1; u++) { const ii = i + u, jj = j + v; if (ii < 0 || jj < 0 || ii >= N || jj >= N || Math.abs(Hm[jj * N + ii] - h0) > 0.3) continue; sum += ao[jj * N + ii]; c++; }
    const o = (j * N + i) * 4; data[o] = Math.round(sum / c * 255); data[o + 1] = Math.round(Math.min(1, (h0 + 3) / 12) * 255); data[o + 2] = 255; data[o + 3] = 255;
  }
  aoTex.needsUpdate = true; aoU.uAORect.value.set(-A, -A, 1 / (2 * A), 0);
}
// Graphics mode relief: a normal map from a texture's own lights and darks, so cobbles, bricks and boards catch the light
function normalFrom(tex, k) {
  if (tex.userData.nrm) return tex.userData.nrm;
  const S = tex.image.width, d = tex.image.getContext('2d').getImageData(0, 0, S, S).data, h = new Float32Array(S * S), b = new Float32Array(S * S);
  for (let i = 0; i < S * S; i++) h[i] = (d[i * 4] * 0.3 + d[i * 4 + 1] * 0.59 + d[i * 4 + 2] * 0.11) / 255;
  const W = (x, y) => ((y + S) % S) * S + (x + S) % S;
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) { let sum = 0; for (let v = -1; v <= 1; v++) for (let u = -1; u <= 1; u++) sum += h[W(x + u, y + v)]; b[y * S + x] = sum / 9; }
  const cv = document.createElement('canvas'); cv.width = cv.height = S; const g = cv.getContext('2d'), im = g.createImageData(S, S), o = im.data;
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const gx = b[W(x + 1, y - 1)] + 2 * b[W(x + 1, y)] + b[W(x + 1, y + 1)] - b[W(x - 1, y - 1)] - 2 * b[W(x - 1, y)] - b[W(x - 1, y + 1)];
    const gy = b[W(x - 1, y + 1)] + 2 * b[W(x, y + 1)] + b[W(x + 1, y + 1)] - b[W(x - 1, y - 1)] - 2 * b[W(x, y - 1)] - b[W(x + 1, y - 1)];
    const nx = -gx * k, ny = gy * k, l = Math.hypot(nx, ny, 1), i = (y * S + x) * 4;
    o[i] = (nx / l * 0.5 + 0.5) * 255; o[i + 1] = (ny / l * 0.5 + 0.5) * 255; o[i + 2] = (1 / l * 0.5 + 0.5) * 255; o[i + 3] = 255;
  }
  g.putImageData(im, 0, 0);
  const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); tex.userData.nrm = t; return t;
}
""")

# theme materials: normal maps, per-theme roughness, AO
rep("""  const fl = T.floor(), sd = T.side(), lighten = (c, k) => new THREE.Color(c).multiplyScalar(k).getHex();
  T.mats = { floor: toon(T.ft, { map: fl }), top: toon(lighten(T.ft, 1.06), { map: fl }), side: toon(T.st, { map: sd }), dark: toon(T.dt, { map: sd }), rampSide: toon(T.st, { map: sd, side: THREE.DoubleSide }),""",
"""  const fl = T.floor(), sd = T.side(), lighten = (c, k) => new THREE.Color(c).multiplyScalar(k).getHex();
  // Graphics mode: each theme's surfaces get relief from their own textures and their own sheen (polished marble, waxed boards, rough moss)
  const nk = T.nrm || [0.7, 0.8], rk = T.rough || [0.78, 0.82];
  const fp = HI ? { normalMap: normalFrom(fl, 1.3), normalScale: new THREE.Vector2(nk[0], nk[0]), roughness: rk[0] } : null, sp = HI ? { normalMap: normalFrom(sd, 1.3), normalScale: new THREE.Vector2(nk[1], nk[1]), roughness: rk[1] } : null;
  T.mats = { floor: toon(T.ft, { map: fl }, fp), top: toon(lighten(T.ft, 1.06), { map: fl }, fp), side: toon(T.st, { map: sd }, sp), dark: toon(T.dt, { map: sd }, sp), rampSide: toon(T.st, { map: sd, side: THREE.DoubleSide }, sp),""")
rep("""metal: toon(0xD6DAE2, null, { metalness: 0.7, roughness: 0.3 }), cream: toon(0xF2E8D2, null, { roughness: 0.55 }), glowY: new THREE.MeshBasicMaterial({ color: 0xFFD27A }), pal: PAL.map(c => toon(c)) };
  return T.mats;""", """metal: toon(0xD6DAE2, null, { metalness: 0.7, roughness: 0.3 }), cream: toon(0xF2E8D2, null, { roughness: 0.55 }), glowY: new THREE.MeshBasicMaterial({ color: 0xFFD27A }), pal: PAL.map(c => toon(c, null, { roughness: 0.42 })) };
  if (HI) for (const k in T.mats) [].concat(T.mats[k]).forEach(aoPatch);
  return T.mats;""")

# stage build: rounder, smoother pieces in Graphics mode, and the AO bake
rep("""  const cyl = (r0, r1, h, n, x, y, z) => at(new THREE.CylinderGeometry(r0, r1, h, n || 28), x, y, z);
  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, 16, 12); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };""",
"""  const cyl = (r0, r1, h, n, x, y, z) => at(new THREE.CylinderGeometry(r0, r1, h, SEG(n || 28)), x, y, z);
  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, SEG(16), SEG(12)); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };""")
rep("""      const body = new THREE.BoxGeometry(along ? sw : th, bodyH, along ? th : sw); body.translate(cx, bodyH / 2, cz);
      const cap = new THREE.CylinderGeometry(sw / 2, sw / 2, th, 18, 1, false, 0, Math.PI);""",
"""      const body = HI ? rbox(along ? sw : th, bodyH, along ? th : sw, 0.05) : new THREE.BoxGeometry(along ? sw : th, bodyH, along ? th : sw); body.translate(cx, bodyH / 2, cz);
      const cap = new THREE.CylinderGeometry(sw / 2, sw / 2, th, SEG(18), 1, false, 0, Math.PI);""")
rep("""    const g = circ ? cyl(rad, rad, h, 44, cx, cy, cz) : at(new THREE.BoxGeometry(w, h, d), cx, cy, cz); worldUV(g, us);""",
"""    const g = HI ? at(circ ? bcyl(rad, h, Math.min(0.11, h * 0.2), 72) : rbox(w, h, d, Math.min(0.1, h * 0.2, w * 0.15, d * 0.15)), cx, cy, cz) : circ ? cyl(rad, rad, h, 44, cx, cy, cz) : at(new THREE.BoxGeometry(w, h, d), cx, cy, cz); worldUV(g, us);""")
rep("""      const own = regroup(g, mats).map(mm => mm.clone()), m = new THREE.Mesh(g, own);""",
"""      const own = regroup(g, mats).map(mm => aoPatch(mm.clone())), m = new THREE.Mesh(g, own);""")
rep("""const tr = new THREE.TorusGeometry(rad - 0.02, 0.07, 8, 44);""", """const tr = new THREE.TorusGeometry(rad - 0.02, 0.07, SEG(8), SEG(44));""")
rep("""put(M.cream, at(new THREE.ConeGeometry(rad, rad * 1.5, 28), cx, top + rad * 0.75, cz)); put(pm, at(new THREE.ConeGeometry(rad * 0.32, rad * 0.5, 16), cx, top + rad * 1.27, cz));""",
"""put(M.cream, at(new THREE.ConeGeometry(rad, rad * 1.5, SEG(28)), cx, top + rad * 0.75, cz)); put(pm, at(new THREE.ConeGeometry(rad * 0.32, rad * 0.5, SEG(16)), cx, top + rad * 1.27, cz));""")
rep("""const tr = new THREE.TorusGeometry(rad, 0.08, 8, 48);""", """const tr = new THREE.TorusGeometry(rad, 0.08, SEG(8), SEG(48));""")
rep("""    put(M.dark, at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push""",
"""    put(M.dark, HI ? worldUV(at(rbox(2.6, 0.7, 2.6, 0.12), x, -0.6, z), us) : at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push""")
rep("""put(M.bark, at(new THREE.CylinderGeometry(0.06, 0.06, 2.2, 8).rotateZ""", """put(M.bark, at(new THREE.CylinderGeometry(0.06, 0.06, 2.2, SEG(8)).rotateZ""")
rep("""at(new THREE.ConeGeometry(0.13, 0.35, 10).rotateX(Math.PI)""", """at(new THREE.ConeGeometry(0.13, 0.35, SEG(10)).rotateX(Math.PI)""")
rep("""  if (!HI) stageGroup.add(new THREE.Mesh(mergeGeos(hulls), outlineMat));
}""", """  if (!HI) stageGroup.add(new THREE.Mesh(mergeGeos(hulls), outlineMat));
  bakeAO();
}""")
rep("""const decalOf = tex => toon(0xE0E0E0, {""", """const decalOf = tex => aoPatch(toon(0xE0E0E0, {""")
rep("""polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
function scatterMat(T) {""", """polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 }, { roughness: 0.7 }));
function scatterMat(T) {""")

# sky world: rounder clouds and far canvases
rep("""  const r = rng(42), sph = new THREE.SphereGeometry(1, 14, 10);""", """  const r = rng(42), sph = new THREE.SphereGeometry(1, SEG(14), SEG(10));""")
rep("""    const bg = new THREE.BoxGeometry(w, 0.7, d); worldUV(bg, 0.5);""", """    const bg = HI ? rbox(w, 0.7, d, 0.18) : new THREE.BoxGeometry(w, 0.7, d); worldUV(bg, 0.5);""")
rep("""  const r = rng(300 + i), sph = new THREE.SphereGeometry(1, 16, 12), list = [];""", """  const r = rng(300 + i), sph = new THREE.SphereGeometry(1, SEG(16), SEG(12)), list = [];""")
open(p,'w').write(s); print('patched')
