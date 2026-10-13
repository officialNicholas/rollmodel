// ---------- (v257) the first launch: a barrel of paint in the dark rocks, tips over and pours; a pair of eyes comes up out of the puddle and
// looks about; you pick their colour and style, then the paint's colour; it hauls itself out and jumps clear, shakes the paint off,
// you name it, it winks and jumps away, and the iris opens on the lobby with it jumping in. The music builds with each pick (AU.flm).
// Only for a brand-new player (no name, no matches, the lesson still ahead; window.__introNow forces it). Its scene is its own,
// built only when it runs, drawn in place of the lobby, and thrown away after ----------
var FL = (() => {
  const due = !!window.__introNow || (!store.introDone && !store.name && !((store.runs || 0) > 0) && tutPh() === 'match');
  const api = { due, live: false, jin: null, hush: due, busy: () => false, frame: () => false, after: () => {}, boot: () => {} };
  if (!due) return api;
  const V3 = THREE.Vector3, PEARL = new THREE.Color(0xE6DEF2), C0 = new V3(0.72, 0, 0.26), LAND = new V3(0.42, 0, 1.18);
  const ease = u => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); }, eOut = u => 1 - Math.pow(1 - clamp(u, 0, 1), 3), eIn = u => Math.pow(clamp(u, 0, 1), 2.2);
  const BR = { base: new V3(-0.66, 0, -0.3), Rb: 0.3, Rm: 0.355, H: 0.92 }, TIP = new V3(0.93, 0, 0.36).normalize(), TIPAX = new V3(TIP.z, 0, -TIP.x);
  let X = null; // everything the scene is made of, while it runs
  // ---- the scene ----
  function canvasTex(w, h, draw, srgb) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); if (srgb !== false) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }
  const rnd = (a, b) => a + Math.random() * (b - a);
  function barrelTex() {
    // the staves, the hoops, the label, and the paint that has run down it over the years
    const hoops = [0.1, 0.32, 0.68, 0.9];
    const map = canvasTex(512, 512, (g, W, H) => {
      const n = 18; for (let i = 0; i < n; i++) { const x0 = i / n * W, w = W / n, l = 22 + Math.random() * 9; g.fillStyle = 'hsl(' + rnd(22, 30) + ',' + rnd(38, 50) + '%,' + l + '%)'; g.fillRect(x0, 0, w + 1, H);
        g.strokeStyle = 'rgba(40,20,10,.35)'; g.lineWidth = 1; for (let k = 0; k < 5; k++) { g.beginPath(); const gx = x0 + rnd(3, w - 3); g.moveTo(gx, 0); for (let y = 0; y <= H; y += 16) g.lineTo(gx + Math.sin(y * 0.02 + k * 3 + i) * 2.2, y); g.stroke(); }
        g.fillStyle = 'rgba(20,10,6,.75)'; g.fillRect(x0, 0, 2, H); g.fillStyle = 'rgba(255,220,180,.08)'; g.fillRect(x0 + 2, 0, 2, H); }
      // old paint, dried on: a few colours the barrel has held
      for (const c of ['#E3122F', '#FFC61A', '#A03CFF', '#2FD15A']) { g.fillStyle = c; g.globalAlpha = 0.55; const x = rnd(0, W); g.beginPath(); g.ellipse(x, rnd(H * 0.35, H * 0.9), rnd(4, 9), rnd(3, 6), 0, 0, 7); g.fill(); for (let k = 0; k < 4; k++) { g.beginPath(); g.arc(x + rnd(-26, 26), rnd(H * 0.3, H * 0.95), rnd(1.5, 3.5), 0, 7); g.fill(); } }
      g.globalAlpha = 1;
      // the label: a paper card taped on the front
      const lx = W * 0.5, ly = H * 0.5; g.save(); g.translate(lx, ly); g.rotate(-0.03); g.fillStyle = '#F4EEE3'; g.strokeStyle = '#171320'; g.lineWidth = 4; g.beginPath(); g.rect(-70, -52, 140, 104); g.fill(); g.stroke();
      g.fillStyle = '#171320'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = '400 30px "Bowlby One", "Arial Black", Impact, sans-serif'; g.fillText('WET', 0, -16); g.fillText('PAINT', 0, 18);
      g.font = '800 11px Figtree, Arial, sans-serif'; g.fillText('HANDLE WITH FLAIR', 0, 42);
      g.fillStyle = 'rgba(255,241,196,.92)'; g.rotate(0.08); g.fillRect(-26, -62, 52, 18); g.restore();
      // the hoops, with their rivets
      for (const v of hoops) { const y = (1 - v) * H, h = 22; g.fillStyle = '#25212C'; g.fillRect(0, y - h / 2, W, h); g.fillStyle = 'rgba(255,255,255,.22)'; g.fillRect(0, y - h / 2, W, 2); g.fillStyle = 'rgba(0,0,0,.5)'; g.fillRect(0, y + h / 2 - 2, W, 2);
        for (let x = 14; x < W; x += 57) { g.fillStyle = '#4A4452'; g.beginPath(); g.arc(x, y, 3.2, 0, 7); g.fill(); g.fillStyle = 'rgba(255,255,255,.35)'; g.beginPath(); g.arc(x - 1, y - 1, 1.2, 0, 7); g.fill(); } }
      // the paint that's in it, run down from the rim: pearly drips, rounded at their ends
      g.fillStyle = '#E9E2F4'; g.fillRect(0, 0, W, 9);
      for (let i = 0; i < 26; i++) { const x = rnd(0, W), w = rnd(5, 13), len = rnd(14, i % 5 === 0 ? 150 : 60); g.beginPath(); g.moveTo(x - w, 0); g.lineTo(x - w * 0.55, len); g.arc(x, len, w * 0.55, Math.PI, 0, true); g.lineTo(x + w, 0); g.closePath(); g.fill(); }
      g.fillStyle = 'rgba(255,255,255,.5)'; for (let i = 0; i < 26; i++) { g.fillRect(rnd(0, W), 2, 2, rnd(5, 30)); }
    });
    // roughness (green) and metalness (blue): the hoops are iron, the paint is glossy
    const rm = canvasTex(128, 128, (g, W, H) => { g.fillStyle = 'rgb(0,215,0)'; g.fillRect(0, 0, W, H); for (const v of hoops) { g.fillStyle = 'rgb(0,120,190)'; g.fillRect(0, (1 - v) * H - 3, W, 6); } g.fillStyle = 'rgb(0,60,0)'; g.fillRect(0, 0, W, 4); g.fillRect(W * 0.36, H * 0.38, W * 0.28, H * 0.24); }, false);
    rm.colorSpace = THREE.NoColorSpace; return { map, rm };
  }
  function makeBarrel() {
    const { Rb, Rm, H } = BR, pts = [new THREE.Vector2(0.001, 0), new THREE.Vector2(Rb, 0)];
    for (let i = 1; i <= 14; i++) { const y = i / 14 * H; pts.push(new THREE.Vector2(Rb + (Rm - Rb) * Math.sin(Math.PI * y / H), y)); }
    pts.push(new THREE.Vector2(Rb - 0.028, H), new THREE.Vector2(Rb - 0.03, H - 0.07), new THREE.Vector2(0.001, H - 0.07));
    const geo = new THREE.LatheGeometry(pts, 36), P3 = geo.attributes.position, UV = geo.attributes.uv;
    for (let i = 0; i < P3.count; i++) { const y = P3.getY(i), r = Math.hypot(P3.getX(i), P3.getZ(i)); UV.setY(i, r < Rb - 0.01 ? 0.995 : clamp(y / H, 0.002, 0.995)); }
    const T = barrelTex(), mat = new THREE.MeshStandardMaterial({ map: T.map, roughnessMap: T.rm, metalnessMap: T.rm, roughness: 1, metalness: 1, side: THREE.DoubleSide });
    const body = new THREE.Mesh(geo, mat); body.rotation.y = Math.PI + 0.35; // (the label to the front)
    const lidTop = canvasTex(128, 128, (g, W) => { g.fillStyle = '#5A3A22'; g.fillRect(0, 0, W, W); for (let i = 0; i < 5; i++) { g.fillStyle = 'hsl(' + rnd(22, 30) + ',45%,' + rnd(22, 30) + '%)'; g.fillRect(0, i * W / 5, W, W / 5 - 2); }
      g.strokeStyle = '#25212C'; g.lineWidth = 9; g.beginPath(); g.arc(W / 2, W / 2, W / 2 - 5, 0, 7); g.stroke(); g.fillStyle = '#E9E2F4'; g.beginPath(); g.ellipse(W * 0.3, W * 0.62, 14, 9, 0.4, 0, 7); g.fill(); });
    const lid = new THREE.Mesh(new THREE.CylinderGeometry(Rb - 0.012, Rb - 0.012, 0.035, 28), [new THREE.MeshStandardMaterial({ color: 0x2A2530, roughness: 0.45, metalness: 0.7 }), new THREE.MeshStandardMaterial({ map: lidTop, roughness: 0.8 }), new THREE.MeshStandardMaterial({ color: 0x3A2618, roughness: 0.9 })]);
    lid.position.y = H + 0.012;
    const g = new THREE.Group(); g.add(body, lid); return { g, body, lid };
  }
  // the floor, the puddle and every splat on it, and the soft shadows: one surface, one draw
  const FLOOR_FS = `uniform vec3 uCol; uniform float uPearl, uT, uR, uMR; uniform vec2 uC, uM, uSpot; uniform vec3 uSpl[24]; uniform vec4 uRip[4]; uniform vec4 uHole; uniform vec3 uKey; uniform vec4 uShB; uniform vec2 uShD; uniform vec4 uShC; uniform int uN;
varying vec3 vW;
float hs(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(hs(i), hs(i + vec2(1.0, 0.0)), f.x), mix(hs(i + vec2(0.0, 1.0)), hs(i + vec2(1.0, 1.0)), f.x), f.y); }
float smin(float a, float b, float k){ float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0); return mix(b, a, h) - k * h * (1.0 - h); }
float field(vec2 p){
  float f = 9.0;
  if (uR > 0.001) { vec2 q = p - uC; float a = atan(q.y, q.x); float w = 0.05 * sin(a * 5.0 + uT * 0.9) + 0.03 * sin(a * 9.0 - uT * 1.3) + 0.05 * (vn(q * 2.6 + uT * 0.15) - 0.5); f = length(q) - uR * (1.0 + w); }
  if (uMR > 0.001) f = smin(f, length(p - uM) - uMR, 0.3);
  for (int i = 0; i < 24; i++) { if (i >= uN) break; vec3 s = uSpl[i]; if (s.z > 0.0) { vec2 q = p - s.xy; float d = length(q) * (1.0 + 0.22 * sin(atan(q.y, q.x) * 5.0 + float(i) * 2.1)) - s.z; f = smin(f, d, 0.035); } }
  return f;
}
float height(vec2 p, float f){
  float h = smoothstep(0.0, -0.11, f);
  for (int i = 0; i < 4; i++) { vec4 r = uRip[i]; float age = uT - r.z; if (r.w > 0.0 && age > 0.0 && age < 3.0) { float d = length(p - r.xy), fr = age * 0.75; h += r.w * sin((d - fr) * 34.0) * exp(-age * 1.6) * smoothstep(0.16, 0.0, abs(d - fr + 0.06)) * smoothstep(0.0, -0.02, f); } }
  if (uHole.w > 0.0) { float d = length(p - uHole.xy); h += uHole.w * 0.55 * exp(-pow((d - uHole.z) / 0.045, 2.0)) * smoothstep(0.0, -0.02, f); }
  return h;
}
void main(){
  vec2 p = vW.xz; float f = field(p), dS = length((p - uSpot) * vec2(1.0, 1.15)), spot = smoothstep(3.4, 0.15, dS); spot *= spot; vec3 col = vec3(0.0);
  if (f > -0.03) {
  // dark old boards
  float bw = 0.26, row = floor(p.y / bw), off = hs(vec2(row, 3.0)) * 4.0, seg = floor((p.x + off) / 1.7), id = hs(vec2(row, seg));
  vec2 lp = vec2(fract((p.x + off) / 1.7), fract(p.y / bw));
  float grain = vn(vec2(p.x * 2.4 + id * 9.0, p.y * 46.0)) * 0.55 + vn(vec2(p.x * 11.0, p.y * 120.0 + id * 5.0)) * 0.45;
  vec3 wood = mix(vec3(0.16, 0.085, 0.05), vec3(0.3, 0.17, 0.095), id) * (0.75 + 0.42 * grain);
  wood *= 0.4 + 0.6 * smoothstep(0.0, 0.04, lp.y) * smoothstep(1.0, 0.96, lp.y) * smoothstep(0.0, 0.006, lp.x) * smoothstep(1.0, 0.994, lp.x);
  // old paint, long dried
  { vec2 sc = floor(p * 2.2); float hh = hs(sc + 7.0); if (hh > 0.9) { vec2 o = (vec2(hs(sc + 1.0), hs(sc + 2.0)) - 0.5) * 0.3; float d = length(fract(p * 2.2) - 0.5 - o) * (1.0 + 0.3 * sin(atan(p.y, p.x) * 7.0 + hh * 40.0)); vec3 pc = 0.5 + 0.5 * cos(6.2832 * (hh * 3.0 + vec3(0.0, 0.33, 0.67))); wood = mix(wood, pc * wood * 2.2, smoothstep(0.09, 0.07, d) * 0.55); } }
  col = wood * (0.035 + 1.15 * spot);
  // shadows: the barrel (a soft capsule along its length) and the character
  { vec2 a = uShB.xy, b = uShB.xy + uShD * uShB.z, pa = p - a, ba = b - a; float hh = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-4), 0.0, 1.0); float d = length(pa - ba * hh); col *= 1.0 - 0.72 * smoothstep(uShB.w + 0.22, uShB.w - 0.12, d); }
  if (uShC.w > 0.0) { float d = length(p - uShC.xy); col *= 1.0 - 0.6 * uShC.w * smoothstep(uShC.z * 1.5, uShC.z * 0.3, d); }
  }
  // the paint
  if (f < 0.03) {
    // (the paint's surface: its height once, its slope from the screen-space change across the pixel, so one evaluation of the field)
    float h = height(p, f); vec3 S = vec3(vW.x, h * 0.09, vW.z); vec3 n = normalize(cross(dFdx(S), dFdy(S))); if (n.y < 0.0) n = -n;
    vec3 v = normalize(cameraPosition - vW), L = normalize(uKey), hv = normalize(L + v);
    vec3 ir = 0.5 + 0.5 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + dot(n.xz, vec2(2.2, 1.4)) + p.x * 0.5 + uT * 0.04));
    vec3 base = mix(uCol, mix(vec3(0.78, 0.74, 0.86), ir * 0.85 + 0.15, 0.32), uPearl);
    float lit = (0.3 + 0.7 * spot) * (0.62 + 0.38 * max(dot(n, L), 0.0));
    vec3 r = reflect(-v, n); vec3 env = mix(vec3(0.03, 0.02, 0.05), vec3(1.0, 0.95, 1.05), smoothstep(0.35, 0.95, r.y)) * (0.4 + 0.6 * spot);
    float fr = 0.04 + 0.96 * pow(1.0 - max(dot(n, v), 0.0), 5.0);
    vec3 pc = base * lit * (0.75 + 0.25 * smoothstep(-0.02, -0.16, f)) + env * fr * 0.9 + vec3(1.0, 0.97, 0.94) * pow(max(dot(n, hv), 0.0), 140.0) * 2.2 * (0.25 + 0.75 * spot);
    if (uShC.w > 0.0) { float d = length(p - uShC.xy); pc *= 1.0 - 0.45 * uShC.w * smoothstep(uShC.z * 1.4, uShC.z * 0.3, d); }
    float aa = fwidth(f) * 1.2 + 0.002; col = mix(col, pc, smoothstep(aa, -aa, f));
    col = mix(col, col * 0.5, smoothstep(0.03, 0.0, f) * smoothstep(-0.02, 0.005, f) * 0.6);
  }
  col = mix(vec3(0.038, 0.026, 0.058), col, smoothstep(4.6, 2.4, length(p - uSpot)));
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
  function makeFloor() {
    const U = { uCol: { value: PEARL.clone() }, uPearl: { value: 1 }, uT: { value: 0 }, uR: { value: 0 }, uMR: { value: 0 }, uC: { value: new THREE.Vector2(C0.x, C0.z) }, uM: { value: new THREE.Vector2() }, uSpot: { value: new THREE.Vector2(0.15, 0.25) },
      uSpl: { value: Array.from({ length: 24 }, () => new V3()) }, uN: { value: 0 }, uRip: { value: Array.from({ length: 4 }, () => new THREE.Vector4()) }, uHole: { value: new THREE.Vector4() }, uKey: { value: new V3(-0.4, 0.8, 0.45) },
      uShB: { value: new THREE.Vector4(BR.base.x, BR.base.z, 0, 0.36) }, uShD: { value: new THREE.Vector2(1, 0) }, uShC: { value: new THREE.Vector4() } };
    const m = new THREE.Mesh(new THREE.PlaneGeometry(40, 40).rotateX(-Math.PI / 2), new THREE.ShaderMaterial({ uniforms: U, extensions: { derivatives: true },
      vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }', fragmentShader: FLOOR_FS }));
    m.position.set(0.15, 0, 0.25); m.renderOrder = -2; return { m, U };
  }
  // the pour: a rope of paint out of the barrel's mouth, falling to the floor
  function makeStream() {
    const U = { uP0: { value: new V3() }, uV0: { value: new V3() }, uT: { value: 0.5 }, uR: { value: 0 }, uCut: { value: 0 }, uCol: { value: PEARL.clone() }, uPearl: { value: 1 }, uTime: { value: 0 } };
    const g = new THREE.CylinderGeometry(1, 1, 1, 12, 28, true);
    const m = new THREE.Mesh(g, new THREE.ShaderMaterial({ uniforms: U,
      vertexShader: `uniform vec3 uP0, uV0; uniform float uT, uR, uCut, uTime; varying float vS; varying vec3 vN, vW;
void main(){ float s = 0.5 - position.y; vS = s; float t = s * uT; vec3 g = vec3(0.0, -9.0, 0.0), c = uP0 + uV0 * t + 0.5 * g * t * t, tg = normalize(uV0 + g * t);
  vec3 sd = normalize(cross(tg, vec3(0.0, 0.0, 1.0)) + vec3(1e-4)), bn = normalize(cross(tg, sd)); float r = uR * mix(1.0, 0.55, s) * (1.0 + 0.12 * sin(s * 26.0 - uTime * 18.0)) * smoothstep(uCut - 0.02, uCut + 0.06, s);
  vec2 q = normalize(position.xz); vN = normalize(sd * q.x + bn * q.y); vec3 w = c + vN * r; vW = w; gl_Position = projectionMatrix * viewMatrix * vec4(w, 1.0); }`,
      fragmentShader: `uniform vec3 uCol; uniform float uPearl, uCut, uTime; varying float vS; varying vec3 vN, vW;
void main(){ if (vS < uCut) discard; vec3 n = normalize(vN), v = normalize(cameraPosition - vW); float nd = max(dot(n, v), 0.0);
  vec3 ir = 0.5 + 0.5 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + n.x * 0.8 + vS * 2.0 - uTime * 0.4)); vec3 base = mix(uCol, mix(vec3(0.78, 0.74, 0.86), ir * 0.85 + 0.15, 0.32), uPearl);
  float streak = 0.5 + 0.5 * sin(vS * 40.0 - uTime * 24.0 + n.x * 3.0); vec3 c = base * (0.45 + 0.55 * nd) + vec3(1.0) * pow(nd, 18.0) * (0.5 + 0.6 * streak) + vec3(0.9, 0.85, 1.0) * pow(1.0 - nd, 3.0) * 0.35;
  gl_FragColor = vec4(c, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}` }));
    m.frustumCulled = false; m.visible = false; return { m, U };
  }
  // drops of paint: one instanced mesh, each drop stretched along its flight
  const DROPS = 96;
  function makeDrops() {
    const m = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 12, 8), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.08, metalness: 0 }), DROPS);
    const z = new THREE.Matrix4().makeScale(0, 0, 0), c = new THREE.Color(1, 1, 1); for (let i = 0; i < DROPS; i++) { m.setMatrixAt(i, z); m.setColorAt(i, c); }
    m.frustumCulled = false; m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); return m;
  }
  // the light from above: a beam through the dark with dust turning in it
  function makeBeam() {
    const U = { uT: { value: 0 }, uPx: { value: 1 } }, g = new THREE.CylinderGeometry(0.22, 1.7, 6, 40, 1, true);
    const m = new THREE.Mesh(g, new THREE.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
      vertexShader: 'varying vec3 vN, vW; varying float vY; void main(){ vY = position.y; vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vN = normalize(mat3(modelMatrix) * normal); gl_Position = projectionMatrix * viewMatrix * w; }',
      fragmentShader: 'uniform float uT; varying vec3 vN, vW; varying float vY; void main(){ vec3 v = normalize(cameraPosition - vW); float e = pow(abs(dot(normalize(vN), v)), 2.5); float h = smoothstep(-3.0, 1.5, vY) * smoothstep(3.0, 0.5, vY); float fl = 0.85 + 0.15 * sin(vW.x * 3.0 + vW.y * 2.0 + uT * 0.7); gl_FragColor = vec4(vec3(1.0, 0.9, 0.78) * e * h * fl * 0.06, 1.0); }' }));
    m.position.set(0.0, 3, 0.1); m.rotation.z = 0.12; m.renderOrder = 50;
    const n = 70, pos = new Float32Array(n * 3), sd = new Float32Array(n); for (let i = 0; i < n; i++) { const a = Math.random() * 6.283, r = Math.sqrt(Math.random()) * 1.2; pos[i * 3] = Math.cos(a) * r; pos[i * 3 + 1] = Math.random() * 3; pos[i * 3 + 2] = Math.sin(a) * r; sd[i] = Math.random(); }
    const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pos, 3)); pg.setAttribute('aS', new THREE.BufferAttribute(sd, 1));
    const dust = new THREE.Points(pg, new THREE.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: 'uniform float uT, uPx; attribute float aS; varying float vA; void main(){ vec3 p = position; p.y = mod(p.y + uT * (0.04 + 0.05 * aS), 3.0); p.x += sin(uT * 0.3 + aS * 30.0) * 0.15; p.z += cos(uT * 0.23 + aS * 20.0) * 0.15; vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = (1.2 + 2.2 * aS) * 7.0 / -mv.z * (uPx); vA = (0.35 + 0.65 * sin(uT * (0.8 + aS) + aS * 40.0) * 0.5 + 0.5) * smoothstep(0.0, 0.4, p.y) * smoothstep(3.0, 2.2, p.y); }',
      fragmentShader: 'varying float vA; void main(){ float d = length(gl_PointCoord - 0.5); gl_FragColor = vec4(vec3(1.0, 0.92, 0.8) * smoothstep(0.5, 0.1, d) * vA * 0.7, 1.0); }' }));
    dust.position.set(0.1, 0.1, 0.2); dust.frustumCulled = false;
    return { m, dust, U };
  }
  const BG_FS = `uniform float uT; uniform vec2 uRes; varying vec2 vUv;
float hs(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main(){ vec2 p = vUv; vec3 c = mix(vec3(0.038, 0.026, 0.058), vec3(0.058, 0.038, 0.088), smoothstep(0.8, 1.05, p.y));
  c += vec3(0.22, 0.17, 0.3) * exp(-dot((p - vec2(0.5, 1.08)) * vec2(1.5, 1.0), (p - vec2(0.5, 1.08)) * vec2(1.5, 1.0)) * 3.5) * 0.12;
  for (int i = 0; i < 4; i++) { float fi = float(i) * 2.0; vec2 o = vec2(fract(hs(vec2(fi, 1.0)) + uT * 0.003 * (1.0 + fi * 0.2)), 0.4 + 0.55 * hs(vec2(fi, 2.0))); vec2 d = (p - o) * vec2(uRes.x / uRes.y, 1.0); float r = 0.025 + 0.035 * hs(vec2(fi, 3.0));
    vec3 bc = 0.5 + 0.5 * cos(6.2832 * (fi * 0.17 + vec3(0.0, 0.33, 0.67))); c += bc * smoothstep(r, r * 0.55, length(d)) * 0.012 * (0.6 + 0.4 * sin(uT * 0.5 + fi)); }
  c *= 0.55 + 0.45 * smoothstep(1.25, 0.35, length((p - 0.5) * vec2(1.1, 1.0)));
  c += (hs(p * uRes + fract(uT)) - 0.5) * 0.01;
  gl_FragColor = vec4(c, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
  function build() {
    const sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(34, viewW / viewH, 0.05, 60);
    sc.environment = scene.environment || null;
    const hemi = new THREE.HemisphereLight(0x9C92D8, 0x1A1022, 0.9), key = new THREE.DirectionalLight(0xFFEEDC, 2.6), rim = new THREE.DirectionalLight(0xA58CFF, 1.6), fill = new THREE.DirectionalLight(0xFFD6B0, 0.35);
    key.position.set(-2.2, 4.6, 3.2); key.target.position.set(0.2, 0, 0.1); rim.position.set(2.6, 2.6, -3.6); rim.target.position.set(0.2, 0.3, 0); fill.position.set(1.5, 1, 4);
    sc.add(hemi, key, key.target, rim, rim.target, fill);
    const bgU = { uT: { value: 0 }, uRes: { value: new THREE.Vector2(viewW, viewH) } }, bg = new THREE.Scene(), bgCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    bg.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ uniforms: bgU, depthTest: false, depthWrite: false, vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }', fragmentShader: BG_FS })));
    const floor = makeFloor(), barrel = makeBarrel(), stream = makeStream(), drops = makeDrops(), beam = makeBeam();
    sc.add(floor.m, barrel.g, stream.m, drops, beam.m, beam.dust);
    // the character: made with the game's own maker, so what you pick is exactly what you get
    const CH = AXOC.S.ready ? AXOC : SLIME, I = CH.make({ color: PEARL.getHex() }), hold = new THREE.Group(); hold.scale.setScalar(PR); hold.add(I.root); hold.visible = false; sc.add(hold);
    I.noGhost = true; if (I.coatOn) I.coatOn(); if (I.setPaint) I.setPaint(PEARL); if (I.setExpression) I.setExpression('happy');
    const o = { pos: [0, 0, 0], wt: { yaw: 0, pitch: 0 }, watch: null, dt: 0 };
    X = { sc, pc: cam, bg, bgCam, bgU, key, floor, barrel, stream, drops, beam, CH, I, hold, o, drop: [], spl: 0, rip: 0,
      t: 0, ph: 'wait', pt: 0, clock: 0, paint: PEARL.clone(), paintTo: null, pearl: 1, R: 0, MR: 0, mouth: new V3(), lid: { on: true, p: new V3(), v: new V3(), r: new V3(), w: new V3(), rest: false },
      ch: { x: C0.x, z: C0.z, y: -1.2, yaw: 0, air: false, vy: 0, h: 0, sq: 0, rise: 0, wy: 0, wp: 0.05, wade: 1, curl: 0, look: [0, 0] }, tilt: 0, lift: 0,
      cs: { t: new V3(-0.25, 0.42, -0.05), r: 1.25, yaw: 0.2, p: 0.3, ox: 0, oy: 0, shake: 0 }, shot: null, flags: {}, picks: { iris: 0, style: 0 } };
    shot('barrel', true);
    // (everything compiled now, out of sight, while the barrel stands in the dark)
    try { if (renderer.compileAsync) { hold.visible = stream.m.visible = true; renderer.compileAsync(sc, cam).catch(() => {}); hold.visible = stream.m.visible = false; } } catch (e) {}
    I.onBurst = () => burstOff();
  }
  function dispose() {
    if (!X) return; const I = X.I, own = new Set();
    I.root.traverse(o => { if (o.material) for (const m of [].concat(o.material)) own.add(m); }); // (the character's geometry and face sheets are shared with the game's own: only its materials are its own)
    for (const m of own) m.dispose();
    { const L = X.CH.S && X.CH.S.list; const i = L ? L.indexOf(I) : -1; if (i >= 0) L.splice(i, 1); }
    X.hold.remove(I.root);
    for (const s of [X.sc, X.bg]) s.traverse(o => { if (o === X.hold || o.parent === X.hold) return; if (o.geometry) o.geometry.dispose(); if (o.material) for (const m of [].concat(o.material)) { for (const k of ['map', 'roughnessMap', 'metalnessMap']) if (m[k] && !own.has(m)) m[k].dispose(); m.dispose(); } });
    X = null;
  }
  // ---- the camera: a shot is what to look at, how much of it to fit, and from which way; it eases between shots, and keeps what it
  // looks at in the part of the screen the cards leave clear ----
  const SHOTS = {
    barrel: () => ({ t: new V3(-0.36, 0.42, -0.12), r: 0.72, yaw: 0.22, p: 0.22, k: 1.4 }),
    tip: () => ({ t: new V3(0.1, 0.2, 0.05), r: 1.15, yaw: 0.12, p: 0.4, k: 1.6 }),
    eyes: () => ({ t: new V3(X.ch.x, 0.06, X.ch.z), r: 0.46, yaw: 0.02, p: 0.32, k: 1.5 }),
    paint: () => ({ t: new V3(X.ch.x - 0.05, 0.08, X.ch.z), r: 0.72, yaw: 0.06, p: 0.44, k: 1.6 }),
    form: () => ({ t: new V3((C0.x + LAND.x) / 2, 0.32, (C0.z + LAND.z) / 2), r: 0.95, yaw: 0.05, p: 0.36, k: 2.2 }),
    name: () => ({ t: new V3(LAND.x, 0.3, LAND.z), r: 0.5, yaw: -0.12, p: 0.2, k: 1.8 }),
    exit: () => ({ t: new V3(LAND.x + 0.5, 0.3, LAND.z - 0.4), r: 1.05, yaw: -0.05, p: 0.22, k: 1.2 }),
  };
  function shot(k, snap) { X.shot = SHOTS[k](); X.shotK = k; if (snap) { const c = X.cs, s = X.shot; c.t.copy(s.t); c.r = s.r; c.yaw = s.yaw; c.p = s.p; } }
  let freeAt = 0, free = null;
  function freeRect() {
    const now = performance.now(); if (free && now - freeAt < 250) return free; freeAt = now;
    const W = viewW, H = viewH, sr = stage.getBoundingClientRect(), top = Math.min(H * 0.12, safeTop() + 8); let r = { x0: 0, y0: top, x1: W, y1: H };
    const c = UI && UI.cur && !UI.cur.hidden && !UI.cur.classList.contains('out') ? UI.cur.getBoundingClientRect() : null;
    if (c && c.width > 0) { if (W > H * 1.05) r.x1 = c.left - sr.left - 8; else r.y1 = c.top - sr.top - 6; }
    return free = r;
  }
  let safeT = -1; function safeTop() { if (safeT < 0) { const d = document.createElement('div'); d.style.cssText = 'position:absolute;top:0;height:env(safe-area-inset-top);visibility:hidden'; document.body.appendChild(d); safeT = d.offsetHeight || 0; d.remove(); } return safeT; }
  function camTick(dt) {
    const c = X.cs, s = X.shot, a = 1 - Math.exp(-dt * s.k), W = viewW, H = viewH, F = freeRect(), fw = Math.max(80, F.x1 - F.x0), fh = Math.max(80, F.y1 - F.y0);
    c.t.lerp(s.t, a); c.r += (s.r - c.r) * a; c.yaw += (s.yaw - c.yaw) * a; c.p += (s.p - c.p) * a;
    // far enough back that the shot's radius fits the clear part of the screen, and that part's middle on what it looks at
    const d = Math.max(0.6, c.r * H / (Math.tan(X.pc.fov * Math.PI / 360) * 0.86 * Math.min(fw, fh)));
    c.ox += ((F.x0 + F.x1) / 2 - W / 2 - c.ox) * a; c.oy += ((F.y0 + F.y1) / 2 - H / 2 - c.oy) * a;
    c.shake = Math.max(0, c.shake - dt * 2.5); const sh = c.shake * c.shake * 0.05, tt = X.t;
    const pp = new V3(Math.sin(c.yaw) * Math.cos(c.p), Math.sin(c.p), Math.cos(c.yaw) * Math.cos(c.p)).multiplyScalar(d).add(c.t);
    pp.x += Math.sin(tt * 0.37) * 0.02 + Math.sin(tt * 37) * sh; pp.y += Math.sin(tt * 0.29) * 0.015 + Math.cos(tt * 41) * sh;
    const cam = X.pc; cam.aspect = W / H; cam.position.copy(pp); cam.lookAt(c.t); cam.setViewOffset(W, H, -c.ox, -c.oy, W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  }
  // ---- drops and splats ----
  function spawn(p, v, r, col) { const D = X.drop; if (D.length >= DROPS) D.shift(); D.push({ p: p.clone(), v: v.clone(), r, c: (col || X.paint).clone(), life: 3 }); }
  function splat(x, z, r) { const S = X.floor.U.uSpl.value, i = X.spl++ % S.length; S[i].set(x, z, r); X.floor.U.uN.value = Math.min(S.length, X.spl); }
  function ripple(x, z, amp) { const R = X.floor.U.uRip.value, i = X.rip++ % R.length; R[i].set(x, z, X.t, amp); }
  const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new V3(), _up = new V3(0, 1, 0), _d = new V3();
  function dropsTick(dt) {
    const M = X.drops, D = X.drop, U = X.floor.U; let i = 0;
    for (let k = D.length - 1; k >= 0; k--) { const d = D[k]; d.v.y -= 9.5 * dt; d.p.addScaledVector(d.v, dt); d.life -= dt;
      if (d.p.y < d.r * 0.6) { const inP = Math.hypot(d.p.x - U.uC.value.x, d.p.z - U.uC.value.y) < X.R * 0.95; if (inP) ripple(d.p.x, d.p.z, 0.25); else splat(d.p.x, d.p.z, d.r * (2.2 + Math.random())); D.splice(k, 1); continue; }
      if (d.life <= 0) { D.splice(k, 1); continue; } }
    for (const d of D) { const sp = d.v.length(); _d.copy(d.v).divideScalar(sp || 1); _q.setFromUnitVectors(_up, _d); _s.set(d.r, d.r * (1 + Math.min(1.6, sp * 0.09)), d.r); _m.compose(d.p, _q, _s); M.setMatrixAt(i, _m); M.setColorAt(i, d.c); i++; }
    _m.makeScale(0, 0, 0); for (; i < (M.userData.n || DROPS); i++) M.setMatrixAt(i, _m); M.userData.n = D.length;
    M.instanceMatrix.needsUpdate = true; if (M.instanceColor) M.instanceColor.needsUpdate = true;
  }
  // the paint coming off it: drops flung out all round from its body and ears as it shakes
  function burstOff() {
    if (!X) return; const c = X.ch, base = new V3(c.x, 0.25, c.z);
    for (let i = 0; i < 40; i++) { const a = Math.random() * 6.283, up = rnd(1.6, 4.2), s = rnd(1.6, 3.6); spawn(new V3(base.x + Math.cos(a) * 0.14, rnd(0.12, 0.42), base.z + Math.sin(a) * 0.14), new V3(Math.cos(a) * s, up, Math.sin(a) * s), rnd(0.012, 0.03)); }
    snd('splat', 1); buzz([8, 20, 8]);
  }
  // ---- sound: the intro's own effects where they've loaded, the game's otherwise ----
  function snd(k, v) {
    const fx = AU.flm && AU.flm.fx;
    switch (k) {
      case 'wobble': if (!fx('wobble', v)) AU.bonk && AU.bonk(); break;
      case 'tip': if (!fx('tip', v)) { AU.land(1); AU.splat(1.2); } break;
      case 'pour': if (!fx('pour', v)) AU.glug && AU.glug(); break;
      case 'eyes': if (!fx('eyes', v)) AU.pop(); break;
      case 'form': if (!fx('form', v)) AU.splashWater && AU.splashWater(); break;
      case 'sparkle': if (!fx('sparkle', v)) AU.ui(); break;
      case 'splat': AU.splat(v || 0.8); break;
      case 'pop': AU.pop(); break;
    }
  }
  // ---- the cards ----
  let UI = null;
  const STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1.5l2.6 7.2 7.6.3-6 4.7 2.1 7.3L12 16.7 5.7 21l2.1-7.3-6-4.7 7.6-.3z"/></svg>';
  function buildUi() {
    const el = document.createElement('div'); el.className = 'flui'; el.id = 'flUi';
    const steps = n => '<div class="flsteps" aria-hidden="true">' + [0, 1, 2].map(i => '<i class="' + (i < n ? 'done' : i === n ? 'on' : '') + '"></i>').join('') + '</div>';
    const irises = EYE_KEYS.map(k => '<button type="button" class="fliri" data-i="' + k + '" style="--ic:' + EYE_COLS[k].css + '" aria-label="' + EYE_COLS[k].name + ' eyes" aria-pressed="' + (myLook.iris === k) + '"><i></i></button>').join('');
    const styles = ['round', 'edgy', 'dot'].map(k => '<button type="button" class="flsty" data-s="' + k + '" aria-pressed="' + ((myLook.eyes || 'round') === k) + '">' + ES_ICON_T[k] + '<b>' + EYE_STYLES[k] + '</b></button>').join('');
    const paints = PALETTE.map(c => '<button type="button" class="flpai" data-c="' + c.id + '" style="--c:#' + c.hex.toString(16).padStart(6, '0') + '" aria-label="' + c.name + '" aria-pressed="false"><i></i></button>').join('');
    el.innerHTML = '<section class="card flcard" id="flEyes" hidden aria-labelledby="flEyesT">' + steps(0) + '<h2 class="ctitle" id="flEyesT">Pick your eyes</h2>'
      + '<div class="flrow"><span class="lhead">Color</span><div class="flirs" id="flIris">' + irises + '</div></div>'
      + '<div class="flrow"><span class="lhead">Style</span><div class="flstys" id="flStyle">' + styles + '</div></div>'
      + '<button class="btn play sm" type="button" id="flEyesGo">Next</button></section>'
      + '<section class="card flcard" id="flPaint" hidden aria-labelledby="flPaintT">' + steps(1) + '<h2 class="ctitle" id="flPaintT">Pick your paint</h2>'
      + '<div class="flpais" id="flPais">' + paints + '</div><p class="flpn" id="flPn">Tap a color</p>'
      + '<button class="btn play sm" type="button" id="flPaintGo" disabled>Next</button></section>'
      + '<form class="card flcard" id="flName" hidden autocomplete="off" aria-labelledby="flNameT">' + steps(2) + '<h2 class="ctitle" id="flNameT">Name your star</h2><p class="cnote">It goes up in lights when you win.</p>'
      + '<div class="namefield"><input id="flNameIn" type="text" size="8" maxlength="12" autocomplete="off" autocapitalize="words" autocorrect="off" spellcheck="false" enterkeyhint="go" aria-label="Your name">'
      + '<button class="dice" id="flDice" type="button" aria-label="Pick a random name"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="8.5" cy="8.5" r="1.6"/><circle cx="15.5" cy="15.5" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="15.5" cy="8.5" r="1.6"/><circle cx="8.5" cy="15.5" r="1.6"/></svg></button></div>'
      + '<button class="btn play sm" type="submit" id="flNameGo">Let’s roll</button></form>'
      + '<div class="flwink" id="flWink" hidden>' + STAR + '</div>';
    stage.appendChild(el); UI = { el, cur: null };
    $('flIris').addEventListener('click', e => { const b = e.target.closest('.fliri'); if (!b) return; AU.init(); pickIris(b.dataset.i); });
    $('flStyle').addEventListener('click', e => { const b = e.target.closest('.flsty'); if (!b) return; AU.init(); pickStyle(b.dataset.s); });
    $('flPais').addEventListener('click', e => { const b = e.target.closest('.flpai'); if (!b) return; AU.init(); pickPaint(b.dataset.c); });
    $('flEyesGo').addEventListener('click', () => { AU.init(); AU.ui(); go('paint'); });
    $('flPaintGo').addEventListener('click', () => { AU.init(); AU.ui(); go('form'); });
    $('flDice').addEventListener('click', () => { AU.init(); AU.pop(); const i = $('flNameIn'); i.value = randomName(); kick($('flDice'), 'bump'); });
    $('flName').addEventListener('submit', e => { e.preventDefault(); AU.init(); AU.ui(); try { $('flNameIn').blur(); } catch (x) {} setTimeout(() => window.scrollTo(0, 0), 60); go('wink'); });
  }
  function card(id) {
    const nu = id ? $(id) : null, old = UI.cur; if (old === nu) return;
    if (old) { old.classList.add('out'); setTimeout(() => { if (UI && UI.cur !== old) old.hidden = true; old.classList.remove('out'); }, 320); }
    UI.cur = nu; free = null; if (nu) { nu.hidden = false; nu.classList.remove('out'); void nu.offsetWidth; nu.classList.add('in'); }
  }
  // ---- the picks ----
  function pickIris(k) {
    if (!EYE_COLS[k]) return; myLook.iris = k; X.I.setIris && X.I.setIris(EYE_COLS[k].lin); for (const b of $('flIris').children) b.setAttribute('aria-pressed', String(b.dataset.i === k));
    X.I.blink && X.I.blink(); X.ch.pop = 1; snd('pop'); ripple(X.ch.x, X.ch.z, 0.35); X.picks.iris++; AU.flm.layer(Math.max(1, AU.flm.lay));
  }
  function pickStyle(k) {
    myLook.eyes = k; X.I.setEyeStyle && X.I.setEyeStyle(EYE_STYLE_K[k] || 0); for (const b of $('flStyle').children) b.setAttribute('aria-pressed', String(b.dataset.s === k));
    $('flIris').classList.toggle('off', NO_IRIS(k)); X.I.flutter && X.I.flutter(3); X.ch.pop = 1.4; snd('pop'); ripple(X.ch.x, X.ch.z, 0.5); X.picks.style++; AU.flm.layer(2);
  }
  function pickPaint(id) {
    const c = PALETTE.find(p => p.id === id); if (!c) return; X.paintTo = new THREE.Color(c.hex); X.paintId = id; X.pearlTo = 0;
    setColor(id); X.I.setColor && X.I.setColor(new THREE.Color(c.hex));
    for (const b of $('flPais').children) b.setAttribute('aria-pressed', String(b.dataset.c === id)); $('flPn').textContent = c.words[0]; $('flPaintGo').disabled = false;
    // a splash of it: the puddle heaves and throws up a few drops
    for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283, s = rnd(0.5, 1.4); spawn(new V3(X.ch.x + Math.cos(a) * 0.25, 0.03, X.ch.z + Math.sin(a) * 0.25), new V3(Math.cos(a) * s, rnd(1.5, 2.8), Math.sin(a) * s), rnd(0.012, 0.024), new THREE.Color(c.hex)); }
    ripple(X.ch.x, X.ch.z, 0.8); snd('splat', 0.7); X.ch.pop = 1.2; X.I.blink && X.I.blink(); buzz(10);
  }
  // ---- the story ----
  function go(ph) {
    if (!X || X.ph === ph) return; X.ph = ph; X.pt = 0; X.flags = {};
    if (ph === 'eyes') { shot('eyes'); card('flEyes'); AU.flm.layer(1); }
    else if (ph === 'paint') { AU.flm.layer(2); shot('paint'); card('flPaint'); }
    else if (ph === 'form') { if (!X.paintId) pickPaint(colorId); card(null); AU.flm.layer(3); shot('form'); }
    else if (ph === 'name') { shot('name'); card('flName'); const i = $('flNameIn'); i.value = cleanName(store.name) || randomName(); AU.flm.layer(4); }
    else if (ph === 'wink') { card(null); shot('exit'); store.name = cleanName($('flNameIn').value) || randomName(); X.hitIn = AU.flm.sting(2.4); }
  }
  // where it is, and how it moves, by the phase
  function story(dt) {
    const c = X.ch, t = X.pt, F = X.flags, once = k => F[k] ? false : (F[k] = true), I = X.I;
    c.air = false; c.sq = 0; c.rise = 0; c.curl = 0; let wy = 0, wp = 0.06;
    if (X.ph === 'wait') { tiltAt(0); return; }
    if (X.ph === 'barrel') {
      // it rocks one way, the other, harder, and over it goes
      const W = [[0.5, 1.12, -0.14], [1.12, 1.74, 0.17], [1.74, 2.36, -0.22]]; let a = 0;
      for (const [s, e, m] of W) if (t >= s && t < e) a = m * Math.sin(Math.PI * (t - s) / (e - s));
      if (t >= 2.5 && t < 3.12) a = (Math.PI / 2) * eIn((t - 2.5) / 0.62);
      if (t >= 3.12) { const u = t - 3.12; a = Math.PI / 2 - 0.16 * Math.abs(Math.sin(u * 9)) * Math.exp(-u * 5.5); }
      tiltAt(a);
      if (t >= 0.5 && once('w1')) snd('wobble', 0.75); if (t >= 1.12 && once('w2')) snd('wobble', 0.85); if (t >= 1.74 && once('w3')) snd('wobble', 1);
      if (t >= 2.3 && once('s1')) shot('tip');
      if (t >= 3.1 && once('thud')) { snd('tip', 1); X.cs.shake = 1; buzz([10, 30, 20]); popLid(); }
      if (t >= 3.2) { const u = (t - 3.2) / 2.8; X.R = 0.95 * eOut(u); X.MR = u < 1 ? 0.2 * (1 - 0.4 * u) : Math.max(0, 0.12 - (t - 6) * 0.08); }
      if (t >= 3.22 && once('pour')) snd('pour', 0.9);
      streamAt(t);
      // the eyes come up out of it and look about
      if (t >= 6.2 && once('pop')) { X.hold.visible = true; snd('eyes', 1); ripple(c.x, c.z, 1); I.face && I.face('startle', 0.6); }
      const up = t < 6.2 ? 0 : 1 - Math.exp(-(t - 6.2) * 7) * Math.cos((t - 6.2) * 15);
      c.y = -0.9 + (eyeY() + 0.9) * up;
      if (t > 6.9 && t < 7.6) wy = 0.7; else if (t >= 7.6 && t < 8.4) wy = -0.7; else wy = 0;
      if (t >= 6.95 && once('l1')) I.face && I.face('curious', 1.2);
      if (t >= 8.4 && once('bl')) I.blink && I.blink();
      if (t >= 8.2 && once('zoom')) shot('eyes');
      if (t >= 9.0) go('eyes');
    }
    if (X.ph === 'eyes' || X.ph === 'paint') {
      tiltAt(Math.PI / 2); c.y += (eyeY() - c.y) * Math.min(1, dt * 6);
      wy = Math.sin(X.t * 0.6) * 0.25 + Math.sin(X.t * 1.7) * 0.06; wp = 0.08;
    }
    if (X.ph === 'form') {
      tiltAt(Math.PI / 2);
      // it gathers itself up out of the paint, crouches, and jumps clear
      if (once('f0')) { snd('form', 1); I.face && I.face('focus', 1.2); }
      const ru = eOut(t / 0.9); c.y = eyeY() + (PR - eyeY()) * ru; c.wade = 1;
      if (t < 0.9 && Math.random() < dt * 30) { const a = Math.random() * 6.283; spawn(new V3(c.x + Math.cos(a) * 0.2, 0.02, c.z + Math.sin(a) * 0.2), new V3(Math.cos(a) * 0.4, rnd(0.8, 1.6), Math.sin(a) * 0.4), rnd(0.01, 0.02)); }
      if (t > 0.95 && t < 1.2) c.sq = 0.35 * Math.sin((t - 0.95) / 0.25 * Math.PI);
      const J0 = 1.2, J1 = 1.95;
      if (t >= J0 && once('jump')) { AU.jump && AU.jump(); AU.vox && AU.vox('hyah', 0.8); ripple(c.x, c.z, 1); for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283, s = rnd(0.6, 1.6); spawn(new V3(c.x + Math.cos(a) * 0.2, 0.04, c.z + Math.sin(a) * 0.2), new V3(Math.cos(a) * s, rnd(2, 3.4), Math.sin(a) * s), rnd(0.014, 0.028)); } }
      if (t >= J0 && t < J1) { const u = (t - J0) / (J1 - J0), H = 0.85; c.x = C0.x + (LAND.x - C0.x) * u; c.z = C0.z + (LAND.z - C0.z) * u; c.h = 4 * H * u * (1 - u); c.y = PR + c.h; c.vy = 4 * H * (1 - 2 * u) / (J1 - J0); c.air = true; c.rise = u < 0.5 ? 0.6 : 0.2;
        if (Math.random() < dt * 25) spawn(new V3(c.x, c.y - 0.1, c.z), new V3(rnd(-0.3, 0.3), -0.5, rnd(-0.3, 0.3)), rnd(0.01, 0.018)); }
      if (t >= J1) { c.x = LAND.x; c.z = LAND.z; c.y = PR; c.h = 0; const k = t - J1; c.sq = Math.max(0, 0.5 * Math.exp(-k * 7) * Math.cos(k * 16)); }
      if (t >= J1 && once('land')) { AU.land && AU.land(0.9); snd('splat', 1.1); X.cs.shake = 0.7; buzz(18); splat(LAND.x, LAND.z, 0.24); for (let i = 0; i < 18; i++) { const a = i / 18 * 6.283, s = rnd(1, 2); spawn(new V3(LAND.x + Math.cos(a) * 0.2, 0.04, LAND.z + Math.sin(a) * 0.2), new V3(Math.cos(a) * s, rnd(1, 2.2), Math.sin(a) * s), rnd(0.01, 0.022)); } }
      // and shakes the paint off
      if (t >= J1 + 0.38 && once('shake')) { I.shake && I.shake(1); I.coatBurst && I.coatBurst(0.16); AU.vox && AU.vox('brr', 0.6); }
      if (t >= J1 + 0.3) c.wade = Math.max(0.25, c.wade - dt * 1.5);
      if (t >= J1 + 1.45) go('name');
    }
    if (X.ph === 'name') { c.x = LAND.x; c.z = LAND.z; c.y = PR; wy = Math.sin(X.t * 0.5) * 0.12; wp = 0.12;
      if (Math.floor(X.t / 3.3) !== X.flags.gl) { X.flags.gl = Math.floor(X.t / 3.3); if (X.flags.gl % 3 === 2) { X.ch.pop = 0.7; I.blink && I.blink(); } } }
    if (X.ph === 'wink') {
      c.h = c.air ? c.h : 0;
      const hit = X.hitIn || 2.4, jumpAt = Math.max(1.3, hit - 0.95), irisAt = Math.max(jumpAt + 0.42, hit - 0.42);
      if (once('w')) { I.face && I.face('smirk', Math.max(1.4, jumpAt - 0.1)); }
      if (t >= 0.2 && once('tw')) { snd('sparkle', 0.9); twinkle(); }
      if (t < jumpAt) { c.x = LAND.x; c.z = LAND.z; c.y = PR; wy = 0; wp = 0.1; if (t > jumpAt - 0.22) c.sq = 0.35 * Math.sin((t - jumpAt + 0.22) / 0.22 * Math.PI); }
      else { const u = (t - jumpAt) / 0.75, H = 0.95; c.yaw += (2.2 - c.yaw) * Math.min(1, dt * 10); c.x = LAND.x + u * 2.9; c.z = LAND.z - u * 2.2; c.h = 4 * H * u * (1 - u); c.y = PR + Math.max(-0.6, c.h); c.vy = 4 * H * (1 - 2 * u) / 0.75; c.air = true; c.rise = 0.5;
        if (once('j')) { AU.jump && AU.jump(); AU.vox && AU.vox('whee', 0.8); } }
      if (t >= irisAt && once('iris')) handoff();
    }
    c.wy += (wy - c.wy) * Math.min(1, dt * 5); c.wp += (wp - c.wp) * Math.min(1, dt * 5);
    // the paint's colour, easing to the one picked
    if (X.paintTo) { X.paint.lerp(X.paintTo, Math.min(1, dt * 5)); X.pearl += (X.pearlTo - X.pearl) * Math.min(1, dt * 4); }
  }
  const eyeY = () => -0.3; // (sunk to its eyes: the top of its head, its eyes and its ears out of the paint)
  function tiltAt(a) {
    // the barrel rocks on the edge of its base it leans toward (lying down, it rests on its widest part)
    const B = X.barrel.g, sg = a >= 0 ? 1 : -1, piv = BR.base.clone().addScaledVector(TIP, sg * BR.Rb);
    _q.setFromAxisAngle(TIPAX, a); const rel = BR.base.clone().sub(piv).applyQuaternion(_q);
    B.position.copy(piv).add(rel); B.position.y += (BR.Rm - BR.Rb) * Math.pow(Math.max(0, Math.sin(a)), 6); B.quaternion.copy(_q); X.tilt = a;
    const U = X.floor.U, k = Math.abs(Math.sin(a)); U.uShB.value.set(B.position.x, B.position.z, BR.H * k, 0.3 + 0.08 * k); U.uShD.value.set(TIP.x * sg, TIP.z * sg);
    B.updateMatrixWorld(true); X.mouth.set(0, BR.H, 0).applyMatrix4(B.matrixWorld);
  }
  function popLid() { const L = X.lid, m = X.barrel.lid; m.updateMatrixWorld(); m.getWorldPosition(L.p); X.barrel.g.remove(m); X.sc.add(m); m.position.copy(L.p); m.quaternion.copy(X.barrel.g.quaternion); L.on = false; L.v.set(TIP.x * 1.6 + 0.4, 1.6, TIP.z * 1.6 + 0.5); L.w.set(rnd(-6, 6), rnd(-3, 3), rnd(4, 9)); }
  function lidTick(dt) {
    const L = X.lid; if (L.on || L.rest) return; const m = X.barrel.lid;
    L.v.y -= 9 * dt; m.position.addScaledVector(L.v, dt); m.rotation.x += L.w.x * dt; m.rotation.z += L.w.z * dt;
    if (m.position.y < 0.02) { m.position.y = 0.02; if (Math.abs(L.v.y) > 0.8) { L.v.y = -L.v.y * 0.35; L.v.x *= 0.6; L.v.z *= 0.6; L.w.multiplyScalar(0.5); AU.bonk && AU.bonk(); } else { L.rest = true; m.rotation.set(0, m.rotation.y, 0); } }
  }
  function streamAt(t) {
    const S = X.stream, U = S.U; if (t < 3.15 || t > 6.4) { S.m.visible = false; return; } S.m.visible = true;
    U.uP0.value.copy(X.mouth); U.uV0.value.copy(TIP).multiplyScalar(0.9 * (1 - 0.6 * clamp((t - 4.8) / 1.4, 0, 1))); U.uV0.value.y = 0.15;
    const dy = X.mouth.y; U.uT.value = Math.sqrt(2 * dy / 9 + 0.0001) + 0.02;
    U.uR.value = 0.075 * Math.min(1, (t - 3.15) / 0.12) * (1 - 0.5 * clamp((t - 5) / 1.3, 0, 1)); U.uCut.value = clamp((t - 5.95) / 0.4, 0, 1);
    const g = new V3().copy(X.mouth).addScaledVector(U.uV0.value, U.uT.value); X.floor.U.uM.value.set(g.x, g.z);
    if (Math.random() < 0.5) ripple(g.x, g.z, 0.15);
  }
  function twinkle() {
    const w = $('flWink'), I = X.I; if (!w || !X.CH.headTop) return; const v = new V3(); X.CH.headTop(I, v, null, 0.55); X.hold.updateMatrixWorld(true); v.applyMatrix4(X.hold.matrixWorld);
    v.x += 0.06; v.project(X.pc); const x = (v.x * 0.5 + 0.5) * viewW, y = (0.5 - v.y * 0.5) * viewH;
    w.style.left = x.toFixed(0) + 'px'; w.style.top = y.toFixed(0) + 'px'; w.hidden = false; w.classList.remove('go'); void w.offsetWidth; w.classList.add('go');
  }
  // the character: its place, its pose (the game's own animator does the rest)
  function charTick(dt) {
    const c = X.ch, I = X.I, o = X.o, h = X.hold;
    c.pop = Math.max(0, (c.pop || 0) - dt * 3); const bob = c.pop > 0 ? Math.sin((1 - c.pop / 1.4) * Math.PI) * 0.03 * c.pop : 0;
    h.position.set(c.x, c.y + bob, c.z); h.rotation.y = c.yaw; h.updateMatrixWorld(true);
    o.dt = dt; o.inAir = c.air; o.vy = c.vy; o.height = c.air ? c.h : 0; o.lean = 0; o.spd = 0; o.speed = 0; o.squash = c.sq; o.rise = c.rise; o.leap = c.air; o.curl = 0; o.blob = 0;
    o.wt.yaw = c.wy; o.wt.pitch = c.wp + 0.85; o.watch = o.wt; o.headRoll = 0; o.headPitch = 0; o.shove = 0; o.push = 0; o.earCover = 0; o.wave = 0; o.climb = null; o.D = null; o.maxBall = 1;
    if (I.setPaint) I.setPaint(X.paint); if (I.setWade) I.setWade(c.wade);
    X.CH.update(I, o);
    // its rim and fin light from the intro's own key light, seen from the intro's camera
    if (I.ax && I.ax.look) { I.ax.look.U.uKeyDir.value.copy(X.key.position).sub(X.key.target.position).normalize().transformDirection(X.pc.matrixWorldInverse); }
    const U = X.floor.U; U.uShC.value.set(c.x, c.z, 0.26 * (1 + c.h * 0.3), X.hold.visible && c.y > -0.05 ? clamp(1 - c.h * 0.5, 0.25, 1) : 0);
    U.uHole.value.set(c.x, c.z, 0.17, X.hold.visible && c.y < PR * 0.9 && !c.air && Math.hypot(c.x - C0.x, c.z - C0.z) < 0.3 ? 1 - clamp((c.y - eyeY()) / (PR - eyeY()), 0, 1) * 0.6 : 0);
  }
  // ---- each frame ----
  function frame(rdt) {
    if (!X) return false; const dt = Math.min(0.05, rdt); X.t += dt; X.pt += dt;
    if (X.ph === 'wait' && X.ready) go('barrel');
    if (AU.flm) AU.flm.wake();
    story(dt); camTick(dt); lidTick(dt); dropsTick(dt); charTick(dt);
    const U = X.floor.U, W = viewW, H = viewH; U.uT.value = X.t; U.uR.value = X.R; U.uMR.value = X.MR; U.uCol.value.copy(X.paint); U.uPearl.value = X.pearl; U.uKey.value.copy(X.key.position).sub(X.key.target.position).normalize();
    X.stream.U.uTime.value = X.t; X.stream.U.uCol.value.copy(X.paint); X.stream.U.uPearl.value = X.pearl; X.beam.U.uT.value = X.t; X.beam.U.uPx.value = renderer.getPixelRatio() * H / 780; X.bgU.uT.value = X.t; X.bgU.uRes.value.set(W, H);
    renderer.setRenderTarget(null); renderer.render(X.bg, X.bgCam);
    const ac = renderer.autoClear; renderer.autoClear = false; renderer.clearDepth(); renderer.render(X.sc, X.pc); renderer.autoClear = ac;
    return true;
  }
  // ---- the hand-over: dark, the lobby set up behind it, then the iris opens on it as the sting hits, and in it jumps ----
  function handoff() {
    const ok = irisClose(() => {
      // what was picked is yours now
      store.introDone = 1; store.color = colorId; saveLook(); save(); paintName();
      api.live = false; document.body.classList.remove('flon'); window.removeEventListener('keydown', keyStop, true);
      if (UI) { UI.el.remove(); UI = null; } dispose();
      try { showMenu(); } finally { api.hush = false; } camSnap = true; if (AU.state !== 'running') AU.music('menu'); // (no sound yet: the song starts as usual when it does)
      api.jin = { t: 0, x0: 0, hop: 0, sq: 0, rise: 0, landed: false };
      irisOpen(); setTimeout(() => { if (AU.flm) AU.flm.end(); }, 6000);
    });
    if (!ok) X.flags.iris = false;
  }
  // in from the side of the lobby: a leap that lands on its spot
  const JIN_T = 0.9, JIN_AT = 0.12; // (how long the leap takes, and a beat of the iris opening before it)
  function after(rdt) {
    const J = api.jin; if (!J) return;
    J.t += Math.min(0.05, rdt); const u = (J.t - JIN_AT) / JIN_T;
    // (from the camera as it is now, every frame: off the left edge of what's in view, and a leap a good part of the view's height)
    camera.updateMatrixWorld(); const e = camera.matrixWorld.elements, d = camera.position.distanceTo(drop.position), hh = Math.tan(camera.fov * Math.PI / 360) * d;
    J.r = (J.r || new V3()).set(e[0], e[1], e[2]).normalize(); J.x0 = -(hh * camera.aspect + 0.9);
    if (u < 1) { const k = Math.max(0, u); J.hop = 4 * Math.min(1.1, hh * 0.5) * k * (1 - k); J.sq = 0; J.rise = k < 0.5 ? 0.6 : 0.2; drop.position.addScaledVector(J.r, J.x0 * (1 - k)); } // (across at an even pace, as a leap goes)
    else { if (!J.landed) { J.landed = true; AU.land && AU.land(0.8); AU.splat(0.9); buzz(16); try { addSplat(P.x, P.y, P.z, P.yaw, 0.9, -8, false, false, 0); for (let i = 0; i < 14; i++) { const a = i / 14 * 6.283; spawnPart(P.x, P.y + 0.3, P.z, Math.cos(a) * 2.2, 2 + Math.random() * 1.6, Math.sin(a) * 2.2, 0.5, teamMats[0], 0.7); } } catch (e) {} }
      const k = J.t - JIN_AT - JIN_T; J.hop = 0; J.rise = 0; J.sq = Math.max(0, 0.5 * Math.exp(-k * 7) * Math.cos(k * 16)); if (k > 0.9) api.jin = null; }
  }
  // keys go to the cards while it runs (Enter mustn't start a match from the lobby behind it)
  function keyStop(e) { if (api.live) e.stopPropagation(); }
  api.boot = () => {
    document.body.classList.add('flon'); api.live = true; window.addEventListener('keydown', keyStop, true);
    build(); buildUi(); AU.flm.load(); AU.music('intro');
    const start = () => { X.ready = true; AU.flm.play(); };
    const orient = () => { if (store.orient) return start(); openOrient(); const w = setInterval(() => { if ($('orient').hidden) { clearInterval(w); start(); } }, 120); };
    if (bootHold) { const w = setInterval(() => { if (!bootHold) { clearInterval(w); orient(); } }, 100); } else orient();
  };
  api.frame = rdt => api.live && !!X && frame(rdt);
  api.after = after;
  api.busy = () => api.live || !!api.jin;
  api.go = ph => go(ph); // (for tests: straight to a phase)
  api.peek = () => X ? { ph: X.ph, pt: X.pt, t: X.t, hit: X.hitIn || 0, lay: AU.flm ? AU.flm.lay : 0, drops: X.drop.length, calls: renderer.info.render.calls, tris: renderer.info.render.triangles } : null; // (for tests: where it's got to)
  return api;
})();
