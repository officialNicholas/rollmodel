"""v315: the boss demo in the Sunken Keep. Season Conquest > the stage preview now has the boss in it, and the stage, the boss and the
demo go into releases (until now they were in test pages only).

- The entrance (a new move, 'emerge', about 7.4 s, with its own camera the first time): the pool churns and spits; both gloves burst up
  out of the slime either side and slam down on the curb, taking hold; it hauls itself up between them in two heaves, eyes first, the
  slime pouring off, shuddering with the strain; it crouches, then shoves off the curb with one great beat of its bell and shoots up past
  its hover, gloves trailing under it, flares out wide at the top, settles, and bumps its fists in a burst of sparks. After that, Go.
- Then it swims: it floats over the arena like a jellyfish, bobbing with its bell, and moves itself in beats of the bell (each beat a
  push, a glide, the water slowing it), the bell tipping into the way it goes. It keeps near the pool, drifting toward your side of it
  (never more than about 3.4 from the middle), turns to watch you, and a slow current never lets it hang dead still. It beats faster
  when it has further to go.
- The panel (top left upright, left side sideways): each move on a button (Entrance, Punch, Slam, Sweep, Zap, Hurt, Stunned, Taunt,
  Defeat), Follow (it swims after you, or stays over the pool) and Auto attack (it picks a move on you every few seconds). The moves aim
  at you: a fist, the slam's shockwave, the zap and the sweep knock you back (a bump and a tumble, never a knock-out). Entrance plays the
  whole entrance again with its camera; after Defeat it sinks into the pool and comes back up by itself a few seconds later.
- The boss runtime learns to leave the pool's middle (its floor, its pool and the stun's gloves go by where the pool really is), takes a
  lean, a roll and a beat rate from outside (the swim), and has the new move.
- Leaving (Pause > Menu) lets the boss go (its meshes, looks and buffers)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

# ---- the runtime: the pool's real middle, the swim's input, the entrance
RT = [
    ("const B = { group, isReady: false, busy: false, scale,",
     "const B = { swim: { lean: 0, roll: 0, pulse: 1 }, group, isReady: false, busy: false, scale,"),
    ("T.lean = 0.04 * wn(t, 0.35, 0.57, 0.91); T.roll = 0.035 * wn(t, 0.29, 0.47, 0.83);",
     "T.lean = 0.04 * wn(t, 0.35, 0.57, 0.91) + B.swim.lean; T.roll = 0.035 * wn(t, 0.29, 0.47, 0.83) + B.swim.roll; // (v315: + the swim's own tip)"),
    ("T.pulse = 1; T.pulseAmp = 1; T.squash = 1;", "T.pulse = B.swim.pulse; T.pulseAmp = 1; T.squash = 1;"),
    ("      const floorAt = (x, z) => x * x + z * z < POOL_R * POOL_R ? POOL_Y - 50 : FLOOR;",
     "      // (v315) the pool's middle in the model's space: the boss can swim off it (opts.poolC, world; by default under the group)\n"
     "      const PC_W = opts.poolC ? new V3().copy(opts.poolC) : null, _pc = new V3(), RIM_R = opts.rimR || POOL_R + 0.35, RIM_H = opts.rimH === undefined ? 0.22 : opts.rimH; let PCX = 0, PCZ = 0;\n"
     "      const pcSync = () => { if (PC_W) { _pc.copy(PC_W).applyMatrix4(Gi); PCX = _pc.x; PCZ = _pc.z; } };\n"
     "      const floorAt = (x, z) => { const dx = x - PCX, dz = z - PCZ; return dx * dx + dz * dz < POOL_R * POOL_R ? POOL_Y - 50 : FLOOR; };"),
    ("st.t += dt; syncG();", "st.t += dt; syncG(); pcSync();"),
    ("        syncG(); yawQ.setFromAxisAngle(AX_Y, st.yaw); yawQi.copy(yawQ).invert();",
     "        syncG(); pcSync(); yawQ.setFromAxisAngle(AX_Y, st.yaw); yawQi.copy(yawQ).invert();"),
    ("init(m) { st.root.set(0, POOL_Y - 4.6, 0);", "init(m) { st.root.set(PCX, POOL_Y - 4.6, PCZ);"),
    ("if (mv.M && mv.name === 'defeat' && name !== 'intro') return 0;", "if (mv.M && mv.name === 'defeat' && name !== 'intro' && name !== 'emerge') return 0;"), # (the entrance brings it back up too)
    ("const r = Math.hypot(mB.x, mB.z), rMin = POOL_R + 1.1; if (r < rMin) { mB.x *= rMin / Math.max(r, 1e-3); mB.z *= rMin / Math.max(r, 1e-3); }",
     "const ex = mB.x - PCX, ez = mB.z - PCZ, r = Math.hypot(ex, ez), rMin = POOL_R + 1.1; if (r < rMin) { const k = rMin / Math.max(r, 1e-3); mB.x = PCX + ex * k; mB.z = PCZ + ez * k; }"),
]

EMERGE = r"""        // ---- (v315) emerge: the entrance. The pool churns; both gloves burst up out of the slime either side and slam down on the curb,
        // taking hold; it hauls itself up between them in two heaves, eyes first, the slime pouring off; it crouches, then shoves off with
        // one great beat of its bell and shoots up past its hover, the gloves trailing under it; it flares out at the top, settles, and
        // bumps its fists in a burst of sparks. Starts out of sight under the pool's middle (the group should be over it)
        emerge: { len: 7.4,
          init(m) { st.root.set(PCX, POOL_Y - 4.2, PCZ); st.rootV.set(0, 0, 0); st.yaw = yawTo(st.look); m.yaw = st.yaw; snap();
            // where the gloves take hold: the curb on its left and its right (the model's space), a little to the front
            const c = Math.cos(m.yaw), sn = Math.sin(m.yaw), y = FLOOR + RIM_H + FR() * 0.72;
            m.P.set(PCX + c * RIM_R + sn * 0.5, y, PCZ - sn * RIM_R + c * 0.5); m.C.set(PCX - c * RIM_R + sn * 0.5, y, PCZ + sn * RIM_R + c * 0.5); },
          run(m, t) {
            const w = 1 - sstep(6.7, 7.4, t);
            const kH = sstep(1.05, 1.4, t), kG = sstep(1.42, 1.62, t), kRel = sstep(4.05, 4.18, t), hold = kG * (1 - kRel);
            const pull1 = sstep(1.85, 2.6, t), sag = sstep(2.6, 2.8, t) * (1 - sstep(2.8, 3.0, t)), pull2 = sstep(2.95, 3.6, t), kC = sstep(3.62, 4.02, t);
            const kL = clamp01((t - 4.05) / 0.55), up = kL > 0 ? eOut(kL) : 0, kDown = sstep(4.6, 5.8, t), kB = sstep(5.75, 6.05, t), kBump = sstep(6.05, 6.17, t);
            // the root: deep under the slime, hauled up to the surface, a crouch, then shot up past the hover and down onto it
            const y0 = POOL_Y - 4.2, yMid = POOL_Y - 1.15, ySurf = POOL_Y + 0.85, yC = POOL_Y + 0.3, yTop = HOVER + 2.3;
            let y = y0 + (yMid - y0) * pull1 - 0.35 * sag + (ySurf - yMid) * pull2 + (yC - ySurf) * kC;
            if (kL > 0) y = yC + (yTop - yC) * up;
            if (kDown > 0) y = yTop + (HOVER - yTop) * eIO(kDown);
            off(0, y - HOVER, 0, w); T.rootK = t < 4.05 ? 3.2 : lerp(3.4, 1, sstep(4.4, 5.6, t));
            T.clipY = t < 4.7 ? POOL_Y : -1e4; T.clipBand = 0.35; T.yaw = m.yaw;
            // the strain: it shudders as it hauls; tips back into the crouch; stretches as it shoots up
            const strain = (sstep(1.9, 2.05, t) * (1 - sstep(2.5, 2.6, t)) + sstep(3.0, 3.12, t) * (1 - sstep(3.5, 3.62, t))) * Math.sin(t * 31);
            T.roll = lerp(T.roll, 0.06 * strain, w); T.lean = lerp(T.lean, 0.1 * pull2 * (1 - kC) - 0.14 * kC * (1 - up), w);
            T.squash = lerp(T.squash, 1 - 0.14 * kC * (1 - kL) + 0.24 * Math.sin(Math.PI * Math.min(1, kL * 1.25)) * (1 - kDown), w);
            T.pulseAmp = lerp(T.pulseAmp, t < 4.0 ? 0.45 : t < 4.8 ? 1.8 : 1.15, w); T.pulse = lerp(T.pulse, t < 3.6 ? 0.6 : 1, w);
            T.tentW = lerp(T.tentW, t < 4.05 ? 0.4 : 1.7 - 0.7 * kDown, w);
            for (const s of SIDES) {
              const g = s === 'L' ? 1 : -1, A = s === 'L' ? m.P : m.C;
              // under the slime, then bursting up out of it, high and wide (the boss's frame)
              const kO = 1 - kG; wrist(s, g * (1.7 + 1.7 * kH), -2.8 + 6.4 * kH, 0.4 + 0.4 * kH, w * kO); springy(s, 1.6, 0.55, w * kO);
              turn(s, g * 0.25, 1, 0.2, g * 0.6, 0.2, 0.8, 0.9, w * kO); grip(s, 'spread', w * kO);
              // on the curb: a fist's middle on it, the knuckles out over the edge, the palm down: holding on, then gripping as it hauls
              if (hold > 0) { fistAt(s, A, hold * w); springy(s, 2.4, 0.75, hold * w); }
              turn(s, g * 0.9, -0.35, 0.3, 0, -1, 0, 0.95, hold * w); curve(s, g * 0.8, 0.55, 0.2, g * 0.5, -0.6, 0.1, 1.5, 1.2, hold * w);
              grip(s, 'relax', hold * w * (1 - 0.65 * pull1)); grip(s, 'fist', hold * w * 0.65 * pull1);
              // let go: trailing under it as it shoots up, then flung wide at the top
              const kT = kRel * (1 - sstep(4.45, 4.9, t)), kW = sstep(4.45, 4.9, t) * (1 - kB);
              wrist(s, g * 1.5, -3.9, -0.4, w * kT); springy(s, 0.85, 0.42, w * kT); grip(s, 'relax', w * kT); turn(s, g * 0.1, -1, 0.1, 0, 0, -1, 0.9, w * kT);
              wrist(s, g * 4.1, 0.35, 0.8, w * kW); springy(s, 1.1, 0.5, w * kW); grip(s, 'spread', w * kW); turn(s, g * 0.9, 0.3, 0.4, 0, 0.2, 1, 0.9, w * kW);
              // the bump (as the intro's)
              boss2m(g * (1.6 - 0.98 * kBump), -1.9, 2.2, mB); fistAt(s, mB, kB * w); turn(s, -g, 0.1, 0.25, 0, -1, 0, 1, kB * w); grip(s, 'fist', kB * w); springy(s, 1.8, 0.62, kB * w);
              T.arm[s].spark = lerp(T.arm[s].spark, t < 3.6 ? 0.12 + 0.5 * hold : t < 4.7 ? 1.6 : t < 5.9 ? 0.6 : 1.5, w);
            }
            T.charge = lerp(T.charge, 0.9 * kC * (1 - kL), w);
            T.expr = t < 2.9 ? 'glare' : t < 3.62 ? 'charging' : t < 4.7 ? 'glow' : 'angry';
            T.eyeGlow = Math.max(T.eyeGlow, (sstep(3.3, 3.6, t) * (1 - sstep(4.8, 5.2, t)) + sstep(6.05, 6.2, t) * (1 - sstep(6.6, 6.9, t))) * w);
            // the slime: the pool churns and spits (more and more), bursts where the gloves break out, pours off it as it climbs and flies
            if (t < 1.7 && Math.random() < 0.25 + 0.6 * t / 1.7) { const a = Math.random() * 6.283, r = Math.random() * 3.3; mA.set(PCX + Math.cos(a) * r, POOL_Y + 0.04, PCZ + Math.sin(a) * r);
              if (Math.random() < 0.55) spawn(0, mA, 0, 1.2 + Math.random() * 1.6, 0, 0.1 + Math.random() * 0.14, 0.7, C_BUB); else spawn(1, mA, Math.cos(a) * 0.8, 2.2 + Math.random() * 2.8 * t, Math.sin(a) * 0.8, 0.09 + Math.random() * 0.1, 1, C_SLIME); }
            if (t > 1.85 && t < 4.9 && st.root.y + 1.2 > POOL_Y && Math.random() < 0.75) { const a = Math.random() * 6.283, r = 0.6 + Math.random() * 1.6;
              mA.set(st.root.x + Math.cos(a) * r, Math.max(POOL_Y + 0.1, st.root.y + 0.3 + Math.random() * 1.1), st.root.z + Math.sin(a) * r);
              spawn(1, mA, Math.cos(a) * 0.9, 0.4 + Math.random() * 0.8, Math.sin(a) * 0.9, 0.08 + Math.random() * 0.09, 1.1, C_SLIME); }
            fire(1, 'emergeChurn');
            if (t >= 1.12 && fire(2, 'emergeHands')) for (const s of SIDES) { const g = s === 'L' ? 1 : -1; boss2m(g * 2.6, 0, 0.6, mC); mC.y = POOL_Y + 0.06;
              for (let i = 0; i < 9; i++) { const a = Math.random() * 6.283; spawn(1, mC, Math.cos(a) * 2.2, 3 + Math.random() * 3.5, Math.sin(a) * 2.2, 0.1 + Math.random() * 0.1, 1.1, C_SLIME); } }
            if (t >= 1.6 && fire(4, 'grab')) { for (const s of SIDES) { const A = s === 'L' ? m.P : m.C; mC.set(A.x, FLOOR + RIM_H + 0.05, A.z); burst(mC, 4, 1.1, true, 1.8);
                for (let i = 0; i < 7; i++) { const a = Math.random() * 6.283; spawn(1, mC, Math.cos(a) * 2.4, 1.6 + Math.random() * 2.2, Math.sin(a) * 2.4, 0.09 + Math.random() * 0.08, 0.9, C_SLIME); } }
              wobble(0.7); st.sqV -= 0.8; }
            if (t >= 1.85) fire(8, 'emergeHaul');
            if (t >= 4.05 && fire(16, 'launch')) {
              st.ph = 0; st.sqV += 1.6; wobble(1.6); tentKick(0, -7, 0, 3); mC.set(PCX, POOL_Y + 0.05, PCZ); burst(mC, 10, 2.4, true, 5.5);
              for (let i = 0; i < 46; i++) { const a = Math.random() * 6.283, r = 0.6 + Math.random() * 3.2; mA.set(PCX + Math.cos(a) * r, POOL_Y + 0.08, PCZ + Math.sin(a) * r);
                spawn(i % 5 ? 1 : 0, mA, Math.cos(a) * (1.5 + Math.random() * 3.5), 4 + Math.random() * 6, Math.sin(a) * (1.5 + Math.random() * 3.5), 0.1 + Math.random() * 0.16, 1.4, i % 5 ? C_SLIME : C_BUB); }
            }
            if (t >= 6.08 && fire(32, 'emergeBump')) { mC.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); burst(mC, 9, 1.4, false, 0); wobble(1.2); st.flash = Math.max(st.flash, 0.25); arms.L.spark = arms.R.spark = 2; }
            if (t >= 7.3) fire(64, 'emergeDone');
          } },
"""

JS = r"""// ---------- (v315) the boss demo in the Sunken Keep (Season Conquest > the stage preview) ----------
// The boss comes up out of the pool in its entrance (its own camera, the first time, before the countdown), then floats over the arena
// like a jellyfish: it swims in beats of its bell, keeps near the pool on your side of it, and turns to watch you. The panel plays each of
// its moves on you (they knock you back, nothing more), Follow and Auto attack. (var, not const: the frame can come before this line runs)
var CQB = null;
function cqbInit() {
  if (CQB) return CQB;
  CQB = { boss: null, on: false, played: false, waitT: 0, cut: null, frozen: false, follow: true, auto: false, autoT: 5, defT: -1, back: 0, paused: false,
    v: new THREE.Vector3(), home: new THREE.Vector3(), tgt: new THREE.Vector3(), pool: new THREE.Vector3(0, 0, 0), kcd: 0, pl: new THREE.Vector3(), bell: new THREE.Vector3(),
    camP: new THREE.Vector3(), camL: new THREE.Vector3(), gP: new THREE.Vector3(), gL: new THREE.Vector3(), tmp: new THREE.Vector3(), shake: 0, rumble: 0, lean: 0, roll: 0, el: null,
    lock: true, lockK: 0, lp: new THREE.Vector3(), ll: new THREE.Vector3(), lpOk: false, gOff: new THREE.Vector3() };
  return CQB;
}
// the preview's match begins: the boss (made once, kept while you stay), out of sight until its entrance
function cqbStart() {
  const Q = cqbInit();
  if (!Q.boss) {
    const b = makeBoss({ scale: 1, poolY: -0.14, poolR: 4.0, poolC: Q.pool, rimR: 4.35, rimH: 0.22 }); Q.boss = b; scene.add(b.group);
    b.group.traverse(m => { if (m.isSkinnedMesh && m.castShadow) m.receiveShadow = false; });
    for (const e of ['start', 'done', 'hit', 'sweep', 'stunStart', 'defeated', 'emergeChurn', 'emergeHands', 'grab', 'emergeHaul', 'launch', 'emergeBump']) b.on(e, d => cqbEvent(e, d));
  }
  const b = Q.boss; b.group.position.copy(Q.pool); b.group.visible = false; Q.v.set(0, 0, 0); Q.home.copy(Q.pool);
  Q.on = true; Q.played = false; Q.waitT = 0; Q.cut = null; Q.defT = -1; Q.back = 0; Q.autoT = 5; Q.paused = false; Q.shake = Q.rumble = 0; Q.lockK = 0; Q.lpOk = false;
  cqbPanel();
}
// leaving the preview: the boss let go, the panel away
function cqbEnd() {
  if (!CQB) return; const Q = CQB;
  if (Q.paused && state === 'paused') state = 'play'; Q.paused = false;
  if (Q.boss) { try { Q.boss.dispose(); } catch (e) {} Q.boss = null; }
  Q.on = false; Q.cut = null; if (Q.el) Q.el.hidden = true;
}
// the reveal holds for the boss: while its pack comes (5 s at most) and through its entrance's camera (the countdown takes over at the end)
function cqbHold() { const Q = CQB; if (!Q || !Q.on || !CQP) return false; if (!Q.played) return true; return !!(Q.cut && Q.cut.first && Q.cut.t < Q.cut.len - 0.85); }
// the entrance: the boss back over the pool's middle and out of sight under it, then up; with the camera (cut) or without
function cqbEntrance(cut) {
  const Q = CQB, b = Q && Q.boss; if (!b || !b.isReady) return;
  b.group.position.copy(Q.pool); Q.v.set(0, 0, 0); Q.home.copy(Q.pool); b.group.visible = true; b.lookAt(null); b.face(null); b.hand('both', null); Q.defT = -1; Q.back = 0;
  b.play('emerge', {});
  if (cut) {
    Q.cut = { t: 0, len: 7.7, side: Math.atan2(P.x - Q.pool.x, P.z - Q.pool.z), first: cut === 'first' };
    if (!Q.cut.first && state === 'play') { state = 'paused'; Q.paused = true; if (P.charging) clearCharge(P); P.spd = 0; P.turn = 0; } // (you're held while it plays)
  }
}
// a move from the panel (or the auto attack): on you; Defeat drifts it back over the pool as it sinks
function cqbPlay(name) {
  const Q = CQB, b = Q && Q.boss; if (!b || !b.isReady || !Q.on) return;
  if (name === 'emerge') { if (state === 'play') { cqbEntrance(true); AU.whoosh(); } return; }
  if (b.move === 'defeat' || b.move === 'emerge') return;   // (down in the pool, or on its way up: wait)
  b.play(name, name === 'stunned' ? { time: 2.6 } : { x: P.x, z: P.z }); if (name === 'defeat') Q.defT = 0;
}
// the boss's events: sounds, the camera's shake, your phone's buzz; its hits knock you back (within reach of the fist or the blast)
function cqbEvent(e, d) {
  const Q = CQB; if (!Q || !Q.on) return; const near = Q.cut ? 1 : 0;
  if (e === 'emergeChurn') { AU.rumble(); Q.rumble = 1.6; }
  else if (e === 'emergeHands') { AU.splashWater(); Q.shake = Math.max(Q.shake, 0.12); }
  else if (e === 'grab') { AU.slam(); Q.shake = Math.max(Q.shake, 0.32); buzz([20, 30, 20]); }
  else if (e === 'emergeHaul') { AU.rumble(); Q.rumble = 1.8; }
  else if (e === 'launch') { AU.quake(); AU.splashWater(); AU.boost(); Q.shake = Math.max(Q.shake, 0.7); buzz([30, 30, 60]); }
  else if (e === 'emergeBump') { AU.thunder(); AU.burst(0.7); Q.shake = Math.max(Q.shake, 0.22); buzz(18); }
  else if (e === 'hit') {
    const p = d.power || 1, dd = Math.hypot(P.x - d.x, P.z - d.z); if (d.hand === 'zap') AU.thunder(); else if (p > 1.2) AU.quake(); else AU.slam();
    shake = Math.max(shake, clamp(0.5 - dd * 0.025, 0.08, 0.5) * Math.min(1.4, p)); if (!near) buzz(12);
    if (dd < (d.r || 0.8) + PR + 0.5 || (d.ring && dd < d.ring * 0.7)) cqbKnock(d.x, d.z, p);
  }
  else if (e === 'sweep') { if (Math.hypot(P.x - d.x, P.z - d.z) < (d.r || 1) + PR + 0.2) cqbKnock(d.x, d.z, 1); }
  else if (e === 'start') { if (d.move === 'sweep') AU.whoosh(); if (d.move === 'hurt') { AU.bonk(1); AU.squish(); } if (d.move === 'taunt') AU.bloop(); cqbNow(d.move); }
  else if (e === 'done') cqbNow('idle');
  else if (e === 'stunStart') AU.sink();
  else if (e === 'defeated') AU.sink();
}
// you, knocked back by a hit: a bump and a tumble (the same as a slingshot's splash, a little bigger), never a knock-out
function cqbKnock(x, z, power) {
  if (state !== 'play' || P.st !== 'play' || P.immuneT > 0 || safe(P) || CQB.kcd > 0) return; CQB.kcd = 0.9; // (once in a while: a sweep's pass is many frames)
  const dx = P.x - x, dz = P.z - z, d = Math.hypot(dx, dz), nx = d > 0.05 ? dx / d : -Math.sin(P.yaw), nz = d > 0.05 ? dz / d : -Math.cos(P.yaw), v = 6 + 2.5 * Math.min(1.6, power);
  if (P.charging) clearCharge(P); holdCharge = false; slingOff();
  P.kx = nx * v; P.kz = nz * v; P.spd *= 0.4; if (!P.air) { P.air = true; P.stroke++; P.vy = 4.2 + 1.2 * power; } else P.vy = Math.max(P.vy, 2.5);
  P.knockT = Math.max(P.knockT, 0.6); P.wob = 1; P.squash = Math.max(P.squash, 0.6); P.turn = 0; fxTumble(P, 0.8, Math.random() - 0.5, nx, nz); fxKnock(P, nx, nz, 0.7);
  emote(P, 'ouch', 0.9); AU.bonk(1); shake = Math.max(shake, 0.4); buzz([20, 25, 30]); popText('Bonked!');
}
// each frame (after the game has placed its camera, before the draw)
function cqbTick(dt, rdt) {
  const Q = CQB; if (!Q || !Q.on || !Q.boss) return;
  const b = Q.boss, inMatch = state === 'play' || state === 'intro' || state === 'reveal' || state === 'paused';
  if (!inMatch) return;
  if (Q.el) { const hid = !(state === 'play' || (state === 'paused' && Q.paused)) || !b.isReady; if (Q.el.hidden !== hid) Q.el.hidden = hid; }
  if (Q.kcd > 0) Q.kcd -= rdt;
  // the first entrance, once the reveal's sweep is over (and the pack is in: 5 s at most)
  if (!Q.played && state === 'reveal' && revealT >= REVEAL_T) {
    if (b.isReady) { Q.played = true; cqbEntrance('first'); } else if ((Q.waitT += rdt) > 5) { Q.played = true; }
  }
  if (!Q.played && state !== 'reveal' && b.isReady) { Q.played = true; cqbEntrance(false); } // (the reveal was skipped: up it comes, no camera)
  const live = Q.frozen ? 0 : Q.paused || (Q.cut && Q.cut.first) ? rdt : dt; // (its own entrance runs on while the game holds still)
  if (live > 0) { cqbSwim(live); b.update(live, { player: Q.pl.set(P.x, (P.y || 0) + 0.45, P.z), camera }); }
  // back up after a defeat, a few seconds on; the auto attack
  if (Q.defT >= 0 && live > 0) { Q.defT += live; if (Q.defT > 7.2) { Q.defT = -1; cqbEntrance(false); } }
  if (Q.auto && state === 'play' && live > 0 && !b.busy) { Q.autoT -= live; if (Q.autoT <= 0) { Q.autoT = 3.2 + Math.random() * 2.2; const r = Math.random(); cqbPlay(r < 0.34 ? 'punch' : r < 0.54 ? 'slam' : r < 0.74 ? 'sweep' : r < 0.9 ? 'zap' : 'taunt'); } }
  const cdt = Q.frozen ? 0 : rdt; if (!Q.cut || !Q.cut.first) cqbLock(cdt); if (Q.cut) cqbCam(cdt); // (an entrance played again goes back to the boss camera at its end)
}
// the swim: it floats in beats of its bell, each beat a push toward where it wants to be, then a glide the water slows; it keeps near the
// pool on your side of it, and leans into the way it goes
function cqbSwim(dt) {
  const Q = CQB, b = Q.boss, g = b.group.position, st = b._dbg ? b._dbg.st : null, mv = b.move;
  if (!b.group.visible) return;
  const anchor = mv === 'emerge' || mv === 'intro' || mv === 'defeat', attack = b.busy && !anchor;
  if (anchor) { // (the entrance and the defeat belong over the pool's middle)
    const k = 1 - Math.exp(-dt * (mv === 'defeat' ? 2.2 : 6)); g.x += (Q.pool.x - g.x) * k; g.z += (Q.pool.z - g.z) * k; Q.v.multiplyScalar(Math.exp(-dt * 4));
  } else {
    // where it wants to be: toward you from the pool's middle, held back from you, never far off the pool
    const dx = P.x - Q.pool.x, dz = P.z - Q.pool.z, d = Math.hypot(dx, dz) || 1, r = Q.follow ? clamp(d - 6.5, 0, 3.4) : 0;
    Q.tgt.set(Q.pool.x + dx / d * r, 0, Q.pool.z + dz / d * r); Q.home.lerp(Q.tgt, 1 - Math.exp(-dt / 1.1));
    const ex = Q.home.x - g.x, ez = Q.home.z - g.z, e = Math.hypot(ex, ez), ph = st ? st.ph : 0, beat = ph < 0.3 ? Math.sin(ph / 0.3 * Math.PI) : 0;
    const push = (attack ? 0 : 1) * Math.min(1, e / 2.2) * 9 * beat;
    if (e > 1e-3) { Q.v.x += ex / e * push * dt; Q.v.z += ez / e * push * dt; }
    if (!attack) { Q.v.x += Math.sin(clock * 0.37 + 1.3) * 0.25 * dt; Q.v.z += Math.cos(clock * 0.29 + 0.4) * 0.25 * dt; } // (a slow current: it never hangs dead still)
    const drag = Math.exp(-dt * (attack ? 4 : 1.35)); Q.v.x *= drag; Q.v.z *= drag;
    g.x += Q.v.x * dt; g.z += Q.v.z * dt;
    const ox = g.x - Q.pool.x, oz = g.z - Q.pool.z, gr = Math.hypot(ox, oz); if (gr > 4.2) { g.x = Q.pool.x + ox / gr * 4.2; g.z = Q.pool.z + oz / gr * 4.2; const vr = (Q.v.x * ox + Q.v.z * oz) / gr; if (vr > 0) { Q.v.x -= ox / gr * vr; Q.v.z -= oz / gr * vr; } }
    b.swim.pulse += ((attack ? 1 : 1 + 0.55 * Math.min(1, e / 3)) - b.swim.pulse) * (1 - Math.exp(-dt * 2)); // (further to go: it beats faster)
  }
  // the lean: the bell tips the way it swims (its frame: forward is where it looks)
  const yw = st ? st.yaw : 0, fw = Q.v.x * Math.sin(yw) + Q.v.z * Math.cos(yw), sd = Q.v.x * Math.cos(yw) - Q.v.z * Math.sin(yw), k = 1 - Math.exp(-dt * 4);
  Q.lean += (clamp(fw * 0.11, -0.2, 0.2) - Q.lean) * k; Q.roll += (clamp(-sd * 0.11, -0.2, 0.2) - Q.roll) * k; b.swim.lean = Q.lean; b.swim.roll = Q.roll;
}
// the entrance's camera: on your side of the pool, swung round 50 degrees (the gloves on the curb then sit one near, one far: both in the
// picture, upright too), looking down at the churning pool, then low as it hauls itself up, tipping up after it as it shoots up, and back
// to the game's camera at the end (the shake its own)
function cqbCam(rdt) {
  const Q = CQB, c = Q.cut; c.t += rdt; const t = c.t;
  if (t >= c.len || (c.first && state !== 'reveal' && state !== 'intro')) { Q.cut = null; if (Q.paused) { Q.paused = false; if (state === 'paused') state = 'play'; } return; }
  Q.boss.bellPoint(Q.bell);
  const sm = (a, b, x) => { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); };
  const port = viewW < viewH, kIn = sm(0.3, 3.6, t), kUp = sm(4.0, 4.9, t), kSet = sm(4.9, 6.4, t);
  const a = c.side + 0.87 - 0.3 * kUp, sx = Math.sin(a), sz = Math.cos(a), D0 = port ? 15.4 : 11.4, D1 = port ? 14.4 : 9.8, D2 = port ? 16.2 : 12.4;
  const d = D0 + (D1 - D0) * kIn + (D2 - D1) * kUp - (port ? 1.9 : 1.4) * kSet, h = 4.2 - 2.3 * kIn + 1.4 * kUp;
  const ly = 0.1 + 0.9 * kIn + (Math.max(Q.bell.y - 0.5, 1.0) - 1.0) * kUp;
  Q.camP.set(Q.pool.x + sx * d, h, Q.pool.z + sz * d); Q.camL.set(Q.pool.x, ly, Q.pool.z);
  if (kUp > 0) { Q.camL.x += (Q.bell.x - Q.pool.x) * kUp; Q.camL.z += (Q.bell.z - Q.pool.z) * kUp; }
  // the shake: a low rumble while it churns and hauls, a jolt on each big moment
  Q.rumble = Math.max(0, Q.rumble - rdt); Q.shake *= Math.exp(-rdt * 5.5); const sk = reduceMotion ? 0 : Q.shake + (Q.rumble > 0 ? 0.035 : 0), tt = performance.now() / 1000;
  Q.camP.x += sk * Math.sin(tt * 61) * 0.6; Q.camP.y += sk * Math.sin(tt * 53 + 1.1) * 0.45; Q.camL.y += sk * Math.sin(tt * 47 + 2.3) * 0.3;
  // from the game's camera and back to it
  const k = (c.first ? sm(0, 0.7, t) : 1) * (1 - sm(c.len - 0.85, c.len, t));
  if (Q.lockK > 0.003 && !c.first) { Q.gP.copy(camera.position); camera.getWorldDirection(Q.tmp); Q.gL.copy(camera.position).addScaledVector(Q.tmp, 10); } // (played again: from the boss camera, just placed)
  else { Q.gP.copy(camPos); Q.gL.copy(camLook); } // (the game's own camera: what it would draw, not what was drawn last)
  camera.position.lerpVectors(Q.gP, Q.camP, k); Q.tmp.lerpVectors(Q.gL, Q.camL, k); camera.up.set(0, 1, 0); camera.lookAt(Q.tmp); camera.updateMatrixWorld();
}
// the boss camera (on unless you turn it off): behind you on the line from the boss through you, looking between the two of you, so you
// and the boss are both in the picture whichever way you roll (your steering is as ever: it turns you, the camera keeps to the line).
// It eases in after Go and out when it's turned off, keeps inside the keep's wall, and keeps the game's shake
function cqbLock(rdt) {
  const Q = CQB, want = Q.lock && (state === 'play' || Q.paused) && Q.boss.group.visible ? 1 : 0;
  Q.lockK += (want - Q.lockK) * (1 - Math.exp(-rdt * 2.2)); if (Q.lockK < 0.003) { Q.lockK = want ? Q.lockK : 0; Q.lpOk = false; return; }
  const port = viewW < viewH, px = P.x - Q.pool.x, pz = P.z - Q.pool.z; Q.boss.bellPoint(Q.bell);
  let ux = P.x - Q.bell.x, uz = P.z - Q.bell.z; const ud = Math.hypot(ux, uz); if (ud > 0.05) { ux /= ud; uz /= ud; } else { ux = Math.sin(P.yaw + Math.PI); uz = Math.cos(P.yaw + Math.PI); }
  const back0 = port ? 8.6 : 7.2; let back = back0, up = port ? 3.2 : 2.6; const lim = 15.4, pu = px * ux + pz * uz, sMax = -pu + Math.sqrt(Math.max(0, pu * pu - (px * px + pz * pz) + lim * lim));
  if (sMax < back) { up -= (back - Math.max(3, sMax)) * 0.2; back = Math.max(3, sMax); } // (near the wall: closer in, and lower, looking up past you)
  const gy = gyCam, k1 = Q.lpOk ? 1 - Math.exp(-rdt * 5) : 1, k2 = Q.lpOk ? 1 - Math.exp(-rdt * 6) : 1;
  Q.tmp.set(P.x + ux * back, gy + Math.max(1.7, up), P.z + uz * back); Q.lp.lerp(Q.tmp, k1);
  // the aim, by angle: halfway between you (low) and the bell (high), so both stay in the picture; if they can't both fit, you do
  const cx = Q.lp.x, cy = Q.lp.y, cz = Q.lp.z, hP = Math.max(0.5, Math.hypot(P.x - cx, P.z - cz)), eP = Math.atan2(gy + 0.45 - cy, hP);
  const bx = Q.bell.x - cx, bz = Q.bell.z - cz, eB = Math.atan2(Q.bell.y - cy, Math.max(0.5, Math.hypot(bx, bz))), half = camera.fov * Math.PI / 360;
  const el = Math.min(eP + (eB - eP) * 0.5, eP + half * 0.8), az = Math.atan2(bx, bz);
  Q.tmp.set(cx + Math.sin(az) * Math.cos(el) * 10, cy + Math.sin(el) * 10, cz + Math.cos(az) * Math.cos(el) * 10); Q.ll.lerp(Q.tmp, k2); Q.lpOk = true;
  const k = Q.lockK * Q.lockK * (3 - 2 * Q.lockK);
  camera.position.lerpVectors(camPos, Q.lp, k); Q.tmp.lerpVectors(camLook, Q.ll, k); camera.up.set(0, 1, 0); camera.lookAt(Q.tmp);
  if (shake > 0.001 && !reduceMotion && state === 'play') camera.position.addScaledVector(Q.gOff.set(Math.random() - 0.5, Math.random() - 0.5, 0).applyQuaternion(camera.quaternion), shake * shake * 2.2); // (the game's shake, as it does it)
  camera.updateMatrixWorld();
}
// the panel: each move on a button, Follow and Auto attack, the move playing; folds to its title
function cqbPanel() {
  const Q = CQB; if (Q.el) { cqbNow('idle'); return; }
  const el = $('cqbPanel'); Q.el = el; if (!el) return;
  el.addEventListener('pointerdown', e => e.stopPropagation());
  el.addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; AU.init(); AU.ui();
    if (t.dataset.m) { cqbPlay(t.dataset.m); return; }
    if (t.id === 'cqbFollow') { Q.follow = !Q.follow; t.setAttribute('aria-pressed', Q.follow ? 'true' : 'false'); }
    else if (t.id === 'cqbAuto') { Q.auto = !Q.auto; Q.autoT = 1.2; t.setAttribute('aria-pressed', Q.auto ? 'true' : 'false'); }
    else if (t.id === 'cqbLock') { Q.lock = !Q.lock; t.setAttribute('aria-pressed', Q.lock ? 'true' : 'false'); }
    else if (t.id === 'cqbFold') { const f = el.classList.toggle('fold'); t.setAttribute('aria-expanded', f ? 'false' : 'true'); } });
  cqbNow('idle');
}
const CQB_NAMES = { idle: 'Floating', emerge: 'Entrance', intro: 'Entrance', punch: 'Punch', slam: 'Slam', sweep: 'Sweep', zap: 'Zap', hurt: 'Hurt', stunned: 'Stunned', taunt: 'Taunt', defeat: 'Defeat' };
function cqbNow(m) {
  const Q = CQB; if (!Q || !Q.el) return; const n = $('cqbNow'); if (n) n.textContent = CQB_NAMES[m] || m;
  for (const x of Q.el.querySelectorAll('[data-m]')) x.classList.toggle('on', x.dataset.m === m);
}
"""

CSS = r"""
/* (v315) the boss demo's panel: upright a strip under the top bar (it scrolls sideways), sideways a small panel at the left */
.cqb{position:absolute;z-index:9;left:calc(env(safe-area-inset-left) + 8px);right:calc(env(safe-area-inset-right) + 8px);top:calc(env(safe-area-inset-top) + 92px);display:flex;align-items:center;gap:6px;padding:5px;border-radius:13px;background:rgba(16,10,34,.72);border:1.5px solid rgba(255,255,255,.12);box-shadow:0 4px 14px rgba(0,0,0,.3);color:#FFF8EA;font:800 12px/1 var(--font-ui);-webkit-user-select:none;user-select:none}
.cqb .cqbh{flex:none;display:flex;align-items:center;gap:6px;padding-left:4px}
.cqb .cqbh b{font:400 13px/1 var(--font-display);letter-spacing:.02em;color:#F2C14E}
.cqb .cqbh span{display:none}
.cqb .cqbh button{flex:none;width:26px;height:26px;border:0;border-radius:8px;background:rgba(255,255,255,.1);color:#FFF8EA;font:800 14px/1 var(--font-ui);cursor:pointer}
.cqb .cqbs{flex:1;min-width:0;display:flex;align-items:center;gap:5px;overflow-x:auto;overscroll-behavior:contain;scrollbar-width:none;touch-action:pan-x;-webkit-mask-image:linear-gradient(90deg,#000 86%,transparent);mask-image:linear-gradient(90deg,#000 86%,transparent);padding-right:18px}
.cqb .cqbs::-webkit-scrollbar{display:none}
.cqb .cqbs button{flex:none;height:30px;padding:0 11px;border:1.5px solid rgba(255,255,255,.16);border-radius:9px;background:rgba(255,255,255,.08);color:#FFF8EA;font:800 12px/1 var(--font-ui);white-space:nowrap;cursor:pointer}
.cqb .cqbs button[data-m="emerge"]{background:rgba(242,193,78,.18);border-color:rgba(242,193,78,.55);color:#FFE7A6}
.cqb .cqbs button.on{border-color:#F2C14E;background:rgba(242,193,78,.32);color:#FFF8EA}
.cqb .cqbs .cqbtg[aria-pressed="true"]{border-color:#9BE15D;background:rgba(155,225,93,.2);color:#E9FFD6}
.cqb .cqbs button:active{transform:scale(.96)}
.cqb .cqbsep{flex:none;width:1px;height:20px;background:rgba(255,255,255,.18)}
.cqb.fold{right:auto}.cqb.fold .cqbs{display:none}
@media (max-height:520px) and (min-aspect-ratio:1/1){
  .cqb{right:auto;top:calc(env(safe-area-inset-top) + 58px);width:206px;display:block;padding:7px}
  .cqb .cqbh{padding:0 0 6px 2px}.cqb .cqbh span{display:block;flex:1;min-width:0;color:#C9C1DC;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .cqb .cqbs{display:grid;grid-template-columns:1fr 1fr;overflow:visible;-webkit-mask-image:none;mask-image:none;padding:0}
  .cqb .cqbs button{height:27px;padding:0 6px}
  .cqb .cqbs button[data-m="emerge"],.cqb .cqbsep{grid-column:1 / -1}
  .cqb .cqbsep{width:auto;height:1px;margin:2px 0}
  .cqb.fold{width:auto}.cqb.fold .cqbh{padding:0}.cqb.fold .cqbh span{display:none}
}
"""

HTML = '<div class="cqb" id="cqbPanel" hidden><div class="cqbh"><b>Boss</b><span id="cqbNow">Floating</span><button id="cqbFold" type="button" aria-expanded="true" aria-label="Fold the boss panel">–</button></div>' \
    '<div class="cqbs"><button type="button" data-m="emerge">Entrance</button><button type="button" data-m="punch">Punch</button><button type="button" data-m="slam">Slam</button>' \
    '<button type="button" data-m="sweep">Sweep</button><button type="button" data-m="zap">Zap</button><button type="button" data-m="hurt">Hurt</button>' \
    '<button type="button" data-m="stunned">Stunned</button><button type="button" data-m="taunt">Taunt</button><button type="button" data-m="defeat">Defeat</button>' \
    '<i class="cqbsep" aria-hidden="true"></i><button type="button" class="cqbtg" id="cqbLock" aria-pressed="true">Boss cam</button><button type="button" class="cqbtg" id="cqbFollow" aria-pressed="true">Follow</button>' \
    '<button type="button" class="cqbtg" id="cqbAuto" aria-pressed="false">Auto attack</button></div></div>'

def apply(s):
    for a, b in RT: s = rep(s, a, b)
    s = rep(s, "        // ---- defeat: a last flinch", EMERGE + "        // ---- defeat: a last flinch")
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, JS + a)
    # the preview's match: the boss with it; the reveal waits for its entrance; each frame its tick; leaving lets it go
    s = rep(s, "function beginMatch() {\n  clearShot();", "function beginMatch() {\n  if (CQP) cqbStart(); // (v315: the boss demo)\n  clearShot();")
    s = rep(s, "if (revealT >= REVEAL_T) { state = 'intro'; introT = 0;", "if (revealT >= REVEAL_T && !cqbHold()) { state = 'intro'; introT = 0;")
    s = rep(s, "  visuals(dt, rdt); flushTrail();", "  visuals(dt, rdt); cqbTick(dt, rdt); flushTrail();")
    s = rep(s, "  if (CQP) { mode = CQP.prevMode; CQP = null; } // (v309: back from the stage preview)", "  if (CQP) { mode = CQP.prevMode; CQP = null; cqbEnd(); } // (v309: back from the stage preview; v315: the boss let go)")
    # the words: a boss demo now
    s = rep(s, '<b>Season Conquest</b><small>Sunken Keep, stage only</small>', '<b>Season Conquest</b><small>Sunken Keep, boss demo</small>')
    s = rep(s, '<span class="evbar"><i>Stage preview</i></span>', '<span class="evbar"><i>Boss demo</i></span>')
    s = rep(s, '<i class="evsoon">Stage preview</i>', '<i class="evsoon">Boss demo</i>')
    s = rep(s, "$('rvSub').textContent = CQP ? 'Season Conquest \\u00b7 stage preview' :", "$('rvSub').textContent = CQP ? 'Season Conquest \\u00b7 boss demo' :")
    s = rep(s, "$('pauseClock').textContent = CQP ? 'Stage preview' :", "$('pauseClock').textContent = CQP ? 'Boss demo' :")
    # the panel
    s = rep(s, '<div class="hud off" id="hud">', HTML + '<div class="hud off" id="hud">')
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
