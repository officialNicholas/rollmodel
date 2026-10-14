// ---------- (v257) the first launch, out in the sun: a scrapyard in a sandstone canyon at midday. The camera looks up over the canyon's
// rim and comes down on an old oil drum; it rocks, tips over and pours; a pair of eyes comes up out of the puddle and looks about; you
// pick their colour, their style, then the paint's colour; it hauls itself out, jumps clear and shakes the paint off; you name it,
// say you're happy, it winks and jumps away, and the iris opens on the lobby with it jumping in. The music builds with each pick
// (AU.flm). Only for a brand-new player (no name, no matches, the lesson still ahead; window.__introNow forces it). Its scene is its
// own, built only when it runs, drawn in place of the lobby, and thrown away after ----------
var FL = (() => {
  const due = !!window.__introNow || (!store.introDone && !store.name && !((store.runs || 0) > 0) && tutPh() === 'match');
  const api = { due, live: false, jin: null, hush: due, busy: () => false, frame: () => false, after: () => {}, boot: () => {} };
  if (!due) return api;
  const V3 = THREE.Vector3, PEARL = new THREE.Color(0xE6DEF2), C0 = new V3(0.72, 0, 0.26), LAND = new V3(0.42, 0, 1.18);
  const SUN = new V3(-0.52, 0.8, 0.3).normalize(); // (toward the sun: high, over your left shoulder; shadows fall back and to the right)
  const clamp01 = u => clamp(u, 0, 1), eOut = u => 1 - Math.pow(1 - clamp01(u), 3), eIn = u => Math.pow(clamp01(u), 2.2);
  const BR = { base: new V3(-0.66, 0, -0.3), R: 0.29, Rm: 0.302, H: 0.88 }, TIP = new V3(0.93, 0, 0.36).normalize(), TIPAX = new V3(TIP.z, 0, -TIP.x);
  const PANO = { r: 26, len: 2.3, img: 1.5, hv: 0.29 }; // (the canyon: its cylinder's radius, how much of a turn it goes round, how much of that the painting itself spans (mirrored out to the ends), where the ground line sits up the painting)
  let X = null; // everything the scene is made of, while it runs
  let seed = 257; const rand = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }, rnd = (a, b) => a + rand() * (b - a);
  // ---- textures ----
  function canvasTex(w, h, draw, srgb) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h); const t = new THREE.CanvasTexture(c); if (srgb !== false) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; t.userData.redraw = () => { g.clearRect(0, 0, w, h); draw(g, w, h); t.needsUpdate = true; }; return t; }
  const IMG = {}; // the intro's art, asked for when it starts (only a first-timer's page ever asks)
  function art(name, done) { if (IMG[name]) { if (IMG[name].complete && IMG[name].naturalWidth) done(IMG[name]); else IMG[name].addEventListener('load', () => done(IMG[name])); return; } const im = new Image(); IMG[name] = im; im.onload = () => { if (X) done(im); }; im.src = 'art/' + name + '.webp'; }
  function imgTex(name, wrap, fallback) {
    // (a dab of its colour until the picture's in, so nothing's ever drawn black)
    const c = document.createElement('canvas'); c.width = c.height = 4; const g = c.getContext('2d'); g.fillStyle = fallback || '#888'; g.fillRect(0, 0, 4, 4);
    const t = new THREE.Texture(c); t.needsUpdate = true; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; if (wrap) t.wrapS = t.wrapT = THREE.RepeatWrapping; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter;
    art(name, im => { t.dispose(); t.image = im; t.needsUpdate = true; }); return t; // (let go of the placeholder's storage first: the picture's a different size)
  }
  // a material whose picture goes soft with the depth of field (the camera's focus): its map sampled with a bias
  function dofMap(m) { m.onBeforeCompile = sh => { sh.uniforms.uDof = X.dofU; sh.fragmentShader = 'uniform float uDof;\n' + sh.fragmentShader.replace('#include <map_fragment>', '#ifdef USE_MAP\n vec4 sampledDiffuseColor = texture2D( map, vMapUv, uDof );\n diffuseColor *= sampledDiffuseColor;\n#endif'); }; m.customProgramCacheKey = () => 'fl-dof'; return m; }
  // ---- the drum: an old steel oil drum, faded red over rust, its lid on tight, the paint inside dribbled down its side ----
  function makeDrum() {
    const { R, H } = BR, pts = [new THREE.Vector2(0.001, 0)];
    const bump = y => 0.012 * (Math.exp(-Math.pow((y - 0.012) / 0.01, 2)) + Math.exp(-Math.pow((y - H + 0.012) / 0.01, 2))) + 0.009 * (Math.exp(-Math.pow((y - H / 3) / 0.016, 2)) + Math.exp(-Math.pow((y - 2 * H / 3) / 0.016, 2)));
    for (let i = 0; i <= 44; i++) { const y = i / 44 * H; pts.push(new THREE.Vector2(R + bump(y), y)); }
    pts.push(new THREE.Vector2(R - 0.006, H), new THREE.Vector2(R - 0.01, 0.06), new THREE.Vector2(0.001, 0.06));
    const geo = new THREE.LatheGeometry(pts, 40), P3 = geo.attributes.position, UV = geo.attributes.uv;
    for (let i = 0; i < P3.count; i++) { const y = P3.getY(i), r = Math.hypot(P3.getX(i), P3.getZ(i)), inner = r < R - 0.004 || (y < 0.002); UV.setY(i, inner ? 0.004 : clamp(y / H, 0.01, 0.995)); }
    const tex = canvasTex(1024, 512, (g, W, Hh) => drawDrum(g, W, Hh, null), true); tex.wrapS = THREE.RepeatWrapping;
    art('intro_drum', im => { tex.userData.redraw = (() => { const c = tex.image, g = c.getContext('2d'); return () => { g.clearRect(0, 0, c.width, c.height); drawDrum(g, c.width, c.height, im); tex.needsUpdate = true; }; })(); tex.userData.redraw(); });
    const mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.62, metalness: 0.35, side: THREE.DoubleSide });
    const body = new THREE.Mesh(geo, mat); body.rotation.y = Math.PI + 0.25;
    const lidTop = canvasTex(256, 256, (g, W) => { g.fillStyle = '#8E2F22'; g.fillRect(0, 0, W, W); for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(' + (rnd(90, 150) | 0) + ',' + (rnd(40, 70) | 0) + ',20,' + rnd(0.25, 0.6).toFixed(2) + ')'; g.beginPath(); g.arc(rnd(0, W), rnd(0, W), rnd(4, 26), 0, 7); g.fill(); }
      g.strokeStyle = '#5A1C14'; g.lineWidth = 10; g.beginPath(); g.arc(W / 2, W / 2, W / 2 - 6, 0, 7); g.stroke(); g.lineWidth = 3; g.strokeStyle = 'rgba(255,220,190,.35)'; g.beginPath(); g.arc(W / 2, W / 2, W / 2 - 14, 0, 7); g.stroke();
      for (const [x, y, r] of [[W * 0.3, W * 0.32, 20], [W * 0.68, W * 0.66, 13]]) { g.fillStyle = '#4A1610'; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); g.fillStyle = '#B4473A'; g.beginPath(); g.arc(x - 2, y - 2, r * 0.7, 0, 7); g.fill(); }
      g.fillStyle = '#ECE5F6'; g.beginPath(); g.ellipse(W * 0.66, W * 0.3, 22, 13, 0.5, 0, 7); g.fill(); g.beginPath(); g.ellipse(W * 0.2, W * 0.7, 10, 7, 0.2, 0, 7); g.fill(); });
    const lid = new THREE.Mesh(new THREE.CylinderGeometry(R + 0.006, R + 0.006, 0.03, 32), [new THREE.MeshStandardMaterial({ color: 0x6E2219, roughness: 0.5, metalness: 0.5 }), new THREE.MeshStandardMaterial({ map: lidTop, roughness: 0.55, metalness: 0.35 }), new THREE.MeshStandardMaterial({ color: 0x3A120C, roughness: 0.8 })]);
    lid.position.y = H + 0.008;
    const g = new THREE.Group(); g.add(body, lid); return { g, body, lid };
  }
  function drawDrum(g, W, H, im) {
    seed = 257; g.fillStyle = '#9B2E21'; g.fillRect(0, 0, W, H);
    if (im) { for (let x = 0; x < W; x += H) g.drawImage(im, x, 0, H, H); g.fillStyle = 'rgba(120,30,20,.18)'; g.fillRect(0, 0, W, H); }
    // darker where the rims and ribs are, the steel showing through in scuffs
    for (const v of [0.013, 1 / 3, 2 / 3, 0.987]) { const y = (1 - v) * H; const gr = g.createLinearGradient(0, y - 14, 0, y + 14); gr.addColorStop(0, 'rgba(40,10,6,0)'); gr.addColorStop(0.5, 'rgba(40,10,6,.45)'); gr.addColorStop(1, 'rgba(40,10,6,0)'); g.fillStyle = gr; g.fillRect(0, y - 14, W, 28); g.fillStyle = 'rgba(255,214,190,.25)'; g.fillRect(0, y - 3, W, 2); }
    for (let i = 0; i < 70; i++) { g.strokeStyle = 'rgba(210,180,160,' + rnd(0.08, 0.25).toFixed(2) + ')'; g.lineWidth = rnd(0.6, 1.6); g.beginPath(); const x = rnd(0, W), y = rnd(0, H); g.moveTo(x, y); g.lineTo(x + rnd(-30, 30), y + rnd(-8, 8)); g.stroke(); }
    // a stencil on the front: a paint drop and PAINT, sprayed in pale cream
    g.save(); g.translate(W * 0.5, H * 0.5); g.fillStyle = 'rgba(244,236,222,.88)'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = '400 64px "Bowlby One", "Arial Black", Impact, sans-serif'; g.fillText('PAINT', 0, 30);
    g.beginPath(); g.moveTo(0, -78); g.bezierCurveTo(30, -38, 30, -18, 0, -16); g.bezierCurveTo(-30, -18, -30, -38, 0, -78); g.fill(); g.font = '800 15px Figtree, Arial, sans-serif'; g.fillText('THICK  .  GLOSSY  .  WET', 0, 74); g.restore();
    // the paint that's in it, run down from the rim: pearly drips, rounded at their ends
    g.fillStyle = '#ECE5F6'; g.fillRect(0, 0, W, 10);
    for (let i = 0; i < 34; i++) { const x = rnd(0, W), w = rnd(6, 15), len = rnd(16, i % 6 === 0 ? 170 : 70); g.beginPath(); g.moveTo(x - w, 0); g.lineTo(x - w * 0.55, len); g.arc(x, len, w * 0.55, Math.PI, 0, true); g.lineTo(x + w, 0); g.closePath(); g.fill(); }
    g.fillStyle = 'rgba(255,255,255,.55)'; for (let i = 0; i < 30; i++) g.fillRect(rnd(0, W), 3, 2, rnd(6, 34));
    g.fillStyle = '#2A0E0A'; g.fillRect(0, H - 4, W, 4); // (the inside: dark)
  }
  // ---- the set: sandstone rocks, agaves, a sheet of corrugated iron, caution tape on posts (the wrecks are in the canyon's painting) ----
  function merge(geos) { // (non-indexed geometries with position, normal and color, into one)
    let n = 0; for (const g of geos) n += g.attributes.position.count; const P = new Float32Array(n * 3), N = new Float32Array(n * 3), C = new Float32Array(n * 3); let o = 0;
    for (const g of geos) { P.set(g.attributes.position.array, o * 3); N.set(g.attributes.normal.array, o * 3); C.set(g.attributes.color.array, o * 3); o += g.attributes.position.count; g.dispose(); }
    const m = new THREE.BufferGeometry(); m.setAttribute('position', new THREE.BufferAttribute(P, 3)); m.setAttribute('normal', new THREE.BufferAttribute(N, 3)); m.setAttribute('color', new THREE.BufferAttribute(C, 3)); return m;
  }
  function paintVerts(g, fn) { const P = g.attributes.position, c = new Float32Array(P.count * 3), col = new THREE.Color(); for (let i = 0; i < P.count; i++) { fn(col, P.getX(i), P.getY(i), P.getZ(i)); c[i * 3] = col.r; c[i * 3 + 1] = col.g; c[i * 3 + 2] = col.b; } g.setAttribute('color', new THREE.BufferAttribute(c, 3)); return g; }
  const ROCKS = [[-1.55, -0.55, 0.42, 0.3, 0.36], [-1.12, -0.95, 0.22, 0.16, 0.2], [2.05, -0.9, 0.5, 0.38, 0.42], [2.5, -0.35, 0.24, 0.18, 0.22], [-1.25, 1.15, 0.16, 0.11, 0.14], [1.55, 1.55, 0.12, 0.08, 0.1], [0.05, -1.9, 0.3, 0.2, 0.26]];
  const AGAVES = [[-0.95, 0.45, 0.42], [1.7, -0.3, 0.5], [-0.25, -1.75, 0.36], [2.35, 0.75, 0.3]];
  function makeSet() {
    const set = new THREE.Group(), mats = [];
    // rocks: chunky faceted sandstone, banded light and dark
    { const gs = []; seed = 31;
      for (const [x, z, sx, sy, sz] of ROCKS) { const g = new THREE.IcosahedronGeometry(1, 1).toNonIndexed(), P = g.attributes.position;
        for (let i = 0; i < P.count; i++) { const vx = P.getX(i), vy = P.getY(i), vz = P.getZ(i), k = 1 + 0.18 * Math.sin(vx * 3.1 + x * 7) * Math.cos(vz * 2.7 + z * 5) + 0.08 * Math.sin(vy * 5 + x); P.setXYZ(i, vx * sx * k, Math.max(-0.2, vy) * sy * k + sy * 0.15, vz * sz * k); }
        g.rotateY(rnd(0, 6.28)); g.translate(x, 0, z); g.computeVertexNormals();
        paintVerts(g, (c, px, py) => { const b = 0.5 + 0.5 * Math.sin(py * 34 + px * 3); c.setHSL(0.045 + 0.01 * b, 0.62, 0.36 + 0.12 * b + 0.06 * Math.min(1, py / 0.4), THREE.SRGBColorSpace); }); gs.push(g); }
      const m = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, flatShading: true }); mats.push(m); set.add(new THREE.Mesh(merge(gs), m)); }
    // agaves: stiff blue-green blades fanning out of the sand
    { const gs = []; seed = 77;
      for (const [x, z, s] of AGAVES) { const n = 13; for (let i = 0; i < n; i++) { const a = i / n * 6.283 + rnd(-0.2, 0.2), lift = rnd(0.35, 1.25), L = s * rnd(0.7, 1.15), w = 0.05 * s / 0.4;
        const pts = []; for (let k = 0; k <= 4; k++) { const u = k / 4, r = u * L * (0.55 + 0.45 * Math.cos(lift)), y = Math.sin(lift) * L * u - u * u * L * 0.25 * (1.4 - lift), ww = w * (1 - u) * (1 - 0.2 * u); const ca = Math.cos(a), sa = Math.sin(a);
          pts.push([x + ca * r - sa * ww, y, z + sa * r + ca * ww], [x + ca * r + sa * ww, y, z + sa * r - ca * ww]); }
        const pos = []; for (let k = 0; k < 4; k++) { const [a0, a1] = [pts[k * 2], pts[k * 2 + 1]], [b0, b1] = [pts[k * 2 + 2], pts[k * 2 + 3]]; pos.push(...a0, ...a1, ...b0, ...a1, ...b1, ...b0); }
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
        paintVerts(g, (c, px, py) => c.setHSL(0.42 - py * 0.12, 0.32, 0.22 + py * 0.55, THREE.SRGBColorSpace)); gs.push(g); } }
      const m = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7, side: THREE.DoubleSide }); mats.push(m); set.add(new THREE.Mesh(merge(gs), m)); }
    // corrugated iron leaning on the big rock
    { const g = new THREE.PlaneGeometry(1.05, 1.25, 36, 1), P = g.attributes.position; for (let i = 0; i < P.count; i++) P.setZ(i, 0.022 * Math.sin(P.getX(i) * Math.PI * 14)); g.computeVertexNormals();
      const m = dofMap(new THREE.MeshStandardMaterial({ map: imgTex('intro_rust', true, '#7A3A24'), color: 0xA9A2A6, roughness: 0.55, metalness: 0.55, side: THREE.DoubleSide })); mats.push(m);
      const s = new THREE.Mesh(g, m); s.position.set(1.62, 0.5, -1.25); s.rotation.set(-0.42, -0.35, 0.06); set.add(s); }
    // caution tape on three posts across the back
    { const posts = [[2.55, -1.9], [1.05, -2.55], [-0.45, -2.85]], gs = [];
      for (const [x, z] of posts) { const g = new THREE.BoxGeometry(0.07, 0.95, 0.07).toNonIndexed(); g.translate(x, 0.45, z); g.rotateY(0); paintVerts(g, (c, px, py) => c.setHSL(0.07, 0.45, 0.22 + py * 0.12, THREE.SRGBColorSpace)); gs.push(g); }
      const pm = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9 }); mats.push(pm); set.add(new THREE.Mesh(merge(gs), pm));
      const tex = canvasTex(512, 32, (g, W, H) => { g.fillStyle = '#F7C51E'; g.fillRect(0, 0, W, H); g.fillStyle = '#16121A'; for (let x = -H; x < W; x += 44) { g.beginPath(); g.moveTo(x, H); g.lineTo(x + 16, H); g.lineTo(x + 16 + H, 0); g.lineTo(x + H, 0); g.fill(); }
        g.fillStyle = '#F7C51E'; g.fillRect(150, 4, 212, H - 8); g.fillStyle = '#16121A'; g.font = '900 19px Figtree, "Arial Black", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('CAUTION  WET PAINT', 256, H / 2 + 1); });
      tex.wrapS = THREE.RepeatWrapping; const pos = [], uv = [];
      for (const h of [0.78, 0.48]) for (let k = 0; k < posts.length - 1; k++) { const [ax, az] = posts[k], [bx, bz] = posts[k + 1], L = Math.hypot(bx - ax, bz - az), N = 10;
        for (let i = 0; i < N; i++) { const u0 = i / N, u1 = (i + 1) / N, sag = u => 0.08 * Math.sin(u * Math.PI), y0 = h - sag(u0), y1 = h - sag(u1), x0 = ax + (bx - ax) * u0, z0 = az + (bz - az) * u0, x1 = ax + (bx - ax) * u1, z1 = az + (bz - az) * u1, w = 0.045;
          pos.push(x0, y0 - w, z0, x1, y1 - w, z1, x1, y1 + w, z1, x0, y0 - w, z0, x1, y1 + w, z1, x0, y0 + w, z0); const a = u0 * L / 1.6, b = u1 * L / 1.6; uv.push(a, 0, b, 0, b, 1, a, 0, b, 1, a, 1); } }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.computeVertexNormals();
      const tm = dofMap(new THREE.MeshStandardMaterial({ map: tex, roughness: 0.6, side: THREE.DoubleSide })); mats.push(tm); set.add(new THREE.Mesh(g, tm)); }
    return set;
  }
  // ---- the ground: warm sand with the wind's ripples, the paint on it (pool, spill and every splat, a metaball field), the hard
  // shadows the sun throws (each caster a capsule laid along the light), going soft away from what the camera's on; one draw ----
  const FLOOR_FS = `uniform sampler2D uSand; uniform vec3 uCol, uSun, uSunCol, uAmb, uHaze, uFocus; uniform float uPearl, uT, uR, uMR, uDof; uniform vec2 uC, uM; uniform vec3 uSpl[24]; uniform int uN, uNC; uniform vec4 uRip[4]; uniform vec4 uHole; uniform vec4 uCapA[4]; uniform vec2 uCapR[4]; uniform sampler2D uShTex;
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
float capsule(vec2 p, vec2 a, vec2 b){ vec2 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-5), 0.0, 1.0); return length(pa - ba * h); }
void main(){
  vec2 p = vW.xz; float df = length(p - uFocus.xz), blur = clamp((df - 0.35) * uDof * 0.55, 0.0, 1.0), far = length(p - vec2(0.3, -0.3));
  float f = far < 4.5 ? field(p) : 9.0; // (the paint never gets further out than this)
  // the sand: the texture (soft where it's out of focus), large patches of lighter and darker, the light in the ripples
  vec3 sand = texture2D(uSand, p * 0.62, blur * 4.5 + smoothstep(6.0, 20.0, far) * 3.0).rgb; float lo = vn(p * 0.32);
  vec3 alb = sand * mix(0.82, 1.12, lo);
  // shadows: every caster, its shadow laid along the sun, crisp near where it stands and softer out of focus
  float sh = 1.0;
  if (far < 6.0) { vec2 st = (p + 5.0) / 10.0; if (st.x > 0.0 && st.x < 1.0 && st.y > 0.0 && st.y < 1.0) sh = texture2D(uShTex, st, blur * 2.5).r; // (the still things' shadows, laid down once)
    for (int i = 0; i < 4; i++) { if (i >= uNC) break; vec4 c = uCapA[i]; vec2 r = uCapR[i]; float d = capsule(p, c.xy, c.zw), w = r.y + blur * 0.12; sh = min(sh, smoothstep(r.x - w, r.x + w, d)); } }
  vec3 col = alb * (uSunCol * sh + uAmb);
  col *= 1.0 - 0.32 * smoothstep(0.09, 0.0, f) * smoothstep(-0.03, 0.0, f); // (damp sand right round the paint)
  if (f < 0.03) {
    // (the paint's surface: its height once, its slope from the screen-space change across the pixel, so one evaluation of the field)
    float h = height(p, f); vec3 S = vec3(vW.x, h * 0.09, vW.z); vec3 n = normalize(cross(dFdx(S), dFdy(S))); if (n.y < 0.0) n = -n;
    vec3 v = normalize(cameraPosition - vW), hv = normalize(uSun + v);
    vec3 ir = 0.5 + 0.5 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + dot(n.xz, vec2(2.2, 1.4)) + p.x * 0.5 + uT * 0.04));
    vec3 base = mix(uCol, mix(vec3(0.82, 0.78, 0.9), ir * 0.85 + 0.15, 0.3), uPearl);
    vec3 r = reflect(-v, n); vec3 sky = mix(vec3(0.55, 0.62, 0.8), vec3(0.06, 0.16, 0.75), smoothstep(0.1, 0.8, r.y));
    float fr = 0.04 + 0.96 * pow(1.0 - max(dot(n, v), 0.0), 5.0);
    vec3 pc = base * (uSunCol * sh * (0.55 + 0.45 * max(dot(n, uSun), 0.0)) + uAmb * 1.2) * (0.78 + 0.22 * smoothstep(-0.02, -0.16, f)) + sky * fr * 0.8 + vec3(1.0, 0.97, 0.9) * pow(max(dot(n, hv), 0.0), 160.0) * 3.0 * sh;
    float aa = fwidth(f) * 1.2 + 0.002; col = mix(col, pc, smoothstep(aa, -aa, f));
  }
  // far off, the sand goes into the canyon's haze
  col = mix(col, uHaze, smoothstep(7.0, 24.0, length(p - uFocus.xz)));
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
  function makeFloor() {
    const sand = imgTex('intro_sand', true, '#E2A06A');
    const U = { uSand: { value: sand }, uCol: { value: PEARL.clone() }, uPearl: { value: 1 }, uT: { value: 0 }, uR: { value: 0 }, uMR: { value: 0 }, uC: { value: new THREE.Vector2(C0.x, C0.z) }, uM: { value: new THREE.Vector2() },
      uSpl: { value: Array.from({ length: 24 }, () => new V3()) }, uN: { value: 0 }, uRip: { value: Array.from({ length: 4 }, () => new THREE.Vector4()) }, uHole: { value: new THREE.Vector4() },
      uSun: { value: SUN.clone() }, uSunCol: { value: new V3(1.25, 1.08, 0.86) }, uAmb: { value: new V3(0.2, 0.26, 0.48) }, uHaze: { value: new V3(0.85, 0.55, 0.36) }, uFocus: { value: new V3() }, uDof: { value: 0 },
      uCapA: { value: Array.from({ length: 4 }, () => new THREE.Vector4()) }, uCapR: { value: Array.from({ length: 4 }, () => new THREE.Vector2()) }, uNC: { value: 0 }, uShTex: { value: null } };
    const m = new THREE.Mesh(new THREE.PlaneGeometry(90, 90).rotateX(-Math.PI / 2), new THREE.ShaderMaterial({ uniforms: U, extensions: { derivatives: true },
      vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }', fragmentShader: FLOOR_FS }));
    m.renderOrder = -2; return { m, U };
  }
  // ---- the sky and the canyon: a dome from deep blue overhead to pale at the horizon with the sun's glow, and the painted canyon
  // round the back on a cylinder (its sky fading into the dome), soft when the camera's in close ----
  const SKY = `uniform vec3 uTop, uHor, uSunD; varying vec3 vW;
vec3 sky(vec3 d){ float y = clamp(d.y, -0.2, 1.0); vec3 c = mix(uHor, uTop, pow(smoothstep(0.0, 0.75, y), 0.7)); float s = max(dot(normalize(d), uSunD), 0.0); c += vec3(1.0, 0.92, 0.75) * (pow(s, 600.0) * 3.0 + pow(s, 12.0) * 0.18); return c; }`;
  function makeSky() {
    const U = { uTop: { value: new V3(0.03, 0.09, 0.62) }, uHor: { value: new V3(0.32, 0.5, 0.95) }, uSunD: { value: SUN.clone() }, uPano: { value: imgTex('intro_canyon', false, '#C98A5A') }, uBias: { value: 0 } };
    U.uPano.value.wrapS = THREE.MirroredRepeatWrapping; U.uPano.value.wrapT = THREE.ClampToEdgeWrapping;
    const dome = new THREE.Mesh(new THREE.SphereGeometry(45, 32, 16), new THREE.ShaderMaterial({ uniforms: U, side: THREE.BackSide, depthWrite: false,
      vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
      fragmentShader: SKY + '\nvoid main(){ gl_FragColor = vec4(sky(normalize(vW - cameraPosition)), 1.0);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}' }));
    dome.renderOrder = 11; dome.frustumCulled = false; // (drawn last: only the sky nothing's in front of gets shaded)
    const H = PANO.r * PANO.img * 972 / 2048, g = new THREE.CylinderGeometry(PANO.r, PANO.r, H, 64, 1, true, Math.PI - PANO.len / 2, PANO.len);
    const pano = new THREE.Mesh(g, new THREE.ShaderMaterial({ uniforms: U, side: THREE.BackSide,
      vertexShader: 'varying vec2 vUv; varying vec3 vW; void main(){ vUv = uv; vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
      fragmentShader: SKY + '\nuniform sampler2D uPano; uniform float uBias; varying vec2 vUv;\nvoid main(){ float ux = 0.5 + (0.5 - vUv.x) * ' + (PANO.len / PANO.img).toFixed(4) + '; vec2 uv = vec2(ux, vUv.y); vec4 t = texture2D(uPano, uv, uBias); float k = smoothstep(0.97, 0.78, uv.y) * smoothstep(0.0, 0.05, vUv.x) * smoothstep(1.0, 0.95, vUv.x);\n gl_FragColor = vec4(mix(sky(normalize(vW - cameraPosition)), t.rgb * 1.08, k), 1.0);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}' }));
    pano.position.y = H / 2 - PANO.hv * H; pano.renderOrder = 10; pano.frustumCulled = false;
    // (the sky and the far sand's colours taken off the painting itself, so the dome and the near sand meet it without a seam)
    art('intro_canyon', im => { try { const c = document.createElement('canvas'); c.width = 64; c.height = 32; const g2 = c.getContext('2d'); g2.drawImage(im, 0, 0, 64, 32); const d = g2.getImageData(0, 0, 64, 32).data;
      const row = (y, x0, x1) => { const s = [0, 0, 0]; let n = 0; for (let x = x0; x < x1; x++) { const i = (y * 64 + x) * 4; s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; n++; } return new THREE.Color(s[0] / n / 255, s[1] / n / 255, s[2] / n / 255).convertSRGBToLinear(); };
      const top = row(1, 20, 44), hor = row(13, 20, 44), gr = row(Math.round(32 * (1 - PANO.hv)) + 2, 20, 44); // (the clear sky's top and its paler blue low down, above the canyon's haze; the sand at the painting's ground line)
      U.uTop.value.set(top.r, top.g, top.b); U.uHor.value.set(hor.r, hor.g, hor.b); if (X) X.floor.U.uHaze.value.set(gr.r, gr.g, gr.b); } catch (e) {} });
    return { dome, pano, U };
  }
  // the pour: a rope of paint out of the drum's mouth, falling to the sand
  function makeStream() {
    const U = { uP0: { value: new V3() }, uV0: { value: new V3() }, uT: { value: 0.5 }, uR: { value: 0 }, uCut: { value: 0 }, uCol: { value: PEARL.clone() }, uPearl: { value: 1 }, uTime: { value: 0 }, uSun: { value: SUN.clone() } };
    const m = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1, 12, 28, true), new THREE.ShaderMaterial({ uniforms: U,
      vertexShader: `uniform vec3 uP0, uV0; uniform float uT, uR, uCut, uTime; varying float vS; varying vec3 vN, vW;
void main(){ float s = 0.5 - position.y; vS = s; float t = s * uT; vec3 g = vec3(0.0, -9.0, 0.0), c = uP0 + uV0 * t + 0.5 * g * t * t, tg = normalize(uV0 + g * t);
  vec3 sd = normalize(cross(tg, vec3(0.0, 0.0, 1.0)) + vec3(1e-4)), bn = normalize(cross(tg, sd)); float r = uR * mix(1.0, 0.55, s) * (1.0 + 0.12 * sin(s * 26.0 - uTime * 18.0)) * smoothstep(uCut - 0.02, uCut + 0.06, s);
  vec2 q = normalize(position.xz); vN = normalize(sd * q.x + bn * q.y); vec3 w = c + vN * r; vW = w; gl_Position = projectionMatrix * viewMatrix * vec4(w, 1.0); }`,
      fragmentShader: `uniform vec3 uCol, uSun; uniform float uPearl, uCut, uTime; varying float vS; varying vec3 vN, vW;
void main(){ if (vS < uCut) discard; vec3 n = normalize(vN), v = normalize(cameraPosition - vW); float nd = max(dot(n, v), 0.0);
  vec3 ir = 0.5 + 0.5 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + n.x * 0.8 + vS * 2.0 - uTime * 0.4)); vec3 base = mix(uCol, mix(vec3(0.82, 0.78, 0.9), ir * 0.85 + 0.15, 0.3), uPearl);
  float streak = 0.5 + 0.5 * sin(vS * 40.0 - uTime * 24.0 + n.x * 3.0); vec3 c = base * (0.55 + 0.75 * max(dot(n, uSun), 0.0)) + vec3(1.0) * pow(max(dot(reflect(-v, n), uSun), 0.0), 40.0) * (1.0 + 0.8 * streak) + vec3(0.4, 0.55, 0.95) * pow(1.0 - nd, 3.0) * 0.4;
  gl_FragColor = vec4(c, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}` }));
    m.frustumCulled = false; m.visible = false; return { m, U };
  }
  // drops of paint: one instanced mesh, each drop stretched along its flight
  const DROPS = 96;
  function makeDrops() {
    const m = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 12, 8), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1, metalness: 0 }), DROPS);
    const z = new THREE.Matrix4().makeScale(0, 0, 0), c = new THREE.Color(1, 1, 1); for (let i = 0; i < DROPS; i++) { m.setMatrixAt(i, z); m.setColorAt(i, c); }
    m.frustumCulled = false; m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); return m;
  }
  // sand on the wind: fine grains drifting past low over the ground
  function makeGrit() {
    const U = { uT: { value: 0 }, uPx: { value: 1 } }, n = 80, pos = new Float32Array(n * 3), sd = new Float32Array(n);
    for (let i = 0; i < n; i++) { pos[i * 3] = rnd(-4, 4); pos[i * 3 + 1] = rnd(0, 0.9); pos[i * 3 + 2] = rnd(-3, 2.5); sd[i] = rand(); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aS', new THREE.BufferAttribute(sd, 1));
    const m = new THREE.Points(g, new THREE.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false,
      vertexShader: 'uniform float uT, uPx; attribute float aS; varying float vA; void main(){ vec3 p = position; p.x = mod(p.x + uT * (0.6 + 0.8 * aS) + 4.0, 8.0) - 4.0; p.y += sin(uT * 2.0 + aS * 30.0) * 0.05; vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = (1.0 + 1.6 * aS) * 6.0 / -mv.z * uPx; vA = smoothstep(4.0, 3.0, abs(p.x)) * (0.35 + 0.4 * aS); }',
      fragmentShader: 'varying float vA; void main(){ float d = length(gl_PointCoord - 0.5); gl_FragColor = vec4(vec3(1.0, 0.86, 0.66), smoothstep(0.5, 0.15, d) * vA); }' }));
    m.frustumCulled = false; return { m, U };
  }
  function build() {
    const sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(34, viewW / viewH, 0.05, 120);
    sc.environment = scene.environment || null;
    const hemi = new THREE.HemisphereLight(0x8FB2FF, 0xD9894E, 1.15), sun = new THREE.DirectionalLight(0xFFEFD6, 3.1), rim = new THREE.DirectionalLight(0xD6E4FF, 0.9), bounce = new THREE.DirectionalLight(0xFFA868, 0.55);
    sun.position.copy(SUN).multiplyScalar(10).add(new V3(0.2, 0, 0.1)); sun.target.position.set(0.2, 0, 0.1); rim.position.set(2.6, 2.4, -4); rim.target.position.set(0.2, 0.3, 0); bounce.position.set(0.3, -1, 1.5); bounce.target.position.set(0, 0, 0);
    sc.add(hemi, sun, sun.target, rim, rim.target, bounce, bounce.target);
    X = { dofU: { value: 0 } }; // (the materials made below read the focus from here)
    const floor = makeFloor(), drum = makeDrum(), stream = makeStream(), drops = makeDrops(), grit = makeGrit(), sky = makeSky(), set = makeSet();
    sc.add(sky.dome, sky.pano, floor.m, set, drum.g, stream.m, drops, grit.m);
    // the character: made with the game's own maker, so what you pick is exactly what you get
    const CH = AXOC.S.ready ? AXOC : SLIME, I = CH.make({ color: PEARL.getHex() }), hold = new THREE.Group(); hold.scale.setScalar(PR); hold.add(I.root); hold.visible = false; sc.add(hold);
    I.noGhost = true; if (I.coatOn) I.coatOn(); if (I.setPaint) I.setPaint(PEARL); if (I.setExpression) I.setExpression('happy');
    const o = { pos: [0, 0, 0], wt: { yaw: 0, pitch: 0 }, watch: null, dt: 0 };
    X = Object.assign(X, { sc, pc: cam, sun, floor, drum, stream, drops, grit, sky, set, CH, I, hold, o, drop: [], spl: 0, rip: 0,
      t: 0, ph: 'wait', pt: 0, paint: PEARL.clone(), paintTo: null, pearl: 1, pearlTo: 1, R: 0, MR: 0, mouth: new V3(), lid: { on: true, p: new V3(), v: new V3(), w: new V3(), rest: false },
      ch: { x: C0.x, z: C0.z, y: -1.2, yaw: 0, air: false, vy: 0, h: 0, sq: 0, rise: 0, wy: 0, wp: 0.05, wade: 1, pop: 0 }, stood: false,
      cs: { p: new V3(0.9, 0.35, 3.6), l: new V3(-1.2, 4.2, -14), ox: 0, oy: 0, shake: 0, dof: 0 }, shot: null, flags: {} });
    shot('sky', true);
    // (everything compiled now, while the orientation's asked for or the camera's still up in the sky)
    try { if (renderer.compileAsync) { hold.visible = stream.m.visible = true; renderer.compileAsync(sc, cam).catch(() => {}); hold.visible = stream.m.visible = false; } } catch (e) {}
    I.onBurst = () => burstOff();
  }
  function dispose() {
    if (!X) return; const I = X.I, own = new Set();
    I.root.traverse(o => { if (o.material) for (const m of [].concat(o.material)) own.add(m); }); // (the character's geometry and face sheets are shared with the game's own: only its materials are its own)
    for (const m of own) m.dispose();
    { const L = X.CH.S && X.CH.S.list; const i = L ? L.indexOf(I) : -1; if (i >= 0) L.splice(i, 1); }
    X.hold.remove(I.root);
    const seen = new Set();
    X.sc.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) for (const m of [].concat(o.material)) { if (own.has(m)) continue; for (const k of ['map', 'roughnessMap', 'metalnessMap']) if (m[k] && !seen.has(m[k])) { seen.add(m[k]); m[k].dispose(); } if (m.uniforms) for (const k in m.uniforms) { const v = m.uniforms[k].value; if (v && v.isTexture && !seen.has(v)) { seen.add(v); v.dispose(); } } m.dispose(); } });
    for (const k in IMG) { IMG[k].onload = null; delete IMG[k]; }
    X = null;
  }
  // ---- the camera: a shot is either a place and a point to look at, or what to look at, how much of it to fit and from which way; it
  // eases between shots, keeps what it looks at in the part of the screen the cards leave clear, and sets the depth of field ----
  const SHOTS = {
    sky: () => ({ pos: new V3(0.9, 0.32, 3.6), look: new V3(-1.3, 4.6, -14), k: 1.5, dof: 0 }),
    barrel: () => ({ t: new V3(-0.6, 0.42, -0.25), r: 0.78, yaw: 0.28, p: 0.14, k: 1.15, dof: 0.35 }),
    tip: () => ({ t: new V3(0.1, 0.22, 0.05), r: 1.15, yaw: 0.14, p: 0.3, k: 1.6, dof: 0.25 }),
    eyes: () => ({ t: new V3(X.ch.x, 0.06, X.ch.z), r: 0.46, yaw: 0.04, p: 0.3, k: 1.5, dof: 1 }),
    paint: () => ({ t: new V3(X.ch.x - 0.05, 0.08, X.ch.z), r: 0.72, yaw: 0.08, p: 0.4, k: 1.6, dof: 0.75 }),
    form: () => ({ t: new V3((C0.x + LAND.x) / 2, 0.32, (C0.z + LAND.z) / 2), r: 0.95, yaw: 0.06, p: 0.3, k: 2.2, dof: 0.4 }),
    name: () => ({ t: new V3(LAND.x, 0.3, LAND.z), r: 0.5, yaw: -0.14, p: 0.16, k: 1.8, dof: 0.95 }),
    stood: () => ({ t: new V3(LAND.x, 0.28, LAND.z), r: 0.56, yaw: 0.1, p: 0.2, k: 1.8, dof: 0.9 }),
    exit: () => ({ t: new V3(LAND.x + 0.5, 0.3, LAND.z - 0.4), r: 1.05, yaw: -0.05, p: 0.2, k: 1.2, dof: 0.4 }),
  };
  function shot(k, snap) { X.shot = SHOTS[k](); X.shotK = k; if (snap) { const s = want(); X.cs.p.copy(s.p); X.cs.l.copy(s.l); X.cs.dof = X.shot.dof; } }
  let freeAt = 0, free = null;
  function freeRect() {
    const now = performance.now(); if (free && now - freeAt < 250) return free; freeAt = now;
    const W = viewW, H = viewH, sr = stage.getBoundingClientRect(); let r = { x0: 0, y0: Math.min(H * 0.12, safeTop() + 8), x1: W, y1: H };
    const c = UI && UI.cur && !UI.cur.hidden && !UI.cur.classList.contains('out') ? UI.cur.getBoundingClientRect() : null;
    if (c && c.width > 0) { if (W > H * 1.05) r.x0 = c.right - sr.left + 8; else r.y1 = c.top - sr.top - 8; }
    return free = r;
  }
  let safeT = -1; function safeTop() { if (safeT < 0) { const d = document.createElement('div'); d.style.cssText = 'position:absolute;top:0;height:env(safe-area-inset-top);visibility:hidden'; document.body.appendChild(d); safeT = d.offsetHeight || 0; d.remove(); } return safeT; }
  // where the shot wants the camera: an orbit shot backs off far enough that its radius fits the clear part of the screen
  function want() {
    const s = X.shot; if (s.pos) return { p: s.pos, l: s.look, framed: false };
    const W = viewW, H = viewH, F = freeRect(), fw = Math.max(80, F.x1 - F.x0), fh = Math.max(80, F.y1 - F.y0), d = Math.max(0.6, s.r * H / (Math.tan(X.pc.fov * Math.PI / 360) * 0.86 * Math.min(fw, fh)));
    return { p: new V3(Math.sin(s.yaw) * Math.cos(s.p), Math.sin(s.p), Math.cos(s.yaw) * Math.cos(s.p)).multiplyScalar(d).add(s.t), l: s.t, framed: true };
  }
  function camTick(dt) {
    const c = X.cs, s = X.shot, a = 1 - Math.exp(-dt * s.k), w = want(), W = viewW, H = viewH, F = freeRect();
    c.p.lerp(w.p, a); c.l.lerp(w.l, a); c.dof += (s.dof - c.dof) * a;
    const ox = w.framed ? (F.x0 + F.x1) / 2 - W / 2 : 0, oy = w.framed ? (F.y0 + F.y1) / 2 - H / 2 : 0; c.ox += (ox - c.ox) * a; c.oy += (oy - c.oy) * a;
    c.shake = Math.max(0, c.shake - dt * 2.5); const sh = c.shake * c.shake * 0.05, tt = X.t;
    const cam = X.pc; cam.aspect = W / H; cam.position.copy(c.p); cam.position.x += Math.sin(tt * 0.37) * 0.02 + Math.sin(tt * 37) * sh; cam.position.y += Math.sin(tt * 0.29) * 0.015 + Math.cos(tt * 41) * sh;
    cam.lookAt(c.l); cam.setViewOffset(W, H, -c.ox, -c.oy, W, H); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    // the depth of field: the canyon and the sand away from the subject go soft, more the closer the shot
    X.dofU.value = c.dof * 2.6; X.sky.U.uBias.value = c.dof * 3.4; X.floor.U.uDof.value = c.dof; X.floor.U.uFocus.value.copy(c.l);
  }
  // ---- drops and splats ----
  function spawn(p, v, r, col) { const D = X.drop; if (D.length >= DROPS) D.shift(); D.push({ p: p.clone(), v: v.clone(), r, c: (col || X.paint).clone(), life: 3 }); }
  function splat(x, z, r) { const S = X.floor.U.uSpl.value, i = X.spl++ % S.length; S[i].set(x, z, r); X.floor.U.uN.value = Math.min(S.length, X.spl); }
  function ripple(x, z, amp) { const R = X.floor.U.uRip.value, i = X.rip++ % R.length; R[i].set(x, z, X.t, amp); }
  const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new V3(), _up = new V3(0, 1, 0), _d = new V3();
  function dropsTick(dt) {
    const M = X.drops, D = X.drop, U = X.floor.U; let i = 0;
    for (let k = D.length - 1; k >= 0; k--) { const d = D[k]; d.v.y -= 9.5 * dt; d.p.addScaledVector(d.v, dt); d.life -= dt;
      if (d.p.y < d.r * 0.6) { const inP = Math.hypot(d.p.x - U.uC.value.x, d.p.z - U.uC.value.y) < X.R * 0.95; if (inP) ripple(d.p.x, d.p.z, 0.25); else splat(d.p.x, d.p.z, d.r * rnd(2.2, 3.2)); D.splice(k, 1); continue; }
      if (d.life <= 0) { D.splice(k, 1); continue; } }
    for (const d of D) { const sp = d.v.length(); _d.copy(d.v).divideScalar(sp || 1); _q.setFromUnitVectors(_up, _d); _s.set(d.r, d.r * (1 + Math.min(1.6, sp * 0.09)), d.r); _m.compose(d.p, _q, _s); M.setMatrixAt(i, _m); M.setColorAt(i, d.c); i++; }
    _m.makeScale(0, 0, 0); for (; i < (M.userData.n || DROPS); i++) M.setMatrixAt(i, _m); M.userData.n = D.length;
    M.instanceMatrix.needsUpdate = true; if (M.instanceColor) M.instanceColor.needsUpdate = true;
  }
  // the paint coming off it: drops flung out all round from its body and ears as it shakes
  function burstOff() {
    if (!X) return; const c = X.ch;
    for (let i = 0; i < 40; i++) { const a = rand() * 6.283, s = rnd(1.6, 3.6); spawn(new V3(c.x + Math.cos(a) * 0.14, rnd(0.12, 0.42), c.z + Math.sin(a) * 0.14), new V3(Math.cos(a) * s, rnd(1.6, 4.2), Math.sin(a) * s), rnd(0.012, 0.03)); }
    snd('splat', 1); buzz([8, 20, 8]);
  }
  // ---- the shadows on the sand: each caster a capsule from where it meets the ground to where its top's shadow falls ----
  const _a = new V3(), _b = new V3(), proj = (v, out) => out.set(v.x - SUN.x / SUN.y * v.y, v.z - SUN.z / SUN.y * v.y);
  const _pa = new THREE.Vector2(), _pb = new THREE.Vector2(), STATIC = [];
  function shadowsInit() {
    STATIC.length = 0;
    for (const [x, z, sx, sy, sz] of ROCKS) { proj(_a.set(x, sy * 0.9, z), _pb); STATIC.push([x, z, _pb.x, _pb.y, Math.min(sx, sz) * 0.75, 0.025]); }
    for (const [x, z, s] of AGAVES) { proj(_a.set(x, s * 0.6, z), _pb); STATIC.push([x, z, _pb.x, _pb.y, s * 0.45, 0.09]); }
    proj(_a.set(1.62, 0.95, -1.25), _pb); STATIC.push([1.5, -1.05, _pb.x, _pb.y, 0.36, 0.03]);
    for (const [x, z] of [[2.55, -1.9], [1.05, -2.55], [-0.45, -2.85]]) { proj(_a.set(x, 0.95, z), _pb); STATIC.push([x, z, _pb.x, _pb.y, 0.035, 0.012]); }
    const N = 384, data = new Uint8Array(N * N * 4), sm = (a, b, x) => { const u = Math.max(0, Math.min(1, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const px = (i + 0.5) / N * 10 - 5, pz = (j + 0.5) / N * 10 - 5; let sh = 1;
      for (const [ax, az, bx, bz, r, w] of STATIC) { if (Math.abs(px - ax) > 2 && Math.abs(px - bx) > 2) continue; const pax = px - ax, paz = pz - az, bax = bx - ax, baz = bz - az, h = Math.max(0, Math.min(1, (pax * bax + paz * baz) / Math.max(bax * bax + baz * baz, 1e-5))), d = Math.hypot(pax - bax * h, paz - baz * h); sh = Math.min(sh, sm(r - w, r + w, d)); }
      const k = (j * N + i) * 4; data[k] = data[k + 1] = data[k + 2] = Math.round(sh * 255); data[k + 3] = 255; }
    const t = new THREE.DataTexture(data, N, N, THREE.RGBAFormat); t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter; t.needsUpdate = true; X.floor.U.uShTex.value = t;
  }
  function shadowsTick() {
    const A = X.floor.U.uCapA.value, Rr = X.floor.U.uCapR.value; let n = 0; const add = (ax, az, bx, bz, r, s) => { if (n >= A.length) return; A[n].set(ax, az, bx, bz); Rr[n].set(r, s); n++; };
    // the drum: along its axis, base to top, each end's shadow where the sun puts it
    X.drum.g.updateMatrixWorld(); _a.set(0, 0.02, 0).applyMatrix4(X.drum.g.matrixWorld); _b.set(0, BR.H, 0).applyMatrix4(X.drum.g.matrixWorld); proj(_a, _pa); proj(_b, _pb); add(_pa.x, _pa.y, _pb.x, _pb.y, BR.R * 0.95, 0.02);
    if (!X.lid.on) { const m = X.drum.lid.position; proj(_a.copy(m), _pa); add(_pa.x, _pa.y, _pa.x + 0.001, _pa.y, BR.R * 0.9 * Math.min(1, 0.4 + m.y * 0), 0.03); }
    // the character: its body, low and high, where the sun throws them (out in the paint, only once it's up out of it)
    const c = X.ch; if (X.hold.visible && c.y > 0.02) { _a.set(c.x, Math.max(0, c.y - PR) + 0.05, c.z); _b.set(c.x, Math.max(0, c.y - PR) + 0.3, c.z); proj(_a, _pa); proj(_b, _pb); add(_pa.x, _pa.y, _pb.x, _pb.y, 0.15, 0.03 + c.h * 0.05); }
    X.floor.U.uNC.value = n;
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
  // ---- the cards: a black strip of tape with the line in big white letters, under it a torn black board with the choices; the
  // pick sits on a splat of your paint with a little drop pointing at it; Next is a splat too ----
  let UI = null;
  const STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1.5l2.6 7.2 7.6.3-6 4.7 2.1 7.3L12 16.7 5.7 21l2.1-7.3-6-4.7 7.6-.3z"/></svg>';
  const DROP = '<svg viewBox="0 0 32 40" aria-hidden="true"><path d="M16 2C22 12 28 18 28 26a12 12 0 0 1-24 0C4 18 10 12 16 2z" fill="var(--ink)" stroke="#fff" stroke-width="2.5"/><circle cx="12" cy="25" r="3.4" fill="#fff"/><circle cx="20" cy="25" r="3.4" fill="#fff"/><circle cx="12.8" cy="25.8" r="1.7" fill="#151218"/><circle cx="20.8" cy="25.8" r="1.7" fill="#151218"/></svg>';
  const DICE = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="8.5" cy="8.5" r="1.6"/><circle cx="15.5" cy="15.5" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="15.5" cy="8.5" r="1.6"/><circle cx="8.5" cy="15.5" r="1.6"/></svg>';
  const BACK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4.5 7.5 12l7.5 7.5" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  // a torn edge all round, its own every time
  function torn(el, amp, n) { const j = () => (rand() * amp).toFixed(1), pts = [];
    for (let i = 0; i <= n; i++) pts.push((i / n * 100).toFixed(1) + '% ' + j() + 'px');
    for (let i = 1; i < 4; i++) pts.push('calc(100% - ' + j() + 'px) ' + (i / 4 * 100).toFixed(1) + '%');
    for (let i = n; i >= 0; i--) pts.push((i / n * 100).toFixed(1) + '% calc(100% - ' + j() + 'px)');
    for (let i = 3; i >= 1; i--) pts.push(j() + 'px ' + (i / 4 * 100).toFixed(1) + '%');
    el.style.clipPath = 'polygon(' + pts.join(',') + ')'; }
  function panel(id, line, body, foot, back) {
    return '<section class="flpanel" id="' + id + '" hidden aria-labelledby="' + id + 'T"><h2 class="flbanner" id="' + id + 'T">' + line + '</h2><div class="flboard">' + body + '</div><div class="flfoot">'
      + (back ? '<button class="flback" type="button" data-back="' + back + '" aria-label="Back">' + BACK + '<span>Back</span></button>' : '<i></i>') + foot + '</div></section>';
  }
  const opt = (attr, k, inner, label, on) => '<button type="button" class="flopt" ' + attr + '="' + k + '" aria-label="' + label + '" aria-pressed="' + !!on + '"><i class="flsel" aria-hidden="true"></i><span class="flcur" aria-hidden="true">' + DROP + '</span>' + inner + '</button>';
  const go_ = (id, label, dis) => '<button class="flgo" type="button" id="' + id + '"' + (dis ? ' disabled' : '') + '><span>' + label + '</span></button>';
  function buildUi() {
    const el = document.createElement('div'); el.className = 'flui'; el.id = 'flUi';
    const irises = EYE_KEYS.map(k => opt('data-i', k, '<i class="fliri" style="--ic:' + EYE_COLS[k].css + '"></i><b>' + EYE_COLS[k].name + '</b>', EYE_COLS[k].name + ' eyes', myLook.iris === k)).join('');
    const styles = ['round', 'edgy', 'dot'].map(k => opt('data-s', k, '<i class="flsty">' + ES_ICON_T[k] + '</i><b>' + EYE_STYLES[k] + '</b>', EYE_STYLES[k] + ' eyes', (myLook.eyes || 'round') === k)).join('');
    const paints = PALETTE.map(c => opt('data-c', c.id, '<i class="flpai" style="--c:#' + c.hex.toString(16).padStart(6, '0') + '"></i><b>' + c.name + '</b>', c.name, false)).join('');
    el.innerHTML = panel('flIris', 'Those eyes need a color.', '<div class="flopts" id="flIrisO">' + irises + '</div>', go_('flIrisGo', 'Next'), null)
      + panel('flStyle', 'Now give them some style.', '<div class="flopts" id="flStyleO">' + styles + '</div>', go_('flStyleGo', 'Next'), 'iris')
      + panel('flPaint', 'Pick your paint.', '<div class="flopts" id="flPaintO">' + paints + '</div>', go_('flPaintGo', 'Next', true), 'style')
      + '<form class="flpanel" id="flName" hidden autocomplete="off" aria-labelledby="flNameT"><h2 class="flbanner" id="flNameT">What do we call you?</h2><div class="flboard"><p class="flnote">It goes up in lights when you win.</p>'
      + '<div class="flfield"><input id="flNameIn" type="text" size="8" maxlength="12" autocomplete="off" autocapitalize="words" autocorrect="off" spellcheck="false" enterkeyhint="go" aria-label="Your name"><button class="fldice" id="flDice" type="button" aria-label="Pick a random name">' + DICE + '</button></div></div>'
      + '<div class="flfoot"><button class="flback" type="button" data-back="paint" aria-label="Back">' + BACK + '<span>Back</span></button><button class="flgo" type="submit" id="flNameGo"><span>Next</span></button></div></form>'
      + '<section class="flpanel flask" id="flAsk" hidden aria-labelledby="flAskT"><h2 class="flbanner" id="flAskT">All set?</h2><div class="flfoot"><button class="flgo alt" type="button" id="flNo"><span>Not yet</span></button><button class="flgo" type="button" id="flYes"><span>Let’s roll</span></button></div></section>'
      + '<div class="flsend" id="flSend" hidden aria-hidden="true"><b>Fresh out of the barrel?</b><b>Now go paint the town!</b></div>'
      + '<div class="flwink" id="flWink" hidden>' + STAR + '</div>';
    stage.appendChild(el); UI = { el, cur: null };
    seed = 4242; for (const b of el.querySelectorAll('.flboard')) torn(b, 7, 14); for (const b of el.querySelectorAll('.flbanner, .flsend b')) torn(b, 5, 9);
    $('flIrisO').addEventListener('click', e => { const b = e.target.closest('.flopt'); if (!b) return; AU.init(); pickIris(b.dataset.i); });
    $('flStyleO').addEventListener('click', e => { const b = e.target.closest('.flopt'); if (!b) return; AU.init(); pickStyle(b.dataset.s); });
    $('flPaintO').addEventListener('click', e => { const b = e.target.closest('.flopt'); if (!b) return; AU.init(); pickPaint(b.dataset.c); });
    $('flIrisGo').addEventListener('click', () => { AU.init(); AU.ui(); go('style'); });
    $('flStyleGo').addEventListener('click', () => { AU.init(); AU.ui(); go('paint'); });
    $('flPaintGo').addEventListener('click', () => { AU.init(); AU.ui(); go(X.stood ? 'name' : 'form'); });
    $('flDice').addEventListener('click', () => { AU.init(); AU.pop(); $('flNameIn').value = randomName(); kick($('flDice'), 'bump'); });
    $('flName').addEventListener('submit', e => { e.preventDefault(); AU.init(); AU.ui(); try { $('flNameIn').blur(); } catch (x) {} setTimeout(() => window.scrollTo(0, 0), 60); store.name = cleanName($('flNameIn').value) || randomName(); go('confirm'); });
    $('flNo').addEventListener('click', () => { AU.init(); AU.ui(); X.stood = true; go('iris'); });
    $('flYes').addEventListener('click', () => { AU.init(); AU.ui(); go('wink'); });
    el.addEventListener('click', e => { const b = e.target.closest('.flback'); if (!b) return; AU.init(); AU.ui(); go(b.dataset.back); });
  }
  function card(id) {
    const nu = id ? $(id) : null, old = UI.cur; if (old === nu) return;
    if (old) { old.classList.remove('in'); old.classList.add('out'); setTimeout(() => { if (UI && UI.cur !== old) old.hidden = true; old.classList.remove('out'); }, 300); }
    UI.cur = nu; free = null; if (nu) { nu.hidden = false; nu.classList.remove('out', 'in'); void nu.offsetWidth; nu.classList.add('in'); }
  }
  // ---- the picks ----
  const pressed = (box, attr, k) => { for (const b of $(box).children) b.setAttribute('aria-pressed', String(b.getAttribute(attr) === k)); };
  function pickIris(k) {
    if (!EYE_COLS[k]) return; myLook.iris = k; X.I.setIris && X.I.setIris(EYE_COLS[k].lin); pressed('flIrisO', 'data-i', k);
    X.I.blink && X.I.blink(); X.ch.pop = 1; snd('pop'); if (!X.stood) ripple(X.ch.x, X.ch.z, 0.35);
  }
  function pickStyle(k) {
    myLook.eyes = k; X.I.setEyeStyle && X.I.setEyeStyle(EYE_STYLE_K[k] || 0); pressed('flStyleO', 'data-s', k);
    X.I.flutter && X.I.flutter(3); X.ch.pop = 1.4; snd('pop'); if (!X.stood) ripple(X.ch.x, X.ch.z, 0.5);
  }
  function pickPaint(id) {
    const c = PALETTE.find(p => p.id === id); if (!c) return; X.paintTo = new THREE.Color(c.hex); X.paintId = id; X.pearlTo = 0;
    setColor(id); X.I.setColor && X.I.setColor(new THREE.Color(c.hex)); pressed('flPaintO', 'data-c', id); $('flPaintGo').disabled = false;
    // a splash of it: the puddle heaves and throws up a few drops
    const cx = X.stood ? C0.x : X.ch.x, cz = X.stood ? C0.z : X.ch.z;
    for (let i = 0; i < 12; i++) { const a = rand() * 6.283, s = rnd(0.5, 1.4); spawn(new V3(cx + Math.cos(a) * 0.25, 0.03, cz + Math.sin(a) * 0.25), new V3(Math.cos(a) * s, rnd(1.5, 2.8), Math.sin(a) * s), rnd(0.012, 0.024), new THREE.Color(c.hex)); }
    ripple(cx, cz, 0.8); snd('splat', 0.7); X.ch.pop = 1.2; X.I.blink && X.I.blink(); buzz(10);
  }
  // ---- the story ----
  function go(ph) {
    if (!X || X.ph === ph) return; X.ph = ph; X.pt = 0; X.flags = {};
    const look = X.stood ? 'stood' : null;
    if (ph === 'sky') shot('sky', true);
    else if (ph === 'iris') { shot(look || 'eyes'); card('flIris'); AU.flm.layer(1); }
    else if (ph === 'style') { shot(look || 'eyes'); card('flStyle'); AU.flm.layer(2); }
    else if (ph === 'paint') { shot(look || 'paint'); card('flPaint'); AU.flm.layer(3); }
    else if (ph === 'form') { if (!X.paintId) pickPaint(colorId); card(null); AU.flm.layer(3); shot('form'); }
    else if (ph === 'name') { X.stood = true; shot('name'); card('flName'); const i = $('flNameIn'); if (!i.value) i.value = cleanName(store.name) || randomName(); AU.flm.layer(4); }
    else if (ph === 'confirm') { shot('stood'); card('flAsk'); }
    else if (ph === 'wink') { card(null); shot('exit'); X.hitIn = AU.flm.sting(2.4); const s = $('flSend'); s.hidden = false; void s.offsetWidth; s.classList.add('on'); }
  }
  // where it is, and how it moves, by the phase
  function story(dt) {
    const c = X.ch, t = X.pt, F = X.flags, once = k => F[k] ? false : (F[k] = true), I = X.I;
    c.air = false; c.sq = 0; c.rise = 0; let wy = 0, wp = 0.06;
    if (X.ph === 'wait') { tiltAt(0); return; }
    if (X.ph === 'sky') { tiltAt(0); if (t >= 0.9 && once('down')) shot('barrel'); if (t >= 2.3) go('barrel'); return; }
    if (X.ph === 'barrel') {
      // it rocks one way, the other, harder, and over it goes
      const W = [[0.5, 1.12, -0.14], [1.12, 1.74, 0.17], [1.74, 2.36, -0.22]]; let a = 0;
      for (const [s, e, m] of W) if (t >= s && t < e) a = m * Math.sin(Math.PI * (t - s) / (e - s));
      if (t >= 2.5 && t < 3.12) a = (Math.PI / 2) * eIn((t - 2.5) / 0.62);
      if (t >= 3.12) { const u = t - 3.12; a = Math.PI / 2 - 0.16 * Math.abs(Math.sin(u * 9)) * Math.exp(-u * 5.5); }
      tiltAt(a);
      if (t >= 0.5 && once('w1')) snd('wobble', 0.75); if (t >= 1.12 && once('w2')) snd('wobble', 0.85); if (t >= 1.74 && once('w3')) snd('wobble', 1);
      if (t >= 2.3 && once('s1')) shot('tip');
      if (t >= 3.1 && once('thud')) { snd('tip', 1); X.cs.shake = 1; buzz([10, 30, 20]); popLid(); for (let i = 0; i < 16; i++) { const a2 = rand() * 6.283, s = rnd(0.4, 1.2); spawn(new V3(X.drum.g.position.x + Math.cos(a2) * 0.3, 0.05, X.drum.g.position.z + Math.sin(a2) * 0.3), new V3(Math.cos(a2) * s, rnd(0.6, 1.4), Math.sin(a2) * s), rnd(0.006, 0.012), new THREE.Color(0xC9874D)); } }
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
      if (t >= 9.0) go('iris');
    }
    if (X.ph === 'iris' || X.ph === 'style' || X.ph === 'paint') {
      tiltAt(Math.PI / 2);
      if (X.stood) { c.x = LAND.x; c.z = LAND.z; c.y = PR; c.yaw += (0 - c.yaw) * Math.min(1, dt * 8); wy = Math.sin(X.t * 0.5) * 0.12; wp = 0.12; }
      else { c.y += (eyeY() - c.y) * Math.min(1, dt * 6); wy = Math.sin(X.t * 0.6) * 0.25 + Math.sin(X.t * 1.7) * 0.06; wp = 0.08; }
    }
    if (X.ph === 'form') {
      tiltAt(Math.PI / 2);
      // it gathers itself up out of the paint, crouches, and jumps clear
      if (once('f0')) { snd('form', 1); I.face && I.face('focus', 1.2); }
      const ru = eOut(t / 0.9); c.y = eyeY() + (PR - eyeY()) * ru; c.wade = 1;
      if (t < 0.9 && rand() < dt * 30) { const a = rand() * 6.283; spawn(new V3(c.x + Math.cos(a) * 0.2, 0.02, c.z + Math.sin(a) * 0.2), new V3(Math.cos(a) * 0.4, rnd(0.8, 1.6), Math.sin(a) * 0.4), rnd(0.01, 0.02)); }
      if (t > 0.95 && t < 1.2) c.sq = 0.35 * Math.sin((t - 0.95) / 0.25 * Math.PI);
      const J0 = 1.2, J1 = 1.95;
      if (t >= J0 && once('jump')) { AU.jump && AU.jump(); AU.vox && AU.vox('hyah', 0.8); ripple(c.x, c.z, 1); for (let i = 0; i < 14; i++) { const a = rand() * 6.283, s = rnd(0.6, 1.6); spawn(new V3(c.x + Math.cos(a) * 0.2, 0.04, c.z + Math.sin(a) * 0.2), new V3(Math.cos(a) * s, rnd(2, 3.4), Math.sin(a) * s), rnd(0.014, 0.028)); } }
      if (t >= J0 && t < J1) { const u = (t - J0) / (J1 - J0), H = 0.85; c.x = C0.x + (LAND.x - C0.x) * u; c.z = C0.z + (LAND.z - C0.z) * u; c.h = 4 * H * u * (1 - u); c.y = PR + c.h; c.vy = 4 * H * (1 - 2 * u) / (J1 - J0); c.air = true; c.rise = u < 0.5 ? 0.6 : 0.2;
        if (rand() < dt * 25) spawn(new V3(c.x, c.y - 0.1, c.z), new V3(rnd(-0.3, 0.3), -0.5, rnd(-0.3, 0.3)), rnd(0.01, 0.018)); }
      if (t >= J1) { c.x = LAND.x; c.z = LAND.z; c.y = PR; c.h = 0; const k = t - J1; c.sq = Math.max(0, 0.5 * Math.exp(-k * 7) * Math.cos(k * 16)); }
      if (t >= J1 && once('land')) { AU.land && AU.land(0.9); snd('splat', 1.1); X.cs.shake = 0.7; buzz(18); splat(LAND.x, LAND.z, 0.24); for (let i = 0; i < 18; i++) { const a = i / 18 * 6.283, s = rnd(1, 2); spawn(new V3(LAND.x + Math.cos(a) * 0.2, 0.04, LAND.z + Math.sin(a) * 0.2), new V3(Math.cos(a) * s, rnd(1, 2.2), Math.sin(a) * s), rnd(0.01, 0.022)); } }
      // and shakes the paint off
      if (t >= J1 + 0.38 && once('shake')) { I.shake && I.shake(1); I.coatBurst && I.coatBurst(0.16); AU.vox && AU.vox('brr', 0.6); }
      if (t >= J1 + 0.3) c.wade = Math.max(0.25, c.wade - dt * 1.5);
      if (t >= J1 + 1.45) go('name');
    }
    if (X.ph === 'name' || X.ph === 'confirm') { tiltAt(Math.PI / 2); c.x = LAND.x; c.z = LAND.z; c.y = PR; c.yaw += (0 - c.yaw) * Math.min(1, dt * 8); wy = Math.sin(X.t * 0.5) * 0.12; wp = 0.12;
      if (Math.floor(X.t / 3.3) !== X.flags.gl) { X.flags.gl = Math.floor(X.t / 3.3); if (X.flags.gl % 3 === 2) { X.ch.pop = 0.7; I.blink && I.blink(); } } }
    if (X.ph === 'wink') {
      tiltAt(Math.PI / 2); c.h = c.air ? c.h : 0;
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
  const eyeY = () => -0.3; // (sunk to its eyes: the top of its head and its eyes out of the paint)
  function tiltAt(a) {
    // the drum rocks on the edge of its base it leans toward (lying down, it rests on its rims)
    const B = X.drum.g, sg = a >= 0 ? 1 : -1, piv = BR.base.clone().addScaledVector(TIP, sg * BR.R);
    _q.setFromAxisAngle(TIPAX, a); const rel = BR.base.clone().sub(piv).applyQuaternion(_q);
    B.position.copy(piv).add(rel); B.position.y += 0.012 * Math.pow(Math.max(0, Math.sin(a)), 6); B.quaternion.copy(_q);
    B.updateMatrixWorld(true); X.mouth.set(0, BR.H, 0).applyMatrix4(B.matrixWorld);
  }
  function popLid() { const L = X.lid, m = X.drum.lid; m.updateMatrixWorld(); m.getWorldPosition(L.p); X.drum.g.remove(m); X.sc.add(m); m.position.copy(L.p); m.quaternion.copy(X.drum.g.quaternion); L.on = false; L.v.set(TIP.x * 1.6 + 0.4, 1.6, TIP.z * 1.6 + 0.5); L.w.set(rnd(-6, 6), rnd(-3, 3), rnd(4, 9)); }
  function lidTick(dt) {
    const L = X.lid; if (L.on || L.rest) return; const m = X.drum.lid;
    L.v.y -= 9 * dt; m.position.addScaledVector(L.v, dt); m.rotation.x += L.w.x * dt; m.rotation.z += L.w.z * dt;
    if (m.position.y < 0.02) { m.position.y = 0.02; if (Math.abs(L.v.y) > 0.8) { L.v.y = -L.v.y * 0.35; L.v.x *= 0.6; L.v.z *= 0.6; L.w.multiplyScalar(0.5); AU.bonk && AU.bonk(); } else { L.rest = true; m.rotation.set(0, m.rotation.y, 0); } }
  }
  function streamAt(t) {
    const S = X.stream, U = S.U; if (t < 3.15 || t > 6.4) { S.m.visible = false; return; } S.m.visible = true;
    U.uP0.value.copy(X.mouth); U.uV0.value.copy(TIP).multiplyScalar(0.9 * (1 - 0.6 * clamp((t - 4.8) / 1.4, 0, 1))); U.uV0.value.y = 0.15;
    U.uT.value = Math.sqrt(2 * X.mouth.y / 9 + 0.0001) + 0.02;
    U.uR.value = 0.075 * Math.min(1, (t - 3.15) / 0.12) * (1 - 0.5 * clamp((t - 5) / 1.3, 0, 1)); U.uCut.value = clamp((t - 5.95) / 0.4, 0, 1);
    const g = new V3().copy(X.mouth).addScaledVector(U.uV0.value, U.uT.value); X.floor.U.uM.value.set(g.x, g.z);
    if (rand() < 0.5) ripple(g.x, g.z, 0.15);
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
    // its rim and fin light from the sun, seen from the intro's camera
    if (I.ax && I.ax.look) I.ax.look.U.uKeyDir.value.copy(SUN).transformDirection(X.pc.matrixWorldInverse);
    X.floor.U.uHole.value.set(c.x, c.z, 0.17, X.hold.visible && c.y < PR * 0.9 && !c.air && Math.hypot(c.x - C0.x, c.z - C0.z) < 0.3 ? 1 - clamp((c.y - eyeY()) / (PR - eyeY()), 0, 1) * 0.6 : 0);
  }
  // ---- each frame ----
  function frame(rdt) {
    if (!X) return false; const dt = Math.min(0.05, rdt); X.t += dt; X.pt += dt;
    if (X.ph === 'wait' && X.ready) go('sky');
    if (AU.flm) AU.flm.wake();
    story(dt); camTick(dt); lidTick(dt); dropsTick(dt); charTick(dt); shadowsTick();
    const U = X.floor.U, H = viewH; U.uT.value = X.t; U.uR.value = X.R; U.uMR.value = X.MR; U.uCol.value.copy(X.paint); U.uPearl.value = X.pearl;
    X.stream.U.uTime.value = X.t; X.stream.U.uCol.value.copy(X.paint); X.stream.U.uPearl.value = X.pearl; X.grit.U.uT.value = X.t; X.grit.U.uPx.value = renderer.getPixelRatio() * H / 780;
    renderer.setRenderTarget(null); renderer.render(X.sc, X.pc);
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
    try { build(); buildUi(); shadowsInit(); }
    catch (e) { console.warn('intro:', e && e.message); try { if (UI) UI.el.remove(); } catch (x) {} UI = null; X = null; api.live = false; api.hush = false; document.body.classList.remove('flon'); window.removeEventListener('keydown', keyStop, true); AU.music('menu'); const ask = () => { if (!store.orient) openOrient(); }; if (bootHold) { const w = setInterval(() => { if (!bootHold) { clearInterval(w); ask(); } }, 100); } else ask(); return; }
    AU.flm.load(); AU.music('intro');
    const start = () => { X.ready = true; AU.flm.play(); };
    const orient = () => { if (store.orient) return start(); openOrient(); const w = setInterval(() => { if ($('orient').hidden) { clearInterval(w); start(); } }, 120); };
    if (bootHold) { const w = setInterval(() => { if (!bootHold) { clearInterval(w); orient(); } }, 100); } else orient();
  };
  api.frame = rdt => api.live && !!X && frame(rdt);
  api.after = after;
  api.busy = () => api.live || !!api.jin;
  api.go = ph => go(ph); // (for tests: straight to a phase)
  api._x = () => X; // (for tests: the scene itself)
  api.peek = () => X ? { ph: X.ph, pt: X.pt, t: X.t, hit: X.hitIn || 0, lay: AU.flm ? AU.flm.lay : 0, drops: X.drop.length, calls: renderer.info.render.calls, tris: renderer.info.render.triangles } : null; // (for tests: where it's got to)
  return api;
})();
