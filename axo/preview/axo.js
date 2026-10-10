// Roll Model axolotl runtime: mesh loader (.bin/.json/.webp), shared-skeleton Puppet with joint limits, procedural Animator.
// A pose = per-bone local rotation expressed in the bone's canonical frame (Y along the bone, Z = flexion / ventral side, X = Y x Z = hinge)
// plus a root position. Each mesh stores its own canonical rest frame per bone, so one pose can drive either mesh.
import * as THREE from 'three';

export const DEG = Math.PI / 180;
const _e = new THREE.Euler(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _m = new THREE.Matrix4();

export async function loadMesh(base, tex, matOpts = {}) {
  const meta = await (await fetch(base + '.json')).json(), buf = Uint8Array.from(atob((await (await fetch(base + '.b64.txt')).text()).trim()), c => c.charCodeAt(0)).buffer;
  const n = meta.n, o = meta.off, g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, o[0], n * 3), 3));
  g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(buf, o[1], n * 3), 3));
  g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(buf, o[2], n * 2), 2));
  g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, o[3], n * 4), 4));
  g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, o[4], n * 4), 4, true));
  g.setIndex(new THREE.BufferAttribute(meta.i32 ? new Uint32Array(buf, o[5], meta.ni) : new Uint16Array(buf, o[5], meta.ni), 1));
  const bones = [], byName = {}, F = [], rest = [], end = [];
  for (const b of meta.bones) { const bn = new THREE.Bone(); bn.name = b.name; bones.push(bn); byName[b.name] = bn; F.push(new THREE.Quaternion(...b.q)); rest.push(new THREE.Vector3(...b.pos)); end.push(new THREE.Vector3(...b.end)); }
  const pidx = {}; meta.bones.forEach((b, i) => pidx[b.name] = i);
  for (let i = 0; i < bones.length; i++) { const b = meta.bones[i], bn = bones[i]; if (b.parent) { byName[b.parent].add(bn); bn.position.copy(rest[i]).sub(rest[pidx[b.parent]]); } else bn.position.copy(rest[i]); }
  const mat = new THREE.MeshStandardMaterial(Object.assign({ map: tex, roughness: 0.6, metalness: 0 }, matOpts));
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(bones[0]); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false; mesh.castShadow = true;
  return { mesh, bones, byName, meta, F, rest, end, names: meta.bones.map(b => b.name), parent: meta.bones.map(b => b.parent ? pidx[b.parent] : -1) };
}

export class Pose {
  constructor(nb) { this.q = []; for (let i = 0; i < nb; i++) this.q.push(new THREE.Quaternion()); this.root = new THREE.Vector3(); }
  copy(p) { for (let i = 0; i < this.q.length; i++) this.q[i].copy(p.q[i]); this.root.copy(p.root); return this; }
  identity() { for (const q of this.q) q.identity(); return this; }
  lerp(p, t) { for (let i = 0; i < this.q.length; i++) this.q[i].slerp(p.q[i], t); this.root.lerp(p.root, t); return this; }
}

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

const _av = new THREE.Vector3(), _av2 = new THREE.Vector3(), _aq = new THREE.Quaternion();
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
      for (let i = 0; i < nb; i++) { const p = P.par[i]; const q = this.LS.q[i].copy(P.Rel[i]).invert(); if (p >= 0) q.multiply(_aq.copy(Fp[p]).invert()); q.multiply(Fs[i]); Fp.push(Fs[i].clone()); } }
    this.standRoot = P.m.stand.rest[0].clone();
    this.chain = { spine: ['hips', 'spine', 'spine1', 'chest', 'neck'].map(n => I[n]), tail: [1, 2, 3, 4, 5, 6].map(k => I['tail' + k]),
      gills: ['L', 'R'].flatMap(s => [0, 1, 2].flatMap(k => [I[`gill${k}.${s}.1`], I[`gill${k}.${s}.2`]])),
      fingers: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`finger${k}.${s}.1`], I[`finger${k}.${s}.2`]])), toes: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`toe${k}.${s}.1`], I[`toe${k}.${s}.2`]])) };
    this.gillSpring = new Spring(12, 140, 8); this.gillTarget = new Float32Array(12);
    this.tailSpring = new Spring(12, 80, 7); this.tailTarget = new Float32Array(12);
    this.headPrev = new THREE.Vector3(); this.headVel = new THREE.Vector3(); this.headVelS = new THREE.Vector3(); this.rootPrev = new THREE.Vector3(); this.rootVel = new THREE.Vector3();
    this.events = [];
  }
  // ---------------- state machine ----------------
  set(state) {
    if (state === this.state && !this.trans) return;
    const from = this.state; const crawlish = s => s === 'crawl' || s === 'toCrawl';
    if (crawlish(from) && state !== 'crawl') { this.trans = { kind: 'crawlToStand', t: 0, target: state }; this.state = 'toStand'; return; }
    if (state === 'crawl' && !crawlish(from)) { this.from.copy(this.pose); this.trans = { kind: 'standToCrawl', t: 0 }; this.state = 'toCrawl'; return; }
    this.from.copy(this.pose); this.state = state; this.blend = 0; this.blendDur = state === 'victory' ? 0.25 : state === 'pound' ? 0.3 : 0.45;
  }
  update(dt) {
    dt = Math.min(dt, 1 / 20); this.t += dt; const out = this.A;
    if (this.trans) this.updateTransition(dt, out);
    else {
      this.evalState(this.state, this.t, out, dt);
      if (this.blend < 1) { this.blend = Math.min(1, this.blend + dt / this.blendDur); const k = ease.inOut(this.blend); this.B.copy(this.from).lerp(out, k); out.copy(this.B); }
    }
    this.pose.copy(out); this.secondary(dt);
    this.P.apply(this.mesh, this.pose);
    if (this.fade < 1) this.P.apply(this.mesh === 'stand' ? 'crawl' : 'stand', this.other);
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
    this.tailWave(t * 1.3, 4 * amp, 0.9, 0); this.digits(out, 0.12 + br * 0.04, 0.35, 0.05);
    return out;
  }
  // ---------------- CRAWL (on the symmetric crawl rest) ----------------
  crawl(t, out, dt, speed = 1, dir = 1) {
    const I = this.I, P = this.P; out.copy(this.LS);
    this.gait += dt * speed * 2 * Math.PI * 1.1; const ph = this.gait;
    // trunk: standing-wave lateral undulation (about the ventral axis), girdles in antiphase, travelling toward the tail
    const sp = this.chain.spine, amps = [-5, 4, 7, 3, 1.5]; let yawSum = 0;
    for (let k = 0; k < sp.length; k++) { const a = amps[k] * Math.sin(ph - k * 0.55 - 0.3) * speed; rot(out, sp[k], 0, 0, a); yawSum += a; }
    rot(out, I.head, 2 + Math.sin(ph * 2) * 1.2 * speed + this.look.pitch, this.look.yaw, 0);   // the head rides the body wave (no counter-yaw: the sculpt's lower gills are fused to the shoulders)
    out.root.x += Math.sin(ph - 0.3) * 0.03 * speed; out.root.y += Math.sin(ph * 2 + 0.9) * 0.008 * speed;
    // limbs in diagonal pairs: LF with RH (phase 0), RF with LH (phase pi). x = swing fore/aft, z = lift (mirrored on the right)
    const limbs = [['upperarm.L', 'forearm.L', 'hand.L', 0, 1, 'fingers', 0], ['upperarm.R', 'forearm.R', 'hand.R', Math.PI, -1, 'fingers', 1], ['thigh.R', 'shin.R', 'foot.R', 0, -1, 'toes', 1], ['thigh.L', 'shin.L', 'foot.L', Math.PI, 1, 'toes', 0]];
    for (const [ua, fa, ha, off, m, dig, side] of limbs) {
      const p = ph + off; const sw = Math.sin(p) * speed, lift = smooth(Math.max(0, Math.sin(p + 0.35))) * speed, stance = 1 - lift;
      const isArm = ua.startsWith('upper'); const reach = isArm ? 22 : 20;
      rot(out, I[ua], sw * reach, 0, lift * 10 * m);
      rot(out, I[fa], lift * 35 - Math.cos(p) * 4 * speed, 0, 0);
      // hand / foot: stay flat in stance (counter the swing about the vertical), lift the fingers off the ground in the air
      rot(out, I[ha], -lift * 12, 0, -sw * reach * 0.6 * m);
      const plant = smooth(clamp01((Math.cos(p + 0.2) + 0.2) * 1.3)) * stance;
      this.chain[dig][side].forEach((f, k) => { rot(out, f[0], -lift * 12 + plant * 4, 0, (k - 1.5) * (5 + plant * 5) * m); rot(out, f[1], -lift * 8 + plant * 3, 0, 0); });
    }
    this.tailWave(ph - 2.0, 10 * speed + 2, 0.7, 0);
    return out;
  }
  proneCrawl(out) { out.copy(this.LS); this.tailWave(0, 0, 1, 0); return out; }
  // ---------------- POWER POSE: akimbo. chest out, elbows out, fists planted on the hips, chin up ----------------
  powerPose(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.5); const br = Math.sin(t * 2.0);
    rot(out, I.spine, -5, 0, 0); rot(out, I.chest, -7 + br * 0.6, 0, 0); rot(out, I.neck, 2, 0, 0); rot(out, I.head, -9, 0, 0);
    const A = (n, d, z) => P.aim(out, I[n], _av.set(...d), _av2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      // upper arm down and well out to the side (elbow away from the body), forearm back in to the waist, hand on the hip bone
      A('upperarm.' + s, [0.7 * m, -0.68, -0.15], [-m, 0, 0.6]); A('forearm.' + s, [-0.35 * m, -0.55, 0.55], [-m, 0, 0.6]); A('hand.' + s, [-0.3 * m, -0.8, 0.4], [-0.9 * m, -0.3, 0.2]);
      rot(out, I['thigh.' + s], 4, 0, 10 * m); rot(out, I['shin.' + s], 6, 0, 0); rot(out, I['foot.' + s], -5, 0, 0); }
    out.root.x = 0; out.root.y -= 0.025; this.digits(out, 0.9, 0.0, 0.1); this.tailWave(t * 1.6, 5, 0.8, 0);
    return out;
  }
  // ---------------- JETPACK: hanging, arms out for balance, legs and tail dangling ----------------
  jetpack(t, out) {
    const I = this.I; this.standIdle(t, out, 0.4); const w = Math.sin(t * 3.0), w2 = Math.sin(t * 2.3 + 1);
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
    const I = this.I; this.standIdle(t, out, 0.3); const sh = Math.sin(t * 16) * 0.5;
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
    this.tailWave(t * 6, 7, 0.9, 0); this.digits(out, 0.1, 0.6, 0.1);
    return out;
  }
  // ---------------- CROUCH (stand mesh): on all fours-ish, the body low and horizontal, head looking ahead, tail trailing low ----------------
  crouch(out, k = 1) {
    const I = this.I, P = this.P; out.identity(); out.root.copy(this.standRoot); out.root.y -= 0.3 * k; out.root.z += 0.1 * k;
    rot(out, I.hips, 58 * k, 0, 0); rot(out, I.spine, 8 * k, 0, 0); rot(out, I.spine1, 6 * k, 0, 0); rot(out, I.chest, 4 * k, 0, 0); rot(out, I.neck, -30 * k, 0, 0); rot(out, I.head, -34 * k, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      setRot(out, I['thigh.' + s], 75 * k, 0, 16 * m * k); setRot(out, I['shin.' + s], 112 * k, 0, 0); setRot(out, I['foot.' + s], -8 * k, 0, 0);
      setRot(out, I['upperarm.' + s], 68 * k, 0, 20 * m * k); setRot(out, I['forearm.' + s], 10 * k, 0, 0); setRot(out, I['hand.' + s], -30 * k, 0, 0); }
    // the pelvis pitched forward would lift the tail: counter it at the root, then let the tail curve down behind
    rot(out, this.chain.tail[0], 52 * k, 0, 0); for (let kk = 1; kk < 6; kk++) rot(out, this.chain.tail[kk], 5 * k, 0, 0);
    this.tailWave(0, 0, 1, 0); this.digits(out, 0.1, 0.5, 0.1);
    return out;
  }
  // ---------------- TRANSITIONS ----------------
  // stand -> crawl: (A) stand mesh folds into the crouch, (B) short squash + crossfade to the crawl mesh in its rest (heads aligned), (C) crawl settles into the gait
  // crawl -> stand: (A) gait eases out, (B) squash + crossfade to the stand mesh in the crouch, (C) stand rises into the target state
  updateTransition(dt, out) {
    const P = this.P, T = this.trans, I = this.I; T.t += dt;
    const A = 0.32, S = 0.07, C = 0.35;
    if (T.kind === 'standToCrawl') {
      if (T.t < A) { const k = ease.inOut(T.t / A); this.crouch(this.B, 1); out.copy(this.from).lerp(this.B, k); this.mesh = 'stand'; this.fade = 1; this.squash = 1 - 0.2 * ease.in(clamp01((T.t - A + 0.12) / 0.12)); }
      else if (T.t < A + S) {
        if (!T.off) { T.off = this.headOffset(); this.gait = 0; }
        const k = (T.t - A) / S; this.mesh = 'crawl'; this.fade = smooth(k); this.squash = 0.8;
        this.proneCrawl(out); out.root.add(T.off); this.crouch(this.other, 1);
      } else if (T.t < A + S + C) {
        const k = ease.inOut((T.t - A - S) / C); this.fade = 1; this.squash = 1 - 0.2 * (1 - ease.out(clamp01((T.t - A - S) / 0.14))); this.crawl(this.t, this.B, dt, k); _av.copy(this.B.root);
        this.proneCrawl(out); out.root.add(T.off); out.lerp(this.B, k); out.root.lerp(_av, k);
      } else { this.trans = null; this.state = 'crawl'; this.blend = 1; this.crawl(this.t, out, dt); }
    } else {
      const C2 = 0.3, A2 = 0.45;
      if (T.t < C2) { const k = ease.inOut(T.t / C2); this.crawl(this.t, this.B, dt, 1 - k); this.proneCrawl(out); out.copy(this.B).lerp(out, k); this.mesh = 'crawl'; this.fade = 1; this.squash = 1 - 0.2 * ease.in(clamp01((T.t - C2 + 0.12) / 0.12)); this.tailWave(0, 0, 1, 0); }
      else if (T.t < C2 + S) {
        if (!T.off) T.off = this.headOffset();
        const k = (T.t - C2) / S; this.mesh = 'stand'; this.fade = smooth(k); this.squash = 0.8;
        this.crouch(out, 1); this.proneCrawl(this.other); this.other.root.add(T.off);
      } else if (T.t < C2 + S + A2) {
        const k = ease.out((T.t - C2 - S) / A2); this.fade = 1; this.squash = 1 - 0.2 * (1 - ease.out(clamp01((T.t - C2 - S) / 0.14))); this.evalState(T.target, this.t, this.B, dt); this.crouch(out, 1); out.lerp(this.B, k); out.root.y += Math.sin(k * Math.PI) * 0.03;
      } else { this.trans = null; this.state = T.target; this.blend = 1; this.evalState(T.target, this.t, out, dt); }
    }
    return out;
  }
  // root offset for the crawl mesh (in its rest) so its head sits where the stand mesh's head is in the crouch
  headOffset() {
    const P = this.P; this.crouch(this.B, 1); P.apply('stand', this.B); const hs = P.jointWorld('stand', 'head'); this.proneCrawl(this.C); P.apply('crawl', this.C); const hc = P.jointWorld('crawl', 'head');
    const off = hs.sub(hc); off.y = Math.max(off.y, 0); return off;
  }
  // ---------------- SECONDARY MOTION ----------------
  secondary(dt) {
    const pose = this.pose, I = this.I;
    const tl = this.tailSpring.step(this.tailTarget, dt); const lat = -this.rootVel.x * 40;
    for (let k = 0; k < 6; k++) rot(pose, this.chain.tail[k], tl[k * 2 + 1], 0, tl[k * 2] + lat * (0.25 + k * 0.12));
    const g = this.chain.gills, vel = this.headVelS;
    for (let j = 0; j < 6; j++) {
      const i1 = g[j * 2]; _aq.copy(this.P.Fp[i1]).invert(); _av.copy(vel).applyQuaternion(_aq);   // head velocity in the stalk's posed frame
      const flutter = Math.sin(this.t * 2.3 + j * 1.7) * 2.0 + Math.sin(this.t * 3.7 + j * 0.9) * 1.0; const cl = x => Math.max(-25, Math.min(25, x));
      this.gillTarget[j * 2] = cl(flutter - _av.z * 20); this.gillTarget[j * 2 + 1] = cl(-_av.x * 20);
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
  trackHead(dt) {
    const P = this.P; const h = P.jointWorld(this.mesh, 'head', _av2);
    if (dt > 0) { this.headVel.copy(h).sub(this.headPrev).divideScalar(dt); this.rootVel.copy(this.pose.root).sub(this.rootPrev).divideScalar(dt); }
    if (this.headVel.length() > 20) this.headVel.set(0, 0, 0);
    this.headVelS.lerp(this.headVel, 1 - Math.exp(-dt * 16)); this.headPrev.copy(h); this.rootPrev.copy(this.pose.root);
  }
}
