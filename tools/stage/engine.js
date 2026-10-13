// ---------- stages that dress themselves (the Sludge Sewer, the Fishing Raft): the theme's dress(K) is handed the stage builder's tools
// and gives back hooks the builder calls as it goes (each block, each round piece, each ramp, the eight spots round the edge, the scenery
// beyond). Their props are colored per vertex and merged into one draw per material; what moves (a flag, a swinging trap, falling slime)
// goes on STAGE_ANIM, ticked every frame ----------
const STAGE_ANIM = [];
function stageTick(dt) { for (let i = 0; i < STAGE_ANIM.length; i++) STAGE_ANIM[i].tick(dt, clock); steamTick(dt); coneTick(dt); }
const SG = {
  // detail: 1 on and round the arena; the stages lower it while they build scenery only seen from afar (k: 0.6 is about half the sides)
  k: 1,
  // how many sides a round part of radius r gets: as many as its size needs (a bolt or a rail six, a barrel about twenty), never more than n asks
  sides: (r, n) => Math.max(6, Math.min(SEG(n || 12), Math.round((r * 55 + 4) * SG.k))),
  // run f with the detail at k (and put it back after)
  lod: (k, f) => { const k0 = SG.k; SG.k = k; try { return f(); } finally { SG.k = k0; } },
  box: (w, h, d, x, y, z) => new THREE.BoxGeometry(w, h, d).translate(x, y, z),
  rbox: (w, h, d, r, x, y, z) => (HI && r > 0.012 ? rbox(w, h, d, r) : new THREE.BoxGeometry(w, h, d)).translate(x, y, z),
  // (round things get as many sides as their size needs: a bolt or a rail a handful, a drum or a spool its full count)
  cyl: (r0, r1, h, n, x, y, z, open) => new THREE.CylinderGeometry(r1, r0, h, SG.sides(Math.max(r0, r1), n), 1, !!open).translate(x, y, z),
  // colors baked onto a part where it's built, so they turn and move with it (handed to vc with the color null)
  paint: (g, c) => { const P = g.attributes.position, N = g.attributes.normal, n = P.count, a = new Float32Array(n * 3), tc = new THREE.Color();
    for (let i = 0; i < n; i++) { const cc = typeof c === 'function' ? c(P.getX(i), P.getY(i), P.getZ(i), tc, N.getX(i), N.getY(i), N.getZ(i)) : c; a[i * 3] = cc.r; a[i * 3 + 1] = cc.g; a[i * 3 + 2] = cc.b; }
    g.setAttribute('color', new THREE.BufferAttribute(a, 3)); return g; },
  // a band round something round (a hoop on a barrel, a lashing round a log): an open cylinder, a quarter of a torus's triangles
  band: (r, h, n) => new THREE.CylinderGeometry(r, r, h, SG.sides(r, n), 1, true),
  ball: (r, x, y, z, sx, sy, sz) => { const big = r * Math.max(sx || 1, sy || 1, sz || 1), n = Math.max(5, Math.round((big < 0.05 ? 6 : big < 0.1 ? 7 : big < 0.2 ? 9 : big < 0.4 ? 12 : SEG(14)) * Math.min(1, SG.k + 0.15)));
    return new THREE.SphereGeometry(r, n, Math.max(3, Math.round(n * 0.6))).scale(sx || 1, sy || 1, sz || 1).translate(x, y, z); },
  torus: (R, r, x, y, z, rx, ry, n) => { const g = new THREE.TorusGeometry(R, r, r < 0.03 ? (SG.k < 0.8 ? 3 : 4) : r < 0.08 ? 5 : 6, Math.max(8, Math.min(SEG(n || 24), Math.round((R * 36 + 8) * SG.k)))); if (rx) g.rotateX(rx); if (ry) g.rotateY(ry); return g.translate(x, y, z); },
  tube: (a, b, r, n) => tubeBetween(a, b, r, r, r < 0.035 ? (SG.k < 0.8 ? 3 : 4) : Math.max(5, Math.min(SEG(n || 8), Math.round((r * 55 + 4) * SG.k)))),
  cone: (r, h, x, y, z, n) => new THREE.ConeGeometry(r, h, SG.sides(r, n || 12)).translate(x, y, z),
  // a rope or a hose along points (smooth through them)
  curve: (pts, r, n, m) => new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'centripetal'), Math.max(4, Math.round((n || 16) * SG.k)), r, r < 0.03 ? (SG.k < 0.8 ? 3 : 4) : Math.max(4, Math.round((m || 6) * Math.min(1, SG.k + 0.2))), false),
  // a rope hanging between two points, sagging by s
  sag: (a, b, s, r, n) => { const pts = []; for (let i = 0; i <= 8; i++) { const t = i / 8; pts.push(new THREE.Vector3(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t - s * 4 * t * (1 - t), a.z + (b.z - a.z) * t)); } return SG.curve(pts, r, n || 10, 5); },
  rotY: (g, a, x, z) => { g.translate(-x, 0, -z); g.rotateY(a); g.translate(x, 0, z); return g; },
  V: (x, y, z) => new THREE.Vector3(x, y, z),
  shade: (c, k) => c.clone().multiplyScalar(k),
};
// vcGeo kept indexed: a vertex the triangles round it share is shaded once rather than once for each of them (on a round part that's a
// fifth of the vertex work), and the buffers are a third the size. A part without normals gets them as vcGeo gave them (flat, face by face)
function vcGeoIdx(parts) {
  let nv = 0, ni = 0; const list = [];
  for (const [g0, c] of parts) { let g = g0; if (!g.attributes.normal) { g = g.index ? g.toNonIndexed() : g; g.computeVertexNormals(); } const k = g.attributes.position.count; nv += k; ni += g.index ? g.index.count : k; list.push([g, c]); }
  const pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), uv = new Float32Array(nv * 2), col = new Float32Array(nv * 3), idx = nv > 65535 ? new Uint32Array(ni) : new Uint16Array(ni), tc = new THREE.Color(); let o = 0, oi = 0;
  for (const [g, c] of list) {
    const P = g.attributes.position, N = g.attributes.normal, k = P.count; pos.set(P.array.subarray(0, k * 3), o * 3); nor.set(N.array.subarray(0, k * 3), o * 3); if (g.attributes.uv) uv.set(g.attributes.uv.array.subarray(0, k * 2), o * 2);
    if (c === null && g.attributes.color) col.set(g.attributes.color.array.subarray(0, k * 3), o * 3);
    else for (let q = 0; q < k; q++) { const cc = typeof c === 'function' ? c(P.getX(q), P.getY(q), P.getZ(q), tc, N.getX(q), N.getY(q), N.getZ(q)) : c; col[(o + q) * 3] = cc.r; col[(o + q) * 3 + 1] = cc.g; col[(o + q) * 3 + 2] = cc.b; }
    if (g.index) { const I = g.index.array, n = g.index.count; for (let q = 0; q < n; q++) idx[oi + q] = I[q] + o; oi += n; } else { for (let q = 0; q < k; q++) idx[oi + q] = o + q; oi += k; }
    o += k;
  }
  const m = new THREE.BufferGeometry(); m.setAttribute('position', new THREE.BufferAttribute(pos, 3)); m.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); m.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); m.setAttribute('color', new THREE.BufferAttribute(col, 3)); m.setIndex(new THREE.BufferAttribute(idx, 1));
  return m;
}
// the props' colors: one shade or a function of the vertex (position, then normal), per material, merged at the end. The small parts (bolts,
// rails, rope, lamps: under 0.3 m across) go in a mesh of their own that casts no shadow and stays out of a polished floor's reflection
function vcBag() {
  const m = new Map();
  return { add(mat, g, c) { let l = m.get(mat); if (!l) m.set(mat, l = [[], []]); if (!g.boundingSphere) g.computeBoundingSphere(); l[g.boundingSphere.radius < 0.3 ? 1 : 0].push([g, c]); return g; },
    flush(group, shadowG, noCast) { for (const [mat, [big, small]] of m) for (const [list, sm] of [[big, false], [small, true]]) { if (!list.length) continue;
      const g = vcGeoIdx(list), me = new THREE.Mesh(g, mat); me.receiveShadow = true; if (!sm) me.layers.enable(3); group.add(me); if (!sm && !(noCast && noCast.has(mat)) && !mat.isMeshBasicMaterial) shadowG.push(g); } m.clear(); } };
}
// a canvas texture painted once: an atlas of little pictures (signs, an emblem), cell k of n x n
const atlasUV = (g, k, n) => { const uv = g.attributes.uv, cu = (k % n) / n, cv = 1 - (Math.floor(k / n) + 1) / n; for (let i = 0; i < uv.count; i++) uv.setXY(i, cu + uv.getX(i) / n, cv + uv.getY(i) / n); return g; };
// ---------- steam: soft puffs rising and spreading from vents, grates and the slime, all of them in one draw. Each puff is a quad turned to
// face the camera (its place in the instance matrix's last column, its size and turn in the first), its fade in aOp ----------
const STEAM_N = HI ? 96 : 56, STEAM_SRC = [], STEAM_P = [];
const stmG = new THREE.PlaneGeometry(1, 1), stmOp = new THREE.InstancedBufferAttribute(new Float32Array(STEAM_N), 1); stmOp.setUsage(THREE.DynamicDrawUsage); stmG.setAttribute('aOp', stmOp);
const stmMat = new THREE.MeshBasicMaterial({ map: (() => { const S = 128, cv = document.createElement('canvas'); cv.width = cv.height = S; const c = cv.getContext('2d'), R = rng(733);
    for (let k = 0; k < 10; k++) { const a = R() * 6.2832, d = R() * 20, x = S / 2 + Math.cos(a) * d, y = S / 2 + Math.sin(a) * d, r = 22 + R() * 22, g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, 'rgba(255,255,255,0.4)'); g.addColorStop(0.55, 'rgba(255,255,255,0.15)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, S, S); }
    return new THREE.CanvasTexture(cv); })(), color: 0xDCEFD4, transparent: true, depthWrite: false });
stmMat.onBeforeCompile = s => {
  s.vertexShader = s.vertexShader.replace('#include <common>', '#include <common>\nattribute float aOp; varying float vOp;').replace('#include <project_vertex>', 'vOp = aOp; vec4 mvPosition = modelViewMatrix * vec4(instanceMatrix[3].xyz, 1.0); float nk = smoothstep(0.9, 3.4, -mvPosition.z - length(instanceMatrix[0].xy) * 0.5); vOp *= nk; vec2 cs = instanceMatrix[0].xy * nk; mvPosition.xy += vec2(cs.x * transformed.x - cs.y * transformed.y, cs.y * transformed.x + cs.x * transformed.y); gl_Position = projectionMatrix * mvPosition;');
  s.fragmentShader = s.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vOp;').replace('#include <opaque_fragment>', '#include <opaque_fragment>\n  gl_FragColor.a *= vOp;');
};
const stmIM = new THREE.InstancedMesh(stmG, stmMat, STEAM_N); stmIM.frustumCulled = false; stmIM.renderOrder = 5; stmIM.visible = false; stmIM.instanceMatrix.setUsage(THREE.DynamicDrawUsage); stmIM.instanceMatrix.array.fill(0); scene.add(stmIM);
for (let i = 0; i < STEAM_N; i++) STEAM_P.push({ i, on: false, x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, t: 0, T: 1, s0: 1, s1: 1, a: 0, rot: 0, rv: 0 });
// a source: where (x, y, z), how wide it breathes out (r), the puffs' size, puffs a second, how fast they rise
function steamAdd(x, y, z, r, s, rate, up) { STEAM_SRC.push({ x, y, z, r: r || 0.2, s: s || 1, rate: rate || 1, up: up || 0.8, acc: Math.random() }); }
function steamReset() { STEAM_SRC.length = 0; for (const p of STEAM_P) p.on = false; stmIM.instanceMatrix.array.fill(0); stmOp.array.fill(0); stmIM.instanceMatrix.needsUpdate = true; stmIM.visible = false; }
function steamTick(dt) {
  if (!STEAM_SRC.length && !stmIM.visible) return;
  dt = Math.min(dt, 0.05); if (dt <= 0) return;
  for (const s of STEAM_SRC) { s.acc += s.rate * dt; while (s.acc >= 1) { s.acc -= 1; let p = null; for (let i = 0; i < STEAM_N; i++) if (!STEAM_P[i].on) { p = STEAM_P[i]; break; } if (!p) { s.acc = 0; break; }
    const a = Math.random() * 6.2832, d = Math.sqrt(Math.random()) * s.r; p.on = true; p.x = s.x + Math.cos(a) * d; p.y = s.y; p.z = s.z + Math.sin(a) * d; p.vx = (Math.random() - 0.5) * 0.25; p.vz = (Math.random() - 0.5) * 0.25; p.vy = s.up * (0.7 + Math.random() * 0.6);
    p.t = 0; p.T = 2.4 + Math.random() * 1.6; p.s0 = s.s * (0.35 + Math.random() * 0.2); p.s1 = s.s * (1.3 + Math.random() * 0.6); p.a = 0.42 + Math.random() * 0.2; p.rot = Math.random() * 6.2832; p.rv = (Math.random() - 0.5) * 0.5; } }
  const A = stmIM.instanceMatrix.array, op = stmOp.array; let any = false;
  for (const p of STEAM_P) { const o = p.i * 16; if (!p.on) { if (A[o + 15] !== 0) { A.fill(0, o, o + 16); op[p.i] = 0; } continue; }
    p.t += dt; const u = p.t / p.T; if (u >= 1) { p.on = false; A.fill(0, o, o + 16); op[p.i] = 0; continue; }
    p.vy *= 1 - dt * 0.35; p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt; p.rot += p.rv * dt;
    const sc = p.s0 + (p.s1 - p.s0) * Math.pow(u, 0.6); A.fill(0, o, o + 16); A[o] = sc * Math.cos(p.rot); A[o + 1] = sc * Math.sin(p.rot); A[o + 12] = p.x; A[o + 13] = p.y; A[o + 14] = p.z; A[o + 15] = 1;
    op[p.i] = p.a * Math.min(1, u / 0.15) * Math.pow(1 - u, 1.4); any = true; }
  stmIM.visible = any; if (any) { stmIM.instanceMatrix.needsUpdate = true; stmOp.needsUpdate = true; }
}
// ---------- props you can knock about: traffic cones (the sewer), barrels and crates (the raft). Bumped gently, one rocks on the edge of its
// base and settles back; hit properly it tips past its balance and goes over: a cone onto its side, rolling round its tip; a barrel onto its
// side, rolling straight off; a crate onto a face, sliding to a stop. A pound throws them about; one knocked over the edge sinks.
// Tipped by th toward dir, each pivots on the edge of its base (its weight low) until it lies down ----------
const KN_MAX = 32, CONES = [], conePV = new Map();
const KN = {   // base half-width rp, height h, the height of its weight c (and its spread k2), how it lies (lie: 'apex' rolls round its tip,
  // 'axis' rolls straight, 'flat' slides), how far its tip is from its base (L), its rolling radius rr, how hard a bump tips it (kick)
  cone: { rp: 0.285, h: 0.735, c: 0.165, k2: 0.027, tip: 0.0375, lie: 'apex', L: 0.69, rr: 0.135, kick: 2.4 },
  barrel: { rp: 0.34, h: 0.84, c: 0.38, k2: 0.088, lie: 'axis', rr: 0.34, kick: 1.9 },
  crate: { rp: 0.3, h: 0.6, c: 0.3, k2: 0.06, lie: 'flat', rr: 0.3, kick: 1.7 },
};
for (const k in KN) { const q = KN[k]; q.id = k; q.tb = Math.atan2(q.rp, q.c); q.tl = q.lie === 'apex' ? Math.PI - Math.atan2(q.h, q.rp - q.tip) : Math.PI / 2;
  q.kg = 9.8 * Math.hypot(q.rp, q.c) / (q.rp * q.rp + q.c * q.c + q.k2); q.im = null; q.n = 0; }
// its lowest point below the middle of its base, tipped by th
const knLow = (q, th) => { const a = Math.abs(Math.atan2(Math.sin(th), Math.cos(th))), s = Math.sin(a), co = Math.cos(a); return Math.min(0, -q.rp * s, q.h * co - (q.lie === 'apex' ? q.tip : q.rp) * s); };
// each kind's mesh and its ink outline (one draw each for all of that kind), made the first time a stage asks for one
function knMesh(q) {
  if (q.im) return q.im;
  const C = hexC; let body, hull;
  if (q.id === 'cone') { const OR = C(0xF2661E), WH = C(0xF4F1E8), BK = C(0x1E201E);
    body = vcGeoIdx([[SG.rbox(0.36, 0.04, 0.36, 0.016, 0, 0.02, 0), BK], [SG.cyl(0.15, 0.03, 0.44, 18, 0, 0.26, 0), (x, y) => (y > 0.17 && y < 0.24) || (y > 0.31 && y < 0.37) ? WH : OR], [SG.cyl(0.03, 0.02, 0.025, 12, 0, 0.49, 0), OR]]).scale(1.5, 1.5, 1.5);
    hull = mergeGeos([new THREE.BoxGeometry(0.4, 0.072, 0.4).translate(0, 0.02, 0), SG.cyl(0.172, 0.044, 0.5, 12, 0, 0.26, 0)]).scale(1.5, 1.5, 1.5); }
  else if (q.id === 'barrel') { const W = C(0xFFFFFF), HP = C(0x6A6E72), LD = C(0xE8E8E8), r = q.rp, h = q.h;
    // a steel drum: its body (tinted per barrel), two rolled hoops and the rims, a lid with a bung
    body = vcGeoIdx([[SG.cyl(r * 0.97, r * 0.97, h - 0.04, 22, 0, h / 2, 0), W], [SG.cyl(r * 0.94, r * 0.94, 0.02, 22, 0, h - 0.01, 0), LD], [SG.cyl(r * 0.94, r * 0.94, 0.02, 22, 0, 0.01, 0), LD],
      ...[0.02, h * 0.33, h * 0.67, h - 0.02].map(y => [SG.torus(r * 0.975, 0.018, 0, y, 0, Math.PI / 2, 0, 24), HP]), [SG.cyl(0.035, 0.035, 0.02, 10, r * 0.5, h + 0.005, 0), HP]]);
    hull = SG.cyl(r + 0.022, r + 0.022, h + 0.04, 16, 0, h / 2, 0); }
  else { const WD = C(0xC08A52), DK = C(0x7A5230), s = q.rp * 2, b = 0.05;
    // a fish crate: slatted sides between corner posts, a rim round the top and the foot
    const parts = [[SG.box(s - 0.02, s - 0.02, s - 0.02, 0, s / 2, 0), WD]];
    for (const [x, z] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(b, s, b, x * (s / 2 - b / 2 + 0.005), s / 2, z * (s / 2 - b / 2 + 0.005)), DK]);
    for (const y of [0.03, s - 0.03]) { parts.push([SG.box(s + 0.01, 0.05, b, 0, y, s / 2 - b / 2 + 0.006), DK], [SG.box(s + 0.01, 0.05, b, 0, y, -s / 2 + b / 2 - 0.006), DK], [SG.box(b, 0.05, s + 0.01, s / 2 - b / 2 + 0.006, y, 0), DK], [SG.box(b, 0.05, s + 0.01, -s / 2 + b / 2 - 0.006, y, 0), DK]); }
    for (const y of [s * 0.36, s * 0.64]) for (const [w, d, x, z] of [[s, 0.012, 0, s / 2], [s, 0.012, 0, -s / 2], [0.012, s, s / 2, 0], [0.012, s, -s / 2, 0]]) parts.push([SG.box(w, 0.016, d, x, y, z), DK]);
    body = vcGeoIdx(parts); hull = new THREE.BoxGeometry(s + 0.05, s + 0.05, s + 0.05).translate(0, s / 2, 0); }
  const im = new THREE.InstancedMesh(body, aoPatch(toon(0xFFFFFF, { vertexColors: true }, { roughness: q.id === 'barrel' ? 0.42 : 0.62, metalness: q.id === 'barrel' ? 0.25 : 0 })), KN_MAX); im.count = 0; im.frustumCulled = false; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  const hm = new THREE.InstancedMesh(hull, outlineMat, KN_MAX); hm.count = 0; hm.frustumCulled = false; hm.instanceMatrix = im.instanceMatrix;
  im.userData.hull = hm; scene.add(im); scene.add(hm); return q.im = im;
}
const coneQ = new THREE.Quaternion(), coneQ2 = new THREE.Quaternion(), coneAx = new THREE.Vector3(), coneMx = new THREE.Matrix4(), coneP3 = new THREE.Vector3(), coneS3 = new THREE.Vector3(1, 1, 1);
function coneDraw(c) {
  coneAx.set(Math.cos(c.dir), 0, -Math.sin(c.dir)); coneQ.setFromAxisAngle(coneAx, c.th); coneQ2.setFromAxisAngle(coneAx.set(0, 1, 0), c.spin); coneQ.multiply(coneQ2);
  coneS3.setScalar(c.live ? 1 : 0.0001); coneP3.set(c.x, c.y, c.z); coneMx.compose(coneP3, coneQ, coneS3); coneMx.toArray(c.k.im.instanceMatrix.array, c.i * 16); c.k.dirty = true;
}
// a prop of a kind at (x, y, z), its color (a barrel's paint) if given
function knAdd(kind, x, y, z, col) { const q = KN[kind]; if (!q || q.n >= KN_MAX) return; const im = knMesh(q);
  const c = { k: q, i: q.n++, x, y, z, vx: 0, vy: 0, vz: 0, dir: 0, th: 0, thV: 0, spin: Math.random() * 6.2832, spinV: 0, st: 0, air: false, sinkT: 0, live: true };
  CONES.push(c); im.count = im.userData.hull.count = q.n; if (col !== undefined || im.instanceColor) { im.setColorAt(c.i, new THREE.Color(col === undefined ? 0xFFFFFF : col)); im.instanceColor.needsUpdate = true; }
  coneDraw(c); im.instanceMatrix.needsUpdate = true; }
const coneAdd = (x, y, z) => knAdd('cone', x, y, z);
function coneReset() { CONES.length = 0; conePV.clear(); for (const k in KN) { const q = KN[k]; q.n = 0; if (q.im) q.im.count = q.im.userData.hull.count = 0; } }
// a pound (or a giant's, a missile's) throws everything near it up and away, tumbling
function coneBlast(x, y, z, R) {
  for (const c of CONES) { if (!c.live || c.st === 3) continue; const dx = c.x - x, dz = c.z - z, d = Math.hypot(dx, dz), RR = R + 2.2; if (d > RR || Math.abs(c.y - y) > 2.5) continue;
    const k = 1 - d / RR, nx = d > 0.01 ? dx / d : 1, nz = d > 0.01 ? dz / d : 0, sp = 3.5 + 7 * k;
    c.vx = nx * sp; c.vz = nz * sp; c.vy = 2.6 + 5 * k; c.air = true; c.st = 1; if (Math.abs(c.th) < 0.05) c.dir = Math.atan2(nx, nz); c.thV += 7 + 9 * k; c.spinV = (Math.random() - 0.5) * 14; }
}
let coneSndT = 0, coneDrop = null;
// a move that runs into a block or the high side of a step stops and bounces back
const knBlocked = (x, z, yb) => solidThrough(x, z, yb + 0.15) || surfaceUnder(x, z, yb + 0.9) > yb + 0.3;
const knMove = (c, tx, tz) => { const yb = c.y + knLow(c.k, c.th); if (!knBlocked(tx, tz, yb)) { c.x = tx; c.z = tz; } else if (!knBlocked(tx, c.z, yb)) { c.x = tx; c.vz = -c.vz * 0.4; } else if (!knBlocked(c.x, tz, yb)) { c.z = tz; c.vx = -c.vx * 0.4; } else { c.vx = -c.vx * 0.4; c.vz = -c.vz * 0.4; } };
const knSnd = c => { if (coneSndT <= 0 && Math.hypot(c.x - P.x, c.z - P.z) < 14) { coneSndT = 0.12; try { AU.at(c.x, c.z); AU.ball(); } catch (e) {} } };
function coneSplash(x, z) {
  const m = TH && TH.slime ? (coneDrop = coneDrop || colMat(0x9CFF4A)) : (waterDrop = waterDrop || colMat(0xEAF8FF));
  for (let i = 0; i < 10; i++) { const a = Math.random() * 6.283, sp = 0.8 + Math.random() * 1.6; spawnPart(x, WATER_Y + 0.05, z, Math.cos(a) * sp, 2.2 + Math.random() * 2.2, Math.sin(a) * sp, 0.45 + Math.random() * 0.3, m, 0.35 + Math.random() * 0.3); }
  const rp = ripples.find(q => q.t >= 1); if (rp) { rp.t = 0; rp.big = 2.4; rp.dur = 0.8; rp.x = x; rp.y = WATER_Y + 0.04; rp.z = z; }
}
function coneTick(dt) {
  if (!CONES.length) return; dt = Math.min(dt, 0.05); if (dt <= 0) return;
  const play = state === 'play' || state === 'dead'; coneSndT -= dt;
  // the blobs' velocities, from where they were a frame ago (a jump across the map, a respawn, reads as standing still)
  if (play) for (const D of ACTIVE) { const pv = conePV.get(D); if (!pv) { conePV.set(D, { x: D.x, z: D.z, vx: 0, vz: 0 }); continue; } let vx = (D.x - pv.x) / dt, vz = (D.z - pv.z) / dt; if (vx * vx + vz * vz > 1600) vx = vz = 0; pv.x = D.x; pv.z = D.z; pv.vx = vx; pv.vz = vz; }
  const move = knMove, snd = knSnd;
  for (let i = 0; i < CONES.length; i++) { const c = CONES[i], q = c.k; if (!c.live) continue;
    if (play && c.st !== 3) for (const D of ACTIVE) { if (D.st !== 'play') continue; const pv = conePV.get(D); if (!pv) continue;
      const big = D.giantT > 0, rB = PR * (big ? GIANT_K : 1), lie = Math.abs(c.th) > 0.8, off = lie ? q.h * 0.4 * Math.sign(c.th) : 0, mx = c.x + Math.sin(c.dir) * off, mz = c.z + Math.cos(c.dir) * off;
      const dx = mx - D.x, dz = mz - D.z, dd = Math.hypot(dx, dz), reach = rB + (lie ? q.rp * 0.6 : q.rp * 0.9);
      if (dd > reach || D.y > c.y + q.h + 0.05 || D.y < c.y - (big ? 1.2 : 0.5)) continue;
      const nx = dd > 1e-3 ? dx / dd : Math.sin(D.yaw), nz = dd > 1e-3 ? dz / dd : Math.cos(D.yaw), vn = (pv.vx - c.vx) * nx + (pv.vz - c.vz) * nz;
      c.x += nx * (reach - dd); c.z += nz * (reach - dd); if (c.st !== 1) { c.st = 1; c.air = false; }
      if (vn <= 0.15) continue;
      c.vx += nx * vn * 1.1 + pv.vx * 0.15; c.vz += nz * vn * 1.1 + pv.vz * 0.15;
      if (vn > 6.5 || (big && vn > 2)) { c.air = true; c.vy = Math.min(6, 1.6 + vn * 0.32); if (Math.abs(c.th) < 0.05) c.dir = Math.atan2(nx, nz); c.thV += (5 + vn) * (c.thV < 0 ? -1 : 1); c.spinV = (Math.random() - 0.5) * 10; }
      else if (!lie) { if (Math.abs(c.th) < 0.05) { c.dir = Math.atan2(nx, nz); c.thV = vn * q.kick; } else c.thV += vn * q.kick * 0.66 * Math.sign(Math.cos(Math.atan2(nx, nz) - c.dir)); }
      if (vn > 1.2) { snd(c); if (D === P) buzz(5); }
    }
    if (c.st === 0 || c.st === 2) continue; // at rest, standing or lying down
    if (c.st === 3) { c.sinkT += dt; c.y -= dt * 0.3; c.th += dt * 0.4; if (c.sinkT > 2.2) c.live = false; coneDraw(c); continue; }
    if (!c.air) { const g = surfaceUnder(c.x, c.z, c.y + knLow(q, c.th) + 0.3); if (g === -Infinity || g < c.y + knLow(q, c.th) - 0.06) c.air = true; } // pushed off an edge
    if (c.air) {
      c.vy -= 14 * dt; c.th += c.thV * dt; c.thV *= 1 - dt * 0.4; c.spin += c.spinV * dt; c.spinV *= 1 - dt * 0.6;
      move(c, c.x + c.vx * dt, c.z + c.vz * dt); c.y += c.vy * dt;
      const lo = knLow(q, c.th), g = surfaceUnder(c.x, c.z, c.y + lo + 0.3);
      if (g === -Infinity) { if (c.y < WATER_Y + 0.1) { c.st = 3; c.sinkT = 0; coneSplash(c.x, c.z); } }
      else if (c.y + lo <= g && c.vy <= 0) { c.y = g - lo;
        if (c.vy < -2.4) { c.vy = -c.vy * 0.3; c.vx *= 0.7; c.vz *= 0.7; c.thV *= 0.6; snd(c); }
        else { c.vy = 0; c.air = false; c.th = Math.atan2(Math.sin(c.th), Math.cos(c.th)); } }
    } else {
      // on the ground: pivoting on the edge of its base, falling back onto it short of its balance, down onto its side past it
      const a = Math.abs(c.th), sg = c.th < 0 ? -1 : 1, th0 = c.th;
      c.thV += (a < q.tl - 0.001 ? sg * q.kg * Math.sin(a - q.tb) : -sg * 22) * dt; c.thV *= 1 - dt * 0.8; c.th += c.thV * dt;
      if (th0 * c.th < 0) c.thV *= 0.5; // rocking back over onto the base's other edge, it loses half its swing
      if (Math.abs(c.th) >= q.tl && Math.abs(th0) < q.tl) { c.th = q.tl * sg; const hard = Math.abs(c.thV) > 2.5; c.thV = hard ? -c.thV * 0.22 : 0; if (hard) snd(c); }
      const lying = Math.abs(c.th) >= q.tl - 0.03 && Math.abs(c.thV) < 0.6;
      if (lying) {
        if (c.th < 0) { c.th = -c.th; c.dir += Math.PI; } c.th = q.tl; c.thV = 0;
        const fx = Math.sin(c.dir), fz = Math.cos(c.dir); let va = c.vx * fx + c.vz * fz, vp = c.vx * fz - c.vz * fx;
        if (q.lie === 'apex') { // a cone rolls round its tip: across itself freely, dragging along itself
          va *= Math.exp(-dt * 5); vp *= Math.exp(-dt * 1.3); const ax = c.x + fx * q.L, az = c.z + fz * q.L; c.dir -= vp * dt / q.L; c.spin -= vp * dt / q.rr;
          const gx = Math.sin(c.dir), gz = Math.cos(c.dir); c.vx = gz * vp + gx * va; c.vz = -gx * vp + gz * va; move(c, ax - gx * q.L + gx * va * dt, az - gz * q.L + gz * va * dt); }
        else if (q.lie === 'axis') { // a barrel rolls straight on across itself, and drags along itself
          va *= Math.exp(-dt * 5); vp *= Math.exp(-dt * 0.7); c.spin -= vp * dt / q.rr; c.vx = fz * vp + fx * va; c.vz = -fx * vp + fz * va; move(c, c.x + c.vx * dt, c.z + c.vz * dt); }
        else { c.vx *= Math.exp(-dt * 4.5); c.vz *= Math.exp(-dt * 4.5); move(c, c.x + c.vx * dt, c.z + c.vz * dt); } // a crate slides to a stop
        if (c.vx * c.vx + c.vz * c.vz < 0.002) { c.vx = c.vz = 0; c.st = 2; }
      } else { c.vx *= Math.exp(-dt * 6); c.vz *= Math.exp(-dt * 6); move(c, c.x + c.vx * dt, c.z + c.vz * dt);
        if (Math.abs(c.th) < 0.015 && Math.abs(c.thV) < 0.35 && c.vx * c.vx + c.vz * c.vz < 0.003) { c.th = 0; c.thV = 0; c.vx = c.vz = 0; c.st = 0; } }
      const g = surfaceUnder(c.x, c.z, c.y + knLow(q, c.th) + 0.3); if (g > -Infinity) c.y = g - knLow(q, c.th);
    }
    coneDraw(c);
  }
  for (const k in KN) { const q = KN[k]; if (q.dirty && q.im) { q.im.instanceMatrix.needsUpdate = true; q.dirty = false; } }
}
