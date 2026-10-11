// Procedural animation for the axolotl puppet (v7): states (stand idle, crawl, power, jetpack, pound, victory, crouch), stand <-> crawl
// transitions, secondary motion (gill stalks, tail, digits, breathing, the neck's small life) and the soft-body jelly layer's drive.
// Pose conventions (canonical frames): x = flex about the hinge, y = twist about the bone, z = swing; see axo.js.
//  - Every change of state is blended by inertialization: the pose shown last frame is carried into the new state as an offset that decays
//    smoothly from its own velocity to zero, so nothing ever jumps, freezes or changes speed abruptly (no snapshot crossfades).
//  - Stand <-> crawl: the outgoing mesh folds into the shared crouch; the incoming mesh takes the very same pose (the two meshes share one
//    canonical skeleton, so every bone points the same way) and both ride ONE skeleton that morphs from the outgoing body's proportions to
//    the incoming one's, so the two bodies coincide while a complementary screen-space dither swaps them (each pixel shows exactly one of the
//    two: no see-through double image), under a jelly squash pulse; the incoming mesh then settles into its own state.
import * as THREE from 'three';
import { Pose, rot, setRot, mirrorQ, DEG } from './axo.js';

const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _v4 = new THREE.Vector3(), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _s1 = new THREE.Quaternion(), _s2 = new THREE.Quaternion(), _s3 = new THREE.Quaternion();
const _wE = new THREE.Euler(), _wq = new THREE.Quaternion(), _wq2 = new THREE.Quaternion(), _wF = new THREE.Quaternion();
const smooth = t => t * t * (3 - 2 * t), clamp01 = t => Math.max(0, Math.min(1, t));
// a Catmull-Rom curve through the points K (n samples per span)
function catmull(K, n) { const out = [K[0].clone()]; for (let i = 0; i < K.length - 1; i++) { const p0 = K[Math.max(0, i - 1)], p1 = K[i], p2 = K[i + 1], p3 = K[Math.min(K.length - 1, i + 2)];
  for (let j = 1; j <= n; j++) { const t = j / n, t2 = t * t, t3 = t2 * t; out.push(new THREE.Vector3().addScaledVector(p0, -0.5 * t3 + t2 - 0.5 * t).addScaledVector(p1, 1.5 * t3 - 2.5 * t2 + 1).addScaledVector(p2, -1.5 * t3 + 2 * t2 + 0.5 * t).addScaledVector(p3, 0.5 * t3 - 0.5 * t2)); } }
  return out; }
export const ease = { inOut: t => smooth(clamp01(t)), out: t => 1 - Math.pow(1 - clamp01(t), 3), in: t => Math.pow(clamp01(t), 3) };
// rotation vector (axis * angle) of a unit quaternion, shortest way round, and back
function qlog(q, out, o) { let x = q.x, y = q.y, z = q.z, w = q.w; if (w < 0) { x = -x; y = -y; z = -z; w = -w; } const s = Math.sqrt(x * x + y * y + z * z); const a = s > 1e-9 ? 2 * Math.atan2(s, w) / s : 2; out[o] = x * a; out[o + 1] = y * a; out[o + 2] = z * a; }
function qexp(x, y, z, q) { const a = Math.sqrt(x * x + y * y + z * z); if (a < 1e-9) return q.set(x * 0.5, y * 0.5, z * 0.5, 1).normalize(); const s = Math.sin(a / 2) / a; return q.set(x * s, y * s, z * s, Math.cos(a / 2)); }

export class Spring {
  constructor(n, k, c) { this.x = new Float32Array(n); this.v = new Float32Array(n); this.k = k; this.c = c; }
  step(target, dt) {
    dt = Math.min(dt, 1 / 30); const sub = 2, h = dt / sub;
    for (let s = 0; s < sub; s++) for (let i = 0; i < this.x.length; i++) { const a = this.k * (target[i] - this.x[i]) - this.c * this.v[i]; this.v[i] += a * h; this.x[i] += this.v[i] * h; }
    return this.x;
  }
}
// a critically damped follower (second order): the value and its rate both stay continuous when the input steps
class Follow { constructor(w, x = 0) { this.w = w; this.x = x; this.v = 0; } step(target, dt) { const w = this.w, h = Math.min(dt, 1 / 30); const a = w * w * (target - this.x) - 2 * w * this.v; this.v += a * h; this.x += this.v * h; return this.x; } }

export class Animator {
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
    const tgt = [(N.glance[0] + drift[0]) * amt + this.look.yaw * 0.6, (N.glance[1] + drift[1]) * amt + br * 1.2 + this.look.pitch * 0.6, (N.glance[2] + drift[2]) * amt];
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
