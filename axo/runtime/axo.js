// Roll Model axolotl runtime: mesh loader (.bin/.json/.webp), shared-skeleton Puppet with joint limits, procedural Animator.
// A pose = per-bone local rotation expressed in the bone's canonical frame (Y along the bone, Z = flexion / ventral side, X = Y x Z = hinge)
// plus a root position. Each mesh stores its own canonical rest frame per bone, so one pose can drive either mesh.
import * as THREE from 'three';
import { axoMaterial } from './look.js';

export const DEG = Math.PI / 180;
const _e = new THREE.Euler(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _m = new THREE.Matrix4();
const _kq = new THREE.Quaternion(), _kq2 = new THREE.Quaternion(), _k1 = new THREE.Vector3(), _k2 = new THREE.Vector3(), _k3 = new THREE.Vector3(), _k4 = new THREE.Vector3(), _k5 = new THREE.Vector3(), _k6 = new THREE.Vector3(), _k7 = new THREE.Vector3(), _k8 = new THREE.Vector3();

export async function loadMesh(base, tex, matOpts = {}) {
  const meta = await (await fetch(base + '.json')).json(), buf = await (await fetch(base + '.bin')).arrayBuffer();
  const n = meta.n, o = meta.off, g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o[0], n * 3), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o[1], n * 3), 3));
  g.setAttribute('uv', meta.uv16 ? new THREE.BufferAttribute(new Uint16Array(buf, o[2], n * 2), 2, true) : new THREE.BufferAttribute(new Float32Array(buf, o[2], n * 2), 2));
  g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o[3], n * 4), 4));
  g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o[4], n * 4), 4, true));
  g.setIndex(new THREE.BufferAttribute(meta.i32 ? new Uint32Array(buf, o[5], meta.ni) : new Uint16Array(buf, o[5], meta.ni), 1));
  if (o.length > 7) { g.setAttribute('jelly', new THREE.BufferAttribute(new Uint8Array(buf, o[6], n * 4), 4, true)); g.setAttribute('fill', new THREE.BufferAttribute(new Uint8Array(buf, o[7], n * 2), 2, true)); }
  else { g.setAttribute('jelly', new THREE.BufferAttribute(new Uint8Array(n * 4), 4, true)); g.setAttribute('fill', new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true)); }
  g.setAttribute('xtra', o.length > 8 ? new THREE.BufferAttribute(new Uint8Array(buf, o[8], n * 2), 2, true) : new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true));   // x ambient occlusion, y webbing
  const bones = [], byName = {}, F = [], rest = [], end = [];
  for (const b of meta.bones) { const bn = new THREE.Bone(); bn.name = b.name; bones.push(bn); byName[b.name] = bn; F.push(new THREE.Quaternion(...b.q)); rest.push(new THREE.Vector3(...b.pos)); end.push(new THREE.Vector3(...b.end)); }
  const pidx = {}; meta.bones.forEach((b, i) => pidx[b.name] = i);
  for (let i = 0; i < bones.length; i++) { const b = meta.bones[i], bn = bones[i]; if (b.parent) { byName[b.parent].add(bn); bn.position.copy(rest[i]).sub(rest[pidx[b.parent]]); } else bn.position.copy(rest[i]); }
  // the head centre in rest space (for the face projection) = the head joint + the exported offset
  const hb = meta.bones.find(b => b.name === 'head'); meta.headAbs = meta.headc ? [hb.pos[0] + meta.headc[0], hb.pos[1] + meta.headc[1], hb.pos[2] + meta.headc[2]] : hb.pos; meta.headr = meta.headr || 0.38;
  // the face frame: the vertical extent of the front of the head (dome top to chin, gills excluded), so face heights mean the same on a flat head and a round one
  { const pa = g.getAttribute('position'), ja = g.getAttribute('jelly'); let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < n; i++) { if (ja.getW(i) > 0.9 && pa.getZ(i) > meta.headAbs[2] + 0.15 * meta.headr) { const y = pa.getY(i); if (y < lo) lo = y; if (y > hi) hi = y; } }
    if (hi > lo) { meta.headMid = (lo + hi) / 2; meta.headH = (hi - lo) / 2; } else { meta.headMid = meta.headAbs[1]; meta.headH = meta.headr; } }
  const mat = matOpts && matOpts.look ? axoMaterial(tex, matOpts.look, meta) : new THREE.MeshStandardMaterial(Object.assign({ map: tex, roughness: 0.6, metalness: 0 }, matOpts || {}));
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(bones[0]); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false; mesh.castShadow = true;
  return { mesh, bones, byName, meta, F, rest, end, names: meta.bones.map(b => b.name), parent: meta.bones.map(b => b.parent ? pidx[b.parent] : -1) };
}

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
  tail: [[-35, 35], [-15, 15], [-45, 45]], gill: [[-35, 35], [-10, 10], [-35, 35]],
};
export function limitsFor(name) {
  let L;
  if (name.startsWith('finger')) L = LIMITS['finger' + name.slice(-1)];
  else if (name.startsWith('toe') && !name.startsWith('toes')) L = LIMITS['toe' + name.slice(-1)];
  else if (name.startsWith('tail')) L = LIMITS.tail; else if (name.startsWith('gill')) L = LIMITS.gill;
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
  }
  // write a pose into one mesh's bones (bones have identity rest rotations; world rotation of bone i = Fp_i * inverse(Fmesh_i))
  apply(which, pose) {
    const M = this.m[which], FM = M.F, Fp = this.Fp, R = this.R, par = this.par, bones = M.bones;
    for (let i = 0; i < this.nb; i++) {
      const p = par[i];
      if (p >= 0) Fp[i].copy(Fp[p]).multiply(this.Rel[i]).multiply(pose.q[i]); else Fp[i].copy(this.Rel[i]).multiply(pose.q[i]);
      R[i].copy(Fp[i]).multiply(_q.copy(FM[i]).invert());
      if (p >= 0) bones[i].quaternion.copy(R[p]).invert().multiply(R[i]); else { bones[i].quaternion.copy(R[i]); bones[i].position.copy(pose.root); }
    }
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
  ik2(which, pose, up, lo, en, target, pole, sU) {
    const M = this.m[which], pos = this.fk(which, pose), a = _k1.copy(pos[up]);
    const L1 = M.rest[lo].distanceTo(M.rest[up]), L2 = M.rest[en].distanceTo(M.rest[lo]);
    const n = _k2.copy(target).sub(a); let d = n.length(); n.normalize(); d = Math.min(Math.max(d, Math.abs(L1 - L2) + 0.01), (L1 + L2) * 0.985);
    const A = Math.acos(Math.min(1, Math.max(-1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))));
    const p = _k3.copy(pole).addScaledVector(n, -n.dot(pole)); if (p.lengthSq() < 1e-6) p.set(0, 1, 0).addScaledVector(n, -n.y); p.normalize();
    const yU = _k4.copy(n).multiplyScalar(Math.cos(A)).addScaledVector(p, Math.sin(A));
    const e = _k5.copy(a).addScaledVector(yU, L1), yL = _k6.copy(a).addScaledVector(n, d).sub(e).normalize();
    this.aim(pose, up, yU, _k7.copy(p).multiplyScalar(sU), false); this.aim(pose, lo, yL, _k8.copy(p).negate(), false);
    return d;
  }
  // world position of a joint of a mesh after apply()
  jointWorld(which, name, out) { const M = this.m[which]; M.mesh.updateMatrixWorld(true); return M.byName[name].getWorldPosition(out || new THREE.Vector3()); }
}
function clampDeg(rad, lim) { const d = rad / DEG; return (d < lim[0] ? lim[0] : d > lim[1] ? lim[1] : d) * DEG; }
export function mirrorQ(q, out) { return out.set(q.x, -q.y, -q.z, q.w); }
// rotate a pose bone by Euler degrees (XYZ) in its own frame, on top of what it has
export function rot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].multiply(_q2.setFromEuler(_e)); }
export function setRot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].setFromEuler(_e); }
