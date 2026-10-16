"""v318: three more boss moves for the demo, after the user's second set of reference pictures (rings rippling out over the floor, a
golden ring under you and a beam of light striking down into an explosion of puffs and rays, round bombs), and a LIFE counter.

- Ripples: the Jellyfish Boss floats back over the pool, rises, then flops down into it three times, slapping the slime with its
  gloves. Each dunk sends a glowing ring of water racing out over the floor from the pool to the wall, a low wall of light on it. On
  the ground when one passes, you're knocked outward; jump and it goes under you.
- Strikes: it raises a glove to the sky, crackling, and calls down three strikes on you, one after another, pumping its fist at each.
  A golden rune ring appears under you and follows you, running ahead of you till it's where you'll be when the beam lands (you never
  stop moving), then locks and blinks; steer off your line. A pink beam strikes down there and it explodes: a
  flash, a cartoon fireball (white-hot, orange, a red rim, cooling into smoke), light rays and a golden shock ring. Inside it,
  you're knocked.
- Sea mines: it reaches back with both gloves and flings three spiked sea mines; they arc over and land on your way (one where you'll
  be when it lands, one either side of your way a little further on). Their red blast rings mark where they'll land from the throw
  and fill as the fuse burns; down, they blink red, beep faster, and blow the same way. Inside the blast, you're knocked; come near
  one (most of the way into its circle, once it's been down a beat) and it blows at once.
- LIFE: three, in a round gauge under the sound button. Each of the boss's hits takes one, then you blink for 1.6 s and nothing
  knocks you (so one attack can't take all three); at none you're knocked out (Splatted by Jellyfish Boss) and come back with three.
- The panel: Ripples, Strikes and Sea mines after Shock wave (sideways the panel goes to three columns to fit); Auto attack picks them.
- The sounds (Ludo, finished by tools/boss_sfx_build.py): the ring of water, the lock-on, the beam, the mine's blast, its beep, the
  throw. Drawn in a few instanced draws (the ripples, the beams, the rays, the fire, the flashes, the mines and their lights, the
  target), made on first use, let go with the demo."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

MOVES = r"""        // ---- (v318) ripple: back over the pool, it rises, then flops down into it three times, slapping the slime with its gloves; each
        // dunk sends a ring of water racing out over the floor (ripple: the demo draws the rings)
        ripple: { len: 3.6,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); },
          run(m, t) {
            const w = wIO(t, 3.6, 0.25, 0.9), kU = sstep(0, 0.6, t), kE = sstep(2.5, 3.2, t);
            let d = 0; for (let k = 0; k < 3; k++) { const u = t - (0.85 + k * 0.65) + 0.2; if (u > 0 && u < 0.55) { const a = u < 0.2 ? eIO(u / 0.2) : 1 - eIO((u - 0.2) / 0.35); d = Math.max(d, a * (1 - 0.18 * k)); } }
            T.yaw = m.yaw; off(0, (1.3 * kU - 3.0 * d) * (1 - kE), 0, w); T.clipY = POOL_Y; T.clipBand = 0.3;
            T.squash = lerp(T.squash, 1 + 0.15 * kU * (1 - kE) - 0.28 * d, w); T.lean = lerp(T.lean, -0.12 * kU * (1 - kE) + 0.1 * d, w); T.tentW = lerp(T.tentW, 1.6, w * (1 - kE));
            for (const s of SIDES) { const g = s === 'L' ? 1 : -1;
              wrist(s, g * (2.6 + 0.4 * d), 1.4 - 2.6 * d, 0.6, w); turn(s, g * 0.5, -0.2 - 0.6 * d, 0.4, 0, -1, 0.2, 0.9, w); grip(s, d > 0.3 ? 'fist' : 'spread', w); springy(s, 1.6, 0.6, w);
              T.arm[s].spark = lerp(T.arm[s].spark, 0.4 + 0.8 * d, w); }
            T.expr = t < 0.7 ? 'charging' : t < 2.6 ? 'angry' : 'glare';
            fire(1, 'windup');
            for (let k = 0; k < 3; k++) if (t >= 0.85 + k * 0.65 && !(m.fired & (2 << k))) { m.fired |= 2 << k;
              mC.set(PCX, POOL_Y + 0.08, PCZ); burst(mC, 6, 2.0, true, 4.6 - k * 0.5); wobble(1.0 - 0.2 * k); st.sqV -= 1.0;
              for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283, r = 1.5 + Math.random() * 2.3, sp = 1.5 + Math.random() * 2.5; mA.set(PCX + Math.cos(a) * r, POOL_Y + 0.08, PCZ + Math.sin(a) * r); spawn(1, mA, Math.cos(a) * sp, 3 + Math.random() * 4, Math.sin(a) * sp, 0.1 + Math.random() * 0.12, 1.2, C_SLIME); }
              mC.set(PCX, FLOOR, PCZ); hitW.copy(mC).applyMatrix4(G); emit('ripple', evOf({ i: k, x: hitW.x, z: hitW.z })); }
            if (t >= 2.6) fire(16, 'recover');
          } },
        // ---- (v318) strike: it raises a glove to the sky, crackling, and calls down three strikes on you, pumping its fist at each
        // (strikeGo: the demo marks you, follows you, locks, and brings each one down)
        strike: { len: 4.7,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); },
          run(m, t) {
            const w = wIO(t, 4.7, 0.25, 0.9), kU = sstep(0, 0.5, t), kE = sstep(4.0, 4.6, t);
            let pump = 0; for (let k = 0; k < 3; k++) { const u = (t - (1.6 + k * 1.15)) / 0.35; if (u > 0 && u < 1) pump = Math.max(pump, Math.sin(u * Math.PI)); }
            T.yaw = yawTo(st.look); off(0, 0.6 * kU * (1 - kE) - 0.3 * pump, -0.2 * kU, w);
            T.lean = lerp(T.lean, -0.18 * kU * (1 - kE) + 0.15 * pump, w); T.squash = lerp(T.squash, 1 + 0.08 * kU - 0.12 * pump, w);
            wrist('R', -1.0, 3.0 - 0.9 * pump, 0.4, w * (1 - kE)); turn('R', 0, 1, 0, 0, 0, 1, 0.95, w * (1 - kE)); grip('R', pump > 0.3 ? 'fist' : 'point', w); springy('R', 1.5, 0.6, w);
            wrist('L', 2.2, -0.6 + 0.4 * pump, 1.6, w); grip('L', 'spread', w); turn('L', -0.6, 0.2, 1, 0, 1, 0, 0.9, w);
            T.arm.R.spark = lerp(T.arm.R.spark, 1.6 * kU * (1 - kE) + 0.6 * pump, w); T.charge = lerp(T.charge, 0.7 * kU * (1 - kE), w);
            T.expr = t < 0.5 ? 'charging' : t < 4.0 ? 'glow' : 'smug'; T.eyeGlow = Math.max(T.eyeGlow, kU * (1 - kE) * w);
            fire(1, 'windup'); if (t >= 0.35) fire(2, 'strikeGo'); if (t >= 4.0) fire(4, 'recover');
          } },
        // ---- (v318) mines: it reaches back with both gloves and flings sea mines at you (minesThrow: from where the gloves let go; the
        // demo flies them, sets them down and sets them off)
        mines: { len: 3.0,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); },
          run(m, t) {
            const w = wIO(t, 3.0, 0.2, 0.9), kB = sstep(0, 0.7, t) * (1 - sstep(0.78, 0.92, t)), kT = sstep(0.78, 0.92, t), kE = sstep(1.6, 2.4, t);
            T.yaw = m.yaw; off(0, 0.3 * kB, -0.6 * kB + 0.5 * kT * (1 - kE), w);
            T.lean = lerp(T.lean, -0.25 * kB + 0.3 * kT * (1 - kE), w); T.squash = lerp(T.squash, 1 + 0.1 * kB - 0.1 * kT * (1 - kE), w);
            for (const s of SIDES) { const g = s === 'L' ? 1 : -1;
              wrist(s, g * 1.9, 1.6 + 0.6 * kB, -1.6 * kB + 2.2 * kT * (1 - kE), w); turn(s, g * 0.3, 0.6, -0.4 * kB + 0.8 * kT, 0, 1, 0.3, 0.9, w); grip(s, kT > 0.5 ? 'spread' : 'fist', w); springy(s, 1.5, 0.6, w);
              T.arm[s].spark = lerp(T.arm[s].spark, 0.4, w); }
            T.expr = t < 0.78 ? 'glare' : t < 1.6 ? 'angry' : 'smug';
            fire(1, 'windup');
            if (t >= 0.86 && !(m.fired & 2)) { m.fired |= 2; mA.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); hitW.copy(mA).applyMatrix4(G); emit('minesThrow', evOf({ x: hitW.x, y: hitW.y, z: hitW.z })); }
            if (t >= 1.6) fire(4, 'recover');
          } },
"""

JS = r"""// ---------- (v318) more of the boss's attacks on the arena floor. Ripples: rings of water race out from the pool as it dunks itself
// (jump them). Strikes: a golden ring follows you, locks, and a pink beam strikes down there and explodes (three in a row). Sea mines:
// spiked mines it throws land round you, blink, and blow. And your LIFE in the demo: three; each of its hits takes one; at none you're
// knocked out by the Jellyfish Boss and come back with three
var CQY = null;
CQB_SFX.push('b_wave', 'b_lock', 'b_beam', 'b_boom', 'b_beep', 'b_toss');
var CQY_NF = 48, CQY_NL = 4;
function cqyInit() {
  if (CQY) return CQY; const X = cqxInit();
  const grp = new THREE.Group(), add = (o, ro) => { o.frustumCulled = false; o.renderOrder = ro; if (o.isInstancedMesh) o.instanceMatrix.setUsage(THREE.DynamicDrawUsage); o.visible = false; grp.add(o); return o; };
  const iattr = (g, n, k, name) => { const a = new THREE.InstancedBufferAttribute(new Float32Array(n * k), k); a.setUsage(THREE.DynamicDrawUsage); g.setAttribute(name, a); return a; };
  const AD = { transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }, TM = '\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n';
  // the ripples: a band on the floor and a low wall of light at its edge, round the pool's middle at radius R (an instance each)
  const SEG = 128, rp = [], rk = [], ri = [];
  for (let k = 0; k <= SEG; k++) { const a = k / SEG * 6.2832; for (let j = 0; j < 4; j++) { rp.push(0, 0, 0); rk.push(a, j); } }
  for (let k = 0; k < SEG; k++) { const b = k * 4, n = b + 4; ri.push(b, n, b + 1, b + 1, n, n + 1, b + 2, n + 2, b + 3, b + 3, n + 2, n + 3); }
  const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.Float32BufferAttribute(rp, 3)); rg.setAttribute('aS', new THREE.Float32BufferAttribute(rk, 2)); rg.setIndex(ri);
  const rA = iattr(rg, 4, 4, 'aW');
  const rm = new THREE.ShaderMaterial(Object.assign({ side: THREE.DoubleSide,
    vertexShader: `attribute vec2 aS; attribute vec4 aW; varying vec2 vQ; varying float vA;
      void main(){ float a = aS.x, j = aS.y, R = aW.x, W = aW.y, H = aW.z; vec3 p; if (j < 1.5) { float r = R + (j < 0.5 ? -W : W); p = vec3(cos(a) * r, 0.05, sin(a) * r); vQ = vec2(0.0, j < 0.5 ? -1.0 : 1.0); }
        else { p = vec3(cos(a) * R, j < 2.5 ? 0.03 : H, sin(a) * R); vQ = vec2(1.0, j < 2.5 ? 0.0 : 1.0); }
        vA = aW.w; gl_Position = projectionMatrix * viewMatrix * modelMatrix * instanceMatrix * vec4(p, 1.0); }`,
    fragmentShader: `varying vec2 vQ; varying float vA;
      void main(){ if (vA <= 0.0) discard; float a; vec3 c;
        if (vQ.x < 0.5) { float u = abs(vQ.y); a = (1.0 - u * u) * 0.55 + exp(-u * u / 0.02) * 0.6; c = mix(vec3(0.3, 0.75, 1.0), vec3(0.9, 1.0, 1.0), exp(-u * u / 0.03)); }
        else { float h = vQ.y; a = (1.0 - h) * (0.55 + 0.45 * (1.0 - h)) * 0.8 + exp(-pow((h - 0.82) / 0.06, 2.0)) * 0.5; c = mix(vec3(0.35, 0.8, 1.0), vec3(0.92, 1.0, 1.0), h); }
        gl_FragColor = vec4(c * a * vA, 1.0);` + TM + `}` }, AD));
  // the beams: a column of light from the sky, a bright core, its edges and its top fading, streaks running down it
  const bg = new THREE.CylinderGeometry(1, 1, 1, 24, 1, true).translate(0, 0.5, 0), bA = iattr(bg, 3, 1, 'aB');
  const bm = new THREE.ShaderMaterial(Object.assign({ uniforms: { uTime: { value: 0 } },
    vertexShader: `attribute float aB; varying vec3 vN, vV; varying float vY, vA; void main(){ vec4 w = modelMatrix * instanceMatrix * vec4(position, 1.0); vN = normalize(mat3(modelMatrix * instanceMatrix) * normal); vV = cameraPosition - w.xyz; vY = position.y; vA = aB; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform float uTime; varying vec3 vN, vV; varying float vY, vA;
      void main(){ if (vA <= 0.0) discard; float f = pow(abs(dot(normalize(vN), normalize(vV))), 1.4), s = 0.75 + 0.25 * sin(vY * 70.0 + uTime * 40.0), a = f * s * (1.0 - smoothstep(0.3, 0.95, vY)) * vA * 1.6;
        gl_FragColor = vec4(mix(vec3(1.0, 0.3, 0.85), vec3(1.0, 0.94, 1.0), pow(f, 3.0)) * a, 1.0);` + TM + `}` }, AD));
  // the rays: thin crossed blades of light flying out of a blast
  const yg = mergeGeos([new THREE.PlaneGeometry(1, 1).translate(0, 0.5, 0), new THREE.PlaneGeometry(1, 1).translate(0, 0.5, 0).rotateY(Math.PI / 2)], true), yA = iattr(yg, 24, 1, 'aY');
  const ym = new THREE.ShaderMaterial(Object.assign({ side: THREE.DoubleSide,
    vertexShader: `attribute float aY; varying vec2 vUv; varying float vA; void main(){ vUv = uv; vA = aY; gl_Position = projectionMatrix * viewMatrix * modelMatrix * instanceMatrix * vec4(position, 1.0); }`,
    fragmentShader: `varying vec2 vUv; varying float vA; void main(){ if (vA <= 0.0) discard; float x = abs(vUv.x - 0.5) * 2.0, a = (1.0 - x * x) * (1.0 - vUv.y) * (0.4 + vUv.y * 1.6) * vA;
      gl_FragColor = vec4(mix(vec3(1.0, 0.75, 0.35), vec3(1.0, 1.0, 0.92), 1.0 - x) * a, 1.0);` + TM + `}` }, AD));
  // the fire: lumpy cartoon fireballs, white-hot in the middle, then orange, then a red rim; cooling into a dusky smoke as they rise
  const fg = new THREE.IcosahedronGeometry(1, 2), fA = iattr(fg, CQY_NF, 2, 'aH');
  const fm = new THREE.ShaderMaterial({
    vertexShader: `attribute vec2 aH; varying vec3 vN, vV; varying vec2 vH; void main(){ vec3 p = position; float l = sin(p.x * 4.0 + aH.y * 6.3) * sin(p.y * 3.5 + aH.y * 2.1) * sin(p.z * 4.0 + aH.y * 4.7); p *= 1.0 + 0.16 * l;
      vec4 w = modelMatrix * instanceMatrix * vec4(p, 1.0); vN = normalize(mat3(modelMatrix * instanceMatrix) * normal); vV = cameraPosition - w.xyz; vH = aH; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `varying vec3 vN, vV; varying vec2 vH;
      void main(){ vec3 n = normalize(vN); float h = vH.x, up = n.y * 0.5 + 0.5, k = (1.0 - abs(dot(n, normalize(vV)))) * 0.95 + (1.0 - h) * 1.1 - up * 0.18;
        vec3 c = mix(vec3(1.0, 0.96, 0.6) * 1.45, vec3(1.0, 0.32, 0.012) * 1.3, smoothstep(0.3, 0.38, k)); c = mix(c, vec3(0.88, 0.05, 0.01), smoothstep(0.68, 0.76, k));
        c = mix(c, vec3(0.12, 0.07, 0.17) * (0.7 + 0.7 * up), smoothstep(0.5, 0.12, h));
        gl_FragColor = vec4(c, 1.0);` + TM + `}` });
  // the flash: a round burst of light facing you, there and gone
  const xg = new THREE.PlaneGeometry(1, 1), xA = iattr(xg, CQY_NL, 1, 'aX');
  const xm = new THREE.ShaderMaterial(Object.assign({
    vertexShader: `attribute float aX; varying vec2 vUv; varying float vA; void main(){ vUv = uv; vA = aX; gl_Position = projectionMatrix * viewMatrix * modelMatrix * instanceMatrix * vec4(position, 1.0); }`,
    fragmentShader: `varying vec2 vUv; varying float vA; void main(){ if (vA <= 0.0) discard; float r = length(vUv - 0.5) * 2.0; if (r > 1.0) discard; float a = (exp(-r * r * 9.0) * 1.3 + (1.0 - r) * 0.35) * vA;
      gl_FragColor = vec4(mix(vec3(1.0, 0.45, 0.08), vec3(1.0, 0.95, 0.75), exp(-r * r * 6.0)) * a, 1.0);` + TM + `}` }, AD));
  // the sea mines: a dark iron ball, spikes all round it, and a light on top that blinks red
  const ico = new THREE.IcosahedronGeometry(1, 0).getAttribute('position'), parts = [new THREE.SphereGeometry(0.5, 18, 12)], seen = new Set(), up = new THREE.Vector3(0, 1, 0);
  for (let i = 0; i < ico.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(ico, i).normalize(), key = v.toArray().map(n => n.toFixed(2)).join(); if (seen.has(key) || v.y > 0.9) continue; seen.add(key);
    parts.push(new THREE.ConeGeometry(0.09, 0.3, 6).translate(0, 0.6, 0).applyQuaternion(new THREE.Quaternion().setFromUnitVectors(up, v))); }
  const mg = mergeGeos(parts, false), mmat = new THREE.MeshStandardMaterial({ color: 0x2C3240, metalness: 0.55, roughness: 0.32, emissive: 0x0A0C14 });
  const lg = new THREE.SphereGeometry(0.13, 10, 8), lmat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
  // the target: the golden rune ring under you
  const tmat = new THREE.ShaderMaterial(Object.assign({ uniforms: { uMap: { value: X.tex }, uA: { value: 0 }, uF: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform sampler2D uMap; uniform float uA, uF; varying vec2 vUv; void main(){ float a = texture2D(uMap, vUv).a * uA; if (a < 0.003) discard; gl_FragColor = vec4(mix(vec3(1.0, 0.72, 0.18), vec3(1.0, 0.97, 0.8), uF) * a * (0.9 + 0.8 * uF), 1.0);` + TM + `}` }, AD));
  const Y = CQY = { grp, rA, rm, bA, bm, yA, ym, fA, fm, xA, xm, mmat, lmat, tmat, geos: [rg, bg, yg, fg, xg, mg, lg],
    fire: add(new THREE.InstancedMesh(fg, fm, CQY_NF), 4), flash: add(new THREE.InstancedMesh(xg, xm, CQY_NL), 10),
    rip: add(new THREE.InstancedMesh(rg, rm, 4), 6), beam: add(new THREE.InstancedMesh(bg, bm, 3), 9), rays: add(new THREE.InstancedMesh(yg, ym, 24), 9), mines: add(new THREE.InstancedMesh(mg, mmat, 6), 3), lights: add(new THREE.InstancedMesh(lg, lmat, 6), 3),
    tgt: add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2).rotateX(-Math.PI / 2), tmat), 8),
    W: [], B: [], Rr: [], Mn: [], F: [], L: [], T: null, q: [], t: 0, M: new THREE.Matrix4(), Qn: new THREE.Quaternion(), v: new THREE.Vector3(), s: new THREE.Vector3(), d: new THREE.Vector3(), c: new THREE.Color(), up };
  for (let i = 0; i < 4; i++) Y.W.push({ on: false }); for (let i = 0; i < 3; i++) Y.B.push({ on: false }); for (let i = 0; i < 24; i++) Y.Rr.push({ on: false }); for (let i = 0; i < CQY_NF; i++) Y.F.push({ on: false }); for (let i = 0; i < CQY_NL; i++) Y.L.push({ on: false }); for (let i = 0; i < 6; i++) { Y.Mn.push({ on: false }); Y.lights.setColorAt(i, Y.c.set(0x330000)); }
  scene.add(grp); return Y;
}
function cqyEnd() { const Y = CQY; if (!Y) return; CQY = null; scene.remove(Y.grp); for (const g of Y.geos) g.dispose(); Y.tgt.geometry.dispose();
  for (const m of [Y.rm, Y.bm, Y.ym, Y.fm, Y.xm, Y.mmat, Y.lmat, Y.tmat]) m.dispose(); for (const o of [Y.rip, Y.beam, Y.rays, Y.fire, Y.flash, Y.mines, Y.lights]) if (o.dispose) o.dispose(); }
function cqyClear() { const Y = CQY; if (!Y) return; Y.q.length = 0; Y.T = null; for (const a of [Y.W, Y.B, Y.Rr, Y.Mn, Y.F, Y.L]) for (const o of a) o.on = false; }
// a blast (a strike, a mine): a flash, a fireball (a hot core and puffs thrown out), light rays, a golden shock ring; you knocked if you're within r
function cqyFire(x, y, z, vx, vy, vz, s, L) { const Y = cqyInit(), o = cqxSlot(Y.F); Object.assign(o, { on: true, x, y, z, vx, vy, vz, s, L, t0: Y.t, seed: Math.random() * 6.283 }); }
function cqyBlast(x, z, r, power) {
  const Y = cqyInit(), k = r / 1.8, fl = cqxSlot(Y.L); Object.assign(fl, { on: true, x, z, t0: Y.t, s: 2.6 * k });
  for (let i = 0; i < 13; i++) { const a = Math.random() * 6.283, c = i < 4, q = c ? 0.2 : 0.5 * k, sp = c ? 0.5 : (1.3 + Math.random() * 1.6) * k;
    cqyFire(x + Math.cos(a) * q, (c ? 0.45 : 0.3) + Math.random() * 0.4, z + Math.sin(a) * q, Math.cos(a) * sp, (c ? 2.0 : 0.9) + Math.random() * 1.5, Math.sin(a) * sp, ((c ? 0.55 : 0.3) + Math.random() * 0.18) * Math.sqrt(k), 0.8 + Math.random() * 0.45); }
  for (let i = 0; i < 7; i++) { const o = cqxSlot(Y.Rr), a = Math.random() * 6.283, el = 0.45 + Math.random() * 0.75; Object.assign(o, { on: true, x, y: 0.3, z, dx: Math.cos(a) * Math.cos(el), dy: Math.sin(el), dz: Math.sin(a) * Math.cos(el), L: 2.4 + Math.random() * 1.8, t0: Y.t }); }
  cqxRing(x, z, 2, 0.5, r * 1.4);
  cqbSfx('b_boom', { at: [x, z], rate: 0.94 + Math.random() * 0.12 }) || AU.quake();
  const dd = Math.hypot(P.x - x, P.z - z); shake = Math.max(shake, clamp(0.5 - dd * 0.025, 0.1, 0.45)); if (dd < 6) buzz([20, 20, 30]);
  if (dd < r + PR * 0.5) cqbKnock(x, z, power);
}
// where you'll be in a moment, kept on the floor between the pool's curb and the wall
function cqyAhead(k) { const Q = CQB, X = cqxInit(); let x = P.x + X.pv.x * k, z = P.z + X.pv.z * k; const ox = x - Q.pool.x, oz = z - Q.pool.z, r = Math.hypot(ox, oz) || 1, rc = clamp(r, CQY_IN, CQY_OUT); return { x: Q.pool.x + ox / r * rc, z: Q.pool.z + oz / r * rc }; }
// the strikes: a golden ring finds you and follows you, running further ahead of you as it goes (0.7 s), till it's where you'll be
// when the beam lands (you never stop, so it aims where you're heading); then it locks and blinks (0.55 s): steer off it; the beam
// comes down; then the next
var CQY_FOLLOW = 0.7, CQY_BEAM = 1.25, CQY_NEAR = 1.3; // (a mine goes off when you come this near)
var CQY_IN = 5.6, CQY_OUT = 16.8; // (where the strikes and mines can come down: the keep's floor, from the curb to the wall)
function cqyStrike(n) {
  const Y = cqyInit(), o = { x: P.x, z: P.z, t0: Y.t, n, ring: cqxRing(P.x, P.z, 3, CQY_BEAM, 1.5) }; Y.T = o;
  cqbSfx('b_lock', { v: 0.8, rate: 1 + (3 - n) * 0.05 });
}
function cqyEv(e, d) {
  const Q = CQB;
  if (e === 'start' && d.move === 'emerge') cqyClear();
  else if (e === 'windup' && (d.move === 'ripple' || d.move === 'mines')) cqbSfx('b_windup', { v: 0.85 });
  else if (e === 'windup' && d.move === 'strike') cqbSfx('b_charge', { v: 0.9 });
  else if (e === 'ripple') { const Y = cqyInit(), o = cqxSlot(Y.W); Object.assign(o, { on: true, x: d.x, z: d.z, r: 4.9, t0: Y.t, hit: false, big: 1 - 0.15 * (d.i | 0) });
    cqbSfx('b_grab', { v: 0.8, at: [d.x, d.z], duck: [0.4, 0.5] }) || AU.slam(); cqbSfx('b_wave', { d: 0.05, v: 0.9 - 0.1 * (d.i | 0) }); shake = Math.max(shake, 0.3); buzz(16); }
  else if (e === 'strikeGo') cqyStrike(3);
  else if (e === 'minesThrow') { const Y = cqyInit(), X = cqxInit(), a = cqyAhead(0.8), bx = Q.boss ? Q.boss.group.position.x : Q.pool.x, bz = Q.boss ? Q.boss.group.position.z : Q.pool.z;
    // (which way you're going; standing about, from the boss to you)
    const sp = Math.hypot(X.pv.x, X.pv.z); let ux, uz; if (sp > 1.5) { ux = X.pv.x / sp; uz = X.pv.z / sp; } else { const ul = Math.hypot(a.x - bx, a.z - bz) || 1; ux = (a.x - bx) / ul; uz = (a.z - bz) / ul; }
    const fw = sp > 1.5 ? 1.2 : -1.6; cqbSfx('b_toss', { at: [d.x, d.z] });
    [[0, 0, 0], [2.4, fw, 0.15], [-2.4, fw, 0.3]].forEach(([s, f, dl]) => { let x = a.x - uz * s + ux * f, z = a.z + ux * s + uz * f; const ox = x - Q.pool.x, oz = z - Q.pool.z, r = Math.hypot(ox, oz) || 1, rc = clamp(r, CQY_IN, CQY_OUT); x = Q.pool.x + ox / r * rc; z = Q.pool.z + oz / r * rc;
      const o = cqxSlot(Y.Mn); Object.assign(o, { on: true, x0: d.x, y0: d.y, z0: d.z, x, z, t0: Y.t + dl, fly: 0.75, fuse: 1.9, ring: null, beeps: 0, rot: Math.random() * 6.283, spin: (Math.random() - 0.5) * 9, landed: false }); }); }
}
// each frame (the boss's time: still while the game is paused)
function cqyTick(dt) {
  const Y = CQY, Q = CQB; if (!Y || !(dt > 0)) return;
  Y.t += dt; Y.bm.uniforms.uTime.value = Y.t; const M = Y.M, v = Y.v, s = Y.s;
  for (let i = Y.q.length - 1; i >= 0; i--) if (Y.t >= Y.q[i].at) { const f = Y.q[i].f; Y.q.splice(i, 1); f(); }
  // the ripples: out from the pool at 6.5 a second to the wall; on the ground as one passes you, you're knocked outward
  let n = 0; const RW = Y.rA.array;
  for (let i = 0; i < Y.W.length; i++) { const o = Y.W[i]; let al = 0;
    if (o.on) { o.r = 4.9 + (Y.t - o.t0) * 6.5; if (o.r > 17.8) o.on = false; }
    if (o.on) { n++; al = Math.min(1, (Y.t - o.t0) / 0.12) * (1 - Math.max(0, (o.r - 15.5) / 2.3)) * o.big; M.makeTranslation(o.x, 0, o.z);
      const pd = Math.hypot(P.x - o.x, P.z - o.z);
      if (!o.hit && Math.abs(pd - o.r) < 0.5 + PR * 0.3 && !(P.air && (P.y || 0) > 0.22)) { o.hit = true; cqbKnock(o.x, o.z, 1.0); } }
    else M.makeScale(0, 0, 0);
    Y.rip.setMatrixAt(i, M); RW[i * 4] = o.on ? o.r : 0; RW[i * 4 + 1] = 0.42; RW[i * 4 + 2] = 0.55 * (o.big || 1); RW[i * 4 + 3] = al; }
  Y.rip.visible = n > 0; Y.rA.needsUpdate = true; Y.rip.instanceMatrix.needsUpdate = true;
  // the strike: the golden ring follows you, then locks and blinks; the beam comes down and it blows; the next one finds you
  const T = Y.T; if (T) { const a = Y.t - T.t0;
    if (a < CQY_FOLLOW) { const k = 1 - Math.exp(-dt * 12), g = cqyAhead((CQY_BEAM - CQY_FOLLOW + 0.08) * Math.min(1, a / CQY_FOLLOW)); T.x += (g.x - T.x) * k; T.z += (g.z - T.z) * k; }
    if (T.ring) { T.ring.x = T.x; T.ring.z = T.z; }
    Y.tmat.uniforms.uA.value = a < CQY_FOLLOW ? Math.min(1, a / 0.15) : 0.55 + 0.45 * Math.sign(Math.sin(a * 40)); Y.tmat.uniforms.uF.value = a < CQY_FOLLOW ? 0 : 1;
    Y.tgt.visible = true; Y.tgt.position.set(T.x, 0.06, T.z); Y.tgt.rotation.y = a * (a < CQY_FOLLOW ? 1.5 : 6); Y.tgt.scale.setScalar(1.5 - 0.15 * Math.min(1, a / CQY_FOLLOW));
    if (a >= CQY_BEAM) { const b = cqxSlot(Y.B); Object.assign(b, { on: true, x: T.x, z: T.z, t0: Y.t }); cqbSfx('b_beam', { at: [T.x, T.z], rate: 0.96 + Math.random() * 0.08 }) || AU.thunder();
      cqyBlast(T.x, T.z, 1.6, 1.4); Y.T = null; Y.tgt.visible = false; if (T.n > 1) cqyStrike(T.n - 1); } }
  else Y.tgt.visible = false;
  // the beams: in fast, thinning and fading
  n = 0; const BB = Y.bA.array;
  for (let i = 0; i < Y.B.length; i++) { const o = Y.B[i]; let al = 0;
    if (o.on) { const a = Y.t - o.t0; if (a > 0.42) o.on = false; else { n++; const r = a < 0.05 ? 0.18 + 0.44 * a / 0.05 : 0.62 - 0.34 * (a - 0.05) / 0.37; al = 1 - Math.max(0, (a - 0.1) / 0.32); M.makeScale(r, 24, r).setPosition(o.x, 0, o.z); } }
    if (!o.on) M.makeScale(0, 0, 0); Y.beam.setMatrixAt(i, M); BB[i] = al; }
  Y.beam.visible = n > 0; Y.bA.needsUpdate = true; Y.beam.instanceMatrix.needsUpdate = true;
  // the rays: shooting out, then fading
  n = 0; const YY = Y.yA.array;
  for (let i = 0; i < Y.Rr.length; i++) { const o = Y.Rr[i]; let al = 0;
    if (o.on) { const a = Y.t - o.t0; if (a > 0.38) o.on = false; else { n++; const L = o.L * Math.min(1, a / 0.1); al = 1 - Math.max(0, (a - 0.12) / 0.26); Y.d.set(o.dx, o.dy, o.dz); Y.Qn.setFromUnitVectors(Y.up, Y.d); M.compose(v.set(o.x, o.y, o.z), Y.Qn, s.set(0.16, Math.max(0.01, L), 0.16)); } }
    if (!o.on) M.makeScale(0, 0, 0); Y.rays.setMatrixAt(i, M); YY[i] = al; }
  Y.rays.visible = n > 0; Y.yA.needsUpdate = true; Y.rays.instanceMatrix.needsUpdate = true;
  // the fire: each fireball swells fast, rises as it slows, cools from white-hot through orange into smoke, and shrinks away
  // (shrinking right in front of the camera, as the clouds do, so a blast on top of you never hides you)
  n = 0; const FH = Y.fA.array;
  for (let i = 0; i < Y.F.length; i++) { const o = Y.F[i];
    if (o.on) { const a = Y.t - o.t0; if (a >= o.L) o.on = false;
      else { n++; const dr = Math.exp(-dt * 3.2), u = a / o.L; o.vx *= dr; o.vz *= dr; o.vy = o.vy * Math.exp(-dt * 2.0) + dt * 0.9; o.x += o.vx * dt; o.y += o.vy * dt; o.z += o.vz * dt;
        const g = a < 0.12 ? 1 - Math.pow(1 - a / 0.12, 3) + Math.sin(a / 0.12 * Math.PI) * 0.25 : 1, sh = u > 0.72 ? Math.max(0, (1 - u) / 0.28) : 1, cd = Math.hypot(o.x - camera.position.x, o.y - camera.position.y, o.z - camera.position.z),
          sc = o.s * g * Math.sqrt(sh) * Math.min(1, Math.max(0, (cd - 2.2) / 3.3)) * (1 + 0.06 * Math.sin(a * 11 + i));
        FH[i * 2] = clamp(1 - u * 1.35, 0, 1); FH[i * 2 + 1] = o.seed; Y.fire.setMatrixAt(i, M.makeScale(sc, sc, sc).setPosition(o.x, o.y, o.z)); continue; } }
    Y.fire.setMatrixAt(i, M.makeScale(0, 0, 0)); }
  Y.fire.visible = n > 0; Y.fA.needsUpdate = true; Y.fire.instanceMatrix.needsUpdate = true;
  // the flash: facing you, a little toward you and up off the floor, swelling and gone in a quarter second
  n = 0; const XL = Y.xA.array;
  for (let i = 0; i < Y.L.length; i++) { const o = Y.L[i]; let al = 0;
    if (o.on) { const a = Y.t - o.t0; if (a > 0.26) o.on = false; else { n++; al = 1 - a / 0.26; const sc = o.s * (0.55 + 0.45 * Math.sqrt(a / 0.26)); v.set(camera.position.x - o.x, 0, camera.position.z - o.z); const dl = v.length() || 1;
      M.compose(v.set(o.x + v.x / dl * 1.2, 0.9, o.z + v.z / dl * 1.2), camera.quaternion, s.set(sc, sc, sc)); } }
    if (!o.on) M.makeScale(0, 0, 0); Y.flash.setMatrixAt(i, M); XL[i] = al; }
  Y.flash.visible = n > 0; Y.xA.needsUpdate = true; Y.flash.instanceMatrix.needsUpdate = true;
  // the mines: flying over in an arc, spinning, their red blast rings already marking where they'll land; down with a clunk; blinking
  // and beeping faster; then they blow (or sooner if you touch one, once it's had a moment)
  n = 0;
  for (let i = 0; i < Y.Mn.length; i++) { const o = Y.Mn[i]; let lit = false;
    if (o.on) { const a = Y.t - o.t0;
      if (a >= 0 && !o.ring) o.ring = cqxRing(o.x, o.z, 4, o.fly + o.fuse, 2.3);
      if (a < 0) M.makeScale(0, 0, 0);
      else if (a < o.fly) { const u = a / o.fly; o.rot += o.spin * dt; Y.Qn.setFromAxisAngle(Y.up, o.rot); M.compose(v.set(o.x0 + (o.x - o.x0) * u, o.y0 + (0.5 - o.y0) * u + 3.2 * 4 * u * (1 - u), o.z0 + (o.z - o.z0) * u), Y.Qn, s.set(1, 1, 1)); n++; }
      else { if (!o.landed) { o.landed = true; cqbSfx('b_grab', { v: 0.45, at: [o.x, o.z], rate: 1.25 }); for (let k = 0; k < 6; k++) { const q = Math.random() * 6.283; cqxPuff(o.x + Math.cos(q) * 0.4, 0.15, o.z + Math.sin(q) * 0.4, Math.cos(q) * 1.2, 0.6, Math.sin(q) * 1.2, 0.14 + Math.random() * 0.1, 0.6, CQX_DUST_C[k % 3]); } }
        const f = (a - o.fly) / o.fuse, per = f < 0.5 ? 0.5 : f < 0.8 ? 0.25 : 0.12, ph = ((a - o.fly) % per) / per, sw = 1 + 0.12 * f + 0.05 * Math.sin(a * 30) * f;
        lit = ph < 0.45; const beat = Math.floor((a - o.fly) / per); if (beat !== o.beeps) { o.beeps = beat; if (beat > 0 && Math.hypot(P.x - o.x, P.z - o.z) < 14) cqbSfx('b_beep', { v: 0.5 + 0.4 * f, rate: 1 + 0.3 * f, at: [o.x, o.z] }); }
        Y.Qn.setFromAxisAngle(Y.up, o.rot); M.compose(v.set(o.x, 0.52, o.z), Y.Qn, s.set(sw, sw, sw)); n++;
        if (f >= 1 || (a - o.fly > 0.15 && Math.hypot(P.x - o.x, P.z - o.z) < CQY_NEAR + PR * 0.5)) { o.on = false; if (o.ring) o.ring.on = false; cqyBlast(o.x, o.z, 2.3, 1.5); M.makeScale(0, 0, 0); } } }
    else M.makeScale(0, 0, 0);
    Y.mines.setMatrixAt(i, M); if (o.on) M.setPosition(v.set(M.elements[12], M.elements[13] + 0.62 * (M.elements[5] || 1), M.elements[14])); Y.lights.setMatrixAt(i, M); Y.lights.setColorAt(i, Y.c.set(lit ? 0xFF2A2A : 0x4A0808)); }
  Y.mines.visible = Y.lights.visible = n > 0; Y.mines.instanceMatrix.needsUpdate = true; Y.lights.instanceMatrix.needsUpdate = true; if (Y.lights.instanceColor) Y.lights.instanceColor.needsUpdate = true;
}
// your LIFE in the demo: a round gauge under the sound button; each of the boss's hits takes one, and you blink for a moment after
// (the game's own grace: nothing knocks you while it lasts), so one attack can't take all three; at none, knocked out by it
var CQL_GRACE = 1.6;
function cqlHit() {
  const Q = CQB; if (!Q || !Q.on || P.st !== 'play') return; Q.life = Math.max(0, (Q.life == null ? 3 : Q.life) - 1); cqlShow(true);
  if (Q.life > 0) P.immuneT = Math.max(P.immuneT || 0, CQL_GRACE);
  if (Q.life <= 0) { knockOut(P, 'boom'); if (P.st === 'ko') { $('kofSmall').textContent = 'Splatted by'; nmSet($('kofBy'), 'Jellyfish Boss'); } }
}
function cqlShow(hurt) { const Q = CQB, el = $('cqLife'); if (!el || !Q) return; const n = Q.life == null ? 3 : Q.life;
  $('cqLifeN').textContent = n; el.style.setProperty('--lf', (n / 3).toFixed(3)); el.classList.toggle('low', n <= 1);
  el.classList.remove('hurt', 'gain'); void el.offsetWidth; if (hurt === true) el.classList.add('hurt'); else if (hurt === 'gain') el.classList.add('gain'); }
function cqlTick() {
  const Q = CQB, el = $('cqLife'); if (!el) return;
  const on = !!(Q && Q.on && (state === 'play' || state === 'paused')); if (el.hidden === on) el.hidden = !on;
  if (!Q) return; if (Q.on !== Q.lifeOn) { Q.lifeOn = Q.on; Q.life = 3; Q.koSeen = false; cqlShow(); }
  if (!Q.on) return; if (P.st === 'ko') Q.koSeen = true; else if (Q.koSeen) { Q.koSeen = false; Q.life = 3; cqlShow('gain'); }
}
"""

HTML = '<div class="cqlife" id="cqLife" hidden role="img" aria-label="Your life"><b>Life</b><span class="cqlr"><i id="cqLifeN">3</i></span></div>'

CSS = r"""
/* (v318) your LIFE in the boss demo: a round gauge (a ring that empties a third at a time, red at the last) under the sound button */
.cqlife{position:absolute;z-index:8;top:calc(env(safe-area-inset-top) + 66px);right:calc(env(safe-area-inset-right) + 12px);width:56px;height:56px;pointer-events:none;--lf:1}
.cqlife .cqlr{position:absolute;inset:0;border-radius:50%;background:conic-gradient(var(--lc,#3FA2FF) calc(var(--lf) * 1turn),rgba(23,19,32,.85) 0);border:3px solid #171320;box-shadow:0 3px 0 #171320;transition:--lf .3s}
.cqlife .cqlr::before{content:'';position:absolute;inset:6px;border-radius:50%;background:#1E1838;box-shadow:inset 0 2px 4px rgba(0,0,0,.5)}
.cqlife .cqlr i{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:400 25px/1 var(--font-display);font-style:normal;color:#FFF8EA;text-shadow:0 2px 0 #171320}
.cqlife b{position:absolute;z-index:1;left:-12px;top:-7px;padding:3px 6px 2px;border-radius:6px;background:#171320;color:#FFF8EA;font:400 10px/1 var(--font-display);letter-spacing:.06em;text-transform:uppercase;transform:rotate(-18deg)}
.cqlife.low{--lc:#FF4A5A}.cqlife.low .cqlr{animation:cqlpulse .8s ease-in-out infinite alternate}
.cqlife.hurt{animation:cqlhurt .45s ease-out}.cqlife.gain{animation:cqlgain .5s cubic-bezier(.2,1.6,.35,1)}
@keyframes cqlhurt{15%{transform:translate(-4px,2px) scale(1.12)}35%{transform:translate(4px,-2px)}55%{transform:translate(-2px,0)}}
@keyframes cqlgain{from{transform:scale(.6)}}
@keyframes cqlpulse{to{box-shadow:0 3px 0 #171320,0 0 14px rgba(255,74,90,.8)}}
@media (orientation:portrait),(min-height:521px){.cqb{right:calc(env(safe-area-inset-right) + 76px)}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.cqb{width:262px}.cqb .cqbs{grid-template-columns:1fr 1fr 1fr}.cqb .cqbs button{padding:0 3px;font-size:11.5px}}
@media (prefers-reduced-motion:reduce){.cqlife.hurt,.cqlife.gain,.cqlife.low .cqlr{animation:none}}
"""


def apply(s):
    # the boss's three new moves; it floats back over the pool for its ripples
    s = rep(s, "        // ---- defeat: a last flinch", MOVES + "        // ---- defeat: a last flinch")
    s = rep(s, "const anchor = mv === 'emerge' || mv === 'intro' || mv === 'defeat',", "const anchor = mv === 'emerge' || mv === 'intro' || mv === 'defeat' || mv === 'ripple',")
    # the demo: the attacks, their events, their frame, let go at the end; the LIFE gauge
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, JS + a)
    s = rep(s, "for (const e of ['rainSpit', 'quakeHit']) b.on(", "for (const e of ['rainSpit', 'quakeHit', 'ripple', 'strikeGo', 'minesThrow']) b.on(")
    s = rep(s, "cqbBarEv(e, d); cqxEv(e, d);", "cqbBarEv(e, d); cqxEv(e, d); cqyEv(e, d);")
    s = rep(s, "  cqxTick(live); // (v317: the area attacks)\n", "  cqxTick(live); cqyTick(live); // (v317, v318: the area attacks)\n")
    s = rep(s, "function cqbTick(dt, rdt) {\n", "function cqbTick(dt, rdt) {\n  cqlTick(); // (v318: your LIFE)\n")
    s = rep(s, "cqbSfxOff(); cqxEnd();", "cqbSfxOff(); cqxEnd(); cqyEnd();")
    s = rep(s, "  emote(P, 'ouch', 0.9); AU.bonk(1); shake = Math.max(shake, 0.4); buzz([20, 25, 30]); popText('Bonked!');",
               "  emote(P, 'ouch', 0.9); AU.bonk(1); shake = Math.max(shake, 0.4); buzz([20, 25, 30]); popText('Bonked!'); cqlHit(); // (v318: a life gone)")
    # the panel: their buttons after Shock wave, their names; the auto attack picks them too
    s = rep(s, '<button type="button" data-m="quake">Shock wave</button>', '<button type="button" data-m="quake">Shock wave</button><button type="button" data-m="ripple">Ripples</button><button type="button" data-m="strike">Strikes</button><button type="button" data-m="mines">Sea mines</button>')
    s = rep(s, "quake: 'Shock wave',", "quake: 'Shock wave', ripple: 'Ripples', strike: 'Strikes', mines: 'Sea mines',")
    s = rep(s, "cqbPlay(r < 0.22 ? 'punch' : r < 0.36 ? 'slam' : r < 0.5 ? 'sweep' : r < 0.62 ? 'zap' : r < 0.77 ? 'rain' : r < 0.92 ? 'quake' : 'taunt'); /* (v317: the area attacks too) */",
               "cqbPlay(r < 0.15 ? 'punch' : r < 0.25 ? 'slam' : r < 0.35 ? 'sweep' : r < 0.44 ? 'zap' : r < 0.55 ? 'rain' : r < 0.66 ? 'quake' : r < 0.77 ? 'ripple' : r < 0.88 ? 'strike' : r < 0.97 ? 'mines' : 'taunt'); /* (v317, v318: the area attacks too) */")
    # the rings: a golden warning (the strike's target) and a red one (a mine's blast)
    s = rep(s, "        if (vR.z < 0.5) { float pu = 0.5 + 0.5 * sin(uTime * (7.0 + 16.0 * p) + vR.w * 6.2832), f = p * 0.88;",
               "        if (vR.z < 0.5 || vR.z > 2.5) { float pu = 0.5 + 0.5 * sin(uTime * (7.0 + 16.0 * p) + vR.w * 6.2832), f = p * 0.88;")
    s = rep(s, "a = rim * (0.8 + 0.35 * pu) + halo + fill + grow + front; c = mix(vec3(1.0, 0.28, 0.78), vec3(1.0, 0.8, 1.0), rim * 0.45 + front * 0.3);",
               "a = rim * (0.8 + 0.35 * pu) + halo + fill + grow + front; vec3 bc = vR.z > 3.5 ? vec3(1.0, 0.3, 0.16) : vR.z > 2.5 ? vec3(1.0, 0.72, 0.18) : vec3(1.0, 0.28, 0.78); c = mix(bc, vec3(1.0, 0.85, 0.95), rim * 0.45 + front * 0.3);")
    # the LIFE gauge's markup and look
    s = rep(s, '<div class="hud off" id="hud">', HTML + '<div class="hud off" id="hud">')
    a = "  .cqb.fold{width:auto}.cqb.fold .cqbh{padding:0}.cqb.fold .cqbh span{display:none}\n}\n"
    s = rep(s, a, a + CSS.strip() + "\n")   # (after the panel's own rules, so these win)
    return s
