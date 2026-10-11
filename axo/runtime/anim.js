// Procedural animation for the axolotl puppet: states (stand idle, crawl, power, jetpack, pound, victory), stand <-> crawl transitions
// with a mesh swap hidden under a squash, and secondary motion (gill stalks, tail, digits) through damped springs.
// Pose conventions (canonical frames): x = flex about the hinge, y = twist about the bone, z = swing; see axo.js.
import * as THREE from 'three';
import { Pose, rot, setRot, mirrorQ, DEG } from './axo.js';

const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3(), _q = new THREE.Quaternion(), _s1 = new THREE.Quaternion(), _s2 = new THREE.Quaternion(), _s3 = new THREE.Quaternion();
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
        const q = this.LS.q[i].copy(P.Rel[i]).invert(); if (p >= 0) q.multiply(_q.copy(Fp[p]).invert()); q.multiply(Fs[i]); Fp.push(Fs[i].clone()); } }
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
    if (this.inAir) { this.airV -= 9.8 * dt; this.airY += this.airV * dt; if (this.airY <= 0) { this.airY = 0; this.inAir = false; const imp = Math.min(1, -this.airV / 4); this.sqV += 6.5 * imp; this.landK = imp; this.kickGills(0, 1.2 * imp); this.lagV.y += 0.5 * imp; for (let k = 0; k < 6; k++) this.tailSpring.v[k * 2 + 1] -= 60 * imp; } }
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
  plantStandFeet(out, lift, w = 1) { for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; out.contact('foot.' + s, _v.copy(this.standFeet[s]).setY(this.H.standFoot + lift), _v2.set(0.3 * m, 0, 1), _v3.set(0.25 * m, 0, 1), w); } }
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
      if (u < 0.6) { z = base.z + S / 2 - S * (u / 0.6); y = h; } else { const sw = (u - 0.6) / 0.4; z = base.z - S / 2 + S * smooth(sw); lift = Math.sin(sw * Math.PI); y = h + 0.045 * lift; }
      const fwd = isArm ? _v2.set(0.35 * m, 0, 1) : _v2.set(0.45 * m, 0, 1), pole = isArm ? _v3.set(m, 0.25, -0.5) : _v3.set(m, -0.2, 0.3);
      out.contact(en, _v.set(base.x * m, y, z), fwd, pole, 1);
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
      out.contact('hand.' + s, _v.set(this.crawlHand.x * m, this.H.crawlHand, this.crawlHand.z), _v2.set(0.35 * m, 0, 1), _v3.set(m, 0.3, -0.5), 1);
      out.contact('foot.' + s, _v.set(this.crawlFoot.x * m, this.H.crawlFoot, this.crawlFoot.z), _v2.set(0.45 * m, 0, 1), _v3.set(m, -0.2, 0.3), 1); }
    this.digits(out, 0.08, 0.3, 0.08); return out;
  }
  // ---------------- POWER POSE: akimbo. chest out, elbows out, fists planted on the hips, chin up ----------------
  powerPose(t, out) {
    const I = this.I, P = this.P; this.standIdle(t, out, 0.5); const br = Math.sin(t * 2.0);
    rot(out, I.spine, -5, 0, 0); rot(out, I.chest, -7 + br * 0.6, 0, 0); rot(out, I.neck, 2, 0, 0); rot(out, I.head, -9, 0, 0);
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
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
      this.P.aim(out, I['upperarm.' + s], _v.set(0.48 * m, 0.3 + sh * 0.01, 0.85), _v2.set(0, 1, -0.3)); this.P.aim(out, I['forearm.' + s], _v.set(0.35 * m, 0.55, 0.78), _v2.set(0, 1, -0.3)); setRot(out, I['hand.' + s], 30, 0, 0);
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
    const A = (n, d, z) => P.aim(out, I[n], _v.set(...d), _v2.set(...z));
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
      out.contact('hand.' + s, _v.set(sh.x + 0.1 * m, this.H.standHand, sh.z + 0.26), _v2.set(0.3 * m, 0, 1), _v3.set(0.6 * m, 0.2, -1), cw);
      out.contact('foot.' + s, _v.set(hp.x + 0.06 * m, this.H.standFoot, hp.z + 0.1), _v2.set(0.3 * m, 0, 1), _v3.set(0.3 * m, 0, 1), 1); }
    return out;
  }
  // arm tests (QA only): standing rest with both arms forward / sideways / up
  armTest(state, out) {
    const I = this.I; out.identity(); out.root.copy(this.standRoot); this.plantStandFeet(out, 0);
    for (const s of ['L', 'R']) { const m = s === 'L' ? 1 : -1; const d = state === 'armsfwd' ? [0.15 * m, 0.05, 1] : state === 'armsside' ? [m, 0.05, 0] : [0.25 * m, 1, 0.1];
      this.P.aim(out, I['upperarm.' + s], _v.set(...d), _v2.set(0, -1, 0.3), false); this.P.aim(out, I['forearm.' + s], _v.set(...d), _v2.set(0, -1, 0.3), false); }
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
        const k = ease.inOut((T.t - A - S) / C); this.fade = 1; this.squash = 1 - 0.2 * (1 - ease.out(clamp01((T.t - A - S) / 0.14))); this.crawl(this.t, this.B, dt, k); _v.copy(this.B.root);
        this.proneCrawl(out); this.offsetContacts(out, T.off); out.lerp(this.B, k); out.root.lerp(_v, k);
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
      P.aim(pose, e, _v.copy(c.fwd).setY(0).normalize(), _v2.set(0, -1, 0), false);   // sole flat on the floor
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
    rot(pose, I.chest, -1.8 * br, 0, 0); rot(pose, I.spine1, -1.2 * br, 0, 0);
    const g = this.chain.gills, vel = this.headVelS;
    for (let j = 0; j < 6; j++) {
      const i1 = g[j * 2]; _q.copy(this.P.Fp[i1]).invert(); _v.copy(vel).applyQuaternion(_q);   // head velocity in the stalk's posed frame
      const flutter = Math.sin(this.t * 2.3 + j * 1.7) * 2.0 + Math.sin(this.t * 3.7 + j * 0.9) * 1.0; const cl = x => Math.max(-25, Math.min(25, x));
      // drag from the head's motion and from the body's acceleration (a turn, a speed change): the stalks trail the other way
      const sgn = j < 3 ? 1 : -1; this.gillTarget[j * 2] = cl(flutter - _v.z * 20 - this.accS.z * 6); this.gillTarget[j * 2 + 1] = cl(-_v.x * 20 - this.accS.x * 5 * sgn);
    }
    const gs = this.gillSpring.step(this.gillTarget, dt);
    const cm = this.mesh === 'crawl' ? 0.6 : 1;   // the crawl sculpt's stalks are fused to the shoulders: gentler flutter there
    const lo = this.mesh === 'crawl' ? 0 : 0.4;   // the crawl sculpt's lowest stalks are fused to the shoulders: no flutter there
    const stalkAmp = [cm, 0.9 * cm, lo * cm, cm, 0.9 * cm, lo * cm];
    for (let j = 0; j < 6; j++) { const a = gs[j * 2] * stalkAmp[j], b = gs[j * 2 + 1] * stalkAmp[j]; rot(pose, g[j * 2], a * 0.55, 0, b * 0.55); rot(pose, g[j * 2 + 1], a * 0.7, 0, b * 0.7); }
    // joint limits: stand poses relative to the stand rest, crawl relative to the symmetric crawl rest
    const base = this.mesh === 'crawl' ? this.LS : null; const P = this.P;
    for (let i = 0; i < P.nb; i++) {
      if (base) { _q.copy(base.q[i]).invert().multiply(pose.q[i]); const bq = pose.q[i]; bq.copy(_q); if (P.clampBone(pose, i)) {} bq.premultiply(base.q[i]); }
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
    L.U.uJelly.value.set(0.018 * this.breath * (0.7 + 0.8 * this.exertS), this.sq * 0.9 + stretch, this.mesh === 'crawl' ? 0.9 : 1.6, this.jellyRipple);
    L.U.uLag.value.x = this.lagP.x; L.U.uLag.value.y = this.lagP.y; L.U.uLag.value.z = this.lagP.z;
    L.coatMixT = this.mesh === 'crawl' ? 0 : 1;
    L.update(dt, [this.look.yaw / 90 * 0.3, this.look.pitch / -50 * 0.2], this.sq * 0.6 + stretch);
  }
  trackHead(dt) {
    const P = this.P; const h = P.jointWorld(this.mesh, 'head', _v2);
    if (dt > 0) { this.headVel.copy(h).sub(this.headPrev).divideScalar(dt); this.rootVel.copy(this.pose.root).sub(this.rootPrev).divideScalar(dt); }
    if (this.headVel.length() > 20) this.headVel.set(0, 0, 0);
    this.headVelS.lerp(this.headVel, 1 - Math.exp(-dt * 16)); this.headPrev.copy(h); this.rootPrev.copy(this.pose.root);
  }
}
