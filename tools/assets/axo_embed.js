// ---------- the axolotl (Roll Model's character): its runtime, made from the axolotl pipeline's axo.js by tools/mk_axo_embed.py ----------
const AXO = (() => {
// Roll Model axolotl runtime v7, single module: the core (mesh loader, dual quaternion skinning, the shared-skeleton Puppet), the
// procedural Animator and the Look (the layered skin, the game's slime face, the paint coat, the jelly layer).
// (core) Roll Model axolotl runtime: mesh loader (.bin/.json/.webp), shared-skeleton Puppet with joint limits, procedural Animator.
// A pose = per-bone local rotation expressed in the bone's canonical frame (Y along the bone, Z = flexion / ventral side, X = Y x Z = hinge)
// plus a root position. Each mesh stores its own canonical rest frame per bone, so one pose can drive either mesh.

const DEG = Math.PI / 180;
const _e = new THREE.Euler(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _m = new THREE.Matrix4();
const _m3a = new THREE.Matrix3(), _m3b = new THREE.Matrix3();
function addOuter(M, a, b) { const e = M.elements; e[0] += a.x * b.x; e[3] += a.x * b.y; e[6] += a.x * b.z; e[1] += a.y * b.x; e[4] += a.y * b.y; e[7] += a.y * b.z; e[2] += a.z * b.x; e[5] += a.z * b.y; e[8] += a.z * b.z; }
function addDiag(M, l) { const e = M.elements; e[0] += l; e[4] += l; e[8] += l; }
const _kq = new THREE.Quaternion(), _kq2 = new THREE.Quaternion(), _k1 = new THREE.Vector3(), _k2 = new THREE.Vector3(), _k3 = new THREE.Vector3(), _k4 = new THREE.Vector3(), _k5 = new THREE.Vector3(), _k6 = new THREE.Vector3(), _k7 = new THREE.Vector3(), _k8 = new THREE.Vector3();

async function loadMesh(base, tex, matOpts = {}) {
  const meta = await (await fetch(base + '.json')).json(), buf = await (await fetch(base + '.bin')).arrayBuffer();
  const n = meta.n, g = new THREE.BufferGeometry();
  if (meta.fmt === 'axo7') {
    // v7: positions f32; normals i8 (xyz + pad); skin u8; indices u16; cpos i16 (canonical place + arc coordinate); jelly / fill / mat u8 (see extras7.py)
    const o = meta.off7;
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o.position, n * 3), 3));
    g.setAttribute('normal', new THREE.InterleavedBufferAttribute(new THREE.InterleavedBuffer(new Int8Array(buf, o.normal, n * 4), 4), 3, 0, true));
    g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o.skinIndex, n * 4), 4));
    g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o.skinWeight, n * 4), 4, true));
    g.setIndex(new THREE.BufferAttribute(new Uint16Array(buf, o.index, meta.ni), 1));
    g.setAttribute('cpos', new THREE.BufferAttribute(new Int16Array(buf, o.cpos, n * 4), 4, true));
    for (const k of ['jelly', 'fill', 'mat']) g.setAttribute(k, new THREE.BufferAttribute(new Uint8Array(buf, o[k], n * 4), 4, true));
    // v8: a UV atlas (u16) and the body's baked base-colour texture (WebP bytes) riding in the same buffer (texbake.py); one texture per body, shared
    if (o.uv !== undefined) g.setAttribute('uv', new THREE.BufferAttribute(new Uint16Array(buf, o.uv, n * 2), 2, true));
    if (o.tex !== undefined && meta.texLen) g.userData.tex = texFromBytes(new Uint8Array(buf, o.tex, meta.texLen), meta.texMime);
  } else {
    const o = meta.off;
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o[0], n * 3), 3));
    g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o[1], n * 3), 3));
    g.setAttribute('uv', meta.uv16 ? new THREE.BufferAttribute(new Uint16Array(buf, o[2], n * 2), 2, true) : new THREE.BufferAttribute(new Float32Array(buf, o[2], n * 2), 2));
    g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o[3], n * 4), 4));
    g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o[4], n * 4), 4, true));
    g.setIndex(new THREE.BufferAttribute(meta.i32 ? new Uint32Array(buf, o[5], meta.ni) : new Uint16Array(buf, o[5], meta.ni), 1));
    g.setAttribute('jelly', o.length > 7 ? new THREE.BufferAttribute(new Uint8Array(buf, o[6], n * 4), 4, true) : new THREE.BufferAttribute(new Uint8Array(n * 4), 4, true));
    g.setAttribute('fill', o.length > 7 ? new THREE.BufferAttribute(new Uint8Array(buf, o[7], n * 2), 2, true) : new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true));
    g.setAttribute('xtra', o.length > 8 ? new THREE.BufferAttribute(new Uint8Array(buf, o[8], n * 2), 2, true) : new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true));
  }
  if (matOpts && matOpts.name) meta.name = matOpts.name; else if (!meta.name) meta.name = /crawl/.test(base) ? 'crawl' : /stand/.test(base) ? 'stand' : base;
  const bones = [], byName = {}, F = [], rest = [], end = [];
  for (const b of meta.bones) { const bn = new THREE.Bone(); bn.name = b.name; bones.push(bn); byName[b.name] = bn; F.push(new THREE.Quaternion(...b.q)); rest.push(new THREE.Vector3(...b.pos)); end.push(new THREE.Vector3(...b.end)); }
  const pidx = {}; meta.bones.forEach((b, i) => pidx[b.name] = i);
  for (let i = 0; i < bones.length; i++) { const b = meta.bones[i], bn = bones[i]; if (b.parent) { byName[b.parent].add(bn); bn.position.copy(rest[i]).sub(rest[pidx[b.parent]]); } else bn.position.copy(rest[i]); }
  // the head centre in rest space (for the face projection) = the head joint + the exported offset
  const hb = meta.bones.find(b => b.name === 'head'); meta.headAbs = meta.headc ? [hb.pos[0] + meta.headc[0], hb.pos[1] + meta.headc[1], hb.pos[2] + meta.headc[2]] : hb.pos; meta.headr = meta.headr || 0.38;
  // the face frame: the vertical extent of the front of the head (dome top to chin, gills excluded), so face heights mean the same on a flat head and a round one
  if (meta.fmt !== 'axo7') { const pa = g.getAttribute('position'), ja = g.getAttribute('jelly'); let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < n; i++) { if (ja.getW(i) > 0.9 && pa.getZ(i) > meta.headAbs[2] + 0.15 * meta.headr) { const y = pa.getY(i); if (y < lo) lo = y; if (y > hi) hi = y; } }
    if (hi > lo) { meta.headMid = (lo + hi) / 2; meta.headH = (hi - lo) / 2; } else { meta.headMid = meta.headAbs[1]; meta.headH = meta.headr; } }
  // dual quaternion skinning: per bone the rigid bind -> pose transform as a unit dual quaternion (2 texels), written by Puppet.apply
  const nb = bones.length, dq = new Float32Array(nb * 8); for (let i = 0; i < nb; i++) dq[i * 8 + 3] = 1;
  const dqTex = new THREE.DataTexture(dq, nb * 2, 1, THREE.RGBAFormat, THREE.FloatType); dqTex.minFilter = dqTex.magFilter = THREE.NearestFilter; dqTex.generateMipmaps = false; dqTex.needsUpdate = true; meta.dqTex = dqTex;
  tex = tex || g.userData.tex || null;
  const mat = matOpts && matOpts.look ? axoMaterial(tex, matOpts.look, meta) : dqsMaterial(new THREE.MeshStandardMaterial(Object.assign({ map: tex, roughness: 0.6, metalness: 0 }, matOpts || {})), meta);
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(bones[0]); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false; mesh.castShadow = true;
  mesh.customDepthMaterial = dqsMaterial(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), meta);
  return { mesh, bones, byName, meta, F, rest, end, dq, dqTex, names: meta.bones.map(b => b.name), parent: meta.bones.map(b => b.parent ? pidx[b.parent] : -1) };
}
function meshFrom(pre, tex, matOpts = {}) {
  // (pre: { meta, buf } from the pack; the geometry is made the first time and shared after that)
  const base = pre.name || '', meta = JSON.parse(JSON.stringify(pre.meta)), buf = pre.buf, n = meta.n;
  let g = pre.geo; if (!g) { g = new THREE.BufferGeometry();
  if (meta.fmt === 'axo7') {
    // v7: positions f32; normals i8 (xyz + pad); skin u8; indices u16; cpos i16 (canonical place + arc coordinate); jelly / fill / mat u8 (see extras7.py)
    const o = meta.off7;
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o.position, n * 3), 3));
    g.setAttribute('normal', new THREE.InterleavedBufferAttribute(new THREE.InterleavedBuffer(new Int8Array(buf, o.normal, n * 4), 4), 3, 0, true));
    g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o.skinIndex, n * 4), 4));
    g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o.skinWeight, n * 4), 4, true));
    g.setIndex(new THREE.BufferAttribute(new Uint16Array(buf, o.index, meta.ni), 1));
    g.setAttribute('cpos', new THREE.BufferAttribute(new Int16Array(buf, o.cpos, n * 4), 4, true));
    for (const k of ['jelly', 'fill', 'mat']) g.setAttribute(k, new THREE.BufferAttribute(new Uint8Array(buf, o[k], n * 4), 4, true));
    // v8: a UV atlas (u16) and the body's baked base-colour texture (WebP bytes) riding in the same buffer (texbake.py); one texture per body, shared
    if (o.uv !== undefined) g.setAttribute('uv', new THREE.BufferAttribute(new Uint16Array(buf, o.uv, n * 2), 2, true));
    if (o.tex !== undefined && meta.texLen) g.userData.tex = texFromBytes(new Uint8Array(buf, o.tex, meta.texLen), meta.texMime);
  } else {
    const o = meta.off;
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o[0], n * 3), 3));
    g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o[1], n * 3), 3));
    g.setAttribute('uv', meta.uv16 ? new THREE.BufferAttribute(new Uint16Array(buf, o[2], n * 2), 2, true) : new THREE.BufferAttribute(new Float32Array(buf, o[2], n * 2), 2));
    g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o[3], n * 4), 4));
    g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o[4], n * 4), 4, true));
    g.setIndex(new THREE.BufferAttribute(meta.i32 ? new Uint32Array(buf, o[5], meta.ni) : new Uint16Array(buf, o[5], meta.ni), 1));
    g.setAttribute('jelly', o.length > 7 ? new THREE.BufferAttribute(new Uint8Array(buf, o[6], n * 4), 4, true) : new THREE.BufferAttribute(new Uint8Array(n * 4), 4, true));
    g.setAttribute('fill', o.length > 7 ? new THREE.BufferAttribute(new Uint8Array(buf, o[7], n * 2), 2, true) : new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true));
    g.setAttribute('xtra', o.length > 8 ? new THREE.BufferAttribute(new Uint8Array(buf, o[8], n * 2), 2, true) : new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true));
  }
  pre.geo = g; }
  if (matOpts && matOpts.name) meta.name = matOpts.name; else if (!meta.name) meta.name = /crawl/.test(base) ? 'crawl' : /stand/.test(base) ? 'stand' : base;
  const bones = [], byName = {}, F = [], rest = [], end = [];
  for (const b of meta.bones) { const bn = new THREE.Bone(); bn.name = b.name; bones.push(bn); byName[b.name] = bn; F.push(new THREE.Quaternion(...b.q)); rest.push(new THREE.Vector3(...b.pos)); end.push(new THREE.Vector3(...b.end)); }
  const pidx = {}; meta.bones.forEach((b, i) => pidx[b.name] = i);
  for (let i = 0; i < bones.length; i++) { const b = meta.bones[i], bn = bones[i]; if (b.parent) { byName[b.parent].add(bn); bn.position.copy(rest[i]).sub(rest[pidx[b.parent]]); } else bn.position.copy(rest[i]); }
  // the head centre in rest space (for the face projection) = the head joint + the exported offset
  const hb = meta.bones.find(b => b.name === 'head'); meta.headAbs = meta.headc ? [hb.pos[0] + meta.headc[0], hb.pos[1] + meta.headc[1], hb.pos[2] + meta.headc[2]] : hb.pos; meta.headr = meta.headr || 0.38;
  // the face frame: the vertical extent of the front of the head (dome top to chin, gills excluded), so face heights mean the same on a flat head and a round one
  if (meta.fmt !== 'axo7') { const pa = g.getAttribute('position'), ja = g.getAttribute('jelly'); let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < n; i++) { if (ja.getW(i) > 0.9 && pa.getZ(i) > meta.headAbs[2] + 0.15 * meta.headr) { const y = pa.getY(i); if (y < lo) lo = y; if (y > hi) hi = y; } }
    if (hi > lo) { meta.headMid = (lo + hi) / 2; meta.headH = (hi - lo) / 2; } else { meta.headMid = meta.headAbs[1]; meta.headH = meta.headr; } }
  // dual quaternion skinning: per bone the rigid bind -> pose transform as a unit dual quaternion (2 texels), written by Puppet.apply
  const nb = bones.length, dq = new Float32Array(nb * 8); for (let i = 0; i < nb; i++) dq[i * 8 + 3] = 1;
  const dqTex = new THREE.DataTexture(dq, nb * 2, 1, THREE.RGBAFormat, THREE.FloatType); dqTex.minFilter = dqTex.magFilter = THREE.NearestFilter; dqTex.generateMipmaps = false; dqTex.needsUpdate = true; meta.dqTex = dqTex;
  tex = tex || g.userData.tex || null;
  const mat = matOpts && matOpts.look ? axoMaterial(tex, matOpts.look, meta) : dqsMaterial(new THREE.MeshStandardMaterial(Object.assign({ map: tex, roughness: 0.6, metalness: 0 }, matOpts || {})), meta);
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(bones[0]); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false; mesh.castShadow = true;
  mesh.customDepthMaterial = dqsMaterial(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), meta);
  return { mesh, bones, byName, meta, F, rest, end, dq, dqTex, names: meta.bones.map(b => b.name), parent: meta.bones.map(b => b.parent ? pidx[b.parent] : -1) };
}

// the body's texture from the encoded bytes in the pack: a tiny skin-coloured stand-in at once, the decoded image when it lands (no fetch,
// so the game's single file loads it like the rest of the pack); glTF-style UVs (v down from the top row), so no flip
function texFromBytes(bytes, mime) {
  const t = new THREE.Texture(); t.colorSpace = THREE.SRGBColorSpace; t.flipY = false; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter; t.anisotropy = 4;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; t.premultiplyAlpha = false;
  if (typeof document !== 'undefined') { const c = document.createElement('canvas'); c.width = c.height = 2; const x = c.getContext('2d'); x.fillStyle = '#f0a4ac'; x.fillRect(0, 0, 2, 2); t.image = c; t.needsUpdate = true; }
  // (the stand-in's GL storage is immutable at its size: the texture is dropped and made again at the image's)
  const blob = new Blob([bytes], { type: mime || 'image/webp' }), done = img => { t.dispose(); t.image = img; t.needsUpdate = true; t.userData.ready = true; };
  const viaImage = () => { const u = URL.createObjectURL(blob), im = new Image(); im.onload = () => { done(im); URL.revokeObjectURL(u); }; im.onerror = () => URL.revokeObjectURL(u); im.src = u; };
  if (typeof createImageBitmap === 'function') createImageBitmap(blob, { imageOrientation: 'none', premultiplyAlpha: 'none', colorSpaceConversion: 'none' }).then(done, viaImage); else viaImage();
  return t;
}

// ---- dual quaternion skinning (no candy-wrapper collapse at twisting / bending joints) ----
const DQS_PARS = `
#ifdef USE_SKINNING
uniform highp sampler2D uDQ;
vec3 dqRot(vec4 q, vec3 v) { return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v); }
#endif`;
const DQS_BASE = `
#ifdef USE_SKINNING
  vec4 dqR, dqD;
  { ivec4 si = ivec4(skinIndex + 0.5);
    vec4 r0 = texelFetch(uDQ, ivec2(si.x * 2, 0), 0), d0 = texelFetch(uDQ, ivec2(si.x * 2 + 1, 0), 0);
    vec4 r1 = texelFetch(uDQ, ivec2(si.y * 2, 0), 0), d1 = texelFetch(uDQ, ivec2(si.y * 2 + 1, 0), 0);
    vec4 r2 = texelFetch(uDQ, ivec2(si.z * 2, 0), 0), d2 = texelFetch(uDQ, ivec2(si.z * 2 + 1, 0), 0);
    vec4 r3 = texelFetch(uDQ, ivec2(si.w * 2, 0), 0), d3 = texelFetch(uDQ, ivec2(si.w * 2 + 1, 0), 0);
    vec4 w = skinWeight; w.y *= dot(r0, r1) < 0.0 ? -1.0 : 1.0; w.z *= dot(r0, r2) < 0.0 ? -1.0 : 1.0; w.w *= dot(r0, r3) < 0.0 ? -1.0 : 1.0;
    dqR = w.x * r0 + w.y * r1 + w.z * r2 + w.w * r3; dqD = w.x * d0 + w.y * d1 + w.z * d2 + w.w * d3;
    float l = length(dqR); dqR /= l; dqD /= l; }
#endif`;
const DQS_NORMAL = `
#ifdef USE_SKINNING
  objectNormal = dqRot(dqR, objectNormal);
  #ifdef USE_TANGENT
  objectTangent = dqRot(dqR, objectTangent);
  #endif
#endif`;
const DQS_POS = `
#ifdef USE_SKINNING
  transformed = dqRot(dqR, transformed) + 2.0 * (dqR.w * dqD.xyz - dqD.w * dqR.xyz + cross(dqR.xyz, dqD.xyz));
#endif`;
function dqsShader(sh, meta) {
  sh.uniforms.uDQ = { value: meta.dqTex };
  sh.vertexShader = sh.vertexShader.replace('#include <skinning_pars_vertex>', '#include <skinning_pars_vertex>\n' + DQS_PARS)
    .replace('#include <skinbase_vertex>', DQS_BASE).replace('#include <skinnormal_vertex>', DQS_NORMAL).replace('#include <skinning_vertex>', DQS_POS);
  return sh;
}
function dqsMaterial(mat, meta) { const prev = mat.onBeforeCompile; mat.onBeforeCompile = (sh, r) => { if (prev) prev.call(mat, sh, r); dqsShader(sh, meta); }; mat.customProgramCacheKey = () => 'dqs-' + mat.type; return mat; }

class Pose {
  constructor(nb) { this.q = []; for (let i = 0; i < nb; i++) this.q.push(new THREE.Quaternion()); this.root = new THREE.Vector3(); this.contacts = {}; }
  copy(p) { for (let i = 0; i < this.q.length; i++) this.q[i].copy(p.q[i]); this.root.copy(p.root); this.contacts = {}; for (const k in p.contacts) this.contacts[k] = cloneContact(p.contacts[k]); return this; }
  identity() { for (const q of this.q) q.identity(); this.contacts = {}; return this; }
  // ground contact for a limb end bone: target position (mesh space), the direction the hand/foot points along the ground, the pole (where the elbow / knee bulges), weight
  contact(name, t, fwd, pole, w = 1) { const c = this.contacts[name] || (this.contacts[name] = { t: new THREE.Vector3(), fwd: new THREE.Vector3(), pole: new THREE.Vector3(), w: 1 }); c.t.copy(t); c.fwd.copy(fwd); c.pole.copy(pole); c.w = w; return c; }
  lerp(p, t) {
    for (let i = 0; i < this.q.length; i++) this.q[i].slerp(p.q[i], t); this.root.lerp(p.root, t);
    for (const k in p.contacts) { const b = p.contacts[k], a = this.contacts[k]; if (!a) { const c = this.contact(k, b.t, b.fwd, b.pole, b.w * t); } else { a.t.lerp(b.t, t); a.fwd.lerp(b.fwd, t); a.pole.lerp(b.pole, t); a.w += (b.w - a.w) * t; } }
    for (const k in this.contacts) if (!p.contacts[k]) this.contacts[k].w *= (1 - t);
    return this;
  }
}
function cloneContact(c) { return { t: c.t.clone(), fwd: c.fwd.clone(), pole: c.pole.clone(), w: c.w }; }

// joint limits in degrees, in the canonical frame (x = flex about the hinge, y = twist about the bone, z = swing / abduction)
const LIMITS = {
  hips: [[-40, 40], [-30, 30], [-25, 25]], spine: [[-25, 30], [-20, 20], [-20, 20]], spine1: [[-25, 30], [-20, 20], [-20, 20]], chest: [[-25, 25], [-20, 20], [-15, 15]],
  neck: [[-35, 35], [-30, 30], [-20, 20]], head: [[-40, 35], [-60, 60], [-30, 30]], headfront: [[0, 0], [0, 0], [0, 0]],
  shoulder: [[-15, 15], [-10, 10], [-15, 15]], upperarm: [[-70, 150], [-60, 60], [-30, 120]], forearm: [[-5, 135], [-70, 70], [-10, 10]], hand: [[-45, 60], [-30, 30], [-25, 25]],
  thigh: [[-45, 110], [-40, 40], [-25, 60]], shin: [[-5, 130], [-15, 15], [-8, 8]], foot: [[-35, 45], [-15, 15], [-20, 20]], toes: [[-25, 35], [0, 0], [-10, 10]],
  finger1: [[-15, 70], [0, 0], [-14, 14]], finger2: [[-5, 90], [0, 0], [0, 0]], toe1: [[-15, 70], [0, 0], [-12, 12]], toe2: [[-5, 80], [0, 0], [0, 0]],
  // the tail curls down a long way (hanging under the jetpack, tucked between the legs, laid on the floor in the crouch); the gill stalks
  // fold back flat along the head (the ground pound)
  tail1: [[-45, 105], [-15, 15], [-50, 50]], tail: [[-45, 80], [-15, 15], [-50, 50]], gill: [[-90, 70], [-15, 15], [-75, 75]],
};
function limitsFor(name) {
  let L;
  if (name.startsWith('finger')) L = LIMITS['finger' + name.slice(-1)];
  else if (name.startsWith('toe') && !name.startsWith('toes')) L = LIMITS['toe' + name.slice(-1)];
  else if (name.startsWith('tail')) L = name === 'tail1' ? LIMITS.tail1 : LIMITS.tail; else if (name.startsWith('gill')) L = LIMITS.gill;
  else L = LIMITS[name.replace(/\.[LR]$/, '')] || [[-180, 180], [-180, 180], [-180, 180]];
  // right-side bones have mirrored frames: twist (y) and swing (z) change sign
  if (/\.R(\.|$)/.test(name)) L = [L[0], [-L[1][1], -L[1][0]], [-L[2][1], -L[2][0]]];
  return L;
}

class Puppet {
  constructor(meshes) {
    this.m = meshes; const ref = meshes.stand || Object.values(meshes)[0]; this.names = ref.names; const nb = this.nb = this.names.length; this.idx = {}; this.names.forEach((n, i) => this.idx[n] = i);
    this.par = ref.parent; this.lim = this.names.map(limitsFor);
    // canonical parent-relative frames come from the reference (stand) mesh; every other mesh's rest is expressed as a pose in those frames
    this.Rel = []; this.Fp = []; this.R = []; this.restPose = {};
    for (let i = 0; i < nb; i++) { const p = this.par[i]; this.Rel.push(p >= 0 ? ref.F[p].clone().invert().multiply(ref.F[i]) : ref.F[i].clone()); this.Fp.push(new THREE.Quaternion()); this.R.push(new THREE.Quaternion()); }
    for (const w in meshes) {
      const M = meshes[w], P = new Pose(nb);
      for (let i = 0; i < nb; i++) { const p = this.par[i]; const wc = p >= 0 ? M.F[p].clone().invert().multiply(M.F[i]) : M.F[i].clone(); P.q[i].copy(this.Rel[i]).invert().multiply(wc); }
      P.root.copy(M.rest[0]); this.restPose[w] = P;
    }
    this.mirror = this.names.map(n => { const m = n.includes('.L') ? n.replace('.L', '.R') : n.includes('.R') ? n.replace('.R', '.L') : n; return this.idx[m]; });
    this.len = ref.meta.bones.map((b, i) => ref.rest[i].distanceTo(ref.end[i]));
    this.kids = this.names.map(() => []); this.par.forEach((p, i) => { if (p >= 0) this.kids[p].push(i); if (p >= i) throw new Error('bones out of order'); });
  }
  // write a pose into one mesh: its bones and its skinning transforms
  apply(which, pose) { const k = this._sk || (this._sk = this.skelBuf()); this.skel(which, pose, k.F, k.P); this.applySkel(which, k.F, k.P); }
  skelBuf() { return { F: Array.from({ length: this.nb }, () => new THREE.Quaternion()), P: Array.from({ length: this.nb }, () => new THREE.Vector3()) }; }
  // the posed skeleton of a mesh for a pose: each bone's canonical world frame F[i] and its joint position P[i] (mesh space)
  skel(which, pose, F, Pj) {
    const M = this.m[which], par = this.par, Fp = this.frames(pose);
    for (let i = 0; i < this.nb; i++) { const p = par[i]; F[i].copy(Fp[i]);
      if (p < 0) Pj[i].copy(pose.root); else Pj[i].copy(M.rest[i]).sub(M.rest[p]).applyQuaternion(_q.copy(Fp[p]).multiply(_q2.copy(M.F[p]).invert())).add(Pj[p]); }
  }
  // put a mesh on a posed skeleton (frames + joint positions; it may be another mesh's, or a blend of two): bones (identity rest rotations:
  // the world rotation of bone i is F_i * inverse(Fmesh_i)) and the dual quaternion of each bone (joint i moves from rest[i] to P[i], turning by R[i])
  applySkel(which, F, Pj, restJ) {
    const M = this.m[which], FM = M.F, R = this.R, par = this.par, bones = M.bones, rest = restJ || M.rest, dq = M.dq;
    for (let i = 0; i < this.nb; i++) {
      const p = par[i]; R[i].copy(F[i]).multiply(_q.copy(FM[i]).invert());
      if (p >= 0) { _q2.copy(R[p]).invert(); bones[i].quaternion.copy(_q2).multiply(R[i]); bones[i].position.copy(Pj[i]).sub(Pj[p]).applyQuaternion(_q2); }
      else { bones[i].quaternion.copy(R[i]); bones[i].position.copy(Pj[i]); }
      const q = R[i], t = _v.copy(rest[i]).applyQuaternion(q).negate().add(Pj[i]), o = i * 8;
      dq[o] = q.x; dq[o + 1] = q.y; dq[o + 2] = q.z; dq[o + 3] = q.w;
      dq[o + 4] = 0.5 * (q.w * t.x + t.y * q.z - t.z * q.y); dq[o + 5] = 0.5 * (q.w * t.y + t.z * q.x - t.x * q.z); dq[o + 6] = 0.5 * (q.w * t.z + t.x * q.y - t.y * q.x); dq[o + 7] = -0.5 * (t.x * q.x + t.y * q.y + t.z * q.z);
    }
    M.dqTex.needsUpdate = true;
  }
  // per bone and mesh, an anatomical anchor in the bone's canonical frame: the face-sphere centre for the head, elsewhere the centroid of the
  // vertices the bone leads (zero where either mesh has too few). Blending anchors instead of joints makes corresponding parts of the two
  // sculpts land on each other (the two heads' joints sit 15 cm apart relative to their skulls, say; their face centres coincide)
  anchors() {
    if (this._anc) return this._anc; const acc = {}, A = {};
    for (const w in this.m) { const M = this.m[w], g = M.mesh.geometry, pos = g.getAttribute('position'), si = g.getAttribute('skinIndex').array, sw = g.getAttribute('skinWeight').array, s = new Float64Array(this.nb * 4);
      for (let v = 0; v < pos.count; v++) { let b = 0, bw = -1; for (let k = 0; k < 4; k++) if (sw[v * 4 + k] > bw) { bw = sw[v * 4 + k]; b = si[v * 4 + k]; } s[b * 4] += pos.getX(v); s[b * 4 + 1] += pos.getY(v); s[b * 4 + 2] += pos.getZ(v); s[b * 4 + 3]++; }
      acc[w] = s; A[w] = []; }
    for (let i = 0; i < this.nb; i++) { const ok = Object.values(acc).every(s => s[i * 4 + 3] >= 12);
      for (const w in this.m) { const M = this.m[w], s = acc[w], a = new THREE.Vector3();
        if (this.names[i] === 'head' && M.meta.face) a.fromArray(M.meta.face.c); else if (ok) a.set(s[i * 4] / s[i * 4 + 3], s[i * 4 + 1] / s[i * 4 + 3], s[i * 4 + 2] / s[i * 4 + 3]); else a.copy(M.rest[i]);
        A[w].push(a.sub(M.rest[i]).applyQuaternion(_q.copy(M.F[i]).invert())); } }
    return this._anc = A;
  }
  // both meshes on one skeleton blended between the stand's skeleton for poseS and the crawl's for poseC (u = 0: the stand's, 1: the crawl's):
  // the bones' frames are slerped and their anchors lerped, and each mesh hangs its own bone on the blended anchor. Used through the
  // stand <-> crawl swap: the two bodies then coincide (they differ only where the sculpts do), the proportions morph smoothly from one
  // to the other and the dissolve between them is all but invisible
  applyMix(poseS, poseC, u) {
    const An = this.anchors(), a = this._ma || (this._ma = this.skelBuf()), b = this._mb || (this._mb = this.skelBuf()), mS = this._ms || (this._ms = this.skelBuf()), mC = this._mc || (this._mc = this.skelBuf());
    this.skel('stand', poseS, a.F, a.P); this.skel('crawl', poseC, b.F, b.P);
    for (let i = 0; i < this.nb; i++) {
      const F = mS.F[i].copy(a.F[i]).slerp(b.F[i], u); mC.F[i].copy(F);
      _v.copy(An.stand[i]).applyQuaternion(a.F[i]).add(a.P[i]); _v2.copy(An.crawl[i]).applyQuaternion(b.F[i]).add(b.P[i]); _v.lerp(_v2, u);   // the blended anchor
      mS.P[i].copy(An.stand[i]).applyQuaternion(F).negate().add(_v); mC.P[i].copy(An.crawl[i]).applyQuaternion(F).negate().add(_v);
    }
    this.applySkel('stand', mS.F, mS.P); this.applySkel('crawl', mC.F, mC.P);
  }
  // evaluate the posed canonical world frames (Fp) up to bone i, for aim / collision queries
  frames(pose) { const Fp = this.Fp; for (let i = 0; i < this.nb; i++) { const p = this.par[i]; if (p >= 0) Fp[i].copy(Fp[p]).multiply(this.Rel[i]).multiply(pose.q[i]); else Fp[i].copy(this.Rel[i]).multiply(pose.q[i]); } return Fp; }
  // set pose.q[i] so the bone's posed Y axis points along dir (world) with its Z (ventral) toward zHint; ancestors are evaluated first; limits applied
  aim(pose, i, dir, zHint, clamp = true) {
    const Fp = this.Fp; const chain = []; for (let b = this.par[i]; b >= 0; b = this.par[b]) chain.push(b); chain.reverse();
    for (const b of chain) { const p = this.par[b]; if (p >= 0) Fp[b].copy(Fp[p]).multiply(this.Rel[b]).multiply(pose.q[b]); else Fp[b].copy(this.Rel[b]).multiply(pose.q[b]); }
    const y = _v.copy(dir).normalize(), z = _v2.copy(zHint).addScaledVector(y, -y.dot(zHint)); if (z.lengthSq() < 1e-8) z.set(0, -1, 0).addScaledVector(y, -y.dot(_v3.set(0, -1, 0))); z.normalize();
    const x = _v3.crossVectors(y, z); _m.makeBasis(x, y, z); _q.setFromRotationMatrix(_m);
    const p = this.par[i]; pose.q[i].copy(this.Rel[i]).invert(); if (p >= 0) pose.q[i].multiply(_q2.copy(Fp[p]).invert()); pose.q[i].multiply(_q);
    if (clamp) this.clampBone(pose, i);
  }
  clampBone(pose, i) {
    const L = this.lim[i]; _e.setFromQuaternion(pose.q[i], 'XYZ');
    const x = clampDeg(_e.x, L[0]), y = clampDeg(_e.y, L[1]), z = clampDeg(_e.z, L[2]);
    if (x !== _e.x || y !== _e.y || z !== _e.z) { _e.set(x, y, z, 'XYZ'); pose.q[i].setFromEuler(_e); return true; }
    return false;
  }
  clampAll(pose) { for (let i = 0; i < this.nb; i++) this.clampBone(pose, i); }
  // joint positions of a mesh for a pose (mesh space, mesh at the origin), without touching the THREE bones
  fk(which, pose) {
    const M = this.m[which], Fp = this.frames(pose), par = this.par; if (!this._pos) { this._pos = []; for (let i = 0; i < this.nb; i++) this._pos.push(new THREE.Vector3()); }
    const pos = this._pos;
    for (let i = 0; i < this.nb; i++) { const p = par[i]; if (p < 0) pos[i].copy(pose.root); else { pos[i].copy(M.rest[i]).sub(M.rest[p]).applyQuaternion(_kq.copy(Fp[p]).multiply(_kq2.copy(M.F[p]).invert())).add(pos[p]); } }
    return pos;
  }
  // two-bone IK: put the end joint `en` at `target` (mesh space) by aiming `up` and `lo`; the joint between bulges toward `pole`; no hyperextension.
  // sU: side of the upper bone's canonical Z relative to the pole (+1 legs: the thigh's front faces the knee bulge; -1 arms: the bicep side faces away from the elbow point)
  // Both bones take their twist from the limb's plane: the hinge axis is the plane normal (n x p), the same for the whole solve, so the frames stay
  // continuous through every configuration (projecting a fixed hint onto each bone flipped the thigh by 180 deg when the knee passed 90 deg, and the
  // shin when it passed square to the hip-foot line: the twisting pops of v6).
  ik2(which, pose, up, lo, en, target, pole, sU, fallback) {
    const M = this.m[which], pos = this.fk(which, pose), a = _k1.copy(pos[up]);
    const L1 = M.rest[lo].distanceTo(M.rest[up]), L2 = M.rest[en].distanceTo(M.rest[lo]);
    // soft reach: past 92 % of the full length the reach eases toward 99.5 % instead of stopping dead at it, so the joint between never
    // snaps as a target crosses the limb's reach (the elbow / knee angle's rate stays continuous)
    const n = _k2.copy(target).sub(a); let d = n.length(); n.normalize(); const Lx = L1 + L2, d0 = 0.92 * Lx, dm = 0.995 * Lx;
    if (d > d0) d = d0 + (dm - d0) * Math.tanh((d - d0) / (dm - d0)); d = Math.max(d, Math.abs(L1 - L2) + 0.01);
    const A = Math.acos(Math.min(1, Math.max(-1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))));
    // the bulge direction, square to the hip-foot line; if the pole runs nearly along that line it is eased toward the fallback (never a sudden swap)
    const p = _k3.copy(pole).addScaledVector(n, -n.dot(pole)); const pl = p.length() / Math.max(1e-6, pole.length());
    if (pl < 0.35) { const fb = fallback || _k8.set(0, 1, 0); const k = 1 - pl / 0.35; _k7.copy(fb).addScaledVector(n, -n.dot(fb)).normalize(); p.normalize().multiplyScalar(1 - k * k).addScaledVector(_k7, k * k); }
    if (p.lengthSq() < 1e-10) p.set(0, 1, 0).addScaledVector(n, -n.y); p.normalize();
    const yU = _k4.copy(n).multiplyScalar(Math.cos(A)).addScaledVector(p, Math.sin(A));
    const e = _k5.copy(a).addScaledVector(yU, L1), yL = _k6.copy(a).addScaledVector(n, d).sub(e).normalize();
    const X = _k7.crossVectors(n, p).normalize();   // the hinge
    this.setFrame(pose, up, yU, _k8.copy(X).multiplyScalar(sU).cross(yU)); this.setFrame(pose, lo, yL, _k8.copy(X).negate().cross(yL));
    return d;
  }
  // turn bone i so its Y axis points along dir (world) by the shortest arc from where it points now: no twist is added (a fixed Z hint
  // flips the frame half a turn when the bone passes through it); ancestors evaluated first; no limits
  aimMin(pose, i, dir) {
    const Fp = this.Fp; const chain = []; for (let b = this.par[i]; b >= 0; b = this.par[b]) chain.push(b); chain.reverse();
    for (const b of chain) { const p = this.par[b]; if (p >= 0) Fp[b].copy(Fp[p]).multiply(this.Rel[b]).multiply(pose.q[b]); else Fp[b].copy(this.Rel[b]).multiply(pose.q[b]); }
    const p = this.par[i], base = _q.copy(this.Rel[i]); if (p >= 0) base.premultiply(Fp[p]);   // the bone's frame with q = identity
    const cur = _q2.copy(base).multiply(pose.q[i]); _v.set(0, 1, 0).applyQuaternion(cur); _v2.copy(dir).normalize();
    const turn = new THREE.Quaternion().setFromUnitVectors(_v, _v2); cur.premultiply(turn);
    pose.q[i].copy(base).invert().multiply(cur);
  }
  // set bone i's posed canonical frame to Y = y and Z = z (both world, z square to y), ancestors evaluated first; no limits
  setFrame(pose, i, y, z) {
    const Fp = this.Fp; const chain = []; for (let b = this.par[i]; b >= 0; b = this.par[b]) chain.push(b); chain.reverse();
    for (const b of chain) { const p = this.par[b]; if (p >= 0) Fp[b].copy(Fp[p]).multiply(this.Rel[b]).multiply(pose.q[b]); else Fp[b].copy(this.Rel[b]).multiply(pose.q[b]); }
    _v.copy(y).normalize(); _v2.copy(z).addScaledVector(_v, -_v.dot(z)).normalize(); _v3.crossVectors(_v, _v2); _m.makeBasis(_v3, _v, _v2); _q.setFromRotationMatrix(_m);
    const p = this.par[i]; pose.q[i].copy(this.Rel[i]).invert(); if (p >= 0) pose.q[i].multiply(_q2.copy(Fp[p]).invert()); pose.q[i].multiply(_q);
  }
  // world position of a joint of a mesh after apply()
  jointWorld(which, name, out) { const M = this.m[which]; M.mesh.updateMatrixWorld(true); return M.byName[name].getWorldPosition(out || new THREE.Vector3()); }
}
function clampDeg(rad, lim) { const d = rad / DEG; return (d < lim[0] ? lim[0] : d > lim[1] ? lim[1] : d) * DEG; }
function mirrorQ(q, out) { return out.set(q.x, -q.y, -q.z, q.w); }
// rotate a pose bone by Euler degrees (XYZ) in its own frame, on top of what it has
function rot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].multiply(_q2.setFromEuler(_e)); }
function setRot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].setFromEuler(_e); }

// ====================================================================== anim
const __anim = (() => {
// Procedural animation for the axolotl puppet (v7): states (stand idle, crawl, power, jetpack, pound, victory, crouch), stand <-> crawl
// transitions, secondary motion (gill stalks, tail, digits, breathing, the neck's small life) and the soft-body jelly layer's drive.
// Pose conventions (canonical frames): x = flex about the hinge, y = twist about the bone, z = swing; see axo.js.
//  - Every change of state is blended by inertialization: the pose shown last frame is carried into the new state as an offset that decays
//    smoothly from its own velocity to zero, so nothing ever jumps, freezes or changes speed abruptly (no snapshot crossfades).
//  - Stand <-> crawl: the outgoing mesh folds into the shared crouch; the incoming mesh takes the very same pose (the two meshes share one
//    canonical skeleton, so every bone points the same way) and both ride ONE skeleton that morphs from the outgoing body's proportions to
//    the incoming one's, so the two bodies coincide while a complementary screen-space dither swaps them (each pixel shows exactly one of the
//    two: no see-through double image), under a jelly squash pulse; the incoming mesh then settles into its own state.

const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _v4 = new THREE.Vector3(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _s1 = new THREE.Quaternion(), _s2 = new THREE.Quaternion(), _s3 = new THREE.Quaternion();
const _wE = new THREE.Euler(), _wq = new THREE.Quaternion(), _wq2 = new THREE.Quaternion(), _wF = new THREE.Quaternion();
const smooth = t => t * t * (3 - 2 * t), clamp01 = t => Math.max(0, Math.min(1, t));
// a Catmull-Rom curve through the points K (n samples per span)
function catmull(K, n) { const out = [K[0].clone()]; for (let i = 0; i < K.length - 1; i++) { const p0 = K[Math.max(0, i - 1)], p1 = K[i], p2 = K[i + 1], p3 = K[Math.min(K.length - 1, i + 2)];
  for (let j = 1; j <= n; j++) { const t = j / n, t2 = t * t, t3 = t2 * t; out.push(new THREE.Vector3().addScaledVector(p0, -0.5 * t3 + t2 - 0.5 * t).addScaledVector(p1, 1.5 * t3 - 2.5 * t2 + 1).addScaledVector(p2, -1.5 * t3 + 2 * t2 + 0.5 * t).addScaledVector(p3, 0.5 * t3 - 0.5 * t2)); } }
  return out; }
const ease = { inOut: t => smooth(clamp01(t)), out: t => 1 - Math.pow(1 - clamp01(t), 3), in: t => Math.pow(clamp01(t), 3) };
// rotation vector (axis * angle) of a unit quaternion, shortest way round, and back
function qlog(q, out, o) { let x = q.x, y = q.y, z = q.z, w = q.w; if (w < 0) { x = -x; y = -y; z = -z; w = -w; } const s = Math.sqrt(x * x + y * y + z * z); const a = s > 1e-9 ? 2 * Math.atan2(s, w) / s : 2; out[o] = x * a; out[o + 1] = y * a; out[o + 2] = z * a; }
function qexp(x, y, z, q) { const a = Math.sqrt(x * x + y * y + z * z); if (a < 1e-9) return q.set(x * 0.5, y * 0.5, z * 0.5, 1).normalize(); const s = Math.sin(a / 2) / a; return q.set(x * s, y * s, z * s, Math.cos(a / 2)); }

class Spring {
  constructor(n, k, c) { this.x = new Float32Array(n); this.v = new Float32Array(n); this.k = k; this.c = c; }
  step(target, dt) {
    dt = Math.min(dt, 1 / 30); const sub = 2, h = dt / sub;
    for (let s = 0; s < sub; s++) for (let i = 0; i < this.x.length; i++) { const a = this.k * (target[i] - this.x[i]) - this.c * this.v[i]; this.v[i] += a * h; this.x[i] += this.v[i] * h; }
    return this.x;
  }
}
// a critically damped follower (second order): the value and its rate both stay continuous when the input steps
class Follow { constructor(w, x = 0) { this.w = w; this.x = x; this.v = 0; } step(target, dt) { const w = this.w, h = Math.min(dt, 1 / 30); const a = w * w * (target - this.x) - 2 * w * this.v; this.v += a * h; this.x += this.v * h; return this.x; } }

class Animator {
  constructor(puppet) {
    const P = this.P = puppet, nb = P.nb, I = this.I = P.idx;
    this.pose = new Pose(nb); this.A = new Pose(nb); this.B = new Pose(nb); this.C = new Pose(nb); this.other = new Pose(nb);
    this.prev = new Pose(nb); this.prev2 = new Pose(nb); this.hasPrev = 0;
    this.inert = { on: false, t: 0, T: 0.4, r: new Float32Array(nb * 3), v: new Float32Array(nb * 3), root: new THREE.Vector3(), rootV: new THREE.Vector3() }; this.pendingInert = 0;
    this.t = 0; this.stT = 0; this.state = 'stand'; this.mesh = 'stand'; this.fade = 1; this.squash = 1; this.gait = 0; this.speed = 1; this.trans = null; this.dt = 1 / 60;
    // the swap: mixU = the crawl's share of the shared skeleton (null: each mesh on its own), swap = the dissolve { from, to, k }
    this.mixU = null; this.swap = null; this.oprev = new Pose(nb); this.oprev2 = new Pose(nb);
    this.TT = { A: 0.32, M0: 0.22, M: 0.52, C: 0.48 };   // fold, morph start and length, settle (s)
    // the crouch (degrees, metres) and the crawl's gathered pose
    this.CR = { hips: 30, spine: 18, spine1: 16, chest: 12, neck: -30, head: -34, thigh: [75, 16], shin: 112, foot: -8, arm: [68, 20], fore: 10, hand: -30, headZ: 0.24, handOut: 0.1, handFwd: 0.26, footOut: 0.04, footZ: 0 };
    this.GA = { spine1: -6, chest: -8, neck: 4, head: 6, handOut: 0, handFwd: 0.02, footZ: 0.05 };
    this.look = { yaw: 0, pitch: 0 };   // game-driven head look, degrees
    // symmetric crawl rest: each bone's world rest frame averaged with the mirror of its partner's, the local canonical poses derived top-down
    const LC = P.restPose.crawl; this.LS = new Pose(nb); this.LS.root.copy(LC.root); this.LS.root.x = 0;
    { const Fw = P.m.crawl.F, Fs = [], Fp = [];
      for (let i = 0; i < nb; i++) { const j = P.mirror[i]; const mj = new THREE.Quaternion(Fw[j].x, -Fw[j].y, -Fw[j].z, Fw[j].w); Fs.push(Fw[i].clone().slerp(mj, 0.5)); }
      for (let i = 0; i < nb; i++) { const p = P.par[i]; const nm = P.names[i];
        if (/^(gill|finger|toe\d)/.test(nm)) { this.LS.q[i].copy(LC.q[i]); Fp.push(p >= 0 ? Fp[p].clone().multiply(P.Rel[i]).multiply(this.LS.q[i]) : Fs[i].clone()); continue; }
        const q = this.LS.q[i].copy(P.Rel[i]).invert(); if (p >= 0) q.multiply(_q.copy(Fp[p]).invert()); q.multiply(Fs[i]); Fp.push(Fs[i].clone()); } }
    this.standRoot = P.m.stand.rest[0].clone();
    const idp = new Pose(nb); idp.root.copy(this.standRoot); const fs = P.fk('stand', idp); this.standFeet = { L: fs[I['foot.L']].clone(), R: fs[I['foot.R']].clone() };
    // each standing foot's own rest direction along the ground (planted that way, the heel and the ankle keep their rest shape)
    this.standFootFwd = { L: fs[I['toes.L']].clone().sub(fs[I['foot.L']]).setY(0).normalize(), R: fs[I['toes.R']].clone().sub(fs[I['foot.R']]).setY(0).normalize() };
    const fc = P.fk('crawl', this.LS);
    // the gait from the limbs themselves: each limb's ground centre along its rest direction at 72% of its reach; one stride keeps every limb
    // inside 90% of its reach
    const Mc = P.m.crawl, len = (a, b) => Mc.rest[I[a]].distanceTo(Mc.rest[I[b]]);
    const centre = (root, end, lo) => { const r = fc[I[root]], e = fc[I[end]], Lm = len(root, lo) + len(lo, end), drop = r.y - e.y;
      const hd = new THREE.Vector3(e.x - r.x, 0, e.z - r.z).normalize(), rh = Math.sqrt(Math.max(0.01, (0.72 * Lm) ** 2 - drop * drop));
      return { c: new THREE.Vector3(Math.abs(r.x + hd.x * rh), 0, r.z + hd.z * rh), root: new THREE.Vector3(Math.abs(r.x), r.y, r.z), Lm, h: e.y }; };
    const gh = centre('upperarm.L', 'hand.L', 'forearm.L'), gf = centre('thigh.L', 'foot.L', 'shin.L');
    const maxStride = g => { let S = 0.4; for (; S > 0.08; S -= 0.01) { let ok = true; for (const dz of [-0.55 * S, 0.55 * S]) { const p = new THREE.Vector3(g.c.x, g.h, g.c.z + dz); if (p.distanceTo(g.root) > 0.9 * g.Lm) ok = false; } if (ok) break; } return S; };
    this.crawlHand = gh.c; this.crawlFoot = gf.c; this.stride = Math.min(0.3, maxStride(gh), maxStride(gf));
    // each limb bends and points the way it does in the sculpt (the bind): the knee / elbow bulge (pole) and the hand / foot direction
    const bendOf = (root, mid, end) => { const r = fc[I[root]], k = fc[I[mid]], e = fc[I[end]], n = e.clone().sub(r).normalize(), p = k.clone().sub(r); return p.addScaledVector(n, -p.dot(n)).normalize(); };
    const dirOf = (end) => { const e = fc[I[end]]; let t = new THREE.Vector3(); for (let k = 0; k < 4; k++) { const nm = (end.startsWith('hand') ? 'finger' : 'toe') + k + '.L.2'; if (I[nm] !== undefined) t.add(fc[I[nm]]); } t.multiplyScalar(0.25); return t.sub(e).setY(0).normalize(); };
    this.limbBind = { arm: { pole: bendOf('upperarm.L', 'forearm.L', 'hand.L'), fwd: dirOf('hand.L') }, leg: { pole: bendOf('thigh.L', 'shin.L', 'foot.L'), fwd: dirOf('foot.L') } };
    this.gaitInfo = { hand: gh, foot: gf, stride: this.stride };
    // contact heights of the wrist / ankle joints above the floor (the crawl's from its own rest, where they lie on the ground)
    this.H = { crawlHand: fc[I['hand.L']].y, crawlFoot: fc[I['foot.L']].y, standHand: fc[I['hand.L']].y, standFoot: P.m.stand.rest[I['foot.L']].y };
    this.groundSpeed = 0;
    this.chain = { spine: ['hips', 'spine', 'spine1', 'chest', 'neck'].map(n => I[n]), tail: [1, 2, 3, 4, 5, 6].map(k => I['tail' + k]),
      gills: ['L', 'R'].flatMap(s => [0, 1, 2].flatMap(k => [I[`gill${k}.${s}.1`], I[`gill${k}.${s}.2`]])),
      fingers: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`finger${k}.${s}.1`], I[`finger${k}.${s}.2`]])), toes: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`toe${k}.${s}.1`], I[`toe${k}.${s}.2`]])) };
    this.gillSpring = new Spring(12, 380, 16); this.gillTarget = new Float32Array(12);   // gills: 3.1 Hz, damping 0.41, well above the gait (0.6 to 1.8 Hz): the stalks never ride a resonance
    this.tailSpring = new Spring(12, 80, 7); this.tailTarget = new Float32Array(12); this.tailFree = 1; this.tailFreeS = new Follow(8, 1);
    // kicks (landings, jumps, the swap's pulse) go through two first-order stages before they reach a spring's rate: an impulse arrives as a
    // short smooth push (about 50 ms) instead of a one-frame jump in speed
    this.tailPush = new Float32Array(12); this.gillPush = new Float32Array(12); this.tailPush2 = new Float32Array(12); this.gillPush2 = new Float32Array(12); this.tailTgt = new Float32Array(12);
    this.sqPush = [0, 0]; this.lagPush = [0, 0]; this.flick = null;
    this.headPrev = new THREE.Vector3(); this.headVel = new THREE.Vector3(); this.headVelS = new THREE.Vector3(); this.rootPrev = new THREE.Vector3(); this.rootVel = new THREE.Vector3();
    this.events = [];
    this.motion = { speed: 1, turn: 0, exert: 0 }; this.look2 = null; this.airY = 0; this.airV = 0; this.inAir = false; this.landK = 0; this.airYS = 0; this.airYV = 0;
    // the drive goes through two critically damped stages each: value, rate and acceleration all stay continuous when an input steps
    this.turnF0 = new Follow(12); this.turnF = new Follow(12); this.speedF0 = new Follow(10); this.speedF = new Follow(10); this.exertF0 = new Follow(6); this.exertF = new Follow(6); this.turnS = 0; this.speedS = 0; this.exertS = 0;
    this.flickT = 2 + Math.random() * 3; this.breath = 0; this.breathPh = 0;
    this.lagP = new THREE.Vector3(); this.lagV = new THREE.Vector3(); this.accS = new THREE.Vector3(); this.sqV = 0; this.sq = 0; this.jellyRipple = 0; this.throatK = 0;
    // the neck's life: a sprung head (yaw, pitch, roll) after a target made of glances, the game's look, a slow drift and the breath
    this.neck = { x: [0, 0, 0], v: [0, 0, 0], glance: [0, 0, 0], glanceT: 1.5 + Math.random() * 2, holdT: 0, eye: [0, 0], amt: 1, thrT: 3 + Math.random() * 3, thrN: 0, thrU: 0 };
    this.digitsCur = null;
  }
  setLook(look) { this.look2 = look; }
  jump() { if (!this.inAir) { this.inAir = true; this.airV = 3.2; this.sqPush[0] -= 3.0; this.kickGills(0, -0.6); this.lagPush[0] -= 0.6; } }
  // ---------------- state machine ----------------
  set(state) {
    if (state === this.state && !this.trans) return;
    const wantCrawl = state === 'crawl', T = this.trans;
    if (T) {
      const toCrawl = T.kind === 'standToCrawl';
      if (wantCrawl === toCrawl) { if (!toCrawl) T.target = state; return; }   // already heading there (rising: only where it rises to changes)
      if (!T.m) { this.trans = null; this.state = state; this.stT = this.t; this.startInertia(0.4); return; }   // still folding on its own mesh: just turn back
      if (!T.c) {   // mid-morph: run the morph backwards from where it is (the other mesh's version of the pose takes over the pose stream)
        const TT = this.TT, back = TT.M0 + TT.M - (T.t - TT.M0);
        this.trans = { kind: toCrawl ? 'crawlToStand' : 'standToCrawl', t: back, target: state, a: 1, m: 1 }; this.state = toCrawl ? 'toStand' : 'toCrawl';
        this.mesh = this.mesh === 'stand' ? 'crawl' : 'stand'; this.prev.copy(this.oprev); this.prev2.copy(this.oprev2); this.hasPrev = 2; this.startInertia(0.25); return;
      }
      // the swap is done: a fresh transition back from here
    }
    const onCrawl = this.mesh === 'crawl';
    if (onCrawl && !wantCrawl) { this.trans = { kind: 'crawlToStand', t: 0, target: state }; this.state = 'toStand'; return; }
    if (!onCrawl && wantCrawl) { this.trans = { kind: 'standToCrawl', t: 0 }; this.state = 'toCrawl'; return; }
    this.trans = null; this.state = state; this.stT = this.t; this.startInertia(state === 'victory' ? 0.4 : state === 'pound' ? 0.4 : 0.5);
  }
  startInertia(T) { this.pendingInert = Math.max(this.pendingInert, T); }
  update(dt) {
    dt = Math.min(dt, 1 / 20); this.dt = dt; this.t += dt; const out = this.A; const M = this.motion;
    // the drive, through critically damped followers: speed, turn and exertion change smoothly in value and in rate
    const spd0 = this.speedS; this.speedS = this.speedF.step(this.speedF0.step(M.speed, dt), dt); this.turnS = this.turnF.step(this.turnF0.step(M.turn, dt), dt); this.exertS = this.exertF.step(this.exertF0.step(M.exert, dt), dt);
    const dv = this.speedF.v;
    this.accS.x += (-this.turnS * this.speedS * 2.5 - this.accS.x) * Math.min(1, dt * 8); this.accS.z += (dv * 1.5 - this.accS.z) * Math.min(1, dt * 8);
    // a hop: ballistic, the root following it through a stiff spring (no instant change of speed at take-off or landing); a landing squashes
    // the body and kicks the gills and the tail
    if (this.inAir) { this.airV -= 9.8 * dt; this.airY += this.airV * dt; if (this.airY <= 0) { this.airY = 0; this.inAir = false; const imp = Math.min(1, -this.airV / 4); this.sqPush[0] += 6.5 * imp; this.landK = imp; this.kickGills(0, 1.2 * imp); this.lagPush[0] += 0.5 * imp; for (let k = 0; k < 6; k++) this.tailPush[k * 2 + 1] -= 60 * imp; } }
    { const w = 34, h = dt; const a = w * w * (this.airY - this.airYS) - 2 * w * this.airYV; this.airYV += a * h; this.airYS += this.airYV * h; }
    this.landK = Math.max(0, this.landK - dt * 3);
    this.eyeBias = [0, 0];   // where the state wants the eyes (face units; the jetpack looks down)
    if (this.trans) this.updateTransition(dt, out); else this.evalStateOnset(this.state, out, dt);
    this.addAir(out); this.stepNeck(dt); this.stepSecondary(dt);
    // the state's pose (with the breath, inside the joint limits, the limbs on their contacts) is what the inertialization blends; the neck's
    // life, the tail and the gill springs go on top after it (both the old and the new state carry them, so they are not blended twice)
    this.pose.copy(out); this.applyBase(this.pose, this.mesh); this.ground(this.mesh, this.pose); this.inertialize(dt); this.applyTop(this.pose, this.mesh); this.jelly(dt);
    for (const q of this.pose.q) q.normalize();   // (rounding never lets a rotation drift off unit length into the skinning)
    if (this.mixU !== null) {
      // the morph: the other mesh's own half of the shared pose, with the same life on it; both meshes on one skeleton blended between the two
      const o = this.mesh === 'stand' ? 'crawl' : 'stand', ot = this.other; ot.copy(this.B); this.addAir(ot); this.applyBase(ot, o); this.ground(o, ot);
      this.oprev2.copy(this.oprev); this.oprev.copy(ot); this.applyTop(ot, o); for (const q of ot.q) q.normalize();
      if (this.mesh === 'stand') this.P.applyMix(this.pose, ot, this.mixU); else this.P.applyMix(ot, this.pose, this.mixU);
    } else this.P.apply(this.mesh, this.pose);
    this.trackHead(dt);
  }
  // in the air the limbs let go of the ground: the contacts fade on a quintic of the height (no kink in rate or acceleration at take-off or at
  // touch-down)
  addAir(p) { p.root.y += this.airYS; if (this.airYS > 1e-4) { const x = clamp01(this.airYS / 0.25), k = 1 - x * x * x * (10 - 15 * x + 6 * x * x); for (const c in p.contacts) p.contacts[c].w *= k; } }
  applyBase(pose, which) { const I = this.I, br = this.breath * (0.6 + 0.9 * this.exertS); rot(pose, I.chest, -1.8 * br, 0, 0); rot(pose, I.spine1, -1.2 * br, 0, 0); this.limits(pose, which); }
  applyTop(pose, which) { this.applyNeck(pose); this.applySecondary(pose, which); this.limits(pose, which, this.topBones || (this.topBones = this.P.names.map((n, i) => /^(neck|head|tail|gill)/.test(n) ? i : -1).filter(i => i >= 0))); }
  // joint limits: stand poses relative to the stand rest, crawl poses relative to the symmetric crawl rest
  limits(pose, which, list) {
    const base = which === 'crawl' ? this.LS : null, P = this.P;
    for (const i of (list || P.lim.keys())) {
      if (base) { _q.copy(base.q[i]).invert().multiply(pose.q[i]); const bq = pose.q[i]; bq.copy(_q); P.clampBone(pose, i); bq.premultiply(base.q[i]); }
      else P.clampBone(pose, i);
    }
  }
  // ---------------- inertialization: the last pose shown carried into the new one as a decaying offset ----------------
  inertialize(dt) {
    const P = this.pose, nb = this.P.nb, R = this.inert;
    if (this.pendingInert > 0) {
      if (this.hasPrev >= 2) {
        R.T = this.pendingInert; R.t = 0; R.on = true; const idt = 1 / Math.max(dt, 1e-3);
        for (let i = 0; i < nb; i++) {
          _q.copy(P.q[i]).invert().premultiply(this.prev.q[i]); qlog(_q, R.r, i * 3);                    // d0 = prev * X^-1
          _q2.copy(this.prev2.q[i]).invert().premultiply(this.prev.q[i]); qlog(_q2, R.v, i * 3);         // the shown pose's own rate
          for (let c = 0; c < 3; c++) { let v = R.v[i * 3 + c] * idt; R.v[i * 3 + c] = Math.max(-12, Math.min(12, v)); }
        }
        R.root.copy(this.prev.root).sub(P.root); R.rootV.copy(this.prev.root).sub(this.prev2.root).multiplyScalar(idt); if (R.rootV.length() > 4) R.rootV.setLength(4);
      }
      this.pendingInert = 0;
    }
    if (R.on) {
      // the offset decays along a quintic: it starts at the last shown pose's offset with its rate and no acceleration of its own, and ends at
      // rest with no rate and no acceleration (an exponential decay starts with a large kick of acceleration: a visible jolt at the gill tips)
      R.t += dt; const T = R.T, s = R.t / T;
      if (s >= 1) R.on = false;
      else {
        const s3 = s * s * s, s4 = s3 * s, s5 = s4 * s, ka = 1 - 10 * s3 + 15 * s4 - 6 * s5, kb = T * (s - 6 * s3 + 8 * s4 - 3 * s5);   // x = r ka + v kb
        for (let i = 0; i < nb; i++) { const o = i * 3;
          const x = R.r[o] * ka + R.v[o] * kb, y = R.r[o + 1] * ka + R.v[o + 1] * kb, z = R.r[o + 2] * ka + R.v[o + 2] * kb;
          if (x * x + y * y + z * z < 1e-12) continue; P.q[i].premultiply(qexp(x, y, z, _q)); }
        _v.copy(R.root).multiplyScalar(ka).addScaledVector(R.rootV, kb); P.root.add(_v);
      }
    }
    this.prev2.copy(this.prev); this.prev.copy(P); this.hasPrev = Math.min(2, this.hasPrev + 1);
  }
  // a state's own motion (sways, hops, pumps, shakes) fades in from rest over its first 0.6 s: the pose it is entered with is the state frozen
  // at the moment of entry, so the target the inertialization blends into starts with no speed of its own (the blend stays smooth in rate too)
  evalStateOnset(state, out, dt) {
    const t0 = this.stT || 0, tau = this.t - t0;
    if (state === 'crawl' || tau >= 0.6) return this.evalState(state, this.t, out, dt);
    const fz = this.OB || (this.OB = new Pose(this.P.nb)); this.evalState(state, t0, fz, dt); this.evalState(state, this.t, out, dt);
    return out.copy(fz.lerp(out, smooth(clamp01(tau / 0.6))));
  }
  evalState(state, t, out, dt) {
    switch (state) {
      case 'stand': return this.standIdle(t, out);
      case 'crawl': return this.crawl(t, out, dt);
      case 'power': return this.powerPose(t, out);
      case 'jetpack': return this.jetpack(t, out);
      case 'pound': return this.groundPound(t, out);
      case 'victory': return this.victory(t, out);
      case 'crouch': return this.crouch(out, 1, 1, 'stand');
      case 'prone': return this.proneCrawl(out);
      case 'rest': out.identity(); out.root.copy(this.standRoot); return out;
      case 'armsfwd': case 'armsside': case 'armsup': return this.armTest(state, out);
      default: return this.standIdle(t, out);
    }
  }
  // ---------------- helpers ----------------
  tailWave(ph, ampDeg, lag, lift) { for (let k = 0; k < 6; k++) { const a = ampDeg * (0.45 + k * 0.2); this.tailTarget[k * 2] = Math.sin(ph - k * lag) * a; this.tailTarget[k * 2 + 1] = lift * (k < 3 ? 1 : 0.6); } }
  // digits: curl about the hinge only, spread about the palm normal, inside the joint limits
  digits(out, curl, spread, toeCurl, toeSpread = spread) {
    for (let s = 0; s < 2; s++) { const m = s === 0 ? 1 : -1;
      this.chain.fingers[s].forEach((f, k) => { rot(out, f[0], curl * 42, 0, (k - 1.5) * spread * 9 * m); rot(out, f[1], curl * 55, 0, 0); });
      this.chain.toes[s].forEach((f, k) => { rot(out, f[0], toeCurl * 40, 0, (k - 1.5) * toeSpread * 8 * m); rot(out, f[1], toeCurl * 45, 0, 0); }); }
  }
  // fists: the fingers curled tight into the palm (inside the joint limits), the toes a little
  // (curled until the tips meet the palm, not through it: the stand's chunky fingers would otherwise sink into the hand)
  fists(out, k = 1) { for (let s = 0; s < 2; s++) this.chain.fingers[s].forEach((f, j) => { rot(out, f[0], 56 * k, 0, (j - 1.5) * -2 * (s === 0 ? 1 : -1) * k); rot(out, f[1], 68 * k, 0, 0); }); }
  // a tail path that starts out the way the tail's root already points and turns by `turn` radians (+: down and under) over an arc of radius
  // R, then runs straight on for `tail` metres: the bend shared out along the tail instead of folded at its root
  arcPath(which, out, turn, R, tail) {
    const P = this.P, ch = this.chain.tail, pos = P.fk(which, out), r = pos[ch[0]].clone(), d0 = pos[ch[1]].clone().sub(r).setX(0).normalize();
    const nrm = new THREE.Vector3(0, -d0.z, d0.y).multiplyScalar(-1);   // the side-plane normal of d0, toward the belly side when turning down
    if (nrm.y > 0) nrm.negate();
    const pts = [r], n = 10;
    for (let k = 1; k <= n; k++) { const a = turn * k / n; pts.push(r.clone().addScaledVector(d0, Math.sin(a) * R).addScaledVector(nrm, (1 - Math.cos(a)) * R)); }
    const dEnd = d0.clone().multiplyScalar(Math.cos(turn)).addScaledVector(nrm, Math.sin(turn)); pts.push(pts[n].clone().addScaledVector(dEnd, tail));
    return pts;
  }
  // the tail laid along a path: each bone aimed at where the path is one bone-length on (pts: mesh-space points from the tail's root on);
  // its ventral side kept toward `down`
  tailAlong(which, out, pts, down) {
    const P = this.P, ch = this.chain.tail; const M = P.m[which];
    // cumulative path lengths
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + pts[i].distanceTo(pts[i - 1]));
    const at = (s, o) => { s = Math.max(0, Math.min(cum[cum.length - 1], s)); let i = 1; while (i < cum.length - 1 && cum[i] < s) i++; const u = (s - cum[i - 1]) / Math.max(1e-6, cum[i] - cum[i - 1]); return o.copy(pts[i - 1]).lerp(pts[i], u); };
    let s = 0;
    for (let k = 0; k < ch.length; k++) {
      const pos = P.fk(which, out), j = ch[k], L = k + 1 < ch.length ? M.rest[ch[k + 1]].distanceTo(M.rest[j]) : M.end[j].distanceTo(M.rest[j]);
      // where this joint sits along the path (projected), then aim one bone length on
      s = k === 0 ? 0 : s + (k < ch.length ? M.rest[j].distanceTo(M.rest[ch[k - 1]]) : 0);
      at(s + L, _v4); P.aimMin(out, j, _v.copy(_v4).sub(pos[j]));   // shortest arc: the tail never twists over (down: unused)
    }
  }
  // ---------------- STAND IDLE ----------------
  standIdle(t, out, amp = 1) {
    const I = this.I; out.identity(); out.root.copy(this.standRoot);
    const br = Math.sin(t * 2.0) * amp, sway = Math.sin(t * 0.6) * amp, sway2 = Math.sin(t * 0.6 + 1.1) * amp;
    out.root.y += -0.004 + br * 0.004; out.root.x += sway * 0.01;
    rot(out, I.hips, 0, 0, sway * 1.2); rot(out, I.spine, br * 0.8, 0, -sway * 1.0); rot(out, I.spine1, br * 0.9, sway2 * 1.5, 0); rot(out, I.chest, br * 1.3, 0, -sway * 0.6); rot(out, I.neck, -br * 1.0, 0, 0);
    rot(out, I.head, -1, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      rot(out, I['upperarm.' + s], 3 + br * 1.2, 0, 5 * m); rot(out, I['forearm.' + s], 10 + br * 1.5, 0, 0); rot(out, I['hand.' + s], 4, 0, 0);
      rot(out, I['thigh.' + s], 0, 0, sway * 1.2 * m); }
    this.tailWave(t * 1.3, 4 * amp, 0.9, 0); this.digits(out, 0.12 + br * 0.04, 0.35, 0.05); this.plantStandFeet(out, 0); this.tailFree = 1; this.neck.amt = 1;
    return out;
  }
  plantStandFeet(out, lift, w = 1) { for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; out.contact('foot.' + s, _v.copy(this.standFeet[s]).setY(this.H.standFoot + lift), _v2.copy(this.standFootFwd[s]), _v3.set(0.0 * m, 0, 1), w); } }
  // ---------------- CRAWL ----------------
  crawl(t, out, dt, speed = 1) {
    const I = this.I; out.copy(this.LS); out.contacts = {}; const on = smooth(clamp01((this.t - (this.stT || 0)) / 0.6)); speed *= (0.15 + 0.85 * this.speedS) * on;
    // the body bends into a turn and swings with the gait about the vertical (each spine bone's own swing axis tilts with the back: about it
    // the swing would also roll the chest and the head)
    const tn = this.turnS; for (let k = 0; k < 5; k++) this.worldTurn(out, this.chain.spine[k], tn * 5, 0);
    this.gait += dt * speed * 2 * Math.PI * 1.1; const ph = this.gait; this.groundSpeed = this.stride * 1.1 * speed;
    const sp = this.chain.spine, amps = [-5, 4, 7, 3, 1.5]; let sway = 0;
    for (let k = 0; k < sp.length; k++) { const a = amps[k] * Math.sin(ph - k * 0.55 - 0.3) * speed; this.worldTurn(out, sp[k], -a, 0); sway += a; }
    this.worldTurn(out, I.head, tn * 12 + 0.7 * sway, 0);   // the head leads the turn and steadies its gaze against the body's sway (as a salamander's does), about the vertical
    rot(out, I.head, 2 + Math.sin(ph * 2) * 1.2 * speed, 0, 0);
    out.root.x += Math.sin(ph - 0.3) * 0.03 * speed; out.root.y += Math.sin(ph * 2 + 0.9) * 0.008 * speed;
    const limbs = [['hand.L', 0, 1, 1], ['hand.R', Math.PI, -1, 1], ['foot.R', 0, -1, 0], ['foot.L', Math.PI, 1, 0]];
    for (const [en, off, m, isArm] of limbs) {
      const u = ((ph + off) / (2 * Math.PI)) % 1, base = isArm ? this.crawlHand : this.crawlFoot, h = isArm ? this.H.crawlHand : this.H.crawlFoot, S = this.stride * speed;
      let z, y, lift = 0; const D = 0.6;
      if (u < D) { z = base.z + S / 2 - S * (u / D); y = h; }
      else { const s = (u - D) / (1 - D), s2 = s * s, s3 = s2 * s, mt = -S * (1 - D) / D;
        z = base.z + (2 * s3 - 3 * s2 + 1) * (-S / 2) + (s3 - 2 * s2 + s) * mt + (-2 * s3 + 3 * s2) * (S / 2) + (s3 - s2) * mt;
        lift = Math.pow(Math.sin(s * Math.PI), 2); y = h + 0.04 * lift * Math.min(1, speed * 1.5); }
      const LB = this.limbBind[isArm ? 'arm' : 'leg']; const fwd = _v2.set(LB.fwd.x * m, -0.3 * lift, LB.fwd.z), pole = _v3.set(LB.pole.x * m, LB.pole.y, LB.pole.z);
      out.contact(en, _v.set(base.x * m, y, z), fwd, pole, 1);
      const dig = this.chain[isArm ? 'fingers' : 'toes'][m > 0 ? 0 : 1]; dig.forEach((f, k) => { rot(out, f[0], 4 + lift * 14, 0, (k - 1.5) * 5 * m); rot(out, f[1], 3 + lift * 10, 0, 0); });
    }
    this.tailWave(ph - 2.0, (10 * speed + 2) * on, 0.7, 0); this.tailFree = 1; this.neck.amt = 0.7;
    return out;
  }
  // crawl rest with all four limbs planted at their gait centres
  proneCrawl(out) {
    out.copy(this.LS); out.contacts = {}; this.tailWave(0, 0, 1, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const A_ = this.limbBind.arm, L_ = this.limbBind.leg;
      out.contact('hand.' + s, _v.set(this.crawlHand.x * m, this.H.crawlHand, this.crawlHand.z), _v2.set(A_.fwd.x * m, 0, A_.fwd.z), _v3.set(A_.pole.x * m, A_.pole.y, A_.pole.z), 1);
      out.contact('foot.' + s, _v.set(this.crawlFoot.x * m, this.H.crawlFoot, this.crawlFoot.z), _v2.set(L_.fwd.x * m, 0, L_.fwd.z), _v3.set(L_.pole.x * m, L_.pole.y, L_.pole.z), 1); }
    this.digits(out, 0.08, 0.3, 0.08); return out;
  }
  // ---------------- POWER POSE: akimbo ----------------
  powerPose(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.5); const br = Math.sin(t * 2.0);
    rot(out, I.spine, -5, 0, 0); rot(out, I.chest, -7 + br * 0.6, 0, 0); rot(out, I.neck, 2, 0, 0); rot(out, I.head, -9, 0, 0);
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      A('upperarm.' + s, [0.7 * m, -0.68, -0.15], [-m, 0, 0.6]); A('forearm.' + s, [-0.35 * m, -0.55, 0.55], [-m, 0, 0.6]); A('hand.' + s, [-0.3 * m, -0.8, 0.4], [-0.9 * m, -0.3, 0.2]);
      rot(out, I['thigh.' + s], 4, 0, 10 * m); rot(out, I['shin.' + s], 6, 0, 0); rot(out, I['foot.' + s], -5, 0, 0); }
    out.root.x = 0; out.root.y -= 0.025; this.digits(out, 0.9, 0.0, 0.1); this.tailWave(t * 1.6, 5, 0.8, 0); this.plantStandFeet(out, 0); this.neck.amt = 0.6;
    return out;
  }
  // ---------------- JETPACK: hanging from the pack, arms down along the sides, fists, looking down at the ground, tail hanging straight down ----------------
  jetpack(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.4); out.contacts = {}; const w = Math.sin(t * 3.0), w2 = Math.sin(t * 2.3 + 1);
    out.root.y += 0.5 + w2 * 0.03; out.root.x += Math.sin(t * 1.1) * 0.015;
    rot(out, I.hips, -6, 0, w2 * 2); rot(out, I.spine, -2, 0, 0); rot(out, I.chest, 6, 0, 0); rot(out, I.neck, 20, 0, 0); rot(out, I.head, 26 + w * 1.5, w * 2, 0);   // looking down at the ground
    this.eyeBias = [0, -0.16];
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const ws = s === 'L' ? w : -w;
      // arms straight down along the sides, a hair out and back, the fists by the thighs, knuckles out
      A('upperarm.' + s, [0.22 * m, -0.97, -0.08], [-0.2 * m, 0, 1]); A('forearm.' + s, [0.12 * m, -0.98, 0.1 + ws * 0.02], [-0.2 * m, 0, 1]); A('hand.' + s, [0.06 * m, -1, 0.06], [-m, 0, 0.1]);
      setRot(out, I['thigh.' + s], 18 + ws * 4, 0, 6 * m); setRot(out, I['shin.' + s], 36 + ws * 6, 0, 0); setRot(out, I['foot.' + s], 24 + ws * 4, 0, 0); }
    this.fists(out, 1); this.digits(out, 0, 0, 0.35, 0.2);
    // the tail hanging straight down from the hips, a slight curl back at the tip
    // (an arc turning the tail from back to straight down over 0.3 m, then hanging)
    this.tailAlong('stand', out, this.arcPath('stand', out, 1.45, 0.3, 1.0), null);
    this.tailWave(t * 2.4, 1.5, 1.0, 0); this.tailFree = 0.35; this.neck.amt = 0.4;
    return out;
  }
  // ---------------- GROUND-POUND WIND-UP: a tucked cannonball in the air: knees up, arms tucked down the sides with fists by the hips (never
  // in front of the face), the gills folded back and in against the head, the tail tucked down under the groin between the legs ----------------
  groundPound(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.3); out.contacts = {}; const sh = Math.sin(t * 16) * 0.5;
    out.root.y += 0.42 + 0.02 * Math.sin(t * 2.2);
    rot(out, I.hips, 12, 0, 0); rot(out, I.spine, 10, 0, 0); rot(out, I.chest, 6, 0, 0); rot(out, I.neck, 8, 0, 0); rot(out, I.head, 10 + sh * 0.6, 0, 0);   // hunched, eyes on the target below
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      A('upperarm.' + s, [0.38 * m, -0.85, -0.3], [-0.3 * m, 0, 1]); A('forearm.' + s, [0.16 * m, -0.35, 0.92], [-0.2 * m, -1, 0.1]); A('hand.' + s, [0.0, -0.5, 0.85], [-m, -0.2, 0]);
      setRot(out, I['thigh.' + s], 72, 0, 16 * m); setRot(out, I['shin.' + s], 104, 0, 0); setRot(out, I['foot.' + s], 22, 0, 0); }
    this.fists(out, 1); this.digits(out, 0, 0, 0.5, 0.1);
    // gills: folded back along the head and in toward it, like ears pinned back: each stalk turned (shortest arc, so it never twists) from
    // where it points toward the back of the head, a little inward and down the stack
    { const Fp = P.frames(out), Fh = Fp[I.head].clone(), fwd = new THREE.Vector3(0, 0, 1).applyQuaternion(Fh), M = P.m.stand, hc = new THREE.Vector3();
      { const pos = P.fk('stand', out); hc.fromArray(M.meta.face.c).sub(M.rest[I.head]).applyQuaternion(_q.copy(Fh).multiply(_q2.copy(M.F[I.head]).invert())).add(pos[I.head]); }
      for (const s of ['L', 'R']) for (let k = 0; k < 3; k++) {
        const g1 = I[`gill${k}.${s}.1`], g2 = I[`gill${k}.${s}.2`]; let pos = P.fk('stand', out);
        // back and a little down along the skull from the root, pinned flat like a cat's ears: the way back mixes the head's own back-and-down
        // with straight back in the world (the head is pitched down at the target: the head's back alone would stand the gills up), made
        // tangent to the skull at the root and pulled into it; the outer half bends on along the skull (tangent at its own joint, pulled in)
        const up = _v4.set(0, 1, 0).applyQuaternion(Fh), n = _v3.copy(pos[g1]).sub(hc).normalize();
        const b = _v.copy(fwd).multiplyScalar(-0.3).addScaledVector(up, -0.25).add(_v2.set(0, -0.4, -1).normalize().multiplyScalar(0.6));
        b.addScaledVector(n, -n.dot(b)).normalize().addScaledVector(n, -0.33).normalize();
        const cur = _v2.copy(pos[g2]).sub(pos[g1]).normalize(), fk = [0.9, 0.85, 0.72][k]; b.multiplyScalar(fk).addScaledVector(cur, 1 - fk).normalize();
        P.aimMin(out, g1, b); pos = P.fk('stand', out);
        const n2 = _v3.copy(pos[g2]).sub(hc).normalize(), b2 = _v2.copy(b); b2.addScaledVector(n2, -n2.dot(b2)).normalize().addScaledVector(n2, -0.3).normalize();
        P.aimMin(out, g2, b2); } }
    // the tail tucked: down behind the seat, forward under the groin between the legs, the tip curling up in front (a smooth curve through
    // points set from the hips and the feet, so it follows the pose)
    { const pos = P.fk('stand', out), r = pos[this.chain.tail[0]], hp = pos[I.hips], fy = 0.5 * (pos[I['foot.L']].y + pos[I['foot.R']].y), fz = 0.5 * (pos[I['foot.L']].z + pos[I['foot.R']].z);
      const V = (y, z) => new THREE.Vector3(0, y, z);
      const K = [r.clone(), V(r.y - 0.2, r.z - 0.05), V(fy, 0.5 * (r.z + hp.z) - 0.06), V(fy - 0.05, hp.z + 0.05), V(fy + 0.01, fz + 0.2), V(fy + 0.18, fz + 0.33), V(fy + 0.36, fz + 0.38)];
      this.tailAlong('stand', out, catmull(K, 6), null); }
    this.tailWave(t * 3, 1, 1, 0); this.tailFree = 0.2; this.neck.amt = 0.25; this.gillHold = 1;
    return out;
  }
  // ---------------- VICTORY: hops (a smooth sin^2 arc: no instant change of speed at the ground), both arms thrown up ----------------
  victory(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.5); const T = (t * 1.6) % 1; const hop = Math.pow(Math.sin(T * Math.PI), 2); const pump = Math.sin(t * 1.6 * Math.PI * 2);
    out.root.y += hop * 0.14; out.root.x = 0;
    rot(out, I.spine, -3 - hop * 3, 0, 0); rot(out, I.chest, -4, 0, 0); rot(out, I.head, -12 + hop * 5, 0, Math.sin(t * 3) * 5);
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const pm = s === 'L' ? pump : -pump;
      A('upperarm.' + s, [0.75 * m, 0.35 + pm * 0.1, 0.55], [-m, 0.3, 0.3]); A('forearm.' + s, [0.6 * m, 0.65 + pm * 0.12, 0.45], [-m, 0.2, 0.2]); A('hand.' + s, [0.55 * m, 0.75, 0.38], [-m, 0, 0]);
      rot(out, I['thigh.' + s], hop * 20, 0, 5 * m); rot(out, I['shin.' + s], hop * 35, 0, 0); rot(out, I['foot.' + s], hop * 16, 0, 0); }
    this.tailWave(t * 6, 7, 0.9, 0); this.digits(out, 0.1, 0.6, 0.1); { const x = Math.min(1, hop / 0.9); this.plantStandFeet(out, 0, 1 - x * x * x * (10 - 15 * x + 6 * x * x)); }   // the feet let go / take hold gradually over the hop (a quintic) this.neck.amt = 0.4;
    return out;
  }
  // ---------------- CROUCH: low on all fours, palms flat on the floor in front of the shoulders, feet planted where they stand, head up
  // looking ahead, the tail curving down to lie along the floor behind. It is also the stand's half of the stand <-> crawl swap ----------------
  crouch(out, k = 1, cw = 1, which = 'stand') {
    const I = this.I, P = this.P, C = this.CR; out.identity(); out.root.copy(this.standRoot);
    rot(out, I.hips, C.hips * k, 0, 0); rot(out, I.spine, C.spine * k, 0, 0); rot(out, I.spine1, C.spine1 * k, 0, 0); rot(out, I.chest, C.chest * k, 0, 0); rot(out, I.neck, C.neck * k, 0, 0); rot(out, I.head, C.head * k, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      setRot(out, I['thigh.' + s], C.thigh[0] * k, 0, C.thigh[1] * m * k); setRot(out, I['shin.' + s], C.shin * k, 0, 0); setRot(out, I['foot.' + s], C.foot * k, 0, 0);
      setRot(out, I['upperarm.' + s], C.arm[0] * k, 0, C.arm[1] * m * k); setRot(out, I['forearm.' + s], C.fore * k, 0, 0); setRot(out, I['hand.' + s], C.hand * k, 0, 0); }
    this.digits(out, 0.04, 0.45, 0.06);
    // placed so the head is over C.headZ and the designed knee bend puts the ankles on the floor (each mesh by its own legs)
    { const p0 = P.fk(which, out), ay = 0.5 * (p0[I['foot.L']].y + p0[I['foot.R']].y), hz = p0[I.head].z;
      out.root.y += (this.H[which === 'crawl' ? 'crawlFoot' : 'standFoot'] - ay) * k; out.root.z += (C.headZ - hz) * k; }
    const pos = P.fk(which, out);
    // the tail: from its root, curving down to touch the floor about a third of a metre back, then lying along it, its tip lifting a little
    { const r = pos[this.chain.tail[0]].clone(), hp = pos[I.hips]; const bk = _v4.copy(r).sub(hp).setY(0); if (bk.lengthSq() < 1e-6) bk.set(0, 0, -1); bk.normalize();
      const g = 0.045 * k + r.y * (1 - k), q = (a, h) => r.clone().addScaledVector(bk, a).setY(r.y + (h - r.y) * k);
      const pts = [r, q(0.12, r.y - 0.06), q(0.26, Math.max(g, r.y * 0.35)), q(0.42, g), q(0.7, g), q(1.0, g + 0.01), q(1.3, g + 0.05)];
      this.tailAlong(which, out, pts, _v3.set(0, -1, 0)); }
    this.tailWave(0, 0, 1, 0); this.tailFree = 0.15 + 0.85 * (1 - k); this.neck.amt = 0.6;
    // contacts: the hands forward-out of the shoulders, palms flat; the feet where the standing feet are, a little wider
    const p2 = P.fk(which, out);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const sh = p2[I['upperarm.' + s]];
      out.contact('hand.' + s, _v.set(sh.x + C.handOut * m, this.H.standHand, sh.z + C.handFwd), _v2.set(0.25 * m, 0, 1), _v3.set(0.7 * m, 0.1, -1), cw);
      out.contact('foot.' + s, _v.copy(this.standFeet[s]).setY(this.H.standFoot).setX(this.standFeet[s].x + C.footOut * m).setZ(this.standFeet[s].z + C.footZ), _v2.copy(this.standFootFwd[s]), _v3.set(0.45 * m, 0.1, 1), 1); }
    return out;
  }
  // ---------------- GATHERED (the crawl's half of the swap): the crawl rest with the front pushed up on straighter arms, the head up where the
  // crouching stand's head is, the hind feet drawn in under the hips, hands and feet planted ----------------
  gather(out) {
    const I = this.I, P = this.P, G = this.GA; out.copy(this.LS); out.contacts = {};
    rot(out, I.spine1, G.spine1, 0, 0); rot(out, I.chest, G.chest, 0, 0); rot(out, I.neck, G.neck, 0, 0); rot(out, I.head, G.head, 0, 0);
    this.digits(out, 0.06, 0.35, 0.06); this.tailWave(0, 0, 1, 0); this.tailFree = 0.6; this.neck.amt = 0.6;
    { const p0 = P.fk('crawl', out); out.root.z += this.CR.headZ - p0[I.head].z; }
    const A_ = this.limbBind.arm, L_ = this.limbBind.leg;
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      out.contact('hand.' + s, _v.set(this.crawlHand.x * m + G.handOut * m, this.H.crawlHand, this.crawlHand.z + G.handFwd), _v2.set(A_.fwd.x * m, 0, A_.fwd.z), _v3.set(A_.pole.x * m, A_.pole.y, A_.pole.z), 1);
      out.contact('foot.' + s, _v.set(this.crawlFoot.x * m, this.H.crawlFoot, this.crawlFoot.z + G.footZ), _v2.set(L_.fwd.x * m, 0, L_.fwd.z), _v3.set(L_.pole.x * m, L_.pole.y, L_.pole.z), 1); }
    return out;
  }
  armTest(state, out) {
    const I = this.I; out.identity(); out.root.copy(this.standRoot); this.plantStandFeet(out, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const d = state === 'armsfwd' ? [0.15 * m, 0.05, 1] : state === 'armsside' ? [m, 0.05, 0] : [0.25 * m, 1, 0.1];
      this.P.aim(out, I['upperarm.' + s], _v.set(...d), _v2.set(0, -1, 0.3), false); this.P.aim(out, I['forearm.' + s], _v.set(...d), _v2.set(0, -1, 0.3), false); }
    return out;
  }
  // ---------------- TRANSITIONS ----------------
  // stand -> crawl (crawl -> stand runs the same steps the other way):
  //  fold   the stand mesh is carried (inertialized) into the crouch, hands down on the floor;
  //  morph  the crawl mesh, in its own half of that shared pose (gathered: front pushed up, head where the crouching head is), and the stand
  //         mesh both ride one skeleton blended from the stand's to the crawl's (Puppet.applyMix): the body lengthens, the hind legs kick
  //         back in a low arc to where the crawl's feet go, and a complementary dither swaps the two bodies while they coincide; a jelly
  //         squash pulse as the hands take the weight (a stretch on the way up);
  //  settle the crawl mesh, on its own skeleton and owning the pose, is carried (inertialized) from the gathered pose into its gait.
  updateTransition(dt, out) {
    const T = this.trans, TT = this.TT; T.t += dt; const toCrawl = T.kind === 'standToCrawl', src = toCrawl ? 'stand' : 'crawl', dst = toCrawl ? 'crawl' : 'stand';
    const mEnd = TT.M0 + TT.M;
    if (T.t < mEnd) {
      if (!T.a) { T.a = 1; this.startInertia(TT.A); }
      this.mesh = src; this.swapPose(src, out);
      if (T.t >= TT.M0) {
        if (!T.m) { T.m = 1; this.sqPush[0] += toCrawl ? 2.2 : -2.0; this.kickGills(0, toCrawl ? 0.5 : -0.4); this.oprev.copy(this.pose); this.oprev2.copy(this.pose); }
        const v = clamp01((T.t - TT.M0) / TT.M), u = smooth(v); this.mixU = toCrawl ? u : 1 - u;
        this.swapPose(dst, this.B);
        // the hind feet (and the hands, a little) travel from the source pose's spots to the destination's: both halves aim at the same point
        // on a low arc, so the blended skeleton carries them along it
        const s = smooth(clamp01((v - 0.08) / 0.8)), lift = Math.pow(Math.sin(Math.PI * s), 2);
        for (const en of ['foot.L', 'foot.R', 'hand.L', 'hand.R']) { const a = out.contacts[en], b = this.B.contacts[en]; if (!a || !b) continue;
          const h = en.startsWith('foot') ? 0.075 : 0.03; _v.copy(a.t).lerp(b.t, s); _v.y += h * lift; _v2.copy(a.fwd).lerp(b.fwd, s);
          a.t.copy(_v); b.t.copy(_v); a.fwd.copy(_v2); b.fwd.copy(_v2); }
        // the change-over itself is per body region, scheduled on u (look.js FADE_FS: the hips, legs and tail between u 0.18 and 0.44, the chest,
        // arms and head up to 0.56), both meshes drawn meanwhile; the shadow comes from one of them only (two coincident casters shadow each other)
        this.swap = { from: src, to: dst, u: this.mixU }; this.fade = 0.5;
      }
    } else {
      if (!T.c) { T.c = 1; this.mesh = dst; this.mixU = null; this.swap = null; this.fade = 1; this.prev.copy(this.oprev); this.prev2.copy(this.oprev2); this.hasPrev = 2; this.startInertia(TT.C); this.stT = this.t; }
      const st = toCrawl ? 'crawl' : T.target;
      if (T.t >= mEnd + TT.C) { this.trans = null; this.state = st; }
      this.evalStateOnset(st, out, dt);
    }
    return out;
  }
  // each mesh's half of the shared pose: the stand crouching, the crawl gathered
  swapPose(which, out) { return which === 'stand' ? this.crouch(out, 1, 1, 'stand') : this.gather(out); }
  // ---------------- GROUND CONTACT: two-bone IK per contact, blended by the contact weight ----------------
  ground(which, pose) {
    const P = this.P, I = this.I, C = pose.contacts; if (!C) return;
    for (const en in C) { const c = C[en]; if (!(c.w > 0)) continue;
      const side = en.slice(-1), isArm = en.startsWith('hand'); const up = I[(isArm ? 'upperarm.' : 'thigh.') + side], lo = I[(isArm ? 'forearm.' : 'shin.') + side], e = I[en];
      if (c.w < 1) { _s1.copy(pose.q[up]); _s2.copy(pose.q[lo]); _s3.copy(pose.q[e]); }
      P.ik2(which, pose, up, lo, e, c.t, c.pole, isArm ? -1 : 1);
      P.aim(pose, e, _v.copy(c.fwd).normalize(), _v2.set(0, -1, 0), false);
      if (c.w < 1) { pose.q[up].copy(_s1.slerp(pose.q[up], c.w)); pose.q[lo].copy(_s2.slerp(pose.q[lo], c.w)); pose.q[e].copy(_s3.slerp(pose.q[e], c.w)); }
    }
  }
  // ---------------- THE NECK'S LIFE: glances (the eyes lead, the head follows on a spring that overshoots a touch and settles), the game's
  // look, a slow drift of tilt, a bob with the breath, a lag behind the body's own movement; less of it in the tense poses ----------------
  stepNeck(dt) {
    const N = this.neck, amt = N.amt; if (!(dt > 0)) return;
    N.glanceT -= dt;
    if (N.glanceT <= 0) {
      if (N.holdT > 0 || Math.random() < 0.35) { N.glance = [0, 0, 0]; N.holdT = 0; N.glanceT = 1.8 + Math.random() * 3.5; }
      else { const big = Math.random() < 0.3; N.glance = [(Math.random() * 2 - 1) * (big ? 20 : 10), (Math.random() * 2 - 1) * 5 - 1, (Math.random() * 2 - 1) * 4]; N.holdT = 1; N.glanceT = 0.7 + Math.random() * 1.6; }
      // the eyes get there first (the face's look), and a glance often comes with a blink
      if (this.look2) { this.look2.att.eye[0] = N.glance[0] / 90 * 0.45; this.look2.att.eye[1] = -N.glance[1] / 50 * 0.25; this.look2.att.t = N.glanceT + 0.2; if (Math.random() < 0.4) this.look2.blinkK = Math.max(this.look2.blinkK, 0.1); }
    }
    const t = this.t, drift = [Math.sin(t * 0.37) * 1.4 + Math.sin(t * 0.91 + 1.3) * 0.6, Math.sin(t * 0.29 + 2.1) * 1.1, Math.sin(t * 0.43 + 0.7) * 1.6 + Math.sin(t * 1.13) * 0.5];
    const br = (this.breath - 0.5) * (0.8 + 0.8 * this.exertS);
    const tgt = [(N.glance[0] + drift[0]) * amt + this.look.yaw * 0.6, (N.glance[1] + drift[1]) * amt + br * 1.2 + this.look.pitch * 0.6, (N.glance[2] + drift[2]) * amt + (this.look.roll || 0) * 0.6];
    // the body's acceleration pushes the head back (it lags, then catches up past where it was and settles)
    tgt[1] += this.accS.z * 2.2 * amt; tgt[0] += this.accS.x * 3 * amt;
    const k = 38, c = 9, h = Math.min(dt, 1 / 30);
    for (let i = 0; i < 3; i++) { const a = k * (tgt[i] - N.x[i]) - c * N.v[i]; N.v[i] += a * h; N.x[i] += N.v[i] * h; }
    if (this.look2) this.look2.turnRate(N.v[0] * DEG);
    // throat pumps: two or three quick swallows of water every few seconds, mostly when still
    N.thrT -= dt * (this.speedS < 0.2 || this.state !== 'crawl' ? 1 : 0.35);
    if (N.thrT <= 0) { N.thrT = 3.5 + Math.random() * 4.5; N.thrN = 2 + (Math.random() < 0.5 ? 1 : 0); N.thrU = 0; }
    let thr = 0; if (N.thrN > 0) { N.thrU += dt / 0.3; const u = N.thrU % 1; thr = Math.pow(Math.sin(u * Math.PI), 2); if (N.thrU >= N.thrN) N.thrN = 0; }
    this.throatK = thr * amt;
  }
  // 60% in the head, 40% in the neck (the head never just swivels on a stiff neck); pitch: positive looks up
  // (pitch about the hinge, which is level in both bodies; yaw about the world's vertical and roll about the world's forward, so the crawl's
  // tilted neck turns the head the way the stand's upright one does instead of rolling it)
  applyNeck(pose) { const N = this.neck, I = this.I; rot(pose, I.neck, -N.x[1] * 0.4, 0, 0); rot(pose, I.head, -N.x[1] * 0.6, 0, 0); this.worldTurn(pose, I.neck, N.x[0] * 0.4, N.x[2] * 0.35); this.worldTurn(pose, I.head, N.x[0] * 0.6, N.x[2] * 0.65); }
  // turn bone i by a yaw about the world's vertical and a roll about the world's forward (degrees), expressed in its own frame
  worldTurn(pose, i, yaw, roll) { if (!yaw && !roll) return; const F = _wF.copy(this.P.frames(pose)[i]).normalize(); _wE.set(0, yaw * DEG, roll * DEG, 'YZX'); _wq.setFromEuler(_wE); _wq2.copy(F).invert().multiply(_wq).multiply(F); pose.q[i].multiply(_wq2).normalize(); }
  // ---------------- SECONDARY MOTION ----------------
  stepSecondary(dt) {
    const tf = this.tf = this.tailFreeS.step(this.tailFree, dt);
    // the tail's flick: a smooth bump (sin^2 over 0.4 s) in where the outer tail wants to be, which the tail spring follows and overshoots
    this.flickT -= dt * (0.3 + this.speedS); if (this.flickT <= 0 && !this.flick) { this.flickT = 2.5 + Math.random() * 4; this.flick = { t: 0, T: 0.4, sgn: Math.random() < 0.5 ? -1 : 1 }; }
    const tt = this.tailTgt; tt.set(this.tailTarget);
    if (this.flick) { const F = this.flick; F.t += dt; const e = Math.pow(Math.sin(Math.PI * Math.min(1, F.t / F.T)), 2); for (let k = 2; k < 6; k++) tt[k * 2] += F.sgn * (5 + 4 * (k - 2)) * e * tf; if (F.t >= F.T) this.flick = null; }
    { const f = Math.min(1, dt / 0.045);
      for (let k = 0; k < 12; k++) { let a = this.tailPush[k] * f; this.tailPush[k] -= a; this.tailPush2[k] += a; a = this.tailPush2[k] * f; this.tailPush2[k] -= a; this.tailSpring.v[k] += a;
        let g = this.gillPush[k] * f; this.gillPush[k] -= g; this.gillPush2[k] += g; g = this.gillPush2[k] * f; this.gillPush2[k] -= g; this.gillSpring.v[k] += g; } }
    this.tailLat = -this.rootVel.x * 40 - this.turnS * this.speedS * 18 - this.accS.x * 4;
    this.tl = this.tailSpring.step(tt, dt);
    // breathing: the chest / belly expand (jelly layer) and the chest bone lifts a little; faster and deeper with exertion
    const rate = 1.9 + 2.6 * this.exertS + 0.6 * this.speedS; this.breathPh += dt * rate; this.breath = 0.5 + 0.5 * Math.sin(this.breathPh);
    const g = this.chain.gills, vel = this.headVelS;
    for (let j = 0; j < 6; j++) {
      const i1 = g[j * 2]; _q.copy(this.P.Fp[i1]).invert(); _v.copy(vel).applyQuaternion(_q);
      const jj = j % 3, flutter = Math.sin(this.t * 2.3 + jj * 0.6 + (j < 3 ? 0 : 1.9)) * 2.0 + Math.sin(this.t * 3.7 + jj * 0.5 + (j < 3 ? 0 : 0.7)) * 1.0;
      const cl = x => 16 * Math.tanh(x / 16);   // a soft limit: the drag saturates instead of clipping
      const sgn = j < 3 ? 1 : -1; this.gillTarget[j * 2] = cl(flutter - _v.z * 15 - this.accS.z * 6); this.gillTarget[j * 2 + 1] = cl(-_v.x * 15 - this.accS.x * 5 * sgn);
    }
    // the top and middle stalks grow from one base (fused): they move mostly together, so the frond between them is never torn
    for (const o of [0, 6]) for (let c = 0; c < 2; c++) { const t0 = this.gillTarget[o + c], t1 = this.gillTarget[o + 2 + c], m = 0.5 * (t0 + t1); this.gillTarget[o + c] = m + 0.3 * (t0 - m); this.gillTarget[o + 2 + c] = m + 0.3 * (t1 - m); }
    this.gs = this.gillSpring.step(this.gillTarget, dt);
    { const T = this.trans, pound = this.state === 'pound' || (T && T.target === 'pound' && T.c); this.gillHoldS = (this.gillHoldF || (this.gillHoldF = new Follow(6, 1))).step(pound ? 0.25 : 1, dt); }
  }
  // the secondary motion on a pose (of either mesh): tail swing, breathing, gill stalks; then the joint limits (stand poses relative to the
  // stand rest, crawl poses relative to the symmetric crawl rest)
  applySecondary(pose, which) {
    const I = this.I, tf = this.tf, tl = this.tl, lat = this.tailLat;
    for (let k = 0; k < 6; k++) rot(pose, this.chain.tail[k], tl[k * 2 + 1] * tf, 0, (tl[k * 2] + lat * (0.25 + k * 0.15)) * tf);
    const g = this.chain.gills, gs = this.gs, hold = this.gillHoldS;
    const cm = hold, lo = 0.4;   // (one head in both states: the same gills, the same motion)
    const stalkAmp = [cm, 0.9 * cm, lo * cm, cm, 0.9 * cm, lo * cm];
    for (let j = 0; j < 6; j++) { const a = gs[j * 2] * stalkAmp[j], b = gs[j * 2 + 1] * stalkAmp[j]; rot(pose, g[j * 2], a * 0.55, 0, b * 0.55); rot(pose, g[j * 2 + 1], a * 0.7, 0, b * 0.7); }
  }
  kickGills(x, y) { const r = 0.85 + 0.15 * Math.random(); for (let j = 0; j < 6; j++) { const k = j % 3 === 2 ? 0.8 : 1; this.gillPush[j * 2] += y * 170 * r * k; this.gillPush[j * 2 + 1] += x * 170 * k; } }
  // the soft-body jelly layer and the swap's dissolve, written into the look's uniforms (both meshes share them)
  jelly(dt) {
    const L = this.look2; const h = Math.min(dt, 1 / 30);
    this.lagV.x += ((-this.accS.x * 0.02 - this.lagP.x) * 90 - this.lagV.x * 8) * h; this.lagV.z += ((-this.accS.z * 0.02 - this.lagP.z) * 90 - this.lagV.z * 8) * h; this.lagV.y += ((0 - this.lagP.y) * 110 - this.lagV.y * 9) * h;
    { const f = Math.min(1, h / 0.045); let a = this.sqPush[0] * f; this.sqPush[0] -= a; this.sqPush[1] += a; a = this.sqPush[1] * f; this.sqPush[1] -= a; this.sqV += a;
      a = this.lagPush[0] * f; this.lagPush[0] -= a; this.lagPush[1] += a; a = this.lagPush[1] * f; this.lagPush[1] -= a; this.lagV.y += a; }
    this.lagP.addScaledVector(this.lagV, h); const lim = 0.04, soft = (x, l) => l * Math.tanh(x / l); this.lagS = this.lagS || new THREE.Vector3(); this.lagS.set(soft(this.lagP.x, lim), soft(this.lagP.y, lim), soft(this.lagP.z, lim));
    this.sqV += ((0 - this.sq) * 150 - this.sqV * 9) * h; this.sq += this.sqV * h; const sqS = this.sq > 0 ? 0.22 * Math.tanh(this.sq / 0.22) : 0.2 * Math.tanh(this.sq / 0.2);
    const stretch = (this.stretchF || (this.stretchF = new Follow(22))).step(this.inAir ? -0.08 * Math.min(1, Math.abs(this.airV) / 3) : 0, dt);   // the in-air stretch eases in and out
    this.jellyRipple += ((this.speedS * 0.35 + this.landK * 0.6) * 0.004 - this.jellyRipple) * Math.min(1, dt * 6);
    if (!L) return;
    L.U.uJelly.value.set(0.018 * this.breath * (0.7 + 0.8 * this.exertS) + 0.006 * this.throatK, sqS * 0.9 + stretch, this.mesh === 'crawl' ? 0.9 : 1.6, this.jellyRipple);
    L.U.uLag.value.x = this.lagS.x; L.U.uLag.value.y = this.lagS.y; L.U.uLag.value.z = this.lagS.z;
    L.coatMixT = this.mesh === 'crawl' ? 0 : 1;
    if (L.setMorphSwap) { if (this.mixU !== null) L.setMorphSwap(this.mixU); else { L.setMorphSwap(null); L.setSwap(this.mesh, this.mesh === 'stand' ? 'crawl' : 'stand', 1); } }
    { const cs = this.mixU !== null ? (this.mixU < 0.37 ? 'stand' : 'crawl') : this.mesh; for (const w in this.P.m) this.P.m[w].mesh.castShadow = w === cs; }
    const eb = this.eyeB || (this.eyeB = [0, 0]); for (let k = 0; k < 2; k++) eb[k] += (this.eyeBias[k] - eb[k]) * Math.min(1, dt * 5);
    L.update(dt, [this.look.yaw / 90 * 0.3 + eb[0], this.look.pitch / -50 * 0.2 + eb[1]], sqS * 0.6 + stretch);
  }
  trackHead(dt) {
    const P = this.P; const h = P.jointWorld(this.mesh, 'head', _v2);
    // a change of mesh (the swap) moves the head joint and the root between two bodies: no velocity is taken across it (it is not motion)
    if (this.thMesh !== this.mesh) { this.thMesh = this.mesh; this.headPrev.copy(h); this.rootPrev.copy(this.pose.root); }
    if (dt > 0) { this.headVel.copy(h).sub(this.headPrev).divideScalar(dt); this.rootVel.copy(this.pose.root).sub(this.rootPrev).divideScalar(dt); }
    if (this.headVel.length() > 20) this.headVel.set(0, 0, 0);
    this.headVelS.lerp(this.headVel, 1 - Math.exp(-dt * 16)); this.headPrev.copy(h); this.rootPrev.copy(this.pose.root);
  }
}

// ---------------- v214: the crawl's life, measured against the ground (inserted into the animator by tools/mk_axo_embed.py) ----------------
// The game moves the body; this works out how the ground moves under it (motion.carry: where world-fixed points go in the body's space
// from one frame to the next) and walks on that ground:
//  - feet stay where they land: a planted hand or foot is carried with the ground, so it never slides, whatever the speed, the turn or a
//    bump; each limb lands where the ground will bring it back under its shoulder or hip half way through its stance;
//  - the stride and its rate come from the speed (a slow creep with long deliberate steps up to a lizard's scurry at full tilt, the time
//    on the ground shrinking as it goes faster), and the body throws a salamander's S-wave into it: the shoulders and hips swing against
//    each other with each pair of steps, the head held steady against it, the tail carrying the wave on;
//  - turns: the body bends round the curve it runs on, the head leads into the turn and leans with it, on a spring, so it swings back
//    past straight and settles when the turn ends;
//  - stopped, it breathes and now and then moves a foot that was left stretched out;
//  - a jump: the planted limbs push the body off (they hold the ground as it rises until they are straight), tuck back as it rises, then
//    reach down for the ground as it comes up; one hand takes the landing, the others come down after it, the body dipping onto it;
//  - curled (the slingshot's long pull, the roll, the pound's tuck): the spine rolls up nose to tail, the limbs tuck in, the gills fold.
{
const LV1 = new THREE.Vector3(), LV2 = new THREE.Vector3(), LV3 = new THREE.Vector3(), LV4 = new THREE.Vector3(), LQ = new THREE.Quaternion();
const LIMB = [{ en: 'hand.L', off: 0, m: 1, arm: true }, { en: 'foot.R', off: 0.04, m: -1, arm: false }, { en: 'hand.R', off: 0.5, m: -1, arm: true }, { en: 'foot.L', off: 0.54, m: 1, arm: false }];
// homes (where each hand / foot sits under its shoulder / hip), how far one may be from it, the longest stride, the fastest steps
// (the crawl's hind legs are short, a quarter of a metre hip to ankle, against nearly half a metre of arm: their feet sweep less and
// spend less of each step on the ground, so at speed they kick through quickly while the hands take long reaching strides)
const GAIT = { handX: 0.4, handZ: 0.035, footX: 0.29, footZ: -0.8, reachH: 0.27, reachF: 0.15, sweepF: 0.28, sMax: 0.54, fMax: 5.6, fMin: 1.7 };
const frac = x => x - Math.floor(x);
const SLITHER = { on: 4.4, off: 3.2, after: 0.45, T0: 1.75, T1: 1.4 }; // (T0 / T1: a stroke cycle's length in seconds, just up to speed / at full tilt)
// one stroke cycle, u from 0 to 1: both hands pull it forward (0 to 0.25: the hands sweep back along the ground, the feet kick back), it
// glides with everything along its sides (to 0.55), slows a touch and crawls two steps (a hand and the opposite foot, then the other
// pair, each reaching forward and taking hold), and pulls again. Each limb's marks through the cycle: [u, mark, swing (lifted over)]
const SWK = { arm: { F: [0.26, 0, 0.18, 0], G: [0.27, 0, 0.09, 0], M: [0.28, 0, 0.0, 0], B: [0.2, 0.012, -0.16, 0], T: [0.05, 0.045, -0.25, 1] }, // [out, up, along, tucked]
  leg: { F: [0.17, 0, 0.06, 0], M: [0.18, 0, -0.06, 0], B: [0.1, 0.02, -0.24, 0], T: [0.035, 0.035, -0.28, 1] } };
const SWT = { 'hand.R': [[0, 'M', 0, 1], [0.15, 'B', 0, 1], [0.25, 'T'], [0.55, 'T'], [0.68, 'F', 1], [1, 'M', 0, 1]], 'hand.L': [[0, 'G', 0, 1], [0.17, 'B', 0, 1], [0.27, 'T'], [0.7, 'T'], [0.83, 'F', 1], [1, 'G', 0, 1]],
  'foot.L': [[0, 'M', 0, 1], [0.14, 'B', 0, 1], [0.25, 'T'], [0.56, 'T'], [0.69, 'F', 1], [1, 'M', 0, 1]], 'foot.R': [[0, 'M', 0, 1], [0.14, 'B', 0, 1], [0.25, 'T'], [0.71, 'T'], [0.84, 'F', 1], [1, 'M', 0, 1]] };
const swTan = (k, K, j, c) => { const n = k.length - 1; if (!k[j][3]) return 0; // (a mark passed through: its pace from the marks either side, round the cycle's end)
  const jp = j > 0 ? j - 1 : n - 1, jn = j < n ? j + 1 : 1, up = j > 0 ? k[jp][0] : k[jp][0] - 1, un = j < n ? k[jn][0] : k[jn][0] + 1;
  return 0.85 * (K[k[jn][1]][c] - K[k[jp][1]][c]) / (un - up); };
const swMark = (en, u, arm, out) => { const k = SWT[en], K = SWK[arm ? 'arm' : 'leg']; let i = 0; while (i < k.length - 2 && u >= k[i + 1][0]) i++;
  const a = K[k[i][1]], b = K[k[i + 1][1]], d = k[i + 1][0] - k[i][0], x = clamp01((u - k[i][0]) / d), arc = k[i + 1][2] ? Math.sin(Math.PI * x) : 0;
  const x2 = x * x, x3 = x2 * x, h00 = 2 * x3 - 3 * x2 + 1, h10 = x3 - 2 * x2 + x, h01 = 3 * x2 - 2 * x3, h11 = x3 - x2;
  for (let j = 0; j < 4; j++) out[j] = h00 * a[j] + h10 * d * swTan(k, K, i, j) + h01 * b[j] + h11 * d * swTan(k, K, i + 1, j);
  out[3] = clamp01(out[3]); out[1] += (arm ? 0.05 : 0.035) * arc; out[4] = arc; return out; };
const spr = (s, target, k, c, dt) => { const h = Math.min(dt, 1 / 30); s.v += (k * (target - s.x) - c * s.v) * h; s.x += s.v * h; return s.x; };
// a pitch about the body's own sideways axis (positive: nose down), put in the bone's own frame
const AXX = new THREE.Vector3(1, 0, 0), LQ2 = new THREE.Quaternion(), LQ3 = new THREE.Quaternion();
Animator.prototype.pitchTurn = function (pose, i, a) { if (!a) return; const F = LQ2.copy(this.P.frames(pose)[i]).normalize(); LQ.setFromAxisAngle(AXX, a); LQ3.copy(F).invert().multiply(LQ).multiply(F); pose.q[i].multiply(LQ3).normalize(); };
Animator.prototype.initLoco = function () {
  const L = this.loco = { ph: 0, f: 0, v: 0, yr: 0, steer: 0, D: 0.65, S: 0.2, act: 0, air: false, airT: 0, lead: 1, landK: 0, still: 0, settle: null, ballK: 0, ballV: 0,
    ht: { x: 0, v: 0 }, bd: { x: 0, v: 0 }, vc: 0, bend: 0, dip: { x: 0, v: 0 }, dipR: { x: 0, v: 0 }, arch: { x: 0, v: 0 }, limbs: [] };
  for (const d of LIMB) {
    const home = new THREE.Vector3(d.arm ? GAIT.handX * d.m : GAIT.footX * d.m, d.arm ? this.H.crawlHand : this.H.crawlFoot, d.arm ? GAIT.handZ : GAIT.footZ);
    L.limbs.push(Object.assign({}, d, { home, p: home.clone(), p0: home.clone(), tgt: home.clone(), gv: new THREE.Vector3(), st: 'stance', lift: 0, held: false, root: this.I[(d.arm ? 'upperarm.' : 'thigh.') + d.en.slice(-1)], len: 0, hb: home.clone(), rr: new THREE.Vector3() }));
  }
  const R0 = this.P.m.crawl.rest, I = this.I; for (const l of L.limbs) { const s = l.en.slice(-1), a = I[(l.arm ? 'upperarm.' : 'thigh.') + s], b = I[(l.arm ? 'forearm.' : 'shin.') + s], c = I[l.en]; l.len = R0[a].distanceTo(R0[b]) + R0[b].distanceTo(R0[c]); }
  { const p0 = this.P.fk('crawl', this.LS); for (const l of L.limbs) l.rr.copy(p0[l.root]); }
  return L;
};
Animator.prototype.crawl = function (t, out, dt) {
  const I = this.I, P = this.P, M = this.motion, L = this.loco || this.initLoco(), C = M.carry || null, h = Math.max(dt, 1e-4), TR = M.terrain || null, gY = (x, z) => TR ? TR(x, z) : 0;
  out.copy(this.LS); out.contacts = {};
  const on = smooth(clamp01((this.t - (this.stT || 0)) / 0.6));
  // the ground's speed under each limb's home, and the body's turn rate (a world-fixed point turns the other way in the body's space)
  let vmax = 0; for (const l of L.limbs) { l.gv.copy(l.home); if (C) l.gv.applyMatrix4(C); l.gv.sub(l.home).divideScalar(h); l.gv.y = 0; vmax = Math.max(vmax, Math.hypot(l.gv.x, l.gv.z)); }
  const yr = C ? -Math.atan2(C.elements[8], C.elements[10]) / h : 0;
  let vc = 0; if (C) { LV1.set(0, 0, -0.4); LV2.copy(LV1).applyMatrix4(C).sub(LV1); vc = Math.hypot(LV2.x, LV2.z) / h; } L.vc += (Math.min(vc, 14) - L.vc) * Math.min(1, dt * 30);
  L.v += (Math.min(vmax, 14) - L.v) * Math.min(1, dt * 30); L.yr += ((Math.abs(yr) < 12 ? yr : 0) - L.yr) * Math.min(1, dt * 10); L.steer += ((M.steer || 0) - L.steer) * Math.min(1, dt * 10);
  const v = L.v, ball = L.ballK = (L.ballF || (L.ballF = new Follow(13))).step(clamp01(M.ball || 0), dt), air = !!M.air;
  // ---- the gait: the time on the ground shrinks and the stride lengthens with speed; the step rate is what keeps a planted foot still
  const Dt = 0.66 - 0.28 * smooth(clamp01(v / 6.5)), S = Math.min(GAIT.sMax, 0.24 + 0.08 * v); L.D += (Dt - L.D) * Math.min(1, dt * 6); L.S = S; const D = L.D;
  let f = v > 0.05 ? Math.min(GAIT.fMax, v * D / S) : 0;
  const swinging = L.limbs.some(l => l.st === 'swing'); if (!air && swinging && f < GAIT.fMin) f = GAIT.fMin;   // (a step under way is finished)
  if (air) f = 0; L.f += (f - L.f) * Math.min(1, dt * 30); L.ph += L.f * dt;
  L.act = smooth(clamp01((v - 0.05) / 0.9)) * on * (air ? 0 : 1);
  const act = L.act, liftH = 0.028 + 0.03 * clamp01(v / 5);
  // ---- at speed it swims along the ground: once it has crawled up to speed and held it a moment, it goes into strokes, a push then a
  // glide, again and again. The push: the arms sweep back, the body surges forward, the head dips into it. The glide: the arms and legs
  // lie along its sides like a swimmer's, fingers closed, the belly slides, a slow gentle wave runs down the body to the tail, which sways
  // slowly from side to side, and the head comes up, held to the way it's going. Slowing down, the limbs come back to the ground and the
  // crawl takes over again (never in the air, climbing, curled, or turned on the spot)
  const SL = L.sl || (L.sl = { k: 0, on: false, hold: 0, u: 0, m: new Float32Array(5), g: 0 });
  { const vc = L.vc, ok = !air && !TR && M.spin === undefined && !((M.climbCurl || 0) > 0) && !((M.ball || 0) > 0.05) && L.ballK < 0.05;
    if (ok && vc > SLITHER.on) SL.hold += dt; else if (!ok || vc < SLITHER.off) SL.hold = 0;
    const want = ok && (SL.on ? vc > SLITHER.off : SL.hold > SLITHER.after);
    if (want && !SL.on) { SL.on = true; if (SL.k < 0.05) SL.u = 0.86; } // (in from the crawl: it reaches forward and takes hold, then the first pull)
    else if (!want && SL.on && (!ok || vc < 1.5 || (SL.u > 0.58 && SL.u < 0.9))) SL.on = false; // (slowing: it swims on into its crawl steps, and the crawl takes over from there)
    SL.k += ((SL.on ? 1 : 0) - SL.k) * Math.min(1, dt * (SL.on ? 3.6 : 4.2)); }
  const sl = L.slK = smooth(SL.k);
  // ---- the body's line (worked out before the limbs: they step from where it carries the shoulders and hips). A salamander's standing
  // wave: the shoulders and hips swing against each other with each pair of steps, the trunk bowing one way then the other, the tail
  // answering it in an S, the head kept steadier. Round a turn the whole body bends into a C: the trunk takes most of it, the neck and
  // head carry the curve on (never a kink at the neck), the tail follows it round; on a spring, so it eases in and swings back past straight
  const sp = this.chain.spine, c1 = Math.cos(2 * Math.PI * L.ph);
  const kap = L.yr / Math.max(L.vc, 1.3), spun = M.spin !== undefined, bend = L.bend = spr(L.bd, (spun ? 66 * Math.tanh(M.spin / 1.9) : Math.max(-64, Math.min(64, kap * 90))) * on, spun ? 48 : 55, spun ? 10 : 11, dt);
  L.tlg = spr(L.tg || (L.tg = { x: 0, v: 0 }), bend, 24, 4, dt);   // (the tail's own lag round a turn: it trails, then swings back past)
  const amp = (12 + 28 * clamp01(v / 6.5)) * act * (1 - sl) * (1 - 0.7 * Math.min(1, Math.abs(bend) / 64)), Ap = 0.4 * amp, As = 0.6 * amp, hs = As * c1 * (1 - Math.min(1, Math.abs(bend) / 64));
  const HT = spr(L.ht, (L.steer * 10 + Math.max(-8, Math.min(8, L.yr * 3))) * on, 75, 10, dt);
  const bU = bend * (1 - 0.6 * sl), T = 50 * Math.tanh((-amp * c1 + bU * 0.92 + HT * 0.45 * (1 - 0.5 * sl)) / 50);
  this.worldTurn(out, I.hips, Ap * c1, 0);
  this.worldTurn(out, sp[1], T * 0.34, 0);
  this.worldTurn(out, sp[2], T * 0.37, -L.steer * 3 * act);
  this.worldTurn(out, sp[3], T * 0.29, 0);
  this.worldTurn(out, I.neck, hs * 0.25 + bU * 0.1 + HT * 0.3 * (1 - 0.5 * sl), -HT * 0.12);
  this.worldTurn(out, I.head, hs * 0.25 + bU * 0.07 + HT * 0.25 * (1 - 0.5 * sl), -HT * 0.3);
  if (sl > 0.001) {
    const vk = clamp01((L.vc - SLITHER.on) / 3.6), u = SL.u = (SL.u + dt / (SLITHER.T0 + (SLITHER.T1 - SLITHER.T0) * vk)) % 1;
    // how far into the glide it is (the limbs' tuck, all four averaged): the wave is fullest there, smaller through the steps and the pull
    let g = 0; for (const l of L.limbs) g += swMark(l.en, u, l.arm, SL.m)[3] * 0.25; SL.g = g;
    // the wave: the lower and middle trunk and the tail swing most, the chest hardly, the head held to the way it's going. Each part's own
    // heading (degrees) along a wave running back from the shoulders to the tail tip, two to a cycle; each joint turns by the difference
    const th = 4 * Math.PI * u, env = sl * (0.5 + 0.5 * g), AB = [[I.head, 0.4], [I.neck, 0.8], [sp[3], 2], [sp[2], 5.5], [sp[1], 10], [I.hips, 14]];
    const hd = k => Math.sin(th - k * 0.55);
    { let up = AB[AB.length - 1][1] * env * hd(AB.length - 1); for (let k = AB.length - 2; k >= 0; k--) { const a = AB[k][1] * env * hd(k); this.worldTurn(out, AB[k][0], a - up, 0); up = a; } }
    // (the hips are the root, so the wave would swing the whole front about them: the body slides sideways against it instead, the head
    // kept on its line, the hips and the tail swaying under it, as a swimmer's do)
    { const pw = P.fk('crawl', out); out.root.x -= pw[I.neck].x * 0.88 * sl; }
    // round a turn, the bend low in the trunk (the tail takes it on in a C; see the secondary motion)
    this.worldTurn(out, sp[1], bend * 0.3 * sl, 0); this.worldTurn(out, sp[2], bend * 0.12 * sl, 0);
    // the surge: forward with the pull, carried through the glide, easing back a touch as it slows into its steps; the belly down on the glide
    // (the pull carries it ahead in the world, quickest mid-pull; then it eases back to its place over the glide and the steps, slowly at
    // first, carrying the speed it got; and it gathers a touch as the hands reach for the next one)
    const lg = u < 0.26 ? (x => x * x * x * (10 - 15 * x + 6 * x * x))(u / 0.26) : 1 - smooth((u - 0.26) / 0.74), gat = u > 0.86 ? Math.sin(Math.PI * (u - 0.86) / 0.14) : 0;
    out.root.z += (0.2 * lg - 0.03 * gat) * sl; out.root.y -= (0.012 + 0.022 * g) * sl;
    if (u < (SL.pu === undefined ? 1 : SL.pu) && sl > 0.5) this.kickGills(0, -0.28 * sl); SL.pu = u; // (each pull: the gills swept back by the lunge, then springing out again)
    // the head: a little dip into each pull, up and steady through the glide, a small nod with each step; the chest rides it gently
    const hp = (0.1 * Math.sin(Math.PI * clamp01(u / 0.26)) - 0.05 * g + 0.035 * (1 - g) * Math.sin(th + 0.6)) * sl;
    this.pitchTurn(out, sp[3], 0.3 * hp); this.pitchTurn(out, I.neck, 0.5 * hp); this.pitchTurn(out, I.head, 0.45 * hp); }
  // the body over uneven ground (climbing out of a basin): the hips up or down to the ground under them, the back tilted to the ground under
  // the chest and the head, bridging a narrow rim (the highest ground within a hand's width under each), eased so it rolls over
  if (TR || L.tbOn) {
    const tb = L.tb || (L.tb = { h: 0, a1: 0, a2: 0, a3: 0, tl: 0 }), on2 = TR ? 1 : 0, bh = (z, back) => { let m = -1e9; for (const dz of back ? [-0.16, -0.08, 0, 0.08, 0.16] : [-0.04, 0, 0.08, 0.16]) m = Math.max(m, gY(0, z + dz)); return m; }; // (ahead of the hips only: a rim it's left behind doesn't hold them up)
    const zH = -0.777, zS = -0.249, zC = 0.015, zN = 0.33, hH = TR ? bh(zH) : 0, sH = TR ? bh(zS, 1) : 0, cH = TR ? bh(zC, 1) : 0, nH = TR ? bh(zN, 1) : 0, t1 = TR ? Math.max(bh(zH - 0.3, 1), bh(zH - 0.6, 1), bh(zH - 0.95, 1)) : 0;
    const a1 = Math.atan2(sH - hH, zS - zH), a2 = Math.atan2(cH - sH, zC - zS) - a1, a3 = Math.atan2(nH - cH, zN - zC) - a1 - a2, cl = x => Math.max(-0.7, Math.min(0.7, x)), k = Math.min(1, dt * 14);
    tb.h += (hH - tb.h) * k; tb.a1 += (cl(a1) - tb.a1) * k; tb.a2 += (cl(a2) - tb.a2) * k; tb.a3 += (cl(a3) - tb.a3) * k; tb.tl += (Math.max(0, Math.atan2(t1 - hH, 0.55)) - tb.tl) * k;
    out.root.y += tb.h; this.pitchTurn(out, I.hips, -tb.a1); this.pitchTurn(out, sp[2], -tb.a2 * 0.6); this.pitchTurn(out, sp[3], -tb.a2 * 0.4); this.pitchTurn(out, I.neck, -tb.a3 * 0.6);
    L.tailUp = tb.a1 + 0.5 * tb.tl * (M.climbTail === undefined ? 1 : M.climbTail); L.tbOn = on2 || Math.abs(tb.h) > 0.002 || Math.abs(tb.a1) > 0.002; // (the tail kept off the hips' tilt, and up over ground behind)
  } else L.tailUp = 0;
  { const pk = P.fk('crawl', out); for (const l of L.limbs) l.hb.set(l.home.x + pk[l.root].x - l.rr.x, l.home.y, l.home.z + pk[l.root].z - l.rr.z); }
  // ---- in the air: the push-off, the tuck, the reach for the ground
  if (air) {
    if (!L.air) { L.air = true; L.airT = 0; L.lead = (L.steer > 0.2 ? 1 : L.steer < -0.2 ? -1 : -L.lead); for (const l of L.limbs) { l.held = l.st === 'stance'; l.st = 'air'; } L.arch.v += 60; }
    L.airT += dt;
    const tl = M.tl === undefined ? 1 : M.tl, reachA = 1 - smooth(clamp01((tl - 0.03) / 0.21)), reachL = 1 - smooth(clamp01((tl - 0.02) / 0.15)), hgt = Math.max(0, M.h || 0), rising = (M.vy || 0) > 0.5;
    const pos = P.fk('crawl', out);
    for (const l of L.limbs) {
      if (C && l.held) { l.p.applyMatrix4(C); l.p0.applyMatrix4(C); }
      if (l.held) { const d = l.p.distanceTo(pos[l.root]); if (d > 0.94 * l.len || L.airT > 0.12 || !rising) { l.held = false; l.p0.copy(l.p); } }
      if (!l.held) {
        // tucked in once it is off the ground (the hands folded back along the chest, the feet drawn up beside the belly), held there
        // through the flight, then reaching down and forward as the ground comes up, the hands first (the lead hand lowest: it touches
        // first), the feet just after
        const lead = l.arm && l.m === L.lead, dn = Math.min(hgt, 0.32), push = 1 - smooth(clamp01((L.airT - 0.04) / 0.08));
        LV1.copy(l.rr).add(l.arm ? LV2.set(0.06 * l.m, -0.12, -0.3) : LV2.set(0.05 * l.m, 0.07, -0.02)).add(LV4.set(l.hb.x - l.home.x, 0, l.hb.z - l.home.z));
        LV4.copy(l.hb).add(l.arm ? LV2.set(-0.03 * l.m, -0.1, -0.1) : LV2.set(-0.02 * l.m, -0.06, -0.1)); LV1.lerp(LV4, push);
        LV3.copy(l.hb).add(l.arm ? LV2.set(0.0, -dn + (lead ? -0.02 : 0.05), 0.15) : LV2.set(0.0, -Math.min(dn, 0.12) + 0.05, 0.06));
        LV1.lerp(LV3, rising ? 0 : l.arm ? reachA : reachL); l.p.lerp(LV1, 1 - Math.exp(-dt * 22));
      }
      l.lift = l.held ? 0 : 1;
    }
  } else if (L.air) {
    // touching down: the lead hand takes it, then the other hand, then the feet, one after another (closer together the faster it goes),
    // the body dipping onto the lead hand; then the gait picks up from there
    L.air = false; const k = Math.min(1.4, (M.landV || 4) / 6), sc = 1 / (1 + v / 1.2);
    const pick = (arm, lead) => L.limbs.find(l => l.arm === arm && (l.m === L.lead) === lead);
    L.land = { t: 0, list: [[pick(true, true), 0], [pick(true, false), 0.075], [pick(false, false), 0.13], [pick(false, true), 0.18]].map(([l, d]) => ({ l, d: d * sc })) };
    for (const z of L.land.list) { const l = z.l; l.st = 'land'; l.p0.copy(l.p); }
    L.ph = frac(-L.land.list[0].l.off + 0.12 * L.D);
    L.dip.v -= 34 * k; L.dipR.v += 40 * k * L.lead; L.landK = k;
  }
  if (!air && L.land) {
    const Z = L.land; Z.t += dt; let done = true;
    const fl = Math.max(GAIT.fMin, Math.min(GAIT.fMax, v * D / S));
    for (const z of Z.list) { const l = z.l; if (l.st !== 'land') continue;
      // still coming down: onto a spot ahead of the shoulder / hip (moving with the body until it touches), then the gait has it
      const Dl = l.arm ? D : Math.max(0.16, Math.min(D, GAIT.sweepF * fl / Math.max(v, 0.01)));
      l.tgt.copy(l.hb).addScaledVector(l.gv, -Dl / fl * 0.5); LV1.copy(l.tgt).sub(l.hb); LV1.y = 0; const r = (l.arm ? GAIT.reachH : GAIT.reachF) * 0.92; if (LV1.length() > r) LV1.setLength(r); l.tgt.set(l.hb.x + LV1.x, l.home.y, l.hb.z + LV1.z);
      if (Z.t >= z.d) { l.st = 'stance'; l.p.copy(l.tgt); l.fresh = true; }
      else { done = false; const s = Z.t / Math.max(z.d, 1e-3), e = s * s * (3 - 2 * s); l.p.lerpVectors(l.p0, l.tgt, e); l.lift = 1 - e; } }
    if (done) L.land = null;
  }
  if (!air) {
    for (const l of L.limbs) {
      if (l.st === 'land') continue;
      if (l.fresh) l.fresh = false; else if (C) { l.p.applyMatrix4(C); l.p0.applyMatrix4(C); }
      const Dl = l.arm ? D : Math.max(0.16, Math.min(D, GAIT.sweepF * Math.max(L.f, 0.5) / Math.max(v, 0.01))), u = frac(L.ph + l.off), stance = u < Dl;
      if (L.settle && L.settle.l === l) continue;
      if (stance) {
        if (l.st !== 'stance') { l.st = 'stance'; l.p.copy(l.tgt); }
        // stretched further than it reaches: it lets the ground drag it (only at full tilt, or shoved)
        LV1.copy(l.p).sub(l.hb); LV1.y = 0; const r = l.arm ? GAIT.reachH : GAIT.reachF; if (LV1.length() > r) { LV1.setLength(r); l.p.x = l.hb.x + LV1.x; l.p.z = l.hb.z + LV1.z; }
        l.p.y += (gY(l.p.x, l.p.z) + l.home.y - l.p.y) * Math.min(1, dt * 30); l.lift = 0;
      } else {
        if (l.st === 'stance') { l.st = 'swing'; l.p0.copy(l.p); }
        const s = (u - Dl) / (1 - Dl), Ts = Dl / Math.max(L.f, 0.5);
        l.tgt.copy(l.hb).addScaledVector(l.gv, -Ts * 0.5); LV1.copy(l.tgt).sub(l.hb); LV1.y = 0; const r = (l.arm ? GAIT.reachH : GAIT.reachF) * 0.92; if (LV1.length() > r) LV1.setLength(r);
        l.tgt.set(l.hb.x + LV1.x, gY(l.hb.x + LV1.x, l.hb.z + LV1.z) + l.home.y, l.hb.z + LV1.z);
        const e = s * s * (3 - 2 * s), lf = Math.pow(Math.sin(Math.PI * Math.min(1, s * 1.08)), 1.4); l.lift = lf;
        let bump = 0; if (TR) { for (const q of [0.25, 0.5, 0.75]) bump = Math.max(bump, gY(l.p0.x + (l.tgt.x - l.p0.x) * q, l.p0.z + (l.tgt.z - l.p0.z) * q) + l.home.y - Math.max(l.p0.y, l.tgt.y)); } /* (something to clear on the way) */
        l.p.lerpVectors(l.p0, l.tgt, e); l.p.y = l.p0.y * (1 - e) + l.tgt.y * e + (liftH + bump * 1.3) * lf;
      }
    }
    // stopped: now and then it moves a foot that was left stretched out back under itself, one at a time
    if (v < 0.08 && !swinging) {
      L.still += dt;
      if (!L.settle && L.still > 0.35) { let best = null, bd = 0.055; for (const l of L.limbs) { LV1.copy(l.p).sub(l.hb); LV1.y = 0; const d = LV1.length(); if (d > bd) { bd = d; best = l; } } if (best) { L.settle = { l: best, s: 0 }; best.p0.copy(best.p); best.tgt.copy(best.hb); } }
    } else L.still = 0;
    if (L.settle) { const z = L.settle, l = z.l; z.s += dt / 0.24; const s = Math.min(1, z.s), e = s * s * (3 - 2 * s), lf = Math.sin(Math.PI * s); l.lift = lf; l.p.lerpVectors(l.p0, l.tgt, e); l.p.y = l.home.y + 0.035 * lf;
      if (z.s >= 1) { L.settle = null; L.still = 0.1; l.st = 'stance'; } }
  }
  // the bob of each pair's footfall, the push-off's arch, the landing's dip onto the lead hand (on springs: they overshoot and settle)
  const bob = Math.cos(4 * Math.PI * (L.ph - D * 0.5)) * 0.009 * act * (1 - sl);
  const arch = spr(L.arch, 0, 90, 12, dt), dip = spr(L.dip, 0, 110, 13, dt), dipR = spr(L.dipR, 0, 110, 12, dt);
  const brI = (this.breath - 0.5) * (1 - act);   // (stopped, the breath shows: the chest rises and falls, the belly swells, the gills flare)
  out.root.y += -bob + dip * 0.0012 + brI * 0.02;
  const fallK = air && (M.vy || 0) < 0 ? 1 - smooth(clamp01(((M.tl === undefined ? 1 : M.tl) - 0.05) / 0.4)) : 0;
  rot(out, I.chest, -arch * 0.12 + dip * 0.1 - 4.5 * brI, 0, 0); rot(out, sp[2], -2 * brI, 0, 0); rot(out, I.head, 2 - arch * 0.1 - Math.min(0, dip) * 0.05 + (air ? -7 + 15 * fallK : 0), 0, 0);
  this.worldTurn(out, sp[3], 0, dipR * 0.12);
  if (air) { rot(out, sp[1], -4 + 7 * fallK, 0, 0); rot(out, sp[2], -4 + 6 * fallK, 0, 0); }
  // ---- the limbs on their marks (in the air the same marks steer them, with no ground under them)
  for (const l of L.limbs) {
    const LB = this.limbBind[l.arm ? 'arm' : 'leg'];
    let tp = l.p, lift = l.lift;
    let tk = 0;
    if (sl > 0.001) { // (swimming: each limb on its marks through the stroke; round a turn the inside hand reaches out and holds on, the outside one sweeps wide)
      const pk2 = L.pk2 && L.pk2f === this.t ? L.pk2 : (L.pk2f = this.t, L.pk2 = P.fk('crawl', out)), pr = pk2[l.root], q = l.q || (l.q = new THREE.Vector3()), mk = swMark(l.en, SL.u, l.arm, SL.m);
      const tn = Math.max(-1, Math.min(1, bend / 45)) * l.m, inn = Math.max(0, tn), outr = Math.max(0, -tn); // (inn: this is the inside of the turn)
      tk = mk[3] * (l.arm ? 1 - 0.75 * inn : 1);
      const ox = mk[0] + (l.arm ? 0.07 * inn * (1 - mk[3] * 0.5) + 0.06 * outr * (1 - mk[3]) : 0.03 * outr), oz = mk[2] + (l.arm ? 0.08 * inn : 0);
      q.set(pr.x + ox * l.m, l.home.y + mk[1] * (1 - (l.arm ? 0.75 * inn : 0)), pr.z + oz);
      q.lerpVectors(l.p, q, sl); tp = q; lift = lift * (1 - sl) + Math.max(tk, mk[4]) * sl; tk *= sl; }
    out.contact(l.en, tp, LV2.set(LB.fwd.x * l.m * (1 - tk) + 0.08 * l.m * tk, -0.35 * lift * (1 - tk), LB.fwd.z * (1 - tk) - tk), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1);
    const dig = this.chain[l.arm ? 'fingers' : 'toes'][l.m > 0 ? 0 : 1], ns = 1 - tk; const sl0 = sl; { const sl = tk; // (along its sides: the fingers and toes closed together, nearly straight)
    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0)) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns + 2 * sl, 0, 0); }); }
  }
  // the tail carries the wave on behind the hips
  this.tailWave(2 * Math.PI * L.ph + Math.PI * 0.85, ((4 + 15 * clamp01(v / 6.5)) * act + 1.5), 0.75, air ? -3 : 0);
  if (sl > 0.001) { const tt = this.tailTarget, th = 4 * Math.PI * SL.u, env = 0.6 + 0.4 * SL.g; let up = 14 * env * Math.sin(th - 5 * 0.55); // (from the hips' own heading on)
    for (let k = 0; k < 6; k++) { const a = (18 + 7 * k) * env * Math.sin(th - (6 + k) * 0.55); tt[k * 2] = tt[k * 2] * (1 - sl) + (a - up) * sl; tt[k * 2 + 1] *= 1 - sl; up = a; } }
  { const cc = L.tcurl = (L.tcurl || 0) + ((M.climbCurl || 0) - (L.tcurl || 0)) * Math.min(1, dt * 8), up = (L.tailUp || 0) - 0.4 * cc, tl = this.chain.tail; // (a positive pitch lifts a tail joint)
    if (Math.abs(up) > 0.005) { this.pitchTurn(out, tl[0], up * 0.85); this.pitchTurn(out, tl[1], up * 0.25); if (up > 0) { this.pitchTurn(out, tl[2], -up * 0.35); this.pitchTurn(out, tl[3], -up * 0.2); } } // (up over the rim, the far end draped back down)
    if (cc > 0.01) for (let k = 0; k < tl.length; k++) this.worldTurn(out, tl[k], (k ? 26 : 14) * cc, 0); } // (still in the tub: its tail curled round inside it, down in the paint) this.tailFree = 1; this.neck.amt = 0.7 - 0.3 * act;
  // ---- curled into a ball: the spine rolls up nose to tail, the limbs tuck in, the gills fold back
  if (ball > 0.002) {
    const b = smooth(ball);
    // (curled, the back bends further than walking ever takes it: the joint limits let the spine, the head and the tail go for the ball)
    rot(out, I.hips, 34 * b, 0, 0); rot(out, sp[1], 42 * b, 0, 0); rot(out, sp[2], 42 * b, 0, 0); rot(out, sp[3], 36 * b, 0, 0); rot(out, I.neck, 40 * b, 0, 0); rot(out, I.head, 40 * b, 0, 0);
    // (the tail wraps round the outside of the ball, the tip tucking in over the head)
    const tl = this.chain.tail; for (let k = 0; k < tl.length; k++) rot(out, tl[k], [58, 46, 46, 46, 48, 52][k] * b, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; rot(out, I['upperarm.' + s], 0, 0, -35 * m * b); rot(out, I['forearm.' + s], 70 * b, 0, 0); rot(out, I['thigh.' + s], 55 * b, 0, -10 * m * b); rot(out, I['shin.' + s], 70 * b, 0, 0); }
    for (const k in out.contacts) out.contacts[k].w *= (1 - b) * (1 - b);
    this.tailFree = 1 - 0.8 * b; this.neck.amt *= 1 - b; this.gillHold = 1;
    { const pos = P.fk('crawl', out), c = this.ballC || (this.ballC = new THREE.Vector3()); c.copy(pos[sp[1]]).lerp(pos[sp[3]], 0.5); }
  }
  this.ballOn = ball;
  return out;
};
// the belly swells with the breath further when it is still
{ const j0 = Animator.prototype.jelly;
  Animator.prototype.jelly = function (dt) { j0.call(this, dt); const L = this.look2, lo = this.loco; if (L && lo && this.mesh === 'crawl') L.U.uJelly.value.x *= 1 + 0.9 * (1 - lo.act); };
}
// curled, the joint limits leave the back, the head and the tail alone (the ball is a designed pose; walking keeps its limits)
{ const lim0 = Animator.prototype.limits;
  Animator.prototype.limits = function (pose, which, list) {
    if (!(this.ballOn > 0.01) || which !== 'crawl') return lim0.call(this, pose, which, list);
    const skip = this.ballSkip || (this.ballSkip = new Set([...this.chain.spine, this.I.head, ...this.chain.tail]));
    return lim0.call(this, pose, which, (list ? Array.from(list) : Array.from(this.P.lim.keys())).filter(i => !skip.has(i)));
  };
}
// the gills: besides the flutter and the drag of the head's own motion, they swing out round a turn (thrown outward, lagging the
// head's swing and overshooting when it stops), and flare a little with each breath in
{ const ss0 = Animator.prototype.stepSecondary;
  Animator.prototype.stepSecondary = function (dt) {
    const L = this.loco; if (!this.gillSpring2) { this.gillSpring2 = 1; this.gillSpring.k = 230; this.gillSpring.c = 10; }
    if (L) { const swing = Math.max(-1, Math.min(1, -(L.yr * Math.max(1.5, L.v) * 0.12 + L.ht.v * 0.012))), fl = (this.breath - 0.5) * 2;
      const add = this.gillAdd || (this.gillAdd = new Float32Array(12));
      for (let j = 0; j < 6; j++) { const sgn = j < 3 ? 1 : -1; add[j * 2] = -fl * 2.5 * (1 - L.act); add[j * 2 + 1] = swing * 24 * sgn + fl * 7 * (1 - L.act); } this.gillAddOn = true; }
    // the original computes the targets and steps the spring: the turn's swing goes in through the push the spring is given
    ss0.call(this, dt);
    // the tail follows the body's bend round a turn (its spring lags it in and swings it back after)
    if (L && this.state === 'crawl') this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.16 + 0.2 * (L.slK || 0)) + (this.motion.spin !== undefined ? L.tlg * 0.27 : 0);
  };
  // the targets: wrapped so the added swing lands in the spring's target before it is stepped
  const SpringStep = Spring.prototype.step;
  Spring.prototype.step = function (target, dt) { if (this.addTo) { const a = this.addTo(); if (a) for (let i = 0; i < target.length; i++) target[i] += a[i]; } return SpringStep.call(this, target, dt); };
  const init0 = Animator.prototype.initLoco;
  Animator.prototype.initLoco = function () { const L = init0.call(this); this.gillSpring.addTo = () => this.gillAddOn ? this.gillAdd : null; return L; };
}
}

return { ease, Spring, Animator };
})();
const { ease, Spring, Animator } = __anim;

// ====================================================================== look
const __look = (() => {
// The axolotl's look (v7): one procedural layered skin on both meshes, the old slime's face, the paint coat, the soft-body jelly layer.
//  - The skin is drawn from per-vertex data (see extras7.py) and the canonical position of each vertex on the standing body (the crawl mesh
//    is mapped onto it through the skeleton), so both meshes carry the same pattern at the same detail: a team-coloured base with slow
//    tone drift and dorsal mottling, a pale cream belly gradient (throat and chin included), blue-grey speckle spots in two sizes, fine skin
//    relief and pores, wrinkle bands at the knuckles, wrists, elbows, knees, ankles and neck, cavity occlusion, a translucent tail fin with a
//    darker blue-grey core band and a lit edge, feathery saturated gill frills that glow when backlit, and a satin sheen on the belly.
//  - The face is the game's slime face: the same face sheets (drawn by the game's own makeFaceSheets, below), the same shader-drawn
//    pupils, iris colours, catchlights and eye styles (round, squid, dot, zombie), the same expressions, blinks and glances, projected onto
//    the front of the head about the head centre exactly as the slime projects it, on a head that is the same shape in both states.

// ---------------- the face projection (shared by both meshes: angles about each mesh's face-sphere centre, in rest space) ----------------
// pitch: the face centre's height above the head centre's horizon (rad); half: the angle a face cell's half width spans (rad); the game's
// slime uses pitch 0, half 0.86 on its round head. The axolotl head is a wider dome, so its face sits a little higher and a little tighter.
const FACE = { pitch: 0.1, half: 1.1, squeeze: 1.0 };
const EYE_COLS = { brown: { name: 'Brown', lin: [0.16, 0.06, 0.035], css: '#8A5636' }, blue: { name: 'Blue', lin: [0.03, 0.1, 0.32], css: '#3B7BE0' }, green: { name: 'Green', lin: [0.04, 0.18, 0.05], css: '#46A853' },
  violet: { name: 'Violet', lin: [0.14, 0.045, 0.28], css: '#8E52DA' }, gold: { name: 'Gold', lin: [0.34, 0.17, 0.016], css: '#D8A41F' } };
const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', zombie: 'Zombie' };
const EYE_STYLE_K = { round: 0, edgy: 1, dot: 2, zombie: 3 };
// each expression is an eye cell and a mouth cell (yawn and dizzy borrow parts of the others), as in the game
const EXPR = { neutral: [0, 8], happy: [1, 9], angry: [2, 10], hurt: [3, 11], glee: [4, 12], scared: [5, 13], yawn: [6, 13], dizzy: [7, 11], peek: [5, 13], leap: [5, 9], brace: [7, 11] };
const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 } };
const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 };
function pupilOf(name) { const F = PUPILS[name] || FACE_LIDS[name]; if (!F) return { pu: 1, py: 0 }; const L = F.L || F; return { pu: L.pu || 1, py: (L.py || 0) * FACE_EYE.ry }; }
// ---------- the slime's face, drawn once into two sheets (4 across, 5 down) ----------
// cells 0-5 eyes: neutral, happy, angry, hurt, glee, scared; 6 eyes closed (a blink); 7 eyes squeezed shut
// cells 8-13 mouths in the same order; 14-19 the same mouths with fangs
// color sheet: everything but the pupils. mask sheet: red = where the eyeball shows (the shader draws the pupils there, so they can look
// around), green = how much the lid shades it
// face space: a cell spans -1..1 both ways, x to the slime's right as you look at it, y up
const FACE_EYE = { x: 0.4, y: 0.16, rx: 0.3, ry: 0.33 };
const FACE_KINDS = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared'];
// per expression: lid height h (-1 shut .. 1 wide), slant toward the middle k, arch c, cheek (lower lid) height, pupil size, and where the
// pupils rest; L and R can differ (hurt winces one eye shut)
const FACE_LIDS = {
  neutral: { h: 0.08, k: 0, c: 0.1, ch: -0.95, pu: 1.0, py: -0.1 },
  happy: { h: 0.42, k: 0.04, c: 0.16, ch: -0.42, chc: 0.34, pu: 1.0, py: -0.02, blush: 1 },
  angry: { h: 0.05, k: -0.46, c: -0.02, ch: -0.7, chc: 0.1, pu: 0.88, py: -0.12 },
  hurt: { L: { h: -0.12, k: 0.3, c: 0.0, ch: -0.42, chc: 0.2, pu: 0.85, py: -0.05 }, R: { shut: 'squeeze' }, sweat: 1 },
  glee: { shut: 'arc', blush: 1.2 },
  scared: { h: 0.86, k: 0.08, c: 0.06, ch: -0.97, pu: 0.62, py: -0.02 },
};
function makeFaceSheets(C) {
  const W = C * 4, H = C * 5, col = document.createElement('canvas'), msk = document.createElement('canvas'); col.width = msk.width = W; col.height = msk.height = H;
  const g = col.getContext('2d'), m = msk.getContext('2d'); m.fillStyle = '#000'; m.fillRect(0, 0, W, H);
  const at = (ctx, cell, fn) => { ctx.save(); ctx.translate((cell % 4) * C + C / 2, Math.floor(cell / 4) * C + C / 2); ctx.scale(C / 2, -C / 2); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; fn(ctx); ctx.restore(); };
  const E = FACE_EYE, INK = '40,6,18';
  // the lid's edge and the lower lid as curves across one eye (sd: -1 the left eye, 1 the right), in face space
  const lidY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * (L.h + (L.k || 0) * u * -sd + (L.c || 0) * (1 - u * u)); };
  const cheekY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * ((L.ch === undefined ? -1 : L.ch) + (L.chc || 0) * (1 - u * u)); };
  const ell = (ctx, sd, k) => { ctx.beginPath(); ctx.ellipse(sd * E.x, E.y, E.rx * (k || 1), E.ry * (k || 1), 0, 0, Math.PI * 2); };
  const curve = (ctx, f, sd, x0, x1, cont) => { const n = 40; for (let i = 0; i <= n; i++) { const x = x0 + (x1 - x0) * i / n; i || cont ? ctx.lineTo(x, f(x)) : ctx.moveTo(x, f(x)); } };
  // the open part of the eye: inside the eyeball, under the lid, over the lower lid
  const openPath = (ctx, L, sd) => { const x0 = sd * E.x - E.rx * 1.2, x1 = sd * E.x + E.rx * 1.2; ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, x0, x1); curve(ctx, x => cheekY(L, sd, x), sd, x1, x0, true); ctx.closePath(); };
  function openEye(cell, L, sd) {
    at(g, cell, ctx => {
      // the bulge's soft shadow on the skin below it
      const sh = ctx.createRadialGradient(sd * E.x, E.y - E.ry * 0.25, E.rx * 0.6, sd * E.x, E.y - E.ry * 0.25, E.rx * 1.35); sh.addColorStop(0, 'rgba(' + INK + ',0.0)'); sh.addColorStop(0.55, 'rgba(' + INK + ',0.2)'); sh.addColorStop(1, 'rgba(' + INK + ',0)');
      ctx.fillStyle = sh; ctx.beginPath(); ctx.ellipse(sd * E.x, E.y - E.ry * 0.2, E.rx * 1.35, E.ry * 1.25, 0, 0, Math.PI * 2); ctx.fill();
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      // the white: bright in the middle, cooler toward the rim, a touch of warm skin light bounced in from below
      const wg = ctx.createRadialGradient(sd * E.x - 0.05, E.y + 0.06, 0.02, sd * E.x, E.y, E.rx * 1.08); wg.addColorStop(0, '#FFFFFF'); wg.addColorStop(0.62, '#F4F3F8'); wg.addColorStop(1, '#C9C7D6');
      ctx.fillStyle = wg; ctx.fillRect(sd * E.x - 0.5, E.y - 0.5, 1, 1);
      ctx.restore();
      // the lid's shadow on the white (a band under its edge)
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      for (let k = 0; k < 6; k++) { ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) - 0.012 * k, sd, sd * E.x - E.rx * 1.2, sd * E.x + E.rx * 1.2); ctx.strokeStyle = 'rgba(60,30,70,' + (0.11 - 0.017 * k).toFixed(3) + ')'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      // the rim where the white meets the skin (strong under the eye, faint up under the lid), the lash line along the lid, and light on the lid's edge
      ctx.save(); openPath(ctx, L, sd); ctx.clip(); ell(ctx, sd); ctx.strokeStyle = 'rgba(' + INK + ',0.62)'; ctx.lineWidth = 0.028; ctx.stroke(); ctx.restore();
      ctx.save(); ell(ctx, sd, 1.002); ctx.clip();
      ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.9)'; ctx.lineWidth = 0.045; ctx.stroke();
      if (L.ch > -0.9) { ctx.beginPath(); curve(ctx, x => cheekY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.55)'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      ctx.save(); ell(ctx, sd, 1.04); ctx.clip(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) + 0.04, sd, sd * E.x - E.rx * 0.8, sd * E.x + E.rx * 0.8); ctx.strokeStyle = 'rgba(255,240,235,0.32)'; ctx.lineWidth = 0.035; ctx.stroke();
      // the lid itself: a faint dark contour where its dome meets the face above
      ctx.restore(); ctx.save(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.3, sd * E.x + E.rx * 1.3); ctx.lineTo(sd * E.x + E.rx * 1.3, 2); ctx.lineTo(sd * E.x - E.rx * 1.3, 2); ctx.closePath(); ctx.clip();
      ell(ctx, sd, 1.01); ctx.strokeStyle = 'rgba(' + INK + ',0.2)'; ctx.lineWidth = 0.022; ctx.stroke(); ctx.restore();
    });
    at(m, cell, ctx => { ctx.save(); ell(ctx, sd, 0.985); ctx.clip(); openPath(ctx, L, sd); ctx.clip(); ctx.fillStyle = '#FF0000'; ctx.fillRect(-1, -1, 2, 2);
      // green: the lid's shade (strong right under its edge)
      for (let k = 0; k < 8; k++) { ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) - 0.012 * k, sd, sd * E.x - E.rx * 1.2, sd * E.x + E.rx * 1.2); ctx.strokeStyle = 'rgba(255,' + Math.round(255 * (1 - k / 8)) + ',0,1)'; ctx.globalCompositeOperation = 'lighten'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore(); });
  }
  function shutEye(cell, sd, kind) {
    at(g, cell, ctx => { ctx.strokeStyle = 'rgba(' + INK + ',0.92)'; ctx.lineWidth = 0.055; const cx = sd * E.x, cy = E.y - 0.02;
      if (kind === 'arc') { ctx.beginPath(); ctx.arc(cx, cy - 0.08, E.rx * 0.82, 0.18 * Math.PI, 0.82 * Math.PI); ctx.stroke(); }
      else if (kind === 'squeeze') { ctx.beginPath(); ctx.moveTo(cx + sd * 0.2, cy + 0.15); ctx.lineTo(cx - sd * 0.12, cy); ctx.lineTo(cx + sd * 0.2, cy - 0.15); ctx.stroke(); ctx.lineWidth = 0.03; ctx.strokeStyle = 'rgba(' + INK + ',0.45)'; ctx.beginPath(); ctx.moveTo(cx - sd * 0.24, cy + 0.17); ctx.lineTo(cx - sd * 0.16, cy + 0.08); ctx.moveTo(cx - sd * 0.26, cy - 0.15); ctx.lineTo(cx - sd * 0.17, cy - 0.08); ctx.stroke(); }
      else { ctx.beginPath(); ctx.ellipse(cx, cy + 0.02, E.rx * 0.95, E.ry * 0.36, 0, Math.PI * 1.06, Math.PI * 1.94, false); ctx.stroke(); ctx.lineWidth = 0.022; ctx.strokeStyle = 'rgba(255,240,235,0.3)'; ctx.beginPath(); ctx.ellipse(cx, cy + 0.06, E.rx * 0.8, E.ry * 0.3, 0, Math.PI * 1.15, Math.PI * 1.85, false); ctx.stroke(); } });
  }
  const blush = (cell, k) => at(g, cell, ctx => { for (const sd of [-1, 1]) { const bg = ctx.createRadialGradient(sd * 0.66, -0.2, 0.01, sd * 0.66, -0.2, 0.2); bg.addColorStop(0, 'rgba(255,110,150,' + (0.55 * k).toFixed(2) + ')'); bg.addColorStop(1, 'rgba(255,110,150,0)'); ctx.fillStyle = bg; ctx.beginPath(); ctx.ellipse(sd * 0.66, -0.2, 0.22, 0.13, 0, 0, Math.PI * 2); ctx.fill(); } });
  const sweat = cell => at(g, cell, ctx => { const d = (x, y, s) => { ctx.beginPath(); ctx.moveTo(x, y + 0.13 * s); ctx.bezierCurveTo(x + 0.07 * s, y, x + 0.06 * s, y - 0.06 * s, x, y - 0.06 * s); ctx.bezierCurveTo(x - 0.06 * s, y - 0.06 * s, x - 0.07 * s, y, x, y + 0.13 * s); const gr = ctx.createLinearGradient(x, y + 0.12 * s, x, y - 0.06 * s); gr.addColorStop(0, 'rgba(190,232,255,0.95)'); gr.addColorStop(1, 'rgba(110,180,240,0.95)'); ctx.fillStyle = gr; ctx.fill(); ctx.strokeStyle = 'rgba(30,60,110,0.7)'; ctx.lineWidth = 0.018; ctx.stroke(); ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.beginPath(); ctx.ellipse(x - 0.018 * s, y - 0.005 * s, 0.014 * s, 0.024 * s, -0.4, 0, Math.PI * 2); ctx.fill(); };
    d(0.84, 0.62, 1.15); d(0.95, 0.4, 0.7); });
  FACE_KINDS.forEach((k, i) => { const F = FACE_LIDS[k];
    for (const sd of [-1, 1]) { const L = F.L ? (sd < 0 ? F.L : F.R) : F; if (L.shut || F.shut) shutEye(i, sd, L.shut || F.shut); else openEye(i, L, sd); }
    if (F.blush) blush(i, F.blush); if (F.sweat) sweat(i); });
  for (const sd of [-1, 1]) { shutEye(6, sd, 'closed'); shutEye(7, sd, 'squeeze'); }
  // ---- the lashes (worn as an accessory): drawn into the mask sheet's blue over every eye cell, so they follow each expression and blink;
  // the shader inks them only when they're worn. A liner along the top of the eye flicking up past its outer corner, and three long
  // lashes sweeping up and out from its outer half, curling at the tips (shut eyes: they hang from the lid and curl up). Drawn for the
  // right eye, mirrored for the left ----
  const clampL = (v, a, b) => Math.max(a, Math.min(b, v));
  const taper = (ctx, pts, wf) => { const n = pts.length, A = [], B = [];
    for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)], tx = b[0] - a[0], ty = b[1] - a[1], l = Math.hypot(tx, ty) || 1, w = wf(i / (n - 1)) * 0.5;
      A.push([pts[i][0] - ty / l * w, pts[i][1] + tx / l * w]); B.push([pts[i][0] + ty / l * w, pts[i][1] - tx / l * w]); }
    ctx.beginPath(); A.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); for (let i = n - 1; i >= 0; i--) ctx.lineTo(B[i][0], B[i][1]); ctx.closePath(); ctx.fill(); };
  // one lash: from p at angle a, turning by curl along its length (more toward the tip), tapering to a point
  const lash = (ctx, p, a, len, curl, w0) => { const pts = [[p[0], p[1]]], n = 18; let x = p[0], y = p[1];
    for (let i = 1; i <= n; i++) { const u = i / n; a += curl / n * (0.2 + 1.6 * u); x += Math.cos(a) * len / n; y += Math.sin(a) * len / n; pts.push([x, y]); }
    taper(ctx, pts, u => w0 * Math.pow(1 - u, 0.75) + 0.003); };
  // the liner: thin at its start, thickest at the corner, then a flick on past it turning up to a point
  const liner = (ctx, pts, a, w) => { const n = pts.length - 1; let [px, py] = pts[n];
    for (let i = 0; i < 9; i++) { a += 0.07; px += Math.cos(a) * 0.017; py += Math.sin(a) * 0.017; pts.push([px, py]); }
    const m0 = n / (pts.length - 1); taper(ctx, pts, u => u <= m0 ? w * (0.38 + 0.62 * Math.pow(u / m0, 0.6)) : w * Math.pow(1 - (u - m0) / (1 - m0), 0.85) + 0.003); };
  const rimT = x => { const u = (x - E.x) / E.rx; return Math.sqrt(Math.max(0, 1 - u * u)); };
  const topY = (L, x) => Math.min(lidY(L, 1, x), E.y + E.ry * rimT(x)), botY = (L, x) => Math.max(cheekY(L, 1, x), E.y - E.ry * rimT(x));
  const LASHES = [[0.38, 0.31, 1.42, -0.62], [0.65, 0.36, 1.06, -0.68], [0.9, 0.34, 0.76, -0.66]]; // where along the outer half, length, lean, curl
  function lashOpen(ctx, L) {
    let x0 = null, x1 = null; for (let i = 0; i <= 240; i++) { const x = E.x - E.rx + 2 * E.rx * i / 240; if (topY(L, x) > botY(L, x) + 0.012) { if (x0 === null) x0 = x; x1 = x; } }
    if (x0 === null) return; const pts = []; for (let i = 0; i <= 40; i++) { const x = x0 + (x1 - x0) * i / 40; pts.push([x, topY(L, x) + 0.004]); }
    const q = pts[36], z = pts[40]; liner(ctx, pts, clampL(Math.atan2(z[1] - q[1], z[0] - q[0]), -0.25, 0.55) + 0.3, 0.092);
    for (const [t, len, a0, curl] of LASHES) { const x = E.x + (x1 - E.x) * t, y = topY(L, x), sl = (topY(L, x + 0.004) - topY(L, x - 0.004)) / 0.008, a = clampL(a0 + 0.45 * (Math.atan2(1, -sl) - Math.PI / 2), 0.32, 1.65);
      lash(ctx, [x, y + 0.006], a, len, Math.max(curl, -0.12 - a), 0.064); }
  }
  function lashShut(ctx, kind) {
    const cy = E.y - 0.02;
    if (kind === 'arc') { const r = E.rx * 0.82, oy = cy - 0.08, pts = []; for (let i = 0; i <= 40; i++) { const th = 0.82 * Math.PI - 0.64 * Math.PI * i / 40; pts.push([E.x + r * Math.cos(th), oy + r * Math.sin(th)]); }
      liner(ctx, pts, -0.18 * Math.PI - Math.PI / 2 + 0.55, 0.085);
      for (const [t, len, , curl] of LASHES) { const th = 0.5 * Math.PI - 0.32 * Math.PI * t, a = clampL(th + 0.12, 0.32, 1.6); lash(ctx, [E.x + r * Math.cos(th), oy + r * Math.sin(th)], a, len * 0.9, Math.max(curl, -0.12 - a), 0.062); } }
    else if (kind === 'squeeze') { const p0 = [E.x - 0.12, cy], p1 = [E.x + 0.2, cy + 0.15], pts = []; for (let i = 0; i <= 20; i++) pts.push([p0[0] + (p1[0] - p0[0]) * i / 20, p0[1] + (p1[1] - p0[1]) * i / 20]);
      liner(ctx, pts, Math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + 0.15, 0.08);
      for (const [t, len, a] of [[0.55, 0.24, 1.3], [0.82, 0.28, 1.0], [1.0, 0.27, 0.7]]) lash(ctx, [p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t], a, len, -0.58, 0.058); }
    else { const a = E.rx * 0.95, b = E.ry * 0.36, oy = cy + 0.02, pts = []; for (let i = 0; i <= 40; i++) { const th = 1.06 * Math.PI + 0.88 * Math.PI * i / 40; pts.push([E.x + a * Math.cos(th), oy + b * Math.sin(th)]); }
      liner(ctx, pts, 0.42, 0.088);
      for (const [t, len] of [[0.36, 0.25], [0.62, 0.29], [0.86, 0.29]]) { const th = 1.5 * Math.PI + 0.44 * Math.PI * t, nrm = Math.atan2(Math.sin(th) / b, Math.cos(th) / a), an = clampL(nrm + 0.3, -1.45, -0.3);
        lash(ctx, [E.x + a * Math.cos(th), oy + b * Math.sin(th) - 0.004], an, len, 0.72, 0.06); } }
  }
  const lashCell = (cell, sd, fn) => at(m, cell, ctx => { if (sd < 0) ctx.scale(-1, 1); ctx.globalCompositeOperation = 'lighten'; ctx.fillStyle = '#0000FF'; fn(ctx); });
  FACE_KINDS.forEach((k, i) => { const F = FACE_LIDS[k];
    for (const sd of [-1, 1]) { const L = F.L ? (sd < 0 ? F.L : F.R) : F; lashCell(i, sd, ctx => L.shut || F.shut ? lashShut(ctx, L.shut || F.shut) : lashOpen(ctx, L)); } });
  for (const sd of [-1, 1]) { lashCell(6, sd, ctx => lashShut(ctx, 'closed')); lashCell(7, sd, ctx => lashShut(ctx, 'squeeze')); }
  // ---- mouths ----
  const MY = -0.5;
  const cavity = (ctx, path, top, bot, tongue) => {
    path(); const gr = ctx.createLinearGradient(0, top, 0, bot); gr.addColorStop(0, '#2A0410'); gr.addColorStop(0.55, '#5A0C1E'); gr.addColorStop(1, '#7E1A2C'); ctx.fillStyle = gr; ctx.fill();
    ctx.save(); path(); ctx.clip();
    if (tongue) { const [tx, ty, tw, th] = tongue, tg = ctx.createRadialGradient(tx - tw * 0.2, ty + th * 0.35, 0, tx, ty, tw * 1.1); tg.addColorStop(0, '#FF9DB0'); tg.addColorStop(0.6, '#F0607E'); tg.addColorStop(1, '#C23A58'); ctx.fillStyle = tg; ctx.beginPath(); ctx.ellipse(tx, ty, tw, th, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = 'rgba(255,215,225,0.55)'; ctx.beginPath(); ctx.ellipse(tx - tw * 0.32, ty + th * 0.42, tw * 0.22, th * 0.14, -0.3, 0, Math.PI * 2); ctx.fill(); }
    const sh = ctx.createLinearGradient(0, top, 0, top - (top - bot) * 0.45); sh.addColorStop(0, 'rgba(10,0,4,0.75)'); sh.addColorStop(1, 'rgba(10,0,4,0)'); ctx.fillStyle = sh; ctx.fillRect(-2, bot, 4, top - bot + 0.2);
    ctx.restore(); path(); ctx.strokeStyle = 'rgba(' + INK + ',0.85)'; ctx.lineWidth = 0.032; ctx.stroke();
  };
  const fang = (ctx, x, y, s) => { ctx.beginPath(); ctx.moveTo(x - 0.035 * s, y + 0.005); ctx.quadraticCurveTo(x - 0.01 * s, y - 0.07 * s, x + 0.002 * s, y - 0.088 * s); ctx.quadraticCurveTo(x + 0.014 * s, y - 0.06 * s, x + 0.035 * s, y + 0.005); ctx.closePath(); const fg = ctx.createLinearGradient(0, y, 0, y - 0.09 * s); fg.addColorStop(0, '#FFFFFF'); fg.addColorStop(1, '#E9E2F0'); ctx.fillStyle = fg; ctx.fill(); ctx.strokeStyle = 'rgba(' + INK + ',0.7)'; ctx.lineWidth = 0.014; ctx.stroke(); };
  const line = (ctx, pts, w) => { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.strokeStyle = 'rgba(' + INK + ',0.92)'; ctx.lineWidth = w || 0.045; ctx.stroke(); };
  const dPath = (ctx, w, top, h, dip) => () => { ctx.beginPath(); ctx.moveTo(-w, top); ctx.quadraticCurveTo(0, top - dip, w, top); for (let k = 1; k <= 40; k++) { const t = k / 40 * Math.PI; ctx.lineTo(w * Math.cos(t), top - h * Math.sin(t)); } ctx.closePath(); };
  const MOUTHS = {
    neutral: (ctx, f) => { line(ctx, Array.from({ length: 21 }, (_, i) => { const u = i / 20 - 0.5; return [u * 0.2, MY + 0.03 - 0.035 * Math.cos(u * Math.PI)]; }), 0.034); if (f) { fang(ctx, -0.05, MY + 0.0, 0.8); fang(ctx, 0.05, MY + 0.0, 0.8); } },
    happy: (ctx, f) => { cavity(ctx, dPath(ctx, 0.2, MY + 0.08, 0.2, 0.03), MY + 0.08, MY - 0.12, [0, MY - 0.09, 0.11, 0.07]); if (f) { fang(ctx, -0.085, MY + 0.072, 0.95); fang(ctx, 0.085, MY + 0.072, 0.95); } },
    angry: (ctx, f) => { line(ctx, [[-0.12, MY - 0.03], [-0.03, MY + 0.01], [0.05, MY + 0.0], [0.12, MY - 0.035]], 0.04); if (f) { fang(ctx, -0.055, MY + 0.003, 0.85); fang(ctx, 0.045, MY + 0.002, 0.85); } },
    hurt: (ctx, f) => { line(ctx, Array.from({ length: 33 }, (_, i) => { const u = i / 32; return [-0.15 + 0.3 * u, MY + 0.025 * Math.sin(u * Math.PI * 4)]; }), 0.036); if (f) { fang(ctx, -0.06, MY + 0.02, 0.75); fang(ctx, 0.06, MY - 0.005, 0.75); } },
    glee: (ctx, f) => { cavity(ctx, dPath(ctx, 0.27, MY + 0.12, 0.3, 0.05), MY + 0.12, MY - 0.18, [0, MY - 0.14, 0.15, 0.1]); if (f) { fang(ctx, -0.12, MY + 0.11, 1.1); fang(ctx, 0.12, MY + 0.11, 1.1); } },
    scared: (ctx, f) => { cavity(ctx, () => { ctx.beginPath(); ctx.ellipse(0, MY - 0.02, 0.07, 0.1, 0, 0, Math.PI * 2); }, MY + 0.08, MY - 0.12, null); if (f) { fang(ctx, -0.035, MY + 0.07, 0.6); fang(ctx, 0.035, MY + 0.07, 0.6); } },
  };
  const big = (ctx, fn) => { ctx.translate(0, MY); ctx.scale(1.35, 1.35); ctx.translate(0, -MY); fn(); };
  FACE_KINDS.forEach((k, i) => { at(g, 8 + i, ctx => big(ctx, () => MOUTHS[k](ctx, false))); at(g, 14 + i, ctx => big(ctx, () => MOUTHS[k](ctx, true))); });
  return { col, msk };
}
// ---------------- shader pieces ----------------
// vertex: the canonical place and the material data through to the fragment, the face's frame from the REST position (so the face rides the
// head rigidly), and the soft-body jelly layer on the skinned position (breathing, squash / stretch, lag, ripple; the head stays rigid)
const VERT_PARS = `
attribute vec4 cpos, jelly, fill, mat;
uniform float uCpScale;
uniform vec4 uJelly;   // x breath (m), y squash (-stretch .. +squash), z body height (m), w ripple (m)
uniform vec4 uLag;     // xyz: lag offset of the soft body (object space, m), w: time
uniform vec4 uHead;    // xyz: the face sphere's centre (rest, object space), w: its radius
uniform vec4 uFaceP;   // x the face centre's pitch, y the half angle of a face cell, z horizontal squeeze, w on
uniform float uCoatMix;
varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO;`;
const VERT_MAIN = `
{
  vCp = cpos.xyz * uCpScale; vAlong = cpos.w * uCpScale; vJelly = jelly; vFill = fill; vMat = mat; vFillO = mix(fill.x, fill.y, uCoatMix);
  vec3 d = position - uHead.xyz; float yw = atan(d.x, d.z), pt = atan(d.y, length(d.xz));
  vFace = vec3(yw / (uFaceP.y * uFaceP.z), (pt - uFaceP.x) / uFaceP.y, smoothstep(-0.05, 0.3, d.z / uHead.w) * smoothstep(0.72, 0.95, jelly.w) * (1.0 - smoothstep(0.2, 0.45, mat.y)) * uFaceP.w);
  float soft = 1.0 - jelly.w, h = clamp(transformed.y / uJelly.z, 0.0, 1.0);
  transformed += objectNormal * (jelly.x * uJelly.x + uJelly.w * soft * sin(position.x * 23.0 + position.y * 17.0 + uLag.w * 9.0) * sin(position.z * 19.0 - uLag.w * 7.0));
  float s = uJelly.y * soft; transformed.y *= 1.0 - s; transformed.xz *= 1.0 + 0.5 * s;
  transformed += uLag.xyz * soft * h;
}`;
const FRAG_PARS = `
uniform vec3 uSkin, uBelly, uSpot, uGill, uGillTip, uFinCore, uFinGlow, uPaint; uniform vec4 uCoat, uDetail, uDetail2, uTint, uTintTo; uniform float uCoatMix;
uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp, fLash; uniform vec3 fIris; uniform float fStyle; uniform vec3 uKeyDir; uniform float uDebug, uFadeK, uIsCrawl; uniform vec4 uSwap;
varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO;
float sCoatM = 0.0, faceInk = 0.0, sEyeM = 0.0, sDrawM = 0.0, sGill = 0.0, sFin = 0.0, sBelly = 0.0, sSpot = 0.0, sAO = 0.0;
float aHash(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yzx + 33.33); return fract((p.x + p.y) * p.z); }
vec3 aHash3(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return fract((p.xxy + p.yxx) * p.zyx); }
float aNoise(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(aHash(i), aHash(i + vec3(1.0, 0.0, 0.0)), f.x), mix(aHash(i + vec3(0.0, 1.0, 0.0)), aHash(i + vec3(1.0, 1.0, 0.0)), f.x), f.y),
             mix(mix(aHash(i + vec3(0.0, 0.0, 1.0)), aHash(i + vec3(1.0, 0.0, 1.0)), f.x), mix(aHash(i + vec3(0.0, 1.0, 1.0)), aHash(i + vec3(1.0, 1.0, 1.0)), f.x), f.y), f.z); }
// speckle spots: each cell of a jittered grid may hold one soft round spot (its size and whether it is there are random; dens is the share
// of cells that have one); a little noise breaks the circles; spots smaller than a pixel fade to their average cover instead of shimmering
float aSpots(vec3 p, float scale, float dens, float rmin, float rmax) {
  vec3 q = p * scale, i = floor(q), f = fract(q); float cov = 0.0, wob = (aNoise(q * 2.7) - 0.5) * 0.16, fw = length(fwidth(q));
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
    vec3 o = vec3(float(x), float(y), float(z)), c = i + o; float pres = aHash(c + 17.31);
    if (pres > dens) continue;
    vec3 hp = aHash3(c); float r = mix(rmin, rmax, fract(pres * 7.13 + hp.x * 3.1)), dd = length(o + 0.2 + 0.6 * hp - f) + wob;
    float aa = 0.5 * fw + 0.02; cov = max(cov, 1.0 - smoothstep(r - aa, r + aa, dd));
  }
  float mean = dens * 3.1416 * (rmin + rmax) * (rmin + rmax) * 0.25 * 1.2;
  return mix(cov, min(mean, 1.0), smoothstep(0.35, 0.9, fw));
}
// bump from a height in metres, with the exact slope (unnormalized derivatives, as the game's skin bump): the same relief at any distance
vec3 aBump(vec3 sp, vec3 sn, float h) { vec3 dpx = dFdx(sp), dpy = dFdy(sp), r1 = cross(dpy, sn), r2 = cross(sn, dpx); float det = dot(dpx, r1);
  if (abs(det) < 1e-14) return sn; vec3 g = (dFdx(h) * r1 + dFdy(h) * r2) / det; float gl = length(g); if (gl > 0.9) g *= 0.9 / gl; return normalize(sn - g); }
vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.2); }
float fCone(vec2 p, vec2 a, vec2 b, float w0, float w1) { vec2 ab = b - a; float t = clamp(dot(p - a, ab) / dot(ab, ab), 0.0, 1.0); float d = length(p - a - ab * t) - mix(w0, w1, t); return 1.0 - smoothstep(-0.004, 0.012, d); }
float coatField(vec3 sp, float sy){ vec3 cq = sp * 5.0 + uCoat.y;
  float ch = 0.5 + 0.25 * sin(cq.x * 1.7 + sin(cq.y * 2.3)) * sin(cq.z * 1.9 + sin(cq.x * 1.3)) + 0.25 * sin(cq.y * 3.1 + cq.z * 1.1 + cq.x * 0.7);
  return clamp(0.55 * ch + 0.45 * sy, 0.0, 1.0); }`;
// the skin: base tone, dorsal mottling, the belly, the tail fin's bands, spots, gill frills, cavities
const SKIN_FS = `
{
  vec3 cp = vCp; float belly = vJelly.x, tail = vJelly.y, thin = vJelly.z;
  float ao = vFill.z, finh = vMat.x, gill = vMat.y, sd = vMat.w;
  float n1 = aNoise(cp * 4.2), n2 = aNoise(cp * 11.0 + 7.1), n3 = aNoise(cp * 31.0 + 3.7);
  vec3 col; float gk;
#ifdef USE_MAP
  // the baked texture is the skin (v8): its light and dark are kept; its pink follows the look's colour by a turn of the texel's chroma
  // about its share of the native pink (uTint: the native chroma direction, the chroma gain, on; uTintTo: the look's direction, its
  // lightness ratio), so the white belly, the blue fin and the dark of the spots keep their own colour under every look
  col = diffuseColor.rgb;
  float Y = dot(col, vec3(0.2126, 0.7152, 0.0722)); vec2 ch = vec2(col.r - Y, col.b - Y);
  float a = dot(ch, uTint.xy), w = smoothstep(0.02, 0.1, a) * uTint.w; vec2 res = ch - a * uTint.xy;
  ch = mix(ch, res + a * uTint.z * uTintTo.xy, w); Y *= mix(1.0, uTintTo.z, w * 0.35);
  float cr = Y + ch.x, cb = Y + ch.y; col = max(vec3(cr, (Y - 0.2126 * cr - 0.0722 * cb) / 0.7152, cb), vec3(0.0));
  float bk = smoothstep(0.1, 0.85, belly); sBelly = bk;
  float core = tail * exp(-pow((finh - 0.4) / 0.19, 2.0)), glowE = tail * (1.0 - smoothstep(0.0, 0.24, finh)); sFin = max(core, glowE);
  col = mix(col, uFinGlow, 0.1 * glowE); sSpot = 0.0;
  col *= 1.0 + 0.06 * bk;   // (the cream belly a touch brighter under the game's warm ground light)
  gk = smoothstep(0.35, 0.8, gill);   // (the stalks keep the skin's pink; the thin fronds take the frill colour)
#else
  col = uSkin * (0.9 + 0.14 * n1 + 0.06 * n2);
  float mot = smoothstep(0.5, 0.78, aNoise(cp * 7.5 + 11.0)) * (1.0 - belly) * (1.0 - gill);   // soft darker patches on the back
  col *= 1.0 - 0.1 * mot;
  float bk = smoothstep(0.1, 0.85, belly + 0.1 * (n2 - 0.5)); col = mix(col, uBelly * (0.96 + 0.06 * n1), bk); sBelly = bk;
  // the tail fin: a darker blue-grey core band, the lower edge glowing, the spotted upper crest stays skin
  float core = tail * exp(-pow((finh - 0.4) / 0.19, 2.0)), glowE = tail * (1.0 - smoothstep(0.0, 0.24, finh));
  col = mix(col, uFinCore * (0.9 + 0.2 * n2), 0.78 * core); col = mix(col, uFinGlow, 0.5 * glowE); sFin = max(core, glowE);
  // speckle spots, two sizes (the canonical body's metres: the standing body is 1.75 tall)
  float dens = sd * uDetail.z;
  float sp = max(aSpots(cp, uDetail.y, 0.7 * dens, 0.17, 0.36), 0.92 * aSpots(cp + 9.7, uDetail.y * 2.3, 0.78 * dens, 0.15, 0.3));
  sp *= 1.0 - 0.75 * bk; col = mix(col, uSpot * (0.82 + 0.36 * n3), sp); sSpot = sp;
  gk = gill;
#endif
  // the gill frills: saturated, lighter toward the thin tips, fine filament streaks
  float fil = 0.5 + 0.5 * sin(vAlong * 480.0 + n2 * 8.0 + n3 * 4.0); fil = mix(0.5, fil, 1.0 - smoothstep(0.12, 0.3, fwidth(vAlong) * 480.0 / 6.2832));
#ifdef USE_MAP
  vec3 gc = mix(uGill * (0.9 + 0.2 * n2), uGillTip, clamp(0.55 * vFill.w, 0.0, 1.0));   // (no filament bands: across the frond they read as stripes)
#else
  vec3 gc = mix(uGill * (0.9 + 0.2 * n2), uGillTip, clamp(0.55 * vFill.w + 0.08 * fil * gill, 0.0, 1.0));
#endif
  col = mix(col, gc, gk); sGill = gill;
#ifdef USE_MAP
  col *= 1.0 - 0.1 * ao;
#else
  col *= 1.0 - 0.18 * ao;
#endif
  sAO = ao;
  diffuseColor.rgb = col;
}`;
// the face: the game's slime face shader (eye layer or blink, the eye styles, pupils where the whites show, then the mouth)
const FACE_FS = `
if (vFace.z > 0.01 && abs(vFace.x * fComp.x) < 0.985 && abs(vFace.y * fComp.y) < 0.985) {
  vec2 fq = vFace.xy * fComp.xy; vec2 cuv = fq * 0.5 + 0.5;
  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = (fStyle > 2.5 && fStyle < 3.5) ? 1.0 : 0.0, sly = fStyle > 3.5 ? 1.0 : 0.0; vec2 fqe = fq; if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.1 + 0.01; l.x = (l.x + l.y * sd0 * 0.2) * 0.97; fqe = pc0 + l; }
  vec2 cuvE = fqe * 0.5 + 0.5;
  vec4 eA = texture2D(fCol, fCell(fCells.x, cuvE)), eB = texture2D(fCol, fCell(fCells.z, cuvE)), eye = mix(eA, eB, fMix.x);
  vec3 emL = mix(texture2D(fMsk, fCell(fCells.x, cuvE)).rgb, texture2D(fMsk, fCell(fCells.z, cuvE)).rgb, fMix.x); vec2 em = emL.rg;
  vec4 bl = texture2D(fCol, fCell(fMix.w, cuvE)); eye = mix(eye, bl, fMix.y); em *= 1.0 - fMix.y;
  float dotK = 0.0; if (fStyle > 1.5 && fStyle < 2.5) { eye.a = 0.0; em = vec2(0.0); }
  if (zmb > 0.5) eye.rgb = eye.rgb * vec3(0.78, 0.9, 0.6) + vec3(0.05, 0.06, 0.0) * eye.a;
  float lsh = 0.0; if (fLash.x + fLash.y > 0.0) lsh = mix(emL.b, texture2D(fMsk, fCell(fMix.w, cuvE)).b, fMix.y) * (fq.x < 0.0 ? fLash.x : fLash.y);
  vec3 c = mix(diffuseColor.rgb, eye.rgb, eye.a);
  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.05, sin(a) * 0.052 + 0.026))).a); }
    float hole = texture2D(fCol, fCell(0.0, cuvE)).a, rim = clamp(d1 - hole, 0.0, 1.0), sp = 0.0;
    for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16); vec2 dw = normalize(vec2(sd, 0.45)); vec2 a = pc + dw * 0.18, b = a + dw * 0.26; sp = max(sp, fCone(fqe, a, b, 0.1, 0.004)); }
    float mk = max(rim, sp); c = mix(c, vec3(0.03, 0.012, 0.02), mk);
    float lidLine = eye.a * step(dot(eye.rgb, vec3(0.333)), 0.3); c = mix(c, vec3(0.03, 0.012, 0.02), hole * (1.0 - eye.a) * (1.0 - mk)); c = mix(c, vec3(0.46, 0.3, 0.38), hole * lidLine * (1.0 - mk)); dotK = max(mk, hole * (1.0 - eye.a)); }
  if (fStyle > 1.5 && fStyle < 2.5) { float bk = 1.0 - fMix.y * 0.92; for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy * 0.6; vec2 dd = (fq - pc) * vec2(1.0, 1.0 / max(0.08, bk)); float r = length(dd);
    float dk = 1.0 - smoothstep(0.125, 0.145, r); c = mix(c, vec3(0.03, 0.012, 0.02), dk); float hl = 1.0 - smoothstep(0.03, 0.046, length((fq - pc - vec2(-0.045, 0.05)) * vec2(1.0, 1.0 / max(0.08, bk)))); c = mix(c, vec3(1.0), hl * dk); dotK = max(dotK, dk); } }
  for (int i = 0; i < 2; i++) {
    float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.235, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.92 : 1.14, zmb), rp = mix(0.092, 0.11, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb) * mix(1.0, 0.66, sly);
    vec3 irC = mix(fIris, vec3(0.42, 0.6, 0.3), zmb); irC = mix(irC, mix(fIris, vec3(0.86, 0.85, 0.9), 0.74), sly);
    float ia = (1.0 - smoothstep(ri - 0.014, ri, r)) * em.r;
    vec3 ic = mix(irC, irC * 0.2, smoothstep(0.0, ri, r)); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - 0.012, rp, r));
    ic += irC * 1.12 * smoothstep(ri * 0.35, ri * 0.95, r) * smoothstep(0.2, -0.6, dd.y / ri) * (1.0 - smoothstep(ri * 0.95, ri, r));
    ic = mix(ic, vec3(0.72, 0.78, 0.62), zmb * 0.42 * smoothstep(rp, ri * 0.9, r) * (0.6 + 0.4 * sin(atan(dd.y, dd.x) * 11.0 + r * 60.0)));
    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r));
    ic = mix(ic, vec3(0.3, 0.17, 0.2), sly * (1.0 - smoothstep(0.006, 0.02, abs(r - ri * 0.93))) * smoothstep(0.3, -0.4, dd.y / ri)); ic = mix(ic, vec3(0.42, 0.19, 0.2), sly * (1.0 - smoothstep(rp - 0.012, rp, r)));
    c = mix(c, ic * (1.0 - 0.55 * em.g), ia);
    float cl = (1.0 - smoothstep(mix(0.03, 0.05, sqd), mix(0.042, 0.06, sqd), length(fqe - pc - vec2(-0.055, 0.06) * (1.0 + 0.3 * sqd) * fPupil.z))) + 0.8 * (1.0 - sqd) * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z)));
    c = mix(c, vec3(1.0), clamp(cl, 0.0, 1.0) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g));
  }
  if (zmb > 0.5) { for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w), dd = fq - pc; float r = length(dd), an = atan(dd.y, dd.x);
      float vn = smoothstep(0.86, 0.99, sin(an * 7.0 + sin(r * 38.0 + an * 3.0) * 0.7 + sd * 1.3)) * smoothstep(0.12, 0.2, r) * (1.0 - smoothstep(0.3, 0.42, r)); c = mix(c, vec3(0.55, 0.03, 0.04), vn * eye.a * (1.0 - em.r * 0.7));
      float lidY = pc.y + (i == 0 ? 0.05 : 0.13) - sd * dd.x * 0.22, lid = eye.a * smoothstep(lidY - 0.012, lidY + 0.012, fq.y), crease = eye.a * (1.0 - smoothstep(0.0, 0.03, abs(fq.y - lidY)));
      c = mix(c, vec3(0.1, 0.045, 0.08), lid); c = mix(c, vec3(0.36, 0.2, 0.28), crease * 0.9);
      float ring = (1.0 - eye.a) * smoothstep(0.52, 0.3, length(dd * vec2(0.9, 1.35))) * smoothstep(0.02, -0.2, dd.y); c = mix(c, c * vec3(0.42, 0.34, 0.5), ring * 0.8); } }
  if (sly > 0.5) { for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w), dd = fq - pc; float ox = dd.x * sd, aw = fwidth(fq.y) + 0.003, side = step(0.0, fq.x * sd);
      float lidY = pc.y + 0.0 - 0.11 * ox - 0.12 * fMix.y, wht = eye.a * side;
      float sh = side * (1.0 - wht) * (1.0 - smoothstep(0.04, 0.27, length((dd - vec2(sd * 0.03, 0.11)) * vec2(0.85, 1.55)))); c = mix(c, c * vec3(0.95, 0.6, 0.72), 0.85 * sh);
      float lid = wht * smoothstep(lidY - aw, lidY + aw, fq.y); c = mix(c, mix(vec3(0.5, 0.22, 0.33), vec3(0.66, 0.34, 0.45), smoothstep(lidY, lidY + 0.07, fq.y)), lid);
      float ll = wht * (1.0 - smoothstep(0.019, 0.019 + aw * 2.0, abs(fq.y - lidY + 0.006)));
      float wy = pc.y + 0.0 - 0.11 * 0.18 - 0.12 * fMix.y, wing = side * fCone(fq, vec2(pc.x + sd * 0.16, wy - 0.004), vec2(pc.x + sd * 0.32, wy + 0.085), 0.026, 0.003);
      float brow = side * max(fCone(fq, vec2(sd * 0.14, pc.y + 0.22), vec2(sd * 0.46, pc.y + 0.35), 0.048, 0.04), fCone(fq, vec2(sd * 0.46, pc.y + 0.35), vec2(sd * 0.67, pc.y + 0.29), 0.04, 0.014));
      c = mix(c, vec3(0.05, 0.015, 0.03), max(ll, wing)); c = mix(c, vec3(0.45, 0.17, 0.24), brow); dotK = max(dotK, max(max(ll, wing), max(brow, lid))); } }
  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);
  if (fLash.z > 0.0) {
    vec2 sdv = normalize(vec2(1.9, -0.8)); float sb = abs(dot(fq - vec2(-0.92, 0.74), vec2(-sdv.y, sdv.x))), saa = fwidth(sb) * 1.25 + 1e-4, sfd = (1.0 - smoothstep(0.88, 0.97, max(abs(fq.x), abs(fq.y)))) * fLash.z;
    float band = (1.0 - smoothstep(0.042 - saa, 0.042 + saa, sb)) * sfd, bed = (1.0 - smoothstep(0.058 - saa, 0.058 + saa, sb)) * sfd;
    c = mix(c, vec3(0.016, 0.0025, 0.007), bed); c = mix(c, mix(vec3(0.04, 0.025, 0.032), vec3(0.1, 0.07, 0.08), 1.0 - smoothstep(0.0, 0.03, sb)), band);
    vec2 pq = (fq - vec2(0.4, 0.15)) / vec2(0.37, 0.4); float pr = length(vec2(pq.x, pq.y * (pq.y > 0.0 ? 1.1 : 0.94))), pa = fwidth(pr) * 1.25 + 1e-4;
    float pb = (1.0 - smoothstep(1.0 - pa, 1.0 + pa, pr)) * fLash.z;
    vec3 pcol = mix(vec3(0.03, 0.019, 0.025), vec3(0.075, 0.05, 0.06), smoothstep(0.79 - pa, 0.84 + pa, pr));
    float sh = 1.0 - smoothstep(0.0, 0.52, length(pq - vec2(-0.3, 0.36))); pcol += vec3(0.3, 0.28, 0.32) * sh * sh * 0.65;
    float stc = step(0.55, fract(atan(pq.y, pq.x) * 4.4)) * (1.0 - smoothstep(0.016, 0.036, abs(pr - 0.895))); pcol = mix(pcol, vec3(0.42, 0.33, 0.26), stc * 0.75);
    float pin = smoothstep(0.93 - pa, 0.95 + pa, pr) * (1.0 - smoothstep(1.06 - pa, 1.08 + pa, pr)) * fLash.z;
    c = mix(c, pcol, pb); c = mix(c, vec3(0.016, 0.0025, 0.007), pin * 0.95); em.r *= 1.0 - pb; lsh = max(lsh, max(max(bed, pb), pin));
  }
  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv)), mB = texture2D(fCol, fCell(fCells.w, cuv)), mo = mix(mA, mB, fMix.x) * fMix.z * (1.0 - zmb);
  c = mix(c, mo.rgb, mo.a);
  float zma = 0.0; if (zmb > 0.5) { float yl = -0.3 + 0.08 * fq.x - 0.12 * fq.x * fq.x, dl = fq.y - yl, inx = smoothstep(0.48, 0.44, abs(fq.x)), fw = fwidth(fq.y) + 0.004;
    float line = (1.0 - smoothstep(0.02 - fw, 0.02 + fw, abs(dl))) * inx, st = (1.0 - smoothstep(0.01, 0.01 + fw, abs(mod(fq.x + 0.075, 0.15) - 0.075))) * (1.0 - smoothstep(0.06, 0.06 + fw, abs(dl))) * inx * step(0.08, abs(fq.x));
    float tooth = 0.0; for (int i = 0; i < 3; i++) { float cx = i == 0 ? -0.2 : i == 1 ? 0.03 : 0.24, w = 0.036 * (1.0 - clamp(-dl / 0.09, 0.0, 1.0)); tooth = max(tooth, (1.0 - smoothstep(w - fw, w + fw, abs(fq.x - cx))) * step(-0.09, dl) * step(dl, 0.0)); }
    zma = max(line, st); c = mix(c, vec3(0.03, 0.012, 0.02), zma); c = mix(c, vec3(0.93, 0.9, 0.78), tooth * (1.0 - line)); zma = max(zma, tooth); }
  faceInk = max(max(max(max(eye.a, mo.a), lsh), dotK), zma) * vFace.z; diffuseColor.rgb = mix(diffuseColor.rgb, c, vFace.z); sEyeM = em.r * vFace.z;
}
sDrawM = faceInk;`;
// the paint coat: rising by the fill order (the crawl's from the ground contacts, the stand's from the feet), in lumps; wet paint levels the skin
const COAT_FS = `
if (uCoat.x > 0.001 || uCoat.w > 0.001) {
  float ch = coatField(vCp, vFillO), cv = uCoat.x * 1.08 - 0.04, cOn = step(0.001, uCoat.x), wOn = step(0.001, uCoat.w);
  sCoatM = smoothstep(ch - 0.035, ch + 0.035, cv) * cOn;
  float wv = uCoat.w - vFillO + 0.02 * sin(vCp.x * 31.0 + vCp.z * 17.0 + uCoat.y) + 0.012 * sin(vCp.z * 53.0 - vCp.x * 23.0 + uCoat.y * 0.7);
  float wm = smoothstep(-0.007, 0.007, wv) * wOn, we = (1.0 - smoothstep(0.0, 0.028, abs(wv))) * wOn * (1.0 - sCoatM);
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.1), vec3(0.0)) * 0.8;
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, sCoatM) * (1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.06, abs(cv - ch))) * step(uCoat.x, 0.995) * cOn);
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, wm * (1.0 - sCoatM)) * (1.0 - 0.24 * we); sCoatM = max(sCoatM, wm);
  faceInk *= 1.0 - sCoatM; sDrawM = faceInk;
}`;
// the relief: bumpy amphibian skin and pores (softer on the belly and the face), wrinkle bands across the joints, the gill filaments,
// the spots a hair lower; flat under the paint; fine octaves fade out where a pixel covers them (no shimmer)
const BUMP_FS = `
{
  vec3 cp = vCp; float fw = length(fwidth(cp)), k1 = 1.0 - smoothstep(0.25, 0.8, fw * 140.0), k2 = 1.0 - smoothstep(0.25, 0.8, fw * 330.0), k3 = 1.0 - smoothstep(0.25, 0.8, fw * 2.0 / 0.011);
  float amp = uDetail.x * (1.0 - 0.6 * sBelly) * (1.0 - 0.8 * faceInk) * (1.0 - sCoatM);
#ifdef USE_MAP
  amp *= 0.5;
#endif
  float h = (aNoise(cp * 140.0) * 0.65 * k1 + aNoise(cp * 330.0 + 5.0) * 0.35 * k2) * amp;
  // (the bands and filaments also fade where the arc coordinate itself runs fast across a pixel, at the tips of fingers and toes say, where
  // they would otherwise alias into a moire)
  float fa = fwidth(vAlong), kw = 1.0 - smoothstep(0.12, 0.3, fa * 571.2 / 6.2832), kg = 1.0 - smoothstep(0.12, 0.3, fa * 480.0 / 6.2832);
  h += uDetail.w * vMat.z * k3 * kw * (0.5 + 0.5 * sin(vAlong * 571.2 + aNoise(cp * 60.0) * 2.5)) * (1.0 - sCoatM) * (1.0 - faceInk);
  h += 0.05 * uDetail.x * sGill * (0.5 + 0.5 * sin(vAlong * 480.0 + aNoise(cp * 11.0 + 7.1) * 8.0)) * k3 * kg;
  h -= 0.5 * uDetail.x * sSpot;
  normal = aBump(-vViewPosition, normal, h);
}`;
const LIT_FS = `
{ float wet = max(sCoatM, 0.45 * uCoat.z);
  float rough = mix(0.52, 0.32, sBelly); rough = mix(rough, 0.52, sGill * 0.7); rough = mix(rough, 0.34, sFin * 0.6); rough = mix(rough, 0.72, sDrawM);
  material.roughness = min(max(mix(rough, 0.16, wet), 0.0525) + geometryRoughness, 1.0);
#ifdef USE_CLEARCOAT
  material.clearcoat = mix(0.12 + 0.28 * sBelly + 0.12 * sFin, 1.0, sCoatM) * (1.0 - 0.9 * sDrawM);
  material.clearcoatRoughness = min(max(mix(0.46 - 0.18 * sBelly, 0.07, sCoatM), 0.0525) + geometryRoughness, 1.0);
#endif
#ifdef USE_SHEEN
  material.sheenColor = uBelly * (0.5 * sBelly + 0.15 * sGill) * (1.0 - sCoatM); material.sheenRoughness = 0.42;
#endif
}`;
const LOOK_FS = `
{ float occ = sAO * (1.0 - 0.3 * sCoatM), ink = sDrawM * (1.0 - sCoatM);
  reflectedLight.indirectDiffuse *= 1.0 - 0.5 * occ; reflectedLight.directDiffuse *= 1.0 - 0.2 * occ; reflectedLight.indirectSpecular *= 1.0 - 0.7 * occ; reflectedLight.directSpecular *= 1.0 - 0.4 * occ;
#ifdef USE_CLEARCOAT
  clearcoatSpecularIndirect *= 1.0 - 0.85 * occ; clearcoatSpecularDirect *= 1.0 - 0.6 * occ;
#endif
  // the drawn face: matte ink, lit a little from within like the game's (it reads at any light)
  reflectedLight.directDiffuse *= 1.0 - 0.45 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.45 * ink; reflectedLight.directSpecular *= 1.0 - 0.9 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.9 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.5;
  // light through the thin parts (fin, frills, toe tips), in the skin's own deeper colour; the free edges of fins and frills lit
  vec3 vd = normalize(vViewPosition), kd = normalize(uKeyDir);
  float thin = vJelly.z * (1.0 - sCoatM) * (1.0 - ink);
  float back = pow(saturate(dot(vd, -normalize(kd + nonPerturbedNormal * 0.35))), 3.0), wrap = saturate((dot(nonPerturbedNormal, kd) + 0.75) / 1.75);
  vec3 deep = pow(max(diffuseColor.rgb, vec3(0.0)), vec3(1.35)) * 1.7;
  // and on the side away from the light, the light that came through (view-independent: the shadow side of a fin glows instead of going
  // dark, which is what reads as translucent from any angle)
  float through = saturate(-dot(nonPerturbedNormal, kd));
  totalEmissiveRadiance += deep * thin * (1.0 * back + 0.2 * wrap + 0.55 * through) * (1.0 - 0.4 * sGill);
  float edge = 1.0 - saturate(dot(nonPerturbedNormal, vd));
#ifdef USE_MAP
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0), 0.35) * vFill.w * (0.2 + 0.8 * back) * 0.6 * (1.0 - sCoatM) * (1.0 - ink);
#else
  totalEmissiveRadiance += mix(diffuseColor.rgb, uFinGlow, 0.5) * vFill.w * (0.18 + 0.7 * back) * 0.55 * (1.0 - sCoatM) * (1.0 - ink);
#endif
  // a soft rim along the body's outline, a whisper of light on the moist skin
  float upk = saturate(dot(nonPerturbedNormal, normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)) + 0.4);
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.92), 0.35) * pow(edge, 3.0) * (0.5 + 0.5 * upk) * 0.22 * (1.0 - ink) * (1.0 - 0.5 * sCoatM);
}`;
// a mesh fading in or out (the stand / crawl swap): a screen-space dither, so it is always drawn opaque and sorted right
// two ways a mesh shares the screen with the other one, both by a screen-space dither (always opaque, sorted right, no see-through double
// image): uFadeK >= 0 keeps the pixels whose threshold is under it, < 0 the others (a plain complementary dissolve); during the stand <->
// crawl morph (uSwap.x on) the crawl's share depends on where on the body the pixel is: each region changes over at the point of the morph
// (uSwap.y, the skeleton's crawl share) where both bodies are clean there: the hips, legs and tail early, the chest, arms and head late.
// The canonical place (vCp) is the same body point on both meshes, so the two stay complementary
const FADE_FS = `
{ vec2 fp = floor(gl_FragCoord.xy); float th = fract(52.9829189 * fract(dot(fp, vec2(0.06711056, 0.00583715))));
  if (uSwap.x > 0.5) {
    float tau = clamp((vCp.y - 0.55) / 0.35, 0.0, 1.0) * (1.0 - smoothstep(-0.25, -0.45, vCp.z)), lo = uSwap.z + uSwap.w * tau;
    float c = smoothstep(lo, lo + 0.12, uSwap.y);
    if (uIsCrawl > 0.5 ? th >= c : th < c) discard;
  } else if (uFadeK < 0.999) { if (uFadeK >= 0.0 ? th >= uFadeK : th < -uFadeK) discard; } }`;
// debug views (the material breakdown): 1 roughness, 2 the detail normal under one light, 3 occlusion, 4 regions (belly red / thin green / gill blue), 5 spots, 6 canonical place
const DEBUG_FS = `
if (uDebug > 0.5) {
  if (uDebug < 1.5) gl_FragColor = vec4(vec3(material.roughness), 1.0);
  else if (uDebug < 2.5) { float l = 0.15 + 0.85 * max(0.0, dot(normal, normalize(vec3(0.4, 0.7, 0.6)))); gl_FragColor = vec4(vec3(l), 1.0); }
  else if (uDebug < 3.5) gl_FragColor = vec4(vec3(1.0 - sAO), 1.0);
  else if (uDebug < 4.5) gl_FragColor = vec4(sBelly, vJelly.z, sGill, 1.0);
  else if (uDebug < 5.5) gl_FragColor = vec4(vec3(1.0 - sSpot), 1.0);
  else gl_FragColor = vec4(fract(vCp * 4.0), 1.0);
}`;

// ---------------- the palette: every colour from the team colour ----------------
const _c = new THREE.Color(), _hsl = {};
function hsl(h, s, l) { return new THREE.Color().setHSL(((h % 1) + 1) % 1, Math.max(0, Math.min(1, s)), Math.max(0, Math.min(1, l))); }
function mixHue(a, b, t) { let d = b - a; d -= Math.round(d); return a + d * t; }
function palette(team) {
  _c.set(team); _c.getHSL(_hsl); const h = _hsl.h, s = _hsl.s, l = _hsl.l;
  const slate = 0.64;   // blue-grey
  return {
    skin: hsl(h, 0.5 + 0.2 * s, 0.55 + 0.04 * (l - 0.5)),
    belly: hsl(mixHue(h, 0.09, 0.78), 0.6, 0.72),
    spot: hsl(mixHue(h, slate, 0.72), 0.26, 0.26),
    gill: hsl(h, 0.72 + 0.28 * s, 0.44),
    gillTip: hsl(mixHue(h, 0.97, 0.15), 0.65, 0.7),
    finCore: hsl(mixHue(h, slate, 0.75), 0.3, 0.25),
    finGlow: hsl(mixHue(h, 0.04, 0.45), 0.85, 0.58),
  };
}
// the texture's own pink (sRGB 0.98, 0.60, 0.66: the sculpt's flanks and limbs), in linear, and a colour's place in the opponent plane
const NATIVE_SKIN = new THREE.Color().setRGB(0.98, 0.60, 0.66, THREE.SRGBColorSpace), NATIVE_HUE = 0.975;
function chroma(c) { const Y = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b; return [c.r - Y, c.b - Y, Y]; }
let SHEETS = null;
function faceSheets(C) {
  if (SHEETS) return SHEETS; const sh = makeFaceSheets(C);
  const col = new THREE.CanvasTexture(sh.col), msk = new THREE.CanvasTexture(sh.msk); col.colorSpace = THREE.SRGBColorSpace; col.anisotropy = 4; msk.colorSpace = THREE.NoColorSpace;
  for (const t of [col, msk]) { t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; }
  return SHEETS = { col, msk };
}

// ---------------- the character's look: shared uniforms for its two meshes, the face's state ----------------
class Look {
  constructor(opts = {}) {
    const sh = faceSheets(opts.faceCell || 320), v3 = () => ({ value: new THREE.Color() });
    this.U = {
      uSkin: v3(), uBelly: v3(), uSpot: v3(), uGill: v3(), uGillTip: v3(), uFinCore: v3(), uFinGlow: v3(), uTeam: v3(),
      uPaint: { value: new THREE.Color(opts.color || 0xff6b8a) }, uCoat: { value: new THREE.Vector4(0, Math.random() * 40, 0, 0) }, uCoatMix: { value: 1 },
      uJelly: { value: new THREE.Vector4(0, 0, 1.6, 0) }, uLag: { value: new THREE.Vector4(0, 0, 0, 0) }, uFaceP: { value: new THREE.Vector4(FACE.pitch, FACE.half, FACE.squeeze, 1) },
      fCol: { value: sh.col }, fMsk: { value: sh.msk }, fCells: { value: new THREE.Vector4(0, 8, 0, 8) }, fMix: { value: new THREE.Vector4(0, 0, 1, 6) }, fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) },
      fComp: { value: new THREE.Vector4(1, 1, 0, 0) }, fLash: { value: new THREE.Vector4(0, 0, 0, 0) }, fIris: { value: new THREE.Vector3(0.14, 0.045, 0.28) }, fStyle: { value: 0 },
      uKeyDir: { value: new THREE.Vector3(0.3, 0.6, 0.7) }, uDebug: { value: 0 }, uSwap: { value: new THREE.Vector4(0, 0, 0.18, 0.26) },
      // skin detail: x relief amplitude (m), y spot cells per metre, z spot amount, w wrinkle depth (m)
      uDetail: { value: new THREE.Vector4(0.0009, 26, 1.0, 0.0007) }, uDetail2: { value: new THREE.Vector4(0, 0, 0, 0) },
      uTint: { value: new THREE.Vector4(1, 0, 1, 1) }, uTintTo: { value: new THREE.Vector4(1, 0, 1, 0) },
    };
    this.meshU = {};   // per-mesh uniforms (the fade), by mesh name
    this.fangs = false; this.expr = 'neutral'; this.exprB = 'neutral'; this.exprK = 1; this.blinkT = 1 + Math.random() * 2; this.blinkK = 0; this.flut = 0; this.flutT = 0;
    this.look = [0, 0]; this.dart = [0, 0]; this.dartT = 0.5; this.att = { t: 1 + Math.random() * 2, eye: [0, 0] }; this.t = 0; this.emote = null; this.turnV = 0; this.tbCool = 0;
    this.setColor(opts.color || 0xff6b8a); this.setIris(opts.iris || 'violet'); this.setEyeStyle(opts.eyes || 'round');
  }
  setColor(c) { const p = palette(c); const U = this.U; U.uTeam.value.set(c); U.uPaint.value.set(c);
    for (const [k, u] of [['skin', 'uSkin'], ['belly', 'uBelly'], ['spot', 'uSpot'], ['gill', 'uGill'], ['gillTip', 'uGillTip'], ['finCore', 'uFinCore'], ['finGlow', 'uFinGlow']]) U[u].value.copy(p[k]);
    // the baked texture's pink turned to the team's hue (v8): a turn of the chroma in the opponent plane (r - Y, b - Y) by the angle between
    // the team hue and the native pink's, at the same saturation and lightness, so every look keeps all of the texture's light, dark and
    // detail; the red and pink teams sit on the native hue and get the texture as baked
    _c.set(c); _c.getHSL(_hsl); const c0 = chroma(NATIVE_SKIN), m0 = Math.hypot(c0[0], c0[1]), d0 = [c0[0] / m0, c0[1] / m0];
    const ang = h => { const q = chroma(hsl(h, 0.7, 0.6)); return Math.atan2(q[1], q[0]); }, th = ang(_hsl.h) - ang(NATIVE_HUE), cs = Math.cos(th), sn = Math.sin(th);
    U.uTint.value.set(d0[0], d0[1], 1, 1); U.uTintTo.value.set(cs * d0[0] - sn * d0[1], sn * d0[0] + cs * d0[1], 1, 0);
    return this; }
  setIris(k) { const e = EYE_COLS[k]; if (e) this.U.fIris.value.set(...e.lin); else { const c = new THREE.Color(k); this.U.fIris.value.set(c.r, c.g, c.b); } this.iris = k; return this; }
  setEyeStyle(k) { this.U.fStyle.value = typeof k === 'string' ? (EYE_STYLE_K[k] || 0) : k; return this; }
  setPaint(level) { this.U.uCoat.value.x = level; return this; }
  setFangs(on) { this.fangs = !!on; return this; }
  setLashes(l, r = l) { this.U.fLash.value.x = l; this.U.fLash.value.y = r; return this; }
  setExpression(name) { if (!(name in EXPR)) name = 'neutral'; if (name === this.exprB) return this; if (this.exprK < 1) this.expr = this.exprK > 0.5 ? this.exprB : this.expr; this.exprB = name; this.exprK = 0; return this; }
  // a short-lived expression (a reaction) that falls back to the current one
  emoteFor(name, dur = 0.8) { if (!this.emote) this.emote = { back: this.exprB }; this.emote.t = dur; this.setExpression(name); return this; }
  blink() { this.blinkK = 0.13; return this; }
  flutter(n = 3) { this.flut = n; this.flutT = 0; return this; }
  // (v6 put 3D eyes on the heads; v7 draws the game's eyes on the skin. Kept so v6 callers do not break: it does nothing.)
  attachEyes() { return this; }
  setFade(which, fade) { this.fades = this.fades || {}; this.fades[which] = fade; const u = this.meshU[which]; if (u) u.uFadeK.value = fade; }
  // the stand <-> crawl morph's change-over (u: the skeleton's crawl share; null: off). See FADE_FS
  setMorphSwap(u) { const S = this.U.uSwap.value; if (u === null || u === undefined) S.x = 0; else { S.x = 1; S.y = u; } }
  // the stand / crawl swap: k of the pixels show the incoming mesh, exactly the rest the outgoing one (complementary dither)
  setSwap(inc, out, k) { const a = this.meshU[inc], b = this.meshU[out]; if (a) a.uFadeK.value = k >= 0.999 ? 1 : Math.max(0, k); if (b) b.uFadeK.value = k <= 0.001 ? 1 : k >= 0.999 ? 0 : -k; }
  // the head's turn rate (rad/s) from the animator: a quick turn brings a blink, as the game's slime does
  turnRate(w) { this.turnV = w; }
  // per frame: expression crossfade and reactions, blinks (double blinks now and then, flutters, a blink with a fast turn), glances and darts,
  // pupils easing toward the look target (x right, y up, in face units), head squash compensation
  update(dt, look, squash = 0) {
    this.t += dt; const U = this.U;
    if (this.emote) { this.emote.t -= dt; if (this.emote.t <= 0) { const b = this.emote.back; this.emote = null; this.setExpression(b); } }
    if (this.exprK < 1) { this.exprK = Math.min(1, this.exprK + dt / 0.12); if (this.exprK >= 1) this.expr = this.exprB; }
    if (this.flut > 0) { this.flutT -= dt; if (this.flutT <= 0) { this.blinkK = 0.075; this.flut--; this.flutT = 0.15; this.blinkT = Math.max(this.blinkT, 1.4); } }
    this.tbCool -= dt; if (Math.abs(this.turnV) > 3.2 && this.tbCool <= 0) { this.blinkK = Math.max(this.blinkK, 0.11); this.tbCool = 1.4; }
    this.blinkT -= dt; if (this.blinkT <= 0) { this.blinkK = 0.13; this.blinkT = Math.random() < 0.22 ? 0.26 : 1.6 + Math.random() * 3.4; } if (this.blinkK > 0) this.blinkK -= dt;
    const A = this.att; A.t -= dt; if (A.t <= 0) { A.t = 1.2 + Math.random() * 2.8; A.eye[0] = (Math.random() * 2 - 1) * 0.1; A.eye[1] = (Math.random() * 2 - 1) * 0.045; if (Math.random() < 0.5) this.blinkK = Math.max(this.blinkK, 0.1); }
    this.dartT -= dt; if (this.dartT <= 0) { this.dartT = 0.35 + Math.random() * 0.9; this.dart[0] = (Math.random() * 2 - 1) * 0.035; this.dart[1] = (Math.random() * 2 - 1) * 0.02; }
    const lx = (look ? look[0] : 0) + A.eye[0] + this.dart[0], ly = (look ? look[1] : 0) + A.eye[1] + this.dart[1];
    this.look[0] += (lx - this.look[0]) * Math.min(1, dt * 26); this.look[1] += (ly - this.look[1]) * Math.min(1, dt * 26);
    const shut = this.blinkK > 0 && !NO_SHUT[this.exprB];
    const pa = pupilOf(this.expr), pb = pupilOf(this.exprB), k = this.exprK, fang = this.fangs ? 6 : 0, ea = EXPR[this.expr], eb = EXPR[this.exprB];
    U.fCells.value.set(ea[0], ea[1] + fang, eb[0], eb[1] + fang); U.fMix.value.set(k, shut ? 1 : 0, 1, 6);
    U.fPupil.value.set(this.look[0], this.look[1], pa.pu + (pb.pu - pa.pu) * k, pa.py + (pb.py - pa.py) * k);
    U.fComp.value.set(1, 1, 0, 0); U.uLag.value.w = this.t;
    if (this.coatMixT !== undefined) U.uCoatMix.value += (this.coatMixT - U.uCoatMix.value) * Math.min(1, dt * 3);
  }
}
// the body material for one mesh of one character (the look's uniforms are shared by the character's two meshes; the head frame, the
// canonical scale, the skinning data and the fade are this mesh's own)
function axoMaterial(tex, look, meta) {
  const mat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, map: tex || null, roughness: 0.5, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.35, sheen: 1, sheenRoughness: 0.42, sheenColor: 0x000000, envMapIntensity: 0.7 });
  const own = { uFadeK: { value: 1 }, uIsCrawl: { value: meta.name === 'crawl' ? 1 : 0 } }; look.meshU[meta.name || ('m' + Object.keys(look.meshU).length)] = own; meta.fadeU = own;
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, look.U, own);
    sh.vertexShader = VERT_PARS + '\n' + sh.vertexShader.replace('#include <skinning_vertex>', '#include <skinning_vertex>\n' + VERT_MAIN);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\n' + FRAG_PARS)
      .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n' + FADE_FS)
      .replace('#include <color_fragment>', '#include <color_fragment>\n' + SKIN_FS + FACE_FS + COAT_FS)
      .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\n' + BUMP_FS)
      .replace('#include <lights_physical_fragment>', '#include <lights_physical_fragment>\n' + LIT_FS)
      .replace('#include <aomap_fragment>', '#include <aomap_fragment>\n' + LOOK_FS)
      .replace('#include <colorspace_fragment>', '#include <colorspace_fragment>\n' + DEBUG_FS);
    if (meta.dqTex) dqsShader(sh, meta);
    const fc = (meta.face && meta.face.c) || meta.headAbs, fr = (meta.face && meta.face.r) || meta.headr;
    sh.uniforms.uHead = { value: new THREE.Vector4(fc[0], fc[1], fc[2], fr) }; sh.uniforms.uCpScale = { value: meta.cpScale || 4.0 };
  };
  mat.customProgramCacheKey = () => tex ? 'axo8-body' : 'axo7-body';
  return mat;
}

return { FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, pupilOf, FACE_EYE, FACE_KINDS, FACE_LIDS, makeFaceSheets, palette, Look, axoMaterial };
})();
const { FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, pupilOf, FACE_EYE, FACE_KINDS, FACE_LIDS, makeFaceSheets, palette, Look, axoMaterial } = __look;
return { DEG, loadMesh, texFromBytes, DQS_PARS, DQS_BASE, DQS_NORMAL, DQS_POS, dqsShader, dqsMaterial, Pose, LIMITS, limitsFor, Puppet, mirrorQ, rot, setRot, ease, Spring, Animator, FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, pupilOf, FACE_EYE, FACE_KINDS, FACE_LIDS, makeFaceSheets, palette, Look, axoMaterial, meshFrom };
})();
