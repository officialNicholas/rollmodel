"""v331: real portraits in place of the drawn faces. Wherever the game showed a little drawn axolotl head for a character (the Friends
page: your tag, your friends, requests, the Friends board; online: Match found, the room, invites; the lobby's name tag and the Friends
button; the locker's tab; the results boards, the victory rows, the Showdown bar), it now shows that character as it really looks: its
paint, its eyes and what it wears, photographed head and shoulders.

- The studio: one stand-in character, made as a CPU's is, in a little scene of its own (a warm key light, a cool rim, a soft fill; no
  fog, no stage). For each look it's dressed, settled into a pose (a three-quarter turn, the head and eyes round to the camera, a
  smile, no blink) and shot with an 85 mm lens's narrow view (16 degrees) from far enough back that the head fills the frame without a
  wide lens's stretch: from the top of the head (or the hat) down to the top of the torso, which fades out at the bottom. Rendered at
  twice the size and scaled down, so the edges are smooth. Each look once, kept as a short blob link.
- When one isn't made yet a soft placeholder holds its place, and the portrait fades in as soon as it's ready (never mid-match: the
  match's own portraits are made while the stage is shown). If portraits can't be made at all, the drawn faces stay.
- Your friends see your hats and things too: your look on the server now carries what you wear (as the online one already did)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

PT_JS = r"""// ---------- (v331) portraits: each character's head and shoulders, photographed with a long lens, in place of the drawn faces ----------
// One stand-in, made as a CPU's is (the game's own body, wear and face), in a little studio scene of its own: dressed in a look, settled
// into a pose (a three-quarter turn, the head and eyes round to the camera, a smile, no blink), and shot with an 85 mm lens's narrow
// view (16 degrees) from far enough back that the head fills the frame with none of a wide lens's stretch: the top of the head (or the
// hat) to the top of the torso, which fades out at the bottom. Drawn at twice the size and scaled down (smooth edges), kept as a blob
// link, each look once. A page asks with ptHtml: the picture if it's made, else a placeholder (the drawn face inside it, for when no
// portrait can be made) that the portrait takes the place of when it's ready. One every few frames, never mid-match.
const PT = { built: false, ready: false, busy: false, fail: false, errs: 0, cool: 0, n: 0, jobs: [], map: new Map(), wait: document.getElementsByClassName('ptwait') };
const PT_S = 256, PT_SS = 2, PT_FOV = 16, PT_X = -640, PT_Z = 640, PT_SLOTS = ['head', 'back', 'mouth', 'eye', 'side', 'neck', 'lash', 'arms'];
// the pose and the light: the body turned this far from the face (rad), the lens this far round from the face's own line and above it,
// where the eyes look (face units), the three lights (times LIGHT_K)
const PT_K = Object.assign({ body: 0.22, turn: -0.12, el: 0.1, lookX: 0, lookY: 0.04, hemi: 0.5, key: 0.8, rim: 0.5 }, window.__ptK || {});
const ptOwn = (o, k) => typeof k === 'string' && Object.prototype.hasOwnProperty.call(o, k);
// a look the game made (yours, a CPU's): the paint, the eyes, what's worn
function ptSpec(hex, w) {
  w = w || {}; const s = { hex: (Number(hex) >>> 0) & 0xFFFFFF, eyes: ptOwn(EYE_STYLES, w.eyes) ? w.eyes : 'round', iris: ptOwn(EYE_COLS, w.iris) ? w.iris : 'brown' };
  for (const k of PT_SLOTS) s[k] = typeof w[k] === 'string' && /^[a-z]{2,12}$/.test(w[k]) ? w[k] : null; return s;
}
// a look from the server (a friend's, an online player's): only paints, eyes and things the game knows
function ptSpecNet(look) {
  look = look && typeof look === 'object' ? look : {}; const p = palOf(look.c) || PALETTE[0], w = look.w && typeof look.w === 'object' ? look.w : {}, s = ptSpec(p.hex, { eyes: look.e, iris: w.iris });
  for (const k of PT_SLOTS) { const v = w[k]; s[k] = typeof v === 'string' && WEAR.some(x => x.id === v && x.slot === k) ? v : null; } return s;
}
const ptKey = s => [s.hex.toString(16), s.eyes, s.iris].concat(PT_SLOTS.map(k => s[k] || '')).join('.');
function ptParse(k) { const a = String(k).split('.'); if (a.length !== 3 + PT_SLOTS.length) return null; const w = { eyes: a[1], iris: a[2] }; PT_SLOTS.forEach((n, i) => { w[n] = a[3 + i] || null; }); return ptSpec(parseInt(a[0], 16) || 0, w); }
function ptJob(k, s) {
  if (PT.fail) return null; let j = PT.map.get(k); if (j) return j.fail ? null : j;
  j = { k, s, url: '', fail: false }; PT.map.set(k, j); PT.jobs.push(j);
  if (PT.map.size > 120) for (const [k2, j2] of PT.map) { if (PT.map.size <= 96) break; if (j2.url || j2.fail) { PT.map.delete(k2); if (j2.url.startsWith('blob:')) try { URL.revokeObjectURL(j2.url); } catch (e) {} } }
  return j;
}
// the picture, or a placeholder for it (holding the drawn face, fb, for if it can't be made); cls: the class the drawn face had
function ptHtml(s, cls, fb) {
  const k = ptKey(s), j = ptJob(k, s);
  if (j && j.url) return '<img class="' + cls + ' ptimg" src="' + j.url + '" alt="" draggable="false" aria-hidden="true">';
  if (!j) return fb;
  return '<i class="' + cls + ' ptwait" data-pk="' + k + '" style="--pc:' + hexCss(s.hex) + '" aria-hidden="true">' + fb + '</i>';
}
const ptWant = s => { ptJob(ptKey(s), s); };
// placeholders on the page: made ones take their picture (fading in), ones that can't be made show their drawn face
function ptSweep() {
  for (const el of Array.from(PT.wait)) {
    const k = el.dataset.pk; let j = PT.map.get(k); if (!j && !PT.fail) { const s = ptParse(k); if (s) j = ptJob(k, s); }
    if (j && j.url) { const im = document.createElement('img'); im.className = el.className.replace('ptwait', 'ptimg ptin'); im.src = j.url; im.alt = ''; im.draggable = false; im.setAttribute('aria-hidden', 'true'); el.replaceWith(im); }
    else if (!j || j.fail) el.replaceWith(...el.childNodes);
  }
}
// the studio: the stand-in, three lights, a long lens
function ptBuild() {
  if (PT.built) return true; if (!VP.slime || !(AXOC.S.ready || SLIME.S.ready)) return false;
  PT.built = true;
  try {
    const sc = PT.scene = new THREE.Scene();
    PT.hemi = new THREE.HemisphereLight(0xFFFFFF, 0xD9CEC2, PT_K.hemi * LIGHT_K); PT.key = new THREE.DirectionalLight(0xFFF1E2, PT_K.key * LIGHT_K); PT.rim = new THREE.DirectionalLight(0xE4ECFF, PT_K.rim * LIGHT_K); // (about the lobby's light: brighter and the paints go pale)
    sc.add(PT.hemi, PT.key, PT.key.target, PT.rim, PT.rim.target);
    PT.cam = new THREE.PerspectiveCamera(PT_FOV, 1, 0.1, 80);
    // (the shot is taken at twice the size and halved on its way into the picture, each pixel the mean of four (smooth edges); and toned
    // there the game's own way: its tone mapping is only put on what's drawn to the screen, so the shot is taken in full range and run
    // through three's Neutral curve, the bright paints keeping their colour instead of clipping pale. Where the browser can't draw in full
    // range the shot is plain, and the lights a little lower)
    PT.tm = renderer.extensions.has('EXT_color_buffer_float') || renderer.extensions.has('EXT_color_buffer_half_float');
    PT.src = new THREE.WebGLRenderTarget(PT_S * PT_SS, PT_S * PT_SS, PT.tm ? { type: THREE.HalfFloatType } : { colorSpace: THREE.SRGBColorSpace });
    PT.rt = new THREE.WebGLRenderTarget(PT_S, PT_S, { colorSpace: THREE.SRGBColorSpace });
    { const tri = new THREE.BufferGeometry(); tri.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
      PT.tmM = new THREE.ShaderMaterial({ uniforms: { tMap: { value: PT.src.texture }, uExp: { value: 1 }, uTM: { value: PT.tm ? 1 : 0 } }, depthTest: false, depthWrite: false, blending: THREE.NoBlending,
        vertexShader: 'varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }',
        fragmentShader: 'precision highp float; uniform sampler2D tMap; uniform float uExp, uTM; varying vec2 vUv;\n'
          + 'vec3 neutral(vec3 c){ c *= uExp; float x = min(c.r, min(c.g, c.b)); c -= x < 0.08 ? x - 6.25 * x * x : 0.04; float pk = max(c.r, max(c.g, c.b)); if (pk < 0.76) return c; float d = 0.24, np = 1.0 - d * d / (pk + d - 0.76); c *= np / pk; float g = 1.0 - 1.0 / (0.15 * (pk - np) + 1.0); return mix(c, vec3(np), g); }\n'
          + 'void main(){ vec4 c = texture2D(tMap, vUv); if (c.a <= 0.0) { gl_FragColor = vec4(0.0); return; } vec3 k = c.rgb / c.a; gl_FragColor = vec4(uTM > 0.5 ? max(neutral(k), 0.0) : k, c.a); }' });
      const q = new THREE.Mesh(tri, PT.tmM); q.frustumCulled = false; PT.tmS = new THREE.Scene(); PT.tmS.add(q); PT.tmC = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1); }
    const D = newBlob(1, true); D.st = 'play'; ipReset(D);
    const L = makeCpuLook(D, TEAMS[1].wet); D.look = L; L.wear = makeWear(L.body);
    const w = { eyes: 'round', head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null, arms: null, iris: 'brown' }; L.wearing = w;
    attachSlime(L.V, L.wear, L.mat.color);
    for (const o of [L.shadow, L.warn, L.warnFill, L.foeMark, L.mark, L.V.puddle, L.stars]) if (o) { if (o.parent) o.parent.remove(o); o.visible = false; } L.V.puddle = null;
    sc.add(L.drop); L.drop.visible = true; L.drop.traverse(m => { if (m.material && m.material.depthFunc === THREE.GreaterDepth) m.layers.mask = 0; }); // (no see-through copy)
    PT.A = { D, L, V: L.V, w, s: null }; PT.cc = new THREE.Color(); PT.rimC = new THREE.Color(); PT.hb = new THREE.Box3(); PT.hc = new THREE.Vector3(); PT.hq = new THREE.Quaternion(); PT.ws = new THREE.Vector3(); PT.fw = new THREE.Vector3(); PT.wq = new THREE.Quaternion();
    if (HI && TH) try { themeEnv(TH); } catch (e) {}
    sc.environment = scene.environment || null;
    // its shaders made in the background where the browser can, for this target (the first portrait doesn't wait on them)
    PT.ready = true;
    if (renderer.compileAsync && renderer.extensions.has('KHR_parallel_shader_compile')) {
      const rt0 = renderer.getRenderTarget(); let p = null; renderer.setRenderTarget(PT.src); try { p = renderer.compileAsync(sc, PT.cam); } finally { renderer.setRenderTarget(rt0); }
      if (p) { PT.ready = false; p.catch(() => {}).then(() => { PT.ready = true; }); setTimeout(() => { PT.ready = true; }, 4000); }
    }
  } catch (e) { PT.fail = true; try { console.warn('portraits:', e); } catch (x) {} ptSweep(); return false; }
  return true;
}
// dressed in the look and settled into the pose: standing still, the head and eyes round to the camera, a smile
function ptPose(s) {
  const A = PT.A, D = A.D, L = A.L, V = A.V, w = A.w; A.s = s;
  w.eyes = s.eyes; w.iris = s.iris; for (const k of PT_SLOTS) w[k] = s[k]; L.wearing = w;
  L.mat.color.setHex(s.hex); L.mat.emissive.copy(L.mat.color).multiplyScalar(0.22);
  Object.assign(D, { x: PT_X, z: PT_Z, y: 0, yaw: 0, st: 'play', spd: 0, turn: 0, air: false, vy: 0, squash: 0, wob: 0, paint: 1, dry: false, power: null, turret: null, rocket: null, rollT: 0, flatT: 0, stunT: 0, frozenT: 0, emoT: 0, giantT: 0, charging: false, charge: 0, slam: false, missile: false, wearOff: false, wearHid: false, wearPop: 1 }); V.yawD = undefined;
  const ip = ipReset(D), wt = ip.watchO || (ip.watchO = { yaw: 0, pitch: 0, look: [0, 0] }); ip.expr = 'happy'; wt.yaw = PT_K.body; wt.pitch = 0.85 + PT_K.el * 0.8; wt.look[0] = PT_K.lookX; wt.look[1] = PT_K.lookY; ip.watch = wt;
  const I = V.slime, lk = I && I.ax && I.ax.look, st0 = state, nl = window.__noLod, dt = 0.05, ke = 1 - Math.exp(-dt * 10), kf = 1 - Math.exp(-dt * 16);
  const still = () => { if (!lk) return; lk.blinkK = 0; lk.blinkT = 9; lk.tbCool = 9; lk.flut = 0; lk.ovr = null; lk.emote = null; if (lk.att) { lk.att.t = 9; lk.att.eye[0] = lk.att.eye[1] = 0; } lk.dart[0] = lk.dart[1] = 0; lk.dartT = 9; };
  state = 'play'; window.__noLod = true;
  try { for (let i = 0, n = PT.primed ? 10 : 40; i < n; i++) { still(); blobVisual(D, V, dt, ke, kf); placeFaceCpu(L, dt); } PT.primed = true; } // (the first time, long enough for the new body to settle into its pose)
  finally { state = st0; window.__noLod = nl; }
  if (lk) { still(); lk.exprK = 1; lk.expr = lk.exprB; lk.U.fMix.value.x = 1; lk.U.fMix.value.y = 0; if (lk.coatMixT !== undefined) lk.U.uCoatMix.value = lk.coatMixT; } // (and its skin's easings where they end up: a new body starts part way)
  if (I && I.setPaint) I.setPaint(L.mat.color); // (its paint its own colour, not the stand-in's team's)
  L.drop.updateMatrixWorld(true);
}
// the frame: the head (and whatever's on it) and the top of the torso, square, through the long lens; the lights placed round it
function ptRender() {
  const A = PT.A, V = A.V, SI = V.slime, VB = V.body, W = A.L.wear, cam = PT.cam, hc = PT.hc, tv = Math.tan(PT_FOV * Math.PI / 360);
  let R = 0.3; hc.set(PT_X, 0.5, PT_Z);
  if (SI && SI.root && SI.root.visible) { const CH = SI.kind === 'axo' ? AXOC : SLIME; SI.root.updateWorldMatrix(true, true); VB.updateWorldMatrix(true, false); CH.headTop(SI, hc, PT.hq, 0); hc.applyMatrix4(VB.matrixWorld); R = CH.headSize(SI) * VB.getWorldScale(PT.ws).y; }
  // the top: the head's, or whatever's worn up there
  let top = hc.y + R; const hb = PT.hb.makeEmpty();
  for (const k in W) { const o = W[k]; for (const m of [].concat(o || [])) if (m && m.isObject3D && m !== W.body && m.visible) hb.expandByObject(m); }
  if (!hb.isEmpty()) top = Math.max(top, Math.min(hb.max.y, hc.y + R * 3.2));
  top += R * 0.1; const bot = hc.y - R * 1.5, half = Math.max((top - bot) / 2, R * 1.78), cy = (top + bot) / 2, dist = half / tv; // (the ears in, both sides)
  // the lens on the face's own line (where the head points, not the body), a little round from it and a little above
  const fw = PT.fw.set(0, 0, 1).applyQuaternion(PT.hq).applyQuaternion(VB.getWorldQuaternion(PT.wq)), az = Math.atan2(fw.x, fw.z) + PT_K.turn, el = clamp(Math.asin(clamp(fw.y, -1, 1)) * 0.5 + PT_K.el, 0.02, 0.35); PT.az = az;
  cam.position.set(hc.x + Math.sin(az) * Math.cos(el) * dist, cy + Math.sin(el) * dist, hc.z + Math.cos(az) * Math.cos(el) * dist); cam.up.set(0, 1, 0); cam.lookAt(hc.x, cy, hc.z);
  cam.aspect = 1; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  // a warm key high on the camera's left, a cool rim from behind on its right
  PT.key.position.set(hc.x + Math.sin(az - 0.8) * 4, hc.y + 4.4, hc.z + Math.cos(az - 0.8) * 4); PT.key.target.position.copy(hc); PT.key.target.updateMatrixWorld();
  PT.rim.position.set(hc.x - Math.sin(az + 0.55) * 4, hc.y + 2.6, hc.z - Math.cos(az + 0.55) * 4); PT.rim.target.position.copy(hc); PT.rim.target.updateMatrixWorld();
  const lk = SI && SI.ax && SI.ax.look; if (lk) lk.U.uKeyDir.value.copy(PT.key.position).sub(PT.key.target.position).normalize().transformDirection(cam.matrixWorldInverse);
  const lk2 = PT.tm ? LIGHT_K : LIGHT_K * 0.7; PT.hemi.intensity = PT_K.hemi * lk2; PT.key.intensity = PT_K.key * lk2; PT.rim.intensity = PT_K.rim * lk2; // (untoned, a little less)
  PT.scene.environment = scene.environment || null;
  if (window.__ptLog) { const m = SI && SI.ax ? SI.ax.S.mesh.material : null, U = lk ? lk.U : null; window.__ptLog.push({ k: ptKey(A.s), th: !!TH, env: !!(m && m.envMap), senv: !!PT.scene.environment, cm: U ? +U.uCoatMix.value.toFixed(3) : null, coat: U ? U.uCoat.value.toArray().map(v => +v.toFixed(3)) : null, paint: U ? U.uPaint.value.toArray().map(v => +v.toFixed(3)) : null, team: U ? U.uTeam.value.toArray().map(v => +v.toFixed(3)) : null, d2: U ? U.uDetail2.value.toArray().map(v => +v.toFixed(3)) : null, toon: U ? U.uToon.value : null, prog: m ? !!m.version : null }); } // (tests)
  const rt0 = renderer.getRenderTarget(), ca = renderer.getClearAlpha(), gk = RIG.uGrabK.value, gfn = JELLY_GRAB.fn; renderer.getClearColor(PT.cc); PT.rimC.copy(RIG.uRigRimC.value);
  try { RIG.uGrabK.value = 0; JELLY_GRAB.fn = null; RIG.uRigRimC.value.set(0xE8F0FF); renderer.setRenderTarget(PT.src); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(PT.scene, cam);
    PT.tmM.uniforms.uExp.value = renderer.toneMappingExposure; renderer.setRenderTarget(PT.rt); renderer.clear(); renderer.render(PT.tmS, PT.tmC); }
  finally { renderer.setRenderTarget(rt0); renderer.setClearColor(PT.cc, ca); RIG.uGrabK.value = gk; JELLY_GRAB.fn = gfn; RIG.uRigRimC.value.copy(PT.rimC); }
}
// the pixels to a picture: the right way up, half the size, the torso fading out at the bottom
function ptEncode(buf) {
  const c = document.createElement('canvas'); c.width = c.height = PT_S; const g = c.getContext('2d'), id = g.createImageData(PT_S, PT_S);
  for (let y = 0; y < PT_S; y++) id.data.set(buf.subarray((PT_S - 1 - y) * PT_S * 4, (PT_S - y) * PT_S * 4), y * PT_S * 4);
  g.putImageData(id, 0, 0);
  g.globalCompositeOperation = 'destination-in'; const gr = g.createLinearGradient(0, PT_S * 0.72, 0, PT_S); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, PT_S, PT_S); g.globalCompositeOperation = 'source-over';
  return new Promise((res, rej) => { const du = () => { try { res(c.toDataURL('image/png')); } catch (e) { rej(e); } };
    if (c.toBlob && window.URL && URL.createObjectURL) c.toBlob(b => { if (b) try { res(URL.createObjectURL(b)); } catch (e) { du(); } else du(); }, 'image/png'); else du(); });
}
async function ptShoot(j) {
  PT.busy = true;
  try {
    ptPose(j.s); ptRender(); const buf = new Uint8Array(PT_S * PT_S * 4);
    if (renderer.readRenderTargetPixelsAsync) await renderer.readRenderTargetPixelsAsync(PT.rt, 0, 0, PT_S, PT_S, buf); else renderer.readRenderTargetPixels(PT.rt, 0, 0, PT_S, PT_S, buf);
    let n = 0; for (let i = 3; i < buf.length; i += 32) if (buf[i]) n++;
    if (n < 20) { if ((j.tries = (j.tries || 0) + 1) < 3) { PT.jobs.push(j); return; } throw new Error('empty portrait'); } // (nothing drawn, the graphics lost a moment: again, later)
    j.url = await ptEncode(buf); PT.n++;
  } catch (e) { j.fail = true; if (++PT.errs >= 3) PT.fail = true; try { console.warn('portrait:', e); } catch (x) {} }
  finally { PT.busy = false; PT.cool = 2; ptSweep(); }
}
// each frame: placeholders put up since the last one, and a portrait now and then (not mid-match, mid-load, mid-wipe or in the intro)
function ptTick() {
  if (PT.wait.length) ptSweep();
  if (PT.busy || PT.fail || !PT.jobs.length || document.hidden) return;
  if (PT.cool > 0) { PT.cool--; return; }
  if (state === 'play' || building || irisBusy || (FL && FL.jin)) return;
  if (!PT.built && !ptBuild()) { if (!PT.t0) PT.t0 = performance.now(); else if (performance.now() - PT.t0 > 30000) { PT.fail = true; ptSweep(); } return; } // (the character never came: the drawn faces)
  if (!PT.ready || !ptSkinIn()) return; { const gl = renderer.getContext(); if (gl && gl.isContextLost && gl.isContextLost()) return; }
  ptShoot(PT.jobs.shift());
}
// (its skin's picture decoded: till then the body wears a plain pale stand-in, and a portrait would keep it)
function ptSkinIn() { const X = PT.A && PT.A.V.slime && PT.A.V.slime.ax; if (!X) return true; for (const M of [X.S, X.C]) { const t = M && M.mesh ? (M.full || M.mesh.geometry).userData.tex : null; if (t && !t.userData.ready) return false; } return true; }
// a match's portraits made before they're wanted (the Showdown bar, the results), while the stage is shown
function ptMatch() { try { for (const D of ACTIVE) ptWant(ptSpec(TEAMS[D.team].wet, lookOf(D))); } catch (e) {} }
"""

def apply(s):
    # the studio, ahead of the friends' faces (FR_FACES is made as the page loads)
    s = rep(s, "// a friend's face: the axolotl head in their paint\nfunction frFace(look) {\n",
               PT_JS + "// a friend's face: the axolotl head in their paint (v331: drawn, now only while their portrait's made, or if it can't be)\nfunction frFaceSvg(look) {\n")
    s = rep(s, "const FR_X = '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\">",
               "// (v331) a face as the character really looks: its portrait\nfunction frFace(look) { return ptHtml(ptSpecNet(look), 'frface', frFaceSvg(look)); }\n"
               "// (v331) the lobby's Friends button: three portraits for its three drawn faces\n"
               "{ const ff = document.querySelector('#friendsBtn .ffaces'); if (ff) { const fb = [...ff.children].map(e => e.outerHTML); ff.innerHTML = [[0xE3122F, 'round'], [0x2479D6, 'dot'], [0x7A4FE0, 'sly']].map(([h, e], i) => ptHtml(ptSpec(h, { eyes: e }), 'ffc', fb[i] || '')).join(''); } }\n"
               "const FR_X = '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\">")
    s = rep(s, "const FR_FACES = '<span class=\"ffaces\" aria-hidden=\"true\">' + ['green', 'purple'].map(c => frFace({ c })).join('') + '</span>';",
               "const FR_FACES = '<span class=\"ffaces\" aria-hidden=\"true\">' + [['green', 'round'], ['purple', 'sly']].map(([c, e]) => frFace({ c, e })).join('') + '</span>';")
    # the results boards, the victory rows, the Showdown bar, the lobby's name tag: the portrait in the coloured circle
    s = rep(s, "const faceIcon = (D, crown) => '<span class=\"bico\" style=\"--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '\">' + slimeIcon(TEAMS[D.team].wet, lookOf(D)) + (crown ? CROWN_SVG : '') + '</span>';",
               "const faceIcon = (D, crown) => '<span class=\"bico\" style=\"--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '\">' + ptHtml(ptSpec(TEAMS[D.team].wet, lookOf(D)), 'sface', slimeIcon(TEAMS[D.team].wet, lookOf(D))) + (crown ? CROWN_SVG : '') + '</span>'; // (v331: the portrait)")
    # the locker's tab and its picture: you as you are
    s = rep(s, "frFace({ c: colorId })", "frFace(frLook())", 3)
    # your look on the server: what you wear too (friends see it on your portrait)
    s = rep(s, "const frLook = () => ({ c: colorId, e: myLook.eyes });",
               "const frWear = () => { const w = {}; for (const k of PT_SLOTS) if (myLook[k]) w[k] = myLook[k]; w.iris = myLook.iris; return w; };\n"
               "const frLook = () => ({ c: colorId, e: myLook.eyes, w: frWear() }); // (v331: and what you wear)")
    s = rep(s, "const frSig = () => frName() + '|' + colorId + '|' + myLook.eyes + '|' + frRank();",
               "const frSig = () => frName() + '|' + colorId + '|' + myLook.eyes + '|' + frRank() + '|' + JSON.stringify(frWear());")
    s = rep(s, "Friends see your name, your paint colour and your rank, and when you’re online.",
               "Friends see your name, your look and your rank, and when you’re online.")
    # each frame; and a match's portraits made while its stage is shown
    s = rep(s, "sgTick(rdt); // (v313: the transform demo) // (v308: and behind every screen that covers it) // (v304: under Commissions the lobby holds still behind the blur)\n",
               "sgTick(rdt); // (v313: the transform demo) // (v308: and behind every screen that covers it) // (v304: under Commissions the lobby holds still behind the blur)\n"
               "  ptTick(); // (v331: the portraits)\n")
    s = rep(s, "giftPlan(); newItem = null; tutBegin();", "giftPlan(); newItem = null; tutBegin(); ptMatch();")
    # the CSS: the Friends button's faces whatever they are; the portraits; the placeholder
    s = rep(s, ".ffaces svg", ".ffaces>:is(svg,img,i)", 9)
    s = rep(s, "#mLocker.sgp .sgnote{justify-self:center;width:fit-content;max-width:calc(100% - 12px);margin:0 auto;padding:4px 10px;border-radius:9px;background:rgba(255,250,238,.95);box-shadow:0 2px 0 rgba(23,19,32,.2);color:#3A3048}\n</style>",
               "#mLocker.sgp .sgnote{justify-self:center;width:fit-content;max-width:calc(100% - 12px);margin:0 auto;padding:4px 10px;border-radius:9px;background:rgba(255,250,238,.95);box-shadow:0 2px 0 rgba(23,19,32,.2);color:#3A3048}\n"
               "/* (v331) the portraits, and the soft round placeholder that holds a portrait's place till it's made */\n"
               "img.ptimg{object-fit:cover;-webkit-user-drag:none;user-select:none;-webkit-user-select:none;pointer-events:none}\n"
               ".ptin{animation:ptin .3s ease-out both}\n@keyframes ptin{from{opacity:0;transform:scale(.92)}}\n"
               "i.ptwait{display:block;border-radius:50%;background:radial-gradient(circle at 50% 44%,color-mix(in srgb,var(--pc) 55%,#fff) 0 42%,transparent 43%);opacity:.35}\n"
               "i.ptwait>*{display:none}\n"
               ".bico i.ptwait{background:none}\n"
               "#friendsModal .frtagc:has(> img.frface){aspect-ratio:1/.94}#friendsModal .frtagc img.frface{position:absolute;left:5px;top:15px;width:calc(100% - 10px);height:calc(100% - 17px);margin:0;border-radius:6px;object-fit:cover;object-position:50% 30%}\n" # (your tag: the portrait as its photo, filling the card under the hook)

               "@media (prefers-reduced-motion:reduce){.ptin{animation:none}}\n</style>")
    return s
