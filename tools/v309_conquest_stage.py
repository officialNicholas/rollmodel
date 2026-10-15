"""v309 (Season Conquest stage, built in the v307 round): the Sunken Keep, a small round boss arena at the bottom of the sea, built by hand to the concept
picture, and a stage preview to walk it from Choose Event.

- One fixed scene (nothing generated, nothing random in where things stand): a round floor of big wet flagstones, a low stone parapet
  all round with square posts, the glowing green slime pool in the middle (its spout rising from the centre) inside a low curb of curved
  stones, slime pouring over the wall top in four places and pooling on the floor, slime splashed across the flagstones, tall ruined
  pillars and arches behind the wall at the back, chains from above holding three round iron cages (the pirate skeleton in a red bandana
  at the left, the little blue ghost at the right of centre, the gold coins and crown at the far right), iron lanterns with candles on
  a chain and on wall brackets, white candles on the wall ledge, the crates and the floor, the ship's wheel on the far wall behind the
  pool, pink, purple and orange coral, kelp swaying, wooden crates and barrels with rope in the front corners, the purple skull flag
  draped over the right-hand crate. Beyond the walls the masts, yards, rigging and torn sails of wrecks stand as hazy silhouettes.
- Underwater: a dense blue-teal haze that deepens with distance (the fog), light shafts slanting down from the surface, caustic ripples
  playing over the floor and the walls, bubbles rising everywhere, fine particles drifting, kelp swaying in the current.
- Size: the wall stands at r = 17.5, the pool is r = 4 with its curb to 4.7, so the walkable ring is about 12.8 wide (wider than the
  picture, as the owner asked). The engine's stages are squares with drop edges; this one is round, and
  floorAt, surfaceUnder and blockedAt know the circle, the pool (a hole: fall in and you're out for a moment, like any pit) and its
  curb (a low ledge you can hop onto but not roll over) through CQ.
- Paint: the floor is the engine's paintable floor (coverage, trails, splats as on every stage); the curb and the wall are not.
- Mobile: everything merged by material (vertex colours for the props), sprite glows and baked light pools instead of real lights, the
  existing slime shaders, one small additive shader for the light shafts and one for the caustics, the motes as bubbles; the quality
  ladder, the shadow tiers and the character LOD apply as on every stage.
- Choose Event: the Season Conquest card opens the stage preview (just you on the stage, painting, no clock, no rival; Pause > Menu
  comes back). The card keeps its look but says Stage preview, since it is the stage only: the boss comes later (the space above the
  pool is left empty for it)."""

import json
from v309_conquest_tex import TEX

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

THEME = r"""
// (v309) the Sunken Keep: the Season Conquest boss arena (one fixed scene, conqDress; the theme carries its light, haze and materials)
THEMES.push(
  { id: 'conquest', label: 'Sunken Keep', sf: ['keepFloor', 'keepWall'], uv: 0.2, ft: 0xE0D8F0, st: 0xE8ECEE, dt: 0x8C9AA4, hor: 0x11506C, fog: [7, 54], sky: [0x2A72B0, 0x1F6E98, 0x11506C], low: 0x0A2E44, hemi: [0x8CB4C4, 0x0C1E28], sunPos: [3, 30, 7],
    kit: {}, fill: 'drum', pot: 'barrel', enclosed: true, slime: true, noSea: true, mirror: true, noClouds: true, noMarks: true, ring: { R: 17.6, wall: 17.5, pool: 4.0, rim: 4.7, rimH: 0.22 },
    nrm: [1, 1], rough: [0.3, 0.9], base: { hemiI: 0.56, key: 0xC0E4F0, keyI: 0.42 }, env: { top: 0x1A5A88, hor: 0x135268, gnd: 0x061C28, sun: 0xA8DCF0, sunK: 0.4 }, lk: { hemi: 0.34, key: 1.22 }, grade: { sat: 1.18, con: 1.12, vig: 0.38, bloom: 1.1, expo: 1.0, tint: [0.96, 1.0, 1.04] }, jglow: 0.7,
    edge: 0x7CFF3A, edgeK: 2.2, mkMats: conqMats, dress: conqDress }
);
"""

CORE = r"""
const CONQ_TEX = __CONQ_TEX__;
// ---------- (v309) the Sunken Keep: the Season Conquest boss arena, one fixed scene built to the picture ----------
// The ring: where the floor ends (R), where the wall stands, the pool and its curb
const conqRing = r => ({ R: r.R, R2: r.R * r.R, block: r.wall - PR * 0.9, pool: r.pool, pool2: r.pool * r.pool, rim: r.rim, rim2: r.rim * r.rim, rimH: r.rimH });
// the keep's surfaces: colour maps made with Ludo.ai (tools/v309_conquest_tex.py); the relief and the gloss come from the colour map
// itself once it loads (a height map from its lights and darks: the grooves between the stones sit low, so they read as grooves)
function imgSurf(url, S, k, rLo, rHi, rGam) {
  const mk = () => { const c = document.createElement('canvas'); c.width = c.height = S; return c; }, C = mk(), Hc = mk(), Rc = mk(), hg = Hc.getContext('2d', { willReadFrequently: true }), rg = Rc.getContext('2d');
  hg.fillStyle = '#808080'; hg.fillRect(0, 0, S, S); rg.fillStyle = gray(rHi); rg.fillRect(0, 0, S, S);
  const map = texOf(C, true), out = HI ? { map, normalMap: heightNormal(Hc, k), roughnessMap: texOf(Rc, false) } : { map };
  const img = new Image(); img.onload = () => { const g = C.getContext('2d'); g.drawImage(img, 0, 0, S, S); map.needsUpdate = true; if (!HI) return;
    const d = g.getImageData(0, 0, S, S).data, n = S * S, lum = new Float32Array(n); for (let i = 0; i < n; i++) lum[i] = (d[i * 4] * 0.3 + d[i * 4 + 1] * 0.59 + d[i * 4 + 2] * 0.11) / 255;
    const bl = new Float32Array(n), W = (x, y) => ((y + S) % S) * S + (x + S) % S; // (a little blur, so the relief is soft)
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) { let v = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) v += lum[W(x + dx, y + dy)]; bl[y * S + x] = v / 9; }
    const hd = hg.createImageData(S, S), rd = rg.createImageData(S, S); for (let i = 0; i < n; i++) { const h = Math.round(bl[i] * 255), r = Math.round((rLo + (rHi - rLo) * Math.pow(1 - bl[i], rGam || 1)) * 255); hd.data[i * 4] = hd.data[i * 4 + 1] = hd.data[i * 4 + 2] = h; hd.data[i * 4 + 3] = 255; rd.data[i * 4] = rd.data[i * 4 + 1] = rd.data[i * 4 + 2] = r; rd.data[i * 4 + 3] = 255; }
    hg.putImageData(hd, 0, 0); rg.putImageData(rd, 0, 0); const nt = heightNormal(Hc, k); out.normalMap.image = nt.image; out.normalMap.needsUpdate = true; out.roughnessMap.needsUpdate = true; };
  img.src = url; return out;
}
SURF_PAINT.keepFloor = () => imgSurf(CONQ_TEX.floor, 768, 3.2, 0.16, 0.7, 1.4); // (wet: the slabs glossy, the grooves dull)
SURF_PAINT.keepWall = () => imgSurf(CONQ_TEX.wall, 512, 2.6, 0.55, 0.95);
SURF_PAINT.keepWood = () => imgSurf(CONQ_TEX.wood, 512, 1.6, 0.6, 0.9);
SURF_PAINT.keepBed = () => imgSurf(CONQ_TEX.seabed, 512, 2.0, 0.7, 1.0);
// (made while Choose Event is open, behind it, so a launch doesn't pay for a stage the player may never open, and the preview doesn't wait)
function conqWarm() { if (conqWarm.done || menuPage !== 'events') return; conqWarm.done = 1; for (const k of ['keepFloor', 'keepWall', 'keepWood', 'keepBed']) surf(k); }
// the pirate flag: a skull and crossbones on purple, with a worn edge
const CONQ_FLAG = makeTex(256, (g, S) => {
  g.fillStyle = '#5A2282'; g.fillRect(0, 0, S, S); const R = rng(307); for (let k = 0; k < 60; k++) { g.fillStyle = 'rgba(30,8,50,' + (0.08 + R() * 0.14) + ')'; g.fillRect(R() * S, R() * S, 6 + R() * 40, 3 + R() * 10); }
  const c = S / 2; g.fillStyle = '#F2EBD8'; g.beginPath(); g.ellipse(c, c - 22, 46, 42, 0, 0, 6.2832); g.fill(); g.fillRect(c - 26, c + 8, 52, 24);
  g.fillStyle = '#5A2282'; for (const dx of [-17, 17]) { g.beginPath(); g.ellipse(c + dx, c - 26, 13, 15, 0, 0, 6.2832); g.fill(); } g.beginPath(); g.moveTo(c, c - 6); g.lineTo(c - 7, c + 8); g.lineTo(c + 7, c + 8); g.closePath(); g.fill();
  for (let k = -2; k <= 2; k++) g.fillRect(c + k * 10 - 2, c + 14, 4, 18);
  g.strokeStyle = '#F2EBD8'; g.lineWidth = 14; g.lineCap = 'round'; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(c - 78 * s, c + 36); g.lineTo(c + 78 * s, c + 92); g.stroke(); }
  g.fillStyle = '#F2EBD8'; for (const [x, y] of [[c - 78, c + 36], [c + 78, c + 36], [c - 78, c + 92], [c + 78, c + 92]]) for (const dy of [-8, 8]) { g.beginPath(); g.arc(x + (x < c ? -4 : 4), y + dy, 9, 0, 6.2832); g.fill(); }
});
// the pool's slime: neon green, rings of ripples spreading from the middle
const CONQ_POOL = makeTex(256, (g, S) => { const c = S / 2, gr = g.createRadialGradient(c, c, 0, c, c, c); gr.addColorStop(0, '#CFFF7A'); gr.addColorStop(0.5, '#8EFF3C'); gr.addColorStop(0.92, '#6CE62A'); gr.addColorStop(1, '#48B018'); g.fillStyle = gr; g.fillRect(0, 0, S, S);
  for (let k = 1; k < 9; k++) { g.strokeStyle = 'rgba(220,255,170,' + (0.28 - k * 0.02) + ')'; g.lineWidth = 3; g.beginPath(); g.arc(c, c, k * 14, 0, 6.2832); g.stroke(); } });
// a bubble: a thin bright ring with a highlight
const CONQ_BUBBLE = (() => { const c = document.createElement('canvas'); c.width = c.height = 32; const g = c.getContext('2d'); g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 2.2; g.beginPath(); g.arc(16, 16, 11, 0, 6.2832); g.stroke(); g.fillStyle = 'rgba(255,255,255,0.35)'; g.beginPath(); g.arc(16, 16, 10, 0, 6.2832); g.fill(); g.fillStyle = 'rgba(255,255,255,0.95)'; g.beginPath(); g.arc(11, 11, 3, 0, 6.2832); g.fill(); return new THREE.CanvasTexture(c); })();
// caustics: a web of bright ripples (two copies of it drift over each other on the floor and the walls)
const CONQ_CAUSTIC = makeTex(256, (g, S) => {
  const R = rng(3073); g.fillStyle = '#000'; g.fillRect(0, 0, S, S); g.lineCap = 'round';
  for (let k = 0; k < 70; k++) { const x = R() * S, y = R() * S, rx = 14 + R() * 30, ry = 10 + R() * 26, a = R() * 6.28, w = 1.5 + R() * 2.5, al = 0.35 + R() * 0.5;
    for (const [dx, dy] of [[0, 0], [S, 0], [-S, 0], [0, S], [0, -S], [S, S], [-S, -S], [S, -S], [-S, S]]) { g.strokeStyle = 'rgba(255,255,255,' + al + ')'; g.lineWidth = w; g.beginPath(); g.ellipse(x + dx, y + dy, rx, ry, a, 0, 6.2832); g.stroke(); } }
});
const conqCausticMat = () => new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 }, uMap: { value: CONQ_CAUSTIC }, uK: { value: HI ? 0.05 : 0.04 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `uniform float uTime, uK; uniform sampler2D uMap; varying vec3 vW;
    void main(){ vec2 p = vW.xz * 0.11 + vW.y * 0.07; float a = texture2D(uMap, p + vec2(uTime * 0.021, uTime * 0.013)).r * texture2D(uMap, p * 1.37 + vec2(-uTime * 0.017, uTime * 0.024)).r;
      gl_FragColor = vec4(vec3(0.6, 0.95, 1.0) * a * uK * 3.0, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
const conqRayMat = () => new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 }, uK: { value: HI ? 1 : 0.85 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  vertexShader: `attribute float aPh; varying vec2 vUv; varying float vPh; void main(){ vUv = uv; vPh = aPh; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `uniform float uTime, uK; varying vec2 vUv; varying float vPh;
    void main(){ float t = uTime; float a = pow(vUv.y, 1.5) * smoothstep(0.0, 0.3, vUv.x) * smoothstep(1.0, 0.7, vUv.x);
      a *= 0.6 + 0.4 * sin(t * 0.37 + vPh) * sin(t * 0.23 + vPh * 1.7 + vUv.x * 3.0); a *= 0.8 + 0.2 * sin(vUv.x * 26.0 + t * 0.3 + vPh);
      gl_FragColor = vec4(vec3(0.55, 0.88, 1.0) * a * 3.2 * uK, a * 0.95);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }` });
function conqMats(M, T) {
  const mk = (c, extra, pbr) => aoPatch(toon(c, extra, pbr));
  M.vc = mk(0xFFFFFF, { vertexColors: true }, { roughness: 0.62 }); M.vcMetal = mk(0xFFFFFF, { vertexColors: true }, { roughness: 0.4, metalness: 0.65 }); { const wd = surf('keepWood'); M.vcWood = mk(0xFFFFFF, { map: wd.map, vertexColors: true }, HI ? { normalMap: wd.normalMap, normalScale: new THREE.Vector2(0.8, 0.8), roughnessMap: wd.roughnessMap, roughness: 1 } : null); }
  M.glowVC = new THREE.MeshBasicMaterial({ vertexColors: true }); { const bd = surf('keepBed'); M.ground = mk(0x6A8C98, { map: bd.map }, HI ? { normalMap: bd.normalMap, normalScale: new THREE.Vector2(0.8, 0.8), roughness: 0.95 } : null); }
  // kelp sways in the current (the sway grows with the height up the blade)
  M.kelp = mk(0x2E9A78, { side: THREE.DoubleSide }, { roughness: 0.7 }); M.kelp.onBeforeCompile = sh => { sh.uniforms.uTime = M.kelpT = { value: 0 };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nuniform float uTime;').replace('#include <begin_vertex>', '#include <begin_vertex>\n{ float k = clamp(position.y / 2.0, 0.0, 1.0); k *= k; transformed.x += sin(uTime * 1.1 + position.x * 0.8 + position.z * 0.6) * 0.16 * k; transformed.z += cos(uTime * 0.9 + position.z * 0.7) * 0.1 * k; }'); };
  M.pool = new THREE.MeshBasicMaterial({ map: CONQ_POOL, color: new THREE.Color(1, 1, 1).multiplyScalar(HI ? 1.5 : 1.15), fog: false }); M.void = new THREE.MeshBasicMaterial({ color: 0x03100A });
  M.puddle = new THREE.MeshBasicMaterial({ map: SEWER_PUDDLES, color: new THREE.Color(1, 1, 1).multiplyScalar(HI ? 1.25 : 1), blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
  M.silh = new THREE.MeshBasicMaterial({ color: 0x072238, fog: true });
  M.water = new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 }, uDeep: { value: new THREE.Color(0x0A2A4E) }, uMid: { value: new THREE.Color(0x11506C) }, uTop: { value: new THREE.Color(0x62CCEC) } }, side: THREE.BackSide, depthWrite: false,
    vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform float uTime; uniform vec3 uDeep, uMid, uTop; varying vec3 vD;
      void main(){ vec3 d = normalize(vD); float y = d.y; vec3 c = y < 0.0 ? mix(uMid, uDeep, smoothstep(0.0, -0.4, y)) : mix(uMid, uTop, pow(smoothstep(0.0, 1.0, y), 1.6));
        float sh = sin(d.x * 9.0 + uTime * 0.6) * sin(d.z * 7.0 - uTime * 0.45) + 0.6 * sin(d.x * 17.0 - uTime * 0.9) * sin(d.z * 13.0 + uTime * 0.7); c += uTop * sh * 0.09 * smoothstep(0.1, 0.9, y);
        c += vec3(0.5, 0.85, 1.0) * pow(max(0.0, dot(d, normalize(vec3(0.1, 1.0, 0.35)))), 14.0) * 0.55;
        gl_FragColor = vec4(c, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }` });
  M.bubble = new THREE.PointsMaterial({ map: CONQ_BUBBLE, size: 0.3, sizeAttenuation: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: new THREE.Color(0x9CD8F0), fog: true }); M.flag = mk(0xFFFFFF, { map: CONQ_FLAG, side: THREE.DoubleSide }, { roughness: 0.8 }); M.ray = conqRayMat(); M.caustic = conqCausticMat();
}
// a cylinder's own uv, scaled to the world (so the courses run round the wall without a seam)
const cylUV = (g, Rr, H, us) => { const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 6.2832 * Rr * us, uv.getY(i) * H * us); return g; };
// a fall of slime over a lip: a sheet curling out and down to the floor (u across it, v from the lip to the bottom)
function conqFallGeo(f, reach, yBot) {
  const nu = 14, nv = 18, pos = [], uv = [], idx = [], drop = f.y0 - yBot;
  for (let j = 0; j <= nv; j++) { const v = j / nv, out = 0.12 + reach * (Math.sqrt(v) * 1.1 - 0.1 * v), y = f.y0 + 0.06 - drop * v * v * (1.05 - 0.05 * v) - 0.04 * v;
    for (let i = 0; i <= nu; i++) { const u = i / nu - 0.5, w = f.w * (1 + 0.3 * v) * u, bulge = 0.1 * Math.cos(u * Math.PI) * (1 - v);
      pos.push(f.x + f.nx * (out + bulge) + f.tx * w, y, f.z + f.nz * (out + bulge) + f.tz * w); uv.push(i / nu, v); } }
  for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) { const a = j * (nu + 1) + i, b = a + 1, c = a + nu + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
function conqDress(K) {
  const { T, M, R, put } = K, us = K.us * 1.7, vc = K.vc, V = SG.V, C = hexC, RG = T.ring, W0 = RG.wall, WT = 0.7, WH = 2.3, DEG = Math.PI / 180; // (the stones smaller than the floor's slabs)
  const ST = C(0x5A6E78), STD = C(0x2A343A), IR = C(0x1C2028), IRL = C(0x3A4048), WD = C(0x6A4A2E), WDD = C(0x3E2A18), WL = C(0x9A7046), ROPE = C(0xC8A070), CRM = C(0xF2ECD8), BONE = C(0xEDE6D4), RD = C(0xD42A2E), GLD = C(0xF2C230);
  const glowC = (c, k) => C(c).multiplyScalar(HI ? k || 2.2 : 1.2);
  const pol = (deg, r, y) => V(Math.cos(deg * DEG) * r, y || 0, Math.sin(deg * DEG) * r);
  // a box stood at polar (deg, r), turned to face the middle (w across, d in and out), in the wall's stone or a vertex colour
  const sbox = (w, h, d, deg, r, y, col) => { const g = SG.box(w, h, d, 0, 0, 0); g.rotateY(-deg * DEG - Math.PI / 2); g.translate(Math.cos(deg * DEG) * r, y, Math.sin(deg * DEG) * r); if (col) vc(M.vc, g, col); else put(M.side, worldUV(g, us)); return g; };
  const chain = (a, b, t) => { const d = V(b.x - a.x, b.y - a.y, b.z - a.z), L = d.length(), n = Math.max(2, Math.round(L / (t || 0.13))); d.normalize(); for (let i = 0; i < n; i++) { const p = V(a.x + d.x * L * (i + 0.5) / n, a.y + d.y * L * (i + 0.5) / n, a.z + d.z * L * (i + 0.5) / n), g = new THREE.BoxGeometry(i % 2 ? 0.024 : 0.075, 0.15, i % 2 ? 0.075 : 0.024); alignZ(g.rotateX(Math.PI / 2), d, p); vc(M.vcMetal, g, IRL); } };
  const candle = (x, y, z, hh, cr) => { vc(M.vc, SG.cyl(cr, cr * 1.06, hh, 8, x, y + hh / 2, z), CRM); for (let k = 0; k < 3; k++) { const a = k * 2.1 + x * 7; vc(M.vc, SG.ball(cr * 0.3, x + Math.cos(a) * cr * 0.95, y + hh - cr * (0.2 + k * 0.3), z + Math.sin(a) * cr * 0.95, 1, 1.6, 1), CRM); } vc(M.vc, SG.cyl(cr * 0.2, cr * 0.2, 0.03, 5, x, y + hh + 0.015, z), IR); K.glow(x, y + hh + 0.1, z, 0.6, 0xFFC27A); if (HI && M.flameCore) put(M.flameCore, flameCoreG(0.5).translate(x, y + hh + 0.05, z)); };
  const candles = (x, y, z, n, big) => { for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + R(), rr = n > 1 ? 0.11 + R() * 0.06 : 0; candle(x + Math.cos(a) * rr, y, z + Math.sin(a) * rr, (big ? 0.2 : 0.12) + R() * 0.24, 0.04 + R() * 0.02); } K.light(x, y + 0.45, z, 3.2, 0xFFB45A, 1.5); };
  // an iron lantern: a cage of a frame round a candle's glass, a ring on top for its chain
  const lantern = (x, y, z, s) => { s = s || 1; vc(M.vcMetal, SG.box(0.3 * s, 0.05 * s, 0.3 * s, x, y + 0.22 * s, z), IR); vc(M.vcMetal, SG.box(0.26 * s, 0.05 * s, 0.26 * s, x, y - 0.2 * s, z), IR); vc(M.vcMetal, SG.cone(0.19 * s, 0.12 * s, x, y + 0.3 * s, z, 6), IR); vc(M.vcMetal, SG.torus(0.05 * s, 0.012 * s, x, y + 0.4 * s, z, 0, 0, 10), IR);
    for (let a = 0.785; a < 6.28; a += 1.5708) vc(M.vcMetal, SG.box(0.024 * s, 0.4 * s, 0.024 * s, x + Math.cos(a) * 0.12 * s, y, z + Math.sin(a) * 0.12 * s), IR);
    vc(M.glowVC, SG.box(0.17 * s, 0.32 * s, 0.17 * s, x, y, z), glowC(0xFFC06A, 2.4)); vc(M.vc, SG.cyl(0.035 * s, 0.035 * s, 0.14 * s, 6, x, y - 0.1 * s, z), CRM); K.glow(x, y, z, 0.9 * s, 0xFFC070); K.light(x, y, z, 4.5 * s, 0xFFB45A, 1.2); };
  // a wooden barrel (upright or lying), stave shading, two iron hoops, a rope round it
  const barrel = (x, y, z, r, h, lay, ry, rope) => { const col = WD, lid = SG.shade(col, 0.72), parts = [SG.paint(SG.cyl(r, r, h, 20, 0, 0, 0), (px, py, pz, o, nx, ny) => { if (Math.abs(ny) > 0.5) return lid; const a = Math.atan2(pz, px), f = ((a / 6.2832 * 14) % 1 + 1) % 1; return SG.shade(col, f < 0.07 ? 0.7 : 0.88 + 0.14 * Math.sin(a * 7)); })];
    for (const yy of [h * 0.3, -h * 0.3]) parts.push(SG.paint(SG.band(r + 0.012, 0.05, 20).translate(0, yy, 0), IRL));
    if (rope) for (const yy of [0.04, -0.06]) parts.push(SG.paint(SG.torus(r + 0.02, 0.025, 0, yy, 0, Math.PI / 2, 0, 20), ROPE));
    for (const g of parts) { if (lay) g.rotateZ(Math.PI / 2); if (ry) g.rotateY(ry); g.translate(x, y + (lay ? r : h / 2), z); vc(M.vcWood, g, null); } };
  // a wooden crate: planks, corner battens, nail heads
  const crate = (x, y, z, s, ry) => { const hs = s / 2, parts = [[SG.box(s, s, s, 0, hs, 0), SG.shade(WL, 0.9 + 0.12 * R())]];
    for (const [ex, ez] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(0.07, s, 0.07, ex * (hs - 0.02), hs, ez * (hs - 0.02)), WDD]);
    for (const yy of [0.04, s - 0.04]) parts.push([SG.box(s + 0.02, 0.07, 0.07, 0, yy, hs - 0.02), WDD], [SG.box(s + 0.02, 0.07, 0.07, 0, yy, -hs + 0.02), WDD], [SG.box(0.07, 0.07, s + 0.02, hs - 0.02, yy, 0), WDD], [SG.box(0.07, 0.07, s + 0.02, -hs + 0.02, yy, 0), WDD]);
    for (const [ex, ez] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(0.1, 0.1, 0.1, ex * (hs - 0.01), s - 0.05, ez * (hs - 0.01)), C(0x3A3530)]);
    for (const [g, c] of parts) { g.rotateY(ry || 0); g.translate(x, y, z); vc(M.vcWood, uvXY(g, (px, py, pz) => [px * 1.3 + pz * 0.7, py * 1.3 + pz * 0.3]), c); } };
  // coral: branching stems with knobbed tips, a fan, a brain; pink, purple or orange, a little lighter toward the tips
  const CORAL = { pink: C(0xFF5FA0), purple: C(0xA860FF), orange: C(0xFF8A3C) };
  const coral = (x, y, z, s, kind, n) => { const col = CORAL[kind]; s *= 1.35; for (let k = 0; k < n + 1; k++) { const a = R() * 6.2832, d = R() * 0.45 * s, px = x + Math.cos(a) * d, pz = z + Math.sin(a) * d, w = R();
      if (w < 0.6) { for (let b = 0, nb = 2 + (R() * 2 | 0); b < nb; b++) { const t = R() * 6.2832, L = (0.35 + R() * 0.45) * s, pts = [V(px, y, pz), V(px + Math.cos(t) * L * 0.3, y + L * 0.55, pz + Math.sin(t) * L * 0.3), V(px + Math.cos(t) * L * 0.5 + (R() - 0.5) * 0.2, y + L * 1.1, pz + Math.sin(t) * L * 0.5 + (R() - 0.5) * 0.2)]; vc(M.vc, SG.curve(pts, 0.04 * s + R() * 0.02, 6, 5), (qx, qy) => SG.shade(col, 0.75 + 0.5 * (qy - y) / (L * 1.1))); vc(M.vc, SG.ball(0.06 * s, pts[2].x, pts[2].y, pts[2].z), SG.shade(col, 1.3)); } }
      else if (w < 0.82) { const g = SG.ball(0.24 * s, 0, 0.22 * s, 0, 1, 1.2, 0.22); g.rotateY(R() * 6.28); g.translate(px, y, pz); vc(M.vc, g, (qx, qy) => SG.shade(col, 0.8 + 0.5 * (qy - y) / (0.5 * s))); }
      else vc(M.vc, SG.ball(0.17 * s, px, y + 0.1 * s, pz, 1, 0.7, 1), (qx, qy, qz) => SG.shade(col, 0.85 + 0.25 * Math.sin(qx * 40) * Math.sin(qz * 40))); } };
  // kelp: tall blades leaning up from the floor (they sway in the kelp material)
  const kelp = (x, y, z, n, s) => { for (let k = 0; k < n; k++) { const L = (1.3 + R() * 1.3) * (s || 1), g = frondGeo(V(0, 0, 0), 0, L, 0.1 + R() * 0.05, 0.2); g.rotateZ(1.1 + R() * 0.3); g.rotateY(R() * 6.2832); g.translate(x + (R() - 0.5) * 0.5, y, z + (R() - 0.5) * 0.5); put(M.kelp, g); } };
  // a round iron cage hanging from a chain: a ring top and bottom, bars round, a domed top with a loop
  const cage = (x, y, z, r, h) => { vc(M.vcMetal, SG.torus(r, 0.035, x, y, z, Math.PI / 2, 0, 20), IRL); vc(M.vcMetal, SG.torus(r, 0.035, x, y + h, z, Math.PI / 2, 0, 20), IRL); vc(M.vcMetal, SG.cyl(r - 0.02, r - 0.02, 0.06, 20, x, y + 0.02, z), STD);
    for (let k = 0; k < 10; k++) { const a = k / 10 * 6.2832; vc(M.vcMetal, SG.box(0.04, h, 0.04, x + Math.cos(a) * r, y + h / 2, z + Math.sin(a) * r), IRL); }
    for (let k = 0; k < 5; k++) { const a = k / 5 * 6.2832 + 0.4; vc(M.vcMetal, SG.tube(V(x + Math.cos(a) * r, y + h, z + Math.sin(a) * r), V(x, y + h + r * 0.8, z), 0.025, 5), IRL); }
    vc(M.vcMetal, SG.torus(0.07, 0.02, x, y + h + r * 0.86, z, 0, 0, 10), IRL); return y + h + r * 0.9; };
  const skull = (x, y, z, s, ry) => { const parts = [[SG.ball(0.19, 0, 0.19, 0, 1, 0.95, 0.9), BONE], [SG.box(0.22, 0.09, 0.16, 0, 0.03, 0.04), BONE], [SG.ball(0.045, 0.07, 0.2, 0.15, 1, 1.2, 0.6), IR], [SG.ball(0.045, -0.07, 0.2, 0.15, 1, 1.2, 0.6), IR], [SG.ball(0.2, 0, 0.28, 0, 1, 0.55, 0.95), RD], [SG.box(0.06, 0.18, 0.03, 0.12, 0.2, -0.17).rotateZ(0.5), RD]];
    for (const [g, c] of parts) { g.scale(s, s, s); g.rotateY(ry || 0); g.translate(x, y, z); vc(M.vc, g, c); } };
  const tenant = (kind, x, y, z, a) => {
    if (kind === 'skeleton') { skull(x, y + 0.62, z, 1, -a + 0.3); vc(M.vc, SG.box(0.07, 0.42, 0.07, x, y + 0.36, z), BONE); for (const yy of [0.5, 0.4, 0.3]) vc(M.vc, SG.torus(0.16, 0.022, x, y + yy, z, Math.PI / 2, 0, 12), BONE);
      for (const s of [-1, 1]) { vc(M.vc, SG.tube(V(x + s * 0.14, y + 0.52, z), V(x + s * 0.3, y + 0.06, z + 0.1), 0.025, 5), BONE); vc(M.vc, SG.tube(V(x + s * 0.1, y + 0.14, z + 0.05), V(x + s * 0.24, y + 0.05, z - 0.3), 0.03, 5), BONE); } }
    else if (kind === 'ghost') { const parts = [[SG.ball(0.26, 0, 0.42, 0, 1, 1.25, 1), glowC(0x7FD8FF, 1.8)], [SG.ball(0.1, 0.13, 0.12, 0.08), glowC(0x7FD8FF, 1.6)], [SG.ball(0.1, -0.13, 0.12, 0.05), glowC(0x7FD8FF, 1.6)], [SG.ball(0.1, 0, 0.1, -0.1), glowC(0x7FD8FF, 1.6)], [SG.ball(0.045, 0.09, 0.5, 0.22, 1, 1.4, 0.6), C(0x08203A)], [SG.ball(0.045, -0.09, 0.5, 0.22, 1, 1.4, 0.6), C(0x08203A)]];
      for (const [g] of parts) g.rotateY(-a + Math.PI / 2); const m = new THREE.Mesh(vcGeoIdx(parts), M.glowVC); m.position.set(x, y, z); m.layers.enable(3); K.add(m); K.anim({ tick(dt, t) { m.position.y = y + 0.1 * Math.sin(t * 1.3); m.rotation.y = 0.2 * Math.sin(t * 0.7); } });
      K.glow(x, y + 0.45, z, 1.8, 0x6AC8FF); K.light(x, y + 0.4, z, 5, 0x6AC8FF, 0.8); }
    else if (kind === 'gold') { vc(M.vcMetal, SG.ball(0.42, x, y + 0.02, z, 1, 0.5, 1), (px, py) => SG.shade(GLD, 0.8 + 0.35 * (py - y) / 0.2)); for (let k = 0; k < 9; k++) { const t = R() * 6.28, d = R() * 0.3; vc(M.vcMetal, SG.cyl(0.065, 0.065, 0.02, 8, x + Math.cos(t) * d, y + 0.2 - d * 0.35 + 0.01, z + Math.sin(t) * d), SG.shade(GLD, 1.1)); }
      vc(M.vcMetal, SG.torus(0.16, 0.045, x, y + 0.27, z, Math.PI / 2, 0, 14), GLD); for (let k = 0; k < 5; k++) { const t = k / 5 * 6.2832; vc(M.vcMetal, SG.cone(0.04, 0.12, x + Math.cos(t) * 0.16, y + 0.34, z + Math.sin(t) * 0.16, 5), GLD); } vc(M.vc, SG.ball(0.05, x + 0.16, y + 0.3, z), C(0xE0304A)); K.glow(x, y + 0.25, z, 1.0, 0xFFD070); }
  };
  // a chain from high above (the ceiling of the world) down to y, then a cage with its tenant
  const hangCage = (kind, deg, r, y) => { const p = pol(deg, r), top = cage(p.x, y, p.z, 0.8, 1.5); chain(V(p.x, 15, p.z), V(p.x, top, p.z)); tenant(kind, p.x, y + 0.06, p.z, deg * DEG); };
  const falls = [];
  return {
    plain() { return true; }, skipBody() { return true; }, roundMats() { return null; }, noPlinth: true, spot() {}, noScatter() { return true; },
    // the pieces you can bump into: the crates and barrels in the front corners (their boxes are in the layout; this is how they look)
    box(b, I) { const { cx, cz } = I, kind = b[7] || '';
      if (kind === 'crateL') { crate(cx - 0.47, 0, cz - 0.1, 0.94, -0.06); crate(cx + 0.47, 0, cz + 0.08, 0.9, 0.08); crate(cx - 0.3, 0.94, cz + 0.05, 0.68, 0.3); candles(cx + 0.45, 0.9, cz, 3, true); candles(cx - 0.3, 1.62, cz + 0.05, 1, true); K.hull(SG.box(1.96, 1.1, 1.14, cx, 0.55, cz)); }
      else if (kind === 'crateR') { crate(cx + 0.47, 0, cz - 0.1, 0.94, 0.05); crate(cx - 0.47, 0, cz + 0.08, 0.9, -0.08); crate(cx + 0.3, 0.94, cz + 0.05, 0.68, -0.25); candles(cx - 0.45, 0.9, cz, 2, true); candles(cx + 0.3, 1.62, cz + 0.05, 1, true); K.hull(SG.box(1.96, 1.1, 1.14, cx, 0.55, cz));
        // the purple skull flag draped over its side (hung over the crate's edge, toward the middle of the arena)
        const g = gridGeo(10, 8, (u, v, o) => { const over = v < 0.3, z = cz + 0.08 + (u - 0.5) * 0.9, y = over ? 0.94 + 0.02 - 0.015 * Math.sin(u * 9) : 0.96 - (v - 0.3) / 0.7 * 1.05, x = over ? cx - 0.47 - (0.3 - v) / 0.3 * 0.42 + 0.45 : cx - 0.47 + 0.47 + 0.02 + 0.04 * Math.sin(u * 7 + v * 5) * (v - 0.3); o.set(x, y, z); });
        uvXY(g, (px, py, pz) => [(pz - cz + 0.5) / 1.0 * 0.95, (py - 0.0) / 1.6]); const fm = new THREE.Mesh(g, M.flag); fm.layers.enable(3); K.add(fm); }
      else if (kind === 'barrel') { barrel(cx, 0, cz, 0.44, 0.9, false, b[8] || 0, true); K.hull(SG.cyl(0.5, 0.5, 1.0, 18, cx, 0.5, cz)); if (b[9]) candles(cx, 0.9, cz, 2, true); }
    },
    // the pool in the middle: a pit of glowing slime a little below the floor, bubbling, the spout rising from its heart, a curb of
    // curved dark stones round it
    hole() {
      const pr = RG.pool, rr = RG.rim, rh = RG.rimH;
      put(M.void, new THREE.CircleGeometry(pr + 0.3, SEG(44)).rotateX(-Math.PI / 2).translate(0, -0.72, 0));
      put(M.pool, new THREE.CircleGeometry(pr + 0.2, SEG(44)).rotateX(-Math.PI / 2).translate(0, -0.14, 0));
      const sp = new THREE.Mesh(new THREE.CircleGeometry(pr + 0.1, SEG(44)).rotateX(-Math.PI / 2), SLIME_SPLASH_MAT); sp.position.y = -0.11; sp.renderOrder = 3; K.add(sp);
      const pg = new THREE.CylinderGeometry(0.17, 0.3, 2.0, SEG(12), 6, true), uv = pg.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i), 1 - uv.getY(i)); pg.translate(0, 0.86, 0);
      const pm = new THREE.Mesh(pg, SLIME_FALL_MAT); pm.renderOrder = 2; K.add(pm); K.anim({ tick(dt, t) { pm.position.x = 0.1 * Math.sin(t * 2.3); pm.position.z = 0.1 * Math.cos(t * 1.9); pm.rotation.z = 0.08 * Math.sin(t * 2.7); pm.rotation.x = 0.08 * Math.cos(t * 2.1); pm.scale.set(1 + 0.1 * Math.sin(t * 3.1), 1 + 0.05 * Math.sin(t * 1.3), 1 + 0.1 * Math.cos(t * 2.7)); } });
      vc(M.glowVC, SG.ball(0.3, 0, 1.9, 0, 1, 1.25, 1), glowC(0xA8FF60, 2.0)); for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832; vc(M.glowVC, SG.ball(0.1 + (k % 2) * 0.05, Math.cos(a) * 0.55, 0.05 + (k % 3) * 0.08, Math.sin(a) * 0.55, 1, 1.4, 1), glowC(0x9CFF4A, 1.8)); } // (the top of the spout and the crown of splashes at its foot)
      for (const [y, s] of [[0.0, 2.6], [0.9, 1.6], [1.8, 1.3]]) K.glow(0, y, 0, s, 0x6CE030);
      K.light(0, 0.3, 0, 7.5, 0x8CFF3A, 2.0); K.steam(0, -0.05, 0, 1.0, 1.2, HI ? 0.7 : 0.4, 0.8); for (let k = 0; k < 3; k++) { const a = k * 2.0944 + 0.5; K.steam(Math.cos(a) * 2.2, -0.08, Math.sin(a) * 2.2, 1.0, 1.0, HI ? 0.4 : 0.25, 0.5); }
      // the curb: 20 curved stones, each a little different, dark, over the pit's lip; the pit's inner wall
      put(M.dark, cylUV(new THREE.CylinderGeometry(pr - 0.015, pr - 0.015, rh + 0.72, SEG(44), 1, true).scale(-1, 1, 1).translate(0, (rh - 0.72) / 2, 0), pr, rh + 0.7, us));
      for (let k = 0; k < 20; k++) { const a0 = k / 20 * 6.2832, a1 = (k + 1) / 20 * 6.2832 + 0.004, hh = rh + (R() - 0.5) * 0.06, g = new THREE.CylinderGeometry(rr, rr, hh, 6, 1, true, a0, a1 - a0), gi = new THREE.CylinderGeometry(pr - 0.05, pr - 0.05, hh, 6, 1, true, a0, a1 - a0).scale(-1, 1, 1), gt = new THREE.RingGeometry(pr - 0.05, rr, 6, 1, -a1 - Math.PI / 2, a1 - a0).rotateX(-Math.PI / 2);
        g.translate(0, hh / 2, 0); gi.translate(0, hh / 2, 0); gt.translate(0, hh, 0); const sh = 0.7 + R() * 0.5; vc(M.vc, g, SG.shade(C(0x262E36), sh * 0.9)); vc(M.vc, gt, SG.shade(C(0x262E36), sh * 1.15)); vc(M.vc, gi, SG.shade(C(0x1C2228), sh)); } // (open sectors: a closed one's cap is a wedge to the middle, a lid over the pool)
      K.hull(new THREE.CylinderGeometry(rr + 0.06, rr + 0.06, rh + 0.1, 40, 1, true).translate(0, rh / 2, 0));
      for (let k = 0; k < 6; k++) { const a = k / 6 * 6.2832 + 0.3, L = 0.12 + R() * 0.12; vc(M.glowVC, new THREE.ConeGeometry(0.035, L, 6).rotateX(Math.PI).translate(Math.cos(a) * (rr + 0.03), rh - L / 2, Math.sin(a) * (rr + 0.03)), glowC(0x8CFF3A, 1.8)); }
    },
    // the whole scene round the floor
    outer() {
      // the sea floor beyond the walls, dark, fading into the haze; rubble on it
      put(M.ground, worldUV(new THREE.RingGeometry(W0 - 0.2, 80, SEG(64), 1).rotateX(-Math.PI / 2).translate(0, -0.06, 0), K.us));
      for (let k = 0; k < 40; k++) { const a = R() * 6.2832, d = W0 + 1.5 + R() * 14, s = 0.25 + R() * 0.6; vc(M.vc, SG.ball(s, Math.cos(a) * d, -0.06 + s * 0.35, Math.sin(a) * d, 1, 0.6, 1), SG.shade(STD, 0.6 + R() * 0.5)); }
      // the parapet: a low wall of stone blocks all round, a cap course on top, square posts with caps every 30 degrees
      put(M.side, cylUV(new THREE.CylinderGeometry(W0, W0, WH + 0.1, SEG(64), 1, true).scale(-1, 1, 1).translate(0, WH / 2 - 0.05, 0), W0, WH, us));
      put(M.side, cylUV(new THREE.CylinderGeometry(W0 + WT, W0 + WT, WH + 0.1, SEG(64), 1, true).translate(0, WH / 2 - 0.05, 0), W0 + WT, WH, us));
      put(M.side, worldUV(new THREE.RingGeometry(W0 - 0.08, W0 + WT + 0.08, SEG(64), 1).rotateX(-Math.PI / 2).translate(0, WH, 0), us));
      put(M.dark, cylUV(new THREE.CylinderGeometry(W0 - 0.08, W0 - 0.08, 0.16, SEG(64), 1, true).scale(-1, 1, 1).translate(0, WH - 0.06, 0), W0, 0.16, us));
      K.hull(new THREE.CylinderGeometry(W0 + WT + 0.06, W0 + WT + 0.06, WH + 0.12, 48, 1, true).translate(0, WH / 2, 0));
      for (let k = 0; k < 12; k++) { const deg = k * 30 + 15, pw = 1.0, ph = WH + 0.8; sbox(pw, ph, pw, deg, W0 + WT / 2 + 0.02, ph / 2); sbox(pw + 0.18, 0.16, pw + 0.18, deg, W0 + WT / 2 + 0.02, ph + 0.08); sbox(pw * 0.55, 0.22, pw * 0.55, deg, W0 + WT / 2 + 0.02, ph + 0.27, SG.shade(ST, 0.7));
        K.hull(sbox(pw + 0.1, ph + 0.1, pw + 0.1, deg, W0 + WT / 2 + 0.02, ph / 2, C(0))); }
      // the ruins behind the wall at the back: tall broken pillars, two arches, chains hanging from above
      const pillar = (deg, r, h, cap) => { const p = pol(deg, r), w = 1.1; put(M.side, worldUV(SG.box(w, h, w, p.x, h / 2 - 0.1, p.z), us)); put(M.side, worldUV(SG.box(w + 0.3, 0.3, w + 0.3, p.x, 0.15, p.z), us)); if (cap) put(M.side, worldUV(SG.box(w + 0.34, 0.26, w + 0.34, p.x, h + 0.03, p.z), us)); K.hull(SG.box(w + 0.1, h + 0.1, w + 0.1, p.x, h / 2, p.z)); return p; };
      const arch = (a, b, y) => { const d = V(b.x - a.x, 0, b.z - a.z), L = d.length(); const g = SG.box(L + 1.1, 0.7, 1.2, 0, 0, 0); g.rotateY(-Math.atan2(d.z, d.x)); g.translate((a.x + b.x) / 2, y, (a.z + b.z) / 2); put(M.side, worldUV(g, us)); K.hull(SG.box(L + 1.2, 0.8, 1.3, 0, 0, 0).rotateY(-Math.atan2(d.z, d.x)).translate((a.x + b.x) / 2, y, (a.z + b.z) / 2)); };
      { const a = pillar(160, 20.4, 6.8, true), b = pillar(138, 20.8, 8.4, true), c = pillar(116, 20.2, 5.8, false); arch(a, b, 7.0); pillar(178, 21.6, 4.8, false);
        const d = pillar(22, 20.6, 7.2, true), e = pillar(44, 21.0, 9.0, true), f = pillar(66, 20.4, 5.6, false); arch(d, e, 7.4); pillar(2, 21.6, 4.6, false); pillar(90, 23, 4.0, false); }
      for (const [deg, r] of [[150, 19.4], [128, 22], [34, 19.6], [56, 22.2], [100, 21]]) { const p = pol(deg, r); chain(V(p.x, 15, p.z), V(p.x, 7.5 + R() * 2, p.z), 0.14); }
      // the cages: the pirate skeleton at the left, the little ghost at the right of centre, the gold and the crown at the far right
      hangCage('skeleton', 310, 8.5, 4.0); hangCage('ghost', 112, 13.5, 5.4); hangCage('gold', 234, 8.4, 3.6);
      // lanterns: a big one on a chain at the left, two on brackets on the wall posts
      { const p = pol(306, 9.9); chain(V(p.x, 15, p.z), V(p.x, 4.5, p.z)); lantern(p.x, 3.4, p.z, 2.6);
        for (const [deg, s] of [[18, 1.3], [162, 1.35]]) { const q = pol(deg, W0 - 0.45), bx = pol(deg, W0 + 0.1); vc(M.vcMetal, SG.tube(V(bx.x, WH + 0.45, bx.z), V(q.x, WH + 1.15, q.z), 0.035, 6), IRL); vc(M.vcMetal, SG.tube(V(bx.x, WH + 1.2, bx.z), V(q.x, WH + 1.15, q.z), 0.035, 6), IRL); chain(V(q.x, WH + 1.15, q.z), V(q.x, WH + 0.95, q.z)); lantern(q.x, WH + 0.5, q.z, s); } }
      // the ship's wheel on the far wall behind the pool, on a short post
      { const deg = 100, q = pol(deg, W0 + 0.25), n = V(-Math.cos(deg * DEG), 0, -Math.sin(deg * DEG)), cy = WH + 1.6; vc(M.vcWood, SG.box(0.16, 1.8, 0.16, q.x, WH + 0.8, q.z), WDD);
        const at = o => V(q.x + n.x * o, cy, q.z + n.z * o);
        vc(M.vcWood, alignZ(SG.torus(1.2, 0.1, 0, 0, 0, 0, 0, 28), n, at(0.2)), WDD); vc(M.vcWood, alignZ(SG.torus(0.55, 0.07, 0, 0, 0, 0, 0, 20), n, at(0.2)), WDD); vc(M.vcWood, alignZ(SG.cyl(0.24, 0.24, 0.26, 12, 0, 0, 0).rotateX(Math.PI / 2), n, at(0.2)), WD);
        for (let k = 0; k < 8; k++) { const t = k / 8 * 6.2832; vc(M.vcWood, alignZ(new THREE.BoxGeometry(0.1, 2.4, 0.08).rotateZ(t), n, at(0.2)), WD); vc(M.vcWood, alignZ(SG.cyl(0.06, 0.05, 0.4, 8, 0, 0, 0).rotateZ(t).translate(-Math.sin(t) * 1.5, Math.cos(t) * 1.5, 0), n, at(0.2)), WDD); } }
      // the slime falls: over the wall top in four places, each from a broken spout, pooling on the floor below
      for (const [deg, w] of [[10, 2.2], [48, 1.3], [132, 2.0], [172, 1.2]]) { const a = deg * DEG, nx = -Math.cos(a), nz = -Math.sin(a), tx = -nz, tz = nx, lip = pol(deg, W0 - 0.05);
        sbox(w + 0.5, 0.26, 0.9, deg, W0 + 0.2, WH + 0.13); vc(M.glowVC, SG.box(w + 0.1, 0.1, 0.7, 0, 0, 0).rotateY(-a - Math.PI / 2).translate(Math.cos(a) * (W0 + 0.3), WH + 0.3, Math.sin(a) * (W0 + 0.3)), glowC(0x8CFF3A, 1.6));
        const f = { x: lip.x, z: lip.z, nx, nz, tx, tz, y0: WH + 0.3, w, reach: 0.9 + w * 0.3 }; falls.push(f);
        K.glow(lip.x + nx * 0.3, WH + 0.35, lip.z + nz * 0.3, 1.2, 0x6CE030); K.glow(lip.x + nx * f.reach, 0.25, lip.z + nz * f.reach, 2.0, 0x6CE030); K.light(lip.x + nx * f.reach, 0.3, lip.z + nz * f.reach, 5.5, 0x8CFF3A, 1.6); K.steam(lip.x + nx * f.reach, 0.2, lip.z + nz * f.reach, 0.6, 1.2, HI ? 0.7 : 0.4, 0.8); }
      { const fm = new THREE.Mesh(mergeGeos(falls.map(f => conqFallGeo(f, f.reach, 0.02)), true), SLIME_FALL_MAT); fm.renderOrder = 2; K.add(fm);
        const sm = new THREE.Mesh(mergeGeos(falls.map(f => new THREE.CircleGeometry(f.w * 0.9, 28).rotateX(-Math.PI / 2).translate(f.x + f.nx * f.reach, 0.03, f.z + f.nz * f.reach)), true), SLIME_SPLASH_MAT); sm.renderOrder = 3; K.add(sm); }
      // slime splashed over the flagstones: round the pool, under the falls, and in pools here and there
      { const pl = [], pud = (x, z, sz, k, rot) => { const g = atlasUV(new THREE.PlaneGeometry(sz, sz), k, 2); g.rotateX(-Math.PI / 2); g.rotateY(rot); g.translate(x, 0.012, z); pl.push(g); };
        for (const f of falls) pud(f.x + f.nx * (f.reach + 0.3), f.z + f.nz * (f.reach + 0.3), 2.2 + f.w, 1, R() * 6.28);
        for (const [deg, r, sz, k] of [[250, 6.0, 3.4, 1], [275, 5.6, 2.6, 0], [300, 8.4, 2.4, 2], [220, 8.8, 2.0, 3], [120, 6.2, 2.8, 1], [95, 7.0, 2.2, 0], [60, 6.4, 2.6, 2], [160, 10.4, 1.8, 3], [20, 10.6, 1.9, 2], [330, 6.3, 2.1, 1], [200, 6.1, 2.3, 0], [350, 13.5, 1.6, 3], [140, 13.2, 1.4, 2], [75, 12.0, 2.0, 1], [185, 12.6, 1.7, 2], [265, 11.2, 2.2, 0], [310, 13.8, 1.5, 3], [40, 9.0, 1.6, 1]]) { const p = pol(deg, r); pud(p.x, p.z, sz, k, deg * 0.7); }
        const pm = new THREE.Mesh(mergeGeos(pl, true), M.puddle); pm.renderOrder = 5; pm.layers.set(2); K.add(pm); }
      // candles: along the wall's ledge, on the posts, on the floor by the wall
      for (const [deg, n] of [[98, 3], [108, 1], [72, 2], [128, 2], [48, 1], [36, 2], [174, 2], [8, 1], [212, 1], [320, 2], [300, 1], [240, 2], [60, 1], [146, 1], [84, 2], [118, 1], [22, 2], [156, 1], [188, 2], [336, 1], [352, 2], [262, 1], [278, 2], [138, 2], [64, 1]]) { const p = pol(deg, W0 + WT / 2); candles(p.x, WH, p.z, n, true); }
      for (const deg of [105, 75, 345, 255]) { const p = pol(deg, W0 + WT / 2 + 0.02); candles(p.x, WH + 0.6 + 0.35, p.z, 1, true); }
      for (const [deg, n] of [[188, 3], [118, 2], [52, 2], [330, 3], [262, 1], [236, 2], [300, 2], [10, 2], [150, 1], [80, 2]]) { const p = pol(deg, W0 - 0.7); candles(p.x, 0, p.z, n); }
      // coral at the foot of the wall and on the stones, kelp swaying by it
      for (const [deg, r, kind, s, n] of [[204, 16.5, 'pink', 2.0, 4], [176, 16.7, 'purple', 1.5, 3], [142, 16.6, 'orange', 1.8, 4], [112, 16.7, 'pink', 1.6, 3], [92, 16.5, 'orange', 1.5, 3], [58, 16.7, 'purple', 1.8, 4], [26, 16.6, 'pink', 2.0, 4], [344, 16.7, 'orange', 1.6, 3], [238, 16.3, 'purple', 1.6, 3], [312, 16.4, 'pink', 1.5, 3], [250, 12.2, 'pink', 1.4, 3], [290, 12.2, 'orange', 1.2, 2], [270, 16.5, 'purple', 1.4, 3], [8, 16.6, 'orange', 1.3, 2]]) { const p = pol(deg, r); coral(p.x, 0, p.z, s, kind, n); }
      for (const [deg, r, n] of [[186, 16.9, 3], [124, 16.8, 2], [66, 16.9, 3], [336, 16.8, 2], [270, 16.9, 2], [40, 16.7, 2], [100, 16.9, 3], [150, 16.8, 2], [208, 16.8, 2], [300, 16.8, 2], [16, 16.9, 2], [228, 16.8, 2], [84, 16.7, 2]]) { const p = pol(deg, r); kelp(p.x, 0, p.z, n, 1.1); }
      for (let k = 0; k < 18; k++) { const deg = k * 20 + 7, p = pol(deg, W0 + 1.6 + (k % 3) * 1.4); kelp(p.x, -0.05, p.z, 2 + (k % 2), 1.3); if (k % 3 === 0) coral(p.x + 0.8, -0.05, p.z, 1.2, ['pink', 'purple', 'orange'][k % 3], 3); }
      // the wrecks beyond the walls at the back: masts, yards, rigging and torn sails, dark in the haze
      SG.lod(0.6, () => { const mast = (deg, d, H, tilt, ry, sail) => { const p = pol(deg, d), parts = [], add = g => parts.push(g);
          add(SG.cyl(0.22, 0.5, H, 7, 0, H / 2, 0)); for (const [yy, L] of [[H * 0.5, H * 0.56], [H * 0.78, H * 0.38]]) { add(SG.box(L, 0.2, 0.2, 0, yy, 0)); for (const s of [-1, 1]) add(SG.tube(V(s * L / 2, yy, 0), V(s * L * 0.3, 0.6, 0.5), 0.028, 4)); if (sail) { const sh = new THREE.Shape(); sh.moveTo(-L / 2 + 0.3, yy - 0.1); sh.lineTo(L / 2 - 0.3, yy - 0.1); for (let q = 6; q >= 0; q--) sh.lineTo(-L / 2 + 0.3 + (L - 0.6) * q / 6, yy - 0.1 - L * (0.3 + 0.25 * Math.sin(q * 2.1 + yy)) * (q % 2 ? 0.75 : 1)); sh.closePath(); add(new THREE.ShapeGeometry(sh).translate(0, 0, 0.12)); } }
          add(SG.cyl(0.55, 0.45, 0.5, 8, 0, H * 0.66, 0)); add(SG.tube(V(0, H, 0), V(-H * 0.45, 0.4, 0.8), 0.028, 4));
          for (const g of parts) { g.rotateZ(tilt); g.rotateY(ry); g.translate(p.x, -0.3, p.z); } put(M.silh, mergeGeos(parts)); };
        mast(96, 22, 20, 0.16, 0.5, true); mast(118, 26, 24, -0.1, 1.2, true); mast(70, 24, 18, 0.26, 2.2, true); mast(46, 29, 22, -0.2, 0.3, true); mast(145, 26, 16, 0.3, 1.9, true); mast(20, 28, 15, 0.12, 2.8, false); mast(170, 31, 14, -0.25, 0.9, false); mast(84, 34, 26, 0.05, 1.6, true); mast(130, 38, 22, 0.2, 0.4, false);
        const hull = SG.box(18, 5.0, 3.6, 0, 0, 0); hull.rotateZ(0.26); hull.rotateY(2.3); hull.translate(Math.cos(100 * DEG) * 27, 4.0, Math.sin(100 * DEG) * 27); put(M.silh, hull);
        const hull2 = SG.box(14, 4.0, 3.2, 0, 0, 0); hull2.rotateZ(-0.2); hull2.rotateY(0.6); hull2.translate(Math.cos(55 * DEG) * 30, 2.8, Math.sin(55 * DEG) * 30); put(M.silh, hull2); });
      // the water above: a dome, deep blue-teal below and brighter toward the surface far up, a slow shimmer of light near the top
      { const sk = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 18), M.water); sk.renderOrder = -5; sk.frustumCulled = false; sk.layers.set(2); K.add(sk); }
      // bubbles rising all through the water, one draw
      { const N = HI ? 180 : 110, pos = new Float32Array(N * 3), B = []; for (let i = 0; i < N; i++) { const a = R() * 6.2832, d = R() * 22; B.push({ x: Math.cos(a) * d, z: Math.sin(a) * d, y: R() * 14, v: 0.5 + R() * 0.9, p: R() * 6.28, s: 0.6 + R() * 0.8 }); }
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); const m = new THREE.Points(g, M.bubble); m.frustumCulled = false; m.renderOrder = 9; m.layers.set(2); K.add(m);
        K.anim({ tick(dt, t) { for (let i = 0; i < N; i++) { const b = B[i]; b.y += b.v * dt; if (b.y > 14) b.y = 0.1; pos[i * 3] = b.x + Math.sin(t * 0.8 * b.s + b.p) * 0.3; pos[i * 3 + 1] = b.y; pos[i * 3 + 2] = b.z + Math.cos(t * 0.6 * b.s + b.p) * 0.3; } g.attributes.position.needsUpdate = true; } }); }
      // light shafts slanting down from the surface, all in one draw; caustic ripples over the floor and the wall
      { const pos = [], uvs = [], phs = [], idx = []; let o = 0;
        for (let k = 0; k < 10; k++) { const a = k / 10 * 6.2832 + 0.3, d = (k % 3) * 5 + 3, w = 4.5 + (k % 2) * 3.5, g = new THREE.PlaneGeometry(w, 40, 1, 1); g.translate(0, 20.3, 0); g.rotateZ(0.22); g.rotateY(a * 1.9); g.translate(Math.cos(a) * d, 0, Math.sin(a) * d + 4);
          const P = g.attributes.position, U = g.attributes.uv, I = g.index.array; for (let i = 0; i < P.count; i++) { pos.push(P.getX(i), P.getY(i), P.getZ(i)); uvs.push(U.getX(i), U.getY(i)); phs.push(k * 1.3); } for (let i = 0; i < I.length; i++) idx.push(I[i] + o); o += P.count; }
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2)); g.setAttribute('aPh', new THREE.Float32BufferAttribute(phs, 1)); g.setIndex(idx);
        const rm = new THREE.Mesh(g, M.ray); rm.renderOrder = 8; rm.frustumCulled = false; rm.layers.set(2); K.add(rm);
        const cg = mergeGeos([new THREE.RingGeometry(RG.rim, W0 + 0.2, 64, 1).rotateX(-Math.PI / 2).translate(0, 0.016, 0), new THREE.CylinderGeometry(W0 - 0.03, W0 - 0.03, WH, 48, 1, true).scale(-1, 1, 1).translate(0, WH / 2, 0)], true);
        const cm = new THREE.Mesh(cg, M.caustic); cm.renderOrder = 6; cm.layers.set(2); K.add(cm); }
      K.glow(0.5, 12, 15, 14, 0x8ED4FF); K.glow(3, 10, 13, 8, 0x7CC8FF);
      K.anim({ tick(dt, t) { SLIME_FALL_MAT.uniforms.uTime.value = t; SLIME_SPLASH_MAT.uniforms.uTime.value = t; M.ray.uniforms.uTime.value = t; M.caustic.uniforms.uTime.value = t; M.water.uniforms.uTime.value = t; if (M.kelpT) M.kelpT.value = t; } });
    },
    props() {},
  };
}
// the arena, laid out by hand: the pool (a hole) in the middle, the crates and barrels in the front corners, the basins, the slime
// pools that water paint down, the power spots, where you start. Then the usual samples, nav graph and meshes
function genConquest() {
  const T = THEME_BY.conquest, RG = T.ring, pol = (deg, r) => [Math.cos(deg * Math.PI / 180) * r, Math.sin(deg * Math.PI / 180) * r];
  const boxes = [];
  { const [x, z] = pol(295, 10.5); boxes.push([x - 0.98, x + 0.98, z - 0.57, z + 0.57, 0, 1.1, undefined, 'crateL']); }
  { const [x, z] = pol(245, 10.5); boxes.push([x - 0.98, x + 0.98, z - 0.57, z + 0.57, 0, 1.1, undefined, 'crateR']); }
  { const [x, z] = pol(236, 12.4); boxes.push([x - 0.44, x + 0.44, z - 0.44, z + 0.44, 0, 0.9, 'c', 'barrel', 0.6, 1]); }
  { const [x, z] = pol(304, 12.4); boxes.push([x - 0.44, x + 0.44, z - 0.44, z + 0.44, 0, 0.9, 'c', 'barrel', 2.1, 0]); }
  for (const b of boxes) for (let i = 0; i < 4; i++) b[i] = Math.round(b[i] * 100) / 100;
  const L = { sym: 'free', arch: 'ring', theme: 'conquest', boxes, ramps: [], holes: [[-RG.pool, RG.pool, -RG.pool, RG.pool, 0, 0, 'c']], clouds: [] };
  genOpt = { easy: false, avoid: null, themes: ['conquest'], flat: false };
  applyLayout(L); rebuildSamples(); buildNav();
  POTS.length = 0; RIVALS.length = 0; POWER_SPOTS.length = 0; COF_SPOTS.length = 0;
  for (const deg of [186, 354, 112, 68]) { const [x, z] = pol(deg, 15.0); POTS.push([x, 0, z]); }
  for (const [deg, r] of [[10, 15.6], [48, 15.9], [132, 15.7], [172, 15.9], [250, 6.3], [95, 7.0], [60, 6.5], [120, 6.3], [300, 8.4], [220, 8.8], [160, 10.4], [20, 10.6]]) { const [x, z] = pol(deg, r); RIVALS.push([x, 0, z]); }
  for (let k = 0; k < 8; k++) { const [x, z] = pol(k * 45 + 22, 11.0); POWER_SPOTS.push([x, 0, z, k < 2 ? 'roller' : undefined]); }
  for (let k = 0; k < 12; k++) { const [x, z] = pol(k * 30 + 15, 15.0); COF_SPOTS.push([x, 0, z, 1]); } for (let k = 0; k < 6; k++) { const [x, z] = pol(k * 60 + 40, 8.0); COF_SPOTS.push([x, 0, z, 0]); }
  Object.assign(START, { x: 0, z: -11, yaw: 0 }); Object.assign(CSTART, { x: 0, z: 11, yaw: Math.PI }); Object.assign(CSTART2, { x: -11, z: 0, yaw: Math.PI / 2 }); Object.assign(CSTART3, { x: 11, z: 0, yaw: -Math.PI / 2 });
  Object.assign(GEN, { seed: 307, sym: 'free', arch: 'ring', tries: 1, fallback: false, easy: false, avoid: null, themes: ['conquest'], flat: false, key: 'conquest', std: false });
  const t0 = performance.now(); rebuildStage(); GEN.ms = performance.now() - t0;
}
// ---- the stage preview: just you on the Sunken Keep, painting, no clock and no rival; Pause > Menu brings you back ----
let CQP = null; // (the preview under way: the mode to go back to)
function conqPreview() {
  if (state !== 'menu' || building || irisBusy) return;
  const prevMode = mode;
  if (menuPage === 'events') { menuPage = 'home'; menu.dataset.page = 'home'; evEl.hidden = true; $('mHome').hidden = false; } evFrom = false; document.body.classList.remove('evon');
  if (shopOpen) closeShop(true); if (lookOpen) closeLook();
  CQP = { prevMode }; mode = 'solo'; applyMode();
  AU.init(); AU.music('vs'); menu.classList.add('leaving'); setTimeout(() => menu.classList.remove('leaving'), 900);
  irisClose(() => {
    menu.hidden = true; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hideTally();
    building = true; genConquest(); mapUsed = true; clearTimeout(warmQ); warmRender(); building = false;
    beginMatch();
  }, null, 'Sunken Keep');
}
window.conqPreview = conqPreview;
"""

MOTES = r"""MOTE_LOOK.conquest = { cols: [0xD0F0FF, 0xFFFFFF, 0xA0E0FF], size: 0.22, rise: 0.9, blink: 0.3, sway: 0.5 }; // (v309: bubbles drifting up)
"""

def apply(s):
    # the round stage's queries: the floor ends at the ring's edge, the pool's curb is a ledge, the wall and the curb block you
    s = rep(s, "function floorAt(x, z) { if (Math.abs(x) > ARENA || Math.abs(z) > ARENA) return -Infinity;",
               "let CQ = null; // (v309) the Sunken Keep's round floor: its radius, the wall, the pool and its curb (null on the square stages)\n"
               "function floorAt(x, z) { if (CQ && x * x + z * z > CQ.R2) return -Infinity; if (Math.abs(x) > ARENA || Math.abs(z) > ARENA) return -Infinity;")
    s = rep(s, "  let best = -Infinity; const f = floorAt(x, z); if (f <= maxY) best = f;\n",
               "  let best = -Infinity; const f = floorAt(x, z); if (f <= maxY) best = f;\n  if (CQ && CQ.rimH <= maxY && CQ.rimH > best) { const r2 = x * x + z * z; if (r2 >= CQ.pool2 && r2 < CQ.rim2) best = CQ.rimH; } // (v309: the pool's curb)\n")
    s = rep(s, "  const m = PR * 0.9;\n  for (const b of qcell(qgB, x, z)) if (y < b[5] - STEP && y + 0.8 > b[4] && inR(x, z, b, m)) return true;",
               "  const m = PR * 0.9;\n  if (CQ) { const r = Math.hypot(x, z); if (r > CQ.block) return true; if (y < CQ.rimH - 0.02 && r >= CQ.pool && r < CQ.rim + m) return true; } // (v309: the keep's wall; the pool's curb holds you off unless you hop)\n  for (const b of qcell(qgB, x, z)) if (y < b[5] - STEP && y + 0.8 > b[4] && inR(x, z, b, m)) return true;")
    s = rep(s, "function applyThemeLook(T) {\n  TH = T;", "function applyThemeLook(T) {\n  TH = T; CQ = T.ring ? conqRing(T.ring) : null;")
    s = rep(s, "sea.visible = !!(T.sea || T.slime);", "sea.visible = !!(T.sea || T.slime) && !T.noSea;")
    s = rep(s, "['crypt', 'cathedral', 'manor', 'sewer'].includes(id) ? 'spooky'", "['crypt', 'cathedral', 'manor', 'sewer', 'conquest'].includes(id) ? 'spooky'")
    # the theme, its materials, scene and generator
    s = rep(s, "const THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));", THEME.strip('\n') + "\nconst THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));")
    s = rep(s, "function sewerMats(M, T) {", CORE.replace('__CONQ_TEX__', json.dumps(TEX)).strip('\n') + "\nfunction sewerMats(M, T) {")
    s = rep(s, "let moteLook = MOTE_LOOK.studio;", MOTES + "let moteLook = MOTE_LOOK.studio;")
    s = rep(s, "TP = genOpt.themes ? THEMES.filter(t => genOpt.themes.includes(t.id)) : THEMES,", "TP = genOpt.themes ? THEMES.filter(t => genOpt.themes.includes(t.id)) : THEMES.filter(t => !t.ring),")
    # the stage builder: a round floor the size of the ring, no square rim, no random markings, the plain pieces
    s = rep(s, "  shape.moveTo(-ARENA, -ARENA); shape.lineTo(ARENA, -ARENA); shape.lineTo(ARENA, ARENA); shape.lineTo(-ARENA, ARENA); shape.lineTo(-ARENA, -ARENA);\n",
               "  if (T.ring) shape.absarc(0, 0, T.ring.R + 0.5, 0, Math.PI * 2, false); /* (v309: round) */ else { shape.moveTo(-ARENA, -ARENA); shape.lineTo(ARENA, -ARENA); shape.lineTo(ARENA, ARENA); shape.lineTo(-ARENA, ARENA); shape.lineTo(-ARENA, -ARENA); }\n")
    s = rep(s, "const fg = new THREE.ExtrudeGeometry(shape, { depth: 0.7, bevelEnabled: false, curveSegments: 28 });", "const fg = new THREE.ExtrudeGeometry(shape, { depth: 0.7, bevelEnabled: false, curveSegments: T.ring ? 64 : 28 });")
    s = rep(s, "  rimEdge(); rect(-ARENA, ARENA, -ARENA, ARENA, -0.7, 0.09);\n  for (const [x, z] of [[-ARENA, -ARENA], [ARENA, -ARENA], [ARENA, ARENA], [-ARENA, ARENA]]) lines.push(beamGeo(V(x, -0.7, z), V(x, 0, z), 0.09));\n",
               "  if (!T.ring) { rimEdge(); rect(-ARENA, ARENA, -ARENA, ARENA, -0.7, 0.09);\n  for (const [x, z] of [[-ARENA, -ARENA], [ARENA, -ARENA], [ARENA, ARENA], [-ARENA, ARENA]]) lines.push(beamGeo(V(x, -0.7, z), V(x, 0, z), 0.09)); }\n")
    s = rep(s, "    const A = ARENA - EDGE_W, n = Math.round(2 * A / 1.3); for (let k = 0; k < n; k++) { const u = -A + (k + 0.5) / n * 2 * A; lt(u, -A); lt(u, A); lt(-A, u); lt(A, u); }\n",
               "    if (!T.ring) { const A = ARENA - EDGE_W, n = Math.round(2 * A / 1.3); for (let k = 0; k < n; k++) { const u = -A + (k + 0.5) / n * 2 * A; lt(u, -A); lt(u, A); lt(-A, u); lt(A, u); } }\n")
    s = rep(s, "  const dm = decalMat(T), ds = 5.5 + R() * 3, taken = [];\n  for (let t = 0; t < 40; t++) {", "  const dm = T.noMarks ? null : decalMat(T), ds = 5.5 + R() * 3, taken = [];\n  for (let t = 0; t < (T.noMarks ? 0 : 40); t++) {")
    s = rep(s, "const sgs = [], nS = 9 + (R() * 6 | 0), cells", "const sgs = [], nS = T.noMarks ? 0 : 9 + (R() * 6 | 0), cells")
    s = rep(s, "circ = b[6] === 'c', grave = b[6] === 'g', rad = w / 2, kind = b[7] || '';\n",
               "circ = b[6] === 'c', grave = b[6] === 'g', rad = w / 2, kind = b[7] || '', plain = !!(DX && DX.plain && DX.plain(b, kind)); // (v309: plain: the theme draws the whole piece itself)\n")
    s = rep(s, "if (HI && T.trim && !grave && !planter) {", "if (HI && T.trim && !grave && !planter && !plain) {")
    s = rep(s, "if (HI && !grave && !circ && (T.foot || T.strips)) {", "if (HI && !grave && !circ && !plain && (T.foot || T.strips)) {")
    s = rep(s, "if (T.candles && !grave && !circ && h > 0.6 && w > 1.1 && d > 1.1 && R() < T.candles) {", "if (T.candles && !grave && !circ && !plain && h > 0.6 && w > 1.1 && d > 1.1 && R() < T.candles) {")
    s = rep(s, "if (IV && !grave && !circ && h > 0.25) {", "if (IV && !grave && !circ && !plain && h > 0.25) {")
    s = rep(s, "if (IV && circ && kind !== 'column' && h > 0.45 && IV.drum && R() < IV.drum) {", "if (IV && circ && !plain && kind !== 'column' && h > 0.45 && IV.drum && R() < IV.drum) {")
    s = rep(s, "if (LMP && !circ && !grave && h > 0.7) {", "if (LMP && !circ && !grave && !plain && h > 0.7) {")
    # the reveal sweep keeps to the small ring
    s = rep(s, "const u = clamp(revealT / REVEAL_T, 0, 1), e = u * u * (3 - 2 * u), R = ARENA * 1.5 - ARENA * 0.3 * e, a = revealA0 - 0.75 * e, Hh = ARENA * 1.0 - ARENA * 0.35 * e;",
               "const u = clamp(revealT / REVEAL_T, 0, 1), e = u * u * (3 - 2 * u), AR = CQ ? CQ.R * 1.55 : ARENA, R = AR * 1.5 - AR * 0.3 * e, a = revealA0 - 0.75 * e, Hh = AR * 1.0 - AR * 0.35 * e; // (v309: the keep's sweep keeps to its ring)")
    # the preview: no clock (it says Preview), no weather, the mode back when you leave, the reveal's line, the pause's line
    s = rep(s, "else if (!(sdEndT > 0)) matchLeft -= dt;", "else if (!(sdEndT > 0) && !CQP) matchLeft -= dt;")
    s = rep(s, "if (ct !== lastClock) { lastClock = ct; const ce = $('clock'); ce.textContent = ct;", "if (ct !== lastClock) { lastClock = ct; const ce = $('clock'); ce.textContent = CQP ? 'Preview' : ct;")
    s = rep(s, "mapUsed = true; resetRun(); gyCam = 0; state = 'intro';", "mapUsed = true; resetRun(); if (CQP) wxLeft = 1e9; gyCam = 0; state = 'intro';")
    s = rep(s, "function showMenu() {\n  if (NM) netLeave();", "function showMenu() {\n  if (CQP) { mode = CQP.prevMode; CQP = null; } // (v309: back from the stage preview)\n  if (NM) netLeave();")
    s = rep(s, "$('rvSub').textContent = tutMatchDue() ?", "$('rvSub').textContent = CQP ? 'Season Conquest \\u00b7 stage preview' : tutMatchDue() ?")
    s = rep(s, "$('pauseClock').textContent = fmtClock(matchLeft) + ' left'; $('quitBtn').textContent = tut ?", "$('pauseClock').textContent = CQP ? 'Stage preview' : fmtClock(matchLeft) + ' left'; $('quitBtn').textContent = tut ?")
    # the Season Conquest card: a stage preview now
    s = rep(s, '<div class="evcard soon" data-ev="conquest" style="--ec:#F2C14E"><button class="evmain" id="evConq" type="button" aria-disabled="true"><span class="evbar"><i>Coming soon</i></span>',
               '<div class="evcard" data-ev="conquest" style="--ec:#F2C14E"><button class="evmain" id="evConq" type="button"><span class="evbar"><i>Stage preview</i></span>')
    s = rep(s, '<b>Season Conquest</b><small>Claim the season’s canvases</small>', '<b>Season Conquest</b><small>Sunken Keep, stage only</small>')
    s = rep(s, '<img id="evConqArt" alt=""></span></button><i class="evsoon">Coming soon</i></div>', '<img id="evConqArt" alt=""></span></button><i class="evsoon">Stage preview</i></div>')
    s = rep(s, "$('evConq').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evConq').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Season Conquest is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); }); // (v300)",
               "$('evConq').addEventListener('click', uiClick(conqPreview)); // (v309: the stage preview)")
    s = rep(s, "set('evConqArt', 'island');", "{ const im = $('evConqArt'), src = CONQ_TEX.card; if (im.getAttribute('src') !== src) im.src = src; } setTimeout(conqWarm, 700); /* (v309: the keep's own picture) */")
    return s
