#!/usr/bin/env python3
"""v249: the sun, the rain and the orb no longer drag the frame rate down. What did it was the page around the canvas: effects that make
an iPhone redraw a layer every frame (a filter, a box shadow, a mask or a position animated frame by frame) and full-screen layers masked
with splat shapes (redrawn off screen each frame). The sun burning you switched on the heat vignette, the masked edge splats, a filtered
flash on the paint tank and another on the weather chip; low paint a filtered glow; the orb a pulsing pointer shadow, five full-screen
flash layers and, once giant, a hue-cycling tank; and the banner's pattern animated its mask all game long, even hidden. Now every
looping effect fades, moves or turns a layer drawn once, and the screen-edge paint and vignette are mixed into the frame's last pass on
the canvas (Graphics mode) or one light overlay pass (Performance mode, where the sun also stops re-rendering the whole frame into a
second high-precision buffer)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui188_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---------------------------------------------------------------- CSS: nothing on the HUD repaints every frame
CSS = r"""
/* ===== nothing repaints every frame: a looping effect fades, moves or turns a layer drawn once (a filter, a box shadow, a mask or a
   position changed frame by frame makes the page redraw that layer each frame, at three times the pixels on a phone). The screen-edge
   paint and the vignette are drawn on the canvas, in the frame's last pass ===== */
.vig{display:none!important}
/* the banner's paint pattern drifts only while the banner is up, as one sliding layer (108 px: a whole number of both its tiles) */
.banner .plate::before{animation:none;right:-108px}
.banner.on .plate::before{animation:platedrift 12s linear infinite}
@keyframes platedrift{to{transform:translateX(-108px)}}
/* the paint tank's glows: a layer of their own behind the tube, faded or turned */
.tank.low .ttrack,.tank.giant .ttrack,.tank.heat .ttrack{animation:none;filter:none}
.ttrack::after{content:"";position:absolute;left:-14px;right:-14px;top:-10px;bottom:-10px;z-index:-1;border-radius:40px;opacity:0;pointer-events:none;background:radial-gradient(closest-side,rgba(232,33,58,.95),rgba(232,33,58,.55) 60%,rgba(232,33,58,0))}
.tank.low .ttrack::after{animation:glowfade .45s ease-in-out infinite alternate}
.tank.heat .ttrack::after{background:radial-gradient(closest-side,rgba(255,248,214,1),rgba(255,200,90,.9) 42%,rgba(255,110,24,.55) 70%,rgba(255,110,24,0));animation:glowstep .3s steps(2) infinite}
.tank.giant .ttrack::after{left:-22px;right:-22px;top:-3px;bottom:-3px;border-radius:50%;background:conic-gradient(#FF4D6D,#FFD23F,#4DFFB8,#4DA6FF,#C77DFF,#FF4D6D);opacity:.85;animation:spinz .9s linear infinite}
@keyframes glowfade{from{opacity:.15}to{opacity:1}}
@keyframes glowfade2{to{opacity:1}}
@keyframes glowstep{50%{opacity:1}}
@keyframes spinz{to{transform:rotate(360deg)}}
/* the weather chip while the sun burns you: a light layer flashing over it (as the brightness flash did) */
.chip.wx.sun.burn{animation:none}
.chip.wx::after{content:"";position:absolute;inset:0;border-radius:3px;background:rgba(255,255,255,.4);opacity:0;pointer-events:none}
.chip.wx.sun.burn::after{animation:glowstep .3s steps(2) infinite}
/* the orb's and the gift's pointers on the screen edge, the foe pointer's warning, the incoming arrow: a glow layer fading in and out */
.orbptr.edge i{animation:orbspin 1.1s linear infinite}
.giftptr.edge i{animation:giftbob 1s ease-in-out infinite alternate}
.orbptr i::after{content:"";position:absolute;inset:-3px;border-radius:50%;box-shadow:0 0 22px 9px rgba(255,255,255,.9);opacity:0;pointer-events:none}
.giftptr i::after{box-shadow:0 0 24px 9px rgba(255,214,79,.95)}
.orbptr.edge i::after{animation:glowfade2 .7s ease-in-out infinite alternate}
.foeptr.warn i,.threatArrow i{animation:none}
.foeptr i::after,.threatArrow i::after{content:"";position:absolute;inset:-3px;border-radius:inherit;box-shadow:0 0 14px 6px rgba(255,59,92,.85);opacity:0;pointer-events:none}
.foeptr.warn i::after,.threatArrow i::after{animation:glowfade2 .35s ease-in-out infinite alternate}
/* the incoming-shot banner and the dry-out countdown: a color layer pulsing under the words */
.threat.on,.tdry{animation:none}
.threat,.tdry{isolation:isolate}
.threat::after,.tdry::after{content:"";position:absolute;inset:0;z-index:-1;border-radius:inherit;background:#FF6B84;opacity:0;pointer-events:none}
.threat.on::after,.tank.dry .tdry::after{animation:glowfade2 .4s ease-in-out infinite alternate}
/* the orb's flash round the screen: one layer, not five */
.orbflash,.orbflash i{will-change:auto}
.orbflash i{display:none}
.orbflash i:nth-child(1){display:block;background:linear-gradient(to right,#FF4D6D 0,rgba(0,0,0,0) 16%,rgba(0,0,0,0) 84%,#4DA6FF 100%),linear-gradient(to bottom,#FFD23F 0,rgba(0,0,0,0) 12%,rgba(0,0,0,0) 88%,#C77DFF 100%)}
.orbflash.on i:nth-child(1){animation:orbone 1.8s ease-out}
@keyframes orbone{0%{opacity:1}100%{opacity:0}}
/* the lobby: Play breathes with a light layer, its sheen and the shop banner's slide across, the victory ribbon's pattern holds still */
.playbtn::before{animation:none}
.playbtn .sheen::before{content:"";position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none;animation:breathop 2.8s ease-in-out infinite}
@keyframes breathop{50%{opacity:.09}}
.playbtn .sheen::after{animation:sheen2 3.2s ease-in-out infinite}
@keyframes sheen2{0%,55%{transform:skewX(-20deg)}100%{transform:translateX(615%) skewX(-20deg)}}
.shcat.season.shban .sbart::after{animation:sbshine2 5.2s ease-in-out 1.2s infinite}
@keyframes sbshine2{0%{transform:skewX(-18deg)}28%,100%{transform:translateX(607%) skewX(-18deg)}}
.lcat.fresh,.ltile.fresh,.eyes.fresh{animation:none}
.vrib::after{animation:none}
@media (prefers-reduced-motion:reduce){.banner.on .plate::before,.tank.low .ttrack::after,.tank.heat .ttrack::after,.tank.giant .ttrack::after,.chip.wx.sun.burn::after,.orbptr.edge i::after,.foeptr.warn i::after,.threatArrow i::after,.threat.on::after,.tank.dry .tdry::after,.playbtn .sheen::before,.playbtn .sheen::after,.shcat.season.shban .sbart::after{animation:none}}
"""
rep("""@media (prefers-reduced-motion:reduce){.tutdim.slow>b{transition:opacity .3s}.tut.swipe.on .tplate,.tut.swipe.on .thand{animation:none}}
</style>""", """@media (prefers-reduced-motion:reduce){.tutdim.slow>b{transition:opacity .3s}.tut.swipe.on .tplate,.tut.swipe.on .thand{animation:none}}""" + CSS + "</style>")

# ---------------------------------------------------------------- the screen-edge paint and vignette, on the canvas
EDGE_JS = r"""// ---------- the screen-edge paint (your color when you run low, orange while the sun burns you, the rival's color when a hit lands) and
// the vignette under it. They were page layers over the canvas, masked with the splat shapes and pulsing: a phone draws a masked layer off
// screen again every frame, and each change of state repainted them whole. Now the splat shapes are drawn once into a texture the size of
// the view (red: the low and heat splats, green: the hit's), and the frame's last pass mixes them in with the same timings ----------
const EDGE_SPL = [['m_splat2', -0.22, -0.14, 0.64], ['m_splat', 1.18, 1.08, 0.66], ['m_drip', 0.18, -0.04, 0.44], ['m_drip', 0.86, -0.06, 0.36], ['m_splat', -0.20, 1.12, 0.54], ['m_splat2', 1.20, -0.10, 0.50]];
const EDGE_HIT = [['m_splat', -0.20, -0.12, 0.70], ['m_splat2', 1.22, -0.08, 0.62], ['m_splat2', -0.24, 1.18, 0.60], ['m_splat', 1.24, 1.20, 0.74], ['m_drip', 0.42, -0.04, 0.40], ['m_splat2', 0.50, 1.28, 0.50]];
const EDGE_U = { tEdge: { value: null }, uEdgeK: { value: new THREE.Vector4(0, 0, 1, 0) }, uEdgeV: { value: new THREE.Vector4(0, 0.55, 0.6, 0) }, uEdgeC: { value: new THREE.Vector3() }, uHitC: { value: new THREE.Vector3() }, uVigC: { value: new THREE.Vector3() } };
const EDGE = { img: {}, w: 0, h: 0, tex: null, ink: new THREE.Vector3(0.89, 0.07, 0.18), f: [false, false, false], fT: -1e9, st: '', vigK: 0, splK: 0, hitT0: -9, on: false, last: 0, bq: 0 };
EDGE_U.tEdge.value = (() => { const t = new THREE.DataTexture(new Uint8Array(4), 1, 1); t.needsUpdate = true; return t; })();
const edgeRGB = (css, v) => { const h = parseInt(String(css).replace('#', ''), 16) || 0; return v.set(((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255); };
// the splat shapes laid out as the page laid them out: a box 5% bigger than the view all round, each shape placed by its percentages
function edgeBuild() {
  if (Object.keys(EDGE.img).length < 3) return;
  const vw = Math.max(1, viewW), vh = Math.max(1, viewH), k = Math.min(1.6, 1400 / Math.max(vw, vh)), W = Math.max(8, Math.round(vw * k)), H = Math.max(8, Math.round(vh * k));
  if (W === EDGE.w && H === EDGE.h) return;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const g = cv.getContext('2d', { willReadFrequently: true });
  const lay = list => { g.clearRect(0, 0, W, H); const bw = W * 1.1, bh = H * 1.1, ox = -W * 0.05, oy = -H * 0.05;
    for (const [n, px, py, sw] of list) { const im = EDGE.img[n], dw = sw * bw, dh = dw * im.naturalHeight / Math.max(1, im.naturalWidth); g.drawImage(im, ox + (bw - dw) * px, oy + (bh - dh) * py, dw, dh); }
    return g.getImageData(0, 0, W, H).data; };
  const a = lay(EDGE_SPL), b = lay(EDGE_HIT), rg = new Uint8Array(W * H * 2);
  for (let y = 0; y < H; y++) { const so = y * W * 4, dO = (H - 1 - y) * W * 2; for (let x = 0; x < W; x++) { rg[dO + x * 2] = a[so + x * 4 + 3]; rg[dO + x * 2 + 1] = b[so + x * 4 + 3]; } } // (its first row the bottom of the view)
  const t = new THREE.DataTexture(rg, W, H, THREE.RGFormat); t.minFilter = t.magFilter = THREE.LinearFilter; t.generateMipmaps = false; t.needsUpdate = true;
  const old = EDGE.tex; EDGE.tex = t; EDGE.w = W; EDGE.h = H; EDGE_U.tEdge.value = t; if (old) old.dispose();
}
for (const n of ['m_splat', 'm_splat2', 'm_drip']) { const im = new Image(); im.onload = () => { EDGE.img[n] = im; edgeBuild(); }; im.src = 'art/' + n + '.webp'; }
window.addEventListener('resize', () => { clearTimeout(EDGE.bq); EDGE.bq = setTimeout(edgeBuild, 250); });
const EDGE_VIG = { low: [0.58, 0.55], danger: [0.50, 0.62], heat: [0.42, 0.6], '': [0.55, 0.6] }, EDGE_NAVY = new THREE.Vector3(35 / 255, 38 / 255, 74 / 255), EDGE_ORANGE = new THREE.Vector3(1, 122 / 255, 30 / 255), EDGE_HEATV = new THREE.Vector3(1, 120 / 255, 30 / 255);
const edgeEase = x => 1 - (1 - x) * (1 - x);
// once a frame: the states the HUD asked for (fresh only while a match is drawing them), eased the way the page eased them
function edgeTick() {
  const now = performance.now() / 1000, dt = Math.min(0.1, Math.max(0, now - (EDGE.last || now))); EDGE.last = now;
  const live = now * 1000 - EDGE.fT < 150, [heat, danger, low] = live ? EDGE.f : [false, false, false], rm = reduceMotion;
  const st = heat ? 'heat' : danger ? 'danger' : low ? 'low' : '', hu = now - EDGE.hitT0, hitOn = hu >= 0 && hu < 1;
  if (st) EDGE.st = st;
  EDGE.vigK += ((st || hitOn ? 1 : 0) - EDGE.vigK) * (1 - Math.exp(-dt / 0.06));
  EDGE.splK += ((st === 'low' || st === 'heat' ? 1 : 0) - EDGE.splK) * (1 - Math.exp(-dt / 0.085));
  const L = EDGE.st || '', thr = rm ? 1 : L === 'low' && st ? 1 - 0.55 * (0.5 - 0.5 * Math.cos(6.2832 * now / 0.7)) : L === 'heat' && st ? 1 - 0.55 * (0.5 - 0.5 * Math.cos(6.2832 * now / 0.45)) : 1;
  const vo = EDGE.vigK * thr, vg = EDGE_VIG[hitOn && !st ? '' : L] || EDGE_VIG[''], U = EDGE_U;
  U.uEdgeV.value.set(vo, vg[0], vg[1], 0); U.uVigC.value.copy(hitOn && !st ? EDGE_NAVY : L === 'low' ? EDGE.ink : L === 'heat' ? EDGE_HEATV : EDGE_NAVY);
  const D = L === 'heat' ? 0.45 : 0.7, so = rm ? (L === 'heat' ? 0.85 : 0.72) : 0.32 + 0.38 * (0.5 - 0.5 * Math.cos(Math.PI * now / D));
  U.uEdgeK.value.x = EDGE.splK * so * vo; U.uEdgeC.value.copy(L === 'heat' ? EDGE_ORANGE : EDGE.ink);
  // the hit: in fast and big, held, fading as it grows a touch (the page's keyframes, each step eased out)
  let ho = 0, hs = 1; if (hitOn) { const u = hu; if (u < 0.1) { const e = edgeEase(u / 0.1); ho = e; hs = 1.18 - 0.18 * e; } else if (u < 0.55) { const e = edgeEase((u - 0.1) / 0.45); ho = 1 - 0.1 * e; hs = 1 + 0.02 * e; } else { const e = edgeEase((u - 0.55) / 0.45); ho = 0.9 * (1 - e); hs = 1.02 + 0.02 * e; } }
  U.uEdgeK.value.y = ho * Math.max(vo, hitOn ? 1 : 0); U.uEdgeK.value.z = hs;
  EDGE.on = vo > 0.003 || U.uEdgeK.value.y > 0.003;
}
function edgeReset() { EDGE.hitT0 = -9; EDGE.vigK = 0; EDGE.splK = 0; EDGE.f = [false, false, false]; EDGE.fT = -1e9; EDGE.st = ''; EDGE_U.uEdgeV.value.x = 0; EDGE_U.uEdgeK.value.x = 0; EDGE_U.uEdgeK.value.y = 0; EDGE.on = false; }
// Performance mode has no last pass: one light overlay instead (the edge paint, the vignette and the sun's warm tint, blended over)
let edgeOv = null;
function edgeOverlay(force) {
  if (!edgeOv) { const sc = new THREE.Scene(), cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), tri = new THREE.BufferGeometry(); tri.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
    const U = Object.assign({ uHeat: { value: 0 } }, EDGE_U);
    const m = new THREE.ShaderMaterial({ uniforms: U, transparent: true, depthTest: false, depthWrite: false, blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      vertexShader: 'varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: `uniform sampler2D tEdge; uniform vec4 uEdgeK, uEdgeV; uniform vec3 uEdgeC, uHitC, uVigC; uniform float uHeat; varying vec2 vUv;
        vec4 over(vec4 acc, vec3 c, float a){ return vec4(c * a + acc.rgb * (1.0 - a), a + acc.a * (1.0 - a)); }
        void main(){ vec4 acc = vec4(0.0);
          if (uHeat > 0.01) { float hv = smoothstep(0.3, 0.95, length(vUv - 0.5) * 1.45); acc = over(acc, vec3(1.0, 0.58, 0.28), uHeat * (0.22 + 0.4 * hv)); }
          if (uEdgeV.x > 0.003) { float d = length((vUv - 0.5) / vec2(0.75, 0.70)); acc = over(acc, uVigC, clamp((d - uEdgeV.y) / (1.0 - uEdgeV.y), 0.0, 1.0) * uEdgeV.z * uEdgeV.x); }
          if (uEdgeK.x > 0.003) acc = over(acc, uEdgeC, texture2D(tEdge, vUv).r * uEdgeK.x);
          if (uEdgeK.y > 0.003) { vec2 hu = (vUv - 0.5) / uEdgeK.z + 0.5; acc = over(acc, uHitC, texture2D(tEdge, hu).g * uEdgeK.y); }
          gl_FragColor = acc; }` });
    const q = new THREE.Mesh(tri, m); q.frustumCulled = false; sc.add(q); edgeOv = { sc, cam, m }; }
  edgeOv.m.uniforms.uHeat.value = force ? 0.02 : heatK;
  const ac = renderer.autoClear; renderer.autoClear = false; renderer.setRenderTarget(null); renderer.render(edgeOv.sc, edgeOv.cam); renderer.autoClear = ac;
}
function lodPass() { blobLOD(body); blobLOD(cBody); blobLOD(L2.body); }"""
rep("function lodPass() { blobLOD(body); blobLOD(cBody); blobLOD(L2.body); }", EDGE_JS)
# the frame: the overlay states eased every frame; Performance mode draws straight to the screen, the overlay over it when it shows
rep("""  if (post) { post.dofK.copy(state !== 'menu' ? DOF_PLAY : lookOpen ? DOF_LOOK : DOF_MENU); return post.render(); }
  if (heatK > 0.02) {
    const w = renderer.domElement.width, h = renderer.domElement.height;
    if (!postRT || postRT.width !== w || postRT.height !== h) { if (postRT) postRT.dispose(); postRT = new THREE.WebGLRenderTarget(w, h, { samples: 4, type: THREE.HalfFloatType }); }
    renderer.setRenderTarget(postRT); renderer.render(scene, camera); renderer.setRenderTarget(null);
    postU.tDiffuse.value = postRT.texture; postU.uHeat.value = heatK; postU.uTime.value = clock; renderer.render(postScene, postCam);
  } else renderer.render(scene, camera);""",
    """  edgeTick();
  if (post) { post.dofK.copy(state !== 'menu' ? DOF_PLAY : lookOpen ? DOF_LOOK : DOF_MENU); return post.render(); }
  renderer.render(scene, camera);
  if (EDGE.on || heatK > 0.02) edgeOverlay();""")
# the Graphics mode last pass mixes them in, over everything as the page layers were
rep("""  const cu = { tScene: { value: null }, tB1: { value: null }, tB2: { value: null }, tDof: { value: null }, uDof: { value: new THREE.Vector4(0.74, 1.0, 0.8, 0.07) }, uBloom: { value: 0.55 }, uSat: { value: 1.08 }, uCon: { value: 1.05 }, uLift: { value: new THREE.Vector3() }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uVig: { value: 0.22 }, uHeat: { value: 0 }, uTime: { value: 0 }, uExpo: { value: 1 } };""",
    """  const cu = { tScene: { value: null }, tB1: { value: null }, tB2: { value: null }, tDof: { value: null }, uDof: { value: new THREE.Vector4(0.74, 1.0, 0.8, 0.07) }, uBloom: { value: 0.55 }, uSat: { value: 1.08 }, uCon: { value: 1.05 }, uLift: { value: new THREE.Vector3() }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uVig: { value: 0.22 }, uHeat: { value: 0 }, uTime: { value: 0 }, uExpo: { value: 1 }, ...EDGE_U };""")
rep("""  const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2, tDof; uniform vec4 uDof; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime, uExpo; uniform vec3 uLift, uTint; varying vec2 vUv;""",
    """  const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2, tDof; uniform vec4 uDof; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime, uExpo; uniform vec3 uLift, uTint; varying vec2 vUv;
    uniform sampler2D tEdge; uniform vec4 uEdgeK, uEdgeV; uniform vec3 uEdgeC, uHitC, uVigC;""")
rep("""      float v = smoothstep(0.4, 1.12, length((vUv - 0.5) * vec2(1.0, 0.86)) * 1.42); c *= 1.0 - v * uVig;""",
    """      float v = smoothstep(0.4, 1.12, length((vUv - 0.5) * vec2(1.0, 0.86)) * 1.42); c *= 1.0 - v * uVig;
      if (uEdgeV.x > 0.003) { float d = length((vUv - 0.5) / vec2(0.75, 0.70)); c = mix(c, uVigC, clamp((d - uEdgeV.y) / (1.0 - uEdgeV.y), 0.0, 1.0) * uEdgeV.z * uEdgeV.x); }
      if (uEdgeK.x > 0.003) c = mix(c, uEdgeC, texture2D(tEdge, vUv).r * uEdgeK.x);
      if (uEdgeK.y > 0.003) { vec2 hu = (vUv - 0.5) / uEdgeK.z + 0.5; c = mix(c, uHitC, texture2D(tEdge, hu).g * uEdgeK.y); }""")
# the HUD hands its states over instead of switching page classes
rep("""    const vig = $('vig'); vig.classList.toggle('heat', burning); vig.classList.toggle('danger', ((dangerK > 0 && P.st === 'play') || foes(P).some(F => F.slam && (hc => Math.hypot(hc.x - P.x, hc.z - P.z))(slamCenter(F)) < slamRadius(F) + PR + 1)) && !burning); vig.classList.toggle('low', P.paint < 0.22 && P.st === 'play' && !(dangerK > 0) && !burning);""",
    """    EDGE.f[0] = burning; EDGE.f[1] = ((dangerK > 0 && P.st === 'play') || foes(P).some(F => F.slam && (hc => Math.hypot(hc.x - P.x, hc.z - P.z))(slamCenter(F)) < slamRadius(F) + PR + 1)) && !burning; EDGE.f[2] = P.paint < 0.22 && P.st === 'play' && !(dangerK > 0) && !burning; EDGE.fT = performance.now();""")
rep("""function hitEdge(A) { if (reduceMotion || !A || A === P) return; const v = $('vig'); v.style.setProperty('--hc', TEAMS[A.team].css); restartCls(v, 'hit'); }""",
    """function hitEdge(A) { if (reduceMotion || !A || A === P) return; edgeRGB(TEAMS[A.team].css, EDGE_U.uHitC.value); EDGE.hitT0 = performance.now() / 1000; }""")
rep("""$('vig').className = 'vig';""", """$('vig').className = 'vig'; edgeReset();""", 2)
rep("""  r.setProperty('--ink', css); r.setProperty('--ink-hi', c.hi);""", """  r.setProperty('--ink', css); edgeRGB(css, EDGE.ink); r.setProperty('--ink-hi', c.hi);""")
# Performance mode compiles the overlay up front with everything else
rep("""  warming = false; if (lobbyOn()) try { renderFrame(); } catch (e) {}""", """  if (!post) try { edgeOverlay(true); } catch (e) {}
  warming = false; if (lobbyOn()) try { renderFrame(); } catch (e) {}""")
# ---- the score strip's paint redraws thirty times a second, not every frame (a canvas redrawn is a texture sent to the screen again)
rep("""  L.tick = now => {
    if (L.cw < 0) L.measure(); const w = L.cw, h = L.ch; if (!w || !h || !L.segs.length) return; const dpr = Math.min(2, window.devicePixelRatio || 1);""",
    """  L.tick = now => {
    if (L.drawn && now - L.drawn < 30 && now >= L.drawn) return; L.drawn = now;
    if (L.cw < 0) L.measure(); const w = L.cw, h = L.ch; if (!w || !h || !L.segs.length) return; const dpr = Math.min(2, window.devicePixelRatio || 1);""")
rep('<p class="ver">Version 248</p>', '<p class="ver">Version 249</p>')
open(DST, 'w').write(s); print('ui189 ok', n0, '->', len(s))
