// Roll Model axolotl: shared-skeleton puppet (stand + crawl meshes), procedural animation states and secondary motion.
// Pose = per-bone local rotation in the bone's canonical frame (Y along the bone, Z ventral / flexion side, X = Y x Z = hinge)
// plus a root position. The same pose drives either mesh: each mesh stores its own rest frame per bone, so a pose is
// mapped onto a mesh through  R_mesh(b) = Fpose(b) * inverse(Frest_mesh(b)).
import * as THREE from 'three';

const DEG = Math.PI / 180;
const _e = new THREE.Euler(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _m = new THREE.Matrix4();

export async function loadMesh(base, tex) {
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
  const mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.62, metalness: 0, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.22 });
  const mesh = new THREE.SkinnedMesh(g, mat); mesh.add(bones[0]); mesh.bind(new THREE.Skeleton(bones)); mesh.frustumCulled = false; mesh.castShadow = true; mesh.receiveShadow = false;
  return { mesh, bones, byName, meta, F, rest, end, names: meta.bones.map(b => b.name) };
}

// a pose: one quaternion per bone (canonical local) + root position
export class Pose {
  constructor(nb) { this.q = []; for (let i = 0; i < nb; i++) this.q.push(new THREE.Quaternion()); this.root = new THREE.Vector3(); }
  copy(p) { for (let i = 0; i < this.q.length; i++) this.q[i].copy(p.q[i]); this.root.copy(p.root); return this; }
  identity() { for (const q of this.q) q.identity(); return this; }
  lerp(p, t) { for (let i = 0; i < this.q.length; i++) this.q[i].slerp(p.q[i], t); this.root.lerp(p.root, t); return this; }
}

export class Puppet {
  constructor(stand, crawl) {
    this.m = { stand, crawl }; this.names = stand.names; const nb = this.nb = this.names.length; this.idx = {}; this.names.forEach((n, i) => this.idx[n] = i);
    this.par = stand.meta.bones.map(b => b.parent ? this.idx[b.parent] : -1);
    // canonical rest-relative frames from the standing model; the crawl rest expressed as a pose in those frames
    this.Rel = []; this.LC = new Pose(nb); this.Fp = []; this.R = [];
    for (let i = 0; i < nb; i++) {
      const p = this.par[i]; const rel = p >= 0 ? stand.F[p].clone().invert().multiply(stand.F[i]) : stand.F[i].clone(); this.Rel.push(rel);
      const wc = p >= 0 ? crawl.F[p].clone().invert().multiply(crawl.F[i]) : crawl.F[i].clone();
      this.LC.q[i].copy(rel).invert().multiply(wc); this.Fp.push(new THREE.Quaternion()); this.R.push(new THREE.Quaternion());
    }
    this.LC.root.copy(crawl.rest[0]); this.standRoot = stand.rest[0].clone();
    // mirror pairs (L <-> R) and the symmetric crawl rest
    this.mirror = this.names.map(n => { const m = n.includes('.L') ? n.replace('.L', '.R') : n.includes('.R') ? n.replace('.R', '.L') : n; return this.idx[m]; });
    this.LS = new Pose(nb); this.LS.root.copy(this.LC.root); this.LS.root.x = 0;
    for (let i = 0; i < nb; i++) {
      const a = this.LC.q[i], b = mirrorQ(this.LC.q[this.mirror[i]], _q); this.LS.q[i].copy(a).slerp(b, 0.5);
    }
    // the tail in the symmetric crawl pose: straight back and horizontal (the stand's rest tail frames), not the sculpt's curled-up tail
    {
      const Fp = []; for (let i = 0; i < nb; i++) { const p = this.par[i]; Fp.push(p >= 0 ? Fp[p].clone().multiply(this.Rel[i]).multiply(this.LS.q[i]) : this.Rel[i].clone().multiply(this.LS.q[i])); }
      for (let k = 1; k <= 6; k++) { const i = this.idx['tail' + k], p = this.par[i];
        this.LS.q[i].copy(this.Rel[i]).invert().multiply(_q.copy(Fp[p]).invert()).multiply(stand.F[i]);
        Fp[i].copy(Fp[p]).multiply(this.Rel[i]).multiply(this.LS.q[i]); }
    }
    // bone lengths (canonical, from the stand) for reach computations
    this.len = stand.meta.bones.map((b, i) => stand.rest[i].distanceTo(stand.end[i]));
  }
  // write a pose into one mesh's bones
  apply(which, pose) {
    const M = this.m[which], FM = M.F, Fp = this.Fp, R = this.R, par = this.par, bones = M.bones;
    for (let i = 0; i < this.nb; i++) {
      const p = par[i];
      if (p >= 0) Fp[i].copy(Fp[p]).multiply(this.Rel[i]).multiply(pose.q[i]); else Fp[i].copy(this.Rel[i]).multiply(pose.q[i]);
      R[i].copy(Fp[i]).multiply(_q.copy(FM[i]).invert());
      if (p >= 0) bones[i].quaternion.copy(R[p]).invert().multiply(R[i]); else { bones[i].quaternion.copy(R[i]); bones[i].position.copy(pose.root); }
    }
  }
  // set pose.q[i] so the bone's posed Y axis points along dir (world) with its Z (ventral) toward zHint; evaluates the ancestors' pose first
  aim(pose, i, dir, zHint) {
    const Fp = this.Fp;  // scratch: walk the chain root -> parent
    const chain = []; for (let b = this.par[i]; b >= 0; b = this.par[b]) chain.push(b); chain.reverse();
    for (const b of chain) { const p = this.par[b]; if (p >= 0) Fp[b].copy(Fp[p]).multiply(this.Rel[b]).multiply(pose.q[b]); else Fp[b].copy(this.Rel[b]).multiply(pose.q[b]); }
    const y = _v.copy(dir).normalize(), z = _v2.copy(zHint).addScaledVector(y, -y.dot(zHint)); if (z.lengthSq() < 1e-8) z.set(0, -1, 0).addScaledVector(y, -y.dot(_v2.set(0, -1, 0))); z.normalize();
    const x = _v3.crossVectors(y, z); _m.makeBasis(x, y, z); _q.setFromRotationMatrix(_m);  // target world frame
    const p = this.par[i]; pose.q[i].copy(this.Rel[i]).invert(); if (p >= 0) pose.q[i].multiply(_q2.copy(Fp[p]).invert()); pose.q[i].multiply(_q);
  }
  // world position of a joint for a mesh after apply (mesh at the origin)
  jointWorld(which, name, out) { const M = this.m[which]; M.mesh.updateMatrixWorld(true); return M.byName[name].getWorldPosition(out || new THREE.Vector3()); }
}
export function mirrorQ(q, out) { return out.set(q.x, -q.y, -q.z, q.w); }
// rotate a pose bone by Euler degrees in its own (posed) frame
export function rot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].multiply(_q2.setFromEuler(_e)); }
export function setRot(pose, i, x, y, z) { _e.set(x * DEG, y * DEG, z * DEG, 'XYZ'); pose.q[i].setFromEuler(_e); }

// ---------- secondary motion: damped springs ----------
export class Spring {
  constructor(n, k, c) { this.x = new Float32Array(n); this.v = new Float32Array(n); this.k = k; this.c = c; this.tmp = new Float32Array(n); }
  step(target, dt, drive) {
    dt = Math.min(dt, 1 / 30); const sub = 2, h = dt / sub;
    for (let s = 0; s < sub; s++) for (let i = 0; i < this.x.length; i++) {
      const a = this.k * (target[i] - this.x[i]) - this.c * this.v[i] + (drive ? drive[i] : 0);
      this.v[i] += a * h; this.x[i] += this.v[i] * h;
    }
    return this.x;
  }
}

// ---------- procedural animation ----------
const smooth = t => t * t * (3 - 2 * t), clamp01 = t => Math.max(0, Math.min(1, t));
export const ease = { inOut: t => smooth(clamp01(t)), out: t => 1 - Math.pow(1 - clamp01(t), 3), in: t => Math.pow(clamp01(t), 3) };

export class Animator {
  constructor(puppet) {
    const P = this.P = puppet; const nb = P.nb; const I = this.I = P.idx;
    this.pose = new Pose(nb); this.tmpA = new Pose(nb); this.tmpB = new Pose(nb); this.outA = new Pose(nb); this.outB = new Pose(nb);
    this.t = 0; this.state = 'stand'; this.prev = null; this.blend = 1; this.blendDur = 0.4; this.phase = 0; this.speed = 1;
    this.mesh = 'stand'; this.fade = 1;  // fade: 1 = current mesh fully shown, during a swap both meshes are rendered
    this.gillSpring = new Spring(12, 160, 9); this.gillTarget = new Float32Array(12); this.gillDrive = new Float32Array(12);
    this.tailSpring = new Spring(12, 90, 7); this.tailTarget = new Float32Array(12);
    this.fingerSpring = new Spring(2, 60, 6); this.fingerTarget = new Float32Array(2);
    this.headPrev = new THREE.Vector3(); this.headVel = new THREE.Vector3(); this.headVelS = new THREE.Vector3(); this.rootPrev = new THREE.Vector3(); this.rootVel = new THREE.Vector3();
    this.rootYawPrev = 0; this.rootYawVel = 0; this.groundScroll = 0; this.gaitPhase = 0; this.lastDt = 1 / 60;
    this.chain = { spine: ['hips', 'spine', 'spine1', 'chest', 'neck'].map(n => I[n]), tail: [1, 2, 3, 4, 5, 6].map(k => I['tail' + k]),
      gills: ['L', 'R'].flatMap(s => [0, 1, 2].flatMap(k => [I[`gill${k}.${s}.1`], I[`gill${k}.${s}.2`]])),
      fingers: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`finger${k}.${s}.1`], I[`finger${k}.${s}.2`]])), toes: ['L', 'R'].map(s => [0, 1, 2, 3].map(k => [I[`toe${k}.${s}.1`], I[`toe${k}.${s}.2`]])) };
    this.trans = null;
  }
  // ---- state machine ----
  set(state) {
    if (state === this.state && !this.trans) return;
    const from = this.state;
    if ((from === 'crawl' || from === 'toCrawl') && state !== 'crawl') { this.trans = { kind: 'crawlToStand', t: 0, target: state }; this.state = 'toStand'; return; }
    if (state === 'crawl' && from !== 'crawl') { this.snapshot(); this.trans = { kind: 'standToCrawl', t: 0 }; this.state = 'toCrawl'; return; }
    this.snapshot(); this.state = state; this.blend = 0; this.blendDur = state === 'victory' ? 0.25 : 0.45;
  }
  snapshot() { this.tmpB.copy(this.pose); this.blend = 0; }
  // ---- per-frame ----
  update(dt) {
    dt = Math.min(dt, 1 / 20); this.lastDt = dt; this.t += dt; const P = this.P;
    const out = this.outA;
    if (this.trans) this.updateTransition(dt, out);
    else {
      this.evalState(this.state, this.t, out, dt);
      if (this.blend < 1) { this.blend = Math.min(1, this.blend + dt / this.blendDur); const k = ease.inOut(this.blend); this.outB.copy(this.tmpB).lerp(out, k); out.copy(this.outB); }
    }
    this.pose.copy(out);
    this.secondary(dt);
    P.apply(this.mesh, this.pose);
    if (this.fade < 1) { P.apply(this.other(this.mesh), this.otherPose || this.pose); }
    this.trackHead(dt);
  }
  other(m) { return m === 'stand' ? 'crawl' : 'stand'; }
  // the pose for a state at time t
  evalState(state, t, out, dt) {
    const P = this.P, I = this.I;
    switch (state) {
      case 'stand': this.standIdle(t, out); break;
      case 'crawl': this.crawl(t, out, dt); break;
      case 'power': this.powerPose(t, out); break;
      case 'jetpack': this.jetpack(t, out); break;
      case 'pound': this.groundPound(t, out); break;
      case 'victory': this.victory(t, out); break;
      case 'prone': out.copy(P.LS); break;
      case 'crouch': this.crouch(out); break;
      case 'sym': out.copy(P.LS); break;
      case 'rest': out.identity(); out.root.copy(P.standRoot); break;
      default: this.standIdle(t, out);
    }
  }
  // ---------- STAND IDLE ----------
  standIdle(t, out, amp = 1) {
    const I = this.I, P = this.P; out.identity(); out.root.copy(P.standRoot);
    const br = Math.sin(t * 2.1) * amp, sway = Math.sin(t * 0.7) * amp, sway2 = Math.sin(t * 0.7 + 1.3) * amp;
    out.root.y += -0.004 + br * 0.004; out.root.x += sway * 0.012;
    rot(out, I.hips, 0, 0, sway * 1.5); rot(out, I.spine, br * 0.8, 0, -sway * 1.2); rot(out, I.spine1, br * 1.0, sway2 * 2, 0);
    rot(out, I.chest, br * 1.4, 0, -sway * 0.8); rot(out, I.neck, -br * 1.2, 0, 0);
    rot(out, I.head, Math.sin(t * 0.9 + 0.4) * 2.5 * amp - 2, Math.sin(t * 0.5) * 7 * amp, Math.sin(t * 0.35) * 3 * amp);
    // arms relaxed at the sides, elbows softly bent, slight breathing swing
    for (const s of ['L', 'R']) {
      const m = s === 'L' ? 1 : -1;
      rot(out, I['upperarm.' + s], 4 + br * 1.5, 0, 6 * m); rot(out, I['forearm.' + s], 12 + br * 2, 0, 0); rot(out, I['hand.' + s], 6, 0, 0);
      rot(out, I['thigh.' + s], 0, 0, sway * 1.5 * m); rot(out, I['shin.' + s], 0, 0, 0);
    }
    // tail: lazy lateral sway with a travelling phase
    this.tailWave(out, t * 1.3, 3.5 * amp, 0.9, 0);
    this.digits(out, 0.15 + br * 0.05, 0.3, 0.1);
    return out;
  }
  tailWave(out, ph, ampDeg, lag, lift) {
    const I = this.I;
    for (let k = 0; k < 6; k++) { const i = this.chain.tail[k]; const a = ampDeg * (0.5 + k * 0.18); this.tailTarget[k * 2] = Math.sin(ph - k * lag) * a; this.tailTarget[k * 2 + 1] = lift * (k < 2 ? 1 : 0.5); }
  }
  digits(out, curl, spread, toeCurl) {
    const I = this.I;
    for (let s = 0; s < 2; s++) {
      this.chain.fingers[s].forEach((f, k) => { rot(out, f[0], curl * 25, 0, (k - 1.5) * spread * 14); rot(out, f[1], curl * 35, 0, 0); });
      this.chain.toes[s].forEach((f, k) => { rot(out, f[0], toeCurl * 20, 0, (k - 1.5) * spread * 10); rot(out, f[1], toeCurl * 25, 0, 0); });
    }
  }
  // ---------- CRAWL ----------
  crawl(t, out, dt, speed = 1) {
    const I = this.I, P = this.P; out.copy(P.LS);
    this.gaitPhase += dt * speed * 2 * Math.PI * 1.05; const ph = this.gaitPhase;
    const s = Math.sin(ph), c = Math.cos(ph);
    // body: standing-wave lateral undulation (girdles in antiphase), travelling toward the tail
    const sp = this.chain.spine; const amps = [-7, 5, 8, 6, 4];
    let yawSum = 0;
    for (let k = 0; k < sp.length; k++) { const a = amps[k] * Math.sin(ph - k * 0.55 - 0.3); rot(out, sp[k], 0, 0, a); yawSum += a; }
    // head counter-rotates so it stays steady, with a small bob
    rot(out, I.head, 3 + Math.sin(ph * 2) * 1.5, Math.sin(ph * 2 + 1) * 1.5, -yawSum * 0.75);
    rot(out, I.neck, Math.sin(ph * 2 + 0.5) * 1.5, 0, 0);
    // root: lateral sway with the wave, slight bob twice per cycle
    out.root.x += Math.sin(ph - 0.3) * 0.035; out.root.y += Math.sin(ph * 2 + 0.9) * 0.012;
    // limbs: diagonal pairs. LF (phase 0) with RH; RF with LH (phase pi)
    const limbs = [['upperarm.L', 'forearm.L', 'hand.L', 0, 1, 'fingers', 0], ['upperarm.R', 'forearm.R', 'hand.R', Math.PI, -1, 'fingers', 1], ['thigh.R', 'shin.R', 'foot.R', 0, -1, 'toes', 1], ['thigh.L', 'shin.L', 'foot.L', Math.PI, 1, 'toes', 0]];
    for (const [ua, fa, ha, off, m, dig, side] of limbs) {
      const p = ph + off; const sw = Math.sin(p), lift = Math.max(0, Math.sin(p + 0.35));  // swing when sin>0: limb protracts forward
      const liftS = smooth(lift), stance = 1 - liftS;
      const isArm = ua.startsWith('upper'); const reach = isArm ? 28 : 26;
      // protraction / retraction about the vertical (local Z), lift about the hinge X, elbow / knee flex during swing
      rot(out, I[ua], -liftS * 11 + 2, 0, sw * reach * m * (isArm ? 1 : 0.9));
      rot(out, I[fa], liftS * 46 - 4 - Math.cos(p) * 3, 0, 0);
      // hand / foot: keep flat on the ground in stance (counter the limb retraction), toes splay on the plant, curl in the air
      rot(out, I[ha], -liftS * 30 + 8, 0, -sw * reach * 0.8 * m);
      const plant = smooth(clamp01((Math.cos(p + 0.2) + 0.2) * 1.3)) * stance;
      this.chain[dig][side].forEach((f, k) => { rot(out, f[0], liftS * 22 - plant * 6, 0, (k - 1.5) * (6 + plant * 10) * (dig === 'toes' ? 1 : 1)); rot(out, f[1], liftS * 30 - plant * 4, 0, 0); });
    }
    // tail: continues the body wave with increasing amplitude, through the spring chain
    this.tailWave(out, ph - 2.2, 9, 0.7, 0);
    this.groundScroll += dt * speed * 0.5;
    return out;
  }
  // ---------- POWER POSE ----------
  powerPose(t, out) {
    const I = this.I; this.standIdle(t, out, 0.6);
    const br = Math.sin(t * 2.1);
    rot(out, I.spine, -4, 0, 0); rot(out, I.chest, -6 + br * 0.5, 0, 0); rot(out, I.neck, 4, 0, 0); rot(out, I.head, -8, 0, 0);
    const P = this.P, A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      A('upperarm.' + s, [0.62 * m, -0.78, -0.1], [-m, 0, 0.6]); A('forearm.' + s, [-0.72 * m, -0.45, 0.5], [0, -1, 0.3]); A('hand.' + s, [-0.7 * m, -0.5, 0.5], [0, -1, 0]);
      rot(out, I['thigh.' + s], 6, 0, 12 * m); rot(out, I['shin.' + s], 8, 0, 0); rot(out, I['foot.' + s], -6, 0, 0); }
    out.root.x = 0; out.root.y -= 0.03; this.digits(out, 1.0, 0.0, 0.1); this.tailWave(out, t * 1.6, 5, 0.8, 0.0);
    return out;
  }
  // ---------- JETPACK ----------
  jetpack(t, out) {
    const I = this.I; this.standIdle(t, out, 0.4); const w = Math.sin(t * 3.2), w2 = Math.sin(t * 2.5 + 1);
    out.root.y += 0.55 + w2 * 0.03; out.root.x += Math.sin(t * 1.1) * 0.02;
    rot(out, I.hips, -6, 0, w2 * 2); rot(out, I.spine, -4, 0, 0); rot(out, I.chest, 4, 0, 0); rot(out, I.head, 6, w * 3, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const ws = s === 'L' ? w : -w;
      // arms out and slightly back like grabbing the jetpack straps, legs dangling with knees bent, feet swinging
      rot(out, I['upperarm.' + s], -16, 0, 34 * m); rot(out, I['forearm.' + s], 70 + ws * 3, 0, 0); rot(out, I['hand.' + s], 25, 0, 0);
      rot(out, I['thigh.' + s], -24 + ws * 4, 0, 10 * m); rot(out, I['shin.' + s], 62 + ws * 8, 0, 0); rot(out, I['foot.' + s], 18 + ws * 6, 0, 0); }
    // tail curled under the body
    for (let k = 0; k < 6; k++) { rot(out, this.chain.tail[k], 9 + k * 2.5, 0, 0); }
    this.tailWave(out, t * 2.5, 3, 1.0, 0); this.digits(out, 0.55, 0.1, 0.4);
    return out;
  }
  // ---------- GROUND-POUND WIND-UP ----------
  groundPound(t, out) {
    const I = this.I; this.standIdle(t, out, 0.3); const sh = Math.sin(t * 14) * 0.4;  // tense quiver
    out.root.y += 0.4 + 0.02 * Math.sin(t * 2.2);
    rot(out, I.hips, 10, 0, 0); rot(out, I.spine, 12, 0, 0); rot(out, I.chest, 10, 0, 0); rot(out, I.neck, 6, 0, 0); rot(out, I.head, -10, 0, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      // both arms raised high over the head, fists clenched; knees tucked up
      this.P.aim(out, I['upperarm.' + s], _v.set(0.75 * m, 0.45 + sh * 0.01, 0.45), _v2.set(0, 1, 0)); this.P.aim(out, I['forearm.' + s], _v.set(0.3 * m, 0.85, 0.45), _v2.set(0, 0, 1)); rot(out, I['hand.' + s], 25, 0, 0);
      rot(out, I['thigh.' + s], -70, 0, 14 * m); rot(out, I['shin.' + s], 95, 0, 0); rot(out, I['foot.' + s], 20, 0, 0); }
    for (let k = 0; k < 6; k++) rot(out, this.chain.tail[k], -6 - k * 2, 0, 0);
    this.tailWave(out, t * 3, 4, 1, 0); this.digits(out, 1.0, 0.0, 0.6);
    return out;
  }
  // ---------- VICTORY ----------
  victory(t, out) {
    const I = this.I; this.standIdle(t, out, 0.5); const T = (t * 1.6) % 1; const hop = Math.max(0, Math.sin(T * Math.PI * 2)); const pump = Math.sin(t * 1.6 * Math.PI * 2);
    out.root.y += hop * 0.18; out.root.x = 0;
    rot(out, I.spine, -3 - hop * 4, 0, 0); rot(out, I.chest, -5, 0, 0); rot(out, I.head, -14 + hop * 6, 0, Math.sin(t * 3) * 6);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const pm = s === 'L' ? pump : -pump;
      this.P.aim(out, I['upperarm.' + s], _v.set(0.82 * m, 0.5 + pm * 0.12, 0.12), _v2.set(0, 0, 1)); this.P.aim(out, I['forearm.' + s], _v.set(0.5 * m, 0.85 + pm * 0.1, 0.1), _v2.set(0, 0, 1)); rot(out, I['hand.' + s], -10, 0, 0);
      rot(out, I['thigh.' + s], -hop * 22, 0, 6 * m); rot(out, I['shin.' + s], hop * 40, 0, 0); rot(out, I['foot.' + s], hop * 18, 0, 0); }
    this.tailWave(out, t * 6, 7, 0.9, 0); this.digits(out, 0.15, 0.6, 0.1);
    return out;
  }
  // squat forward on the way down to all fours (and up from them)
  crouch(out) {
    const I = this.I, P = this.P; out.identity(); out.root.copy(P.standRoot); out.root.y = 0.33; out.root.z = 0.05;
    rot(out, I.hips, 30, 0, 0); rot(out, I.spine, 12, 0, 0); rot(out, I.spine1, 10, 0, 0); rot(out, I.chest, 6, 0, 0); rot(out, I.neck, -22, 0, 0); rot(out, I.head, -30, 0, 0);
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1;
      A('thigh.' + s, [0.35 * m, -0.25, 0.9], [0, -1, -0.4]); A('shin.' + s, [0.05 * m, -1, -0.35], [0, -0.3, -1]); A('foot.' + s, [0.1 * m, 0, 1], [0, -1, 0]);
      A('upperarm.' + s, [0.4 * m, -0.55, 0.75], [0, -0.3, 1]); A('forearm.' + s, [0.1 * m, -0.95, 0.3], [0, 0, 1]); A('hand.' + s, [0.1 * m, -0.2, 1], [0, -1, 0]); }
    A('tail1', [0, -0.12, -1], [0, -1, 0]); for (let k = 2; k <= 6; k++) A('tail' + k, [0, -0.05, -1], [0, -1, 0]);
    this.digits(out, 0.2, 0.5, 0.2); return out;
  }
  proneStand(out) { const P = this.P, I = this.I; out.copy(P.LS); const A = (n, d) => P.aim(out, I[n], _v.set(...d), _v2.set(0, -1, 0));
    A('tail1', [0, -0.55, -0.85]); A('tail2', [0, -0.4, -0.92]); A('tail3', [0, -0.2, -0.98]); for (let k = 4; k <= 6; k++) A('tail' + k, [0, -0.03, -1]); return out; }
  // ---------- TRANSITIONS ----------
  // stand -> crawl: drop onto the belly on the stand mesh, swap to the crawl mesh at the crawl rest pose, slide into the gait
  // crawl -> stand: ease the gait out to the crawl rest, swap to the stand mesh, push up to standing
  updateTransition(dt, out) {
    const P = this.P, T = this.trans; T.t += dt; const I = this.I;
    const A = 0.55, S = 0.14, C = 0.45;  // seconds: drop / crossfade / settle
    if (T.kind === 'standToCrawl') {
      if (T.t < A) {
        // phase A on the stand mesh: idle -> prone (crawl rest). Crouch first (knees, arms forward), then the belly comes down
        const u = T.t / A; this.mesh = 'stand'; this.fade = 1;
        if (u < 0.45) { const k = ease.inOut(u / 0.45); this.crouch(this.tmpA); out.copy(this.tmpB).lerp(this.tmpA, k); }
        else { const k = ease.inOut((u - 0.45) / 0.55); this.crouch(this.tmpA); this.proneStand(this.outB); out.copy(this.tmpA).lerp(this.outB, k); }
      } else if (T.t < A + S) {
        // phase B: crossfade stand -> crawl at the matched pose; the crawl's root is offset so the heads coincide
        if (!T.off) { T.off = this.headOffset('stand', 'crawl', P.LS); this.gaitPhase = 0; }
        const k = (T.t - A) / S; out.copy(P.LS); out.root.add(T.off);
        this.mesh = 'crawl'; this.fade = k; this.otherPose = this.otherPose || new Pose(P.nb); this.proneStand(this.otherPose);
      } else if (T.t < A + S + C) {
        const k = ease.inOut((T.t - A - S) / C); this.fade = 1;
        this.crawl(this.t, this.tmpA, dt, k);
        const r = _v2.copy(this.tmpA.root); out.copy(P.LS).lerp(this.tmpA, k); out.root.copy(P.LS.root).add(T.off).lerp(r, k);
      } else { this.trans = null; this.state = 'crawl'; this.blend = 1; this.crawl(this.t, out, dt); }
    } else { // crawlToStand
      const C2 = 0.35, S2 = 0.14, A2 = 0.6;
      if (T.t < C2) {
        const k = ease.inOut(T.t / C2); this.crawl(this.t, this.tmpA, dt, 1 - k); out.copy(this.tmpA).lerp(P.LS, k); this.mesh = 'crawl'; this.fade = 1;
        this.tailWave(out, this.t, 2, 1, 0);
      } else if (T.t < C2 + S2) {
        if (!T.off) T.off = this.headOffset('crawl', 'stand', P.LS);
        const k = (T.t - C2) / S2; this.proneStand(out); out.root.add(T.off);
        this.mesh = 'stand'; this.fade = k; this.otherPose = this.otherPose || new Pose(P.nb); this.otherPose.copy(P.LS);
      } else if (T.t < C2 + S2 + A2) {
        const u = (T.t - C2 - S2) / A2; this.fade = 1; const from = this.proneStand(this.outB); from.root.add(T.off);
        if (u < 0.5) { const k = ease.inOut(u / 0.5); this.crouch(this.tmpA); out.copy(from).lerp(this.tmpA, k); }
        else { const k = ease.out((u - 0.5) / 0.5); this.evalState(T.target, this.t, this.tmpA, dt); this.crouch(this.tmpB); out.copy(this.tmpB).lerp(this.tmpA, k); out.root.y += Math.sin(k * Math.PI) * 0.05; }
      } else { this.trans = null; this.state = T.target; this.blend = 1; this.evalState(T.target, this.t, out, dt); }
    }
  }
  // root offset that makes mesh B's head coincide with mesh A's head when both show `pose` (both roots at pose.root)
  headOffset(a, b, pose) {
    const P = this.P; P.apply(a, pose); const ha = P.jointWorld(a, 'head'); P.apply(b, pose); const hb = P.jointWorld(b, 'head');
    return ha.sub(hb);
  }
  // ---------- SECONDARY MOTION ----------
  secondary(dt) {
    const I = this.I, P = this.P, pose = this.pose;
    // tail: spring chain follows the procedural targets (lateral about Z, lift about X) and lags the root's yaw / lateral motion
    const tl = this.tailSpring.step(this.tailTarget, dt);
    const lat = -this.rootVel.x * 55 - this.rootYawVel * 10;   // body sliding sideways / turning throws the tail the other way
    for (let k = 0; k < 6; k++) rot(pose, this.chain.tail[k], tl[k * 2 + 1], 0, tl[k * 2] + lat * (0.3 + k * 0.15));
    // gill stems: idle flutter + drag from the head's motion, through an under-damped spring (lag and overshoot)
    const g = this.chain.gills; const vel = this.headVelS;
    for (let j = 0; j < 6; j++) {
      const i1 = g[j * 2], i2 = g[j * 2 + 1];
      // project the head velocity into the stem's posed frame: drag bends the stem away from the motion
      _q.copy(this.P.Fp[i1]).invert(); _v.copy(vel).applyQuaternion(_q);
      const flutter = Math.sin(this.t * 2.3 + j * 1.7) * 1.5 + Math.sin(this.t * 3.7 + j * 0.9) * 0.8;
      const cl = x => Math.max(-28, Math.min(28, x));
      this.gillTarget[j * 2] = cl(flutter + _v.z * 28); this.gillTarget[j * 2 + 1] = cl(_v.x * 28);
    }
    const gs = this.gillSpring.step(this.gillTarget, dt);
    for (let j = 0; j < 6; j++) { const i1 = g[j * 2], i2 = g[j * 2 + 1]; const a = gs[j * 2], b = gs[j * 2 + 1];
      rot(pose, i1, a * 0.6, 0, b * 0.6); rot(pose, i2, a * 0.7, 0, b * 0.7); }
  }
  trackHead(dt) {
    const P = this.P; const h = P.jointWorld(this.mesh, 'head', _v2);
    if (dt > 0) { this.headVel.copy(h).sub(this.headPrev).divideScalar(dt); this.rootVel.copy(this.pose.root).sub(this.rootPrev).divideScalar(dt); }
    if (this.headVel.length() > 20) this.headVel.set(0, 0, 0);
    this.headVelS.lerp(this.headVel, 1 - Math.exp(-dt * 18));
    this.headPrev.copy(h); this.rootPrev.copy(this.pose.root);
    const yaw = 0; this.rootYawVel = 0;
  }
}
