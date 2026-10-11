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
const SLITHER = { on: 4.4, off: 3.2, after: 0.45, f0: 0.75, f1: 0.3, pw: 0.34, tail: 22 }; // (f0 + f1: strokes a second at cruising speed; pw: the push's share of a stroke)
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
  const SL = L.sl || (L.sl = { k: 0, on: false, was: false, hold: 0, u: 0, tph: 0, push: 0, reach: 0 });
  { const vc = L.vc, ok = !air && !TR && M.spin === undefined && !((M.climbCurl || 0) > 0) && !((M.ball || 0) > 0.05) && L.ballK < 0.05;
    if (ok && vc > SLITHER.on) SL.hold += dt; else if (!ok || vc < SLITHER.off) SL.hold = 0;
    SL.on = ok && (SL.on ? vc > SLITHER.off : SL.hold > SLITHER.after);
    if (SL.on && !SL.was) SL.u = 0; SL.was = SL.on; // (it goes in on a push)
    SL.k += ((SL.on ? 1 : 0) - SL.k) * Math.min(1, dt * (SL.on ? 4.5 : 6)); }
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
  const T = 50 * Math.tanh((-amp * c1 + bend * 0.92 + HT * 0.45) / 50);
  this.worldTurn(out, I.hips, Ap * c1, 0);
  this.worldTurn(out, sp[1], T * 0.34, 0);
  this.worldTurn(out, sp[2], T * 0.37, -L.steer * 3 * act);
  this.worldTurn(out, sp[3], T * 0.29, 0);
  this.worldTurn(out, I.neck, hs * 0.25 + bend * 0.1 + HT * 0.3, -HT * 0.12);
  this.worldTurn(out, I.head, hs * 0.25 + bend * 0.07 + HT * 0.25, -HT * 0.3);
  if (sl > 0.001) { // (a stroke: u runs 0 to 1, the push its first part, the glide the rest)
    const f = SLITHER.f0 + SLITHER.f1 * clamp01((L.vc - 4) / 4); SL.u = (SL.u + dt * f) % 1; SL.tph += dt * 2 * Math.PI * f * 0.5;
    const u = SL.u, PW = SLITHER.pw, push = u < PW ? Math.sin(Math.PI * u / PW) : 0, th = 2 * Math.PI * u;
    SL.push = push; SL.reach = u < PW ? 1 - smooth(u / PW) : u > 0.82 ? smooth((u - 0.82) / 0.18) : 0; // (the arms out ahead at the push's start, swept back along the sides by its end, eased forward again at the glide's end)
    const env = sl * (0.45 + 0.55 * (1 - push)); let acc = 0; // (the wave: gentle, travelling from the shoulders to the hips, fullest in the glide; straighter through the push)
    const w = (j, A, s) => { const a = A * env * Math.sin(th - s * 1.4); acc += a; this.worldTurn(out, j, a, 0); };
    w(I.hips, 6, 1.0); w(sp[1], 7.5, 0.75); w(sp[2], 6, 0.5); w(sp[3], 3.5, 0.3); w(I.neck, 1.5, 0.15);
    this.worldTurn(out, I.head, -0.85 * acc, 0); // (the head held to the way it's going, not swung about by the wave)
    const surge = u < PW ? smooth(u / PW) : 1 - smooth((u - PW) / (1 - PW)); out.root.z += (0.045 * surge - 0.02) * sl; out.root.y -= 0.03 * sl; // (the body lunges on the push and settles back through the glide)
    const hp = Math.sin(2 * Math.PI * (u - 0.06)) * sl; // (the head's bob: down into the push, up through the glide; positive: nose down)
    this.pitchTurn(out, sp[3], 0.08 * hp); this.pitchTurn(out, I.neck, 0.16 * hp); this.pitchTurn(out, I.head, 0.12 * hp); }
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
    if (sl > 0.001) { // (swimming: the limbs flat along its sides, the arms sweeping back from out ahead on each push, the legs trailing beside the tail with a little kick)
      const pk2 = L.pk2 && L.pk2f === this.t ? L.pk2 : (L.pk2f = this.t, L.pk2 = P.fk('crawl', out)), pr = pk2[l.root], q = l.q || (l.q = new THREE.Vector3()), R = SL.reach, K = SL.push;
      if (l.arm) q.set(pr.x + (0.045 + 0.08 * R) * l.m, l.home.y + 0.04 - 0.02 * R, pr.z - 0.24 + 0.16 * R);
      else q.set(pr.x + (0.035 + 0.02 * K) * l.m, l.home.y + 0.035, pr.z - 0.28 - 0.04 * K);
      q.lerpVectors(l.p, q, sl); tp = q; lift = Math.max(lift, 0.8 * sl); }
    out.contact(l.en, tp, LV2.set(LB.fwd.x * l.m * (1 - sl) + 0.08 * l.m * sl, -0.35 * lift * (1 - sl), LB.fwd.z * (1 - sl) - sl), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1);
    const dig = this.chain[l.arm ? 'fingers' : 'toes'][l.m > 0 ? 0 : 1], ns = 1 - sl; // (swimming: the fingers and toes closed together, nearly straight)
    dig.forEach((g, k) => { rot(out, g[0], (4 + lift * 16 - (air ? 8 : 0)) * ns + 3 * sl, 0, (k - 1.5) * (5 + (air ? 5 : 0)) * l.m * ns - (k - 1.5) * 2 * l.m * sl); rot(out, g[1], (3 + l.lift * 12) * ns + 2 * sl, 0, 0); });
  }
  // the tail carries the wave on behind the hips
  this.tailWave(2 * Math.PI * L.ph + Math.PI * 0.85, ((4 + 15 * clamp01(v / 6.5)) * act + 1.5) * (1 - sl), 0.75, air ? -3 : 0);
  if (sl > 0.001) { const tt = this.tailTarget, c = L.ttc || (L.ttc = new Float32Array(tt.length)); c.set(tt); // (the slither's wave carries on down the tail, bigger toward its tip)
    this.tailWave(SL.tph, SLITHER.tail * sl, 0.55, 0); for (let k = 0; k < tt.length; k++) tt[k] += c[k]; } // (the tail sways slowly, once each way every two strokes, steadying it)
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
      for (let j = 0; j < 6; j++) { const sgn = j < 3 ? 1 : -1; add[j * 2] = -fl * 2.5 * (1 - L.act); add[j * 2 + 1] = swing * 14 * sgn + fl * 7 * (1 - L.act); } this.gillAddOn = true; }
    // the original computes the targets and steps the spring: the turn's swing goes in through the push the spring is given
    ss0.call(this, dt);
    // the tail follows the body's bend round a turn (its spring lags it in and swings it back after)
    if (L && this.state === 'crawl') this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.16) + (this.motion.spin !== undefined ? L.tlg * 0.27 : 0);
  };
  // the targets: wrapped so the added swing lands in the spring's target before it is stepped
  const SpringStep = Spring.prototype.step;
  Spring.prototype.step = function (target, dt) { if (this.addTo) { const a = this.addTo(); if (a) for (let i = 0; i < target.length; i++) target[i] += a[i]; } return SpringStep.call(this, target, dt); };
  const init0 = Animator.prototype.initLoco;
  Animator.prototype.initLoco = function () { const L = init0.call(this); this.gillSpring.addTo = () => this.gillAddOn ? this.gillAdd : null; return L; };
}
}
