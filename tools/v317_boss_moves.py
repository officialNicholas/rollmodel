"""v317: two new boss moves for the demo, after the user's reference pictures (a boss arena: warning circles glowing on the floor that
then burst into big puffy clouds, and a trail of golden rune circles racing over the floor).

- Slime rain: the Jellyfish Boss swells, throws its gloves up to the sky and spits globs of slime high out of its bell, three hard
  beats one after another. With each, warning rings light up on the floor, glowing pink, a fill growing out to their edge as the time
  runs out: first two anywhere, then two near you, then one where you're heading. Globs of slime fall into them and burst in clouds of
  puffy slime (purple, blue, pink); a flat shock ring spreads from each. Inside a ring when it lands, you're knocked away.
- Shock wave: it raises both fists high together over its bell, a golden charge crackling in them, then slams them down on the floor
  at the pool's edge on your side, in a puff of stone dust and a golden shock ring. Three lines of golden rune circles race out over
  the floor from there, one straight at you and one either side; each circle pops up, flashes and fades. Touch a lit one and you're
  knocked on, the way the wave goes. Too close to the slam itself, and that knocks you too.
- The panel: Slime rain and Shock wave after Zap; Auto attack picks them too.
- The sounds (made with Ludo, finished by tools/boss_sfx_build.py): the rain's wind-up, the spits, a warning hum as the rings light,
  each glob bursting; the shock wave's golden charge, the slam and the rumble of the wave.
- Drawn in four draws (the rings, the globs, the clouds, the runes), made the first time one is needed, let go when the demo ends."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

# ---- the boss: its two new moves (the runtime's MOVES)
MOVES = r"""        // ---- (v317) rain: it swells with its gloves up to the sky and spits globs of slime high up out of its bell, three hard beats,
        // one after another; the demo rings the floor where they'll come down and drops them (rainSpit: where each one left it)
        rain: { len: 3.5,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); },
          run(m, t) {
            const w = wIO(t, 3.5, 0.25, 0.9), kW = sstep(0, 0.6, t), kE = sstep(1.95, 2.6, t), up = kW * (1 - kE);
            let beat = 0; for (let k = 0; k < 3; k++) { const u = (t - 0.7 - k * 0.35) / 0.3; if (u > 0 && u < 1) beat = Math.max(beat, Math.sin(u * Math.PI)); }
            T.yaw = m.yaw; off(0, 0.5 * up - 0.28 * beat, -0.3 * up, w);
            T.lean = lerp(T.lean, -0.28 * up + 0.12 * beat, w); T.squash = lerp(T.squash, 1 + 0.16 * up - 0.24 * beat, w);
            T.pulse = lerp(T.pulse, 1.9, w * up); T.pulseAmp = lerp(T.pulseAmp, 0.6, w * up); T.tentW = lerp(T.tentW, 1.5, w * up);
            for (const s of SIDES) { const g = s === 'L' ? 1 : -1;
              wrist(s, g * (2.2 + 0.35 * beat), 2.5 - 0.45 * beat, 0.25, w * (1 - kE)); springy(s, 1.4, 0.55, w); turn(s, g * 0.4, 1, 0.1, 0, 0.2, 1, 0.9, w * (1 - kE)); grip(s, 'spread', w * (1 - kE));
              wrist(s, g * 2.1, -1.4, 1.2, w * kE); grip(s, 'fist', w * kE); T.arm[s].spark = lerp(T.arm[s].spark, 0.5 + 0.6 * beat, w); }
            T.expr = t < 0.65 ? 'charging' : t < 1.95 ? 'glow' : 'smug';
            T.eyeGlow = Math.max(T.eyeGlow, sstep(0.4, 0.7, t) * (1 - sstep(1.8, 2.2, t)) * w);
            fire(1, 'windup');
            for (let k = 0; k < 3; k++) if (t >= 0.7 + k * 0.35 && !(m.fired & (2 << k))) { m.fired |= 2 << k;
              boss2m(0, 2.0, 0.25, mC); st.sqV -= 1.3; wobble(0.7);
              for (let i = 0; i < 16; i++) { const a = Math.random() * 6.283, sp = 0.6 + Math.random() * 1.2; spawn(1, mC, Math.cos(a) * sp, 7 + Math.random() * 6, Math.sin(a) * sp, 0.13 + Math.random() * 0.15, 1.3, C_SLIME); }
              hitW.copy(mC).applyMatrix4(G); emit('rainSpit', evOf({ i: k, x: hitW.x, y: hitW.y, z: hitW.z })); }
            if (t >= 2.0) fire(16, 'recover');
          } },
        // ---- (v317) quake: both fists up high together over its bell, a golden charge crackling in them; then down, hard, on the floor
        // at the pool's edge on your side (quakeHit: where), and the demo sends lines of golden rings racing out from there
        quake: { len: 3.2,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); const dx = m.P.x - PCX, dz = m.P.z - PCZ, d = Math.max(0.01, Math.hypot(dx, dz));
            m.C.set(PCX + dx / d * (RIM_R + 0.6), FLOOR, PCZ + dz / d * (RIM_R + 0.6)); },
          run(m, t) {
            const w = wIO(t, 3.2, 0.2, 0.9), kW = sstep(0, 0.75, t) * (1 - sstep(0.8, 0.9, t)), kS = sstep(0.8, 0.9, t), kH = sstep(0.95, 1.15, t), kR = sstep(1.9, 2.5, t), dn = kS * (1 - kR);
            const lunge = Math.min(2.6, Math.max(0, Math.hypot(m.C.x - st.root.x, m.C.z - st.root.z) - 2.2));
            T.yaw = m.yaw; off(0, 0.9 * kW - 1.5 * dn, -0.4 * kW + 0.7 * lunge * dn, w);
            T.lean = lerp(T.lean, -0.3 * kW + 0.42 * dn, w); T.squash = lerp(T.squash, 1 + 0.18 * kW - 0.2 * kS * (1 - kH) * (1 - kR), w);
            T.charge = lerp(T.charge, 0.9 * kW, w); T.eyeGlow = Math.max(T.eyeGlow, sstep(0.3, 0.75, t) * (1 - sstep(1.2, 1.6, t)) * w);
            for (const s of SIDES) { const g = s === 'L' ? 1 : -1;
              wrist(s, g * 0.45, 3.0, 0.45, kW * w); turn(s, -g * 0.2, 1, 0.1, 0, 0, 1, 0.95, kW * w); springy(s, 1.3, 0.55, kW * w); grip(s, 'fist', w);
              if (kS > 0) { mB.set(g * 0.62, 0, 0).applyQuaternion(yawQ).add(m.C); mB.y = FLOOR + FR() * 0.95; reach(s, mB); fistAt(s, mB, dn * w); springy(s, 2.8 - 1.4 * kH, 0.85, kS * w);
                turn(s, 0, -1, 0.55, -g, -0.3, 0, 1, dn * w); curve(s, g * 0.3, 0.6, 1, 0, -1, 0.5, 1.2, 0.9, dn * w); }
              T.arm[s].spark = lerp(T.arm[s].spark, 2.0 * kW + 0.5 * dn + 0.3, w); }
            T.expr = t < 0.3 ? 'charging' : t < 0.9 ? 'glow' : t < 1.9 ? 'glare' : 'angry';
            fire(1, 'windup');
            if (!(m.fired & 2) && t >= 0.9) { m.fired |= 2; mC.copy(m.C); mC.y = FLOOR; burst(mC, 8, 2.4, true, 4.5); wobble(1.6); st.flash = Math.max(st.flash, 0.3);
              hitW.copy(mC).applyMatrix4(G); emit('quakeHit', evOf({ x: hitW.x, y: hitW.y, z: hitW.z })); }
            if (t >= 1.9) fire(4, 'recover');
          } },
"""

# ---- the demo: the attacks on the floor
JS = r"""// ---------- (v317) the boss's area attacks, on the arena floor. Slime rain: warning rings glow on the floor (the last one where you're
// heading), globs of slime fall into them and burst in clouds of puffy slime; inside one, you're knocked away. Shock wave: its fists hit
// the floor at the pool's edge and three lines of golden rune circles race out over the floor; touch a lit one and you're knocked on.
// Four draws (rings, globs, clouds, runes), made the first time one is needed, let go with the demo
var CQX = null;
CQB_SFX.push('b_spit', 'b_ring', 'b_erupt', 'b_erupt2', 'b_glow', 'b_rune'); CQB_TWO.b_erupt = 0; // (the bursts' two takes, in turn)
var CQX_N = { ring: 12, blob: 8, puff: 160, rune: 48 }, CQX_R = 1.7, CQX_PUFF_C = [0xA868FF, 0x6F9BFF, 0xFF6FCF, 0xD49EFF, 0xFF8AA0, 0x8F7BFF, 0x7FD8FF], CQX_DUST_C = [0xC9C2E6, 0xAEA6CF, 0xE2DCF5];
function cqxInit() {
  if (CQX) return CQX;
  const grp = new THREE.Group(), V = THREE.Vector3;
  const flat = () => new THREE.PlaneGeometry(2, 2).rotateX(-Math.PI / 2), attr = (g, n, k, name) => { const a = new THREE.InstancedBufferAttribute(new Float32Array(n * k), k); a.setUsage(THREE.DynamicDrawUsage); g.setAttribute(name, a); return a; };
  const im = (g, m, n, ro) => { const o = new THREE.InstancedMesh(g, m, n); o.frustumCulled = false; o.renderOrder = ro; o.instanceMatrix.setUsage(THREE.DynamicDrawUsage); o.visible = false; grp.add(o); return o; };
  // the rings: warnings (a glowing pink edge, a faint fill, the fill growing out to the edge as the time runs out, pulsing faster), and
  // flat shock rings spreading (pink from a glob, gold from the slam)
  const rg = flat(), rA = attr(rg, CQX_N.ring, 4, 'aR');
  const rm = new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute vec4 aR; varying vec2 vP; varying vec4 vR; void main(){ vP = uv * 2.0 - 1.0; vR = aR; gl_Position = projectionMatrix * viewMatrix * modelMatrix * instanceMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform float uTime; varying vec2 vP; varying vec4 vR;
      void main(){ float d = length(vP); if (d > 1.0 || vR.y <= 0.0) discard; float p = vR.x, a; vec3 c;
        if (vR.z < 0.5) { float pu = 0.5 + 0.5 * sin(uTime * (7.0 + 16.0 * p) + vR.w * 6.2832), f = p * 0.88;
          float rim = smoothstep(0.83, 0.89, d) * (1.0 - smoothstep(0.93, 0.99, d)), halo = exp(-pow((d - 0.91) / 0.1, 2.0)) * 0.55;
          float fill = (1.0 - smoothstep(0.85, 0.9, d)) * (0.09 + 0.07 * pu), grow = (1.0 - smoothstep(f - 0.03, f, d)) * 0.2, front = exp(-pow((d - f) / 0.035, 2.0)) * 0.75 * step(0.03, p);
          a = rim * (0.8 + 0.35 * pu) + halo + fill + grow + front; c = mix(vec3(1.0, 0.28, 0.78), vec3(1.0, 0.8, 1.0), rim * 0.45 + front * 0.3);
        } else { float r = 0.35 + 0.65 * sqrt(p); a = (exp(-pow((d - r) / 0.07, 2.0)) * 1.3 + (1.0 - smoothstep(0.0, r, d)) * 0.15) * (1.0 - p);
          c = vR.z < 1.5 ? vec3(1.0, 0.45, 0.95) : vec3(1.0, 0.82, 0.35); }
        gl_FragColor = vec4(c * a * vR.y, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }` });
  // the golden rune circle: a ring, a ring inside it, two squares across each other, ticks between, a dot, a soft glow behind
  const cv = document.createElement('canvas'); cv.width = cv.height = 256; { const g = cv.getContext('2d'), c = 128;
    const gr = g.createRadialGradient(c, c, 50, c, c, 128); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.72, 'rgba(255,255,255,0.3)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
    g.strokeStyle = '#fff'; g.lineWidth = 12; g.beginPath(); g.arc(c, c, 104, 0, 6.2832); g.stroke(); g.lineWidth = 6; g.beginPath(); g.arc(c, c, 80, 0, 6.2832); g.stroke();
    g.lineWidth = 7; g.save(); g.translate(c, c); g.rotate(Math.PI / 4); g.strokeRect(-47, -47, 94, 94); g.restore(); g.lineWidth = 6; g.strokeRect(c - 40, c - 40, 80, 80);
    for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; g.beginPath(); g.moveTo(c + Math.cos(a) * 84, c + Math.sin(a) * 84); g.lineTo(c + Math.cos(a) * 100, c + Math.sin(a) * 100); g.stroke(); }
    g.fillStyle = '#fff'; g.beginPath(); g.arc(c, c, 13, 0, 6.2832); g.fill(); }
  const tex = new THREE.CanvasTexture(cv); tex.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
  const ng = flat(), nA = attr(ng, CQX_N.rune, 2, 'aK');
  const nm = new THREE.ShaderMaterial({ uniforms: { uMap: { value: tex } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute vec2 aK; varying vec2 vUv; varying vec2 vK; void main(){ vUv = uv; vK = aK; gl_Position = projectionMatrix * viewMatrix * modelMatrix * instanceMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform sampler2D uMap; varying vec2 vUv; varying vec2 vK;
      void main(){ float a = texture2D(uMap, vUv).a * vK.x; if (a < 0.003) discard; vec3 c = mix(vec3(1.0, 0.7, 0.16), vec3(1.0, 0.96, 0.78), clamp(vK.y, 0.0, 1.0) * 0.7);
        gl_FragColor = vec4(c * a * (0.8 + 0.9 * vK.y), 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }` });
  // the globs (glossy purple slime) and the clouds (round puffs, each its own colour)
  const ball = new THREE.IcosahedronGeometry(1, 2);
  const bm = new THREE.MeshStandardMaterial({ color: 0x9B3CFF, emissive: 0x3C0E86, roughness: 0.22, metalness: 0 });
  const pm = new THREE.MeshLambertMaterial({ color: 0xFFFFFF, emissive: 0x000000 }); // (each puff glows in its own colour too: vivid in the blue water)
  pm.onBeforeCompile = sh => { sh.fragmentShader = sh.fragmentShader.replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n  #ifdef USE_INSTANCING_COLOR\n  { float fr = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 2.2); totalEmissiveRadiance += vColor * 0.75 + vec3(0.92, 0.88, 1.0) * fr * 0.4; }\n  #endif'); }; // (and a soft pale rim, like cotton)
  const X = CQX = { grp, rA, rm, nA, nm, tex, ball, bm, pm, rings: im(rg, rm, CQX_N.ring, 7), runes: im(ng, nm, CQX_N.rune, 7), blobs: im(ball, bm, CQX_N.blob, 3), puffs: im(ball, pm, CQX_N.puff, 3),
    R: [], N: [], F: [], q: [], t: 0, lp: { x: P.x, z: P.z }, pv: { x: 0, z: 0 }, M: new THREE.Matrix4(), Q4: new THREE.Quaternion(), v: new V(), s: new V(), c: new THREE.Color(), Y: new V(0, 1, 0) };
  for (let i = 0; i < CQX_N.ring; i++) X.R.push({ on: false });
  for (let i = 0; i < CQX_N.rune; i++) X.N.push({ on: false });
  for (let i = 0; i < CQX_N.puff; i++) { X.F.push({ on: false }); X.puffs.setColorAt(i, X.c.set(0xFFFFFF)); }
  X.puffs.instanceColor.setUsage(THREE.DynamicDrawUsage);
  scene.add(grp); return X;
}
function cqxEnd() {
  const X = CQX; if (!X) return; CQX = null; scene.remove(X.grp);
  for (const o of [X.rings, X.runes, X.blobs, X.puffs]) { o.geometry.dispose(); if (o.dispose) o.dispose(); }
  for (const m of [X.rm, X.nm, X.bm, X.pm]) m.dispose(); X.tex.dispose(); X.ball.dispose();
}
function cqxClear() { const X = CQX; if (!X) return; X.q.length = 0; for (const a of [X.R, X.N, X.F]) for (const o of a) o.on = false; }
// a free slot (or the oldest one in use)
function cqxSlot(a) { let best = null, bt = 1e9; for (const o of a) { if (!o.on) return o; if (o.t0 < bt) { bt = o.t0; best = o; } } return best; }
function cqxRing(x, z, mode, T, r) { const X = cqxInit(), o = cqxSlot(X.R); Object.assign(o, { on: true, x, z, mode, T, r, t0: X.t, k: Math.random(), blob: mode === 0 }); return o; }
function cqxPuff(x, y, z, vx, vy, vz, s, L, col) { const X = cqxInit(), o = cqxSlot(X.F); Object.assign(o, { on: true, x, y, z, vx, vy, vz, s, L, t0: X.t }); X.puffs.setColorAt(X.F.indexOf(o), X.c.set(col)); X.puffs.instanceColor.needsUpdate = true; }
function cqxRune(x, z, dx, dz) { const X = cqxInit(), o = cqxSlot(X.N); Object.assign(o, { on: true, x, z, dx, dz, t0: X.t, rot: Math.random() * 6.283 }); }
// where a ring can go: on the floor between the pool's curb and the wall, clear of the others (unless it's the one where you're heading)
function cqxOk(x, z, any) { const Q = CQB, X = CQX, r = Math.hypot(x - Q.pool.x, z - Q.pool.z); if (r < 5.8 || r > 15.2) return false;
  if (!any) for (const o of X.R) if (o.on && o.mode === 0 && Math.hypot(o.x - x, o.z - z) < CQX_R * 1.7) return false; return true; }
function cqxSpot(cx, cz, r0, r1) { const Q = CQB;
  for (let n = 0; n < 40; n++) { const a = Math.random() * 6.283, d = r0 + Math.random() * (r1 - r0), x = cx + Math.sin(a) * d, z = cz + Math.cos(a) * d; if (cqxOk(x, z)) return { x, z }; }
  for (let n = 0; n < 60; n++) { const a = Math.random() * 6.283, d = 6.2 + Math.random() * 8.5, x = Q.pool.x + Math.sin(a) * d, z = Q.pool.z + Math.cos(a) * d; if (cqxOk(x, z)) return { x, z }; } return null; }
// a glob's ring: lights up now, the glob comes down at its end
function cqxWarn(x, z, T) { cqxRing(x, z, 0, T, CQX_R); }
// a glob lands: a burst of slime clouds, a shock ring, and you knocked away if you're inside
function cqxErupt(x, z) {
  for (let i = 0; i < 22; i++) { const a = Math.random() * 6.283, r = Math.random() * 1.2, sp = 0.6 + Math.random() * 1.8;
    cqxPuff(x + Math.cos(a) * r, 0.2 + Math.random() * 0.5, z + Math.sin(a) * r, Math.cos(a) * sp, 0.8 + Math.random() * 2.0, Math.sin(a) * sp, 0.22 + Math.random() * 0.28, 1.0 + Math.random() * 0.8, CQX_PUFF_C[(Math.random() * CQX_PUFF_C.length) | 0]); }
  cqxRing(x, z, 1, 0.5, 2.6);
  cqbSfx('b_erupt', { at: [x, z], rate: 0.92 + Math.random() * 0.16 }) || AU.splashWater();
  const dd = Math.hypot(P.x - x, P.z - z); shake = Math.max(shake, clamp(0.34 - dd * 0.02, 0.06, 0.3));
  if (dd < CQX_R + PR * 0.6) cqbKnock(x, z, 1.3);
}
function cqxEv(e, d) {
  const Q = CQB;
  if (e === 'start' && d.move === 'emerge') cqxClear();
  else if (e === 'windup' && d.move === 'rain') cqbSfx('b_windup', { v: 0.85 });
  else if (e === 'windup' && d.move === 'quake') cqbSfx('b_glow');
  else if (e === 'rainSpit') {
    const X = cqxInit(), i = d.i | 0, sp = []; cqbSfx('b_spit', { at: [d.x, d.z], rate: 0.95 + i * 0.06 });
    const T0 = 1.62 - i * 0.12;
    if (i < 2) for (let k = 0; k < 2; k++) { const s = i === 0 ? cqxSpot(Q.pool.x, Q.pool.z, 6.2, 14.6) : cqxSpot(P.x, P.z, 2.6, 3.8); if (s) { sp.push(s); cqxWarn(s.x, s.z, T0 + k * 0.12); } }
    else { let x = P.x + X.pv.x * 0.55, z = P.z + X.pv.z * 0.55; const ox = x - Q.pool.x, oz = z - Q.pool.z, r = Math.hypot(ox, oz) || 1, rc = clamp(r, 6.0, 15.0); x = Q.pool.x + ox / r * rc; z = Q.pool.z + oz / r * rc; sp.push({ x, z }); cqxWarn(x, z, T0); }
    if (sp.length) cqbSfx('b_ring', { v: 0.6, at: [sp[0].x, sp[0].z], rate: 1 + i * 0.06 });
  }
  else if (e === 'quakeHit') {
    const X = cqxInit(), ix = d.x, iz = d.z, a0 = Math.atan2(P.x - ix, P.z - iz);
    cqxRing(ix, iz, 2, 0.55, 4.6);
    for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283, sp = 1 + Math.random() * 2.2; cqxPuff(ix + Math.cos(a) * 0.8, 0.2 + Math.random() * 0.4, iz + Math.sin(a) * 0.8, Math.cos(a) * sp, 0.8 + Math.random() * 1.6, Math.sin(a) * sp, 0.2 + Math.random() * 0.26, 0.8 + Math.random() * 0.6, CQX_DUST_C[(Math.random() * CQX_DUST_C.length) | 0]); }
    for (const da of [-0.42, 0, 0.42]) { const a = a0 + da, sx = Math.sin(a), sz = Math.cos(a);
      for (let k = 0; k < 13; k++) { const dist = 1.4 + k * 1.25, x = ix + sx * dist, z = iz + sz * dist, rr = Math.hypot(x - Q.pool.x, z - Q.pool.z);
        if (rr > 16.4) break; if (rr < 5.0) continue; X.q.push({ at: X.t + 0.06 + k * 0.075, f: () => cqxRune(x, z, sx, sz) }); } }
    cqbSfx('b_slam', { at: [ix, iz], duck: [0.75, 1.4] }) || AU.quake(); cqbSfx('b_rune', { d: 0.06 });
    const dd = Math.hypot(P.x - ix, P.z - iz); shake = Math.max(shake, clamp(0.6 - dd * 0.025, 0.12, 0.55)); buzz([30, 30, 50]);
    if (dd < 2.2) cqbKnock(ix, iz, 1.6);
  }
}
// each frame (the boss's time: still while the game is paused)
function cqxTick(dt) {
  const X = CQX; if (!X || !(dt > 0)) return;
  X.t += dt; X.rm.uniforms.uTime.value = X.t;
  const kv = Math.min(1, dt * 6); X.pv.x += ((P.x - X.lp.x) / dt - X.pv.x) * kv; X.pv.z += ((P.z - X.lp.z) / dt - X.pv.z) * kv; X.lp.x = P.x; X.lp.z = P.z;
  for (let i = X.q.length - 1; i >= 0; i--) if (X.t >= X.q[i].at) { const f = X.q[i].f; X.q.splice(i, 1); f(); }
  const M = X.M, v = X.v, s = X.s;
  // the rings, and the globs falling into the warnings
  let nR = 0, nB = 0;
  for (let i = 0; i < X.R.length; i++) { const o = X.R[i], A = X.rA.array; let p = 0, al = 0;
    if (o.on) { p = (X.t - o.t0) / o.T;
      if (o.mode === 0 && p >= 1) { o.on = false; cqxErupt(o.x, o.z); }
      else if (o.mode !== 0 && p >= 1) o.on = false; }
    if (o.on) { nR++; al = o.mode === 0 ? Math.min(1, (X.t - o.t0) / 0.15) : 1; M.makeScale(o.r, 1, o.r).setPosition(o.x, 0.04, o.z); }
    else M.makeScale(0, 0, 0);
    X.rings.setMatrixAt(i, M); A[i * 4] = Math.min(1, p); A[i * 4 + 1] = al; A[i * 4 + 2] = o.on ? o.mode : 0; A[i * 4 + 3] = o.k || 0;
    // its glob: the last half second before it lands, falling faster and stretching
    if (o.on && o.mode === 0 && nB < CQX_N.blob) { const u = (X.t - o.t0 - (o.T - 0.5)) / 0.5;
      if (u > 0) { const y = 14 - 13.6 * u * u, st = 1 + 0.9 * u; M.makeScale(0.55 / Math.sqrt(st), 0.55 * st, 0.55 / Math.sqrt(st)).setPosition(o.x, y, o.z); X.blobs.setMatrixAt(nB++, M); } } }
  for (let i = nB; i < CQX_N.blob; i++) X.blobs.setMatrixAt(i, M.makeScale(0, 0, 0));
  X.rings.visible = nR > 0; X.blobs.visible = nB > 0; X.rA.needsUpdate = true; X.rings.instanceMatrix.needsUpdate = true; X.blobs.instanceMatrix.needsUpdate = true;
  // the clouds: each puffs up fast, drifts up and out as the water slows it, holds, and shrinks away
  let nF = 0;
  for (let i = 0; i < X.F.length; i++) { const o = X.F[i];
    if (o.on) { const a = X.t - o.t0; if (a >= o.L) o.on = false;
      else { nF++; const dr = Math.exp(-dt * 2.4); o.vx *= dr; o.vz *= dr; o.vy *= Math.exp(-dt * 1.6); o.x += o.vx * dt; o.y += o.vy * dt; o.z += o.vz * dt;
        const g = a < 0.2 ? 1 - Math.pow(1 - a / 0.2, 3) * 1.0 + Math.sin(a / 0.2 * Math.PI) * 0.18 : 1, sh = a > o.L - 0.55 ? Math.max(0, (o.L - a) / 0.55) : 1, cd = Math.hypot(o.x - camera.position.x, o.y - camera.position.y, o.z - camera.position.z), near = Math.min(1, Math.max(0, (cd - 2.2) / 3.3)), sc = o.s * g * sh * near * (1 + 0.05 * Math.sin(a * 9 + i)); // (shrinking away right in front of the camera, so it never hides you)
        X.puffs.setMatrixAt(i, M.makeScale(sc, sc * 0.92, sc).setPosition(o.x, o.y, o.z)); continue; } }
    X.puffs.setMatrixAt(i, M.makeScale(0, 0, 0)); }
  X.puffs.visible = nF > 0; X.puffs.instanceMatrix.needsUpdate = true;
  // the runes: each pops up, flashes, holds lit, fades; a lit one knocks you on, the way the wave goes
  let nN = 0; const K = X.nA.array;
  for (let i = 0; i < X.N.length; i++) { const o = X.N[i];
    if (o.on) { const a = X.t - o.t0; if (a >= 0.95) o.on = false;
      else { nN++; o.rot += dt * 0.9; const u = Math.min(1, a / 0.18) - 1, sc = 0.85 * (0.35 + 0.65 * (1 + 2.7 * u * u * u + 1.7 * u * u)); // (popping up, a little past its size and back)
        X.Q4.setFromAxisAngle(X.Y, o.rot); M.compose(v.set(o.x, 0.05, o.z), X.Q4, s.set(sc, 1, sc)); X.runes.setMatrixAt(i, M);
        K[i * 2] = a < 0.5 ? 1 : Math.max(0, 1 - (a - 0.5) / 0.45); K[i * 2 + 1] = Math.max(0, 1 - a / 0.25);
        if (a < 0.5 && CQB.kcd <= 0 && Math.hypot(P.x - o.x, P.z - o.z) < 0.85 + PR * 0.4) cqbKnock(P.x - o.dx, P.z - o.dz, 1.1);
        continue; } }
    X.runes.setMatrixAt(i, M.makeScale(0, 0, 0)); K[i * 2] = 0; }
  X.runes.visible = nN > 0; X.nA.needsUpdate = true; X.runes.instanceMatrix.needsUpdate = true;
}
"""


def apply(s):
    # the boss's two new moves
    s = rep(s, "        // ---- defeat: a last flinch", MOVES + "        // ---- defeat: a last flinch")
    # the demo: the attacks on the floor, their events, their frame, let go at the end
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, JS + a)
    s = rep(s, "    b.on('windup', d => cqbEvent('windup', d)); // (v316: for its sound)\n",
               "    b.on('windup', d => cqbEvent('windup', d)); // (v316: for its sound)\n    for (const e of ['rainSpit', 'quakeHit']) b.on(e, d => cqbEvent(e, d)); // (v317: the area attacks)\n")
    s = rep(s, "cqbBarEv(e, d); // (v316: the health bar)", "cqbBarEv(e, d); cqxEv(e, d); // (v316: the health bar; v317: the area attacks)")
    s = rep(s, "  if (live > 0) { cqbSwim(live); b.update(live, { player: Q.pl.set(P.x, (P.y || 0) + 0.45, P.z), camera }); }\n",
               "  if (live > 0) { cqbSwim(live); b.update(live, { player: Q.pl.set(P.x, (P.y || 0) + 0.45, P.z), camera }); }\n  cqxTick(live); // (v317: the area attacks)\n")
    s = rep(s, "cqbSfxOff(); // (v316: its sounds stopped and let go)", "cqbSfxOff(); cqxEnd(); // (v316: its sounds stopped and let go; v317: the area attacks)")
    # the panel: their buttons after Zap, their names; the auto attack picks them too
    s = rep(s, '<button type="button" data-m="zap">Zap</button>', '<button type="button" data-m="zap">Zap</button><button type="button" data-m="rain">Slime rain</button><button type="button" data-m="quake">Shock wave</button>')
    s = rep(s, "zap: 'Zap',", "zap: 'Zap', rain: 'Slime rain', quake: 'Shock wave',")
    s = rep(s, "cqbPlay(r < 0.34 ? 'punch' : r < 0.54 ? 'slam' : r < 0.74 ? 'sweep' : r < 0.9 ? 'zap' : 'taunt');",
               "cqbPlay(r < 0.22 ? 'punch' : r < 0.36 ? 'slam' : r < 0.5 ? 'sweep' : r < 0.62 ? 'zap' : r < 0.77 ? 'rain' : r < 0.92 ? 'quake' : 'taunt'); /* (v317: the area attacks too) */")
    return s
