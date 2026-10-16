"""v319: the Jellyfish Boss's entrance finished like a boss fight's should: once it's out of the pool it charges up, looks at you, and
roars; the fight starts with the screen shaking, a screen effect, and then its health bar.

- The charge (after it has shot up out of the pool and settled): it brings its fists together in front of its bell and presses them,
  trembling. Sparks of energy stream in to its fists from all round, the gloves crackle more and more, its eyes glow, its bell tightens
  and beats fast. The camera closes in. Then the energy breaks in a burst of sparks: a flash, a ring, the picture splitting a moment.
- The stare: it lowers its fists, turns to face you and leans in, eyes narrowed. The camera cuts to over your shoulder, low, looking up
  into its face, and creeps closer. The water goes quiet: one deep heartbeat and a dark swell. Its eyes catch the light once.
- The roar: it rears back, then throws itself forward, arms flung wide, bell flared, tentacles whipping, slime and bubbles flying. The
  screen shakes hard and the camera is knocked back. The screen effect: a flash, speed lines rushing in toward it, a ring racing out,
  the edges flushed with its pink and (on the hi graphics setting) the picture splitting into colour and smearing toward it. A shock
  ring races out over the floor. Then its health bar drops in: the name stamps in, the bar fills with its paint, a shine runs along
  it, and it flashes full. Then the countdown, as before.
- It all plays the same when the entrance plays again from the panel, and when it comes back up after a defeat.
- The fight's own moments: a hit that knocks you is a short freeze with a jolt of the colour split (hi); the boss hurt, a short freeze;
  a strike or a mine blowing near you, a jolt of the colour split.
- New sounds (Ludo): the power-up, the stare's heartbeat, the roar's impact boom and the bar filling.
- The screen effect is drawn only while it plays (one full-screen pass over the frame, both graphics settings; the colour split and the
  smear are part of the hi setting's last pass). With reduced motion on, there's no shake, speed lines, smear or split: a softer flash."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

# ---- the runtime: the entrance runs on to 11 s (the charge, the pop, the stare, the roar)
RT = [
    ("        emerge: { len: 7.4,", "        emerge: { len: 11.0,"),
    ("            const w = 1 - sstep(6.7, 7.4, t);\n            const kH = sstep(1.05, 1.4, t),",
     "            const w = 1 - sstep(10.35, 11.0, t);\n            const kH = sstep(1.05, 1.4, t),"),
    ("kDown = sstep(4.6, 5.8, t), kB = sstep(5.75, 6.05, t), kBump = sstep(6.05, 6.17, t);",
     "kDown = sstep(4.6, 5.8, t), kB = sstep(5.75, 6.05, t) * (1 - sstep(7.5, 7.62, t)), kBump = sstep(6.05, 6.3, t);\n"
     "            // (v319) the charge (fists pressed together, gathering), the fling as it breaks, the stare (low, leaning in), rearing back, the roar\n"
     "            const kQ = sstep(6.2, 7.45, t), kF = sstep(7.5, 7.62, t) * (1 - sstep(7.9, 8.45, t)), kS = sstep(7.9, 8.45, t) * (1 - sstep(9.02, 9.22, t)),\n"
     "              kA = sstep(9.0, 9.22, t) * (1 - sstep(9.28, 9.36, t)), kR = sstep(9.28, 9.38, t) * (1 - sstep(10.1, 10.85, t)), trem = 0.5 * Math.sin(t * 47) + 0.5 * Math.sin(t * 71.3);"),
    ("              boss2m(g * (1.6 - 0.98 * kBump), -1.9, 2.2, mB); fistAt(s, mB, kB * w); turn(s, -g, 0.1, 0.25, 0, -1, 0, 1, kB * w); grip(s, 'fist', kB * w); springy(s, 1.8, 0.62, kB * w);\n"
     "              T.arm[s].spark = lerp(T.arm[s].spark, t < 3.6 ? 0.12 + 0.5 * hold : t < 4.7 ? 1.6 : t < 5.9 ? 0.6 : 1.5, w);",
     "              // (v319) the fists come together and press, raised a little, trembling as it gathers itself\n"
     "              boss2m(g * (1.6 - 0.98 * kBump) + g * 0.035 * trem * kQ, -1.9 + 0.75 * kBump, 2.2 - 0.25 * kBump, mB); fistAt(s, mB, kB * w); turn(s, -g, 0.1, 0.25, 0, -1, 0, 1, kB * w); grip(s, 'fist', kB * w); springy(s, 1.8 + 0.5 * kQ, 0.62, kB * w);\n"
     "              // flung wide as the charge breaks; low and wide, fists ready, for the stare; drawn back and up; flung wide and high for the roar\n"
     "              wrist(s, g * 4.2, 0.6, 0.9, w * kF); grip(s, 'spread', w * kF); springy(s, 1.0, 0.45, w * kF);\n"
     "              wrist(s, g * 2.5, -1.35, 1.55, w * kS); turn(s, g * 0.3, 0.6, 0.4, 0, 1, 0, 0.9, w * kS); grip(s, 'fist', w * kS); springy(s, 1.5, 0.6, w * kS);\n"
     "              wrist(s, g * 2.2, 1.8, -1.1, w * kA); grip(s, 'fist', w * kA); springy(s, 1.6, 0.55, w * kA);\n"
     "              wrist(s, g * (4.3 + 0.12 * trem), 1.35, 0.75, w * kR); grip(s, 'spread', w * kR); springy(s, 0.95, 0.42, w * kR);\n"
     "              T.arm[s].spark = lerp(T.arm[s].spark, t < 3.6 ? 0.12 + 0.5 * hold : t < 4.7 ? 1.6 : t < 6.0 ? 0.6 : t < 7.62 ? 0.7 + 1.9 * kQ : t < 7.95 ? 2.4 : t < 9.3 ? 0.45 : 0.3 + 1.7 * (1 - sstep(10.0, 10.8, t)), w);"),
    ("            T.charge = lerp(T.charge, 0.9 * kC * (1 - kL), w);\n"
     "            T.expr = t < 2.9 ? 'glare' : t < 3.62 ? 'charging' : t < 4.7 ? 'glow' : 'angry';\n"
     "            T.eyeGlow = Math.max(T.eyeGlow, (sstep(3.3, 3.6, t) * (1 - sstep(4.8, 5.2, t)) + sstep(6.05, 6.2, t) * (1 - sstep(6.6, 6.9, t))) * w);",
     "            T.charge = lerp(T.charge, Math.max(0.9 * kC * (1 - kL), kQ * kB), w);\n"
     "            T.expr = t < 2.9 ? 'glare' : t < 3.62 ? 'charging' : t < 4.7 ? 'glow' : t < 6.0 ? 'angry' : t < 7.55 ? 'charging' : t < 7.9 ? 'glow' : t < 9.25 ? 'glare' : 'angry';\n"
     "            T.eyeGlow = Math.max(T.eyeGlow, (sstep(3.3, 3.6, t) * (1 - sstep(4.8, 5.2, t)) + 0.85 * kQ * kB + sstep(7.5, 7.56, t) * (1 - sstep(7.7, 8.0, t)) + sstep(8.4, 8.5, t) * (1 - sstep(8.6, 8.95, t)) + sstep(9.3, 9.36, t) * (1 - sstep(10.0, 10.6, t))) * w);\n"
     "            // (v319) the body: tight and trembling, beating fast as it gathers itself; leaning in, slow beats, for the stare (turned to face you\n"
     "            // from then on); rearing back, stretched; then thrown forward and flared, shaking, its tentacles whipping, for the roar\n"
     "            if (t > 5.9) { const q = kB * w;\n"
     "              T.squash = lerp(T.squash, 1 - 0.09 * kQ + 0.025 * trem * kQ, q); T.lean = lerp(T.lean, -0.07 * kQ, q); T.roll = lerp(T.roll, 0.035 * trem * kQ, q);\n"
     "              T.pulse = lerp(T.pulse, 1 + 1.6 * kQ, q); T.pulseAmp = lerp(T.pulseAmp, 1 - 0.55 * kQ, q); T.tentW = lerp(T.tentW, 1 - 0.6 * kQ, q);\n"
     "              T.lean = lerp(T.lean, 0.15, kS * w); T.squash = lerp(T.squash, 1, kS * w); T.pulse = lerp(T.pulse, 0.5, kS * w); T.pulseAmp = lerp(T.pulseAmp, 0.8, kS * w); T.tentW = lerp(T.tentW, 0.7, kS * w);\n"
     "              T.lean = lerp(T.lean, -0.26, kA * w); T.squash = lerp(T.squash, 1.14, kA * w);\n"
     "              T.lean = lerp(T.lean, 0.2 + 0.04 * trem, kR * w); T.squash = lerp(T.squash, 0.88 + 0.03 * trem, kR * w); T.roll = lerp(T.roll, 0.05 * trem, kR * w); T.pulseAmp = lerp(T.pulseAmp, 1.7, kR * w); T.tentW = lerp(T.tentW, 2.3, kR * w);\n"
     "              if (t > 7.75) T.yaw = null; else T.yaw = m.yaw + 0.5 * sstep(5.9, 6.5, t); // (turned a little away as it gathers itself, then round to you)\n"
     "              if (t > 6.05 && t < 7.55) T.lookOv = mE.set(st.root.x, st.root.y + 6, st.root.z); }"),
    ("            if (t >= 6.08 && fire(32, 'emergeBump')) { mC.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); burst(mC, 9, 1.4, false, 0); wobble(1.2); st.flash = Math.max(st.flash, 0.25); arms.L.spark = arms.R.spark = 2; }\n"
     "            if (t >= 7.3) fire(64, 'emergeDone');",
     "            // (v319) the charge: sparks of energy streaming in to its fists from all round; the break (emergeBump); the stare; the roar\n"
     "            if (t >= 6.2) fire(128, 'emergeCharge');\n"
     "            if (t > 6.2 && t < 7.5 && Math.random() < 0.35 + 0.6 * kQ) { mC.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); const a = Math.random() * 6.283, e = (Math.random() - 0.3) * 1.6, r = 2.2 + Math.random() * 1.4, sp = r * (1.5 + kQ);\n"
     "              mA.set(mC.x + Math.cos(a) * Math.cos(e) * r, mC.y + Math.sin(e) * r, mC.z + Math.sin(a) * Math.cos(e) * r); spawn(3, mA, (mC.x - mA.x) / r * sp, (mC.y - mA.y) / r * sp, (mC.z - mA.z) / r * sp, 0.06 + Math.random() * 0.07, 0.42 + Math.random() * 0.15, C_SPARK); }\n"
     "            if (t >= 7.52 && fire(32, 'emergeBump')) { mC.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); burst(mC, 14, 2.2, false, 0); wobble(1.5); st.flash = Math.max(st.flash, 0.4); st.sqV += 1.1; arms.L.spark = arms.R.spark = 2.4; }\n"
     "            if (t >= 7.75) fire(256, 'emergeStare');\n"
     "            if (t >= 9.33 && fire(512, 'emergeRoar')) { wobble(2.0); st.flash = Math.max(st.flash, 0.5); st.sqV -= 1.3; tentKick(0, 5, 0, 3.5); arms.L.spark = arms.R.spark = 2.6;\n"
     "              mC.set(st.root.x, st.root.y - 0.4, st.root.z); burst(mC, 16, 2.6, false, 0);\n"
     "              for (let i = 0; i < 30; i++) { const a = Math.random() * 6.283, e = Math.random() * 0.9, sp = 3 + Math.random() * 4; mA.set(st.root.x + Math.cos(a) * 1.2, st.root.y - 0.6 + Math.random() * 0.8, st.root.z + Math.sin(a) * 1.2);\n"
     "                spawn(i % 3 ? 1 : 0, mA, Math.cos(a) * Math.cos(e) * sp, Math.sin(e) * sp + 1.5, Math.sin(a) * Math.cos(e) * sp, 0.08 + Math.random() * 0.12, 1.2, i % 3 ? C_SLIME : C_BUB); } }\n"
     "            if (t >= 10.9) fire(64, 'emergeDone');"),
]

JS = r"""// ---------- (v319) the entrance's end (the charge, the stare, the roar) and the screen's big moments ----------
CQB_SFX.push('b_power', 'b_stare', 'b_impact', 'b_fill');
// the entrance's events: the power-up and a rumble as it gathers itself; the break; the stare (the water hushed, a heartbeat); the roar
// (the impact and its roar, the shake, the screen effect, a shock ring over the floor; the bar comes in after it)
function cqiEv(e, d) {
  const Q = CQB, b = Q.boss;
  if (e === 'start' && d.move === 'emerge') Q.hush = 0;
  else if (e === 'emergeCharge') { cqbSfx('b_power', { v: 0.95 }) || AU.power(); Q.rumble = Math.max(Q.rumble, 1.35); buzz(10); }
  else if (e === 'emergeBump') { if (b) { b.bellPoint(Q.bell); cqfGo(2, Q.bell); } }
  else if (e === 'emergeStare') { Q.hush = 1; cqbSfx('b_stare', { v: 0.9 }); }
  else if (e === 'emergeRoar') { Q.hush = 0; cqbSfx('b_impact', { v: 1, duck: [0.6, 1.2] }) || AU.quake(); cqbSfx('b_roar', { v: 1, d: 0.03 });
    Q.shake = Math.max(Q.shake, Q.cut ? 1.0 : 0.6); Q.rumble = Math.max(Q.rumble, 0.7); if (!Q.cut) shake = Math.max(shake, 0.45); buzz([40, 30, 70]);
    if (b) { b.bellPoint(Q.bell); cqfGo(1, Q.bell); } cqxRing(Q.pool.x, Q.pool.z, 2, 0.95, 16); }
  // its defeat: its last flinch in slow motion, a flash and the screen effect
  else if (e === 'start' && d.move === 'defeat' && state === 'play') { if (b) { b.bellPoint(Q.bell); cqfGo(4, Q.bell); } slow = Math.max(slow, 0.7); shake = Math.max(shake, 0.4); buzz([30, 30, 60]); Q.winT = 0.75; }
}
// "Boss defeated!" stamped over the middle with a win sting, then away
function cqiWin() { const el = $('cqWin'); if (!el) return; el.hidden = false; el.classList.remove('go'); void el.offsetWidth; el.classList.add('go'); AU.sting('win'); CQB.winOut = 2.7; }
// A camera on the line out behind you (u: from the boss through you), as it nears the keep's wall or passes it: up over the wall (higher
// at one of its pillars), high enough to see you over its top, and no further back than that lets it (nor out among the tall pillars and
// arches beyond). The height back; CQB.wb the distance back
function cqiWall(px, pz, ux, uz, back, up, hMax) {
  const pu = px * ux + pz * uz, p2 = px * px + pz * pz, at = r => -pu + Math.sqrt(Math.max(0, pu * pu - p2 + r * r));
  back = Math.min(back, at(18.9));
  const s0 = at(17.42), dg = ((Math.atan2(pz + uz * s0, px + ux * s0) * 57.29578 - 15) % 30 + 30) % 30, pil = clamp((3.6 - Math.min(dg, 30 - dg)) / 1.6, 0, 1);
  const sE = Math.max(0.1, at(17.42 - 0.17 * pil)), hE = 2.6 + 1.3 * pil, yP = 0.6, bMax = sE * (hMax - yP) / (hE - yP);
  if (back > bMax) back = Math.max(0.6, bMax);
  CQB.wb = back; return Math.max(up, yP + (hE - yP) * back / sE);
}
// the entrance's camera: for the charge, round in front of it, low, looking up at it and its fists, creeping in; then, for the stare, over your shoulder (on the line from it through
// you), low, looking up into its face and creeping closer, kept inside the keep's wall or up over it; the roar knocks it back
function cqiCam(c, t, port) {
  const Q = CQB, sm = (a, b, x) => { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); };
  if (t < 7.72) { const k = sm(5.8, 6.55, t); if (k <= 0) return;
    const fa = c.side + (port ? 0.42 : 0.55), dist = (port ? 8.4 : 6.6) * (1 - 0.12 * sm(6.55, 7.6, t));
    Q.tmp.set(Q.bell.x + Math.sin(fa) * dist, Math.max(1.2, Q.bell.y - 1.3), Q.bell.z + Math.cos(fa) * dist); Q.camP.lerp(Q.tmp, k);
    Q.tmp.set(Q.bell.x, Q.bell.y - 0.55, Q.bell.z); Q.camL.lerp(Q.tmp, k); return; }
  let ux = P.x - Q.bell.x, uz = P.z - Q.bell.z; const ud = Math.hypot(ux, uz); if (ud > 0.05) { ux /= ud; uz /= ud; } else { ux = Math.sin(c.side); uz = Math.cos(c.side); }
  const dolly = sm(7.72, 9.3, t), kick = t > 9.3 ? Math.min(1, (t - 9.3) / 0.06) * Math.exp(-Math.max(0, t - 9.36) * 3.2) : 0;
  let back = (port ? 4.6 : 3.7) - 0.8 * dolly + 1.2 * kick, up = (port ? 1.45 : 1.15) + 0.12 * dolly + 0.25 * kick;
  const px = P.x - Q.pool.x, pz = P.z - Q.pool.z, lim = 16.2, pu = px * ux + pz * uz, sMax = -pu + Math.sqrt(Math.max(0, pu * pu - (px * px + pz * pz) + lim * lim));
  if (sMax < back) { up += (back - Math.max(1.6, sMax)) * 0.3; back = Math.max(1.6, sMax); }
  up = cqiWall(px, pz, ux, uz, back, up, port ? 6.4 : 5.4); back = Q.wb;
  const sd = port ? 0.55 : 0.9; // (a little to one side: you in a corner of the picture, it in the middle)
  Q.camP.set(P.x + ux * back - uz * sd, Math.max(0, P.y || 0) + up, P.z + uz * back + ux * sd); Q.camL.set(Q.bell.x, Q.bell.y - 0.25, Q.bell.z);
}
// The screen's big moments (1 the roar, 2 the charge breaking, 3 a hit or a blast on you, 4 its defeat): a flash, speed lines rushing
// in toward it, a ring racing out, the edges flushed with its pink; on hi, the picture splits into colour and smears toward it too (the
// last pass's CQF_FX). Drawn over the frame only while one plays
var CQF = { t: -1, kind: 0, wp: new THREE.Vector3(), c: new THREE.Vector2(0.5, 0.5), q: new THREE.Vector3(), ov: null, on: false };
function cqfGo(kind, wp) { const F = CQF; if (F.t >= 0 && F.kind === 1 && kind > 2 && F.t < 0.8) return; F.t = 0; F.kind = kind; if (wp) F.wp.copy(wp); else F.wp.set(NaN, 0, 0); }
function cqfTick(rdt) { const F = CQF, Q = CQB;
  if (Q && Q.winT > 0 && (Q.winT -= rdt) <= 0) cqiWin(); if (Q && Q.winOut > 0 && (Q.winOut -= rdt) <= 0) { const w = $('cqWin'); if (w) { w.hidden = true; w.classList.remove('go'); } }
  if (F.t < 0) return; F.t += rdt; if (F.t > (F.kind === 1 ? 1.3 : F.kind === 4 ? 1.1 : F.kind === 2 ? 0.6 : 0.42)) F.t = -1; }
function cqfPre() {
  const F = CQF; F.on = F.t >= 0 && !!CQB && CQB.on; if (!F.on) { CQF_FX.x = CQF_FX.y = 0; return; }
  if (!isNaN(F.wp.x)) { F.q.copy(F.wp).project(camera); F.c.set(clamp(F.q.x * 0.5 + 0.5, 0.1, 0.9), clamp(F.q.y * 0.5 + 0.5, 0.15, 0.9)); } else F.c.set(0.5, 0.5);
  const t = F.t, k = F.kind, rm = reduceMotion, sm = (a, b, x) => { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); };
  const flash = (k === 1 ? 0.6 * Math.exp(-t * 8) : k === 4 ? 0.85 * Math.exp(-t * 5) : k === 2 ? 0.4 * Math.exp(-t * 12) : 0) * (rm ? 0.5 : 1);
  const lines = rm ? 0 : k === 1 ? sm(0, 0.05, t) * (1 - sm(0.5, 1.15, t)) : k === 4 ? 0.6 * sm(0, 0.05, t) * (1 - sm(0.3, 0.9, t)) : 0;
  const rT = k === 1 || k === 4 ? 0.75 : 0.45, ringR = (k === 1 || k === 4 ? 1.6 : 0.6) * (1 - Math.pow(1 - Math.min(1, t / rT), 3)) + 0.03, ringA = k === 3 ? 0 : Math.max(0, 1 - t / rT) * (rm ? 0.5 : 1);
  const vig = k === 1 ? 0.6 * Math.exp(-t * 2.2) : k === 4 ? 0.6 * Math.exp(-t * 2) : k === 3 ? 0.35 * Math.exp(-t * 8) : 0;
  CQF_FX.set(rm ? 0 : k === 1 ? Math.exp(-t * 3) : k === 4 ? 0.8 * Math.exp(-t * 3) : k === 2 ? 0.55 * Math.exp(-t * 7) : 0.6 * Math.exp(-t * 9), rm ? 0 : k === 1 ? Math.exp(-t * 4.2) : k === 4 ? 0.7 * Math.exp(-t * 3.5) : k === 2 ? 0.25 * Math.exp(-t * 9) : 0, F.c.x, F.c.y);
  if (!F.ov) { const sc = new THREE.Scene(), cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), tri = new THREE.BufferGeometry(); tri.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
    const m = new THREE.ShaderMaterial({ uniforms: { uA: { value: new THREE.Vector4() }, uB: { value: new THREE.Vector4() }, uV: { value: new THREE.Vector2() } }, transparent: true, depthTest: false, depthWrite: false,
      blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      vertexShader: 'varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: `uniform vec4 uA, uB; uniform vec2 uV; varying vec2 vUv;
        float h1(float n){ return fract(sin(n * 127.1) * 43758.5453); }
        void main(){ vec2 d = vUv - uB.xy; d.x *= uB.z; float r = length(d), an = atan(d.y, d.x); vec3 col = vec3(0.0); float a = 0.0;
          if (uA.y > 0.003) { float u = (an + 3.14159265) / 6.2831853 * 64.0, id = floor(u), f = fract(u), fr = floor(uB.w * 20.0), rnd = h1(id + fr * 3.17), wd = 0.12 + 0.24 * h1(id * 1.7),
              r0 = 0.24 + 0.36 * h1(id * 2.3 + fr), lk = smoothstep(wd, 0.0, abs(f - 0.5)) * step(0.45, rnd) * smoothstep(r0, r0 + 0.2, r) * uA.y;
            col += vec3(1.0, 0.97, 1.0) * lk; a = max(a, lk * 0.9); }
          if (uA.w > 0.003) { float e = (r - uA.z) / 0.035, rg = exp(-e * e) * uA.w; col += vec3(1.0, 0.75, 0.95) * rg; a = max(a, rg * 0.55); }
          if (uV.x > 0.003) { float v = smoothstep(0.45, 1.25, length((vUv - 0.5) * vec2(uB.z, 1.0)) * 1.1) * uV.x; col = col * (1.0 - v) + vec3(0.85, 0.15, 0.6) * v; a = max(a, v); }
          if (uA.x > 0.003) { float f = uA.x * (1.0 - 0.35 * smoothstep(0.0, 1.2, r)); col = col * (1.0 - f) + vec3(1.0, 0.92, 0.98) * f; a = a + f * (1.0 - a); }
          gl_FragColor = vec4(col, a); }` });
    const q = new THREE.Mesh(tri, m); q.frustumCulled = false; sc.add(q); F.ov = { sc, cam, m }; }
  const U = F.ov.m.uniforms; U.uA.value.set(flash, lines, ringR, ringA); U.uB.value.set(F.c.x, F.c.y, viewW / Math.max(1, viewH), clock); U.uV.value.set(vig, 0);
  F.draw = flash > 0.003 || lines > 0.003 || ringA > 0.003 || vig > 0.003;
}
function cqfDraw() { const F = CQF; if (!F.on || !F.draw || !F.ov) return; const ac = renderer.autoClear; renderer.autoClear = false; renderer.setRenderTarget(null); renderer.render(F.ov.sc, F.ov.cam); renderer.autoClear = ac; }
"""

HTML = '<div class="cqwin" id="cqWin" hidden role="status"><b>Boss defeated!</b></div>'

CSS = r"""
/* (v319) the health bar's entrance after the roar: the name stamps in, a shine runs along the bar as it fills, a flash when it's full */
.cqbar.in .cqbn b{animation:cqbname .5s cubic-bezier(.2,1.6,.35,1) .12s both}
@keyframes cqbname{from{opacity:0;transform:scale(1.9) rotate(-4deg)}}
.cqbar.in .cqbn svg{animation:cqbicon .5s cubic-bezier(.2,1.6,.35,1) .04s both}
@keyframes cqbicon{from{opacity:0;transform:scale(0) rotate(-40deg)}}
.cqbt::after{content:'';position:absolute;inset:-3px;border-radius:99px;pointer-events:none;opacity:0}
.cqbar.in .cqbt::after{background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,.85) 50%,transparent 70%);background-size:300% 100%;animation:cqbsheen 1.25s ease-out .3s both}
@keyframes cqbsheen{0%{opacity:1;background-position:100% 0}80%{opacity:1}100%{opacity:0;background-position:0 0}}
.cqbt::before{content:'';position:absolute;inset:-5px;border-radius:99px;pointer-events:none;box-shadow:0 0 16px 5px rgba(255,110,215,.9);opacity:0}
.cqbar.full .cqbt::before{animation:cqbfull .7s ease-out}
@keyframes cqbfull{20%{opacity:1}100%{opacity:0}}
/* low on health: a red glow round the tube pulses (a layer of its own fading in and out, nothing repainted; the hurt jolt still plays over it) */
.cqbar::after{content:'';position:absolute;left:0;right:0;bottom:0;height:22px;border-radius:99px;box-shadow:0 0 14px 4px rgba(255,70,110,.8);opacity:0;pointer-events:none}
.cqbar.low:not(.hit)::after{animation:cqblow .9s ease-in-out infinite alternate}
@keyframes cqblow{from{opacity:.08}to{opacity:1}}
.cqbar.low .cqbn{color:#FFC2D6}
@media (max-height:520px) and (min-aspect-ratio:1/1){.cqbar::after{height:24px}}
/* the paint's flow along the bar and the last life's pulse: moved and faded (each a layer of its own), not repainted every frame */
.cqbf{overflow:hidden}
.cqbf::before{inset:0 0 0 -44px;border-radius:0;animation-name:cqbflow2}
@keyframes cqbflow2{to{transform:translateX(44px)}}
.cqlife .cqlr::after{content:'';position:absolute;inset:-3px;border-radius:50%;box-shadow:0 0 14px 2px rgba(255,74,90,.85);opacity:0;pointer-events:none}
#cqLife.low .cqlr{animation:none}
.cqlife.low .cqlr::after{animation:cqlglow .8s ease-in-out infinite alternate}
@keyframes cqlglow{from{opacity:.1}to{opacity:1}}
/* its defeat: a stamp over the middle */
.cqwin{position:absolute;z-index:9;left:50%;top:36%;transform:translate(-50%,-50%);pointer-events:none;white-space:nowrap}
.cqwin b{display:block;padding:14px 26px 12px;border-radius:18px;background:#F04FC0;border:4px solid #171320;box-shadow:0 6px 0 #171320,inset 0 -6px 0 rgba(0,0,0,.16);color:#FFF8EA;font:400 clamp(28px,8.5vw,50px)/1 var(--font-display);letter-spacing:.02em;text-transform:uppercase;text-shadow:0 3px 0 #171320}
.cqwin.go{animation:cqwin 2.6s cubic-bezier(.2,1.5,.35,1) both}
@keyframes cqwin{0%{opacity:0;transform:translate(-50%,-50%) scale(2.2) rotate(-9deg)}12%{opacity:1;transform:translate(-50%,-50%) scale(.94) rotate(-3deg)}18%{transform:translate(-50%,-50%) scale(1.04) rotate(-3deg)}24%,84%{opacity:1;transform:translate(-50%,-50%) scale(1) rotate(-3deg)}100%{opacity:0;transform:translate(-50%,-62%) scale(.96) rotate(-3deg)}}
@media (prefers-reduced-motion:reduce){.cqbar.in .cqbn b,.cqbar.in .cqbn svg,.cqbar.in .cqbt::after,.cqbar.full .cqbt::before,.cqbar.low:not(.hit)::after,.cqbf::before,.cqlife.low .cqlr::after{animation:none}.cqbar.low::after,.cqlife.low .cqlr::after{opacity:.7}.cqwin.go{animation:cqwinrm 2.6s both}@keyframes cqwinrm{0%,100%{opacity:0}10%,85%{opacity:1}}}
"""


def apply(s):
    for a, b in RT: s = rep(s, a, b)
    # the demo: the new events heard, their camera, the hush, the screen effect each frame, the cut long enough for it all
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, JS + a)
    s = rep(s, "'emergeHaul', 'launch', 'emergeBump']) b.on(", "'emergeHaul', 'launch', 'emergeBump', 'emergeCharge', 'emergeStare', 'emergeRoar', 'emergeDone']) b.on(")
    s = rep(s, "cqbBarEv(e, d); cqxEv(e, d); cqyEv(e, d);", "cqbBarEv(e, d); cqxEv(e, d); cqyEv(e, d); cqiEv(e, d);")
    s = rep(s, "  else if (e === 'emergeBump') { if (!cqbSfx('b_bump', { duck: [0.35, 0.5] })) { AU.thunder(); AU.burst(0.7); } cqbSfx('b_roar', { d: 0.4 }); Q.shake",
               "  else if (e === 'emergeBump') { if (!cqbSfx('b_bump', { duck: [0.35, 0.5] })) { AU.thunder(); AU.burst(0.7); } Q.shake") # (its roar comes with the roar now)
    s = rep(s, "    Q.cut = { t: 0, len: 7.7, side:", "    Q.cut = { t: 0, len: 11.3, side:")
    s = rep(s, "  if (kUp > 0) { Q.camL.x += (Q.bell.x - Q.pool.x) * kUp; Q.camL.z += (Q.bell.z - Q.pool.z) * kUp; }\n",
               "  if (kUp > 0) { Q.camL.x += (Q.bell.x - Q.pool.x) * kUp; Q.camL.z += (Q.bell.z - Q.pool.z) * kUp; }\n  cqiCam(c, t, port); // (v319: the charge, the stare, the roar)\n")
    s = rep(s, "function cqbTick(dt, rdt) {\n", "function cqbTick(dt, rdt) {\n  cqfTick(rdt); // (v319: the screen's big moments)\n")
    s = rep(s, "  const lv = state === 'paused' && !Q.paused ? 0.5 : 1, e = Math.max(0,", "  const lv = (state === 'paused' && !Q.paused ? 0.5 : 1) * (Q.hush ? 0.22 : 1), e = Math.max(0,") # (v319: hushed for the stare)
    # the bar: in after the roar (not as it shoots up): stamped, filled with a shine and its sound, a flash when full
    s = rep(s, "  if (e === 'start' && d.move === 'emerge') { B.vis = false; B.hp = 0; B.gh = 0; B.fillT = -1; B.defIn = 0; }\n"
               "  else if (e === 'launch' || (e === 'emergeDone' && !B.vis)) { B.vis = true; B.hp = 1; B.gh = 0; B.fillT = 0; B.el.classList.remove('in'); void B.el.offsetWidth; B.el.classList.add('in'); }",
               "  if (e === 'start' && d.move === 'emerge') { B.vis = false; B.hp = 0; B.gh = 0; B.fillT = -1; B.defIn = 0; B.inT = 0; }\n"
               "  else if (e === 'emergeRoar') B.inT = 0.42; // (v319: after the roar's shake and screen effect)\n"
               "  else if (e === 'emergeDone' && !B.vis) cqbBarIn();")
    s = rep(s, "function cqbBarTick(rdt) {\n", "function cqbBarIn() { const B = CQB.bar; if (!B) return; B.inT = 0; B.vis = true; B.hp = 1; B.gh = 0; B.fillT = 0; B.el.classList.remove('in', 'full'); void B.el.offsetWidth; B.el.classList.add('in'); cqbSfx('b_fill', { v: 0.8, d: 0.25 }); }\n"
               "function cqbBarTick(rdt) {\n")
    s = rep(s, "B.vis = false; B.hp = 0; B.gh = 0; B.fillT = -1; B.defIn = 0; B.hold = 0; } // (a new demo: no bar until the boss is up)\n",
               "B.vis = false; B.hp = 0; B.gh = 0; B.fillT = -1; B.defIn = 0; B.hold = 0; B.inT = 0; } // (a new demo: no bar until the boss is up)\n"
               "  if (B.inT > 0 && (B.inT -= rdt) <= 0) cqbBarIn(); // (v319)\n")
    s = rep(s, "f = B.hp * (1 - Math.pow(1 - u, 3)); if (u >= 1) B.fillT = -1; }",
               "f = B.hp * (1 - Math.pow(1 - u, 3)); if (u >= 1) { B.fillT = -1; B.el.classList.remove('full'); void B.el.offsetWidth; B.el.classList.add('full'); } }")
    a = "@media (prefers-reduced-motion:reduce){.cqbar.in,.cqbf::before,.cqbe,.cqbd i,.cqbar.hit .cqbt{animation:none}}\n"
    s = rep(s, a, a + CSS.strip() + "\n")
    s = rep(s, '<div class="hud off" id="hud">', HTML + '<div class="hud off" id="hud">')
    s = rep(s, "B.el.classList.toggle('empty', f < 0.01);", "B.el.classList.toggle('empty', f < 0.01); B.el.classList.toggle('low', B.fillT < 0 && B.hp > 0.01 && B.hp < 0.3);")
    s = rep(s, "cqbSfxOff(); cqxEnd(); cqyEnd();", "cqbSfxOff(); cqxEnd(); cqyEnd(); { const w = $('cqWin'); if (w) w.hidden = true; } CQF.t = -1; CQB.winT = CQB.winOut = 0;")
    # the frame: the screen effect's numbers before the draw (the hi setting's last pass reads them), its pass over the frame after
    s = rep(s, "// ---------- Graphics mode post: the frame renders into an antialiased target,",
               "var CQF_FX = new THREE.Vector4(0, 0, 0.5, 0.5); // (v319: the screen's big moments in the last pass: x the colour split, y the smear toward zw)\n"
               "// ---------- Graphics mode post: the frame renders into an antialiased target,")
    s = rep(s, "  const cu = { tScene: { value: null },", "  const cu = { uFx: { value: CQF_FX }, tScene: { value: null },")
    s = rep(s, "    uniform sampler2D tEdge; uniform vec4 uEdgeK, uEdgeV; uniform vec3 uEdgeC, uHitC, uVigC;\n",
               "    uniform sampler2D tEdge; uniform vec4 uEdgeK, uEdgeV; uniform vec3 uEdgeC, uHitC, uVigC; uniform vec4 uFx;\n")
    s = rep(s, "      vec3 c = fin3(texture2D(tScene, uv).rgb);\n",
               "      vec3 c;\n"
               "      if (uFx.x + uFx.y > 0.004) { // (v319) a big moment: the picture splits into colour and smears toward its middle\n"
               "        vec2 dv = uv - uFx.zw; float dl = length(dv); vec3 acc = vec3(0.0); float ws = 0.0;\n"
               "        for (int i = 0; i < 7; i++) { float f = float(i) / 6.0, w = 1.0 - 0.7 * f; vec2 u2 = uFx.zw + dv * (1.0 - uFx.y * 0.09 * f), co = dv * uFx.x * (0.010 + 0.016 * dl);\n"
               "          acc += vec3(fin3(texture2D(tScene, u2 + co).rgb).r, fin3(texture2D(tScene, u2).rgb).g, fin3(texture2D(tScene, u2 - co).rgb).b) * w; ws += w; }\n"
               "        c = acc / ws;\n"
               "      } else c = fin3(texture2D(tScene, uv).rgb);\n")
    s = rep(s, "  if (post) { post.dofK.copy(state !== 'menu' ? DOF_PLAY : lookOpen ? DOF_LOOK : DOF_MENU); return post.render(); }\n"
               "  renderer.render(scene, camera);\n"
               "  if (EDGE.on || heatK > 0.02) edgeOverlay();\n",
               "  cqfPre(); // (v319: the screen's big moments)\n"
               "  if (post) { post.dofK.copy(state !== 'menu' ? DOF_PLAY : lookOpen ? DOF_LOOK : DOF_MENU); post.render(); cqfDraw(); return; }\n"
               "  renderer.render(scene, camera);\n"
               "  if (EDGE.on || heatK > 0.02) edgeOverlay();\n"
               "  cqfDraw();\n")
    # the fight's own moments: knocked by it (a short freeze, a jolt); it hurt (a short freeze); a strike or a mine blowing near you
    s = rep(s, "  emote(P, 'ouch', 0.9); AU.bonk(1); shake = Math.max(shake, 0.4); buzz([20, 25, 30]); popText('Bonked!'); cqlHit(); // (v318: a life gone)",
               "  emote(P, 'ouch', 0.9); AU.bonk(1); shake = Math.max(shake, 0.4); buzz([20, 25, 30]); popText('Bonked!'); cqlHit(); // (v318: a life gone)\n"
               "  hold = Math.max(hold, 0.06); fovKick = Math.max(fovKick, 6); cqfGo(3); // (v319: a short freeze, a kick, a jolt of the colour split)")
    s = rep(s, "  else if (e === 'start') { if (d.move === 'sweep') cqbSfx('b_sweep', { d: 0.4 }) || AU.whoosh();",
               "  else if (e === 'start') { if (d.move === 'hurt' && state === 'play') hold = Math.max(hold, 0.07); if (d.move === 'sweep') cqbSfx('b_sweep', { d: 0.4 }) || AU.whoosh();")
    s = rep(s, "  const dd = Math.hypot(P.x - x, P.z - z); shake = Math.max(shake, clamp(0.5 - dd * 0.025, 0.1, 0.45)); if (dd < 6) buzz([20, 20, 30]);",
               "  const dd = Math.hypot(P.x - x, P.z - z); shake = Math.max(shake, clamp(0.5 - dd * 0.025, 0.1, 0.45)); if (dd < 6) buzz([20, 20, 30]); if (dd < 4.5) cqfGo(3); // (v319)")
    # the boss camera by the wall: with you pressed against the keep's wall there's no room behind you, and the camera ended up outside
    # it, low, looking at stone. Now, as it nears the wall, it rises (over the kelp and coral along it), and past it, it goes up over the
    # wall, high enough to see you over its top, still on the line from the boss through you, so the two of you stay in the picture
    s = rep(s, "  const gy = gyCam, k1 = Q.lpOk ? 1 - Math.exp(-rdt * 5) : 1, k2 = Q.lpOk ? 1 - Math.exp(-rdt * 6) : 1;\n"
               "  Q.tmp.set(P.x + ux * back, gy + Math.max(1.7, up), P.z + uz * back); Q.lp.lerp(Q.tmp, k1);",
               "  const gy = gyCam, k1 = Q.lpOk ? 1 - Math.exp(-rdt * 5) : 1, k2 = Q.lpOk ? 1 - Math.exp(-rdt * 6) : 1;\n"
               "  { const rc = Math.hypot(px + ux * back, pz + uz * back); up += clamp(rc - 15.4, 0, 2) * 0.9; up = cqiWall(px, pz, ux, uz, back, up, port ? 7.6 : 6.4); back = Q.wb; } // (v319: by the wall, up over it)\n"
               "  Q.tmp.set(P.x + ux * back, gy + Math.max(1.7, up), P.z + uz * back); Q.lp.lerp(Q.tmp, k1);")
    return s
