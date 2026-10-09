P = '/home/claude/paint-the-canvas.html'
s = open(P).read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:150]); s = s.replace(old, new)

# ---------- theme lighting base + environment (sky light) ----------
rep("""// the sky, fog and moonlight shift with the theme
const CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xC2CAF0, manor: 0xE0C4E2, garden: 0xA6CCC0 };
function applyThemeLook(T) {
  TH = T; HOR.set(T.hor); cloudMat.color.set(CLOUD_TINT[T.id] || 0xD9D4F2); skyU.top.value.set(T.sky[0]); skyU.mid.value.set(T.sky[1]); skyU.hor.value.set(T.sky[2]); NIGHT.sky.set(T.hemi[0]); NIGHT.gnd.set(T.hemi[1]);
}""", """// the sky, fog and moonlight shift with the theme
const CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xC2CAF0, manor: 0xE0C4E2, garden: 0xA6CCC0 };
const BASE_NIGHT = { hemiI: 0.56, key: 0xC4BEFF, keyI: 0.5 };
// Graphics mode lights surfaces with the sky itself: each theme's sky (and its sun or moon) is filtered into an environment
// map once, so every physically based surface gets soft light from above, bounce from below and glossy reflections
const LK = HI ? { hemi: 0.42, key: 1.12 } : { hemi: 1, key: 1 };
const pmrem = HI ? new THREE.PMREMGenerator(renderer) : null, envScene = new THREE.Scene();
const envU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() }, gnd: { value: new THREE.Color() }, sunCol: { value: new THREE.Color() }, sunDir: { value: new THREE.Vector3(16, 30, 9).normalize() }, sunK: { value: 0 } };
envScene.add(new THREE.Mesh(new THREE.SphereGeometry(10, 48, 24), new THREE.ShaderMaterial({ uniforms: envU, side: THREE.BackSide, depthWrite: false,
  vertexShader: 'varying vec3 vD; void main(){ vD = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: `uniform vec3 top, hor, gnd, sunCol, sunDir; uniform float sunK; varying vec3 vD;
  void main(){ vec3 d = normalize(vD); float y = d.y;
    vec3 c = y > 0.0 ? mix(hor, top, pow(smoothstep(0.0, 1.0, y), 0.55)) : mix(hor, gnd, smoothstep(0.0, -0.32, y));
    float s = max(dot(d, normalize(sunDir)), 0.0); c += sunCol * (pow(s, 900.0) * 24.0 + pow(s, 40.0) * 0.9 + pow(s, 6.0) * 0.18) * sunK;
    gl_FragColor = vec4(c, 1.0); }` })));
function themeEnv(T) {
  if (!HI) return;
  if (!T.envRT) {
    const e = T.env || { top: new THREE.Color(T.hemi[0]).multiplyScalar(0.55).getHex(), hor: new THREE.Color(T.sky[2]).lerp(new THREE.Color(T.hemi[0]), 0.35).getHex(), gnd: new THREE.Color(T.hemi[1]).multiplyScalar(0.9).getHex(), sun: 0xD8D2FF, sunK: 0.35 };
    envU.top.value.set(e.top); envU.hor.value.set(e.hor); envU.gnd.value.set(e.gnd); envU.sunCol.value.set(e.sun); envU.sunK.value = e.sunK;
    T.envRT = pmrem.fromScene(envScene, 0.02);
  }
  scene.environment = T.envRT.texture;
}
function applyThemeLook(T) {
  TH = T; HOR.set(T.hor); cloudMat.color.set(CLOUD_TINT[T.id] || 0xD9D4F2); skyU.top.value.set(T.sky[0]); skyU.mid.value.set(T.sky[1]); skyU.hor.value.set(T.sky[2]); NIGHT.sky.set(T.hemi[0]); NIGHT.gnd.set(T.hemi[1]);
  const B = T.base || BASE_NIGHT; NIGHT.hemi = B.hemiI; NIGHT.key.set(B.key); NIGHT.keyI = B.keyI;
  themeEnv(T); if (post) post.grade(T);
}""")
rep("  hemi.color.copy(NIGHT.sky).lerp(DAY.sky, dayK); hemi.groundColor.copy(NIGHT.gnd).lerp(DAY.gnd, dayK); hemi.intensity = NIGHT.hemi + (DAY.hemi - NIGHT.hemi) * dayK - 0.08 * rainK;\n  sun.color.copy(NIGHT.key).lerp(DAY.key, dayK); sun.intensity = NIGHT.keyI + (DAY.keyI - NIGHT.keyI) * dayK - 0.18 * rainK;",
    "  hemi.color.copy(NIGHT.sky).lerp(DAY.sky, dayK); hemi.groundColor.copy(NIGHT.gnd).lerp(DAY.gnd, dayK); hemi.intensity = (NIGHT.hemi + (DAY.hemi - NIGHT.hemi) * dayK - 0.08 * rainK) * LK.hemi;\n  sun.color.copy(NIGHT.key).lerp(DAY.key, dayK); sun.intensity = (NIGHT.keyI + (DAY.keyI - NIGHT.keyI) * dayK - 0.18 * rainK) * LK.key;")

# ---------- post pipeline ----------
a = s.index("let postRT = null;")
b = s.index("// ---------- the victory screen ----------")
old_post = s[a:b]
heat_fs = old_post[old_post.index("fragmentShader: `uniform sampler2D tDiffuse;"):]
new_post = old_post.replace("function renderFrame() {\n  if (vic) return renderVictory();\n  if (heatK > 0.02) {", "function renderFrame() {\n  if (vic) return renderVictory();\n  if (post) return post.render();\n  if (heatK > 0.02) {")
new_post += r"""// ---------- Graphics mode post: the frame renders into an antialiased target, then a soft bloom from the brightest parts,
// a gentle grade (contrast and saturation, set per theme), the heat shimmer when the sun burns, a vignette and a dither ----------
const post = HI ? (() => {
  const gl2 = renderer.capabilities.isWebGL2, opt = { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBAFormat, depthBuffer: false, stencilBuffer: false };
  const main = gl2 && THREE.WebGLMultisampleRenderTarget ? new THREE.WebGLMultisampleRenderTarget(4, 4, Object.assign({}, opt, { depthBuffer: true })) : new THREE.WebGLRenderTarget(4, 4, Object.assign({}, opt, { depthBuffer: true }));
  const rt = () => new THREE.WebGLRenderTarget(4, 4, opt), A = rt(), B = rt(), C2 = rt(), D = rt(), E = rt();
  const ps = new THREE.Scene(), pc = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), tri = new THREE.BufferGeometry();
  tri.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
  const quad = new THREE.Mesh(tri); quad.frustumCulled = false; ps.add(quad);
  const VS = 'varying vec2 vUv; void main(){ vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }';
  const sm = (u, fs) => new THREE.ShaderMaterial({ uniforms: u, vertexShader: VS, fragmentShader: fs, depthTest: false, depthWrite: false });
  const bright = sm({ tSrc: { value: null }, uPx: { value: new THREE.Vector2() }, uTh: { value: 0.74 }, uKnee: { value: 0.22 } }, `uniform sampler2D tSrc; uniform vec2 uPx; uniform float uTh, uKnee; varying vec2 vUv;
    vec3 pick(vec2 uv){ vec3 c = texture2D(tSrc, uv).rgb; float l = max(c.r, max(c.g, c.b)), s = clamp(l - uTh + uKnee, 0.0, 2.0 * uKnee); s = s * s / (4.0 * uKnee + 1e-4); return c * max(s, l - uTh) / max(l, 1e-4); }
    void main(){ gl_FragColor = vec4((pick(vUv + uPx * vec2(-0.5, -0.5)) + pick(vUv + uPx * vec2(0.5, -0.5)) + pick(vUv + uPx * vec2(-0.5, 0.5)) + pick(vUv + uPx * vec2(0.5, 0.5))) * 0.25, 1.0); }`);
  const blur = sm({ tSrc: { value: null }, uDir: { value: new THREE.Vector2() } }, `uniform sampler2D tSrc; uniform vec2 uDir; varying vec2 vUv;
    void main(){ vec3 c = texture2D(tSrc, vUv).rgb * 0.227027;
      c += (texture2D(tSrc, vUv + uDir * 1.384615).rgb + texture2D(tSrc, vUv - uDir * 1.384615).rgb) * 0.316216;
      c += (texture2D(tSrc, vUv + uDir * 3.230769).rgb + texture2D(tSrc, vUv - uDir * 3.230769).rgb) * 0.070270;
      gl_FragColor = vec4(c, 1.0); }`);
  const cu = { tScene: { value: null }, tB1: { value: null }, tB2: { value: null }, uBloom: { value: 0.55 }, uSat: { value: 1.08 }, uCon: { value: 1.05 }, uLift: { value: new THREE.Vector3() }, uTint: { value: new THREE.Vector3(1, 1, 1) }, uVig: { value: 0.22 }, uHeat: { value: 0 }, uTime: { value: 0 } };
  const comp = sm(cu, `uniform sampler2D tScene, tB1, tB2; uniform float uBloom, uSat, uCon, uVig, uHeat, uTime; uniform vec3 uLift, uTint; varying vec2 vUv;
    void main(){ vec2 uv = vUv;
      if (uHeat > 0.01) { float k = uHeat * (0.6 + 0.4 * vUv.y); uv.x += (sin(uv.y * 42.0 + uTime * 5.2) * 0.0026 + sin(uv.y * 97.0 - uTime * 7.7) * 0.0012) * k; uv.y += cos(uv.x * 33.0 + uTime * 4.3) * 0.0016 * k; }
      vec3 c = texture2D(tScene, uv).rgb;
      c += (texture2D(tB1, uv).rgb * 0.75 + texture2D(tB2, uv).rgb * 0.6) * uBloom;
      float l = dot(c, vec3(0.299, 0.587, 0.114)); c = mix(vec3(l), c, uSat);
      c = (c - 0.5) * uCon + 0.5 + uLift; c *= uTint;
      if (uHeat > 0.01) { vec3 hot = c * vec3(1.1, 0.94, 0.78) + vec3(0.07, 0.03, 0.0); float hv = smoothstep(0.3, 0.95, length(vUv - 0.5) * 1.45); hot = mix(hot, hot * vec3(1.0, 0.62, 0.42), hv * 0.5); c = mix(c, hot, uHeat * 0.85); }
      float v = smoothstep(0.4, 1.12, length((vUv - 0.5) * vec2(1.0, 0.86)) * 1.42); c *= 1.0 - v * uVig;
      c += (fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) - 0.5) / 255.0;
      gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0); }`);
  const pass = (mat, src, dst) => { if (src) mat.uniforms.tSrc.value = src.texture; quad.material = mat; renderer.setRenderTarget(dst); renderer.render(ps, pc); };
  const sz = new THREE.Vector2();
  const P0 = { bloom: true, resize() { renderer.getDrawingBufferSize(sz); const w = Math.max(4, sz.x | 0), h = Math.max(4, sz.y | 0); main.setSize(w, h); A.setSize(w >> 1, h >> 1); B.setSize(w >> 2, h >> 2); C2.setSize(w >> 2, h >> 2); D.setSize(w >> 3, h >> 3); E.setSize(w >> 3, h >> 3); },
    grade(T) { const g = T.grade || {}; cu.uSat.value = g.sat || 1.08; cu.uCon.value = g.con || 1.05; cu.uVig.value = g.vig == null ? 0.24 : g.vig; cu.uBloom.value = g.bloom || 0.55; bright.uniforms.uTh.value = g.th || 0.74; const t = g.tint || [1, 1, 1], l = g.lift || [0, 0, 0]; cu.uTint.value.set(t[0], t[1], t[2]); cu.uLift.value.set(l[0], l[1], l[2]); },
    render() {
      renderer.setRenderTarget(main); renderer.render(scene, camera);
      if (P0.bloom) {
        bright.uniforms.uPx.value.set(1 / main.width, 1 / main.height); pass(bright, main, A);
        blur.uniforms.uDir.value.set(1 / B.width, 0); pass(blur, A, B); blur.uniforms.uDir.value.set(0, 1 / C2.height); pass(blur, B, C2);
        blur.uniforms.uDir.value.set(1 / D.width, 0); pass(blur, C2, D); blur.uniforms.uDir.value.set(0, 1 / E.height); pass(blur, D, E);
      }
      cu.tScene.value = main.texture; cu.tB1.value = C2.texture; cu.tB2.value = E.texture; cu.uHeat.value = heatK; cu.uTime.value = clock;
      const bk = cu.uBloom.value; if (!P0.bloom) cu.uBloom.value = 0;
      quad.material = comp; renderer.setRenderTarget(null); renderer.render(ps, pc); cu.uBloom.value = bk;
    } };
  return P0;
})() : null;
if (post) { post.resize(); window.addEventListener('resize', () => post.resize()); }

"""
s = s[:a] + new_post + s[b:]
# resize after pixel ratio changes
rep("function resize() { const b = stage.getBoundingClientRect(); viewW = Math.max(1, b.width); viewH = Math.max(1, b.height); pctRect = null; renderer.setSize(b.width, b.height, false);",
    "function resize() { const b = stage.getBoundingClientRect(); viewW = Math.max(1, b.width); viewH = Math.max(1, b.height); pctRect = null; renderer.setSize(b.width, b.height, false); if (typeof post !== 'undefined' && post) post.resize();")

# ---------- stage outlines: off in Graphics mode (bevels and contact shadows carry the shape instead) ----------
rep("  stageGroup.add(new THREE.Mesh(mergeGeos(lines), lineMat));", "  if (!HI) stageGroup.add(new THREE.Mesh(mergeGeos(lines), lineMat));")
rep("  stageGroup.add(new THREE.Mesh(mergeGeos(hulls), outlineMat));\n}", "  if (!HI) stageGroup.add(new THREE.Mesh(mergeGeos(hulls), outlineMat));\n}")
rep("      const hm = new THREE.Mesh(o, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hm.userData.own = true; stageGroup.add(hm);",
    "      const hm = new THREE.Mesh(o, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hm.userData.own = true; hm.visible = !HI; stageGroup.add(hm);")
open(P, 'w').write(s); print('ok')
