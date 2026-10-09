# Two new stages: Palette Island (sun, sand and sea) and Blank Canvas (a white world). Textures, themes, sky, sea, far scenery, birds
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:100], c)
    s = s.replace(a, b)

# ---------- sky: day themes hide the stars and the moon and show a high sun ----------
rep("""rain: { value: 0 }, heat: { value: 0 }, day: { value: 0 }, uTime: { value: 0 }, moonDir: { value: MOON_DIR.clone() }, sunDir: { value: SUN_DIR } };""",
    """rain: { value: 0 }, heat: { value: 0 }, day: { value: 0 }, uTime: { value: 0 }, moonDir: { value: MOON_DIR.clone() }, sunDir: { value: SUN_DIR }, dayBase: { value: 0 }, sunAmt: { value: 0 }, sunHi: { value: new THREE.Vector3(16, 30, 9).normalize() } };""")
rep("""  fragmentShader: `uniform vec3 top, mid, hor, low, moonDir, sunDir; uniform float rain, heat, day, uTime; varying vec3 vD;""",
    """  fragmentShader: `uniform vec3 top, mid, hor, low, moonDir, sunDir, sunHi; uniform float rain, heat, day, uTime, dayBase, sunAmt; varying vec3 vD;""")
rep("""    c += vec3(1.0, 0.94, 0.86) * st * (0.6 + 0.8 * step(0.996, h)) * (1.0 - smoothstep(0.0, 0.6, day)) * (1.0 - rain);""",
    """    c += vec3(1.0, 0.94, 0.86) * st * (0.6 + 0.8 * step(0.996, h)) * (1.0 - smoothstep(0.0, 0.6, day)) * (1.0 - rain) * (1.0 - dayBase);""")
rep("""    float night = (1.0 - day) * (1.0 - rain * 0.75);
    c += vec3(0.78, 0.74, 1.0) * glow * night;
    c = mix(c, moonC, disc * (1.0 - day * 0.85) * (1.0 - rain * 0.6));""", """    float night = (1.0 - day) * (1.0 - rain * 0.75) * (1.0 - dayBase);
    c += vec3(0.78, 0.74, 1.0) * glow * night;
    c = mix(c, moonC, disc * (1.0 - day * 0.85) * (1.0 - rain * 0.6) * (1.0 - dayBase));
    // a day sky's sun, high up: a white disc in a warm glow (the burning sun later turns it all gold)
    float sh = dot(d, sunHi); c += vec3(1.0, 0.97, 0.88) * (smoothstep(0.9992, 0.9995, sh) * 1.6 + pow(max(sh, 0.0), 60.0) * 0.32 + pow(max(sh, 0.0), 6.0) * 0.1) * sunAmt * (1.0 - rain);""")

# ---------- textures ----------
rep("""const THEMES = [""", """// Palette Island: wind-rippled sand flecked with shell, and sun-bleached boardwalk planks
const sandTex = makeTex(256, (g, S) => { const r = rng(41); g.fillStyle = '#E9D2A2'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 26; i++) { const y0 = r() * S, a = 3 + r() * 5, k = 1 + (r() * 2 | 0), ph = r() * 6.28, w = 2 + r() * 3;
    for (const [col, dy] of [[`rgba(${176 + r() * 20 | 0},${136 + r() * 20 | 0},${88 + r() * 14 | 0},${0.16 + r() * 0.12})`, 0], ['rgba(255,247,226,0.22)', -2.5]]) { g.strokeStyle = col; g.lineWidth = w; for (const off of [-S, 0, S]) { g.beginPath(); for (let x = 0; x <= S; x += 4) { const y = y0 + off + dy + Math.sin(x / S * 6.2832 * k + ph) * a; x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); } } }
  specks(g, S, r, 1700, k => k < 0.5 ? `rgba(150,112,70,${0.16 + k * 0.3})` : `rgba(255,250,236,${0.2 + k * 0.3})`);
  for (let i = 0; i < 26; i++) { const x = r() * S, y = r() * S, col = ['rgba(255,232,224,0.9)', 'rgba(250,246,236,0.9)', 'rgba(200,190,180,0.85)'][i % 3]; wrapAt(S, x, y, 6, (X, Y) => { g.fillStyle = col; g.beginPath(); g.ellipse(X, Y, 2 + r() * 2, 1.2 + r() * 1.2, r() * 3, 0, 6.2832); g.fill(); }); } });
const plankTex = makeTex(256, (g, S) => { const r = rng(42), rows = 6, h = S / rows; g.fillStyle = '#5E4630'; g.fillRect(0, 0, S, S);
  for (let j = 0; j < rows; j++) { let x = -r() * S * 0.4; while (x < S) { const L = S * (0.35 + r() * 0.5), l = r(), col = `rgb(${178 + l * 40 | 0},${150 + l * 34 | 0},${112 + l * 30 | 0})`;
      for (const off of [-S, 0, S]) { g.fillStyle = col; g.fillRect(x + off + 1.5, j * h + 2, L - 3, h - 4); g.strokeStyle = 'rgba(110,84,56,0.3)'; g.lineWidth = 1; for (let k = 0; k < 3; k++) { const gy = j * h + 5 + r() * (h - 10); g.beginPath(); g.moveTo(x + off + 4, gy); g.lineTo(x + off + L - 4, gy + (r() - 0.5) * 3); g.stroke(); } g.fillStyle = 'rgba(70,52,36,0.6)'; g.beginPath(); g.arc(x + off + 7, j * h + h / 2, 1.6, 0, 6.2832); g.arc(x + off + L - 7, j * h + h / 2, 1.6, 0, 6.2832); g.fill(); }
      x += L; } }
  specks(g, S, r, 500, k => `rgba(255,255,255,${0.04 + k * 0.08})`); });
// the Blank Canvas: plain white with the faintest drafting grid, and white panels
const blankTex = makeTex(256, (g, S) => { const r = rng(43); g.fillStyle = '#F4F4F1'; g.fillRect(0, 0, S, S);
  specks(g, S, r, 900, k => `rgba(150,150,160,${0.03 + k * 0.05})`);
  g.strokeStyle = 'rgba(120,124,140,0.13)'; g.lineWidth = 1.5; for (let k = 0; k <= 4; k++) { const v = k * S / 4; g.beginPath(); g.moveTo(v, 0); g.lineTo(v, S); g.stroke(); g.beginPath(); g.moveTo(0, v); g.lineTo(S, v); g.stroke(); }
  g.strokeStyle = 'rgba(120,124,140,0.06)'; g.lineWidth = 1; for (let k = 0; k < 16; k++) { const v = (k + 0.5) * S / 16; g.beginPath(); g.moveTo(v, 0); g.lineTo(v, S); g.stroke(); g.beginPath(); g.moveTo(0, v); g.lineTo(S, v); g.stroke(); } });
const blankSideTex = makeTex(256, (g, S) => { const r = rng(44); g.fillStyle = '#F1F1EE'; g.fillRect(0, 0, S, S);
  specks(g, S, r, 700, k => `rgba(150,150,160,${0.03 + k * 0.05})`);
  g.fillStyle = 'rgba(120,124,140,0.12)'; for (let k = 0; k < 4; k++) g.fillRect(0, k * S / 4, S, 2); g.fillStyle = 'rgba(255,255,255,0.5)'; for (let k = 0; k < 4; k++) g.fillRect(0, k * S / 4 + 2, S, 2); });
const THEMES = [""")
rep("""const THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));""", """THEMES.push(
  { id: 'island', label: 'Palette Island', floor: () => sandTex, side: () => plankTex, uv: 0.3, ft: 0xB2B2B2, st: 0xB0B0B0, dt: 0x8E8E8E, hor: 0xC4E8F4, sky: [0x2B7FD4, 0x6CB6EE, 0xCDEEFA], low: 0x7CC3DA, hemi: [0xD6ECFF, 0xD9C59C], kit: { column: [1, 3], drum: [1, 2], rpad: [0, 1], rotunda: [0, 1] }, fill: 'drum', pot: 'can',
    day: true, sun: 1, sea: true, base: { hemiI: 0.6, key: 0xFFF2DC, keyI: 0.8 }, env: { top: 0x2E5478, hor: 0x76949E, gnd: 0x8A7A5C, sun: 0xFFF2DC, sunK: 1.0 }, lk: { hemi: 0.32, key: 1.12 }, grade: { sat: 1.1, con: 1.06, vig: 0.16, bloom: 0.38, th: 0.86, tint: [1.02, 1.0, 0.97] }, jglow: 0.55, trim: { c: 0x8C6A48, m: 0, r: 0.62 }, nrm: [0.7, 1.0], rough: [0.92, 0.8], cloud: 0xFFFFFF },
  { id: 'blank', label: 'Blank Canvas', floor: () => blankTex, side: () => blankSideTex, uv: 0.25, ft: 0xBBBBBB, st: 0xB8B8B8, dt: 0xA2A2A2, hor: 0xEDEFF3, sky: [0xD5DAE3, 0xE7E9EE, 0xF7F8FA], low: 0xEEF0F3, hemi: [0xFFFFFF, 0xC4C7D0], kit: { column: [1, 2], drum: [1, 2], rpad: [0, 1], rotunda: [0, 1] }, fill: 'drum', pot: 'can',
    day: true, sun: 0.25, base: { hemiI: 0.82, key: 0xFFFFFF, keyI: 0.55 }, env: { top: 0x6C6E74, hor: 0x84868C, gnd: 0x5A5C62, sun: 0xFFFFFF, sunK: 0.3 }, lk: { hemi: 0.32, key: 0.95 }, grade: { sat: 1.16, con: 1.05, vig: 0.1, bloom: 0.22, th: 0.93 }, jglow: 0.5, trim: { c: 0xF2F2F0, m: 0, r: 0.5 }, nrm: [0.25, 0.4], rough: [0.6, 0.6], cloud: 0xF7F8FA }
);
const THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));""")
rep("""const CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xC2CAF0, manor: 0xE0C4E2, garden: 0xA6CCC0 };""",
    """const CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xC2CAF0, manor: 0xE0C4E2, garden: 0xA6CCC0, island: 0xFFFFFF, blank: 0xF4F5F8 };""")
rep("""  garden: { cols: [0xD8FF6A, 0xFFF07A, 0xB0FF8A], size: 0.5, rise: 0.04, blink: 1, sway: 1.2 },
};""", """  garden: { cols: [0xD8FF6A, 0xFFF07A, 0xB0FF8A], size: 0.5, rise: 0.04, blink: 1, sway: 1.2 },
  island: { cols: [0xFFF6D8, 0xFFFFFF], size: 0.22, rise: 0.08, blink: 0.3, sway: 0.8 },
  blank: { cols: [0x9FD8FF, 0xFFC0E0, 0xFFE38A], size: 0.26, rise: 0.06, blink: 0.4, sway: 0.7 },
};""")

# ---------- clouds remember their height; the far canvases and the bats can be swapped out ----------
rep("""  const addCloud = (vi, x, y, z, ry, sc, v) => { const m = new THREE.Object3D(); m.position.set(x, y, z); m.rotation.y = ry; m.scale.setScalar(sc); clouds.push({ m, v, vi, k: cvN[vi]++ }); };""",
    """  const addCloud = (vi, x, y, z, ry, sc, v) => { const m = new THREE.Object3D(); m.position.set(x, y, z); m.rotation.y = ry; m.scale.setScalar(sc); clouds.push({ m, v, vi, k: cvN[vi]++, y0: y, layer: clouds.length < 18 ? 0 : 1 }); };""")
rep("""  const r = rng(77), mat = new THREE.MeshBasicMaterial({ color: 0x0C0718, side: THREE.DoubleSide, fog: false });""", """  const r = rng(77), mat = batMat;""")
rep("""const bats = [];""", """const bats = [], batMat = new THREE.MeshBasicMaterial({ color: 0x0C0718, side: THREE.DoubleSide, fog: false });""")
rep("""function updateBats(dt) {
  const on = 1 - Math.min(1, dayK * 1.6);""", """function updateBats(dt) {
  const on = TH.day ? (TH.sea ? 1 : 0) : 1 - Math.min(1, dayK * 1.6); // gulls over the island, nothing over the blank world""")

# ---------- the sea, little islands out on it, and white blocks for the blank world ----------
rep("""// ---------- bats circling out by the moon ----------""", """// ---------- Palette Island: the sea all round it, little islands out on the water ----------
const WATER_Y = -0.42;
const seaU = Object.assign(THREE.UniformsUtils.clone(THREE.UniformsLib.fog), { uTime: { value: 0 }, uA: { value: 26.4 }, uSkyT: { value: new THREE.Color(0x5FA8E8) }, uSkyH: { value: new THREE.Color(0xCDEFFA) }, uSunC: { value: new THREE.Color(1, 0.95, 0.85) }, uSunD: { value: new THREE.Vector3(16, 30, 9).normalize() }, uDeep: { value: new THREE.Color(0x0C6A9A) }, uShal: { value: new THREE.Color(0x3CCFD2) }, uPl: { value: Array.from({ length: 8 }, () => new THREE.Vector2(999, 999)) } });
const seaMat = new THREE.ShaderMaterial({ uniforms: seaU, fog: true, defines: HI ? { HIQ: '' } : {},
  vertexShader: `varying vec3 vW;
  #include <fog_pars_vertex>
  void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
  }`,
  fragmentShader: `uniform float uTime, uA; uniform vec3 uSkyT, uSkyH, uSunC, uSunD, uDeep, uShal; uniform vec2 uPl[8]; varying vec3 vW;
  #include <fog_pars_fragment>
  float sh2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float svn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(sh2(i), sh2(i + vec2(1.0, 0.0)), f.x), mix(sh2(i + vec2(0.0, 1.0)), sh2(i + vec2(1.0, 1.0)), f.x), f.y); }
  float boxD(vec2 p, vec2 c, float h){ vec2 d = abs(p - c) - h; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
  void main(){
    vec2 p = vW.xz; float t = uTime;
    float dA = boxD(p, vec2(0.0), uA), d = abs(dA);
    for (int i = 0; i < 8; i++) d = min(d, max(boxD(p, uPl[i], 1.3), 0.0));
    if (dA < 0.0) d = 0.45; // water under the island, seen through its holes: shallow and calm
    vec3 V = normalize(cameraPosition - vW);
    vec2 g = vec2(0.8, 0.6) * cos(dot(p, vec2(0.8, 0.6)) * 0.55 + t * 1.2) * 0.09 + vec2(-0.5, 0.86) * cos(dot(p, vec2(-0.5, 0.86)) * 0.9 - t * 1.5) * 0.06;
    #ifdef HIQ
    g += vec2(0.96, -0.28) * cos(dot(p, vec2(0.96, -0.28)) * 2.1 + t * 2.3) * 0.035 + (vec2(svn(p * 1.3 + t * 0.4), svn(p * 1.3 - t * 0.35 + 7.0)) - 0.5) * 0.12;
    #endif
    vec3 n = normalize(vec3(-g.x, 1.0, -g.y));
    float fr = 0.02 + 0.98 * pow(1.0 - max(dot(n, V), 0.0), 5.0);
    vec3 R = reflect(-V, n), sky = mix(uSkyH, uSkyT, smoothstep(0.0, 0.5, R.y));
    vec3 base = mix(uShal, uDeep, smoothstep(0.5, 10.0, d)) * (0.86 + 0.14 * svn(p * 0.2 + t * 0.05));
    vec3 col = mix(base, sky, fr * 0.85) + uSunC * pow(max(dot(R, uSunD), 0.0), 220.0) * 2.4;
    // the shoreline: white water hugging the edge, broken up by noise, and lines of surf rolling in
    float nz = svn(p * 2.3 + t * 0.6);
    float foam = smoothstep(0.55, 0.05, d + (nz - 0.5) * 0.35);
    float surf = step(0.72, fract(d * 0.55 - t * 0.28 + nz * 0.3)) * smoothstep(3.2, 0.6, d) * smoothstep(0.35, 0.7, nz);
    col = mix(col, vec3(1.0), clamp(foam * 0.9 + surf * 0.5, 0.0, 1.0));
    gl_FragColor = vec4(col, 1.0);
    #include <fog_fragment>
  }` });
const sea = new THREE.Mesh(new THREE.PlaneGeometry(1500, 1500).rotateX(-Math.PI / 2), seaMat); sea.position.y = WATER_Y; sea.visible = false; scene.add(sea);
const YAX = new THREE.Vector3(0, 1, 0);
function cylBetween(a, b, r0, r1, n) { const d = new THREE.Vector3().subVectors(b, a), L = d.length(), g = new THREE.CylinderGeometry(r1, r0, L, n, 1); g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(YAX, d.normalize())); g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2); return g; }
// a palm frond: a long leaf rising then drooping from the crown, creased down its middle, its edge cut into leaflets
function frondGeo(o, a, L, W, droop) {
  const n = 10, pos = [], idx = [], dir = new THREE.Vector3(Math.cos(a), 0, Math.sin(a)), side = new THREE.Vector3(-Math.sin(a), 0, Math.cos(a)), c = new THREE.Vector3(), e = new THREE.Vector3();
  for (let i = 0; i <= n; i++) { const t = i / n, w = W * Math.sin(Math.PI * Math.min(1, t * 1.12)) * (i % 2 ? 1 : 0.6); c.copy(o).addScaledVector(dir, L * t); c.y += L * (0.3 * t - droop * t * t);
    e.copy(c).addScaledVector(side, -w); pos.push(e.x, e.y - w * 0.15, e.z, c.x, c.y + w * 0.12, c.z); e.copy(c).addScaledVector(side, w); pos.push(e.x, e.y - w * 0.15, e.z); }
  for (let i = 0; i < n; i++) { const a0 = i * 3, b0 = a0 + 3; idx.push(a0, b0, a0 + 1, b0, b0 + 1, a0 + 1, a0 + 1, b0 + 1, a0 + 2, b0 + 1, b0 + 2, a0 + 2); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
// a palm: a leaning trunk of flared rings, a crown of fronds and a few coconuts (geometry in world space, sorted by material)
function palmParts(x, y, z, h, s, lean, rot, R) {
  const trunk = [], fronds = [], nuts = [], n = 7, lx = Math.cos(rot) * lean, lz = Math.sin(rot) * lean, P = t => new THREE.Vector3(x + lx * t * t * h, y + t * h, z + lz * t * t * h);
  for (let k = 0; k < n; k++) { const r0 = s * (0.2 - 0.075 * k / n); trunk.push(cylBetween(P(k / n), P((k + 1) / n), r0, r0 * 1.14, SEG(9))); }
  const top = P(1);
  for (let k = 0; k < 8; k++) fronds.push(frondGeo(top, k / 8 * 6.283 + R() * 0.5, s * (1.45 + R() * 0.5), s * 0.3, 0.85 + R() * 0.35));
  for (let k = 0; k < 3; k++) { const a = k * 2.094 + R(), g = new THREE.SphereGeometry(s * 0.1, 10, 8); g.translate(top.x + Math.cos(a) * s * 0.12, top.y - s * 0.1, top.z + Math.sin(a) * s * 0.12); nuts.push(g); }
  return { trunk, fronds, nuts };
}
const farIsles = new THREE.Group(), farBlocks = new THREE.Group(); farIsles.visible = farBlocks.visible = false; scene.add(farIsles, farBlocks);
let farBuilt = false;
function buildFar() {
  if (farBuilt) return; farBuilt = true;
  const r = rng(808), sandM = toon(0xE6CF9C, null, { roughness: 0.95 }), leafM = toon(0x3F9A50, { side: THREE.DoubleSide }, { roughness: 0.6 }), barkM = toon(0x9A7A56, null, { roughness: 0.9 }), bushM = toon(0x2F8446, null, { roughness: 0.7 }), rockM = toon(0x9A9088, null, { roughness: 0.9 });
  for (let i = 0; i < 9; i++) {
    const a = i / 9 * 6.283 + r() * 0.5, d = 110 + r() * 80, w = 8 + r() * 12, cx = Math.cos(a) * d, cz = Math.sin(a) * d, tr = [], fr = [], nu = [], bu = [];
    const mound = new THREE.Mesh(new THREE.SphereGeometry(1, SEG(22), SEG(10), 0, 6.283, 0, Math.PI / 2), sandM); mound.scale.set(w, w * (0.14 + r() * 0.1), w * (0.65 + r() * 0.4)); mound.position.set(cx, WATER_Y - 0.4, cz); mound.rotation.y = r() * 6.28; farIsles.add(mound);
    if (r() < 0.4) { const rk = new THREE.Mesh(new THREE.DodecahedronGeometry(w * 0.22, 1), rockM); rk.position.set(cx + (r() - 0.5) * w * 0.6, WATER_Y + w * 0.06, cz + (r() - 0.5) * w * 0.4); rk.scale.set(1, 0.7, 1); farIsles.add(rk); }
    for (let k = 0, np = 1 + (r() * 3 | 0); k < np; k++) { const px = cx + (r() - 0.5) * w * 0.7, pz = cz + (r() - 0.5) * w * 0.4, P = palmParts(px, WATER_Y + w * 0.08, pz, 4 + r() * 3.5, 2.2 + r() * 0.8, 0.12 + r() * 0.25, r() * 6.28, r); tr.push(...P.trunk); fr.push(...P.fronds); nu.push(...P.nuts); }
    for (let k = 0; k < 3; k++) { const g = new THREE.SphereGeometry(w * (0.1 + r() * 0.06), 12, 8); g.scale(1, 0.7, 1); g.translate(cx + (r() - 0.5) * w * 0.8, WATER_Y + w * 0.1, cz + (r() - 0.5) * w * 0.5); bu.push(g); }
    farIsles.add(new THREE.Mesh(mergeGeos(tr), barkM), new THREE.Mesh(mergeGeos(fr), leafM), new THREE.Mesh(mergeGeos(nu), barkM), new THREE.Mesh(mergeGeos(bu), bushM));
  }
  // the blank world: plain white blocks and drums floating off in the haze, waiting for paint
  const wm = toon(0xF2F2F0, null, { roughness: 0.8 });
  for (let i = 0; i < 18; i++) { const a = r() * 6.283, d = 70 + r() * 110, h = 5 + r() * 26, w = 4 + r() * 9, round = r() < 0.3; const g = round ? (HI ? bcyl(w * 0.5, h, 0.6, 48) : new THREE.CylinderGeometry(w * 0.5, w * 0.5, h, 32)) : HI ? rbox(w, h, w * (0.6 + r() * 0.8), 0.5) : new THREE.BoxGeometry(w, h, w * (0.6 + r() * 0.8));
    const m = new THREE.Mesh(g, wm); m.position.set(Math.cos(a) * d, -16 + r() * 34, Math.sin(a) * d); m.rotation.y = r() * 6.28; farBlocks.add(m); }
}
// ---------- bats circling out by the moon ----------""")

# ---------- swap the scenery when the theme changes ----------
rep("""  JGLOW.value = T.jglow != null ? T.jglow : 1; if (HI) Object.assign(LK, T.lk || LK0); themeEnv(T); if (post) post.grade(T);""",
    """  JGLOW.value = T.jglow != null ? T.jglow : 1; if (HI) Object.assign(LK, T.lk || LK0); themeEnv(T); if (post) post.grade(T);
  // day worlds: no stars or moon, a sun, clouds up in the sky (not under the canvas), birds or none, and their own far scenery
  skyU.dayBase.value = T.day ? 1 : 0; skyU.sunAmt.value = T.sun || 0; skyU.low.set(T.low || 0x150D33);
  const lift = T.day ? [62, 16] : [0, 0]; for (const c of clouds) c.m.position.y = c.y0 + lift[c.layer];
  for (const it of islands) it.g.visible = !T.day;
  if (T.day) buildFar(); farIsles.visible = T.id === 'island'; farBlocks.visible = T.id === 'blank'; sea.visible = !!T.sea;
  batMat.color.set(T.day ? 0xF4F4F4 : 0x0C0718); for (const g of moverMeshes) g.children[0].material.color.set(T.cloud || CLOUD_TINT[T.id] || 0xD9D4F2);""")
open(p,'w').write(s); print('theme patch 1 ok')
