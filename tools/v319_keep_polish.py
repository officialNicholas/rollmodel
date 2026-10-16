"""v319: the Sunken Keep, polished. More of a sea round the fight: light falling through the water, the surface rippling far overhead,
life swimming past, and the world going on beyond the walls.

- Light shafts: soft beams of sunlight slant down through the water from the surface, in loose groups of wide and narrow ones, a few
  over the arena and more out beyond the walls. Each one sways a little and slowly brightens and fades; inside, faint streaks drift
  across it. They are brightest high up and fade out toward the floor and as you come close to them. Where the brightest ones land on
  the floor, the light there is a little brighter and its web of ripples stronger, moving with the beam. They take the place of the old
  flat shafts.
- The surface overhead: look up and the water's surface is there far above, a soft web of light rippling slowly over it, brightest
  straight up and fading into the haze toward the horizon (drawn in the water's own backdrop, so it costs no extra draw).
- The water is full of things: specks of marine snow hang and sink slowly all round you (always some near the camera), now and then one
  catches the light and twinkles, the bubbles rise all through the water as before, and from six cracks at the foot of the wall thin
  streams of bubbles wobble up, growing as they rise, high over the wall top. All of it is one draw that moves on the graphics chip
  (the old bubbles were moved one by one every frame).
- Life and depth beyond the walls: schools of little fish (yellow, blue and silver, pink, teal) circle the keep at different heights,
  weaving between the ruins, their tails beating, and a small orange school swims round just inside the wall, high over the floor; far
  off, now and then, a great manta ray glides past high up. Behind the ruins and the wrecks, big rock spires, mounds and broken towers
  stand round the whole keep in the haze, so the sea doesn't end at the wall: lit from the surface's side and from above, darker at their
  feet, the nearer ones dark against the water and the far ones nearly gone in it, each tinted by the water behind it.
- The spout is gone: the column of goo that stood in the middle of the pool, with the glow at its top and the mound round its foot. The
  pool still bubbles, steams and glows, and the boss still rises from its middle.
- On lower graphics settings: fewer shafts, specks, fish (two schools) and rocks, no manta, a plainer surface overhead, the same draws.
- What it costs: one draw more than before on either setting (the shafts, the specks and bubbles, and the fish and rocks are three
  draws; the old shafts and bubbles were two), about 3,700 more triangles (1,900 on lower settings). Nothing new
  is made at launch: the looks are made with the keep's other looks and let go with them, and the pieces are built with the stage and
  let go with it."""


def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)


POLISH = r"""
// ---------- (v319) the Sunken Keep, polished: light shafts falling through the water (and pooling on the floor where they land),
// marine snow, glints and streams of bubbles, schools of fish and a manta circling the keep, rock spires and broken towers in the haze
// beyond. Three draws, all of it moving in the shaders; the looks are the keep's (made and let go with them), the pieces the stage's ----------
const CQV = { t: { value: 0 }, px: { value: 400 }, bs: new THREE.Vector2(), pools: [], pb: [], dir: new THREE.Vector3(-0.17, -1, -0.43).normalize() };
for (let i = 0; i < 8; i++) { CQV.pools.push(new THREE.Vector4(0, 0, 0, 0)); CQV.pb.push([0, 0, 0, 0, 0]); } // (where the light gathers on the floor: now, and still)
// the light shafts: each a ribbon from high above down through the floor, turned to face you round its own line; soft across, brightest
// high up, a few faint streaks drifting inside, swaying and breathing slowly, fading near the floor and as you come close
const cqvShaftMat = () => new THREE.ShaderMaterial({ uniforms: { uTime: CQV.t, uK: { value: HI ? 0.55 : 0.4 }, uDir: { value: CQV.dir } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `uniform float uTime; uniform vec3 uDir; attribute vec4 aA; attribute vec2 aB; varying vec3 vU; varying float vK;
    void main(){ float side = position.x, along = position.y, ph = aA.w, t = uTime;
      vec3 d = normalize(uDir + vec3(0.035 * sin(t * 0.21 + ph), 0.0, 0.035 * sin(t * 0.17 + ph * 1.7)));
      vec3 P = vec3(aA.x, aB.y, aA.y) + d * ((aB.y + 0.8) / -d.y * along), V = cameraPosition - P, W = cross(d, V);
      W = dot(W, W) > 1e-6 ? normalize(W) : vec3(1.0, 0.0, 0.0);
      P += W * (side * aA.z * (0.7 + 0.65 * along) * 0.5);
      vec4 mv = viewMatrix * vec4(P, 1.0); gl_Position = projectionMatrix * mv;
      vK = aB.x * (0.6 + 0.4 * sin(t * 0.29 + ph * 2.3)) * smoothstep(2.0, 9.0, -mv.z) * smoothstep(-0.4, 3.2, P.y);
      vU = vec3(side, along, ph); }`,
  fragmentShader: `uniform float uTime, uK; varying vec3 vU; varying float vK;
    void main(){ float x = vU.x, a = 1.0 - x * x; a *= a;
      float v = vU.y, len = smoothstep(0.0, 0.07, v) * (1.0 - v * 0.72);
      float st = 0.62 + 0.38 * sin(x * 5.0 + vU.z * 3.0 + uTime * 0.23) * sin(x * 13.0 - uTime * 0.17 + vU.z * 5.0);
      gl_FragColor = vec4(vec3(0.56, 0.88, 1.0) * (a * len * st * vK * uK), 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
// the specks and bubbles, one draw of points, all moving here: 0 marine snow and 1 glints (a box that follows the camera, so some are
// always near; they drift and sink slowly, the glints twinkling now and then), 2 bubbles rising all through the water, 3 the streams
// from the cracks at the wall's foot (quick, wobbling, growing as they rise)
const cqvMoteMat = () => new THREE.ShaderMaterial({ uniforms: Object.assign(THREE.UniformsUtils.clone(THREE.UniformsLib.fog), { uTime: CQV.t, uPx: CQV.px, uK: { value: HI ? 1.0 : 0.9 } }), fog: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  vertexShader: `uniform float uTime, uPx, fogNear, fogFar; attribute vec4 aP; attribute vec4 aQ; varying vec4 vC; varying float vT;
    void main(){ float t = uTime, ty = aQ.x, ph = aP.w, a = 1.0, sz = aQ.y; vec3 p;
      if (ty < 1.5) { vec3 B = vec3(22.0, 14.0, 22.0), c = vec3(cameraPosition.x, 7.2, cameraPosition.z);
        vec3 d = vec3(sin(t * 0.13 + ph) * 0.5 + t * 0.06, -t * aQ.z, cos(t * 0.11 + ph * 1.3) * 0.5 + t * 0.03);
        p = c + mod(aP.xyz * B + d - c + B * 0.5, B) - B * 0.5; vec3 e = abs(p - c) / (B * 0.5); a = 1.0 - smoothstep(0.72, 1.0, max(max(e.x, e.z), e.y));
        if (ty > 0.5) { float tw = pow(max(0.0, sin(t * aQ.w + ph * 37.0)), 10.0); a *= tw; sz *= 0.5 + 0.7 * tw; } }
      else if (ty < 2.5) { float y = mod(aP.y + t * aQ.z, 15.0); p = vec3(aP.x + sin(t * 0.8 * aQ.w + ph) * 0.3, y, aP.z + cos(t * 0.6 * aQ.w + ph) * 0.3); a = smoothstep(0.0, 0.6, y) * (1.0 - smoothstep(12.5, 15.0, y)); }
      else { float f = fract(ph + t * aQ.z / aQ.w), w = 0.04 + 0.13 * f; p = aP.xyz + vec3(sin(t * 3.1 + ph * 23.0) * w, f * aQ.w, cos(t * 2.7 + ph * 19.0) * w); sz *= 0.5 + 0.9 * f; a = smoothstep(0.0, 0.03, f) * (1.0 - smoothstep(0.82, 1.0, f)); }
      vec4 mv = viewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; float dz = max(-mv.z, 0.01);
      gl_PointSize = clamp(sz * uPx / dz, 1.0, 90.0);
      a *= smoothstep(0.35, 1.8, dz) * (1.0 - 0.85 * smoothstep(fogNear, fogFar, dz));
      vC = vec4(ty < 0.5 ? vec3(0.66, 0.84, 0.88) * 0.72 : ty < 1.5 ? vec3(1.0, 0.97, 0.88) * 2.0 : vec3(0.61, 0.85, 0.94), a); vT = ty; }`,
  fragmentShader: `uniform float uK; varying vec4 vC; varying float vT;
    void main(){ vec2 q = gl_PointCoord * 2.0 - 1.0; float r = length(q), a;
      if (vT > 1.5) a = smoothstep(0.55, 0.78, r) * (1.0 - smoothstep(0.84, 1.0, r)) * 0.95 + (1.0 - smoothstep(0.6, 0.8, r)) * 0.2 + (1.0 - smoothstep(0.0, 0.26, length(q + vec2(0.3)))) * 0.9;
      else if (vT > 0.5) a = 1.0 - smoothstep(0.0, 0.32, r) + (max(0.0, 1.0 - abs(q.x) * 7.0) * (1.0 - abs(q.y)) + max(0.0, 1.0 - abs(q.y) * 7.0) * (1.0 - abs(q.x))) * 0.7;
      else { a = 1.0 - smoothstep(0.1, 1.0, r); a *= a; }
      if (a * vC.a < 0.003) discard;
      gl_FragColor = vec4(vC.rgb * (a * vC.a * uK), 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
// the fish, the manta and the rocks far off: one look. A fish swims its school's circle round the keep at its place in the school, its
// tail beating (the manta's wings beat slowly); everything far is lit from above and tinted toward the water behind it with distance
const cqvFarMat = W => new THREE.ShaderMaterial({ uniforms: Object.assign(THREE.UniformsUtils.clone(THREE.UniformsLib.fog), { uTime: CQV.t, uDeep: W.uniforms.uDeep, uMid: W.uniforms.uMid, uTop: W.uniforms.uTop }), fog: true,
  vertexShader: `uniform float uTime, fogNear, fogFar; attribute vec4 aF; attribute vec4 aG; attribute vec4 aC; varying vec3 vC, vN, vW; varying float vF;
    void main(){ vec3 p = position, n = normal; float hz = aC.w;
      if (aG.w != 0.0) { float t = uTime, sp = aF.z, s = abs(aG.w), ang = aF.w + sp * t, r = aF.x + aG.z + sin(t * 0.21 + aF.w * 3.0) * 1.1, y = aF.y + aG.y + sin(t * 0.37 + aF.w * 5.0 + aG.x) * 0.45;
        ang += aG.x / r * sign(sp);
        vec3 C = vec3(cos(ang) * r, y, sin(ang) * r), fw = vec3(-sin(ang), 0.0, cos(ang)) * sign(sp), up = vec3(0.0, 1.0, 0.0), sd = cross(fw, up);
        vec3 q = p * s;
        if (aG.w > 0.0) q.z += sin(t * 8.0 + aG.x * 2.3 + aF.w * 9.0 - position.x * 6.0) * 0.1 * clamp(-position.x / 0.3, 0.0, 1.0) * s;
        else { float fl = sin(t * 1.3 + aF.w) * abs(position.z); q.y += fl * 0.32 * s; n = normalize(n + vec3(0.0, 0.0, -sign(position.z) * cos(t * 1.3 + aF.w) * 0.5)); }
        p = C + fw * q.x + up * q.y + sd * q.z; n = normalize(fw * n.x + up * n.y + sd * n.z); }
      vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz; vN = n; vC = aC.rgb;
      vec4 mv = viewMatrix * w; gl_Position = projectionMatrix * mv;
      vF = clamp(smoothstep(fogNear, fogFar * 1.5, -mv.z) + hz, 0.0, 0.96); }`,
  fragmentShader: `uniform vec3 uDeep, uMid, uTop; varying vec3 vC, vN, vW; varying float vF;
    vec3 dome(vec3 d){ float y = d.y; return y < 0.0 ? mix(uMid, uDeep, smoothstep(0.0, 0.4, -y)) : mix(uMid, uTop, pow(smoothstep(0.0, 1.0, y), 1.6)); }
    void main(){ vec3 N = normalize(gl_FrontFacing ? vN : -vN); float l = (0.42 + 0.38 * smoothstep(-0.3, 0.75, N.y) + 0.42 * max(dot(N, vec3(0.37, 0.56, 0.74)), 0.0) + 0.3 * smoothstep(0.6, 0.95, N.y)) * (0.78 + 0.36 * smoothstep(-1.0, 22.0, vW.y));
      gl_FragColor = vec4(mix(vC * l, dome(normalize(vW - cameraPosition)), vF), 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
function conqPolishMats(M) { M.cqvShaft = cqvShaftMat(); M.cqvMote = cqvMoteMat(); M.cqvFar = cqvFarMat(M.water); }
// a little fish (its nose at +x, about 0.55 long): a chunky body of two rings between the nose and the tail's root, a forked tail and a
// fin on its back; the manta: a broad flat diamond, its wing tips out along z, a thin tail
const cqvFishTris = () => { const T = [], r1 = [], r2 = [], n = 6;
  for (let i = 0; i < n; i++) { const a = i / n * 6.2832; r1.push([0.04, Math.cos(a) * 0.12, Math.sin(a) * 0.07]); r2.push([-0.12, Math.cos(a) * 0.075, Math.sin(a) * 0.042]); }
  const nose = [0.27, 0.01, 0], root = [-0.19, 0, 0];
  for (let i = 0; i < n; i++) { const j = (i + 1) % n; T.push([nose, r1[i], r1[j]], [r1[i], r2[j], r1[j]], [r1[i], r2[i], r2[j]], [r2[i], root, r2[j]]); }
  const fin = (a, b, c) => T.push([a, b, c], [a, c, b]);
  fin(root, [-0.33, 0.13, 0], [-0.27, 0, 0]); fin(root, [-0.27, 0, 0], [-0.33, -0.13, 0]); fin([0.05, 0.115, 0], [-0.1, 0.19, 0], [-0.11, 0.07, 0]); return T; };
const cqvMantaTris = () => { const T = [], P = [[0.55, 0.02, 0], [0.12, 0.06, 0.5], [-0.05, 0.02, 1.0], [-0.3, 0.04, 0.35], [-0.42, 0.02, 0], [-0.3, 0.04, -0.35], [-0.05, 0.02, -1.0], [0.12, 0.06, -0.5]], C = [0.06, 0.11, 0], B = [0.06, -0.05, 0];
  for (let i = 0; i < 8; i++) { const j = (i + 1) % 8; T.push([C, P[j], P[i]], [B, P[i], P[j]]); }
  T.push([[-0.42, 0.02, 0], [-1.15, 0.0, 0.012], [-0.42, 0.0, -0.03]], [[-0.42, 0.0, -0.03], [-1.15, 0.0, 0.012], [-0.42, 0.02, 0]]); return T; };
// build the pieces with the stage: the shafts (and where they land, for the light on the floor), the specks and bubbles, the fish and
// the rocks. Everything is placed the same every time
function conqPolish(K) {
  const { M } = K, Rg = rng(3191), lo = !HI, D = Math.PI / 180, W0 = K.T.ring.wall, V3 = THREE.Vector3;
  // ---- the light shafts: groups of parallel beams; where each lands (the light on the floor gathers there), its top is up the slant
  { const L = [], kx = CQV.dir.x / CQV.dir.y, kz = CQV.dir.z / CQV.dir.y; // (a beam's top: where it lands, back up the slant)
    const grp = (x, z, n, w, k) => { for (let i = 0; i < n; i++) L.push([x + (Rg() - 0.5) * 3.4, z + (Rg() - 0.5) * 3.4, w * (0.45 + Rg() * 0.85), k * (0.6 + Rg() * 0.4), L.length * 2.39 + Rg() * 3, 24 + Rg() * 3]); };
    grp(-6.5, 5.5, 3, 2.3, 0.9); grp(7.5, 8.5, 3, 2.0, 0.85); grp(3.5, -7.5, 2, 2.2, 0.75); grp(-9.5, -5, 2, 1.8, 0.7); grp(11, -2, 2, 1.7, 0.7);
    for (const [x, z, w, k] of [[-11, 9, 7.5, 0.42], [12.5, -6, 7.0, 0.4], [2, 13, 8.0, 0.38]]) L.push([x, z, w, k, L.length * 2.39 + Rg() * 3, 24 + Rg() * 3]); // (three broad, faint ones: the light from above over all)
    if (!lo) { grp(-23, 13, 3, 3.2, 1.0); grp(21, 17, 3, 3.4, 1.0); grp(3, 27, 3, 3.6, 1.0); grp(-20, -19, 2, 3.0, 0.9); grp(24, -15, 2, 3.0, 0.9); grp(-29, -2, 2, 3.4, 0.9); }
    else { grp(-23, 13, 2, 3.2, 1.0); grp(21, 17, 2, 3.4, 1.0); grp(3, 27, 2, 3.6, 1.0); }
    const S = 6, pos = [], aA = [], aB = [], idx = [];
    L.forEach(([x, z, w, k, ph, top]) => { const o = pos.length / 3;
      for (let j = 0; j <= S; j++) for (const sd of [-1, 1]) { pos.push(sd, j / S, 0); aA.push(x + kx * top, z + kz * top, w, ph); aB.push(k, top); }
      for (let j = 0; j < S; j++) { const a = o + j * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); } });
    // (the eight brightest that land on the floor: where, how wide, their phase, for the light gathering under them)
    const fl = L.filter(b => Math.hypot(b[0], b[1]) < W0 - 1.5 && b[2] < 4.5).sort((a, b) => b[3] * b[2] - a[3] * a[2]).slice(0, 8);
    CQV.pb.forEach((q, i) => { const b = fl[i]; if (b) { q[0] = b[0]; q[1] = b[1]; q[2] = 1 / (b[2] * b[2] * 0.56); q[3] = b[4]; q[4] = 0.035 / -CQV.dir.y * b[5]; } else q[2] = 0; }); cqvPools(0);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aA', new THREE.Float32BufferAttribute(aA, 4)); g.setAttribute('aB', new THREE.Float32BufferAttribute(aB, 2)); g.setIndex(idx);
    const m = new THREE.Mesh(g, M.cqvShaft); m.renderOrder = 8; m.frustumCulled = false; m.layers.set(2); K.add(m); }
  // ---- the specks and bubbles
  { const aP = [], aQ = [], add = (x, y, z, ph, ty, sz, sp, w) => { aP.push(x, y, z, ph); aQ.push(ty, sz, sp, w); };
    for (let i = 0, n = lo ? 150 : 280; i < n; i++) add(Rg(), Rg(), Rg(), Rg() * 6.28, 0, 0.05 + Rg() * 0.065, 0.05 + Rg() * 0.08, 0);
    for (let i = 0, n = lo ? 30 : 64; i < n; i++) add(Rg(), Rg(), Rg(), Rg() * 6.28, 1, 0.16 + Rg() * 0.1, 0.03 + Rg() * 0.04, 0.35 + Rg() * 0.5);
    for (let i = 0, n = lo ? 110 : 180; i < n; i++) { const a = Rg() * 6.2832, d = Rg() * 22; add(Math.cos(a) * d, Rg() * 15, Math.sin(a) * d, Rg() * 6.28, 2, 0.24 + Rg() * 0.12, 0.5 + Rg() * 0.9, 0.6 + Rg() * 0.8); }
    // the cracks at the wall's foot, between the coral and the kelp, each with its stream
    for (const deg of lo ? [28, 140, 252, 318] : [28, 88, 140, 200, 252, 318]) { const r = W0 - 0.35, x = Math.cos(deg * D) * r, z = Math.sin(deg * D) * r, H = 9 + Rg() * 4, sp = 1.4 + Rg() * 0.5;
      for (let i = 0, n = lo ? 10 : 15; i < n; i++) add(x, 0.05, z, i / n + Rg() * 0.04, 3, 0.11 + Rg() * 0.08, sp * (0.85 + Rg() * 0.3), H); }
    const g = new THREE.BufferGeometry(), N = aP.length / 4; g.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(N * 3), 3)); g.setAttribute('aP', new THREE.Float32BufferAttribute(aP, 4)); g.setAttribute('aQ', new THREE.Float32BufferAttribute(aQ, 4));
    const m = new THREE.Points(g, M.cqvMote); m.renderOrder = 9; m.frustumCulled = false; m.layers.set(2); K.add(m); }
  // ---- the fish, the manta and the rocks far off
  { const pos = [], nrm = [], aF = [], aG = [], aC = [], nv = new V3(), e1 = new V3(), e2 = new V3();
    const tri = (A, B, C, f, g, ca, cb, hz) => { e1.set(B[0] - A[0], B[1] - A[1], B[2] - A[2]); e2.set(C[0] - A[0], C[1] - A[1], C[2] - A[2]); nv.crossVectors(e1, e2).normalize(); const up = (A[1] + B[1] + C[1]) / 3 > (cb ? 0.0 : -9);
      for (const P of [A, B, C]) { pos.push(P[0], P[1], P[2]); nrm.push(nv.x, nv.y, nv.z); aF.push(f[0], f[1], f[2], f[3]); aG.push(g[0], g[1], g[2], g[3]); const c = up || !cb ? ca : cb; aC.push(c.r, c.g, c.b, hz || 0); } };
    // the schools: [radius, height, turn speed (+ one way, - the other), how many, back, belly]
    const FT = cqvFishTris(), SCH = [[23.8, 8.4, 0.085, 14, 0xFFC23A, 0xFFF2C8], [30.5, 12.5, -0.06, 12, 0x3E86D0, 0xD6ECF6], [24.4, 4.0, -0.075, 10, 0xE878C8, 0xFBE0F2], [28.0, 16.5, 0.05, 9, 0x52C0B0, 0xDCF6EE], [15.8, 9.6, -0.11, 8, 0xFF9450, 0xFFE8D6]];
    SCH.slice(0, lo ? 2 : 5).forEach(([r, h, sp, n, cb, cl]) => { const a0 = Rg() * 6.2832, ca = new THREE.Color(cb), cc = new THREE.Color(cl); n = lo ? Math.round(n * 0.7) : n;
      for (let i = 0; i < n; i++) { const g = [(Rg() - 0.5) * (2.2 + n * 0.32), (Rg() - 0.5) * 1.5, (Rg() - 0.5) * 2.2, 1.0 + Rg() * 0.5], f = [r, h, sp * (0.97 + Rg() * 0.06), a0];
        for (const t of FT) tri(t[0], t[1], t[2], f, g, ca, cc, 0); } });
    if (!lo) { const MT = cqvMantaTris(), ca = new THREE.Color(0x2C4E66), cc = new THREE.Color(0x9CC4D2), f = [35, 15.5, 0.032, Rg() * 6.28], g = [0, 0, 0, -3.6]; for (const t of MT) tri(t[0], t[1], t[2], f, g, ca, cc, 0); }
    // the rocks: spires (some leaning, some blunt), low mounds and broken towers, round the whole keep beyond the ruins and the wrecks
    const Z4 = [0, 0, 0, 0], RC = [new THREE.Color(0x16405A), new THREE.Color(0x1A4862), new THREE.Color(0x123A52)];
    const solid = (rings, col, hz, cap) => { const n = rings[0].length; for (let j = 0; j + 1 < rings.length; j++) for (let i = 0; i < n; i++) { const a = rings[j][i], b = rings[j][(i + 1) % n], c = rings[j + 1][(i + 1) % n], d = rings[j + 1][i]; tri(a, c, b, Z4, Z4, col, null, hz); tri(a, d, c, Z4, Z4, col, null, hz); }
      if (cap) { const tp = rings[rings.length - 1], cx = tp.reduce((s, p) => s + p[0], 0) / n, cz = tp.reduce((s, p) => s + p[2], 0) / n, cy = tp.reduce((s, p) => s + p[1], 0) / n + cap; for (let i = 0; i < n; i++) tri(tp[i], [cx, cy, cz], tp[(i + 1) % n], Z4, Z4, col, null, hz); } };
    const NF = lo ? 15 : 24;
    for (let k = 0; k < NF; k++) { const deg = (k + Rg() * 0.6) / NF * 360, r = 36 + Rg() * 15, x0 = Math.cos(deg * D) * r, z0 = Math.sin(deg * D) * r, kind = Rg(), col = RC[k % 3], hz = (r - 36) / 15 * 0.12;
      if (kind < 0.58) { // a spire
        const H = 13 + Rg() * 17, r0 = 2.2 + Rg() * 2.6, n = 7, NR = 5, la = Rg() * 6.2832, lean = (Rg() - 0.3) * 0.22, rings = [];
        for (let j = 0; j <= NR; j++) { const f = j / NR, rr = r0 * (1 - f * 0.72) * (0.85 + Rg() * 0.3), cx = x0 + Math.cos(la) * lean * f * H, cz = z0 + Math.sin(la) * lean * f * H, ring = [];
          for (let i = 0; i < n; i++) { const a = i / n * 6.2832 + j * 0.37, jr = rr * (0.78 + Rg() * 0.44); ring.push([cx + Math.cos(a) * jr, f * H - 1 + (j ? (Rg() - 0.5) * 0.8 : 0), cz + Math.sin(a) * jr]); } rings.push(ring); }
        solid(rings, col, hz, r0 * (Rg() < 0.5 ? 0.9 : 0.15)); }
      else if (kind < 0.82) { // a mound
        const H = 4 + Rg() * 5, r0 = 6 + Rg() * 5, n = 9, rings = [];
        for (const [f, k2] of [[0, 1], [0.5, 0.82], [0.85, 0.5], [1, 0.22]]) { const ring = []; for (let i = 0; i < n; i++) { const a = i / n * 6.2832 + f, jr = r0 * k2 * (0.8 + Rg() * 0.4); ring.push([x0 + Math.cos(a) * jr, f * H - 0.8, z0 + Math.sin(a) * jr]); } rings.push(ring); }
        solid(rings, col, hz, 0.4); }
      else { // a broken tower: round, a little narrower up its height, its top broken off at a slant, a few stones gone
        const H = 12 + Rg() * 10, r0 = 2.6 + Rg() * 1.4, n = 9, tilt = Rg() * 6.2832, rings = [];
        for (const f of [0, 0.35, 0.7, 1]) { const ring = []; for (let i = 0; i < n; i++) { const a = i / n * 6.2832, rr = r0 * (1 - f * 0.12), y = f < 1 ? f * H : H * (0.78 + 0.22 * Math.cos(a - tilt)) - (i % 3 === 1 ? 1.4 : 0); ring.push([x0 + Math.cos(a) * rr, y - 1, z0 + Math.sin(a) * rr]); } rings.push(ring); }
        solid(rings, col, hz, -1.5);
        // its battlement band, a little wider, two thirds up
        const yb = H * 0.62, band = []; for (const dy of [0, 0.9]) { const ring = []; for (let i = 0; i < n; i++) { const a = i / n * 6.2832; ring.push([x0 + Math.cos(a) * r0 * 1.12, yb + dy - 1, z0 + Math.sin(a) * r0 * 1.12]); } band.push(ring); } solid(band, col, hz, 0); } }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3)); g.setAttribute('aF', new THREE.Float32BufferAttribute(aF, 4)); g.setAttribute('aG', new THREE.Float32BufferAttribute(aG, 4)); g.setAttribute('aC', new THREE.Float32BufferAttribute(aC, 4));
    const m = new THREE.Mesh(g, M.cqvFar); m.frustumCulled = false; m.layers.set(2); K.add(m); }
  K.anim({ tick(dt, t) { CQV.t.value = t; renderer.getDrawingBufferSize(CQV.bs); CQV.px.value = CQV.bs.y * 0.5; cqvPools(t); } });
}
// the light gathering on the floor under each beam that lands there follows the beam's sway (as in its shader)
function cqvPools(t) { for (let i = 0; i < 8; i++) { const q = CQV.pb[i]; CQV.pools[i].set(q[0] + Math.sin(t * 0.21 + q[3]) * q[4], q[1] + Math.sin(t * 0.17 + q[3] * 1.7) * q[4], q[2], 0); } }
"""

# the surface far overhead, seen from below: a web of light rippling over it (the floor's caustic map, a little softened, slid two ways on
# higher settings), brightest overhead and fading into the haze toward the horizon; in the water's own dome (no new draw)
DOME_V = "    vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,\n    fragmentShader: `uniform float uTime; uniform vec3 uDeep, uMid, uTop; varying vec3 vD;"
DOME_V2 = ("    defines: { CQ_SURF: HI ? 2 : 1 }, /* (v319: the surface overhead) */\n"
           "    vertexShader: `varying vec3 vD, vP; void main(){ vD = normalize(position); vP = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,\n"
           "    fragmentShader: `uniform float uTime; uniform vec3 uDeep, uMid, uTop; uniform sampler2D uMap; varying vec3 vD, vP;")
DOME_U = "uTop: { value: new THREE.Color(0x62CCEC) } }, side: THREE.BackSide, depthWrite: false,"
DOME_U2 = "uTop: { value: new THREE.Color(0x62CCEC) }, uMap: { value: conqCausticTex() } }, side: THREE.BackSide, depthWrite: false,"
DOME_F = "        c += vec3(0.5, 0.85, 1.0) * pow(max(0.0, dot(d, normalize(vec3(0.1, 1.0, 0.35)))), 14.0) * 0.55;\n        gl_FragColor = vec4(c, 1.0);"
DOME_F2 = """        c += vec3(0.5, 0.85, 1.0) * pow(max(0.0, dot(d, normalize(vec3(0.1, 1.0, 0.35)))), 14.0) * 0.55;
        { vec3 v = normalize(vP - cameraPosition); if (v.y > 0.03) { vec2 sp = cameraPosition.xz + v.xz * ((30.0 - cameraPosition.y) / v.y); // (v319: the surface overhead)
          float w = texture2D(uMap, sp * 0.021 + vec2(uTime * 0.008, uTime * 0.005), 2.2).r;
          #if CQ_SURF > 1
          w *= 0.4 + 1.2 * texture2D(uMap, sp * 0.029 + vec2(-uTime * 0.006, uTime * 0.009) + 0.31, 2.2).r;
          #endif
          c += vec3(0.62, 0.9, 1.0) * w * smoothstep(0.05, 0.7, v.y) * 0.2; } }
        gl_FragColor = vec4(c, 1.0);"""

# the light on the floor gathers where the shafts land (a soft pool under each of the eight brightest that land on the floor, four on lower
# settings, wobbling with its beam's sway): the web of ripples brighter there and a soft light besides; in the v316 caustics shader
POOLS_U = "uK: { value: HI ? 0.36 : 0.3 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,\n  defines: HI ? { CQ_RGB: 1 } : {},"
POOLS_U2 = "uK: { value: HI ? 0.36 : 0.3 }, uPool: { value: CQV.pools } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,\n  defines: HI ? { CQ_RGB: 1, CQ_POOLS: 8 } : { CQ_POOLS: 4 }, /* (v319: the light gathering under the shafts) */"
POOLS_F = "fragmentShader: `uniform float uTime, uK; uniform sampler2D uMap; varying vec3 vW;"
POOLS_F2 = "fragmentShader: `uniform float uTime, uK; uniform sampler2D uMap; uniform vec4 uPool[8]; varying vec3 vW;"
POOLS_B = "float beam = smoothstep(0.2, 0.85, cN(vW.xz * 0.11 + vec2(uTime * 0.03, -uTime * 0.02))), fade ="
POOLS_G = "      gl_FragColor = vec4(vec3(0.6, 0.92, 1.0) * c * uK * (0.45 + 0.85 * beam) * fade, 1.0);"
POOLS_G2 = "      gl_FragColor = vec4(vec3(0.6, 0.92, 1.0) * (c * uK * (0.45 + 0.85 * beam) + pl * 0.07) * fade, 1.0);"
POOLS_B2 = ("float pl = 0.0; for (int i = 0; i < CQ_POOLS; i++) { vec4 q = uPool[i]; vec2 o = vW.xz - q.xy; pl += exp(-dot(o, o) * q.z); } // (v319: under the shafts)\n"
            "      float beam = min(1.6, smoothstep(0.2, 0.85, cN(vW.xz * 0.11 + vec2(uTime * 0.03, -uTime * 0.02))) + pl * 0.9), fade =")


def apply(s):
    # 1. the new looks, made with the keep's other looks (and let go with them)
    s = rep(s, "M.ray = conqRayMat(); M.caustic = conqCausticMat();\n}", "M.ray = conqRayMat(); M.caustic = conqCausticMat(); conqPolishMats(M); // (v319)\n}")
    # 2. the old bubbles (moved one by one every frame) go: they rise in the new points, on the graphics chip
    a = s.index("      // bubbles rising all through the water, one draw\n      { const N = HI ? 180 : 110, pos = new Float32Array(N * 3), B = [];")
    e = "g.attributes.position.needsUpdate = true; } }); }\n"; b = s.index(e, a) + len(e); assert b - a < 1400, b - a
    s = s[:a] + "      // (v319: the bubbles rise with the specks in conqPolish, one draw moving on the graphics chip)\n" + s[b:]
    # 3. the old flat shafts go (the new ones are conqPolish's); the caustics stay
    a = s.index("      // light shafts slanting down from the surface, all in one draw; caustic ripples over the floor and the wall\n      { const pos = [], uvs = [], phs = [], idx = []; let o = 0;")
    e = "const rm = new THREE.Mesh(g, M.ray); rm.renderOrder = 8; rm.frustumCulled = false; rm.layers.set(2); K.add(rm);\n"; b = s.index(e, a) + len(e); assert b - a < 1600, b - a
    s = s[:a] + "      // caustic ripples over the floor and the wall (v319: the light shafts are conqPolish's)\n      {\n" + s[b:]
    # 4. the new pieces, built with the stage
    s = rep(s, "      K.glow(1, 21, 26, 8, 0x3A78A4); // (the surface's light, softly at the top of the view)\n", "      conqPolish(K); // (v319)\n      K.glow(1, 21, 26, 8, 0x3A78A4); // (the surface's light, softly at the top of the view)\n")
    # 5. the light on the floor gathers under the shafts
    s = rep(s, POOLS_U, POOLS_U2); s = rep(s, POOLS_F, POOLS_F2); s = rep(s, POOLS_B, POOLS_B2); s = rep(s, POOLS_G, POOLS_G2)
    # 6. the surface overhead
    s = rep(s, DOME_V, DOME_V2); s = rep(s, DOME_U, DOME_U2); s = rep(s, DOME_F, DOME_F2)
    # 7. the spout goes: the column of goo that stood in the middle of the pool, the glow at its top, and the mound and the crown of
    #    bumps round its foot in the pool's surface (the pool still bubbles and glows; the boss rises from its middle)
    s = rep(s, "        const sm = new THREE.Mesh(gooSpout(), gooMat(GOO_SPOUT_VS)); sm.position.y = -0.1; sm.layers.enable(3); sm.userData.own = true; K.add(sm); K.anim({ tick: gooTick }); gooTick(0, 0); }",
               "        K.anim({ tick: gooTick }); gooTick(0, 0); } // (v319: no spout)")
    s = rep(s, "      K.glow(0, 0.35, 0, 2.2, 0x7A30D8); K.glow(0, 1.3, 0, 1.0, 0x9A48F0);\n", "      K.glow(0, 0.35, 0, 2.2, 0x7A30D8);\n")
    s = rep(s, "  float rc = length(p); return h + 0.24 * exp(-rc * rc / 0.3) + 0.06 * exp(-pow((rc - 0.72) / 0.2, 2.0)) * (0.75 + 0.25 * sin(atan(p.y, p.x) * 7.0 + t * 0.5)); }",
               "  return h; }")
    # the code
    s = rep(s, "// the arena, laid out by hand: the pool (a hole) in the middle,", POLISH.strip('\n') + "\n// the arena, laid out by hand: the pool (a hole) in the middle,")
    return s
