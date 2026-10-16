"""v309 (Season Conquest stage, reworked in the v311 round): the Sunken Keep, a small round boss arena at the bottom of the sea, built by
hand to the concept picture, and a stage preview to walk it from Choose Event. Kept out of the release list until the owner is happy.

- One fixed scene, nothing random in where things stand. A round floor of wet cobbles laid in rough rows; a parapet of chunky stone all
  round with a capped post every 15 degrees; the pool of slime in the middle, sunk inside a curb of bevelled dark stones, its spout
  rising from the centre; behind the parapet the ruins crowd up in layers into the haze: three great arches, broken half arches, tall
  crumbling pillars, wall sections with arched windows, rubble, chains hanging from the arches. Three round iron cages swing on their
  chains: the pirate skeleton (left), the little blue ghost (right of centre), the gold and the crown (far right). Iron lanterns hang on a
  chain and on wooden brackets from the pillars; clusters of candles stand on the wall top, its posts, the crates and the floor; crates
  with rope and iron corners and barrels stand in the front corners, the purple skull flag over the right-hand stack; the ship's wheel
  on the far wall; coral and swaying kelp at the walls' feet; wreck masts and rigging as silhouettes in the haze.
- The models (the ruins, the cages, the skeleton, the props) were made from pictures by an image-to-3D generator, decimated to a
  budget and packed small by tools/glb2pack.py --v2 into tools/v309_conquest_models.json, which goes in the page as a JSON block
  (keepPack). Nothing reads it at boot: Choose Event's warm-up or the stage's build decodes it. Each kind of model is one draw (the
  parapet four, a quarter of the ring each); copies out of view aren't drawn; the far ruins are simpler copies of the near ones.
- The skeleton is rigged (the 22-joint humanoid template, with a jaw added under the head) and plays clips (an idle sway, looking
  round, calling out, a laugh) in a mixer, with its hands on the bars; on top of that it turns its head to follow you, rattles the bars
  (its cage swinging harder) when you come close, and laughs, its jaw flapping, when you fall in the slime.
- The ooze is one look with a light of its own: a deep green body, bright highlights, a soft glow from inside. The pool's surface is
  lumpy and slow with bubbles that swell and pop; in four places the goo has slumped across the wall top in heavy blobs and hangs down
  the face in a thick, lumpy sheet with tongues of different lengths; drips stretch from the longest tongues for seconds, let go, fall
  slowly and splat into the puddle below, which ripples; thick puddles lie on the floor.
- Underwater: a blue-teal haze deepening with distance, light shafts from the surface, faint caustics, bubbles, drifting motes.
- Size and rules: the wall at r = 17.5, the pool r = 4 with its curb to 4.7, so the walkable ring is about 12.8 wide. floorAt,
  surfaceUnder and blockedAt know the circle, the pool (a hole: fall in and you're out for a moment) and its curb (a low ledge you can
  hop onto but not roll over) through CQ. The space above the pool is left empty for the boss.
- Memory: as every canvas since v309, the keep lets go of its models' meshes, maps and looks when its canvas is let go (or when Choose
  Event warmed them and another canvas came instead); the stage's clean-up also disposes instanced copies, a group's pieces and the
  skeleton's bones.
- Choose Event: the Season Conquest card opens the stage preview (just you on the stage, painting, no clock, no rival; Pause > Menu
  comes back)."""

import json, os
from v309_conquest_tex import TEX
# the models (tools/glb2pack.py --v2 entries, by name), a JSON block in the page
MODELS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v309_conquest_models.json')).read()

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

THEME = r"""
// (v309) the Sunken Keep: the Season Conquest boss arena (one fixed scene, conqDress; the theme carries its light, haze and materials)
THEMES.push(
  { id: 'conquest', label: 'Sunken Keep', sf: ['keepFloor', 'keepWall'], uv: 0.075, ft: 0xC2BED6, st: 0xE8ECEE, dt: 0x8C9AA4, hor: 0x11506C, fog: [7, 54], sky: [0x2A72B0, 0x1F6E98, 0x11506C], low: 0x0A2E44, hemi: [0x9CB0D8, 0x141E36], sunPos: [3, 30, 7],
    kit: {}, fill: 'drum', pot: 'barrel', enclosed: true, slime: true, noSea: true, mirror: true, noClouds: true, noMarks: true, ring: { R: 17.6, wall: 17.5, pool: 4.0, rim: 4.7, rimH: 0.22 },
    nrm: [1, 1], rough: [0.3, 0.9], base: { hemiI: 0.62, key: 0xC8DCF4, keyI: 0.46 }, env: { top: 0x1A5A88, hor: 0x135268, gnd: 0x061C28, sun: 0xA8DCF0, sunK: 0.4 }, lk: { hemi: 0.34, key: 1.22 }, grade: { sat: 1.24, con: 1.1, vig: 0.36, bloom: 1.1, expo: 1.1, tint: [1.03, 0.99, 1.0] }, jglow: 0.7,
    edge: 0x14261A, edgeK: 1.0, mkMats: conqMats, dress: conqDress }
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
SURF_PAINT.keepFloor = () => imgSurf(CONQ_TEX.floor, 1024, 3.6, 0.14, 0.75, 1.6); // (wet: the slabs glossy, the grooves dull)
SURF_PAINT.keepWall = () => imgSurf(CONQ_TEX.wall, 512, 2.6, 0.55, 0.95);
SURF_PAINT.keepWood = () => imgSurf(CONQ_TEX.wood, 512, 1.6, 0.6, 0.9);
SURF_PAINT.keepBed = () => imgSurf(CONQ_TEX.seabed, 512, 2.0, 0.7, 1.0);
// (made while Choose Event is open, behind it, so a launch doesn't pay for a stage the player may never open, and the preview doesn't wait)
function conqWarm() { if (conqWarm.done || menuPage !== 'events') return; conqWarm.done = 1; for (const k of ['keepFloor', 'keepWall', 'keepWood', 'keepBed']) surf(k); conqModelsWarm(); }
// the pirate flag: a skull and crossbones on purple, with a worn edge
const CONQ_FLAG = makeTex(256, (g, S) => {
  g.fillStyle = '#5A2282'; g.fillRect(0, 0, S, S); const R = rng(307); for (let k = 0; k < 60; k++) { g.fillStyle = 'rgba(30,8,50,' + (0.08 + R() * 0.14) + ')'; g.fillRect(R() * S, R() * S, 6 + R() * 40, 3 + R() * 10); }
  const c = S / 2; g.fillStyle = '#F2EBD8'; g.beginPath(); g.ellipse(c, c - 22, 46, 42, 0, 0, 6.2832); g.fill(); g.fillRect(c - 26, c + 8, 52, 24);
  g.fillStyle = '#5A2282'; for (const dx of [-17, 17]) { g.beginPath(); g.ellipse(c + dx, c - 26, 13, 15, 0, 0, 6.2832); g.fill(); } g.beginPath(); g.moveTo(c, c - 6); g.lineTo(c - 7, c + 8); g.lineTo(c + 7, c + 8); g.closePath(); g.fill();
  for (let k = -2; k <= 2; k++) g.fillRect(c + k * 10 - 2, c + 14, 4, 18);
  g.strokeStyle = '#F2EBD8'; g.lineWidth = 14; g.lineCap = 'round'; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(c - 78 * s, c + 36); g.lineTo(c + 78 * s, c + 92); g.stroke(); }
  g.fillStyle = '#F2EBD8'; for (const [x, y] of [[c - 78, c + 36], [c + 78, c + 36], [c - 78, c + 92], [c + 78, c + 92]]) for (const dy of [-8, 8]) { g.beginPath(); g.arc(x + (x < c ? -4 : 4), y + dy, 9, 0, 6.2832); g.fill(); }
});
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
  M.void = new THREE.MeshBasicMaterial({ color: 0x03100A }); M.silh = new THREE.MeshBasicMaterial({ color: 0x072238, fog: true });
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
function conqDress(K) {
  const { T, M, R, put } = K, us = K.us * 2.8, vc = K.vc, V = SG.V, C = hexC, RG = T.ring, W0 = RG.wall, WT = 0.7, WH = 2.3, DEG = Math.PI / 180; // (the stones smaller than the floor's slabs)
  const ST = C(0x5A6E78), STD = C(0x2A343A), IR = C(0x1C2028), IRL = C(0x3A4048), WD = C(0x6A4A2E), WDD = C(0x3E2A18), WL = C(0x9A7046), ROPE = C(0xC8A070), CRM = C(0xF2ECD8), BONE = C(0xEDE6D4), RD = C(0xD42A2E), GLD = C(0xF2C230);
  const glowC = (c, k) => C(c).multiplyScalar(HI ? k || 2.2 : 1.2);
  const pol = (deg, r, y) => V(Math.cos(deg * DEG) * r, y || 0, Math.sin(deg * DEG) * r);
  // a box stood at polar (deg, r), turned to face the middle (w across, d in and out), in the wall's stone or a vertex colour
  const sbox = (w, h, d, deg, r, y, col) => { const g = SG.box(w, h, d, 0, 0, 0); g.rotateY(-deg * DEG - Math.PI / 2); g.translate(Math.cos(deg * DEG) * r, y, Math.sin(deg * DEG) * r); if (col) vc(M.vc, g, col); else put(M.side, worldUV(g, us)); return g; };
  const chain = (a, b, t) => { const d = V(b.x - a.x, b.y - a.y, b.z - a.z), L = d.length(), n = Math.max(2, Math.round(L / (t || 0.13))); d.normalize(); for (let i = 0; i < n; i++) { const p = V(a.x + d.x * L * (i + 0.5) / n, a.y + d.y * L * (i + 0.5) / n, a.z + d.z * L * (i + 0.5) / n), g = new THREE.BoxGeometry(i % 2 ? 0.024 : 0.075, 0.15, i % 2 ? 0.075 : 0.024); alignZ(g.rotateX(Math.PI / 2), d, p); vc(M.vcMetal, g, IRL); } };
  const candle = (x, y, z, hh, cr) => { vc(M.vc, SG.cyl(cr, cr * 1.06, hh, 8, x, y + hh / 2, z), CRM); for (let k = 0; k < 3; k++) { const a = k * 2.1 + x * 7; vc(M.vc, SG.ball(cr * 0.3, x + Math.cos(a) * cr * 0.95, y + hh - cr * (0.2 + k * 0.3), z + Math.sin(a) * cr * 0.95, 1, 1.6, 1), CRM); } vc(M.vc, SG.cyl(cr * 0.2, cr * 0.2, 0.03, 5, x, y + hh + 0.015, z), IR); K.glow(x, y + hh + 0.1, z, 0.6, 0xFFC27A); if (HI && M.flameCore) put(M.flameCore, flameCoreG(0.5).translate(x, y + hh + 0.05, z)); };
  const candles0 = (x, y, z, n, big) => { for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + R(), rr = n > 1 ? 0.11 + R() * 0.06 : 0; candle(x + Math.cos(a) * rr, y, z + Math.sin(a) * rr, (big ? 0.2 : 0.12) + R() * 0.24, 0.04 + R() * 0.02); } K.light(x, y + 0.45, z, 3.2, 0xFFB45A, 1.5); };
  // an iron lantern: a cage of a frame round a candle's glass, a ring on top for its chain
  const lantern0 = (x, y, z, s) => { s = s || 1; vc(M.vcMetal, SG.box(0.3 * s, 0.05 * s, 0.3 * s, x, y + 0.22 * s, z), IR); vc(M.vcMetal, SG.box(0.26 * s, 0.05 * s, 0.26 * s, x, y - 0.2 * s, z), IR); vc(M.vcMetal, SG.cone(0.19 * s, 0.12 * s, x, y + 0.3 * s, z, 6), IR); vc(M.vcMetal, SG.torus(0.05 * s, 0.012 * s, x, y + 0.4 * s, z, 0, 0, 10), IR);
    for (let a = 0.785; a < 6.28; a += 1.5708) vc(M.vcMetal, SG.box(0.024 * s, 0.4 * s, 0.024 * s, x + Math.cos(a) * 0.12 * s, y, z + Math.sin(a) * 0.12 * s), IR);
    vc(M.glowVC, SG.box(0.17 * s, 0.32 * s, 0.17 * s, x, y, z), glowC(0xFFC06A, 2.4)); vc(M.vc, SG.cyl(0.035 * s, 0.035 * s, 0.14 * s, 6, x, y - 0.1 * s, z), CRM); K.glow(x, y, z, 0.9 * s, 0xFFC070); K.light(x, y, z, 4.5 * s, 0xFFB45A, 1.2); };
  // a wooden barrel (upright or lying), stave shading, two iron hoops, a rope round it
  const barrel0 = (x, y, z, r, h, lay, ry, rope) => { const col = WD, lid = SG.shade(col, 0.72), parts = [SG.paint(SG.cyl(r, r, h, 20, 0, 0, 0), (px, py, pz, o, nx, ny) => { if (Math.abs(ny) > 0.5) return lid; const a = Math.atan2(pz, px), f = ((a / 6.2832 * 14) % 1 + 1) % 1; return SG.shade(col, f < 0.07 ? 0.7 : 0.88 + 0.14 * Math.sin(a * 7)); })];
    for (const yy of [h * 0.3, -h * 0.3]) parts.push(SG.paint(SG.band(r + 0.012, 0.05, 20).translate(0, yy, 0), IRL));
    if (rope) for (const yy of [0.04, -0.06]) parts.push(SG.paint(SG.torus(r + 0.02, 0.025, 0, yy, 0, Math.PI / 2, 0, 20), ROPE));
    for (const g of parts) { if (lay) g.rotateZ(Math.PI / 2); if (ry) g.rotateY(ry); g.translate(x, y + (lay ? r : h / 2), z); vc(M.vcWood, g, null); } };
  // a wooden crate: planks, corner battens, nail heads
  const crate0 = (x, y, z, s, ry) => { const hs = s / 2, parts = [[SG.box(s, s, s, 0, hs, 0), SG.shade(WL, 0.9 + 0.12 * R())]];
    for (const [ex, ez] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(0.07, s, 0.07, ex * (hs - 0.02), hs, ez * (hs - 0.02)), WDD]);
    for (const yy of [0.04, s - 0.04]) parts.push([SG.box(s + 0.02, 0.07, 0.07, 0, yy, hs - 0.02), WDD], [SG.box(s + 0.02, 0.07, 0.07, 0, yy, -hs + 0.02), WDD], [SG.box(0.07, 0.07, s + 0.02, hs - 0.02, yy, 0), WDD], [SG.box(0.07, 0.07, s + 0.02, -hs + 0.02, yy, 0), WDD]);
    for (const [ex, ez] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(0.1, 0.1, 0.1, ex * (hs - 0.01), s - 0.05, ez * (hs - 0.01)), C(0x3A3530)]);
    for (const [g, c] of parts) { g.rotateY(ry || 0); g.translate(x, y, z); vc(M.vcWood, uvXY(g, (px, py, pz) => [px * 1.3 + pz * 0.7, py * 1.3 + pz * 0.3]), c); } };
  // the props as models when the pack has them (crates with rope and iron corners, barrels, iron lanterns whose panes glow, clusters of
  // candles with a flame on every wick): one draw for each kind, the copies out of view not drawn
  const PM = cqGeo('crate') && cqGeo('candles') ? { crate: [], barrel: [], lantern: [], candles: [], candlesF: [] } : null, flames = [];
  const crate = (x, y, z, s, ry) => PM ? PM.crate.push([x, y, z, (ry || 0) + (R() - 0.5) * 0.12, s / 0.966]) : crate0(x, y, z, s, ry);
  const barrel = (x, y, z, r, h, lay, ry, rope) => { if (!PM) return barrel0(x, y, z, r, h, lay, ry, rope); ry = ry || 0; const k = r / 0.459;
    PM.barrel.push(lay ? [x + h / 2 * Math.cos(ry), y + r, z - h / 2 * Math.sin(ry), ry, k, h, k, 0, Math.PI / 2] : [x, y, z, ry, k, h, k]); };
  const lantern = (x, y, z, s, ry) => { if (!PM) return lantern0(x, y, z, s); s = s || 1; PM.lantern.push([x, y - 0.26 * s, z, ry || 0, 0.66 * s]); K.glow(x, y + 0.02 * s, z, 0.8 * s, 0xFFB868); K.light(x, y, z, Math.min(6.5, 4.5 * s), 0xFFB45A, 1.25); };
  const candles = (x, y, z, n, big, far) => { if (!PM) return candles0(x, y, z, n, big); const sc = (big ? 0.3 : 0.26) + 0.05 * n + R() * 0.04, ry = R() * 6.2832, c = Math.cos(ry), sn = Math.sin(ry);
    (far ? PM.candlesF : PM.candles).push([x, y, z, ry, sc]); CQ_WICKS.forEach(([wx, wy, wz], i) => flames.push([x + (wx * c + wz * sn) * sc, y + wy * sc, z + (-wx * sn + wz * c) * sc, sc, i < 4]));
    K.light(x, y + 0.45, z, 2.8, 0xFFB45A, far ? 1.0 : 0.65); };
  // coral: clumps of curving stems, each forking once into knobbed tips; pink, purple or orange, a little lighter toward the tips
  const CORAL = { pink: C(0xFF5FA0), purple: C(0xA860FF), orange: C(0xFF8A3C) };
  const coral = (x, y, z, s, kind, n) => SG.lod(0.55, () => coral0(x, y, z, s, kind, n));
  const coral0 = (x, y, z, s, kind, n) => { const col = CORAL[kind]; s *= 1.35; for (let k = 0; k < n; k++) { const a = R() * 6.2832, d = R() * 0.45 * s, px = x + Math.cos(a) * d, pz = z + Math.sin(a) * d, w = R();
      for (let b = 0, nb = 2 + (w < 0.3 ? 1 : 0); b < nb; b++) { const t = R() * 6.2832, L = (0.32 + R() * 0.4) * s, r = 0.035 * s + R() * 0.015, pts = [V(px, y, pz), V(px + Math.cos(t) * L * 0.3, y + L * 0.55, pz + Math.sin(t) * L * 0.3), V(px + Math.cos(t) * L * 0.45 + (R() - 0.5) * 0.15, y + L, pz + Math.sin(t) * L * 0.45 + (R() - 0.5) * 0.15)];
        vc(M.vc, SG.curve(pts, r, 6, 5), (qx, qy) => SG.shade(col, 0.7 + 0.5 * (qy - y) / L)); const e = pts[2];
        for (let f = 0; f < 2; f++) { const tf = t + (f ? 0.9 : -0.9) + (R() - 0.5) * 0.5, Lf = L * (0.35 + R() * 0.2), q = V(e.x + Math.cos(tf) * Lf * 0.55, e.y + Lf, e.z + Math.sin(tf) * Lf * 0.55);
          vc(M.vc, SG.curve([e, V((e.x + q.x) / 2, (e.y + q.y) / 2 + Lf * 0.08, (e.z + q.z) / 2), q], r * 0.75, 4, 5), SG.shade(col, 1.15)); vc(M.vc, SG.ball(r * 0.95, q.x, q.y, q.z), SG.shade(col, 1.3)); } } } };
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
  // the ghost and the gold as meshes of their own, in their cage's frame (its floor plate at y 0.23, facing +z), to ride its swing
  const tenantMesh = kind => {
    if (kind === 'ghost') { const gc = glowC(0x7FD8FF, 1.8), parts = [[SG.ball(0.26, 0, 0.42, 0, 1, 1.25, 1), gc], [SG.ball(0.1, 0.13, 0.12, 0.08), gc], [SG.ball(0.1, -0.13, 0.12, 0.05), gc], [SG.ball(0.1, 0, 0.1, -0.1), gc], [SG.ball(0.045, 0.09, 0.5, 0.22, 1, 1.4, 0.6), C(0x08203A)], [SG.ball(0.045, -0.09, 0.5, 0.22, 1, 1.4, 0.6), C(0x08203A)]];
      const m = new THREE.Mesh(vcGeoIdx(parts), M.glowVC); m.position.y = 0.3; m.layers.enable(3); K.anim({ tick(dt, t) { m.position.y = 0.3 + 0.1 * Math.sin(t * 1.3); m.rotation.y = 0.25 * Math.sin(t * 0.7); } }); return m; }
    if (kind === 'gold') { const parts = [[SG.ball(0.42, 0, 0.25, 0, 1, 0.5, 1), (px, py) => SG.shade(GLD, 0.8 + 0.35 * (py - 0.25) / 0.2)]];
      for (let k = 0; k < 9; k++) { const t = R() * 6.28, d = R() * 0.3; parts.push([SG.cyl(0.065, 0.065, 0.02, 8, Math.cos(t) * d, 0.43 - d * 0.35 + 0.01, Math.sin(t) * d), SG.shade(GLD, 1.1)]); }
      parts.push([SG.torus(0.16, 0.045, 0, 0.5, 0, Math.PI / 2, 0, 14), GLD]); for (let k = 0; k < 5; k++) { const t = k / 5 * 6.2832; parts.push([SG.cone(0.04, 0.12, Math.cos(t) * 0.16, 0.57, Math.sin(t) * 0.16, 5), GLD]); }
      parts.push([SG.ball(0.05, 0.16, 0.53, 0), C(0xE0304A)]); return new THREE.Mesh(vcGeoIdx(parts), M.vcMetal); }
    return null; };
  // a chain from high above (the ceiling of the world) down to y, then a cage with its tenant
  const hangCage = (kind, deg, r, y) => { const p = pol(deg, r), top = cage(p.x, y, p.z, 0.8, 1.5); chain(V(p.x, 15, p.z), V(p.x, top, p.z)); tenant(kind, p.x, y + 0.06, p.z, deg * DEG); };
  const falls = [];
  return {
    plain() { return true; }, skipBody() { return true; }, roundMats() { return null; }, noPlinth: true, spot() {}, noScatter() { return true; },
    // the pieces you can bump into: the crates and barrels in the front corners (their boxes are in the layout; this is how they look)
    box(b, I) { const { cx, cz } = I, kind = b[7] || '';
      if (kind === 'crateL') { crate(cx - 0.47, 0, cz - 0.1, 0.94, -0.06); crate(cx + 0.47, 0, cz + 0.08, 0.9, 0.08); crate(cx - 0.3, 0.94, cz + 0.05, 0.68, 0.3); candles(cx + 0.45, 0.86, cz, 2, true); candles(cx - 0.3, 1.5, cz + 0.05, 1, true); if (!PM) K.hull(SG.box(1.96, 1.1, 1.14, cx, 0.55, cz)); }
      else if (kind === 'crateR') { crate(cx + 0.47, 0, cz - 0.1, 0.94, 0.05); crate(cx - 0.47, 0, cz + 0.08, 0.9, -0.08); crate(cx + 0.3, 0.94, cz + 0.05, 0.68, -0.25); candles(cx - 0.45, 0.86, cz, 2, true); candles(cx + 0.3, 1.5, cz + 0.05, 1, true); if (!PM) K.hull(SG.box(1.96, 1.1, 1.14, cx, 0.55, cz));
        // the purple skull flag draped over its side (hung over the crate's edge, toward the middle of the arena)
        const top = PM ? 0.86 : 0.96, fz = cz - 0.1 - (PM ? 0.5 : 0.48);
        const g = gridGeo(10, 8, (u, v, o) => { const over = v < 0.22, x = cx + 0.47 + (0.5 - u) * 0.84; if (over) o.set(x, top + 0.012 + 0.01 * Math.sin(u * 9), fz + 0.3 - v / 0.22 * 0.3); else o.set(x, top - (v - 0.22) / 0.78 * (top - 0.1), fz - 0.025 - 0.035 * Math.sin(u * 7 + v * 5) * (v - 0.22)); });
        uvXY(g, (px, py, pz) => [(cx + 0.89 - px) / 0.84, Math.min(1, (py - 0.1) / (top - 0.1) * 0.92 + (pz > fz + 0.02 ? 0.08 : 0))]); const fm = new THREE.Mesh(g, M.flag); fm.layers.enable(3); K.add(fm); }
      else if (kind === 'barrel') { barrel(cx, 0, cz, 0.44, 0.9, false, b[8] || 0, true); if (!PM) K.hull(SG.cyl(0.5, 0.5, 1.0, 18, cx, 0.5, cz)); if (b[9]) candles(cx, 0.9, cz, 2, true); }
    },
    // the pool in the middle: a pit of glowing slime a little below the floor, bubbling, the spout rising from its heart, a curb of
    // curved dark stones round it
    hole() {
      const pr = RG.pool, rr = RG.rim, rh = RG.rimH;
      put(M.void, new THREE.CircleGeometry(pr + 0.3, SEG(44)).rotateX(-Math.PI / 2).translate(0, -0.72, 0));
      { GOO_U.uK.value = HI ? 1.0 : 0.9; const pm = new THREE.Mesh(gooPool(pr + 0.02), gooMat(GOO_POOL_VS, { uBub: { value: GOO_BUB } })); pm.position.y = -0.16; pm.renderOrder = 2; pm.userData.own = true; K.add(pm);
        const sm = new THREE.Mesh(gooSpout(), gooMat(GOO_SPOUT_VS)); sm.position.y = -0.1; sm.layers.enable(3); sm.userData.own = true; K.add(sm); K.anim({ tick: gooTick }); gooTick(0, 0); }
      K.glow(0, 0.35, 0, 2.2, 0x3C9A20); K.glow(0, 1.3, 0, 1.0, 0x4CB028);
      K.light(0, 0.3, 0, 7.5, 0x7CE83A, 1.5); K.steam(0, -0.05, 0, 1.0, 1.2, HI ? 0.7 : 0.4, 0.8); for (let k = 0; k < 3; k++) { const a = k * 2.0944 + 0.5; K.steam(Math.cos(a) * 2.2, -0.08, Math.sin(a) * 2.2, 1.0, 1.0, HI ? 0.4 : 0.25, 0.5); }
      // the curb: 20 curved stones, each a little different, dark, over the pit's lip; the pit's inner wall
      put(M.dark, cylUV(new THREE.CylinderGeometry(pr - 0.015, pr - 0.015, rh + 0.72, SEG(44), 1, true).scale(-1, 1, 1).translate(0, (rh - 0.72) / 2, 0), pr, rh + 0.7, us));
      // the curb: 24 dark stones round the pool, each a curved block with bevelled edges and a joint between it and the next, a little uneven
      for (let k = 0; k < 24; k++) { const a0 = k / 24 * 6.2832 + 0.013, a1 = (k + 1) / 24 * 6.2832 - 0.013, bv = 0.035, hh = rh + (R() - 0.5) * 0.05, ri = pr + 0.03, ro = rr - 0.03, pts = [];
        for (let q = 0; q <= 5; q++) { const a = a0 + (a1 - a0) * q / 5; pts.push(new THREE.Vector2(Math.cos(a) * ro, -Math.sin(a) * ro)); }
        for (let q = 5; q >= 0; q--) { const a = a0 + (a1 - a0) * q / 5; pts.push(new THREE.Vector2(Math.cos(a) * ri, -Math.sin(a) * ri)); }
        const g = new THREE.ExtrudeGeometry(new THREE.Shape(pts), { depth: Math.max(0.02, hh - 2 * bv), bevelEnabled: true, bevelThickness: bv, bevelSize: bv * 0.8, bevelSegments: 2, curveSegments: 4 });
        g.rotateX(-Math.PI / 2); g.translate(0, bv, 0); put(M.dark, worldUV(g, us)); }
      K.hull(new THREE.CylinderGeometry(rr + 0.06, rr + 0.06, rh + 0.1, 40, 1, true).translate(0, rh / 2, 0));
    },
    // the whole scene round the floor
    outer() {
      // the sea floor beyond the walls, dark, fading into the haze; rubble on it
      put(M.ground, worldUV(new THREE.RingGeometry(W0 - 0.2, 80, SEG(64), 1).rotateX(-Math.PI / 2).translate(0, -0.06, 0), K.us));
      for (let k = 0; k < 40; k++) { const a = R() * 6.2832, d = W0 + 1.5 + R() * 14, s = 0.25 + R() * 0.6; vc(M.vc, SG.ball(s, Math.cos(a) * d, -0.06 + s * 0.35, Math.sin(a) * d, 1, 0.6, 1), SG.shade(STD, 0.6 + R() * 0.5)); }
      // the parapet and the ruins (the models); without them, the old blocks: a low wall all round with square posts, pillars and two arches
      if (!conqRuins(K)) {
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
      }
      for (const [deg, r, y0, y1] of [[24, 21.2, 11.2, 6.4], [29, 21.2, 11.0, 7.6], [156, 21.2, 11.6, 6.8], [151, 21.2, 11.4, 8.2], [272, 21.4, 10.4, 6.6], [96, 22.5, 15, 8.5]]) { const p = pol(deg, r); chain(V(p.x, y0, p.z), V(p.x, y1, p.z), 0.14); }
      // the cages: the pirate skeleton at the left, the little ghost at the right of centre, the gold and the crown at the far right
      { const spots = [['skeleton', 292, 9.0, 2.7], ['ghost', 124, 11.5, 6.0], ['gold', 234, 9.0, 3.1]];
        if (conqCages(K, spots, tenantMesh)) { const p = pol(124, 11.5); K.glow(p.x, 6.0 + 0.75, p.z, 1.6, 0x6AC8FF); K.light(p.x, 6.0 + 0.6, p.z, 5, 0x6AC8FF, 0.8); const q = pol(234, 9.0); K.glow(q.x, 3.1 + 0.6, q.z, 1.0, 0xFFD070); }
        else { hangCage('skeleton', 292, 9.0, 3.4); hangCage('ghost', 124, 11.5, 6.8); hangCage('gold', 234, 9.0, 3.6); } }
      // lanterns: a big one on a chain at the left, two on brackets on the wall posts
      if (PM) { const p = pol(318, 9.6); chain(V(p.x, 15, p.z), V(p.x, 5.8, p.z)); lantern(p.x, 5.0, p.z, 2.2, 0.4);
        for (const [deg, s, y] of [[50, 2.3, 4.9], [130, 2.3, 4.7], [214, 1.9, 4.6], [326, 1.9, 4.7]]) { const r0 = 18.1, r1 = 16.6, q = pol(deg, r1 + 0.08), top = y + 0.4 * s, by = top + 0.42; // (the lantern's ring at top, the beam above it)
          { const bm = SG.box(0.22, 0.22, r0 - r1 + 0.25, 0, 0, 0), c = pol(deg, (r0 + r1) / 2, by); bm.rotateY(-deg * DEG - Math.PI / 2); bm.translate(c.x, c.y, c.z); vc(M.vcWood, bm, WDD); } vc(M.vcWood, SG.tube(pol(deg, r0 - 0.05, by - 0.85), pol(deg, r1 + 0.7, by - 0.06), 0.075, 6), WDD);
          vc(M.vcMetal, SG.torus(0.07, 0.02, q.x, by - 0.14, q.z, 0, 0, 8), IR); chain(V(q.x, by - 0.12, q.z), V(q.x, top - 0.02, q.z)); lantern(q.x, y, q.z, s, deg * DEG); } }
      else { const p = pol(306, 9.9); chain(V(p.x, 15, p.z), V(p.x, 4.5, p.z)); lantern(p.x, 3.4, p.z, 2.6);
        for (const [deg, s] of [[18, 1.3], [162, 1.35]]) { const q = pol(deg, W0 - 0.45), bx = pol(deg, W0 + 0.1); vc(M.vcMetal, SG.tube(V(bx.x, WH + 0.45, bx.z), V(q.x, WH + 1.15, q.z), 0.035, 6), IRL); vc(M.vcMetal, SG.tube(V(bx.x, WH + 1.2, bx.z), V(q.x, WH + 1.15, q.z), 0.035, 6), IRL); chain(V(q.x, WH + 1.15, q.z), V(q.x, WH + 0.95, q.z)); lantern(q.x, WH + 0.5, q.z, s); } }
      // the ship's wheel on the far wall behind the pool, on a short post
      { const deg = 100, q = pol(deg, W0 + 0.25), n = V(-Math.cos(deg * DEG), 0, -Math.sin(deg * DEG)), cy = WH + 1.6; vc(M.vcWood, SG.box(0.16, 1.8, 0.16, q.x, WH + 0.8, q.z), WDD);
        const at = o => V(q.x + n.x * o, cy, q.z + n.z * o);
        vc(M.vcWood, alignZ(SG.torus(1.2, 0.1, 0, 0, 0, 0, 0, 28), n, at(0.2)), WDD); vc(M.vcWood, alignZ(SG.torus(0.55, 0.07, 0, 0, 0, 0, 0, 20), n, at(0.2)), WDD); vc(M.vcWood, alignZ(SG.cyl(0.24, 0.24, 0.26, 12, 0, 0, 0).rotateX(Math.PI / 2), n, at(0.2)), WD);
        for (let k = 0; k < 8; k++) { const t = k / 8 * 6.2832; vc(M.vcWood, alignZ(new THREE.BoxGeometry(0.1, 2.4, 0.08).rotateZ(t), n, at(0.2)), WD); vc(M.vcWood, alignZ(SG.cyl(0.06, 0.05, 0.4, 8, 0, 0, 0).rotateZ(t).translate(-Math.sin(t) * 1.5, Math.cos(t) * 1.5, 0), n, at(0.2)), WDD); } }
      // the slime falls: in four places the goo has slumped across the wall top and hangs down its face in a thick, lumpy sheet, its hem
      // in tongues of different lengths, a few heavy blobs on the lip; it pools on the floor below
      const blobs = [], drips = [];
      for (const [deg, w, nd] of [[22, 3.0, 3], [48, 1.6, 2], [132, 1.6, 2], [158, 2.9, 3]]) { const a = deg * DEG, nx = -Math.cos(a), nz = -Math.sin(a), tx = -nz, tz = nx, lip = pol(deg, W0 - 0.02), out_ = V(nx, 0, nz), along = V(tx, 0, tz);
        const f = { x: lip.x, z: lip.z, nx, nz, tx, tz, y0: WH + 0.3, w, reach: 0.55 }; falls.push(f);
        const dr = gooDrape(deg, W0, WT, WH, w, deg * 31 + 7); blobs.push(dr.g);
        const nb = Math.max(2, Math.round(w / 0.7)); for (let k = 0; k < nb; k++) { const u = (k + 0.5 + (R() - 0.5) * 0.5) / nb - 0.5, c = V(lip.x + tx * u * w * 0.9 + nx * 0.05, WH + 0.1 + R() * 0.04, lip.z + tz * u * w * 0.9 + nz * 0.05);
          blobs.push(gooBlob(c, out_, along, 0.24 + R() * 0.1, 0.22 + R() * 0.05, 0.12 + R() * 0.04, R())); }
        // the drips hang from the longest tongues, each in its own time (seconds: they stretch for most of it, then let go)
        for (const tp of dr.tips.slice(0, nd)) drips.push({ x: tp.x, y: tp.y, z: tp.z, T: 6.0 + R() * 4.5, ph: R() * 9, L: Math.min(0.45 + R() * 0.5, tp.y - 0.35), a: Math.atan2(nz, nx) });
        // the puddle at its foot, wide and thick
        blobs.push(gooPuddle(lip.x + nx * (0.75 + w * 0.2), lip.z + nz * (0.75 + w * 0.2), 0.75 + w * 0.42, 0.075, deg * 13));
        K.glow(lip.x + nx * 0.9, 0.3, lip.z + nz * 0.9, 1.4, 0x3C9A20); K.light(lip.x + nx * 0.9, 0.3, lip.z + nz * 0.9, 5.0, 0x7CE83A, 1.25); K.steam(lip.x + nx * 0.9, 0.15, lip.z + nz * 0.9, 0.5, 1.0, HI ? 0.4 : 0.25, 0.6); }
      { const uDr = [], uDl = []; for (let i = 0; i < 16; i++) { const d = drips[i]; if (!d) { uDr.push(new THREE.Vector4(0, 0, 0, 0)); uDl.push(0); continue; } const land = Math.sqrt(Math.max(0, 2 * (d.y - (d.L - 0.19) - 0.06) / 2.2));
          uDr.push(new THREE.Vector4(d.x + Math.cos(d.a) * 0.1, d.z + Math.sin(d.a) * 0.1, d.T, d.ph)); uDl.push(0.74 * d.T + land); }
        GOO_U.uDr = { value: uDr }; GOO_U.uDl = { value: uDl };
        const dm = new THREE.Mesh(gooDripGeo(drips), gooMat(GOO_DRIP_VS)); dm.frustumCulled = false; dm.layers.enable(3); dm.userData.own = true; K.add(dm);
        CQ_GOO.blobs = blobs; CQ_GOO.drips = drips; }
      // slime splashed over the flagstones: round the pool, under the falls, and in pools here and there
      { const pl = [], pud = (x, z, sz, k, rot) => { const g = atlasUV(new THREE.PlaneGeometry(sz, sz), k, 2); g.rotateX(-Math.PI / 2); g.rotateY(rot); g.translate(x, 0.012, z); pl.push(g); };
        const PUDS = [[250, 6.0, 3.4, 1], [275, 5.6, 2.6, 0], [300, 8.4, 2.4, 2], [220, 8.8, 2.0, 3], [120, 6.2, 2.8, 1], [95, 7.0, 2.2, 0], [60, 6.4, 2.6, 2], [160, 10.4, 1.8, 3], [20, 10.6, 1.9, 2], [330, 6.3, 2.1, 1], [200, 6.1, 2.3, 0], [350, 13.5, 1.6, 3], [140, 13.2, 1.4, 2], [75, 12.0, 2.0, 1], [185, 12.6, 1.7, 2], [265, 11.2, 2.2, 0], [310, 13.8, 1.5, 3], [40, 9.0, 1.6, 1]];
        // (thick goo, where the splashes were: the same places, a little smaller than the old flat splashes)
        const bl = CQ_GOO.blobs.slice(); for (const [deg, r, sz] of PUDS) { const p = pol(deg, r); bl.push(gooPuddle(p.x, p.z, sz * 0.36, 0.035 + sz * 0.012, deg * 7 + r)); }
        const bm = new THREE.Mesh(gooMerge(bl), gooMat(GOO_BLOB_VS)); bm.renderOrder = 2; bm.userData.own = true; K.add(bm); }
      // candles: along the wall's ledge, on the posts, on the floor by the wall
      for (const [deg, n] of (PM ? [[98, 3], [108, 1], [72, 2], [124, 2], [36, 2], [174, 2], [212, 1], [320, 2], [240, 2], [84, 2], [116, 1], [10, 2], [146, 1], [188, 2], [352, 2], [278, 2]] : [[98, 3], [108, 1], [72, 2], [124, 2], [58, 1], [36, 2], [174, 2], [4, 1], [212, 1], [320, 2], [300, 1], [240, 2], [64, 1], [144, 1], [84, 2], [116, 1], [12, 2], [148, 1], [188, 2], [336, 1], [352, 2], [262, 1], [278, 2], [140, 2], [66, 1]])) { const p = pol(deg, W0 + WT / 2); candles(p.x, WH, p.z, n, true, true); }
      if (PM) for (const deg of [104.4, 74.4, 344.4, 254.4, 164.4]) { const p = pol(deg, W0 + WT / 2); candles(p.x, 3.14, p.z, 1, true, true); }
      else for (const deg of [105, 75, 345, 255]) { const p = pol(deg, W0 + WT / 2 + 0.02); candles(p.x, WH + 0.6 + 0.35, p.z, 1, true); }
      for (const [deg, n] of [[188, 3], [118, 2], [56, 2], [330, 3], [262, 1], [236, 2], [300, 2], [10, 2], [146, 1], [80, 2]]) { const p = pol(deg, W0 - 0.7); candles(p.x, 0, p.z, n); }
      // coral at the foot of the wall and on the stones, kelp swaying by it
      for (const [deg, r, kind, s, n] of [[204, 16.5, 'pink', 2.0, 4], [176, 16.7, 'purple', 1.5, 3], [145, 16.6, 'orange', 1.8, 4], [112, 16.7, 'pink', 1.6, 3], [92, 16.5, 'orange', 1.5, 3], [62, 16.7, 'purple', 1.8, 4], [35, 16.6, 'pink', 2.0, 4], [344, 16.7, 'orange', 1.6, 3], [238, 16.3, 'purple', 1.6, 3], [312, 16.4, 'pink', 1.5, 3], [250, 12.2, 'pink', 1.4, 3], [290, 12.2, 'orange', 1.2, 2], [270, 16.5, 'purple', 1.4, 3], [8, 16.6, 'orange', 1.3, 2]]) { const p = pol(deg, r); coral(p.x, 0, p.z, s, kind, n); }
      for (const [deg, r, n] of [[186, 16.9, 3], [124, 16.8, 2], [66, 16.9, 3], [336, 16.8, 2], [270, 16.9, 2], [40, 16.7, 2], [100, 16.9, 3], [150, 16.8, 2], [208, 16.8, 2], [300, 16.8, 2], [11, 16.9, 2], [228, 16.8, 2], [84, 16.7, 2]]) { const p = pol(deg, r); kelp(p.x, 0, p.z, n, 1.1); }
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
      if (PM) { const mk = (nm, o) => { const m = cqInstanced(nm, PM[nm], cqMat(nm, Object.assign({ id: 'p' }, o)), { cull: true }); if (m) K.add(m); };
        mk('crate', { rough: 0.74, nk: 1, lift: 0.05, litK: 0.55 }); mk('barrel', { rough: 0.7, nk: 1, lift: 0.05, litK: 0.55 }); mk('lantern', { rough: 0.45, metal: 0.35, nk: 1, pane: 3.6 }); mk('candles', { rough: 0.45, nk: 0.6, lift: 0.04, c: 0xD8D0C8, litK: 0.4 }); mk('candlesF', { rough: 0.45, nk: 0, lift: 0.04, c: 0xD8D0C8, litK: 0.4 });
        for (const [x, y, z, sc, core] of flames) { K.glow(x, y + 0.06 * sc / 0.35, z, 0.06 + sc * 0.16, 0xFFC27A); if (HI && core && M.flameCore) put(M.flameCore, cqFlameG(sc).translate(x, y + 0.005, z)); } }
      K.glow(1, 21, 26, 8, 0x3A78A4); // (the surface's light, softly at the top of the view)
      K.anim({ tick(dt, t) { M.ray.uniforms.uTime.value = t; M.caustic.uniforms.uTime.value = t; M.water.uniforms.uTime.value = t; if (M.kelpT) M.kelpT.value = t; } });
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
  for (const [deg, r] of [[22, 15.6], [48, 15.9], [132, 15.9], [158, 15.6], [250, 6.3], [95, 7.0], [60, 6.5], [120, 6.3], [300, 8.4], [220, 8.8], [160, 10.4], [20, 10.6]]) { const [x, z] = pol(deg, r); RIVALS.push([x, 0, z]); }
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

KEEP = r"""
// ---------- (v309) the keep's models: the stone ruins, the cages, the pirate skeleton and the props were made from pictures by an image-to-3D
// generator and packed small (tools/glb2pack.py --v2: positions and uvs quantized to their boxes, normals in two bytes, the indices as
// varint steps, the maps as webp). The pack is a JSON block in the page (keepPack) that nothing reads at boot: Choose Event's warm-up or
// the stage's build decodes it, once ----------
const CQM = { E: null, G: {}, M: {}, T: {} };
const cqB64 = t => { if (typeof Uint8Array.fromBase64 === 'function') return Uint8Array.fromBase64(t); const s = atob(t), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; };
function cqEntries() { if (!CQM.E) { try { const el = document.getElementById('keepPack'); CQM.E = el ? JSON.parse(el.textContent) : {}; } catch (e) { CQM.E = {}; } } return CQM.E; }
// one model's geometry: positions and uvs out of their boxes, normals out of their two octahedral bytes, the indices out of their steps
function cqGeo(name) {
  if (CQM.G[name] !== undefined) return CQM.G[name];
  const E = cqEntries()[name]; if (!E || !E.b) return CQM.G[name] = null;
  const buf = cqB64(E.b).buffer, n = E.n, L = E.lay, qp = new Uint16Array(buf, L.pos, n * 3), qu = new Uint16Array(buf, L.uv, n * 2);
  const P = new Float32Array(n * 3), U = new Float32Array(n * 2), oct = (q, o) => { const N = new Float32Array(n * 3); for (let i = 0; i < n; i++) { let x = q[i * 2] / 127, y = q[i * 2 + 1] / 127; const z = 1 - Math.abs(x) - Math.abs(y);
    if (z < 0) { const tx = (1 - Math.abs(y)) * (x >= 0 ? 1 : -1); y = (1 - Math.abs(x)) * (y >= 0 ? 1 : -1); x = tx; } const l = Math.hypot(x, y, z) || 1; N[i * 3] = x / l; N[i * 3 + 1] = y / l; N[i * 3 + 2] = z / l; } return N; };
  for (let i = 0; i < n; i++) { for (let c = 0; c < 3; c++) P[i * 3 + c] = E.mn[c] + qp[i * 3 + c] / 65535 * (E.mx[c] - E.mn[c]); for (let c = 0; c < 2; c++) U[i * 2 + c] = E.umn[c] + qu[i * 2 + c] / 65535 * (E.umx[c] - E.umn[c]); }
  const ib = new Uint8Array(buf, L.idx, E.ib), I = n > 65535 ? new Uint32Array(E.ni) : new Uint16Array(E.ni); let p = 0, v = 0;
  for (let k = 0; k < E.ni; k++) { let z = 0, m = 1, c; do { c = ib[p++]; z += (c & 127) * m; m *= 128; } while (c & 128); v += z % 2 ? -(z + 1) / 2 : z / 2; I[k] = v; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.BufferAttribute(oct(new Int8Array(buf, L.nrm, n * 2)), 3)); g.setAttribute('uv', new THREE.BufferAttribute(U, 2)); g.setIndex(new THREE.BufferAttribute(I, 1));
  if (L.ink !== undefined) g.setAttribute('inkN', new THREE.BufferAttribute(oct(new Int8Array(buf, L.ink, n * 2)), 3));
  if (L.jaw !== undefined) g.setAttribute('aJaw', new THREE.BufferAttribute(new Uint8Array(buf, L.jaw, n), 1, true));
  if (L.joints !== undefined) { g.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint8Array(buf, L.joints, n * 4), 4)); g.setAttribute('skinWeight', new THREE.BufferAttribute(new Uint8Array(buf, L.weights, n * 4), 4, true)); }
  g.computeBoundingSphere(); g.computeBoundingBox(); E.b = null; return CQM.G[name] = g;
}
// a mirror image of a model (x the other way, the triangles wound the other way so they still face out)
function cqGeoFlip(name) {
  const id = name + '~'; if (CQM.G[id] !== undefined) return CQM.G[id]; const g0 = cqGeo(name); if (!g0) return CQM.G[id] = null;
  const g = g0.clone(), P = g.attributes.position.array, N = g.attributes.normal.array, I = g.index.array; for (let i = 0; i < P.length; i += 3) { P[i] = -P[i]; N[i] = -N[i]; }
  for (let k = 0; k < I.length; k += 3) { const t = I[k + 1]; I[k + 1] = I[k + 2]; I[k + 2] = t; } g.computeBoundingSphere(); g.computeBoundingBox(); return CQM.G[id] = g;
}
// a model's map: decoded by the browser off the main thread, the texture uploaded when it lands
function cqTex(name, key, srgb) {
  const E0 = cqEntries()[name]; if (E0 && E0.texOf) name = E0.texOf; const id = name + '.' + key; if (CQM.T[id]) return CQM.T[id];
  const E = cqEntries()[name], im = new Image(), t = new THREE.Texture(im); t.flipY = false; t.anisotropy = 4; if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  im.onload = () => { t.needsUpdate = true; }; im.src = 'data:' + E.mime + ';base64,' + E[key]; return CQM.T[id] = t;
}
// a model's look: its own colour map tinted by c; in Graphics mode its relief (normal map) and the stage's baked light and shade too
function cqMat(name, o) {
  o = o || {}; const id = name + (o.id || ''); if (CQM.M[id]) return CQM.M[id];
  const E0 = cqEntries()[name], E = E0 && E0.texOf ? cqEntries()[E0.texOf] : E0; if (!E) return null; const map = E.col ? cqTex(name, 'col', true) : null;
  const pb = HI ? Object.assign({ roughness: o.rough != null ? o.rough : 0.86, metalness: o.metal || 0 }, E.nrm && o.nk !== 0 ? { normalMap: cqTex(name, 'nrm', false), normalScale: new THREE.Vector2(o.nk || 1, o.nk || 1) } : {}) : null;
  const m = toon(o.c != null ? o.c : 0xFFFFFF, Object.assign({ map }, o.lift ? { emissive: new THREE.Color(o.lift, o.lift, o.lift * 1.1), emissiveMap: map } : {}, o.extra || {}), pb);
  const fk = o.fogK != null ? o.fogK : 1, lk = o.litK != null ? o.litK : 1, uJaw = { value: 0 }; m.userData.uJaw = uJaw; const hook = sh => {
    if (o.pane) sh.fragmentShader = sh.fragmentShader.replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\ntotalEmissiveRadiance += diffuseColor.rgb * smoothstep(0.18, 0.45, diffuseColor.r - diffuseColor.b) * ' + o.pane.toFixed(2) + ';');
    if (o.jaw) { sh.uniforms.uJaw = uJaw; sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float aJaw; varying float vJaw;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvJaw = aJaw;');
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform float uJaw; varying float vJaw;').replace('#include <color_fragment>', '#include <color_fragment>\ndiffuseColor.rgb *= 1.0 - uJaw * smoothstep(0.15, 0.6, 1.0 - abs(vJaw * 2.0 - 1.0)) * 0.92;'); } if (lk !== 1) sh.fragmentShader = sh.fragmentShader.replace('stageLit(vAOw, normalize(vAOn)) * (0.6 + 0.4 * sao)', 'stageLit(vAOw, normalize(vAOn)) * (0.6 + 0.4 * sao) * ' + lk.toFixed(3)); if (fk !== 1) sh.fragmentShader = sh.fragmentShader.replace('#include <fog_fragment>', '#ifdef USE_FOG\n gl_FragColor.rgb = mix(gl_FragColor.rgb, fogColor, smoothstep(fogNear, fogFar, vFogDepth) * ' + fk.toFixed(3) + ');\n#endif'); };
  if (HI) { aoPatch(m); m.onBeforeCompile = sh => { aoHook(sh); hook(sh); }; } else m.onBeforeCompile = hook; m.customProgramCacheKey = () => 'cq' + fk + '/' + lk + (o.jaw ? 'j' : '') + (o.pane ? 'p' + o.pane : ''); return CQM.M[id] = m;
}
// memory (as every canvas since v309): when the keep's canvas is let go (two others played since, or the phone asks for memory), or when
// Choose Event warmed the models and another canvas came instead, its meshes, maps and looks are given back; they're made again from the
// page's pack if the keep comes round
function conqFree() {
  if (!CQM.E && !Object.keys(CQM.G).length) return;
  for (const k in CQM.M) CQM.M[k].dispose(); for (const k in CQM.T) { const t = CQM.T[k]; t.dispose(); t.image = null; } for (const k in CQM.G) if (CQM.G[k]) CQM.G[k].dispose();
  CQM.E = null; CQM.G = {}; CQM.M = {}; CQM.T = {}; CQ_CULL.length = 0; if (CQ_CAGE.skel) CQ_CAGE.skel.mesh.skeleton.dispose(); CQ_CAGE.list = []; CQ_CAGE.skel = null; conqWarm.done = 0;
}
// (warmed while Choose Event is open: the geometry made and the maps decoding before the preview is opened)
function conqModelsWarm() { const E = cqEntries(), ks = Object.keys(E); let i = 0; // (one model a step, so the screen stays responsive)
  const step = () => { if (CQM.E !== E || i >= ks.length) return; const k = ks[i++]; cqGeo(k); if (E[k].col) cqTex(k, 'col', true); if (HI && E[k].nrm) cqTex(k, 'nrm', false); setTimeout(step, 16); }; step(); }
// the copies out of view aren't drawn: once a frame (and before a still) each culled set writes the copies the camera can see first and
// draws only those (a few dozen sphere tests)
const CQ_CULL = []; const cqFr = new THREE.Frustum(), cqPM = new THREE.Matrix4(), cqSph = new THREE.Sphere();
function conqCull() { if (!CQ_CULL.length) return; cqPM.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse); cqFr.setFromProjectionMatrix(cqPM);
  for (const c of CQ_CULL) { let n = 0, key = 0; for (let i = 0; i < c.mats.length; i++) { cqSph.center.copy(c.cen[i]); cqSph.radius = c.rad[i]; if (cqFr.intersectsSphere(cqSph)) { c.im.setMatrixAt(n++, c.mats[i]); key = key * 31 + i + 1 | 0; } }
    c.im.count = n; if (key !== c.key) { c.key = key; c.im.instanceMatrix.needsUpdate = true; } } }
// many copies of one model in one draw: each [x, y, z, turn, sx, sy, sz] (the model stands on y = 0 at its middle); bend: wrap it round
// the ring (its x along the circle at radius r, its z in and out), so straight wall sections close up into the round parapet
function cqInstanced(name, list, mat, o) {
  const g = name.endsWith('~') ? cqGeoFlip(name.slice(0, -1)) : cqGeo(name); if (!g || !list.length || !mat) return null; o = o || {};
  const im = new THREE.InstancedMesh(g, mat, list.length), m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sv = new THREE.Vector3(), pv = new THREE.Vector3();
  list.forEach((it, i) => { e.set(it[7] || 0, it[3], it[8] || 0, 'YXZ'); q.setFromEuler(e); m4.compose(pv.set(it[0], it[1], it[2]), q, sv.set(it[4], it[5] != null ? it[5] : it[4], it[6] != null ? it[6] : it[4])); im.setMatrixAt(i, m4); });
  im.instanceMatrix.needsUpdate = true; im.computeBoundingSphere(); im.receiveShadow = true; im.castShadow = !!o.cast; if (o.mirror !== false) im.layers.enable(3);
  if (o.cull) { const bs = g.boundingSphere, mats = [], cen = [], rad = []; for (let i = 0; i < list.length; i++) { const m = new THREE.Matrix4(); im.getMatrixAt(i, m); mats.push(m); cen.push(bs.center.clone().applyMatrix4(m)); rad.push(bs.radius * m.getMaxScaleOnAxis()); } CQ_CULL.push({ im, mats, cen, rad, key: -1 }); }
  return im;
}
// ---------- the cages on their chains (one draw for the three cages, one for the chains), swinging slowly like pendulums in the water, and
// the pirate skeleton in the first one, alive: it holds the bars and sways, looks round, calls out, turns its head to follow you, rattles the
// bars when you come close and laughs, its jaw flapping, when you fall in the slime ----------
const CQ_GOO = { blobs: [], drips: [] };
const CQ_WICKS = [[0.006, 0.929, -0.013], [0.295, 0.736, -0.01], [-0.168, 0.721, -0.283], [0.14, 0.721, -0.292], [0.189, 0.612, 0.298], [-0.179, 0.602, 0.288], [-0.335, 0.599, 0.029]];
const cqFlameG = s => { const k = 0.32 * s / 0.35, pts = [[0.001, 0], [0.035, 0.05], [0.028, 0.11], [0.001, 0.19]].map(([r, y]) => new THREE.Vector2(r * k, y * k)); return new THREE.LatheGeometry(pts, 5); };
const CQ_CAGE = { list: [], skel: null, cages: null, chains: null, cs: 1, CH: 2.6 };
const cqX = new THREE.Vector3(1, 0, 0), cqY = new THREE.Vector3(0, 1, 0), cqZ = new THREE.Vector3(0, 0, 1), cqQ = new THREE.Quaternion(), cqM4 = new THREE.Matrix4(), cqS4 = new THREE.Matrix4();
function conqCages(K, spots, tenant) {
  if (CQ_CAGE.skel) CQ_CAGE.skel.mesh.skeleton.dispose(); CQ_CAGE.list = []; CQ_CAGE.skel = null; const cg = cqGeo('cage'); if (!cg || !cqGeo('skeleton')) return false;
  const CH = CQ_CAGE.CH, cs = CQ_CAGE.cs = CH / ((cg.boundingBox.max.y - cg.boundingBox.min.y) || 1), D = Math.PI / 180, top = 15;
  // a chain of flat links from the anchor straight down, ten long (each cage's copy is stretched to its own length)
  const links = [], nl = 72; for (let i = 0; i < nl; i++) links.push(new THREE.BoxGeometry(i % 2 ? 0.028 : 0.09, 10 / nl * 1.3, i % 2 ? 0.09 : 0.028).translate(0, -(i + 0.5) * 10 / nl, 0));
  const chainM = toon(0x3A3F48, null, { metalness: 0.6, roughness: 0.45 }); if (HI) aoPatch(chainM);
  const cages = CQ_CAGE.cages = new THREE.InstancedMesh(cg, cqMat('cage', { rough: 0.5, metal: 0.5, nk: 1, lift: 0.1, fogK: 0.85 }), spots.length), chains = CQ_CAGE.chains = new THREE.InstancedMesh(mergeGeos(links), chainM, spots.length);
  for (const m of [cages, chains]) { m.frustumCulled = false; m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); m.receiveShadow = true; K.add(m); } chains.userData.own = true;
  spots.forEach(([kind, deg, r, y], i) => {
    const a = deg * D, x = Math.cos(a) * r, z = Math.sin(a) * r, L = top - (y + CH), grp = new THREE.Group(), inner = new THREE.Group();
    grp.position.set(x, top, z); inner.position.y = -L - CH; inner.rotation.y = Math.atan2(-x, -z); grp.add(inner); K.add(grp); // (the pivot at the anchor; the cage's floor turned to face the middle)
    let occ = null; if (kind === 'skeleton') occ = conqSkel(inner, cs); else { occ = tenant(kind); if (occ) inner.add(occ); }
    CQ_CAGE.list.push({ kind, x, z, L, grp, inner, occ, th: [0.05 * (i % 2 ? 1 : -1), -0.03], v: [0, 0.02], ph: i * 2.1 });
  });
  K.anim({ tick: conqCageTick }); conqCageTick(0, 0); return true;
}
function conqSkel(parent, cs) {
  const E = cqEntries().skeleton, g = cqGeo('skeleton'), sk = E.skel, nJ = sk.names.length;
  const bones = sk.names.map(nm => { const b = new THREE.Bone(); b.name = nm; return b; });
  sk.names.forEach((nm, i) => { const r = sk.rest[i]; bones[i].position.set(r[0], r[1], r[2]); bones[i].quaternion.set(r[3], r[4], r[5], r[6]); if (sk.parent[i] >= 0) bones[sk.parent[i]].add(bones[i]); });
  const mat = cqMat('skeleton', { id: 'sk', rough: 0.5, nk: 0.8, lift: 0.12, fogK: 0.85, jaw: true }), mesh = new THREE.SkinnedMesh(g, mat);
  mesh.add(bones[sk.parent.indexOf(-1)]); mesh.bind(new THREE.Skeleton(bones, sk.ibm.map(a => new THREE.Matrix4().fromArray(a))), new THREE.Matrix4()); mesh.frustumCulled = false;
  // standing on the cage's floor plate, a step toward the bars on the arena side (so its hands meet them)
  const S = 1.7, holder = new THREE.Group(); holder.scale.setScalar(S); holder.position.set(-sk.shift[0] * S, 0.085 * cs - sk.shift[1] * S, 0.12 - sk.shift[2] * S); holder.add(mesh); parent.add(holder);
  const clips = {}; for (const nm in E.clips) { const c = E.clips[nm], q = new Int16Array(cqB64(c.rot).buffer), pv = new Float32Array(cqB64(c.pos).buffer), tt = new Float32Array(c.n); for (let f = 0; f < c.n; f++) tt[f] = f / c.fps;
    const tracks = [new THREE.VectorKeyframeTrack('Pelvis.position', tt, pv)];
    for (let j = 0; j < nJ; j++) { if (sk.names[j] === 'Jaw') continue; const v = new Float32Array(c.n * 4); for (let f = 0; f < c.n; f++) for (let k = 0; k < 4; k++) v[f * 4 + k] = q[(f * nJ + j) * 4 + k] / 32767; tracks.push(new THREE.QuaternionKeyframeTrack(sk.names[j] + '.quaternion', tt, v)); }
    clips[nm] = new THREE.AnimationClip(nm, (c.n - 1) / c.fps, tracks); }
  const mixer = new THREE.AnimationMixer(mesh), act = {}; for (const nm in clips) act[nm] = mixer.clipAction(clips[nm]); act.idle.play();
  const B = {}; for (const b of bones) B[b.name] = b;
  // its hands on the bars: each arm raised from the hanging pose toward level and swung forward, the elbow bent in (left and right mirrored)
  const qa = (ax, a, ax2, a2) => new THREE.Quaternion().setFromAxisAngle(ax2, a2).multiply(new THREE.Quaternion().setFromAxisAngle(ax, a));
  const hold = { L_Shoulder: qa(cqZ, 0.62, cqY, -0.5), R_Shoulder: qa(cqZ, -0.62, cqY, 0.5), L_Elbow: qa(cqZ, 0.3, cqY, -0.55), R_Elbow: qa(cqZ, -0.3, cqY, 0.55) };
  const Sk = CQ_CAGE.skel = { mesh, mixer, act, B, mat, hold, hw: 1, cur: 'idle', T: 6, rattle: 0, laugh: 0, cool: 2, falls: (P.outWhy && P.outWhy.fall) || 0, look: 0,
    go(nm) { if (nm === this.cur || !this.act[nm]) return; const a = this.act[nm]; a.reset(); a.setEffectiveWeight(1); a.play(); this.act[this.cur].crossFadeTo(a, 0.45, false); this.cur = nm; } };
  return holder;
}
const cqTw = (q, axis, a) => q.multiply(cqQ.setFromAxisAngle(axis, a));
function conqCageTick(dt, t) {
  const L = CQ_CAGE.list; if (!L.length) return; dt = Math.min(dt || 0, 0.05);
  const { cages, chains, cs, CH } = CQ_CAGE;
  // the skeleton first: what it's up to, then the cage it shakes
  const Sk = CQ_CAGE.skel, c0 = L.find(c => c.kind === 'skeleton');
  if (Sk && c0) {
    const d = Math.hypot(P.x - c0.x, P.z - c0.z), falls = (P.outWhy && P.outWhy.fall) || 0;
    Sk.cool -= dt; if (d < 5.5 && P.st === 'play' && Sk.cool <= 0 && Sk.laugh <= 0) { Sk.rattle = 2.4; Sk.cool = 6.5; Sk.go('idle'); c0.v[0] += 0.09; c0.v[1] -= 0.07; }
    if (falls > Sk.falls) { Sk.laugh = 3.4; Sk.rattle = 0; Sk.go('laugh'); c0.v[1] += 0.05; } Sk.falls = falls;
    Sk.T -= dt; if (Sk.laugh <= 0 && Sk.rattle <= 0 && Sk.T <= 0) { const nx = Sk.cur !== 'idle' ? 'idle' : Math.random() < 0.55 ? 'look' : 'call'; Sk.go(nx); Sk.T = nx === 'idle' ? 5 + Math.random() * 5 : nx === 'call' ? 4.9 : 2.7; }
    if (Sk.laugh > 0) { Sk.laugh -= dt; if (Sk.laugh <= 0) { Sk.go('idle'); Sk.T = 4; } }
    Sk.mixer.update(dt); const B = Sk.B;
    // the arms back on the bars (all the way while it holds or rattles them, most of the way while it looks round, half while it calls, not while it laughs)
    const hwT = Sk.laugh > 0 ? 0 : Sk.cur === 'call' ? 0.5 : Sk.cur === 'look' ? 0.85 : 1; Sk.hw += (hwT - Sk.hw) * Math.min(1, dt * 4);
    for (const k in Sk.hold) B[k].quaternion.slerp(Sk.hold[k], Sk.hw);
    // the rattle on top: spine and shoulders shaking hard, the head with them
    const rk = Math.min(1, Math.max(0, Sk.rattle) / 0.4); Sk.rattle -= dt;
    if (rk > 0) { const sh = Math.sin(t * 21), pu = Math.sin(t * 21 + 1.2); cqTw(B.Spine2.quaternion, cqZ, 0.08 * rk * sh); cqTw(B.Spine3.quaternion, cqX, 0.1 * rk * pu); cqTw(B.L_Shoulder.quaternion, cqY, 0.2 * rk * pu); cqTw(B.R_Shoulder.quaternion, cqY, -0.2 * rk * pu); cqTw(B.L_Elbow.quaternion, cqY, 0.15 * rk * sh); cqTw(B.R_Elbow.quaternion, cqY, -0.15 * rk * sh); cqTw(B.Head.quaternion, cqZ, 0.12 * rk * Math.sin(t * 17)); }
    // the head turns to follow you while it holds the bars (not while it laughs or calls)
    const face = c0.inner.rotation.y + c0.grp.rotation.y; let want = 0; if (d < 13 && (Sk.cur === 'idle')) { want = Math.atan2(P.x - c0.x, P.z - c0.z) - face; want = Math.atan2(Math.sin(want), Math.cos(want)); want = Math.max(-0.8, Math.min(0.8, want)); }
    Sk.look += (want - Sk.look) * Math.min(1, dt * 3); cqTw(B.Neck.quaternion, cqY, Sk.look * 0.45); cqTw(B.Head.quaternion, cqY, Sk.look * 0.55);
    // the jaw: flapping when it laughs, chattering when it rattles, calling out, else a slow little chew
    const jaw = Sk.laugh > 0 ? 0.2 + 0.22 * Math.abs(Math.sin(t * 12)) : rk > 0 ? 0.08 + 0.18 * Math.abs(Math.sin(t * 16)) : Sk.cur === 'call' ? 0.06 + 0.2 * Math.max(0, Math.sin(t * 7)) : 0.03 + 0.03 * Math.max(0, Math.sin(t * 1.7));
    B.Jaw.quaternion.setFromAxisAngle(cqX, jaw); Sk.mat.userData.uJaw.value = Math.min(1, jaw / 0.22);
  }
  // each cage a pendulum from its anchor, slow in the water, nudged now and then by the current, twisting a little on its chain
  for (let i = 0; i < L.length; i++) { const c = L[i], w2 = 9.8 / (c.L + CH * 0.6) * 0.3;
    for (let k = 0; k < 2; k++) { const f = 0.01 * Math.sin(t * Math.sqrt(w2) * (k ? 0.91 : 1.0) + c.ph + k * 1.7); c.v[k] += (-w2 * c.th[k] - 0.16 * c.v[k] + f) * dt; c.th[k] += c.v[k] * dt; }
    c.grp.rotation.set(c.th[0], 0.22 * Math.sin(t * 0.19 + c.ph), c.th[1]); c.grp.updateMatrixWorld(true);
    chains.setMatrixAt(i, cqM4.copy(c.grp.matrixWorld).multiply(cqS4.makeScale(1, c.L / 10, 1))); cages.setMatrixAt(i, cqM4.copy(c.inner.matrixWorld).multiply(cqS4.makeScale(cs, cs, cs))); }
  cages.instanceMatrix.needsUpdate = true; chains.instanceMatrix.needsUpdate = true;
}

// ---------- (v309) the keep's ooze: thick, glossy goo, all of it one look with a light of its own (a deep saturated green body, bright sharp
// highlights, only a soft glow from inside). The pool's surface is lumpy and slow, with bubbles that swell and pop; the spout rises from its
// middle; in four places the goo has slumped across the wall top and hangs down the face in a thick sheet with tongues, and drips stretch
// slowly from the tongues, let go now and then, fall and splat into the puddle at its foot; puddles of it lie thick on the floor. Four
// draws; everything moves in the shaders ----------
const GOO_U = { uTime: { value: 0 }, uK: { value: 1 }, uDeep: { value: new THREE.Color(0x03200A) }, uBody: { value: new THREE.Color(0x167A10) }, uGlow: { value: new THREE.Color(0x0A4005) } };
const GOO_FRAG = `uniform float uK; uniform vec3 uDeep, uBody, uGlow; varying vec3 vW, vN; varying float vThick;
#include <fog_pars_fragment>
void main(){ vec3 N = normalize(vN), V = normalize(cameraPosition - vW); float ndv = clamp(dot(N, V), 0.0, 1.0), fr = pow(1.0 - ndv, 3.5);
  vec3 L1 = normalize(vec3(0.3, 1.0, 0.25)), L2 = normalize(vec3(-0.55, 0.55, -0.6)), L3 = normalize(vec3(0.6, 0.35, -0.7));
  vec3 col = mix(uDeep, uBody, 0.25 + 0.75 * ndv) * (0.4 + 0.6 * max(dot(N, L1), 0.0));
  col += uGlow * (0.25 + 0.75 * vThick) * (0.3 + 0.7 * ndv);
  float s1 = pow(max(dot(N, normalize(L1 + V)), 0.0), 160.0), s2 = pow(max(dot(N, normalize(L2 + V)), 0.0), 70.0), s3 = pow(max(dot(N, normalize(L3 + V)), 0.0), 90.0);
  col += vec3(0.92, 1.0, 0.9) * s1 * 3.4 + vec3(1.0, 0.8, 0.5) * s2 * 1.0 + vec3(0.8, 0.98, 0.9) * s3 * 1.4 + vec3(0.1, 0.4, 0.13) * fr * (0.35 + 0.65 * max(N.y, 0.0));
  gl_FragColor = vec4(col * uK, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  #include <fog_fragment>
}`;
const GOO_NOISE = `float gHash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float gNoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(gHash(i), gHash(i + vec2(1.0, 0.0)), f.x), mix(gHash(i + vec2(0.0, 1.0)), gHash(i + vec2(1.0, 1.0)), f.x), f.y); }`;
const gooMat = (vs, uni) => new THREE.ShaderMaterial({ uniforms: Object.assign(THREE.UniformsUtils.clone(THREE.UniformsLib.fog), GOO_U, uni || {}), vertexShader: vs, fragmentShader: GOO_FRAG, fog: true });
// the pool's surface: lumps drifting slowly, the bubbles (six at a time: x, z, size, how far along), a mound and a crown round the spout's foot
const GOO_POOL_VS = `uniform float uTime; uniform vec4 uBub[6]; varying vec3 vW, vN; varying float vThick;
#include <fog_pars_vertex>
${GOO_NOISE}
float poolH(vec2 p){ float t = uTime, h = (gNoise(p * 0.9 + vec2(t * 0.08, -t * 0.05)) - 0.5) * 0.22 + (gNoise(p * 2.0 + vec2(-t * 0.1, t * 0.07)) - 0.5) * 0.09 + (gNoise(p * 4.3 + vec2(t * 0.06, t * 0.11)) - 0.5) * 0.03;
  for (int i = 0; i < 6; i++) { vec4 b = uBub[i]; if (b.w < 0.0) continue; float d = length(p - b.xy);
    if (b.w < 0.84) { float g = smoothstep(0.0, 0.84, b.w), r = b.z * (0.3 + 0.7 * g), q = 1.0 - d * d / (r * r); if (q > 0.0) h += b.z * 0.8 * g * sqrt(q); }
    else { float u = (b.w - 0.84) / 0.16, rr = b.z * (0.5 + 2.4 * u); h += 0.05 * (1.0 - u) * exp(-pow((d - rr) / 0.1, 2.0)) - 0.04 * (1.0 - u) * exp(-d * d / (b.z * b.z * 0.3)); } }
  float rc = length(p); return h + 0.24 * exp(-rc * rc / 0.3) + 0.06 * exp(-pow((rc - 0.72) / 0.2, 2.0)) * (0.75 + 0.25 * sin(atan(p.y, p.x) * 7.0 + t * 0.5)); }
void main(){ vec4 w = modelMatrix * vec4(position, 1.0); float e = 0.05, h = poolH(w.xz), hx = poolH(w.xz + vec2(e, 0.0)), hz = poolH(w.xz + vec2(0.0, e));
  w.y += h * (1.0 - 0.6 * smoothstep(3.3, 4.0, length(w.xz))); vW = w.xyz; vN = normalize(vec3(-(hx - h) / e, 1.0, -(hz - h) / e)); vThick = clamp(0.55 - h * 4.0, 0.0, 1.0);
  vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
}`;
// the spout: a column of goo (its profile in the geometry, s up it) breathing up and down, bulges creeping up it, leaning in the current
const GOO_SPOUT_VS = `attribute float aS; uniform float uTime; varying vec3 vW, vN; varying float vThick;
#include <fog_pars_vertex>
void main(){ float t = uTime, s = aS, a = atan(position.z, position.x), H = 1.15 + 0.14 * sin(t * 0.42) + 0.06 * sin(t * 1.07);
  float k = 1.0 + 0.22 * sin(s * 9.0 - t * 1.3) * (1.0 - 0.4 * s) + 0.08 * sin(a * 3.0 + t * 0.7 + s * 5.0);
  vec3 p = vec3(position.x * k, s * H, position.z * k); p.x += 0.14 * sin(t * 0.55) * s * s; p.z += 0.11 * cos(t * 0.47 + 1.0) * s * s;
  float lump = sin(a * 5.0 + s * 7.0 - t * 0.9) * sin(a * 3.0 - s * 11.0 + t * 0.6); p += normal * 0.035 * lump;
  vec3 n = normalize(normal + vec3(cos(a + 1.3), 0.0, sin(a + 1.3)) * 0.35 * lump + vec3(0.0, 0.25 * sin(s * 13.0 + a * 2.0 - t), 0.0));
  vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz; vN = normalize(mat3(modelMatrix) * n); vThick = 0.65;
  vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
}`;
// the blobs: the goo slumped over the wall top and the puddles on the floor, wobbling slowly; a puddle ripples where a drop lands in it
// (uDr: each drip's x, z, period, phase; uDl: when in its cycle the drop lands)
const GOO_BLOB_VS = `attribute float aW; uniform float uTime; uniform vec4 uDr[16]; uniform float uDl[16]; varying vec3 vW, vN; varying float vThick;
#include <fog_pars_vertex>
${GOO_NOISE}
float rip(vec2 p){ float h = (gNoise(p * 3.1 + vec2(uTime * 0.07, -uTime * 0.05)) - 0.5) * 0.03 + (gNoise(p * 7.3 - vec2(uTime * 0.05, uTime * 0.04)) - 0.5) * 0.012; for (int i = 0; i < 16; i++) { vec4 d = uDr[i]; if (d.z <= 0.0) continue; float tl = mod(uTime + d.w, d.z) - uDl[i];
    if (tl > 0.0 && tl < 1.5) { float r = length(p - d.xy), rr = 0.08 + tl * 0.55; h += 0.028 * (1.0 - tl / 1.5) * exp(-pow((r - rr) / 0.07, 2.0)) - 0.03 * max(0.0, 1.0 - tl * 3.0) * exp(-r * r / 0.02); } } return h; }
void main(){ float t = uTime; vec3 p = position + normal * 0.022 * sin(t * 0.8 + aW * 6.2832 + position.y * 3.0 + position.x * 1.7) * step(0.0, aW);
  vec4 w = modelMatrix * vec4(p, 1.0); vec3 n = normal;
  if (aW < 0.0) { float e = 0.04, h = rip(w.xz), hx = rip(w.xz + vec2(e, 0.0)), hz = rip(w.xz + vec2(0.0, e)); w.y += h * (-aW); n = normalize(n + vec3(-(hx - h) / e, 0.0, -(hz - h) / e) * (-aW) * 1.5); }
  vW = w.xyz; vN = normalize(mat3(modelMatrix) * n); vThick = 0.5; vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
}`;
// the drips: each a tongue of goo hanging from a blob at the lip (aA: where, aD: its period, phase, longest stretch, the way out of the
// wall), stretching slowly, its bulb swelling; then the bulb lets go and falls (slowly: thick goo, deep water), squashes flat where it
// lands and is gone, while the tongue snaps back up with a wobble. aS: how far down the tongue (s), and 1 for the drop
const GOO_DRIP_VS = `attribute vec3 aA; attribute vec4 aD; attribute vec2 aS; uniform float uTime; varying vec3 vW, vN; varying float vThick;
#include <fog_pars_vertex>
void main(){ float T = aD.x, tt = mod(uTime + aD.y, T), tR = 0.74 * T, Lm = aD.z, a = aD.w, g = 2.2;
  vec3 out_ = vec3(cos(a), 0.0, sin(a)), along = vec3(-sin(a), 0.0, cos(a)); float L, bulb, neck;
  if (tt < tR) { float u = tt / tR, e = u * u * (3.0 - 2.0 * u); L = mix(0.24, Lm, pow(e, 1.4)); bulb = mix(0.11, 0.19, e); neck = mix(0.1, 0.06, e); }
  else { float u = tt - tR; L = mix(0.24, 0.32 * Lm, exp(-u * 2.4)) + 0.05 * exp(-u * 2.0) * sin(u * 11.0); bulb = 0.11; neck = 0.1; }
  vec3 p; vec3 n;
  if (aS.y < 0.5) { float s = aS.x, y, r; float top = max(0.0, L - 2.0 * bulb);
    if (s < 0.7) { y = -s / 0.7 * top; r = mix(0.12, neck, smoothstep(0.0, 0.7, s)); }
    else { float v = (s - 0.7) / 0.3; y = -top - v * 2.0 * bulb; r = max(neck * (1.0 - v), bulb * pow(sin(3.14159 * v), 0.6)); }
    vec2 c = normalize(position.xz + vec2(1e-5)); n = normalize(along * c.x + out_ * c.y - vec3(0.0, smoothstep(0.8, 1.0, s) * 1.5, 0.0));
    p = aA + along * c.x * r + out_ * (c.y * r * 0.8 + r * 0.55) + vec3(0.0, y, 0.0); }
  else { float tau = tt - tR, y0 = -(Lm - 0.19), land = sqrt(max(0.0, 2.0 * (aA.y + y0 - 0.06) / g)); vec3 c = position; n = normalize(position);
    if (tau < 0.0 || tau > land + 0.4) p = aA; // (not yet let go, or already gone: folded away)
    else if (tau < land) { float y = y0 - 0.5 * g * tau * tau; p = aA + out_ * 0.14 + vec3(c.x * 0.19, y + c.y * 0.19 * 1.3, c.z * 0.19); }
    else { float k = (tau - land) / 0.4; p = vec3(aA.x, 0.08, aA.z) + out_ * 0.14 + vec3(c.x * 0.2 * (1.6 + k), max(-0.02, c.y) * 0.2 * 0.3 * (1.0 - k), c.z * 0.2 * (1.6 + k)); } }
  vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz; vN = normalize(mat3(modelMatrix) * n); vThick = 0.7; vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
}`;
// pieces of goo merged into one, their wobble phase (aW) kept with them
function gooMerge(list) { const g = mergeIdx(list); let n = 0; const W = new Float32Array(g.attributes.position.count); for (const p of list) { const a = p.attributes.aW, k = p.attributes.position.count; if (a) W.set(a.array.subarray(0, k), n); n += k; } g.setAttribute('aW', new THREE.BufferAttribute(W, 1)); return g; }
// the pool's bubbles: six slots, each swelling for a few seconds, popping and ringing out, then starting again somewhere else
const GOO_BUB = []; for (let i = 0; i < 6; i++) GOO_BUB.push(new THREE.Vector4(0, 0, 0.3, -1));
const gooBubS = []; function gooTick(dt, t) { GOO_U.uTime.value = t;
  for (let i = 0; i < 6; i++) { let b = gooBubS[i]; if (!b || t > b.t0 + b.T) { const a = Math.random() * 6.2832, r = 0.9 + Math.random() * 2.5; b = gooBubS[i] = { x: Math.cos(a) * r, z: Math.sin(a) * r, R: 0.28 + Math.random() * 0.36, t0: t + Math.random() * 1.6, T: 2.6 + Math.random() * 2.2 }; }
    const ph = (t - b.t0) / b.T; GOO_BUB[i].set(b.x, b.z, b.R, ph < 0 ? -1 : ph); } }
function gooPool(R) { const nr = 22, ns = 72, pos = [], idx = []; pos.push(0, 0, 0); for (let i = 1; i <= nr; i++) { const r = R * Math.pow(i / nr, 0.85); for (let k = 0; k < ns; k++) { const a = k / ns * 6.2832; pos.push(Math.cos(a) * r, 0, Math.sin(a) * r); } }
  for (let k = 0; k < ns; k++) idx.push(0, 1 + (k + 1) % ns, 1 + k); for (let i = 1; i < nr; i++) for (let k = 0; k < ns; k++) { const a = 1 + (i - 1) * ns + k, b = 1 + (i - 1) * ns + (k + 1) % ns, c = 1 + i * ns + k, d = 1 + i * ns + (k + 1) % ns; idx.push(a, b, c, b, d, c); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeBoundingSphere(); g.boundingSphere.radius += 1; return g; }
function gooSpout() { const prof = [[0.0, 0.66], [0.05, 0.5], [0.14, 0.38], [0.28, 0.31], [0.44, 0.27], [0.58, 0.29], [0.7, 0.36], [0.8, 0.4], [0.88, 0.37], [0.94, 0.28], [0.98, 0.14], [1.0, 0.0]];
  const pts = prof.map(([y, r]) => new THREE.Vector2(Math.max(0.001, r), y)), g = new THREE.LatheGeometry(pts, 18); const P = g.attributes.position, S = new Float32Array(P.count); for (let i = 0; i < P.count; i++) S[i] = P.getY(i);
  g.setAttribute('aS', new THREE.BufferAttribute(S, 1)); g.computeVertexNormals(); g.computeBoundingSphere(); g.boundingSphere.radius += 1.2; return g; }
// a thick puddle: an uneven outline, a flat top falling away in a rounded edge (aW: -1, so it ripples)
function gooPuddle(x, z, r, H, seed) { const R = rng(seed), ph = [R() * 6.28, R() * 6.28, R() * 6.28], rings = [0, 0.3, 0.55, 0.75, 0.88, 0.95, 1.0], ns = 22, pos = [], idx = [];
  for (const q of rings) for (let k = 0; k < ns; k++) { const a = k / ns * 6.2832, rr = r * (1 + 0.16 * Math.sin(2 * a + ph[0]) + 0.1 * Math.sin(3 * a + ph[1]) + 0.06 * Math.sin(5 * a + ph[2])) * q, h = H * Math.sqrt(Math.max(0, 1 - Math.pow(q, 6))) * (0.8 + 0.4 * (1 - q * q)); pos.push(x + Math.cos(a) * rr, 0.004 + h, z + Math.sin(a) * rr); }
  for (let i = 0; i < rings.length - 1; i++) for (let k = 0; k < ns; k++) { const a = i * ns + k, b = i * ns + (k + 1) % ns, c = a + ns, d = b + ns; idx.push(a, b, c, b, d, c); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals(); g.setAttribute('aW', new THREE.BufferAttribute(new Float32Array(pos.length / 3).fill(-1), 1)); return g; }
// a heavy blob slumped over the lip of the wall top: an ellipsoid half on the top and half hanging over (aW: its phase in the wobble)
function gooBlob(c, out_, along, sa, sr, sy, ph) { const g = new THREE.SphereGeometry(1, 16, 10), P = g.attributes.position, N = g.attributes.normal;
  for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i), yy = y < 0 ? y * 1.6 : y; P.setXYZ(i, c.x + along.x * x * sa - out_.x * z * sr, c.y + yy * sy, c.z + along.z * x * sa - out_.z * z * sr); }
  g.computeVertexNormals(); g.setAttribute('aW', new THREE.BufferAttribute(new Float32Array(P.count).fill(ph), 1)); g.deleteAttribute('uv'); return g; }
// a fall's sheet: the goo slumped across the wall top and hanging down the face, thick and lumpy, its hem in tongues of different lengths
// and rolled under (u across it; down its profile: from the back of the top, over the lip, down the face); aW: its wobble phase. Gives
// the geometry and the tongues' tips, longest first, where the drips hang
function gooDrape(deg, W0, WT, WH, w, seed) {
  const R = rng(seed), ph = [0, 1, 2, 3, 4].map(() => R() * 6.2832), nu = Math.max(24, Math.round(w * 20)), a0 = deg * Math.PI / 180, dA = w / W0;
  const nt = Math.max(2, Math.round(w * 1.7)), tg = []; for (let k = 0; k < nt; k++) tg.push({ c: (k + 0.5 + (R() - 0.5) * 0.5) / nt, s: 0.03 + R() * 0.04, L: 0.45 + R() * 0.8 });
  const env = (u, e) => Math.pow(Math.max(0, Math.sin(Math.PI * u)), e);
  const hem = u => { let h = 0.5 + 0.14 * Math.sin(u * 8 + ph[0]) + 0.07 * Math.sin(u * 21 + ph[1]); for (const t of tg) h += t.L * Math.exp(-Math.pow(Math.abs(u - t.c) / t.s, 3)); h = Math.min(h, 1.25 + 0.3 * Math.tanh((h - 1.25) / 0.3)); return Math.max(0.1, h * env(u, 0.6)); };
  const thick = u => (0.13 + 0.045 * Math.sin(u * w * 6 + ph[2]) + 0.03 * Math.sin(u * w * 15 + ph[3])) * env(u, 0.45);
  const back = u => WT * (0.4 + 0.2 * Math.sin(u * 6 + ph[4])) * env(u, 0.35);
  const pos = []; let np = 0;
  for (let i = 0; i <= nu; i++) { const u = i / nu, h = hem(u), rr = 1.15 * thick(u), tb = rr * 1.5, P = [];
    for (let k = 0; k <= 4; k++) { const q = k / 4; P.push([-back(u) * (1 - q), WH + rr * Math.sqrt(q)]); } // (on the top)
    for (let k = 1; k <= 3; k++) { const f = k / 8 * Math.PI; P.push([0.03 + Math.sin(f) * rr, WH + Math.cos(f) * rr]); } // (over the lip)
    for (let k = 0; k <= 7; k++) { const q = k / 7, lump = 1 + 0.2 * Math.sin(u * w * 5 + q * 6 + ph[0]) * Math.sin(u * w * 3.3 - q * 8 + ph[3]); P.push([0.03 + rr * (1 - 0.3 * q + 0.5 * Math.pow(q, 5)) * lump, WH - q * h]); } // (down the face)
    for (let k = 1; k <= 3; k++) { const f = k / 6 * Math.PI; P.push([0.03 + tb * Math.cos(f) * 0.9 - 0.02 * k, WH - h - tb * 0.5 * Math.sin(f)]); } // (the hem, rolled under)
    const a = a0 + (u - 0.5) * dA, ca = Math.cos(a), sa = Math.sin(a); for (const [o, y] of P) pos.push(ca * (W0 - o), y, sa * (W0 - o)); np = P.length; }
  const idx = []; for (let i = 0; i < nu; i++) for (let j = 0; j < np - 1; j++) { const a = i * np + j, b = a + np, c = a + 1, d = b + 1; idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  g.setAttribute('aW', new THREE.BufferAttribute(new Float32Array(pos.length / 3).fill(R()), 1));
  const tips = tg.map(t => { const h = hem(t.c), a = a0 + (t.c - 0.5) * dA, r = W0 - 0.03; return { x: Math.cos(a) * r, y: WH - h - 0.02, z: Math.sin(a) * r, h }; }).sort((p, q) => q.h - p.h);
  return { g, tips }; }
// a drip's tongue (13 rings down it, 8 round) and its drop (a ball), for the drip shader
function gooDripGeo(list) { const pos = [], aA = [], aD = [], aS = [], idx = []; const SS = [0, 0.12, 0.25, 0.38, 0.5, 0.62, 0.7, 0.76, 0.82, 0.88, 0.93, 0.97, 1.0], nseg = 8;
  for (const d of list) { let o = pos.length / 3;
    for (const s of SS) for (let k = 0; k < nseg; k++) { const a = k / nseg * 6.2832; pos.push(Math.cos(a), 0, Math.sin(a)); aA.push(d.x, d.y, d.z); aD.push(d.T, d.ph, d.L, d.a); aS.push(s, 0); }
    for (let i = 0; i < SS.length - 1; i++) for (let k = 0; k < nseg; k++) { const a = o + i * nseg + k, b = o + i * nseg + (k + 1) % nseg; idx.push(a, a + nseg, b, b, a + nseg, b + nseg); }
    o = pos.length / 3; const sp = new THREE.SphereGeometry(1, 10, 7), P = sp.attributes.position; for (let i = 0; i < P.count; i++) { pos.push(P.getX(i), P.getY(i), P.getZ(i)); aA.push(d.x, d.y, d.z); aD.push(d.T, d.ph, d.L, d.a); aS.push(0, 1); }
    for (let i = 0; i < sp.index.count; i++) idx.push(o + sp.index.array[i]); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(pos.slice(), 3)); g.setAttribute('aA', new THREE.Float32BufferAttribute(aA, 3)); g.setAttribute('aD', new THREE.Float32BufferAttribute(aD, 4)); g.setAttribute('aS', new THREE.Float32BufferAttribute(aS, 2)); g.setIndex(idx); return g; }
// straight wall sections wrapped round the ring, merged into one mesh: each [deg, sx, sy, sz, flip] puts a copy with its middle at angle deg
// on the circle of radius R, its length along the circle (x / R is the angle), its depth in and out (its front, +z, toward the middle)
function cqRing(name, R, list) {
  const g0 = cqGeo(name); if (!g0) return null; const P0 = g0.attributes.position.array, N0 = g0.attributes.normal.array, n = P0.length / 3, I0 = g0.index.array, out = [];
  for (const [deg, sx, sy, sz, flip] of list) { const a0 = deg * Math.PI / 180, P = new Float32Array(n * 3), N = new Float32Array(n * 3), f = flip ? -1 : 1;
    for (let i = 0; i < n; i++) { const x = P0[i * 3] * sx * f, y = P0[i * 3 + 1] * sy, z = P0[i * 3 + 2] * sz, ph = x / R, rho = R - z, nx = N0[i * 3] * f / sx, ny = N0[i * 3 + 1] / sy, nz = N0[i * 3 + 2] / sz;
      // (local: x along the wall, z toward the middle; the copy's own frame has the middle at +z, so the circle's centre is (0, 0, R))
      const lx = rho * Math.sin(ph), lz = R - rho * Math.cos(ph), mx = nx * Math.cos(ph) - nz * Math.sin(ph), mz = nx * Math.sin(ph) + nz * Math.cos(ph);
      // (then turned so that local +z points from the copy's place on the circle to the middle)
      const c = Math.cos(a0), s = Math.sin(a0), px = R * c, pz = R * s, ix = -c, iz = -s, tx = -s, tz = c; // (inward and along)
      P[i * 3] = px + tx * lx + ix * lz; P[i * 3 + 1] = y; P[i * 3 + 2] = pz + tz * lx + iz * lz; const ln = Math.hypot(mx, ny, mz) || 1; N[i * 3] = (tx * mx + ix * mz) / ln; N[i * 3 + 1] = ny / ln; N[i * 3 + 2] = (tz * mx + iz * mz) / ln; }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.BufferAttribute(N, 3)); g.setAttribute('uv', g0.attributes.uv);
    g.setIndex(new THREE.BufferAttribute(flip ? (() => { const J = I0.slice(); for (let k = 0; k < J.length; k += 3) { const t = J[k + 1]; J[k + 1] = J[k + 2]; J[k + 2] = t; } return J; })() : I0, 1)); out.push(g); }
  return mergeIdx(out, true);
}
// the ruins, placed to the picture: the parapet all round (straight sections wrapped round the ring, a capped post at the end of each), and
// outside it the stonework left to ruin: the two big arches framing the back (left and right of the pool, seen across it from the start),
// broken half arches, crumbling pillars, wall sections with arched windows, rubble at their feet. Each kind is one draw (instanced); the
// parapet is four (a quarter of the ring each, so the far side is skipped when it's out of view). Returns false without the models
function conqRuins(K) {
  CQ_CULL.length = 0; if (!cqGeo('parapet') || !cqGeo('arch')) return false;
  const W0 = K.T.ring.wall, WT = 0.7, WH = 2.3, D = Math.PI / 180, lo = !HI;
  const stone = { c: 0xB8B6D0, rough: 0.8, nk: 1.25, lift: 0.22, fogK: 0.55, litK: 0.6 }, wall = Object.assign({}, stone, { id: 'w', fogK: 0.8, lift: 0.12, litK: 0.45 }), far = Object.assign({}, stone, { id: 'f', fogK: 0.75, nk: 0 });
  // (the parapet model: 1.0 long, 0.515 high with its post, 0.24 deep, the wall's capstones at 0.377: so WH tall, WT deep, 15 degrees long)
  const Rm = W0 + WT / 2, seg = 15, sx = Rm * seg * D * 1.035, sy = WH / 0.377, sz = WT / 0.242;
  for (let q = 0; q < 4; q++) { const list = []; for (let k = 0; k < 24 / 4; k++) list.push([(q * 6 + k) * seg + seg / 2, sx, sy * (1 + 0.012 * Math.sin(q * 6 + k)), sz, 0]);
    const g = cqRing('parapet', Rm, list); if (!g) continue; const m = new THREE.Mesh(g, cqMat('parapet', wall)); m.receiveShadow = true; m.layers.enable(3); K.add(m); }
  // the pieces outside the wall: [model, deg, r, height, turn (from facing the middle), flip x]
  // (each model's front: the arch's faces +x, the rest +z; their heights: arch 1, half arch 1, pillar 1, window wall 1, rubble 0.58)
  const front = { arch: -Math.PI / 2, halfarch: 0, pillar: 0, wallwin: 0, rubble: 0, pillarF: 0, wallwinF: 0, halfarchF: 0 }, H0 = { arch: 1, halfarch: 1, pillar: 1, wallwin: 0.844, rubble: 0.57, pillarF: 1, wallwinF: 0.844, halfarchF: 1 };
  const P = [
    // the back left (seen across the pool from the start), in three layers: right behind the wall a tall broken wall section, a tall pillar
    // (where the lantern hangs), a half arch and a lower window wall stepping down toward the middle; behind them the great arch rising out
    // of the top of the view and a taller pillar and wall; far back in the haze more walls and pillars. The middle stays low, for the wrecks
    ['wallwin', 37, 19.1, 8.4, 0.05], ['pillar', 50, 19.6, 9.4, 0], ['halfarch', 63, 19.2, 8.2, 0.2, 1], ['wallwin', 77, 19.4, 5.0, 0],
    ['arch', 26, 21.8, 14.0, 0.1], ['pillar', 14, 20.6, 11.2, 0.5], ['wallwin', 56, 22.8, 7.6, 0.15],
    ['wallwinF', 33, 26.5, 10.5, -0.1], ['pillarF', 69, 26.0, 12.5, 0.2], ['halfarchF', 46, 27.5, 12.0, 0.1],
    // the back right, the same the other way round
    ['wallwin', 143, 19.1, 8.8, -0.05], ['pillar', 130, 19.5, 8.8, 0], ['halfarch', 117, 19.2, 7.8, -0.2], ['wallwin', 103, 19.4, 4.7, 0.1],
    ['arch', 154, 21.8, 14.4, -0.1], ['pillar', 166, 20.6, 10.6, -0.5], ['wallwin', 124, 22.8, 7.2, -0.15],
    ['wallwinF', 147, 26.5, 10.0, 0.1], ['pillarF', 111, 26.0, 12.0, -0.2], ['halfarchF', 134, 27.5, 11.5, Math.PI - 0.1],
    // round the sides and the front (behind you at the start): a third great arch, broken pillars, half arches, window walls, and far ones
    ['wallwin', 345, 19.3, 6.0, 0.1], ['pillar', 326, 19.0, 7.6, 0.4], ['halfarch', 302, 19.4, 9.2, 0.1, 1], ['arch', 270, 21.8, 15.0, 0],
    ['halfarch', 238, 19.4, 9.0, -0.1], ['pillar', 214, 19.0, 7.2, -0.4], ['wallwin', 195, 19.3, 5.6, -0.1],
    ['wallwinF', 286, 26.0, 9.0, 0], ['pillarF', 250, 25.5, 11.0, 0.3], ['wallwinF', 224, 26.5, 8.5, 0.2], ['pillarF', 312, 25.5, 10.0, -0.2], ['wallwinF', 4, 25.5, 8.0, 0.3], ['wallwinF', 176, 25.5, 8.4, -0.3],
    // rubble at their feet
    ['rubble', 44, 18.9, 1.1, 2.1], ['rubble', 70, 19.0, 1.0, 1.0], ['rubble', 110, 19.0, 1.05, 2.6], ['rubble', 137, 18.9, 1.0, 0.4],
    ['rubble', 206, 19.0, 1.0, 0.9], ['rubble', 314, 19.0, 1.05, 0.2],
  ];
  const by = {};
  for (const [nm, deg, r, h, turn, flip] of P) { if (lo && (nm === 'rubble' || nm.endsWith('F') || (nm === 'pillar' && (deg > 180)))) continue; if (!cqGeo(nm)) continue; const a = deg * D, s = h / H0[nm], face = Math.atan2(-Math.cos(a), -Math.sin(a));
    (by[nm + (flip ? '~' : '')] = by[nm + (flip ? '~' : '')] || []).push([Math.cos(a) * r, 0, Math.sin(a) * r, face + (flip ? -front[nm] : front[nm]) + (turn || 0), s]); }
  for (const nm in by) { const base = nm.replace('~', ''), m = cqInstanced(nm, by[nm], cqMat(base, base.endsWith('F') ? far : stone), { mirror: false, cull: true }); if (m) K.add(m); }
  K.anim({ tick: conqCull });
  return true;
}
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
    s = rep(s, "function sewerMats(M, T) {", CORE.replace('__CONQ_TEX__', json.dumps(TEX)).strip('\n') + KEEP.rstrip('\n') + "\nfunction sewerMats(M, T) {")
    assert '</' not in MODELS
    s = rep(s, '<script src="three.r186.min.js"></script>', '<script type="application/json" id="keepPack">' + MODELS + '</script>\n<script src="three.r186.min.js"></script>')
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
    # memory: the keep's models go with its canvas (v309's themeFree), or when another canvas comes after Choose Event warmed them
    s = rep(s, "    T.mats = null; T.decal = null; T.scat = null; T.sfUsed = null;\n", "    T.mats = null; T.decal = null; T.scat = null; T.sfUsed = null; if (T.ring) conqFree(); // (the keep's models with it)\n")
    s = rep(s, "while (thLru.length > keep) themeFree(thLru.pop()); }", "while (thLru.length > keep) themeFree(thLru.pop()); if (!thLru.some(T => T.ring)) conqFree(); }")
    # the stage's clean-up: copies drawn many times give back their copies' buffer, a group's pieces are disposed too, a skinned one's bones
    s = rep(s, "  for (const o of stageGroup.children.slice()) { stageGroup.remove(o); if (o.geometry) o.geometry.dispose(); if (o.userData.own) o.material.dispose();",
               "  for (const o of stageGroup.children.slice()) { stageGroup.remove(o); if (o.geometry) o.geometry.dispose(); if (o.userData.own) o.material.dispose(); if (o.isInstancedMesh) o.dispose(); if (o.isGroup) o.traverse(c => { if (c === o) return; if (c.geometry) c.geometry.dispose(); if (c.isSkinnedMesh && c.skeleton) c.skeleton.dispose(); if (c.userData.own && c.material) c.material.dispose(); }); /* (v309 keep) */")
    # the Season Conquest card: a stage preview now
    s = rep(s, '<div class="evcard soon" data-ev="conquest" style="--ec:#F2C14E"><button class="evmain" id="evConq" type="button" aria-disabled="true"><span class="evbar"><i>Coming soon</i></span>',
               '<div class="evcard" data-ev="conquest" style="--ec:#F2C14E"><button class="evmain" id="evConq" type="button"><span class="evbar"><i>Stage preview</i></span>')
    s = rep(s, '<b>Season Conquest</b><small>Claim the season’s canvases</small>', '<b>Season Conquest</b><small>Sunken Keep, stage only</small>')
    s = rep(s, '<img id="evConqArt" alt=""></span></button><i class="evsoon">Coming soon</i></div>', '<img id="evConqArt" alt=""></span></button><i class="evsoon">Stage preview</i></div>')
    s = rep(s, "$('evConq').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evConq').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Season Conquest is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); }); // (v300)",
               "$('evConq').addEventListener('click', uiClick(conqPreview)); // (v309: the stage preview)")
    s = rep(s, "set('evConqArt', 'island');", "{ const im = $('evConqArt'), src = CONQ_TEX.card; if (im.getAttribute('src') !== src) im.src = src; } setTimeout(conqWarm, 700); /* (v309: the keep's own picture) */")
    return s
