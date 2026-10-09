// ---------- the refill stations: every stage has its own. Palette Island pours paint from a bamboo spout into a staved tub,
// the Halloween stages have an open coffin with a quilted lid, lanterns and candles, and Blank Canvas has a dispenser over a round tub ----------
const hexC = c => new THREE.Color(c);
// parts merged into one geometry, each with a color (or a function of the vertex: position, then normal), keeping uvs where a part has them.
// A part given null keeps the colors it already carries. One draw for a whole station's worth of one material
function vcGeo(parts) {
  let n = 0; const list = [];
  for (const [g, c] of parts) { const ng = g.index ? g.toNonIndexed() : g; if (!ng.attributes.normal) ng.computeVertexNormals(); n += ng.attributes.position.count; list.push([ng, c]); }
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2), col = new Float32Array(n * 3), tc = new THREE.Color(); let o = 0;
  for (const [g, c] of list) {
    const P = g.attributes.position, N = g.attributes.normal, k = P.count; pos.set(P.array, o * 3); nor.set(N.array, o * 3); if (g.attributes.uv) uv.set(g.attributes.uv.array, o * 2);
    if (c === null && g.attributes.color) col.set(g.attributes.color.array, o * 3);
    else for (let q = 0; q < k; q++) { const cc = typeof c === 'function' ? c(P.getX(q), P.getY(q), P.getZ(q), tc, N.getX(q), N.getY(q), N.getZ(q)) : c; col[(o + q) * 3] = cc.r; col[(o + q) * 3 + 1] = cc.g; col[(o + q) * 3 + 2] = cc.b; }
    o += k;
  }
  const m = new THREE.BufferGeometry(); m.setAttribute('position', new THREE.BufferAttribute(pos, 3)); m.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); m.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); m.setAttribute('color', new THREE.BufferAttribute(col, 3));
  return m;
}
// a surface from a grid of points (f fills o for u and v in 0..1); flip turns its faces the other way
function gridGeo(nu, nv, f, flip) {
  const pos = new Float32Array((nu + 1) * (nv + 1) * 3), uvs = new Float32Array((nu + 1) * (nv + 1) * 2), idx = [], o = new THREE.Vector3(); let k = 0;
  for (let j = 0; j <= nv; j++) for (let i = 0; i <= nu; i++, k++) { f(i / nu, j / nv, o); pos[k * 3] = o.x; pos[k * 3 + 1] = o.y; pos[k * 3 + 2] = o.z; uvs[k * 2] = i / nu; uvs[k * 2 + 1] = j / nv; }
  for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) { const a = j * (nu + 1) + i, b = a + 1, c = a + nu + 1, d = c + 1; if (flip) idx.push(a, c, b, b, c, d); else idx.push(a, b, c, b, d, c); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.BufferAttribute(uvs, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
const uvXY = (g, f) => { const P = g.attributes.position, uv = new Float32Array(P.count * 2); for (let i = 0; i < P.count; i++) { const r = f(P.getX(i), P.getY(i), P.getZ(i)); uv[i * 2] = r[0]; uv[i * 2 + 1] = r[1]; } g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); return g; };
function tubeBetween(a, b, r0, r1, n, open) { const d = new THREE.Vector3().subVectors(b, a), L = d.length(), g = new THREE.CylinderGeometry(r1, r0, L, n, 1, !!open); g.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(YAX, d.normalize()))); g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2); return g; }
const ZAX3 = new THREE.Vector3(0, 0, 1);
const alignZ = (g, dir, at) => { g.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(ZAX3, dir.clone().normalize()))); g.translate(at.x, at.y, at.z); return g; };
// a ring of rope: three strands twisting round each other (colored, lying flat about the origin)
function ropeRing(R, r, tw) {
  const nA = Math.min(96, Math.max(16, Math.round(R * (HI ? 240 : 140)))), g = gridGeo(nA, HI ? 7 : 5, (u, v, o) => { const a = u * 6.2832, ph = v * 6.2832, rr = r * (1 + 0.22 * Math.cos(3 * ph + a * tw)); o.set((R + rr * Math.cos(ph)) * Math.cos(a), rr * Math.sin(ph), (R + rr * Math.cos(ph)) * Math.sin(a)); }, true);
  uvXY(g, (x, y, z) => [Math.atan2(z, x) * R * 6, y * 3]);
  const c0 = hexC(0xD6AE72); return vcGeo([[g, (x, y, z, o) => { const a = Math.atan2(z, x), ph = Math.atan2(y, Math.hypot(x, z) - R); return o.copy(c0).multiplyScalar(0.72 + 0.28 * (0.5 + 0.5 * Math.cos(3 * ph + a * tw))); }]]);
}
// paint run over a rim and down the outside wall (wallR gives the wall's radius at a height): thick where it leaves, a bead at the end.
// The mesh sits at the rim's height and shrinks upward as the paint runs out
const rimDrips = (seed, wallR, yTop, n, len0, len1) => { const r = rng(seed), list = []; for (let k = 0; k < n; k++) { const a = r() * 6.2832, c = Math.cos(a), s2 = Math.sin(a), len = len0 + r() * (len1 - len0), y1 = yTop - 0.01, y2 = y1 - len, r1 = wallR(y1) + 0.017, r2 = wallR(y2) + 0.021;
  list.push(tubeBetween(new THREE.Vector3(c * r1, y1, s2 * r1), new THREE.Vector3(c * r2, y2, s2 * r2), 0.026, 0.019, 10), new THREE.SphereGeometry(0.031, 12, 10).scale(1, 1.3, 1).translate(c * r2, y2, s2 * r2), new THREE.SphereGeometry(0.036, 12, 8).scale(1.25, 0.5, 1.25).translate(c * (wallR(yTop) - 0.012), yTop + 0.004, s2 * (wallR(yTop) - 0.012))); }
  const g = mergeGeos(list); g.translate(0, -yTop, 0); return g; };
// a lumpy splat of paint on the floor beside a station
const spillAt = (seed, rad, y, sz) => { const r = rng(seed + 5), g = new THREE.CircleGeometry(1, 36), P = g.attributes.position, f = [[3, r() * 6, 0.18], [5, r() * 6, 0.1], [2, r() * 6, 0.14]];
  for (let q = 1; q < P.count; q++) { const x = P.getX(q), yy = P.getY(q), a = Math.atan2(yy, x); let k = 1; for (const [m, ph, am] of f) k += am * Math.sin(a * m + ph); P.setXY(q, x * k * sz, yy * k * sz); }
  g.rotateX(-Math.PI / 2); const a = r() * 6.28; g.translate(Math.cos(a) * rad, y, Math.sin(a) * rad); return g; };
const BAM = hexC(0xE0C878), BAM_N = hexC(0xA9883F), LEAF_A = hexC(0x23763A), LEAF_B = hexC(0x55C24F);
// shared materials: the wood ones reuse the coffin's vertex-colored wood; the rest are plain vertex color, glossy, metal, and two that glow
const stPlainM = toon(0xFFFFFF, { vertexColors: true, side: THREE.DoubleSide }, { roughness: 0.62 });
const stGlossM = toon(0xFFFFFF, { vertexColors: true }, { roughness: 0.3 });
const stMetalM = toon(0xFFFFFF, { vertexColors: true }, { roughness: 0.3, metalness: 0.85 });
const stGlowM = new THREE.MeshBasicMaterial({ vertexColors: true, color: new THREE.Color(1, 1, 1).multiplyScalar(2.6) });
const stLedM = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xFFE6BC).multiplyScalar(2.3) });
let potDropM = null; const potDrop = () => potDropM || (potDropM = colMat(0xD3112C)); // paint drops (made on first use: colMat comes later)
// warm glows that flicker, one draw for all of a station's lamps and flames (they ride along when it sinks and rises)
const stGlowSpriteM = new THREE.ShaderMaterial({ uniforms: { uTime: paintUniforms.uTime, uK: { value: HI ? 1.7 : 1 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec3 aQ; attribute vec4 aCol; uniform float uTime; varying vec2 vUv; varying vec3 vCol;
    void main(){ vUv = aQ.xy + 0.5; vCol = aCol.rgb; float ph = aCol.a + dot(modelMatrix[3].xyz, vec3(1.3, 0.7, 2.1)), s = aQ.z * (0.86 + 0.12 * sin(uTime * 11.0 + ph) + 0.06 * sin(uTime * 23.0 + ph * 1.83));
      vec4 mv = modelViewMatrix * vec4(position, 1.0); mv.xy += aQ.xy * s * length(modelMatrix[0].xyz); gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform float uK; varying vec2 vUv; varying vec3 vCol;
    void main(){ float r = length(vUv - 0.5) * 2.0, a = r < 0.22 ? mix(1.0, 0.6, r / 0.22) : 0.6 * max(0.0, 1.0 - (r - 0.22) / 0.78); a *= a * 0.35 + 0.65;
      gl_FragColor = vec4(vCol * uK, a);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
function glowCluster(list) {
  const n = list.length, pos = new Float32Array(n * 12), q = new Float32Array(n * 12), col = new Float32Array(n * 16), idx = [], c = new THREE.Color();
  list.forEach(([x, y, z, s, cc], i) => { c.set(cc); [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]].forEach(([cx, cy], k) => { const v = i * 4 + k; pos.set([x, y, z], v * 3); q.set([cx, cy, s], v * 3); col.set([c.r, c.g, c.b, i * 1.7], v * 4); }); idx.push(i * 4, i * 4 + 1, i * 4 + 2, i * 4, i * 4 + 2, i * 4 + 3); });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aQ', new THREE.BufferAttribute(q, 3)); g.setAttribute('aCol', new THREE.BufferAttribute(col, 4)); g.setIndex(idx);
  const m = new THREE.Mesh(g, stGlowSpriteM); m.frustumCulled = false; m.renderOrder = 9; return m;
}
// paint pouring: the stream's surface wobbles as bulges run down it, glints slide down, and it thins away to nothing when the station runs dry
function streamSurf(m) {
  const rad = { value: 1 }; m.userData.rad = rad;
  m.onBeforeCompile = sh => { sh.uniforms.uTime = paintUniforms.uTime; sh.uniforms.uRad = rad;
    sh.vertexShader = 'uniform float uTime, uRad;\nattribute vec3 aC;\nattribute vec2 aFl;\nvarying float vFl;\n' + sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      vFl = aFl.x; float wv = sin(aFl.x * 30.0 - uTime * 34.0) * 0.6 + sin(aFl.x * 13.0 - uTime * 19.0 + 1.3) * 0.4;
      transformed = aC + (position - aC) * uRad * (1.0 + 0.16 * wv * aFl.y);`);
    sh.fragmentShader = 'uniform float uTime;\nvarying float vFl;\n' + sh.fragmentShader.replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\ntotalEmissiveRadiance += diffuseColor.rgb * 0.55 * pow(max(0.0, sin(vFl * 19.0 - uTime * 27.0)), 12.0);'); };
  m.customProgramCacheKey = () => 'paint-stream-' + m.type; return m;
}
// the stream's mesh: rings round a curve (an ellipse each, so it can be a round pour or a flat sheet), each vert knowing its ring's center so it can thin out
function streamGeo(curve, n, m, prof, wob) {
  const pos = [], nor = [], cen = [], fl = [], idx = [], Pt = new THREE.Vector3(), T = new THREE.Vector3(), B0 = new THREE.Vector3(1, 0, 0), N = new THREE.Vector3(), B = new THREE.Vector3(), L = curve.getLength();
  for (let i = 0; i <= n; i++) { const t = i / n; curve.getPointAt(t, Pt); curve.getTangentAt(t, T); N.crossVectors(T, B0).normalize(); B.crossVectors(N, T).normalize(); const [ra, rb] = prof(t), w = wob(t);
    for (let j = 0; j <= m; j++) { const a = j / m * 6.2832, ca = Math.cos(a), sa = Math.sin(a); pos.push(Pt.x + B.x * ca * ra + N.x * sa * rb, Pt.y + B.y * ca * ra + N.y * sa * rb, Pt.z + B.z * ca * ra + N.z * sa * rb);
      const nx = B.x * ca * rb + N.x * sa * ra, ny = B.y * ca * rb + N.y * sa * ra, nz = B.z * ca * rb + N.z * sa * ra, nl = Math.hypot(nx, ny, nz) || 1; nor.push(nx / nl, ny / nl, nz / nl); cen.push(Pt.x, Pt.y, Pt.z); fl.push(t * L, w); } }
  for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) { const a = i * (m + 1) + j, b = a + m + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3)); g.setAttribute('aC', new THREE.Float32BufferAttribute(cen, 3)); g.setAttribute('aFl', new THREE.Float32BufferAttribute(fl, 2)); g.setIndex(idx); return g;
}
// a crown of paint thrown up round a blob that dives in (a flared wall drawn up into points, a drop on each), a jet when it leaps out, and the little boil where a stream lands
const POT_CROWN_G = (() => { const N = 9, M = HI ? 63 : 36, parts = [];
  const wall = (ins, flip) => gridGeo(M, 4, (u, v, o) => { const a = u * 6.2832, k = Math.pow(Math.max(0, Math.cos(a * N)), 3), h = (0.08 + 0.13 * k) * v, r = 0.19 + 0.09 * v + 0.05 * v * v * k - ins; o.set(Math.cos(a) * r, h, Math.sin(a) * r); }, flip);
  parts.push(wall(0, true), wall(0.014, false));
  for (let k = 0; k < N; k++) { const a = k / N * 6.2832; parts.push(new THREE.SphereGeometry(0.028, 8, 6).translate(Math.cos(a) * 0.34, 0.25, Math.sin(a) * 0.34)); }
  return mergeGeos(parts); })();
const POT_JET_G = mergeGeos([new THREE.CylinderGeometry(0.016, 0.05, 0.2, 10, 1, true).translate(0, 0.1, 0), new THREE.SphereGeometry(0.04, 10, 8).translate(0, 0.24, 0), new THREE.SphereGeometry(0.075, 12, 6, 0, 6.2832, 0, Math.PI / 2).scale(1, 0.35, 1)]);
const POT_FOAM_G = mergeGeos([new THREE.TorusGeometry(0.052, 0.017, 6, 18).rotateX(Math.PI / 2), new THREE.SphereGeometry(0.046, 12, 6, 0, 6.2832, 0, Math.PI / 2).scale(1, 0.55, 1)]);
// a disc of rings stretched out to an outline (convex round the middle), so paint in an odd-shaped vessel can ripple all over
function polySurf(pts, rings, segs) {
  const rad = a => { const dx = Math.cos(a), dz = Math.sin(a); let best = 1e9; for (let i = 0; i < pts.length; i++) { const p = pts[i], q = pts[(i + 1) % pts.length], ex = q[0] - p[0], ez = q[1] - p[1], den = ex * dz - dx * ez; if (Math.abs(den) < 1e-9) continue; const t = (ex * p[1] - p[0] * ez) / den, s = (dx * p[1] - dz * p[0]) / den; if (t > 0 && s >= -1e-6 && s <= 1 + 1e-6) best = Math.min(best, t); } return best; };
  return gridGeo(segs, rings, (u, v, o) => { const a = u * 6.2832, r = rad(a) * v; o.set(Math.cos(a) * r, 0, Math.sin(a) * r); }, false);
}
// leaves and flowers for the island station: a leaf (base at the origin, out along +x, a raised middle and an upturned tip) and a hibiscus
function leafG(L, W) { const g = new THREE.CircleGeometry(1, HI ? 12 : 8), P = g.attributes.position; for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), u = (x + 1) * 0.5, tip = x > 0 ? 1 - 0.4 * x * x : 1; P.setXYZ(i, u * L, 0.05 * L * (1 - y * y) + 0.16 * L * u * u, y * W * 0.5 * tip); } g.computeVertexNormals(); return g; }
function hibiscusG(s) {
  const parts = [], cA = hexC(0x9E0E25), cB = hexC(0xF0283C), cC = hexC(0xFF6670);
  for (let k = 0; k < 5; k++) { const g = new THREE.CircleGeometry(1, HI ? 12 : 8), P = g.attributes.position;
    for (let i = 0; i < P.count; i++) { const x = (P.getX(i) + 1) * 0.5, y = P.getY(i); P.setXYZ(i, x * s, 0.5 * s * x * x, y * s * 0.44 * (0.5 + 0.5 * x)); }
    g.rotateY(-(k / 5) * 6.2832); g.computeVertexNormals();
    parts.push([g, (x, y, z, o) => { const t = Math.min(1, Math.hypot(x, z) / s); return t < 0.32 ? o.copy(cA).lerp(cB, t / 0.32) : o.copy(cB).lerp(cC, (t - 0.32) / 0.68 * 0.7); }]); }
  parts.push([new THREE.CylinderGeometry(0.0045, 0.006, s * 0.95, 5).translate(0, s * 0.475, 0).rotateZ(-0.4), hexC(0xFFE6A8)]);
  parts.push([new THREE.SphereGeometry(0.013, 8, 6).translate(0, s * 0.95, 0).rotateZ(-0.4), hexC(0xFFB81A)]);
  return vcGeo(parts);
}
function stoneG(r, seed) { const g = new THREE.SphereGeometry(1, HI ? 12 : 8, HI ? 9 : 6), P = g.attributes.position, rr = rng(seed), f = [1 + rr() * 2, rr() * 6, 1 + rr() * 3, rr() * 6];
  for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i), k = 1 + 0.12 * Math.sin(x * 3.1 * f[0] + f[1]) * Math.cos(z * 2.7 * f[2] + f[3]) + 0.06 * Math.sin(y * 5 + f[1]); P.setXYZ(i, x * r * k, Math.max(-0.25, y) * r * 0.62 * k, z * r * 0.9 * k); }
  g.computeVertexNormals(); return g; }

// ---- Palette Island: a staved tub on a round plank deck, a bamboo pole and spout pouring paint into it, palm fronds on top, rope, stones and hibiscus ----
const TIKI = (() => {
  const R = rng(4242), DY = 0.055, DR = 0.8, TB = 0.47, TT = 0.545, TH = 0.45, WALL = 0.045, NS = HI ? 18 : 14, y0 = DY;
  const tubR = t => TB + (TT - TB) * t + 0.018 * Math.sin(Math.PI * t);
  const tub = [], deck = [], plant = [], canopy = [], woodC = [0xA36B44, 0xB57C4F, 0x96613D, 0xAA7349].map(hexC);
  // the deck: planks across a circle, their ends cut to the round, a finger's gap between
  const PW = 0.17, GAP = 0.032, NP = Math.floor((2 * DR + GAP) / (PW + GAP)), z0 = -(NP * (PW + GAP) - GAP) / 2;
  for (let i = 0; i < NP; i++) {
    const za = z0 + i * (PW + GAP), zb = za + PW, end = sx => { const pts = []; for (let k = 0; k <= 4; k++) { const z = za + (zb - za) * k / 4; pts.push([sx * Math.sqrt(Math.max(0.0004, DR * DR - z * z)), -z]); } return pts; };
    const sh = new THREE.Shape(); [...end(-1), ...end(1).reverse()].forEach(([x, y], k) => k ? sh.lineTo(x, y) : sh.moveTo(x, y)); sh.closePath();
    const h = DY - 0.002 + R() * 0.006, g = new THREE.ExtrudeGeometry(sh, { depth: h - 0.016, bevelEnabled: true, bevelThickness: 0.008, bevelSize: 0.008, bevelSegments: 1, curveSegments: 1 });
    g.rotateX(-Math.PI / 2); g.translate(0, 0.008, 0); uvXY(g, (x, y, z) => [x * 1.7, z * 1.7 + i * 0.37]);
    const c = woodC[(i * 3 + 1) % 4].clone().multiplyScalar(0.84 + R() * 0.18); deck.push([g, (x, y, z, o, nx, ny) => o.copy(c).multiplyScalar(ny > 0.5 ? 1 : 0.72)]);
  }
  // the tub: staves round a gently bellied barrel, a hair apart, each its own tone, darker where it meets the deck
  for (let i = 0; i < NS; i++) {
    const ac = (i + 0.5) / NS * 6.2832, hw = Math.PI / NS - 0.005 / TT, a0 = ac - hw, a1 = ac + hw, top = TH + (R() - 0.5) * 0.024, nu = HI ? 4 : 2, nv = HI ? 6 : 4;
    const P = (a, t, ins, o) => { const r = tubR(t) - ins; return o.set(Math.cos(a) * r, y0 + t * top, Math.sin(a) * r); };
    const c = woodC[(i * 7) % 4].clone().multiplyScalar(0.86 + R() * 0.22), col = (x, y, z, o, nx, ny) => o.copy(c).multiplyScalar((0.64 + 0.36 * Math.min(1, (y - y0) / 0.16)) * (ny > 0.6 ? 1.12 : 1));
    for (const g of [gridGeo(nu, nv, (u, v, o) => P(a0 + (a1 - a0) * u, v, 0, o), true), gridGeo(nu, nv, (u, v, o) => P(a0 + (a1 - a0) * u, v, WALL, o), false), gridGeo(nu, 1, (u, v, o) => P(a0 + (a1 - a0) * u, 1, WALL * v, o), true), gridGeo(1, nv, (u, v, o) => P(a0, v, WALL * u, o), false), gridGeo(1, nv, (u, v, o) => P(a1, v, WALL * u, o), true)])
      tub.push([uvXY(g, (x, y, z) => { const a = Math.atan2(z, x), da = Math.atan2(Math.sin(a - ac), Math.cos(a - ac)); return [y * 2.2, da * 1.2 + i * 0.31]; }), col]);
  }
  // the paint's floor, dark red, at the bottom of the tub
  tub.push([new THREE.CircleGeometry(tubR(0.08) - WALL, 28).rotateX(-Math.PI / 2).translate(0, y0 + 0.04, 0), hexC(0x5A1426)]);
  // two hoops of split bamboo, short canes standing between them, a bamboo ring and a rope round its foot
  const bamCol = nn => (x, y, z, o) => { const a = Math.atan2(z, x), f = ((a / 6.2832 * nn) % 1 + 1) % 1; return o.copy(f < 0.035 || f > 0.965 ? BAM_N : BAM).multiplyScalar(0.92 + 0.08 * Math.sin(a * 37)); };
  const band = t => uvXY(gridGeo(HI ? 80 : 40, HI ? 8 : 5, (u, v, o) => { const a = u * 6.2832, ph = v * 6.2832, r = tubR(t) + 0.022 * (0.5 + 0.5 * Math.cos(ph)); o.set(Math.cos(a) * r, y0 + t * TH + Math.sin(ph) * 0.026, Math.sin(a) * r); }, true), (x, y, z) => [Math.atan2(z, x) * 3, y * 4]);
  tub.push([band(0.22), bamCol(9)], [band(0.8), bamCol(9)]);
  for (let k = 0; k < 4; k++) { const a = k / 4 * 6.2832 + 0.4, r0 = tubR(0.16) + 0.016, r1 = tubR(0.86) + 0.016; tub.push([uvXY(tubeBetween(new THREE.Vector3(Math.cos(a) * r0, y0 + 0.16 * TH, Math.sin(a) * r0), new THREE.Vector3(Math.cos(a) * r1, y0 + 0.86 * TH, Math.sin(a) * r1), 0.016, 0.016, HI ? 10 : 6), (x, y, z) => [y * 3, Math.atan2(z, x) * 0.5]), BAM]); }
  tub.push([uvXY(new THREE.TorusGeometry(TB + 0.035, 0.024, HI ? 8 : 5, HI ? 72 : 36).rotateX(Math.PI / 2).translate(0, y0 + 0.022, 0), (x, y, z) => [Math.atan2(z, x) * 3, y * 4]), bamCol(8)]);
  // the pole: a bamboo cane with its rings, cut open at the top; the spout, a fatter cane leaning down over the tub, lashed on with rope
  const PZ = -0.69, pr = 0.05, PTOP = 1.22, J = new THREE.Vector3(0, 0.9, PZ), dir = new THREE.Vector3(0, -0.36, 1).normalize(), MO = J.clone().addScaledVector(dir, 0.3);
  const ny = [y0, 0.36, 0.66, 0.96, PTOP];
  for (let k = 0; k < ny.length - 1; k++) deck.push([uvXY(new THREE.CylinderGeometry(pr * 0.96, pr, ny[k + 1] - ny[k], HI ? 16 : 10, 1, true).translate(0, (ny[k] + ny[k + 1]) / 2, PZ), (x, y, z) => [y * 3, Math.atan2(z - PZ, x) * 0.4]), (x, y, z, o) => o.copy(BAM).multiplyScalar(0.86 + 0.14 * (y - ny[k]) / (ny[k + 1] - ny[k]))]);
  for (const y of ny.slice(1, -1)) deck.push([new THREE.TorusGeometry(pr + 0.002, 0.009, 6, HI ? 20 : 12).rotateX(Math.PI / 2).translate(0, y, PZ), BAM_N]);
  deck.push([new THREE.TorusGeometry(pr - 0.005, 0.007, 6, HI ? 20 : 12).rotateX(Math.PI / 2).translate(0, PTOP, PZ), BAM_N]);
  plant.push([new THREE.CircleGeometry(pr - 0.006, 14).rotateX(-Math.PI / 2).translate(0, PTOP - 0.025, PZ), hexC(0x3B2A12)]);
  deck.push([uvXY(tubeBetween(J.clone().addScaledVector(dir, -0.05), MO, 0.056, 0.056, HI ? 16 : 10, true), (x, y, z) => [(z - PZ) * 3, x * 3 + y]), (x, y, z, o) => o.copy(BAM).multiplyScalar(0.9)]);
  deck.push([alignZ(new THREE.TorusGeometry(0.058, 0.009, 6, HI ? 20 : 12), dir, J.clone().addScaledVector(dir, 0.15)), BAM_N]);
  deck.push([alignZ(new THREE.TorusGeometry(0.05, 0.008, 6, HI ? 20 : 12), dir, MO), BAM_N]);
  plant.push([alignZ(new THREE.CircleGeometry(0.05, 14), dir.clone().negate(), MO.clone().addScaledVector(dir, -0.09)), hexC(0x2A1D0C)]);
  for (const dy of [-0.05, 0, 0.05]) { const g = ropeRing(pr + 0.016, 0.016, 7); g.translate(0, J.y + dy, PZ); deck.push([g, null]); }
  for (const yy of [y0 + 0.03, y0 + 0.07]) { const g = ropeRing(pr + 0.015, 0.015, 7); g.translate(0, yy, PZ); deck.push([g, null]); }
  { const g = ropeRing(TB + 0.07, 0.016, 5); g.translate(0, y0 + 0.012, 0); tub.push([g, null]); }
  // palm fronds on the pole's top, leaning away from the tub, and a few coconuts under them (built about the crown)
  const fA = [-90, -48, -132, -8, -172, 28, 152].map(d => d * Math.PI / 180);
  fA.forEach((a, k) => { const L = (0.62 + R() * 0.16) * (1 - 0.18 * Math.max(0, Math.sin(a))), g = frondGeo(new THREE.Vector3(0, 0.02, 0), a + (R() - 0.5) * 0.2, L, 0.2, 0.9 + R() * 0.25), sh = 0.9 + 0.1 * Math.sin(k * 2.3);
    canopy.push([g, (x, y, z, o) => o.copy(LEAF_A).lerp(LEAF_B, Math.min(1, Math.hypot(x, z) / L) * 0.85).multiplyScalar(sh)]); });
  for (let k = 0; k < 3; k++) { const a = k * 2.1 + 0.5; canopy.push([new THREE.SphereGeometry(0.045, 10, 8).translate(Math.cos(a) * 0.055, -0.045, Math.sin(a) * 0.055), hexC(0x6B4A2A)]); }
  // round its edge: rope-bound posts at the front, stones, and hibiscus fanning out of the deck's rim
  for (const a of [Math.PI / 2 - 0.62, Math.PI / 2 + 0.62]) { const cx = Math.cos(a) * 0.72, cz = Math.sin(a) * 0.72;
    deck.push([uvXY(new THREE.CylinderGeometry(0.058, 0.064, 0.25, HI ? 14 : 8).translate(cx, y0 + 0.125, cz), (x, y, z) => [y * 2.4, Math.atan2(z - cz, x - cx) * 0.4]), (x, y, z, o) => o.copy(woodC[2]).multiplyScalar(0.78 + 0.22 * Math.min(1, (y - y0) / 0.1))]);
    deck.push([uvXY(new THREE.SphereGeometry(0.058, HI ? 14 : 8, 6, 0, 6.2832, 0, Math.PI / 2).scale(1, 0.5, 1).translate(cx, y0 + 0.25, cz), (x, y, z) => [x * 2, z * 2]), woodC[2]]);
    for (const yy of [y0 + 0.09, y0 + 0.16]) { const g = ropeRing(0.072, 0.014, 6); g.translate(cx, yy, cz); deck.push([g, null]); } }
  [[3.75, 0.72, 0.1, 11], [-0.6, 0.73, 0.085, 12], [1.85, 0.75, 0.062, 13]].forEach(([a, r, s, sd]) => { const g = stoneG(s, sd); g.translate(Math.cos(a) * r, y0 + s * 0.2, Math.sin(a) * r); plant.push([g, (x, y, z, o) => o.setHex(0x9A958E).multiplyScalar(0.8 + 0.3 * Math.min(1, Math.max(0, (y - y0) / (s * 0.6))))]); });
  const cluster = (aOut, rad, n, fl) => { const cx = Math.cos(aOut) * rad, cz = Math.sin(aOut) * rad;
    for (let k = 0; k < n; k++) { const a = aOut + (k / (n - 1) - 0.5) * 2.3 + (R() - 0.5) * 0.3, g = leafG(0.16 + R() * 0.06, 0.075 + R() * 0.02); g.rotateZ(0.25 + R() * 0.35); g.rotateY(-a); g.translate(cx, y0 - 0.004, cz); plant.push([g, (x, y, z, o) => o.copy(LEAF_A).lerp(LEAF_B, Math.min(1, Math.hypot(x - cx, z - cz) / 0.21))]); }
    for (let k = 0; k < fl; k++) { const g = hibiscusG(0.078 + R() * 0.016), a = aOut + (k - (fl - 1) / 2) * 0.95; g.rotateZ(0.42); g.rotateY(-a); g.translate(cx + Math.cos(a) * 0.035, y0 + 0.045 + k * 0.015, cz + Math.sin(a) * 0.035); plant.push([g, null]); } };
  cluster(0.5, 0.68, 5, 2); cluster(Math.PI - 0.5, 0.68, 5, 1); cluster(4.05, 0.69, 4, 1);
  // the stream: out of the spout's mouth, curling over its lip and dropping into the tub
  const sc = new THREE.CatmullRomCurve3([MO.clone().addScaledVector(dir, -0.06), MO.clone().addScaledVector(dir, 0.006), new THREE.Vector3(0, MO.y - 0.06, MO.z + 0.035), new THREE.Vector3(0, MO.y - 0.2, MO.z + 0.05), new THREE.Vector3(0, 0.4, MO.z + 0.055), new THREE.Vector3(0, y0 + 0.02, MO.z + 0.056)], false, 'centripetal');
  const stream = streamGeo(sc, HI ? 40 : 20, HI ? 12 : 8, t => { const r = t < 0.15 ? 0.041 : 0.041 - 0.012 * Math.min(1, (t - 0.15) / 0.5); return [r, r]; }, t => Math.min(1, Math.max(0, (t - 0.08) / 0.12)));
  const tubHull = new THREE.CylinderGeometry(TT + 0.04, TB + 0.035, TH + 0.03, 28, 1, true).translate(0, y0 + TH / 2 + 0.005, 0);
  const hull = mergeGeos([new THREE.CylinderGeometry(DR + 0.03, DR + 0.03, DY + 0.012, 40).translate(0, (DY + 0.012) / 2 - 0.006, 0), new THREE.CylinderGeometry(pr + 0.017, pr + 0.017, PTOP - y0, 12, 1, true).translate(0, (PTOP + y0) / 2, PZ), tubeBetween(J.clone().addScaledVector(dir, -0.02), MO.clone().addScaledVector(dir, 0.012), 0.071, 0.071, 12, true)]);
  const lv0 = y0 + 0.045, lv1 = y0 + TH - 0.055, rIn = y => tubR(Math.max(0, Math.min(1, (y - y0) / TH))) - WALL - 0.004;
  return { tub: vcGeo(tub), deck: vcGeo(deck), plant: vcGeo(plant), canopy: vcGeo(canopy), crownAt: new THREE.Vector3(0, PTOP, PZ), tubHull, hull, stream, src: [0, MO.z + 0.055], lv0, lvK: lv1 - lv0, rIn, wallR: y => tubR(Math.max(0, Math.min(1, (y - y0) / TH))), yTop: y0 + TH, surf: new THREE.RingGeometry(0, 1, HI ? 56 : 28, HI ? 6 : 3).rotateX(-Math.PI / 2) };
})();
function tikiDeco(p, dt, bo) {
  if (bo > p.dB + 0.05) p.cV += 2.6 * (Math.random() < 0.5 ? -1 : 1); p.dB = bo; const h = Math.min(dt, 0.05);
  p.cV += (-26 * p.cA - 2.6 * p.cV) * h; p.cA += p.cV * h;
  const w = Math.sin(clock * 1.25 + p.phase) * 0.028 + Math.sin(clock * 2.7 + p.phase * 1.7) * 0.012;
  p.canopy.rotation.set(p.cA * 0.5 + w, 0, p.cA * 0.32 - w * 0.6);
}
// the parts every station shares: its paint materials, the paint's surface, the drips and spill, the pour, the splash pieces, and the ring
function stationBase(x, y, z, seed, kind) {
  const g = new THREE.Group(), inner = new THREE.Group(), tub = new THREE.Group(); g.add(inner); inner.add(tub);
  const bm = toon(C.velvet), tm = toon(C.ink, null, { roughness: 0.22 }), lm = paintSurf(toon(C.ink, null, { roughness: 0.1 }), seed);
  const ring = new THREE.Mesh(ringG, potRingMat()); ring.rotation.x = -Math.PI / 2; ring.position.y = 0.07; ring.renderOrder = 3; g.add(ring);
  const crown = new THREE.Mesh(POT_CROWN_G, tm), jet = new THREE.Mesh(POT_JET_G, tm); crown.visible = jet.visible = false; tub.add(crown); tub.add(jet);
  g.position.set(x, y, z); g.rotation.y = rng(seed + 3)() * 6.28; scene.add(g);
  return { g, inner, tub, bm, tm, lm, ring, crown, jet, x, y, z, kind, bA: 0, bV: 0, lastB: 0, slosh: 0, crT: 9, jtT: 9, dripT: 0, dripN: 0, flow: 1, cA: 0, cV: 0, dB: 0, lastOcc: null };
}
function addPour(p, geo, src, seed) {
  const sm = streamSurf(toon(C.ink, null, { roughness: 0.12 })), st = new THREE.Mesh(geo, sm); st.frustumCulled = false; p.inner.add(st);
  const foam = new THREE.Mesh(POT_FOAM_G, p.tm); foam.position.set(src[0], 0.3, src[1]); p.tub.add(foam);
  p.lm.userData.wave.uSrc.value.set(src[0], src[1], 1); Object.assign(p, { sm, stream: st, foam, src });
}
function makeTiki(x, y, z, seed) {
  const T = TIKI, p = stationBase(x, y, z, seed, 'tiki'), { inner, tub } = p;
  const tw = new THREE.Mesh(T.tub, cofVC); tw.castShadow = true; tub.add(tw); tub.add(new THREE.Mesh(T.tubHull, outlineMat));
  const dk = new THREE.Mesh(T.deck, cofVC); dk.castShadow = true; dk.receiveShadow = true; inner.add(dk); inner.add(new THREE.Mesh(T.hull, outlineMat));
  inner.add(new THREE.Mesh(T.plant, stPlainM));
  const cn = new THREE.Mesh(T.canopy, stPlainM); cn.castShadow = true; cn.position.copy(T.crownAt); inner.add(cn);
  const liq = new THREE.Mesh(T.surf, p.lm); liq.position.y = 0.3; tub.add(liq);
  const drips = new THREE.Mesh(rimDrips(seed, T.wallR, T.yTop, 3, 0.08, 0.24), p.tm); drips.position.y = T.yTop; tub.add(drips);
  const spill = new THREE.Mesh(spillAt(seed, 0.62, 0.061, 0.2), p.tm); spill.renderOrder = 2; inner.add(spill);
  Object.assign(p, { liq, drips, spill, canopy: cn, lv0: T.lv0, lvK: T.lvK, liqR: T.rIn, lift: 0.065, sinkD: 1.0, deco: tikiDeco, deb: DEB.tiki });
  addPour(p, T.stream, T.src, seed); return p;
}

// ---- the Halloween coffin: dark wood with gilt edges and corner straps, raised panels with a little ghost badge, the lid standing open on its
// hinge with quilted red velvet and a glowing bat inside, two lanterns at its foot, candles round it, all on a round stone dais ----
const NCOF = [[0.26, 0.62], [0.42, 0.24], [0.22, -0.62], [-0.22, -0.62], [-0.42, 0.24], [-0.26, 0.62]], NCH = 0.42, CPY = 0.05, LID_OPEN = 1.676;
const offsetPoly = (pts, d) => pts.map((p1, i) => { const n = pts.length, p0 = pts[(i + n - 1) % n], p2 = pts[(i + 1) % n], nn = (a, b) => { const ex = b[0] - a[0], ey = b[1] - a[1], l = Math.hypot(ex, ey); return [-ey / l, ex / l]; }, n1 = nn(p0, p1), n2 = nn(p1, p2), k = d / (1 + n1[0] * n2[0] + n1[1] * n2[1]); return [p1[0] + (n1[0] + n2[0]) * k, p1[1] + (n1[1] + n2[1]) * k]; });
const polyShape = (pts, hole, keepZ) => { const s = keepZ ? 1 : -1, sh = new THREE.Shape(); pts.forEach(([x, z], i) => i ? sh.lineTo(x, s * z) : sh.moveTo(x, s * z)); sh.closePath(); if (hole) { const h = new THREE.Path(); hole.forEach(([x, z], i) => i ? h.lineTo(x, s * z) : h.moveTo(x, s * z)); h.closePath(); sh.holes.push(h); } return sh; };
const extrudeUp = (sh, y0, h, bev, cs) => { const b = bev || 0, g = new THREE.ExtrudeGeometry(sh, { depth: Math.max(0.0005, h - 2 * b), bevelEnabled: b > 0, bevelThickness: b, bevelSize: b, bevelSegments: HI && b > 0.009 ? 2 : 1, curveSegments: cs || 6 }); g.rotateX(-Math.PI / 2); g.translate(0, y0 + b, 0); return g; };
// the badge: a little ghost with bat wings (in the xy plane, facing +z)
function ghostBadge() {
  const out = [], ex = (sh, d) => new THREE.ExtrudeGeometry(sh, { depth: d, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 1, curveSegments: HI ? 10 : 5 });
  const body = new THREE.Shape(); body.moveTo(-0.055, -0.05); body.lineTo(-0.055, 0.015); body.absarc(0, 0.015, 0.055, Math.PI, 0, true); body.lineTo(0.055, -0.05);
  for (let k = 0; k < 3; k++) { const x0 = 0.055 - k * 0.0367; body.quadraticCurveTo(x0 - 0.009, -0.072, x0 - 0.0183, -0.05); body.quadraticCurveTo(x0 - 0.0275, -0.03, x0 - 0.0367, -0.05); }
  for (const sx of [-1, 1]) { const e = new THREE.Path(); e.absellipse(sx * 0.02, 0.018, 0.01, 0.015, 0, 6.2832, true); body.holes.push(e); }
  out.push(ex(body, 0.012));
  for (const sx of [-1, 1]) { const w = new THREE.Shape(); w.moveTo(sx * 0.045, 0.02); w.quadraticCurveTo(sx * 0.1, 0.064, sx * 0.137, 0.036); w.lineTo(sx * 0.126, 0.0); w.quadraticCurveTo(sx * 0.11, 0.018, sx * 0.098, -0.005); w.quadraticCurveTo(sx * 0.082, 0.012, sx * 0.07, -0.012); w.quadraticCurveTo(sx * 0.058, 0.004, sx * 0.045, -0.015); w.closePath(); out.push(ex(w, 0.008).translate(0, 0, 0.002)); }
  return out;
}
// a bat silhouette for the lid's top end
function batShape(s) { const sh = new THREE.Shape(); sh.moveTo(0, 0.05 * s);
  sh.lineTo(0.014 * s, 0.075 * s); sh.lineTo(0.022 * s, 0.045 * s); sh.quadraticCurveTo(0.08 * s, 0.075 * s, 0.13 * s, 0.05 * s); sh.lineTo(0.12 * s, 0.015 * s); sh.quadraticCurveTo(0.1 * s, 0.03 * s, 0.088 * s, 0.005 * s); sh.quadraticCurveTo(0.07 * s, 0.022 * s, 0.055 * s, -0.005 * s); sh.quadraticCurveTo(0.035 * s, 0.01 * s, 0.018 * s, -0.012 * s); sh.lineTo(0, -0.03 * s);
  sh.lineTo(-0.018 * s, -0.012 * s); sh.quadraticCurveTo(-0.035 * s, 0.01 * s, -0.055 * s, -0.005 * s); sh.quadraticCurveTo(-0.07 * s, 0.022 * s, -0.088 * s, 0.005 * s); sh.quadraticCurveTo(-0.1 * s, 0.03 * s, -0.12 * s, 0.015 * s); sh.lineTo(-0.13 * s, 0.05 * s); sh.quadraticCurveTo(-0.08 * s, 0.075 * s, -0.022 * s, 0.045 * s); sh.lineTo(-0.014 * s, 0.075 * s); sh.closePath(); return sh; }
// the lid's velvet: diamond tufting with a button at every corner, and a bat-winged ghost in the middle that glows
const VELVET = (() => {
  const W = HI ? 512 : 256, H = HI ? 768 : 384, k = W / 512, mk = () => { const cv = document.createElement('canvas'); cv.width = W; cv.height = H; return [cv, cv.getContext('2d')]; };
  const [cv, g] = mk(), [gv, gg] = mk(), cell = 64 * k;
  g.fillStyle = '#5E0A1C'; g.fillRect(0, 0, W, H);
  for (let y = -cell; y < H + cell; y += cell / 2) for (let x = -cell; x < W + cell; x += cell) { const cx = x + ((Math.round(y / (cell / 2)) & 1) ? cell / 2 : 0), cy = y;
    const gr = g.createRadialGradient(cx - 6 * k, cy - 8 * k, 2 * k, cx, cy, cell * 0.62); gr.addColorStop(0, '#C02344'); gr.addColorStop(0.55, '#8E1430'); gr.addColorStop(1, '#4A0614');
    g.fillStyle = gr; g.beginPath(); g.moveTo(cx, cy - cell / 2); g.lineTo(cx + cell / 2, cy); g.lineTo(cx, cy + cell / 2); g.lineTo(cx - cell / 2, cy); g.closePath(); g.fill(); }
  g.strokeStyle = 'rgba(30,0,8,0.55)'; g.lineWidth = 2.2 * k;
  for (let x = -H; x < W + H; x += cell) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x + H, H); g.stroke(); g.beginPath(); g.moveTo(x, 0); g.lineTo(x - H, H); g.stroke(); }
  for (let y = 0; y <= H + cell; y += cell / 2) for (let x = 0; x <= W + cell; x += cell) { const cx = x + ((Math.round(y / (cell / 2)) & 1) ? cell / 2 : 0); g.fillStyle = '#2A0410'; g.beginPath(); g.arc(cx, y, 5 * k, 0, 6.2832); g.fill(); g.fillStyle = 'rgba(255,160,180,0.55)'; g.beginPath(); g.arc(cx - 1.5 * k, y - 1.5 * k, 1.8 * k, 0, 6.2832); g.fill(); }
  // the glowing ghost, a little above the middle
  const ghost = (c, fill, lw) => { const cx = W / 2, cy = H * 0.4, s = 1.5 * k; c.save(); c.translate(cx, cy); c.scale(s, s);
    c.beginPath(); c.moveTo(-34, 30); c.lineTo(-34, -4); c.arc(0, -4, 34, Math.PI, 0); c.lineTo(34, 30); for (let i = 0; i < 3; i++) { const x0 = 34 - i * 22.67; c.quadraticCurveTo(x0 - 5.7, 44, x0 - 11.3, 30); c.quadraticCurveTo(x0 - 17, 18, x0 - 22.67, 30); } c.closePath();
    for (const sx of [-1, 1]) { c.moveTo(sx * 30, -6); c.quadraticCurveTo(sx * 70, -40, sx * 96, -18); c.lineTo(sx * 88, 6); c.quadraticCurveTo(sx * 78, -6, sx * 70, 10); c.quadraticCurveTo(sx * 58, 0, sx * 50, 16); c.quadraticCurveTo(sx * 42, 6, sx * 32, 18); }
    if (fill) { c.fillStyle = fill; c.fill(); } c.lineWidth = lw; c.stroke();
    c.fillStyle = '#3A0012'; for (const sx of [-1, 1]) { c.beginPath(); c.ellipse(sx * 12, -4, 6, 9, 0, 0, 6.2832); c.fill(); } c.restore(); };
  g.shadowColor = '#FF6A9A'; g.shadowBlur = 22 * k; g.strokeStyle = '#FF8AB0'; ghost(g, 'rgba(255,90,140,0.55)', 4); g.shadowBlur = 0;
  gg.fillStyle = '#000'; gg.fillRect(0, 0, W, H); gg.shadowColor = '#FFFFFF'; gg.shadowBlur = 26 * k; gg.strokeStyle = '#FFFFFF'; ghost(gg, 'rgba(255,255,255,0.6)', 5);
  const t1 = new THREE.CanvasTexture(cv), t2 = new THREE.CanvasTexture(gv); t1.colorSpace = t2.colorSpace = THREE.SRGBColorSpace; t1.anisotropy = 4;
  return toon(0xFFFFFF, { map: t1, emissive: 0xFF4F86, emissiveMap: t2, emissiveIntensity: HI ? 1.9 : 1.2 }, { roughness: 0.82 });
})();
const COFFIN = (() => {
  const box = [], gilt = [], dais = [], lw = [], lg = [], lamp = [], glow = [], glows = [];
  const WD = hexC(0x55352A), WP = hexC(0x6B4433), GD = hexC(0xE0B050), IR = hexC(0x332C38), WAX = hexC(0xF4E6C8), ST = [0x5E5869, 0x544E5F, 0x67617A].map(hexC);
  // the dais: a round slab in the middle and a ring of nine round it, a little gap between each
  dais.push([extrudeUp(new THREE.Shape().absarc(0, 0, 0.355, 0, 6.2832, false), 0, CPY, 0.008, 24), ST[0]]);
  for (let k = 0; k < 9; k++) { const a0 = k / 9 * 6.2832 + 0.026, a1 = (k + 1) / 9 * 6.2832 - 0.026, sh = new THREE.Shape(); for (let i = 0; i <= 6; i++) { const a = a0 + (a1 - a0) * i / 6; i ? sh.lineTo(Math.cos(a) * 0.8, Math.sin(a) * 0.8) : sh.moveTo(Math.cos(a) * 0.8, Math.sin(a) * 0.8); } for (let i = 6; i >= 0; i--) { const a = a0 + (a1 - a0) * i / 6 + (i === 6 ? -0.02 : i === 0 ? 0.02 : 0); sh.lineTo(Math.cos(a) * 0.378, Math.sin(a) * 0.378); } sh.closePath();
    dais.push([extrudeUp(sh, 0, CPY - 0.004 + (k % 3) * 0.003, 0.008, 2), ST[k % 3]]); }
  // the box: thick walls, a gilt rim and foot band, gilt straps up every corner
  const IN = offsetPoly(NCOF, -0.062);
  box.push([extrudeUp(polyShape(NCOF, IN), CPY, NCH, 0.014), (x, y, z, o, nx, ny) => o.copy(WD).multiplyScalar(ny > 0.5 ? 0.85 : 1)]);
  box.push([new THREE.ShapeGeometry(polyShape(IN, null, true)).rotateX(Math.PI / 2).translate(0, CPY + 0.04, 0), hexC(0x3A0814)]);
  gilt.push([extrudeUp(polyShape(offsetPoly(NCOF, 0.028), offsetPoly(NCOF, -0.08)), CPY + NCH - 0.004, 0.03, 0.006), GD]);
  gilt.push([extrudeUp(polyShape(offsetPoly(NCOF, 0.032), offsetPoly(NCOF, -0.02)), CPY, 0.045, 0.006), GD]);
  offsetPoly(NCOF, 0.017).forEach(([x, z], i) => { const a = Math.atan2(x - NCOF[i][0], z - NCOF[i][1]), g = HI ? rbox(0.036, NCH - 0.07, 0.036, 0.008) : new THREE.BoxGeometry(0.036, NCH - 0.07, 0.036); g.rotateY(a); g.translate(x, CPY + NCH / 2, z); gilt.push([g, GD]); });
  // raised panels on every side, each in a gilt frame; the ghost badge on the two long sides
  for (let i = 0; i < 6; i++) { const p1 = NCOF[i], p2 = NCOF[(i + 1) % 6], ex = p2[0] - p1[0], ez = p2[1] - p1[1], L = Math.hypot(ex, ez), nx = -ez / L, nz = ex / L, mx = (p1[0] + p2[0]) / 2, mz = (p1[1] + p2[1]) / 2, ry = Math.atan2(nx, nz);
    const pw = L - 0.17, ph = NCH - 0.17, yc = CPY + NCH / 2 + 0.008, place = (g, out) => { g.rotateY(ry); g.translate(mx + nx * out, yc, mz + nz * out); return g; };
    box.push([place(HI ? rbox(pw, ph, 0.02, 0.008) : new THREE.BoxGeometry(pw, ph, 0.02), 0.024), WP]);
    for (const [w, h, ox, oy] of [[pw + 0.028, 0.014, 0, ph / 2 + 0.007], [pw + 0.028, 0.014, 0, -ph / 2 - 0.007], [0.014, ph, pw / 2 + 0.007, 0], [0.014, ph, -pw / 2 - 0.007, 0]]) gilt.push([place(new THREE.BoxGeometry(w, h, 0.016).translate(ox, oy, 0), 0.03), GD]);
    if (i === 1 || i === 4) for (const g of ghostBadge()) gilt.push([place(g.scale(1.15, 1.15, 1), 0.036), GD]); }
  // the lid, built lying shut with its hinge (the head end) at the origin: wood, a gilt edge on top, a gilt frame round the velvet underneath, a bat on its far end
  const hingeZ = 0.62 + 0.02 + 0.012, LO = offsetPoly(NCOF, 0.02), toHinge = g => g.translate(0, 0, -hingeZ);
  lw.push([toHinge(extrudeUp(polyShape(LO), 0, 0.055, 0.012)), WD]);
  lg.push([toHinge(extrudeUp(polyShape(LO, offsetPoly(NCOF, -0.035)), 0.055, 0.012, 0.004)), GD]);
  lg.push([toHinge(extrudeUp(polyShape(offsetPoly(NCOF, -0.03), offsetPoly(NCOF, -0.072)), -0.012, 0.012, 0.003)), GD]);
  { const sh = batShape(1.4), g = new THREE.ExtrudeGeometry(sh, { depth: 0.01, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 1, curveSegments: 6 }); g.rotateX(-Math.PI / 2); g.translate(0, 0.02, -0.62 - 0.02 - 0.05); lg.push([toHinge(g), GD]); }
  const vel = new THREE.ShapeGeometry(polyShape(offsetPoly(NCOF, -0.03), null, true), 4); uvXY(vel, (x, y) => [-x / 0.84 + 0.5, -y / 1.24 + 0.5]); vel.rotateX(Math.PI / 2); vel.translate(0, -0.004, -hingeZ);
  // lanterns at its foot: an iron frame round glowing glass, a gilt cap and a ring to carry it by
  const lantern = (cx, cz) => { const y = CPY, rb = (w, h, d, r) => HI ? rbox(w, h, d, r) : new THREE.BoxGeometry(w, h, d);
    lamp.push([rb(0.15, 0.03, 0.15, 0.008).translate(cx, y + 0.015, cz), IR]);
    for (const [sx, sz] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) lamp.push([new THREE.BoxGeometry(0.018, 0.17, 0.018).translate(cx + sx * 0.058, y + 0.115, cz + sz * 0.058), IR]);
    glow.push([new THREE.BoxGeometry(0.1, 0.15, 0.1).translate(cx, y + 0.11, cz), hexC(0xFFA640)]);
    lamp.push([rb(0.16, 0.025, 0.16, 0.008).translate(cx, y + 0.21, cz), GD]);
    lamp.push([new THREE.ConeGeometry(0.105, 0.075, 4, 1).rotateY(Math.PI / 4).translate(cx, y + 0.26, cz), IR]);
    lamp.push([new THREE.TorusGeometry(0.026, 0.0065, 6, 14).translate(cx, y + 0.315, cz), GD]);
    glows.push([cx, y + 0.11, cz, 0.62, 0xFFAE52]); };
  lantern(0.37, -0.58); lantern(-0.37, -0.58);
  // candles round it, a dip in each top and wax run down the sides, a wick and a flame
  const candle = (cx, cz, h, r) => { const y = CPY;
    lamp.push([new THREE.CylinderGeometry(r, r * 1.05, h, HI ? 14 : 8).translate(cx, y + h / 2, cz), (x, yy, z, o) => o.copy(WAX).multiplyScalar(0.82 + 0.18 * (yy - y) / h)]);
    lamp.push([new THREE.TorusGeometry(r * 0.76, r * 0.25, 5, HI ? 14 : 8).rotateX(Math.PI / 2).translate(cx, y + h, cz), WAX]);
    for (let k = 0; k < 2; k++) { const a = k * 2.4 + h * 9, dl = 0.03 + k * 0.025; lamp.push([new THREE.CapsuleGeometry(r * 0.26, dl, 3, 6).translate(cx + Math.cos(a) * r * 0.95, y + h - dl / 2 - 0.006, cz + Math.sin(a) * r * 0.95), WAX]); }
    lamp.push([new THREE.CylinderGeometry(0.0035, 0.0035, 0.025, 4).translate(cx, y + h + 0.012, cz), hexC(0x2A2220)]);
    glow.push([flameCoreG(0.4).translate(cx, y + h + 0.05, cz), hexC(0xFFE0A0)]);
    glows.push([cx, y + h + 0.06, cz, 0.32, 0xFFC27A]); };
  candle(0.53, 0.3, 0.22, 0.04); candle(-0.5, 0.36, 0.15, 0.036); candle(0.4, 0.62, 0.12, 0.032); candle(-0.34, 0.66, 0.19, 0.038);
  const hull = extrudeUp(polyShape(offsetPoly(NCOF, 0.055)), CPY - 0.004, NCH + 0.044, 0);
  const lidHull = toHinge(extrudeUp(polyShape(offsetPoly(NCOF, 0.05)), -0.028, 0.115, 0));
  // the paint reaches the walls on every side
  const surf = polySurf(offsetPoly(IN, -0.004), HI ? 6 : 3, HI ? 48 : 24);
  return { box: vcGeo(box), gilt: vcGeo(gilt), dais: vcGeo([...dais, ...lamp]), glow: vcGeo(glow), glows, lidW: vcGeo(lw), lidG: vcGeo(lg), vel, hull, lidHull, surf, hingeY: CPY + NCH + 0.026, hingeZ, lv0: CPY + 0.045, lvK: NCH - 0.09, yTop: CPY + NCH + 0.026 };
})();
// drips off the coffin's rim and down its walls (the walls are straight, so straight down), on the long sides
const cofRimDrips = seed => { const r = rng(seed), list = [], OUT = offsetPoly(NCOF, 0.036); for (let k = 0; k < 3; k++) { const i = [1, 4, 2][k], j = (i + 1) % 6, t = 0.25 + r() * 0.5, x = OUT[i][0] + (OUT[j][0] - OUT[i][0]) * t, z = OUT[i][1] + (OUT[j][1] - OUT[i][1]) * t, len = 0.07 + r() * 0.18;
  list.push(new THREE.CylinderGeometry(0.022, 0.026, len, 10).translate(x, -0.01 - len / 2, z), new THREE.SphereGeometry(0.03, 12, 10).scale(1, 1.3, 1).translate(x, -0.01 - len, z), new THREE.SphereGeometry(0.034, 12, 8).scale(1.3, 0.5, 1.3).translate(x * 0.96, 0.004, z * 0.97)); }
  return mergeGeos(list); };
function cofDeco(p, dt, bo) { if (bo > p.dB + 0.05) p.cV -= 2.4; p.dB = bo; const h = Math.min(dt, 0.05); p.cV += (-55 * p.cA - 4.5 * p.cV) * h; p.cA += p.cV * h; p.lid.rotation.x = LID_OPEN + p.cA * 0.16; }
function makeCoffin(x, y, z, seed) {
  const K = COFFIN, p = stationBase(x, y, z, seed, 'coffin'), { inner, tub } = p;
  const bw = new THREE.Mesh(K.box, cofVC); bw.castShadow = true; tub.add(bw); tub.add(new THREE.Mesh(K.gilt, stMetalM)); tub.add(new THREE.Mesh(K.hull, outlineMat));
  const da = new THREE.Mesh(K.dais, stPlainM); da.receiveShadow = true; inner.add(da); inner.add(new THREE.Mesh(K.glow, stGlowM)); inner.add(glowCluster(K.glows));
  const lid = new THREE.Group(); lid.position.set(0, K.hingeY, K.hingeZ); lid.rotation.x = LID_OPEN; inner.add(lid);
  const lw = new THREE.Mesh(K.lidW, cofVC); lw.castShadow = true; lid.add(lw); lid.add(new THREE.Mesh(K.lidG, stMetalM)); lid.add(new THREE.Mesh(K.vel, VELVET)); lid.add(new THREE.Mesh(K.lidHull, outlineMat));
  const liq = new THREE.Mesh(K.surf, p.lm); liq.position.y = 0.3; tub.add(liq);
  const drips = new THREE.Mesh(cofRimDrips(seed), p.tm); drips.position.y = K.yTop; tub.add(drips);
  const spill = new THREE.Mesh(spillAt(seed, 0.6, CPY + 0.004, 0.2), p.tm); spill.renderOrder = 2; inner.add(spill);
  Object.assign(p, { liq, drips, spill, lid, lv0: K.lv0, lvK: K.lvK, lift: 0.03, sinkD: 1.2, deco: cofDeco, deb: DEB.coffin });
  return p;
}

// ---- Blank Canvas: a white round tub with orange clamps on a dark base lit by strips, and a dispenser behind it pouring a sheet of paint over its lip ----
const TANK = (() => {
  const V2 = (x, y) => new THREE.Vector2(x, y), seg = HI ? 72 : 36, pl = [], led = [];
  const WH = hexC(0xF4F5F7), LG = hexC(0xC6CBD2), DG = hexC(0x454A54), OR = hexC(0xF2592A), ORL = hexC(0xFF8C50);
  pl.push([new THREE.LatheGeometry([[0.49, 0.001], [0.652, 0.001], [0.665, 0.012], [0.665, 0.058], [0.655, 0.072], [0.63, 0.08], [0.49, 0.08]].map(p => V2(p[0], p[1])), seg), DG]);
  const wallP = [[0.6, 0.078], [0.6, 0.112], [0.592, 0.118], [0.592, 0.126], [0.6, 0.132], [0.6, 0.41], [0.597, 0.432], [0.586, 0.448], [0.566, 0.457], [0.532, 0.457], [0.513, 0.45], [0.503, 0.438], [0.499, 0.42], [0.499, 0.1], [0.001, 0.1]];
  pl.push([new THREE.LatheGeometry(wallP.map(p => V2(p[0], p[1])), seg), (x, y, z, o) => { const r = Math.hypot(x, z); return o.copy(r < 0.505 ? (y < 0.105 ? hexC(0x5A1426) : LG) : (y > 0.111 && y < 0.133 && r < 0.598) ? DG : WH); }]);
  // four clamps over the rim: a block down the outside, a cap across the top, a white stripe down its face
  for (let k = 0; k < 4; k++) { const a = Math.PI / 4 + k * Math.PI / 2, ca = Math.cos(a), sa = Math.sin(a), ry = Math.atan2(ca, sa), P = (g, r, y) => { g.rotateY(ry); g.translate(ca * r, y, sa * r); return g; }, oc = (x, y, z, o, nx, ny) => o.copy(ny > 0.6 ? ORL : OR);
    pl.push([P(HI ? rbox(0.13, 0.31, 0.07, 0.02) : new THREE.BoxGeometry(0.13, 0.31, 0.07), 0.625, 0.27), oc]);
    pl.push([P(HI ? rbox(0.13, 0.042, 0.19, 0.015) : new THREE.BoxGeometry(0.13, 0.042, 0.19), 0.575, 0.47), oc]);
    pl.push([P(new THREE.BoxGeometry(0.034, 0.17, 0.012), 0.662, 0.27), WH]); }
  // light strips round the base (the back one would sit behind the dispenser)
  for (const a of [Math.PI / 2, 0, Math.PI]) led.push(gridGeo(HI ? 16 : 8, 1, (u, v, o) => { const t = a - 0.34 + 0.68 * u; o.set(Math.cos(t) * 0.668, 0.026 + 0.022 * v, Math.sin(t) * 0.668); }, true));
  // the dispenser: dark below, white above with a seam between, a hopper lid on top, a light on its face, and a chute out over the rim
  const DZ = -0.725, rb = (w, h, d, r) => HI ? rbox(w, h, d, r) : new THREE.BoxGeometry(w, h, d);
  pl.push([rb(0.46, 0.3, 0.22, 0.035).translate(0, 0.15, DZ), DG]);
  pl.push([rb(0.46, 0.33, 0.22, 0.045).translate(0, 0.455, DZ), WH]);
  pl.push([new THREE.BoxGeometry(0.47, 0.022, 0.226).translate(0, 0.302, DZ), LG]);
  pl.push([rb(0.34, 0.07, 0.15, 0.025).translate(0, 0.635, DZ - 0.01), WH]);
  for (const [g, x, y] of [[rb(0.31, 0.022, 0.3, 0.008), 0, 0.556], [rb(0.024, 0.075, 0.3, 0.008), 0.143, 0.59], [rb(0.024, 0.075, 0.3, 0.008), -0.143, 0.59]]) { g.rotateX(0.07); g.translate(x, y, -0.5); pl.push([g, (xx, yy, zz, o, nx, ny) => o.copy(ny > 0.6 ? WH : LG)]); }
  led.push(new THREE.BoxGeometry(0.2, 0.026, 0.012).translate(0, 0.42, DZ + 0.112));
  // the sheet: along the chute, over its lip and down into the tub
  const rc = new THREE.CatmullRomCurve3([[0, 0.592, -0.66], [0, 0.58, -0.5], [0, 0.569, -0.37], [0, 0.545, -0.338], [0, 0.47, -0.322], [0, 0.32, -0.315], [0, 0.11, -0.312]].map(q => new THREE.Vector3(q[0], q[1], q[2])), false, 'centripetal');
  const ramp = t => Math.min(1, Math.max(0, (t - 0.35) / 0.5));
  const stream = streamGeo(rc, HI ? 40 : 20, HI ? 16 : 10, t => [0.118 - 0.022 * ramp(t), 0.011 + 0.006 * ramp(t)], t => Math.min(1, Math.max(0, (t - 0.3) / 0.15)));
  const tubHull = mergeGeos([new THREE.CylinderGeometry(0.635, 0.635, 0.39, 32, 1, true).translate(0, 0.27, 0), new THREE.CylinderGeometry(0.69, 0.69, 0.09, 36).translate(0, 0.04, 0)]);
  const hull = new THREE.BoxGeometry(0.5, 0.71, 0.26).translate(0, 0.335, DZ);
  return { pl: vcGeo(pl), led: mergeGeos(led), stream, src: [0, -0.318], tubHull, hull, lv0: 0.105, lvK: 0.31, yTop: 0.457, surf: new THREE.RingGeometry(0, 0.495, HI ? 56 : 28, HI ? 6 : 3).rotateX(-Math.PI / 2) };
})();
function makeTank(x, y, z, seed) {
  const K = TANK, p = stationBase(x, y, z, seed, 'tank'), { inner, tub } = p;
  const pm = new THREE.Mesh(K.pl, stGlossM); pm.castShadow = true; pm.receiveShadow = true; inner.add(pm); inner.add(new THREE.Mesh(K.led, stLedM));
  tub.add(new THREE.Mesh(K.tubHull, outlineMat)); inner.add(new THREE.Mesh(K.hull, outlineMat));
  const liq = new THREE.Mesh(K.surf, p.lm); liq.position.y = 0.3; tub.add(liq);
  const drips = new THREE.Mesh(rimDrips(seed, () => 0.6, K.yTop, 2, 0.06, 0.17), p.tm); drips.position.y = K.yTop; tub.add(drips);
  const spill = new THREE.Mesh(spillAt(seed, 0.8, 0.004, 0.22), p.tm); spill.renderOrder = 2; inner.add(spill);
  Object.assign(p, { liq, drips, spill, lv0: K.lv0, lvK: K.lvK, lift: 0.03, sinkD: 0.85, deb: DEB.tank });
  addPour(p, K.stream, K.src, seed); return p;
}
// what flies when a station is burst: two kinds of plank (or chunk) and its most telling piece
const DEB = (() => {
  const chuteG = new THREE.BoxGeometry(0.31, 0.05, 0.3), chuteHullG = new THREE.BoxGeometry(0.35, 0.09, 0.34);
  const tikiA = toon(0xA36B44, { map: woodTex }), tikiB = toon(0xE0C878), cofA = toon(0x55352A, { map: woodTex }), cofB = toon(0xE0B050, null, { metalness: 0.85, roughness: 0.3 }), tankA = toon(0xF4F5F7, null, { roughness: 0.3 }), tankB = toon(0xF2592A, null, { roughness: 0.35 });
  return {
    tiki: { a: tikiA, b: tikiB, lid: () => { const g = new THREE.Group(); g.add(new THREE.Mesh(TIKI.canopy, stPlainM)); return g; } },
    coffin: { a: cofA, b: cofB, lid: () => { const g = new THREE.Group(), K = COFFIN; for (const [geo, m] of [[K.lidW, cofVC], [K.lidG, stMetalM], [K.vel, VELVET], [K.lidHull, outlineMat]]) { const o = new THREE.Mesh(geo, m); o.position.z = K.hingeZ * 0.5; g.add(o); } return g; } },
    tank: { a: tankA, b: tankB, lid: () => { const g = new THREE.Group(); g.add(new THREE.Mesh(chuteG, tankA)); g.add(new THREE.Mesh(chuteHullG, outlineMat)); return g; } },
  };
})();
// turn a station's tall back (spout, lid, dispenser) toward the nearest wall or drop, so it stands against it and opens onto the floor
function potYaw(x, y, z) {
  let sx = 0, sz = 0;
  for (let k = 0; k < 16; k++) { const a = k / 16 * 6.2832, dx = Math.sin(a), dz = Math.cos(a); for (const rad of [1.15, 1.6]) { const px = x + dx * rad, pz = z + dz * rad, s = surfaceUnder(px, pz, y + 0.3); if (blockedAt(px, pz, y) || s === -Infinity || s < y - 0.2) { const w = rad < 1.3 ? 1.5 : 1; sx += dx * w; sz += dz * w; } } }
  return sx * sx + sz * sz > 0.01 ? Math.atan2(sx, sz) + Math.PI : null;
}
// the pour runs while there's paint to give, thinning as it runs low: ripples and a little boil where it lands, and a drop thrown up now and then
function potPour(p, lv, dt) {
  const on = potUp(p) && p.ink > 0.02 ? Math.min(1, 0.45 + p.ink * 0.7) : 0; p.flow += (on - p.flow) * Math.min(1, dt * 5);
  const vis = p.flow > 0.05; p.stream.visible = vis; p.sm.userData.rad.value = p.flow; p.lm.userData.wave.uSrc.value.z = p.flow;
  p.foam.visible = vis; p.foam.position.y = lv + 0.004; const s = Math.max(0.01, p.flow) * (1 + 0.14 * Math.sin(clock * 19 + p.phase)); p.foam.scale.set(s, s * (0.8 + 0.3 * Math.sin(clock * 13 + p.phase)), s);
  if (vis && (p.popT = (p.popT || 0) - dt) < 0) { p.popT = 0.18 + Math.random() * 0.3; if (Math.abs(p.x - P.x) + Math.abs(p.z - P.z) < 16) { const c = Math.cos(p.g.rotation.y), sn = Math.sin(p.g.rotation.y), lx = p.src[0], lz = p.src[1], a = Math.random() * 6.283; spawnPart(p.x + lx * c + lz * sn, p.y + lv + 0.03, p.z - lx * sn + lz * c, Math.cos(a) * 0.5, 0.9 + Math.random() * 0.9, Math.sin(a) * 0.5, 0.35, potDrop(), 0.35 + Math.random() * 0.25); } }
}
// someone dives in: a crown of paint and drops flying; someone leaps out: a jet behind them and paint dripping off them for a moment (and from a coffin, little bat wings)
function potDive(p, D, lv) {
  p.crT = 0; p.slosh = Math.min(1.4, p.slosh + 0.4);
  if (Math.abs(p.x - P.x) + Math.abs(p.z - P.z) > 22) return;
  for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283, sp = 1.1 + Math.random() * 1.8; spawnPart(p.x + Math.cos(a) * 0.28, p.y + lv + 0.06, p.z + Math.sin(a) * 0.28, Math.cos(a) * sp, 2.4 + Math.random() * 2.6, Math.sin(a) * sp, 0.6, potDrop(), 0.5 + Math.random() * 0.45); }
}
function potLeap(p, D) { p.jtT = 0; p.dripD = D; p.dripT = 0.55; p.dripN = 0; if (p.kind === 'coffin' && D.st !== 'ko') D.batT = 1.15; }
function potFx(p, lv, dt) {
  const ck = (p.crT += dt) / 0.5; p.crown.visible = ck < 1;
  if (ck < 1) { const up = ck < 0.26 ? 1 - Math.pow(1 - ck / 0.26, 2) : 1 - Math.pow((ck - 0.26) / 0.74, 1.5), w = 0.72 + 0.6 * (1 - Math.pow(1 - ck, 3)); p.crown.position.y = lv - 0.03 - 0.1 * Math.max(0, ck - 0.45); p.crown.scale.set(w, Math.max(0.02, up), w); }
  const jk = (p.jtT += dt) / 0.42; p.jet.visible = jk < 1;
  if (jk < 1) { p.jet.position.y = lv - 0.015; p.jet.scale.set(1, Math.max(0.02, Math.sin(Math.min(1, jk * 1.25) * Math.PI)), 1); }
  if (p.dripT > 0) { p.dripT -= dt; p.dripN += dt; const D = p.dripD; if (D && D.st !== 'ko' && p.dripN > 0.045) { p.dripN = 0; spawnPart(D.x + (Math.random() - 0.5) * 0.22, D.y + 0.12, D.z + (Math.random() - 0.5) * 0.22, (Math.random() - 0.5) * 0.4, -0.4 - Math.random() * 0.6, (Math.random() - 0.5) * 0.4, 0.7, potDrop(), 0.4 + Math.random() * 0.35); } }
}
// little bat wings for a blob flying out of a coffin: a scalloped membrane with its finger bones, flapping hard, then gone
const BAT_WING_G = (() => { const sh = new THREE.Shape();
  sh.moveTo(0, 0.06); sh.quadraticCurveTo(0.2, 0.24, 0.5, 0.2); sh.lineTo(0.47, 0.07); sh.quadraticCurveTo(0.42, 0.13, 0.36, 0.03); sh.quadraticCurveTo(0.29, 0.1, 0.22, -0.02); sh.quadraticCurveTo(0.14, 0.06, 0.06, -0.06); sh.lineTo(0, -0.03); sh.closePath();
  const g = new THREE.ExtrudeGeometry(sh, { depth: 0.012, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.006, bevelSegments: 1, curveSegments: 6 }); g.translate(0, 0, -0.006);
  const A = hexC(0x2E1B44), B = hexC(0x7347A0), bone = hexC(0x1E1030), parts = [[g, (x, y, z, o) => o.copy(A).lerp(B, Math.min(1, Math.max(0, x / 0.5)) * 0.65)]];
  for (const [tx, ty] of [[0.47, 0.07], [0.36, 0.03], [0.22, -0.02], [0.5, 0.2]]) parts.push([tubeBetween(new THREE.Vector3(0.02, 0.02, 0.008), new THREE.Vector3(tx, ty, 0.008), 0.012, 0.006, 5), bone]);
  return vcGeo(parts); })();
function addBat(V) { const g = new THREE.Group(); g.visible = false; for (const sd of [-1, 1]) { const w = new THREE.Mesh(BAT_WING_G, stPlainM); w.scale.x = sd; g.add(w); } V.root.add(g); V.bat = g; }
