// Roll Model axolotl runtime: mesh loader (.bin/.json/.webp), shared-skeleton Puppet with joint limits, procedural Animator.
// A pose = per-bone local rotation expressed in the bone's canonical frame (Y along the bone, Z = flexion / ventral side, X = Y x Z = hinge)
// plus a root position. Each mesh stores its own canonical rest frame per bone, so one pose can drive either mesh.
import * as THREE from 'three';
import { axoMaterial } from './look.js';

export const DEG = Math.PI / 180;
const _e = new THREE.Euler(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _m = new THREE.Matrix4();
const _m3a = new THREE.Matrix3(), _m3b = new THREE.Matrix3();
function addOuter(M, a, b) { const e = M.elements; e[0] += a.x * b.x; e[3] += a.x * b.y; e[6] += a.x * b.z; e[1] += a.y * b.x; e[4] += a.y * b.y; e[7] += a.y * b.z; e[2] += a.z * b.x; e[5] += a.z * b.y; e[8] += a.z * b.z; }
function addDiag(M, l) { const e = M.elements; e[0] += l; e[4] += l; e[8] += l; }
const _kq = new THREE.Quaternion(), _kq2 = new THREE.Quaternion(), _k1 = new THREE.Vector3(), _k2 = new THREE.Vector3(), _k3 = new THREE.Vector3(), _k4 = new THREE.Vector3(), _k5 = new THREE.Vector3(), _k6 = new THREE.Vector3(), _k7 = new THREE.Vector3(), _k8 = new THREE.Vector3();

export async function loadMesh(base, tex, matOpts = {}) {
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
  const mat = matOpts && matOpts.look ? axoMaterial(tex, matOpts.look, meta) : dqsMaterial(new THREE.MeshStandardMaterial(Object.assign({ map: tex, roughness: 0.6, metalness: 0 }, matOpts || {})), meta);
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(bones[0]); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false; mesh.castShadow = true;
  mesh.customDepthMaterial = dqsMaterial(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), meta);
  return { mesh, bones, byName, meta, F, rest, end, dq, dqTex, names: meta.bones.map(b => b.name), parent: meta.bones.map(b => b.parent ? pidx[b.parent] : -1) };
}

// ---- dual quaternion skinning (no candy-wrapper collapse at twisting / bending joints) ----
export const DQS_PARS = `
#ifdef USE_SKINNING
uniform highp sampler2D uDQ;
vec3 dqRot(vec4 q, vec3 v) { return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v); }
#endif`;
export const DQS_BASE = `
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
export const DQS_NORMAL = `
#ifdef USE_SKINNING
  objectNormal = dqRot(dqR, objectNormal);
  #ifdef USE_TANGENT
  objectTangent = dqRot(dqR, objectTangent);
  #endif
#endif`;
export const DQS_POS = `
#ifdef USE_SKINNING
  transformed = dqRot(dqR, transformed) + 2.0 * (dqR.w * dqD.xyz - dqD.w * dqR.xyz + cross(dqR.xyz, dqD.xyz));
#endif`;
export function dqsShader(sh, meta) {
  sh.uniforms.uDQ = { value: meta.dqTex };
  sh.vertexShader = sh.vertexShader.replace('#include <skinning_pars_vertex>', '#include <skinning_pars_vertex>\n' + DQS_PARS)
    .replace('#include <skinbase_vertex>', DQS_BASE).replace('#include <skinnormal_vertex>', DQS_NORMAL).replace('#include <skinning_vertex>', DQS_POS);
  return sh;
}
export function dqsMaterial(mat, meta) { const prev = mat.onBeforeCompile; mat.onBeforeCompile = (sh, r) => { if (prev) prev.call(mat, sh, r); dqsShader(sh, meta); }; mat.customProgramCacheKey = () => 'dqs-' + mat.type; return mat; }

export class Pose {
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
export const LIMITS = {
  hips: [[-40, 40], [-30, 30], [-25, 25]], spine: [[-25, 30], [-20, 20], [-20, 20]], spine1: [[-25, 30], [-20, 20], [-20, 20]], chest: [[-25, 25], [-20, 20], [-15, 15]],
  neck: [[-35, 35], [-30, 30], [-20, 20]], head: [[-40, 35], [-60, 60], [-30, 30]], headfront: [[0, 0], [0, 0], [0, 0]],
  shoulder: [[-15, 15], [-10, 10], [-15, 15]], upperarm: [[-70, 150], [-60, 60], [-30, 120]], forearm: [[-5, 135], [-70, 70], [-10, 10]], hand: [[-45, 60], [-30, 30], [-25, 25]],
  thigh: [[-45, 110], [-40, 40], [-25, 60]], shin: [[-5, 130], [-15, 15], [-8, 8]], foot: [[-35, 45], [-15, 15], [-20, 20]], toes: [[-25, 35], [0, 0], [-10, 10]],
  finger1: [[-15, 70], [0, 0], [-14, 14]], finger2: [[-5, 90], [0, 0], [0, 0]], toe1: [[-15, 70], [0, 0], [-12, 12]], toe2: [[-5, 80], [0, 0], [0, 0]],
  // the tail curls down a long way (hanging under the jetpack, tucked between the legs, laid on the floor in the crouch); the gill stalks
  // fold back flat along the head (the ground pound)
  tail1: [[-45, 105], [-15, 15], [-50, 50]], tail: [[-45, 80], [-15, 15], [-50, 50]], gill: [[-90, 70], [-15, 15], [-75, 75]],
};
export function limitsFor(name) {
  let L;
  if (name.startsWith('finger')) L = LIMITS['finger' + name.slice(-1)];
  else if (name.startsWith('toe') && !name.startsWith('toes')) L = LIMITS['toe' + name.slice(-1)];
  else if (name.startsWith('tail')) L = name === 'tail1' ? LIMITS.tail1 : LIMITS.tail; else if (name.startsWith('gill')) L = LIMITS.gill;
  else L = LIMITS[name.replace(/\.[LR]$/, '')] || [[-180, 180], [-180, 180], [-180, 180]];
  // right-side bones have mirrored frames: twist (y) and swing (z) change sign
  if (/\.R(\.|$)/.test(name)) L = [L[0], [-L[1][1], -L[1][0]], [-L[2][1], -L[2][0]]];
  return L;
}

export class Puppet {
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
export function mirrorQ(q, out) { return out.set(q.x, -q.y, -q.z, q.w); }
// rotate a pose bone by Euler degrees (XYZ) in its own frame, on top of what it has
export function rot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].multiply(_q2.setFromEuler(_e)); }
export function setRot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].setFromEuler(_e); }
