// Roll Model axolotl runtime: mesh loader (.bin/.json/.webp), shared-skeleton Puppet with joint limits, procedural Animator.
// A pose = per-bone local rotation expressed in the bone's canonical frame (Y along the bone, Z = flexion / ventral side, X = Y x Z = hinge)
// plus a root position. Each mesh stores its own canonical rest frame per bone, so one pose can drive either mesh.
import * as THREE from 'three';

export const DEG = Math.PI / 180;
const _e = new THREE.Euler(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _m = new THREE.Matrix4();
const _kq = new THREE.Quaternion(), _kq2 = new THREE.Quaternion(), _k1 = new THREE.Vector3(), _k2 = new THREE.Vector3(), _k3 = new THREE.Vector3(), _k4 = new THREE.Vector3(), _k5 = new THREE.Vector3(), _k6 = new THREE.Vector3(), _k7 = new THREE.Vector3(), _k8 = new THREE.Vector3();

export async function loadMesh(base, tex, matOpts = {}) {
  const meta = await (await fetch(base + '.json')).json(), buf = Uint8Array.from(atob((await (await fetch(base + '.b64.txt')).text()).trim()), c => c.charCodeAt(0)).buffer;
  const n = meta.n, o = meta.off, g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o[0], n * 3), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o[1], n * 3), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(buf, o[2], n * 2), 2));
  g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o[3], n * 4), 4));
  g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o[4], n * 4), 4, true));
  g.setIndex(new THREE.BufferAttribute(meta.i32 ? new Uint32Array(buf, o[5], meta.ni) : new Uint16Array(buf, o[5], meta.ni), 1));
  if (o.length > 7) { g.setAttribute('jelly', new THREE.BufferAttribute(new Uint8Array(buf, o[6], n * 4), 4, true)); g.setAttribute('fill', new THREE.BufferAttribute(new Uint8Array(buf, o[7], n * 2), 2, true)); }
  else { g.setAttribute('jelly', new THREE.BufferAttribute(new Uint8Array(n * 4), 4, true)); g.setAttribute('fill', new THREE.BufferAttribute(new Uint8Array(n * 2), 2, true)); }
  const bones = [], byName = {}, F = [], rest = [], end = [];
  for (const b of meta.bones) { const bn = new THREE.Bone(); bn.name = b.name; bones.push(bn); byName[b.name] = bn; F.push(new THREE.Quaternion(...b.q)); rest.push(new THREE.Vector3(...b.pos)); end.push(new THREE.Vector3(...b.end)); }
  const pidx = {}; meta.bones.forEach((b, i) => pidx[b.name] = i);
  for (let i = 0; i < bones.length; i++) { const b = meta.bones[i], bn = bones[i]; if (b.parent) { byName[b.parent].add(bn); bn.position.copy(rest[i]).sub(rest[pidx[b.parent]]); } else bn.position.copy(rest[i]); }
  // the head centre in rest space (for the face projection) = the head joint + the exported offset
  const hb = meta.bones.find(b => b.name === 'head'); meta.headAbs = meta.headc ? [hb.pos[0] + meta.headc[0], hb.pos[1] + meta.headc[1], hb.pos[2] + meta.headc[2]] : hb.pos; meta.headr = meta.headr || 0.38;
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

// ======================================================================
// Procedural animation for the axolotl puppet: states (stand idle, crawl, power, jetpack, pound, victory), stand <-> crawl transitions
// with a mesh swap hidden under a squash, and secondary motion (gill stalks, tail, digits) through damped springs.
// Pose conventions (canonical frames): x = flex about the hinge, y = twist about the bone, z = swing; see axo.js.

const _av = new THREE.Vector3(), _av2 = new THREE.Vector3(), _av3 = new THREE.Vector3(), _aq = new THREE.Quaternion(), _s1 = new THREE.Quaternion(), _s2 = new THREE.Quaternion(), _s3 = new THREE.Quaternion();
const smooth = t => t * t * (3 - 2 * t), clamp01 = t => Math.max(0, Math.min(1, t));
export const ease = { inOut: t => smooth(clamp01(t)), out: t => 1 - Math.pow(1 - clamp01(t), 3), in: t => Math.pow(clamp01(t), 3) };

export class Spring {
  constructor(n, k, c) { this.x = new Float32Array(n); this.v = new Float32Array(n); this.k = k; this.c = c; }
  step(target, dt) {
    dt = Math.min(dt, 1 / 30); const sub = 2, h = dt / sub;
    for (let s = 0; s < sub; s++) for (let i = 0; i < this.x.length; i++) { const a = this.k * (target[i] - this.x[i]) - this.c * this.v[i]; this.v[i] += a * h; this.x[i] += this.v[i] * h; }
    return this.x;
  }
}

export class Animator {
  constructor(puppet) {
    const P = this.P = puppet, nb = P.nb, I = this.I = P.idx;
    this.pose = new Pose(nb); this.from = new Pose(nb); this.A = new Pose(nb); this.B = new Pose(nb); this.C = new Pose(nb); this.other = new Pose(nb);
    this.t = 0; this.state = 'stand'; this.mesh = 'stand'; this.fade = 1; this.squash = 1; this.blend = 1; this.blendDur = 0.4; this.gait = 0; this.speed = 1; this.trans = null;
    this.look = { yaw: 0, pitch: 0 };   // game-driven head look, degrees
    // symmetric crawl rest: the sculpt is mid-stride and curved, so each bone's world rest frame is averaged with the mirror (x -> -x)
    // of its left/right partner's frame, then the local canonical poses are derived top-down from those symmetric world frames
    const LC = P.restPose.crawl; this.LS = new Pose(nb); this.LS.root.copy(LC.root); this.LS.root.x = 0;
    { const Fw = P.m.crawl.F, Fs = [], Fp = [];
      for (let i = 0; i < nb; i++) { const j = P.mirror[i]; const mj = new THREE.Quaternion(Fw[j].x, -Fw[j].y, -Fw[j].z, Fw[j].w); Fs.push(Fw[i].clone().slerp(mj, 0.5)); }
      for (let i = 0; i < nb; i++) { const p = P.par[i]; const nm = P.names[i];
        if (/^(gill|finger|toe\d)/.test(nm)) { this.LS.q[i].copy(LC.q[i]); Fp.push(p >= 0 ? Fp[p].clone().multiply(P.Rel[i]).multiply(this.LS.q[i]) : Fs[i].clone()); continue; }   // stalks and digits keep their sculpted pose relative to the head / hand
        const q = this.LS.q[i].copy(P.Rel[i]).invert(); if (p >= 0) q.multiply(_aq.copy(Fp[p]).invert()); q.multiply(Fs[i]); Fp.push(Fs[i].clone()); } }
    this.standRoot = P.m.stand.rest[0].clone();
    // rest-pose limb-end positions: the stand's feet (standing), the symmetric crawl rest's hands and feet (prone / gait centres)
    const idp = new Pose(nb); idp.root.copy(this.standRoot); const fs = P.fk('stand', idp); this.standFeet = { L: fs[I['foot.L']].clone(), R: fs[I['foot.R']].clone() };
    const fc = P.fk('crawl', this.LS); const avg = (a, b) => new THREE.Vector3((Math.abs(fc[I[a]].x) + Math.abs(fc[I[b]].x)) / 2, 0, (fc[I[a]].z + fc[I[b]].z) / 2);
    this.crawlHand = avg('hand.L', 'hand.R'); this.crawlFoot = avg('foot.L', 'foot.R');
    this.H = { crawlHand: 0.05, crawlFoot: 0.045, standHand: 0.06, standFoot: P.m.stand.rest[I['foot.L']].y };   // contact heights of the wrist / ankle joints above the floor
    this.stride = 0.3; this.groundSpeed = 0;
    this.chain = { spine: ['hips', 'spine', 'spine1', 'chest', 'neck'].map(n => I[n]), tail: [1, 2, 3, 4, 5, 6].map(k => I['tail' + k]),
      gills: ['L', 'R'].flatMap(s => [0, 1, 2].flatMap(k => [I[`gill${k}.${s}.1`], I[`gill${k}.${s}.2`]])),
      fingers: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`finger${k}.${s}.1`], I[`finger${k}.${s}.2`]])), toes: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`toe${k}.${s}.1`], I[`toe${k}.${s}.2`]])) };
    this.gillSpring = new Spring(12, 140, 8); this.gillTarget = new Float32Array(12);
    this.tailSpring = new Spring(12, 80, 7); this.tailTarget = new Float32Array(12);
    this.headPrev = new THREE.Vector3(); this.headVel = new THREE.Vector3(); this.headVelS = new THREE.Vector3(); this.rootPrev = new THREE.Vector3(); this.rootVel = new THREE.Vector3();
    this.events = [];
    // movement the game (or the preview) drives: speed 0..1 (crawl gait), turn -1..1, exertion 0..1, jump / land events; the look (face / materials)
    this.motion = { speed: 1, turn: 0, exert: 0 }; this.look2 = null; this.airY = 0; this.airV = 0; this.inAir = false; this.landK = 0;
    this.turnS = 0; this.speedS = 0; this.flickT = 2 + Math.random() * 3; this.breath = 0; this.breathPh = 0; this.exertS = 0;
    this.lagP = new THREE.Vector3(); this.lagV = new THREE.Vector3(); this.accS = new THREE.Vector3(); this.sqV = 0; this.sq = 0; this.jellyRipple = 0;
  }
  setLook(look) { this.look2 = look; }
  jump() { if (!this.inAir) { this.inAir = true; this.airV = 3.2; this.sqV -= 3.0; this.kickGills(0, -0.6); this.lagV.y -= 0.6; } }
  // ---------------- state machine ----------------
  set(state) {
    if (state === this.state && !this.trans) return;
    const from = this.state; const crawlish = s => s === 'crawl' || s === 'toCrawl';
    if (crawlish(from) && state !== 'crawl') { this.trans = { kind: 'crawlToStand', t: 0, target: state }; this.state = 'toStand'; return; }
    if (state === 'crawl' && !crawlish(from)) { this.from.copy(this.pose); this.trans = { kind: 'standToCrawl', t: 0 }; this.state = 'toCrawl'; return; }
    this.from.copy(this.pose); this.state = state; this.blend = 0; this.blendDur = state === 'victory' ? 0.25 : state === 'pound' ? 0.3 : 0.45;
  }
  update(dt) {
    dt = Math.min(dt, 1 / 20); this.t += dt; const out = this.A; const M = this.motion;
    // smoothed drive: speed and turn ease in, the turn's lateral acceleration and any speed change feed the springs
    const spd0 = this.speedS; this.speedS += (M.speed - this.speedS) * Math.min(1, dt * 6); this.turnS += (M.turn - this.turnS) * Math.min(1, dt * 5); this.exertS += (M.exert - this.exertS) * Math.min(1, dt * 2);
    const dv = (this.speedS - spd0) / Math.max(dt, 1e-3);
    this.accS.x += (-this.turnS * this.speedS * 2.5 - this.accS.x) * Math.min(1, dt * 8); this.accS.z += (dv * 1.5 - this.accS.z) * Math.min(1, dt * 8);
    // a hop (jump / land): the root rises on a simple arc, the landing squashes the body and kicks the gills and the tail
    if (this.inAir) { this.airV -= 9.8 * dt; this.airY += this.airV * dt; if (this.airY <= 0) { this.airY = 0; this.inAir = false; const imp = Math.min(1, -this.airV / 4); this.sqV += 4.5 * imp; this.landK = imp; this.kickGills(0, 1.2 * imp); this.lagV.y += 0.5 * imp; for (let k = 0; k < 6; k++) this.tailSpring.v[k * 2 + 1] -= 60 * imp; } }
    this.landK = Math.max(0, this.landK - dt * 3);
    if (this.trans) this.updateTransition(dt, out);
    else {
      this.evalState(this.state, this.t, out, dt);
      if (this.blend < 1) { this.blend = Math.min(1, this.blend + dt / this.blendDur); const k = ease.inOut(this.blend); this.B.copy(this.from).lerp(out, k); out.copy(this.B); }
    }
    out.root.y += this.airY; for (const k in out.contacts) if (this.inAir) out.contacts[k].w *= Math.max(0, 1 - this.airY * 6);
    this.pose.copy(out); this.secondary(dt); this.ground(this.mesh, this.pose); this.jelly(dt);
    this.P.apply(this.mesh, this.pose);
    if (this.fade < 1) { const o = this.mesh === 'stand' ? 'crawl' : 'stand'; this.ground(o, this.other); this.P.apply(o, this.other); }
    this.trackHead(dt);
  }
  evalState(state, t, out, dt) {
    switch (state) {
      case 'stand': return this.standIdle(t, out);
      case 'crawl': return this.crawl(t, out, dt);
      case 'power': return this.powerPose(t, out);
      case 'jetpack': return this.jetpack(t, out);
      case 'pound': return this.groundPound(t, out);
      case 'victory': return this.victory(t, out);
      case 'crouch': return this.crouch(out, 1);
      case 'prone': return this.proneCrawl(out);
      case 'rest': out.identity(); out.root.copy(this.standRoot); return out;
      case 'armsfwd': case 'armsside': case 'armsup': return this.armTest(state, out);
      default: return this.standIdle(t, out);
    }
  }
  // ---------------- helpers ----------------
  tailWave(ph, ampDeg, lag, lift) { for (let k = 0; k < 6; k++) { const a = ampDeg * (0.45 + k * 0.2); this.tailTarget[k * 2] = Math.sin(ph - k * lag) * a; this.tailTarget[k * 2 + 1] = lift * (k < 3 ? 1 : 0.6); } }
  // digits: curl about the hinge only, spread about the palm normal, inside the joint limits (clamped later per bone)
  digits(out, curl, spread, toeCurl, toeSpread = spread) {
    for (let s = 0; s < 2; s++) { const m = s === 0 ? 1 : -1;
      this.chain.fingers[s].forEach((f, k) => { rot(out, f[0], curl * 42, 0, (k - 1.5) * spread * 9 * m); rot(out, f[1], curl * 55, 0, 0); });
      this.chain.toes[s].forEach((f, k) => { rot(out, f[0], toeCurl * 40, 0, (k - 1.5) * toeSpread * 8 * m); rot(out, f[1], toeCurl * 45, 0, 0); }); }
  }
  // ---------------- STAND IDLE ----------------
  standIdle(t, out, amp = 1) {
    const I = this.I; out.identity(); out.root.copy(this.standRoot);
    const br = Math.sin(t * 2.0) * amp, sway = Math.sin(t * 0.6) * amp, sway2 = Math.sin(t * 0.6 + 1.1) * amp;
    out.root.y += -0.004 + br * 0.004; out.root.x += sway * 0.01;
    rot(out, I.hips, 0, 0, sway * 1.2); rot(out, I.spine, br * 0.8, 0, -sway * 1.0); rot(out, I.spine1, br * 0.9, sway2 * 1.5, 0); rot(out, I.chest, br * 1.3, 0, -sway * 0.6); rot(out, I.neck, -br * 1.0, 0, 0);
    rot(out, I.head, Math.sin(t * 0.9 + 0.4) * 2.5 * amp - 1 + this.look.pitch, Math.sin(t * 0.45) * 8 * amp + this.look.yaw, Math.sin(t * 0.35) * 2.5 * amp);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      rot(out, I['upperarm.' + s], 3 + br * 1.2, 0, 5 * m); rot(out, I['forearm.' + s], 10 + br * 1.5, 0, 0); rot(out, I['hand.' + s], 4, 0, 0);
      rot(out, I['thigh.' + s], 0, 0, sway * 1.2 * m); }
    this.tailWave(t * 1.3, 4 * amp, 0.9, 0); this.digits(out, 0.12 + br * 0.04, 0.35, 0.05); this.plantStandFeet(out, 0);
    return out;
  }
  plantStandFeet(out, lift, w = 1) { for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; out.contact('foot.' + s, _av.copy(this.standFeet[s]).setY(this.H.standFoot + lift), _av2.set(0.3 * m, 0, 1), _av3.set(0.25 * m, 0, 1), w); } }
  // ---------------- CRAWL (on the symmetric crawl rest): trunk S-wave + IK-planted diagonal gait ----------------
  // each limb: stance (60% of the cycle) = foot locked on the ground, moving back under the body at ground speed; swing (40%) = forward with a lift
  crawl(t, out, dt, speed = 1) {
    const I = this.I, P = this.P; out.copy(this.LS); out.contacts = {}; speed *= 0.15 + 0.85 * this.speedS;
    // a turn: the trunk bends into the turn (about the ventral axis), the head leads it a little
    const tn = this.turnS; for (let k = 0; k < 5; k++) rot(out, this.chain.spine[k], 0, 0, tn * 5); rot(out, I.head, 0, tn * 12, 0);
    this.gait += dt * speed * 2 * Math.PI * 1.1; const ph = this.gait; this.groundSpeed = this.stride * 1.1 * speed;
    const sp = this.chain.spine, amps = [-5, 4, 7, 3, 1.5];
    for (let k = 0; k < sp.length; k++) rot(out, sp[k], 0, 0, amps[k] * Math.sin(ph - k * 0.55 - 0.3) * speed);
    rot(out, I.head, 2 + Math.sin(ph * 2) * 1.2 * speed + this.look.pitch, this.look.yaw, 0);
    out.root.x += Math.sin(ph - 0.3) * 0.03 * speed; out.root.y += Math.sin(ph * 2 + 0.9) * 0.008 * speed;
    // diagonal pairs: LF + RH at phase 0, RF + LH at pi
    const limbs = [['hand.L', 0, 1, 1], ['hand.R', Math.PI, -1, 1], ['foot.R', 0, -1, 0], ['foot.L', Math.PI, 1, 0]];
    for (const [en, off, m, isArm] of limbs) {
      const u = ((ph + off) / (2 * Math.PI)) % 1, base = isArm ? this.crawlHand : this.crawlFoot, h = isArm ? this.H.crawlHand : this.H.crawlFoot, S = this.stride * speed;
      let z, y, lift = 0;
      if (u < 0.6) { z = base.z + S / 2 - S * (u / 0.6); y = h; } else { const sw = (u - 0.6) / 0.4; z = base.z - S / 2 + S * smooth(sw); lift = Math.sin(sw * Math.PI); y = h + 0.07 * lift; }
      const fwd = isArm ? _av2.set(0.35 * m, 0, 1) : _av2.set(0.45 * m, 0, 1), pole = isArm ? _av3.set(m, 0.3, -0.5) : _av3.set(m, 0.3, 0.4);
      out.contact(en, _av.set(base.x * m, y, z), fwd, pole, 1);
      // digits: flat on the ground in stance, relaxed curl in the air
      const dig = this.chain[isArm ? 'fingers' : 'toes'][m > 0 ? 0 : 1]; dig.forEach((f, k) => { rot(out, f[0], 4 + lift * 14, 0, (k - 1.5) * 5 * m); rot(out, f[1], 3 + lift * 10, 0, 0); });
    }
    this.tailWave(ph - 2.0, 10 * speed + 2, 0.7, 0);   // the S-wave: amplitude with speed
    return out;
  }
  // crawl rest with all four limbs planted at their gait centres (the pose shown during the swap)
  proneCrawl(out) {
    out.copy(this.LS); out.contacts = {}; this.tailWave(0, 0, 1, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      out.contact('hand.' + s, _av.set(this.crawlHand.x * m, this.H.crawlHand, this.crawlHand.z), _av2.set(0.35 * m, 0, 1), _av3.set(m, 0.3, -0.5), 1);
      out.contact('foot.' + s, _av.set(this.crawlFoot.x * m, this.H.crawlFoot, this.crawlFoot.z), _av2.set(0.45 * m, 0, 1), _av3.set(m, 0.3, 0.4), 1); }
    this.digits(out, 0.08, 0.3, 0.08); return out;
  }
  // ---------------- POWER POSE: akimbo. chest out, elbows out, fists planted on the hips, chin up ----------------
  powerPose(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.5); const br = Math.sin(t * 2.0);
    rot(out, I.spine, -5, 0, 0); rot(out, I.chest, -7 + br * 0.6, 0, 0); rot(out, I.neck, 2, 0, 0); rot(out, I.head, -9, 0, 0);
    const A = (n, d, z) => P.aim(out, I[n], _av.set(...d), _av2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      // upper arm down and well out to the side (elbow away from the body), forearm back in to the waist, hand on the hip bone
      A('upperarm.' + s, [0.7 * m, -0.68, -0.15], [-m, 0, 0.6]); A('forearm.' + s, [-0.35 * m, -0.55, 0.55], [-m, 0, 0.6]); A('hand.' + s, [-0.3 * m, -0.8, 0.4], [-0.9 * m, -0.3, 0.2]);
      rot(out, I['thigh.' + s], 4, 0, 10 * m); rot(out, I['shin.' + s], 6, 0, 0); rot(out, I['foot.' + s], -5, 0, 0); }
    out.root.x = 0; out.root.y -= 0.025; this.digits(out, 0.9, 0.0, 0.1); this.tailWave(t * 1.6, 5, 0.8, 0); this.plantStandFeet(out, 0);
    return out;
  }
  // ---------------- JETPACK: hanging, arms out for balance, legs and tail dangling ----------------
  jetpack(t, out) {
    const I = this.I; this.standIdle(t, out, 0.4); out.contacts = {}; const w = Math.sin(t * 3.0), w2 = Math.sin(t * 2.3 + 1);
    out.root.y += 0.5 + w2 * 0.03; out.root.x += Math.sin(t * 1.1) * 0.015;
    rot(out, I.hips, -8, 0, w2 * 2); rot(out, I.spine, -4, 0, 0); rot(out, I.chest, 3, 0, 0); rot(out, I.head, 5, w * 3, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const ws = s === 'L' ? w : -w;
      setRot(out, I['upperarm.' + s], -8, 0, 52 * m); setRot(out, I['forearm.' + s], 24 + ws * 4, 0, 0); setRot(out, I['hand.' + s], -12, 0, 6 * m);
      setRot(out, I['thigh.' + s], 24 + ws * 5, 0, 10 * m); setRot(out, I['shin.' + s], 48 + ws * 8, 0, 0); setRot(out, I['foot.' + s], 22 + ws * 5, 0, 0); }
    for (let k = 0; k < 6; k++) rot(out, this.chain.tail[k], 10 + k * 2, 0, 0);   // tail hangs
    this.tailWave(t * 2.4, 3, 1.0, 0); this.digits(out, 0.35, 0.3, 0.3);
    return out;
  }
  // ---------------- GROUND-POUND WIND-UP: tucked crouch in the air, both arms raised forward / up, fists ----------------
  groundPound(t, out) {
    const I = this.I; this.standIdle(t, out, 0.3); out.contacts = {}; const sh = Math.sin(t * 16) * 0.5;
    out.root.y += 0.42 + 0.02 * Math.sin(t * 2.2);
    rot(out, I.hips, 14, 0, 0); rot(out, I.spine, 10, 0, 0); rot(out, I.chest, 8, 0, 0); rot(out, I.neck, -6, 0, 0); rot(out, I.head, -14, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      // arms raised forward and up in front of the head (never behind it), elbows slightly bent, fists clenched; knees tucked
      this.P.aim(out, I['upperarm.' + s], _av.set(0.48 * m, 0.3 + sh * 0.01, 0.85), _av2.set(0, 1, -0.3)); this.P.aim(out, I['forearm.' + s], _av.set(0.35 * m, 0.55, 0.78), _av2.set(0, 1, -0.3)); setRot(out, I['hand.' + s], 30, 0, 0);
      setRot(out, I['thigh.' + s], 70, 0, 14 * m); setRot(out, I['shin.' + s], 100, 0, 0); setRot(out, I['foot.' + s], 25, 0, 0); }
    for (let k = 0; k < 6; k++) rot(out, this.chain.tail[k], -5 - k * 2, 0, 0);
    this.tailWave(t * 3, 4, 1, 0); this.digits(out, 0.65, 0.0, 0.5);
    return out;
  }
  // ---------------- VICTORY: hops, both arms thrown up and forward, clear of the head and gills ----------------
  victory(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.5); const T = (t * 1.6) % 1; const hop = Math.max(0, Math.sin(T * Math.PI * 2)); const pump = Math.sin(t * 1.6 * Math.PI * 2);
    out.root.y += hop * 0.16; out.root.x = 0;
    rot(out, I.spine, -3 - hop * 3, 0, 0); rot(out, I.chest, -4, 0, 0); rot(out, I.head, -12 + hop * 5, 0, Math.sin(t * 3) * 5);
    const A = (n, d, z) => P.aim(out, I[n], _av.set(...d), _av2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const pm = s === 'L' ? pump : -pump;
      // upper arm up, forward and out (past the gills), forearm straight on up with a little pump
      A('upperarm.' + s, [0.75 * m, 0.35 + pm * 0.1, 0.55], [-m, 0.3, 0.3]); A('forearm.' + s, [0.6 * m, 0.65 + pm * 0.12, 0.45], [-m, 0.2, 0.2]); A('hand.' + s, [0.55 * m, 0.75, 0.38], [-m, 0, 0]);
      rot(out, I['thigh.' + s], hop * 20, 0, 5 * m); rot(out, I['shin.' + s], hop * 35, 0, 0); rot(out, I['foot.' + s], hop * 16, 0, 0); }
    this.tailWave(t * 6, 7, 0.9, 0); this.digits(out, 0.1, 0.6, 0.1); this.plantStandFeet(out, 0, 1 - smooth(Math.min(1, hop * 3)));
    return out;
  }
  // ---------------- CROUCH (stand mesh): low and horizontal, hands and feet planted on the floor, head looking ahead, tail trailing low ----------------
  crouch(out, k = 1, cw = 1) {
    const I = this.I, P = this.P; out.identity(); out.root.copy(this.standRoot); out.root.y -= 0.3 * k; out.root.z += 0.1 * k;
    rot(out, I.hips, 58 * k, 0, 0); rot(out, I.spine, 8 * k, 0, 0); rot(out, I.spine1, 6 * k, 0, 0); rot(out, I.chest, 4 * k, 0, 0); rot(out, I.neck, -30 * k, 0, 0); rot(out, I.head, -34 * k, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      setRot(out, I['thigh.' + s], 75 * k, 0, 16 * m * k); setRot(out, I['shin.' + s], 112 * k, 0, 0); setRot(out, I['foot.' + s], -8 * k, 0, 0);
      setRot(out, I['upperarm.' + s], 68 * k, 0, 20 * m * k); setRot(out, I['forearm.' + s], 10 * k, 0, 0); setRot(out, I['hand.' + s], -30 * k, 0, 0); }
    rot(out, this.chain.tail[0], 52 * k, 0, 0); for (let kk = 1; kk < 6; kk++) rot(out, this.chain.tail[kk], 5 * k, 0, 0);
    this.tailWave(0, 0, 1, 0); this.digits(out, 0.08, 0.4, 0.08);
    // contacts: hands forward-out of the shoulders, feet under the hips, all on the floor
    const pos = P.fk('stand', out);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const sh = pos[I['upperarm.' + s]], hp = pos[I['thigh.' + s]];
      out.contact('hand.' + s, _av.set(sh.x + 0.1 * m, this.H.standHand, sh.z + 0.26), _av2.set(0.3 * m, 0, 1), _av3.set(0.6 * m, 0.2, -1), cw);
      out.contact('foot.' + s, _av.set(hp.x + 0.06 * m, this.H.standFoot, hp.z + 0.1), _av2.set(0.3 * m, 0, 1), _av3.set(0.3 * m, 0, 1), 1); }
    return out;
  }
  // arm tests (QA only): standing rest with both arms forward / sideways / up
  armTest(state, out) {
    const I = this.I; out.identity(); out.root.copy(this.standRoot); this.plantStandFeet(out, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const d = state === 'armsfwd' ? [0.15 * m, 0.05, 1] : state === 'armsside' ? [m, 0.05, 0] : [0.25 * m, 1, 0.1];
      this.P.aim(out, I['upperarm.' + s], _av.set(...d), _av2.set(0, -1, 0.3), false); this.P.aim(out, I['forearm.' + s], _av.set(...d), _av2.set(0, -1, 0.3), false); }
    return out;
  }
  // ---------------- TRANSITIONS ----------------
  // stand -> crawl: (A) stand mesh folds into the crouch, (B) short squash + crossfade to the crawl mesh in its rest (heads aligned), (C) crawl settles into the gait
  // crawl -> stand: (A) gait eases out, (B) squash + crossfade to the stand mesh in the crouch, (C) stand rises into the target state
  updateTransition(dt, out) {
    const P = this.P, T = this.trans, I = this.I; T.t += dt;
    const A = 0.32, S = 0.07, C = 0.35;
    if (T.kind === 'standToCrawl') {
      if (T.t < A) { const k = ease.inOut(T.t / A); this.crouch(this.B, 1, 1); out.copy(this.from).lerp(this.B, k); this.mesh = 'stand'; this.fade = 1; this.squash = 1 - 0.2 * ease.in(clamp01((T.t - A + 0.12) / 0.12)); }
      else if (T.t < A + S) {
        if (!T.off) { T.off = this.headOffset(); this.gait = 0; }
        const k = (T.t - A) / S; this.mesh = 'crawl'; this.fade = smooth(k); this.squash = 0.8;
        this.proneCrawl(out); this.offsetContacts(out, T.off); this.crouch(this.other, 1, 1);
      } else if (T.t < A + S + C) {
        const k = ease.inOut((T.t - A - S) / C); this.fade = 1; this.squash = 1 - 0.2 * (1 - ease.out(clamp01((T.t - A - S) / 0.14))); this.crawl(this.t, this.B, dt, k); _av.copy(this.B.root);
        this.proneCrawl(out); this.offsetContacts(out, T.off); out.lerp(this.B, k); out.root.lerp(_av, k);
      } else { this.trans = null; this.state = 'crawl'; this.blend = 1; this.crawl(this.t, out, dt); }
    } else {
      const C2 = 0.3, A2 = 0.45;
      if (T.t < C2) { const k = ease.inOut(T.t / C2); this.crawl(this.t, this.B, dt, 1 - k); this.proneCrawl(out); out.copy(this.B).lerp(out, k); this.mesh = 'crawl'; this.fade = 1; this.squash = 1 - 0.2 * ease.in(clamp01((T.t - C2 + 0.12) / 0.12)); this.tailWave(0, 0, 1, 0); }
      else if (T.t < C2 + S) {
        if (!T.off) T.off = this.headOffset();
        const k = (T.t - C2) / S; this.mesh = 'stand'; this.fade = smooth(k); this.squash = 0.8;
        this.crouch(out, 1, 1); this.proneCrawl(this.other); this.offsetContacts(this.other, T.off);
      } else if (T.t < C2 + S + A2) {
        const k = ease.out((T.t - C2 - S) / A2); this.fade = 1; this.squash = 1 - 0.2 * (1 - ease.out(clamp01((T.t - C2 - S) / 0.14))); this.evalState(T.target, this.t, this.B, dt); this.crouch(out, 1, 1 - k); out.lerp(this.B, k); out.root.y += Math.sin(k * Math.PI) * 0.03;
      } else { this.trans = null; this.state = T.target; this.blend = 1; this.evalState(T.target, this.t, out, dt); }
    }
    return out;
  }
  offsetContacts(pose, off) { pose.root.add(off); for (const k in pose.contacts) pose.contacts[k].t.add(off); }
  // root offset for the crawl mesh (in its rest) so its head sits where the stand mesh's head is in the crouch
  headOffset() {
    const P = this.P; this.crouch(this.B, 1); P.apply('stand', this.B); const hs = P.jointWorld('stand', 'head'); this.proneCrawl(this.C); P.apply('crawl', this.C); const hc = P.jointWorld('crawl', 'head');
    const off = hs.sub(hc); off.y = 0; return off;
  }
  // ---------------- GROUND CONTACT: two-bone IK per contact, blended by the contact weight ----------------
  ground(which, pose) {
    const P = this.P, I = this.I, C = pose.contacts; if (!C) return;
    for (const en in C) { const c = C[en]; if (!(c.w > 0)) continue;
      const side = en.slice(-1), isArm = en.startsWith('hand'); const up = I[(isArm ? 'upperarm.' : 'thigh.') + side], lo = I[(isArm ? 'forearm.' : 'shin.') + side], e = I[en];
      if (c.w < 1) { _s1.copy(pose.q[up]); _s2.copy(pose.q[lo]); _s3.copy(pose.q[e]); }
      P.ik2(which, pose, up, lo, e, c.t, c.pole, isArm ? -1 : 1);
      P.aim(pose, e, _av.copy(c.fwd).setY(0).normalize(), _av2.set(0, -1, 0), false);   // sole flat on the floor
      if (c.w < 1) { pose.q[up].copy(_s1.slerp(pose.q[up], c.w)); pose.q[lo].copy(_s2.slerp(pose.q[lo], c.w)); pose.q[e].copy(_s3.slerp(pose.q[e], c.w)); }
    }
  }
  // ---------------- SECONDARY MOTION ----------------
  secondary(dt) {
    const pose = this.pose, I = this.I;
    // the tail: a spring chain after its target wave; a turn swings it out the other way (more toward the tip), a flick now and then, it settles when idle
    this.flickT -= dt * (0.3 + this.speedS); if (this.flickT <= 0) { this.flickT = 2.5 + Math.random() * 4; const sgn = Math.random() < 0.5 ? -1 : 1; for (let k = 2; k < 6; k++) this.tailSpring.v[k * 2] += sgn * (30 + 25 * (k - 2)); }
    const lat = -this.rootVel.x * 40 - this.turnS * this.speedS * 18 - this.accS.x * 4;
    const tl = this.tailSpring.step(this.tailTarget, dt);
    for (let k = 0; k < 6; k++) rot(pose, this.chain.tail[k], tl[k * 2 + 1], 0, tl[k * 2] + lat * (0.25 + k * 0.15));
    // breathing: the chest / belly expand (jelly layer) and the chest bone lifts a little; faster and deeper with exertion
    const rate = 1.9 + 2.6 * this.exertS + 0.6 * this.speedS; this.breathPh += dt * rate; this.breath = 0.5 + 0.5 * Math.sin(this.breathPh); const br = this.breath * (0.6 + 0.9 * this.exertS);
    rot(pose, I.chest, -1.2 * br, 0, 0); rot(pose, I.spine1, -0.8 * br, 0, 0);
    const g = this.chain.gills, vel = this.headVelS;
    for (let j = 0; j < 6; j++) {
      const i1 = g[j * 2]; _aq.copy(this.P.Fp[i1]).invert(); _av.copy(vel).applyQuaternion(_aq);   // head velocity in the stalk's posed frame
      const flutter = Math.sin(this.t * 2.3 + j * 1.7) * 2.0 + Math.sin(this.t * 3.7 + j * 0.9) * 1.0; const cl = x => Math.max(-25, Math.min(25, x));
      // drag from the head's motion and from the body's acceleration (a turn, a speed change): the stalks trail the other way
      const sgn = j < 3 ? 1 : -1; this.gillTarget[j * 2] = cl(flutter - _av.z * 20 - this.accS.z * 6); this.gillTarget[j * 2 + 1] = cl(-_av.x * 20 - this.accS.x * 5 * sgn);
    }
    const gs = this.gillSpring.step(this.gillTarget, dt);
    const cm = this.mesh === 'crawl' ? 0.6 : 1;   // the crawl sculpt's stalks are fused to the shoulders: gentler flutter there
    const lo = this.mesh === 'crawl' ? 0 : 0.4;   // the crawl sculpt's lowest stalks are fused to the shoulders: no flutter there
    const stalkAmp = [cm, 0.9 * cm, lo * cm, cm, 0.9 * cm, lo * cm];
    for (let j = 0; j < 6; j++) { const a = gs[j * 2] * stalkAmp[j], b = gs[j * 2 + 1] * stalkAmp[j]; rot(pose, g[j * 2], a * 0.55, 0, b * 0.55); rot(pose, g[j * 2 + 1], a * 0.7, 0, b * 0.7); }
    // joint limits: stand poses relative to the stand rest, crawl relative to the symmetric crawl rest
    const base = this.mesh === 'crawl' ? this.LS : null; const P = this.P;
    for (let i = 0; i < P.nb; i++) {
      if (base) { _aq.copy(base.q[i]).invert().multiply(pose.q[i]); const bq = pose.q[i]; bq.copy(_aq); if (P.clampBone(pose, i)) {} bq.premultiply(base.q[i]); }
      else P.clampBone(pose, i);
    }
  }
  // a kick into the gill springs (impulse about the hinge, degrees/s): landings and jumps
  kickGills(x, y) { for (let j = 0; j < 6; j++) { this.gillSpring.v[j * 2] += y * 120 * (0.7 + 0.3 * Math.random()); this.gillSpring.v[j * 2 + 1] += x * 120; } }
  // the soft-body jelly layer: a lag spring behind the body's acceleration, squash / stretch on jumps and landings, a ripple while moving;
  // written into the look's uniforms (both meshes share them)
  jelly(dt) {
    const L = this.look2; const h = Math.min(dt, 1 / 30);
    // lag: a damped spring driven by the (smoothed) acceleration; it overshoots and settles
    this.lagV.x += ((-this.accS.x * 0.02 - this.lagP.x) * 90 - this.lagV.x * 8) * h; this.lagV.z += ((-this.accS.z * 0.02 - this.lagP.z) * 90 - this.lagV.z * 8) * h; this.lagV.y += ((0 - this.lagP.y) * 110 - this.lagV.y * 9) * h;
    this.lagP.addScaledVector(this.lagV, h); const lim = 0.04; this.lagP.x = Math.max(-lim, Math.min(lim, this.lagP.x)); this.lagP.z = Math.max(-lim, Math.min(lim, this.lagP.z)); this.lagP.y = Math.max(-lim, Math.min(lim, this.lagP.y));
    this.sqV += ((0 - this.sq) * 150 - this.sqV * 9) * h; this.sq += this.sqV * h; this.sq = Math.max(-0.2, Math.min(0.22, this.sq));
    const stretch = this.inAir ? -0.08 * Math.min(1, Math.abs(this.airV) / 3) : 0;
    this.jellyRipple += ((this.speedS * 0.35 + this.landK * 0.6) * 0.004 - this.jellyRipple) * Math.min(1, dt * 6);
    if (!L) return;
    L.U.uJelly.value.set(0.012 * this.breath * (0.7 + 0.8 * this.exertS), this.sq * 0.6 + stretch, this.mesh === 'crawl' ? 0.9 : 1.6, this.jellyRipple);
    L.U.uLag.value.x = this.lagP.x; L.U.uLag.value.y = this.lagP.y; L.U.uLag.value.z = this.lagP.z;
    L.coatMixT = this.mesh === 'crawl' ? 0 : 1;
    L.update(dt, [this.look.yaw / 90 * 0.3, this.look.pitch / -50 * 0.2], this.sq * 0.6 + stretch);
  }
  trackHead(dt) {
    const P = this.P; const h = P.jointWorld(this.mesh, 'head', _av2);
    if (dt > 0) { this.headVel.copy(h).sub(this.headPrev).divideScalar(dt); this.rootVel.copy(this.pose.root).sub(this.rootPrev).divideScalar(dt); }
    if (this.headVel.length() > 20) this.headVel.set(0, 0, 0);
    this.headVelS.lerp(this.headVel, 1 - Math.exp(-dt * 16)); this.headPrev.copy(h); this.rootPrev.copy(this.pose.root);
  }
}

// ======================================================================
// The axolotl's look: team-colour recolour of the baked texture, wet goo with clearcoat, the paint coat rising by a per-vertex fill order,
// a soft-body jelly layer in the vertex shader (breathing, lag wobble, squash / stretch, ripple; the head is rigid), rim light and thin-part
// warmth, and the face (eyes, pupils, blink, mouth, fangs) projected onto the front of the head from the rest-space head frame.

// ---------------- face sheets (ported from the game's slime: 4 x 5 cells; 0-5 eyes, 6 closed, 7 squeezed, 8-13 mouths, 14-19 mouths with fangs) ----------------
export const FACE_EYE = { x: 0.4, y: 0.16, rx: 0.3, ry: 0.33 };
export const FACE_KINDS = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared'];
export const FACE_LIDS = {
  neutral: { h: 0.08, k: 0, c: 0.1, ch: -0.95, pu: 1.0, py: -0.1 },
  happy: { h: 0.42, k: 0.04, c: 0.16, ch: -0.42, chc: 0.34, pu: 1.0, py: -0.02, blush: 1 },
  angry: { h: 0.05, k: -0.46, c: -0.02, ch: -0.7, chc: 0.1, pu: 0.88, py: -0.12 },
  hurt: { L: { h: -0.12, k: 0.3, c: 0.0, ch: -0.42, chc: 0.2, pu: 0.85, py: -0.05 }, R: { shut: 'squeeze' }, sweat: 1 },
  glee: { shut: 'arc', blush: 1.2 },
  scared: { h: 0.86, k: 0.08, c: 0.06, ch: -0.97, pu: 0.62, py: -0.02 },
};
export const EXPR = { neutral: [0, 8], happy: [1, 9], angry: [2, 10], hurt: [3, 11], glee: [4, 12], scared: [5, 13], yawn: [6, 13], dizzy: [7, 11], peek: [5, 13], leap: [5, 9], brace: [7, 11] };
const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 } };
export function pupilOf(name) { const F = PUPILS[name] || FACE_LIDS[name]; if (!F) return { pu: 1, py: 0 }; const L = F.L || F; return { pu: L.pu || 1, py: (L.py || 0) * FACE_EYE.ry }; }
export function makeFaceSheets(C) {
  const W = C * 4, H = C * 5, col = document.createElement('canvas'), msk = document.createElement('canvas'); col.width = msk.width = W; col.height = msk.height = H;
  const g = col.getContext('2d'), m = msk.getContext('2d'); m.fillStyle = '#000'; m.fillRect(0, 0, W, H);
  const at = (ctx, cell, fn) => { ctx.save(); ctx.translate((cell % 4) * C + C / 2, Math.floor(cell / 4) * C + C / 2); ctx.scale(C / 2, -C / 2); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; fn(ctx); ctx.restore(); };
  const E = FACE_EYE, INK = '40,6,18';
  const lidY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * (L.h + (L.k || 0) * u * -sd + (L.c || 0) * (1 - u * u)); };
  const cheekY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * ((L.ch === undefined ? -1 : L.ch) + (L.chc || 0) * (1 - u * u)); };
  const ell = (ctx, sd, k) => { ctx.beginPath(); ctx.ellipse(sd * E.x, E.y, E.rx * (k || 1), E.ry * (k || 1), 0, 0, Math.PI * 2); };
  const curve = (ctx, f, sd, x0, x1, cont) => { const n = 40; for (let i = 0; i <= n; i++) { const x = x0 + (x1 - x0) * i / n; i || cont ? ctx.lineTo(x, f(x)) : ctx.moveTo(x, f(x)); } };
  const openPath = (ctx, L, sd) => { const x0 = sd * E.x - E.rx * 1.2, x1 = sd * E.x + E.rx * 1.2; ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, x0, x1); curve(ctx, x => cheekY(L, sd, x), sd, x1, x0, true); ctx.closePath(); };
  function openEye(cell, L, sd) {
    at(g, cell, ctx => {
      const sh = ctx.createRadialGradient(sd * E.x, E.y - E.ry * 0.25, E.rx * 0.6, sd * E.x, E.y - E.ry * 0.25, E.rx * 1.35); sh.addColorStop(0, 'rgba(' + INK + ',0.0)'); sh.addColorStop(0.55, 'rgba(' + INK + ',0.2)'); sh.addColorStop(1, 'rgba(' + INK + ',0)');
      ctx.fillStyle = sh; ctx.beginPath(); ctx.ellipse(sd * E.x, E.y - E.ry * 0.2, E.rx * 1.35, E.ry * 1.25, 0, 0, Math.PI * 2); ctx.fill();
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      const wg = ctx.createRadialGradient(sd * E.x - 0.05, E.y + 0.06, 0.02, sd * E.x, E.y, E.rx * 1.08); wg.addColorStop(0, '#FFFFFF'); wg.addColorStop(0.62, '#F4F3F8'); wg.addColorStop(1, '#C9C7D6');
      ctx.fillStyle = wg; ctx.fillRect(sd * E.x - 0.5, E.y - 0.5, 1, 1); ctx.restore();
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      for (let k = 0; k < 6; k++) { ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) - 0.012 * k, sd, sd * E.x - E.rx * 1.2, sd * E.x + E.rx * 1.2); ctx.strokeStyle = 'rgba(60,30,70,' + (0.11 - 0.017 * k).toFixed(3) + ')'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      ctx.save(); openPath(ctx, L, sd); ctx.clip(); ell(ctx, sd); ctx.strokeStyle = 'rgba(' + INK + ',0.62)'; ctx.lineWidth = 0.028; ctx.stroke(); ctx.restore();
      ctx.save(); ell(ctx, sd, 1.002); ctx.clip();
      ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.9)'; ctx.lineWidth = 0.045; ctx.stroke();
      if (L.ch > -0.9) { ctx.beginPath(); curve(ctx, x => cheekY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.55)'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      ctx.save(); ell(ctx, sd, 1.04); ctx.clip(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) + 0.04, sd, sd * E.x - E.rx * 0.8, sd * E.x + E.rx * 0.8); ctx.strokeStyle = 'rgba(255,240,235,0.32)'; ctx.lineWidth = 0.035; ctx.stroke();
      ctx.restore(); ctx.save(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.3, sd * E.x + E.rx * 1.3); ctx.lineTo(sd * E.x + E.rx * 1.3, 2); ctx.lineTo(sd * E.x - E.rx * 1.3, 2); ctx.closePath(); ctx.clip();
      ell(ctx, sd, 1.01); ctx.strokeStyle = 'rgba(' + INK + ',0.2)'; ctx.lineWidth = 0.022; ctx.stroke(); ctx.restore();
    });
    at(m, cell, ctx => { ctx.save(); ell(ctx, sd, 0.985); ctx.clip(); openPath(ctx, L, sd); ctx.clip(); ctx.fillStyle = '#FF0000'; ctx.fillRect(-1, -1, 2, 2);
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
  const big = (ctx, fn) => { ctx.translate(0, MY); ctx.scale(1.2, 1.2); ctx.translate(0, -MY); fn(); };   // (the axolotl's mouth: small)
  FACE_KINDS.forEach((k, i) => { at(g, 8 + i, ctx => big(ctx, () => MOUTHS[k](ctx, false))); at(g, 14 + i, ctx => big(ctx, () => MOUTHS[k](ctx, true))); });
  return { col, msk };
}
let SHEETS = null;
export function faceSheets(C = 256) {
  if (SHEETS) return SHEETS; const sh = makeFaceSheets(C);
  const col = new THREE.CanvasTexture(sh.col), msk = new THREE.CanvasTexture(sh.msk); col.colorSpace = THREE.SRGBColorSpace; col.anisotropy = 4; msk.colorSpace = THREE.NoColorSpace;
  for (const t of [col, msk]) { t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; }
  return SHEETS = { col, msk };
}

// ---------------- shader pieces ----------------
// vertex: the jelly layer on the skinned position, and the face / coat varyings from the REST position (so the face rides the head rigidly)
const VERT_PARS = `
attribute vec4 jelly; attribute vec2 fill;
uniform vec4 uJelly;   // x breath (m), y squash (-stretch .. +squash), z body height (m), w ripple (m)
uniform vec4 uLag;     // xyz: lag offset of the soft body (object space, m), w: time
uniform vec4 uFace;    // x yaw half-width (rad), y pitch half-height (rad), z pitch of the face centre (rad), w on
uniform vec4 uHead;    // xyz head centre (rest, object space), w head radius
uniform float uCoatMix;
varying vec3 vSkinP, vFace; varying vec4 vJelly; varying float vFill;`;
const VERT_MAIN = `
{
  vJelly = jelly; vSkinP = position; vFill = mix(fill.x, fill.y, uCoatMix);
  vec3 d = position - uHead.xyz; float yw = atan(d.x, d.z), pt = atan(d.y, length(d.xz));
  vFace = vec3(yw / uFace.x, (pt - uFace.z) / uFace.y, smoothstep(0.05, 0.4, d.z / uHead.w) * smoothstep(0.6, 0.9, jelly.w) * uFace.w);
  float soft = jelly.y, h = clamp(transformed.y / uJelly.z, 0.0, 1.0);
  transformed += objectNormal * (jelly.x * uJelly.x + uJelly.w * soft * sin(position.x * 23.0 + position.y * 17.0 + uLag.w * 9.0) * sin(position.z * 19.0 - uLag.w * 7.0));
  float s = uJelly.y * soft; transformed.y *= 1.0 - s; transformed.xz *= 1.0 + 0.5 * s;
  transformed += uLag.xyz * soft * h;
}`;
// fragment: the recolour, the coat, the face, the gloss, the rim and the thin-part warmth
const FRAG_PARS = `
uniform vec3 uTeam, uPaint; uniform vec4 uCoat;   // uCoat: x level 0..1, y seed, z wet 0..1, w 0
uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp; uniform vec3 fIris; uniform float fStyle; uniform vec3 uKeyDir;
varying vec3 vSkinP, vFace; varying vec4 vJelly; varying float vFill;
float sCoatM = 0.0, sGloss = 0.5, faceInk = 0.0, sEyeM = 0.0;
vec3 sHue(vec3 c, float a){ const vec3 k = vec3(0.57735); float ca = cos(a); return c * ca + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - ca); }
vec3 rgb2hsv(vec3 c){ vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0); vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g)); vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
  float d = q.x - min(q.w, q.y), e = 1.0e-10; return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x); }
float coatField(vec3 sp, float sy){ vec3 cq = sp * 5.0 + uCoat.y;
  float ch = 0.5 + 0.25 * sin(cq.x * 1.7 + sin(cq.y * 2.3)) * sin(cq.z * 1.9 + sin(cq.x * 1.3)) + 0.25 * sin(cq.y * 3.1 + cq.z * 1.1 + cq.x * 0.7);
  return clamp(0.55 * ch + 0.45 * sy, 0.0, 1.0); }
vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.2); }`;
// the recolour: the baked map's pink skin, pale belly, red gills and blue fin each take a member of the team colour's palette, keeping the map's own shading
const MAP_FS = `
{
  const vec3 LW = vec3(0.2126, 0.7152, 0.0722);
  vec4 texel = texture2D(map, vMapUv); vec3 tl = texel.rgb; float lum = dot(tl, LW); vec3 hsv = rgb2hsv(tl);
  vec3 T = mix(vec3(dot(uTeam, LW)), uTeam, 0.92);
  vec3 HA = max(sHue(T, 0.34), vec3(0.0)), HB = max(sHue(T, -0.34), vec3(0.0)); float upA = step(dot(HB, LW), dot(HA, LW));
  vec3 up = mix(HB, HA, upA), dn = mix(HA, HB, upA);
  vec3 skinC = mix(T, vec3(1.0, 0.93, 0.9), 0.3), bellyC = mix(T, vec3(1.0, 0.96, 0.9), 0.8), gillC = mix(pow(T, vec3(1.6)) * 1.25, dn, 0.3), finC = mix(up, vec3(1.0), 0.25);
  float redM = smoothstep(0.45, 0.65, hsv.y) * (1.0 - smoothstep(0.04, 0.09, min(hsv.x, 1.0 - hsv.x))) * (1.0 - smoothstep(0.3, 0.5, lum));
  float blueM = smoothstep(0.2, 0.35, hsv.y) * smoothstep(0.5, 0.58, hsv.x) * (1.0 - smoothstep(0.82, 0.9, hsv.x));
  float paleM = (1.0 - smoothstep(0.1, 0.28, hsv.y)) * smoothstep(0.25, 0.5, lum) * (1.0 - redM) * (1.0 - blueM);
  float skinM = max(0.0, 1.0 - redM - blueM - paleM);
  vec3 pal = skinC * min(1.25, lum / 0.36) * skinM + bellyC * min(1.1, lum / 0.6) * paleM + gillC * clamp(lum / 0.2, 0.6, 1.3) * redM + finC * min(1.2, lum / 0.3) * blueM;
  diffuseColor.rgb = clamp(pal, 0.0, 1.0);
  // gloss: wet goo, wetter low down, on the belly and the thin frills; a touch drier over the back
  sGloss = clamp(0.45 + 0.3 * vJelly.z + 0.25 * vJelly.x + 0.3 * uCoat.z + 0.2 * redM - 0.1 * smoothstep(0.3, 0.8, vNormal.y), 0.0, 1.0);
}
if (uCoat.x > 0.001) {
  float ch = coatField(vSkinP, vFill), cv = uCoat.x * 1.08 - 0.04;
  sCoatM = smoothstep(ch - 0.035, ch + 0.035, cv);
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.12), vec3(0.0)) * 0.86;
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, sCoatM) * (1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.06, abs(cv - ch))) * step(uCoat.x, 0.995));
  sGloss = max(sGloss, sCoatM);
}`;
const FACE_FS = `
if (vFace.z > 0.01 && abs(vFace.x * fComp.x) < 0.985 && abs(vFace.y * fComp.y) < 0.985) {
  vec2 fq = vFace.xy * fComp.xy; vec2 cuv = fq * 0.5 + 0.5;
  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = fStyle > 2.5 ? 1.0 : 0.0; vec2 fqe = fq; if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.1 + 0.01; l.x = (l.x + l.y * sd0 * 0.2) * 0.97; fqe = pc0 + l; }
  vec2 cuvE = fqe * 0.5 + 0.5;
  vec4 eA = texture2D(fCol, fCell(fCells.x, cuvE)), eB = texture2D(fCol, fCell(fCells.z, cuvE)), eye = mix(eA, eB, fMix.x);
  vec3 emL = mix(texture2D(fMsk, fCell(fCells.x, cuvE)).rgb, texture2D(fMsk, fCell(fCells.z, cuvE)).rgb, fMix.x); vec2 em = emL.rg;
  vec4 bl = texture2D(fCol, fCell(fMix.w, cuvE)); eye = mix(eye, bl, fMix.y); em *= 1.0 - fMix.y;
  float dotK = 0.0; if (fStyle > 1.5 && fStyle < 2.5) { eye.a = 0.0; em = vec2(0.0); }
  if (zmb > 0.5) eye.rgb = eye.rgb * vec3(0.78, 0.9, 0.6) + vec3(0.05, 0.06, 0.0) * eye.a;
  vec3 c = mix(diffuseColor.rgb, eye.rgb, eye.a);
  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.05, sin(a) * 0.052 + 0.026))).a); }
    float hole = texture2D(fCol, fCell(0.0, cuvE)).a, rim = clamp(d1 - hole, 0.0, 1.0), sp = 0.0;
    for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16); vec2 dw = normalize(vec2(sd, 0.45)); vec2 a = pc + dw * 0.18, b = a + dw * 0.26;
      vec2 ab = b - a; float t = clamp(dot(fqe - a, ab) / dot(ab, ab), 0.0, 1.0); float dd = length(fqe - a - ab * t) - mix(0.1, 0.004, t); sp = max(sp, 1.0 - smoothstep(-0.004, 0.012, dd)); }
    float mk = max(rim, sp); c = mix(c, vec3(0.03, 0.012, 0.02), mk);
    float lidLine = eye.a * step(dot(eye.rgb, vec3(0.333)), 0.3); c = mix(c, vec3(0.03, 0.012, 0.02), hole * (1.0 - eye.a) * (1.0 - mk)); c = mix(c, vec3(0.46, 0.3, 0.38), hole * lidLine * (1.0 - mk)); dotK = max(mk, hole * (1.0 - eye.a)); }
  if (fStyle > 1.5 && fStyle < 2.5) { float bk = 1.0 - fMix.y * 0.92; for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy * 0.6; vec2 dd = (fq - pc) * vec2(1.0, 1.0 / max(0.08, bk)); float r = length(dd);
    float dk = 1.0 - smoothstep(0.125, 0.145, r); c = mix(c, vec3(0.03, 0.012, 0.02), dk); float hl = 1.0 - smoothstep(0.03, 0.046, length((fq - pc - vec2(-0.045, 0.05)) * vec2(1.0, 1.0 / max(0.08, bk)))); c = mix(c, vec3(1.0), hl * dk); dotK = max(dotK, dk); } }
  for (int i = 0; i < 2; i++) {
    float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.235, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.92 : 1.14, zmb), rp = mix(0.092, 0.11, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb);
    vec3 irC = mix(fIris, vec3(0.42, 0.6, 0.3), zmb);
    float ia = (1.0 - smoothstep(ri - 0.014, ri, r)) * em.r;
    vec3 ic = mix(irC, irC * 0.2, smoothstep(0.0, ri, r)); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - 0.012, rp, r));
    ic += irC * 1.12 * smoothstep(ri * 0.35, ri * 0.95, r) * smoothstep(0.2, -0.6, dd.y / ri) * (1.0 - smoothstep(ri * 0.95, ri, r));
    ic = mix(ic, vec3(0.72, 0.78, 0.62), zmb * 0.42 * smoothstep(rp, ri * 0.9, r) * (0.6 + 0.4 * sin(atan(dd.y, dd.x) * 11.0 + r * 60.0)));
    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r));
    c = mix(c, ic * (1.0 - 0.55 * em.g), ia);
    float cl = (1.0 - smoothstep(mix(0.03, 0.05, sqd), mix(0.042, 0.06, sqd), length(fqe - pc - vec2(-0.055, 0.06) * (1.0 + 0.3 * sqd) * fPupil.z))) + 0.8 * (1.0 - sqd) * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z)));
    c = mix(c, vec3(1.0), clamp(cl, 0.0, 1.0) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g));
  }
  if (zmb > 0.5) { for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w), dd = fq - pc; float r = length(dd), an = atan(dd.y, dd.x);
      float vn = smoothstep(0.86, 0.99, sin(an * 7.0 + sin(r * 38.0 + an * 3.0) * 0.7 + sd * 1.3)) * smoothstep(0.12, 0.2, r) * (1.0 - smoothstep(0.3, 0.42, r)); c = mix(c, vec3(0.55, 0.03, 0.04), vn * eye.a * (1.0 - em.r * 0.7));
      float lidY = pc.y + (i == 0 ? 0.05 : 0.13) - sd * dd.x * 0.22, lid = eye.a * smoothstep(lidY - 0.012, lidY + 0.012, fq.y), crease = eye.a * (1.0 - smoothstep(0.0, 0.03, abs(fq.y - lidY)));
      c = mix(c, vec3(0.1, 0.045, 0.08), lid); c = mix(c, vec3(0.36, 0.2, 0.28), crease * 0.9);
      float ring = (1.0 - eye.a) * smoothstep(0.52, 0.3, length(dd * vec2(0.9, 1.35))) * smoothstep(0.02, -0.2, dd.y); c = mix(c, c * vec3(0.42, 0.34, 0.5), ring * 0.8); } }
  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv)), mB = texture2D(fCol, fCell(fCells.w, cuv)), mo = mix(mA, mB, fMix.x) * fMix.z * (1.0 - sCoatM) * (1.0 - zmb);
  c = mix(c, mo.rgb, mo.a);
  faceInk = max(max(eye.a, mo.a), dotK) * vFace.z; diffuseColor.rgb = mix(diffuseColor.rgb, c, vFace.z); sEyeM = em.r * vFace.z;
}`;
// the goo's gloss, the face kept crisp, a rim of light along the body's edge, warmth glowing through the thin frills
const LIT_FS = `
{ float wet = max(sGloss, sCoatM) * (1.0 - 0.7 * faceInk);
  material.roughness = min(max(mix(0.62, 0.12, wet), 0.0525) + geometryRoughness, 1.0);
#ifdef USE_CLEARCOAT
  material.clearcoat = max(0.9 * sGloss * (1.0 - faceInk), sCoatM);
  material.clearcoatRoughness = min(max(mix(0.3, 0.06, wet), 0.0525) + geometryRoughness, 1.0);
#endif
}`;
const LOOK_FS = `
{ float ink = faceInk * (1.0 - sCoatM);
  reflectedLight.directDiffuse *= 1.0 - 0.5 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.5 * ink; reflectedLight.directSpecular *= 1.0 - 0.85 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.85 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.55;
  vec3 vd = normalize(vViewPosition), upV = normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz), kd = normalize(uKeyDir);
  float edge = 1.0 - saturate(dot(nonPerturbedNormal, vd));
  float rim = pow(edge, 3.0) * (0.5 + 0.5 * saturate(dot(nonPerturbedNormal, upV) + 0.4)) * (1.0 - faceInk) * (1.0 - 0.5 * sCoatM);
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.9), 0.4) * rim * 0.3;
  // thin parts: the key light shining through from behind, in the skin's own deeper colour; a soft wrap of warmth on the frills
  float thin = vJelly.z * (1.0 - sCoatM), tr = pow(saturate(dot(vd, -normalize(kd + nonPerturbedNormal * 0.4))), 3.0), wrap = saturate((dot(nonPerturbedNormal, kd) + 0.6) / 1.6);
  vec3 deep = pow(max(diffuseColor.rgb, vec3(0.0)), vec3(1.5)) * 1.6;
  totalEmissiveRadiance += deep * thin * (0.55 * tr + 0.12 * wrap) + diffuseColor.rgb * 0.05 * edge * edge * (1.0 - faceInk);
}`;

// ---------------- the material and its per-character state ----------------
export class Look {
  constructor(opts = {}) {
    const sh = faceSheets(opts.faceCell || 256);
    this.U = {
      uTeam: { value: new THREE.Color(opts.color || 0xff6b8a) }, uPaint: { value: new THREE.Color(opts.color || 0xff6b8a) }, uCoat: { value: new THREE.Vector4(0, Math.random() * 40, 0, 0) }, uCoatMix: { value: 1 },
      uJelly: { value: new THREE.Vector4(0, 0, 1.6, 0) }, uLag: { value: new THREE.Vector4(0, 0, 0, 0) }, uFace: { value: new THREE.Vector4(1.15, 0.8, 0.0, 1) }, uHead: { value: new THREE.Vector4(0, 1.37, 0.64, 0.38) },
      fCol: { value: sh.col }, fMsk: { value: sh.msk }, fCells: { value: new THREE.Vector4(0, 8, 0, 8) }, fMix: { value: new THREE.Vector4(0, 0, 1, 6) }, fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) }, fComp: { value: new THREE.Vector4(1, 1, 0, 0) },
      fIris: { value: new THREE.Vector3(0.16, 0.06, 0.035) }, fStyle: { value: 0 }, uKeyDir: { value: new THREE.Vector3(0.3, 0.6, 0.7) },
    };
    this.fangs = false; this.expr = 'neutral'; this.exprB = 'neutral'; this.exprK = 1; this.blinkT = 1 + Math.random() * 2; this.blinkK = 0; this.look = [0, 0]; this.lookT = [0, 0];
    this.att = { t: 1 + Math.random() * 2, eye: [0, 0] }; this.t = 0;
  }
  setColor(c) { this.U.uTeam.value.set(c); this.U.uPaint.value.set(c); return this; }
  setPaint(level) { this.U.uCoat.value.x = level; return this; }
  setFangs(on) { this.fangs = !!on; return this; }
  setEyeStyle(k) { this.U.fStyle.value = k; return this; }
  setExpression(name) { if (!(name in EXPR)) name = 'neutral'; if (name === this.exprB) return this; if (this.exprK < 1) this.expr = this.exprK > 0.5 ? this.exprB : this.expr; this.exprB = name; this.exprK = 0; return this; }
  blink() { this.blinkK = 0.13; }
  // per frame: expression crossfade, blinks, pupils drifting toward the look target (x right, y up, in face units), head squash compensation
  update(dt, look, squash = 0) {
    this.t += dt;
    if (this.exprK < 1) { this.exprK = Math.min(1, this.exprK + dt / 0.12); if (this.exprK >= 1) this.expr = this.exprB; }
    this.blinkT -= dt; if (this.blinkT <= 0) { this.blinkK = 0.13; this.blinkT = Math.random() < 0.22 ? 0.26 : 1.6 + Math.random() * 3.4; } if (this.blinkK > 0) this.blinkK -= dt;
    const A = this.att; A.t -= dt; if (A.t <= 0) { A.t = 1.2 + Math.random() * 2.8; A.eye[0] = (Math.random() * 2 - 1) * 0.12; A.eye[1] = (Math.random() * 2 - 1) * 0.05; }
    const lx = (look ? look[0] : 0) + A.eye[0], ly = (look ? look[1] : 0) + A.eye[1];
    this.look[0] += (lx - this.look[0]) * Math.min(1, dt * 26); this.look[1] += (ly - this.look[1]) * Math.min(1, dt * 26);
    const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 }; const shut = this.blinkK > 0 && !NO_SHUT[this.exprB];
    const pa = pupilOf(this.expr), pb = pupilOf(this.exprB), k = this.exprK, fang = this.fangs ? 6 : 0, ea = EXPR[this.expr], eb = EXPR[this.exprB];
    this.U.fCells.value.set(ea[0], ea[1] + fang, eb[0], eb[1] + fang); this.U.fMix.value.set(k, shut ? 1 : 0, 1, 6);
    this.U.fPupil.value.set(this.look[0], this.look[1], pa.pu + (pb.pu - pa.pu) * k, pa.py + (pb.py - pa.py) * k);
    this.U.fComp.value.set(1, 1 - 0.3 * squash, 0, 0); this.U.uLag.value.w = this.t;
    if (this.coatMixT !== undefined) this.U.uCoatMix.value += (this.coatMixT - this.U.uCoatMix.value) * Math.min(1, dt * 3);   // the coat's fill order glides between the crawl's and the stand's
  }
}
// the body material for one mesh of one character (the look's uniforms are shared by the character's two meshes)
export function axoMaterial(tex, look, meta) {
  const mat = new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.4, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.15, envMapIntensity: 1.0 });
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, look.U);
    sh.vertexShader = VERT_PARS + '\n' + sh.vertexShader.replace('#include <skinning_vertex>', '#include <skinning_vertex>\n' + VERT_MAIN);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\n' + FRAG_PARS)
      .replace('#include <map_fragment>', MAP_FS).replace('#include <color_fragment>', '#include <color_fragment>\n' + FACE_FS)
      .replace('#include <lights_physical_fragment>', '#include <lights_physical_fragment>\n' + LIT_FS)
      .replace('#include <aomap_fragment>', '#include <aomap_fragment>\n' + LOOK_FS);
    // this mesh's own head frame (rest space): centre and radius from the meta
    sh.uniforms.uHead = { value: new THREE.Vector4(...meta.headAbs, meta.headr) };
  };
  mat.customProgramCacheKey = () => 'axo-body';
  return mat;
}
