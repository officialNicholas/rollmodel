# Palette Island: golden late-afternoon light, and sand with wind ripples, fine grain and glints
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

# ---------- the island's light: a lower, warmer sun, a hazy warm horizon, warm bounce off the sand ----------
rep("{ id: 'island', label: 'Palette Island', sf: ['sand', 'plank'], uv: 0.3, ft: 0xF0F0F0, st: 0xC4C4C4, dt: 0x8E8E8E, hor: 0xC4E8F4, sky: [0x2B7FD4, 0x6CB6EE, 0xCDEEFA], low: 0x7CC3DA, hemi: [0xD6ECFF, 0xD9C59C],",
    "{ id: 'island', label: 'Palette Island', sf: ['sand', 'plank'], uv: 0.3, ft: 0xF0F0F0, st: 0xC4C4C4, dt: 0x8E8E8E, hor: 0xEED9BE, sky: [0x3A86D2, 0x88C0EA, 0xF2DFC6], low: 0x7CC3DA, hemi: [0xCFE2FA, 0xE8C088], sunPos: [24, 21, 13], sand: true,")
rep("day: true, sun: 1, sea: true, base: { hemiI: 0.74, key: 0xFFF4DE, keyI: 0.9 }, env: { top: 0x3A6A94, hor: 0x8CB4BE, gnd: 0xC8B28A, sun: 0xFFF4DE, sunK: 1.0 }, lk: { hemi: 0.36, key: 1.18 }, grade: { sat: 1.2, con: 1.05, vig: 0.07, bloom: 0.4, th: 0.86, expo: 1.1, tint: [1.03, 1.01, 0.95] },",
    "day: true, sun: 1, sea: true, base: { hemiI: 0.62, key: 0xFFDDAE, keyI: 1.02 }, env: { top: 0x4A7CAE, hor: 0xE6CBA4, gnd: 0xD6A464, sun: 0xFFE0B2, sunK: 1.1 }, lk: { hemi: 0.34, key: 1.26 }, grade: { sat: 1.24, con: 1.08, vig: 0.1, bloom: 0.5, expo: 1.08, tint: [1.06, 1.0, 0.9] },")

# the sun can sit where a theme wants it (the island's is lower and warmer); the gameplay shade test follows it
rep("const DK = T.dusk; sun.position.fromArray(DK ? DK.sun : [16, 30, 9]);", "const DK = T.dusk; sun.position.fromArray(DK ? DK.sun : T.sunPos || [16, 30, 9]); SHX = sun.position.x / sun.position.y; SHZ = sun.position.z / sun.position.y;")
rep("if (DK) skyU.sunHi.value.fromArray(DK.skySun).normalize(); else skyU.sunHi.value.set(16, 30, 9).normalize();", "if (DK) skyU.sunHi.value.fromArray(DK.skySun).normalize(); else skyU.sunHi.value.fromArray(T.sunPos || [16, 30, 9]).normalize();")
rep("const SHX = 16 / 30, SHZ = 9 / 30;\nfunction inShadow(x, z, y, noDyn) {\n  for (let h = 0.1; y + 0.35 + h < 3.3; h += 0.12) {",
    "let SHX = 16 / 30, SHZ = 9 / 30; // (along the ground per unit up, toward the sun: set with each theme's sun)\nfunction inShadow(x, z, y, noDyn) {\n  for (let h = 0.1; y + 0.35 + h < 3.3; h += 0.12) {")

# ---------- the sand texture: warm and golden, soft drifts, fine close-toned grains (Performance mode gets its ripples painted in) ----------
a = src.index("  sand: () => makeSurf(HI ? 1024 : 512, (c, h, r, S) => {")
b = src.index("  }, 1.7),", a) + len("  }, 1.7),")
SAND = r"""  sand: () => makeSurf(HI ? 1024 : 512, (c, h, r, S) => {
    const R = rng(141), q = S / 512;
    c.fillStyle = '#E8C78B'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.5); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.9); r.fillRect(0, 0, S, S);
    // broad, soft shifts of tone: paler dry drifts, warmer damp patches
    for (let i = 0; i < 24; i++) { const x = R() * S, y = R() * S, rad = S * (0.08 + R() * 0.16), dry = R() < 0.55; wrapAt(S, x, y, rad, (X, Y) => blob(c, X, Y, rad, dry ? 'rgba(252,236,200,0.2)' : 'rgba(204,154,92,0.14)')); }
    // Performance mode paints the wind ripples in (Graphics mode shapes them in its shader, lit by the sun): a soft shade along each lee
    // side, a bright line along each crest
    if (!HI) { const n = 11; for (let i = 0; i < n; i++) { const y0 = (i + 0.5 + (R() - 0.5) * 0.3) * S / n, am = (2 + R() * 3) * q, k = 1 + (R() * 2 | 0), ph = R() * 6.28;
      for (const [col, dy, lw] of [['rgba(176,126,68,0.24)', 3 * q, 5 * q], ['rgba(255,246,218,0.34)', -2 * q, 2.2 * q]]) { c.strokeStyle = col; c.lineWidth = lw; for (const off of [-S, 0, S]) { c.beginPath(); for (let x = 0; x <= S; x += 4) { const y = y0 + off + dy + Math.sin(x / S * 6.2832 * k + ph) * am; x ? c.lineTo(x, y) : c.moveTo(x, y); } c.stroke(); } } } }
    // the grains: tiny and close in tone, a few darker or brighter ones among them, each a small bump in the relief
    const tones = [[[238, 208, 150], 12], [[228, 194, 134], 12], [[244, 220, 168], 8], [[220, 184, 124], 6], [[250, 232, 190], 5], [[208, 170, 112], 3], [[255, 246, 218], 2], [[182, 142, 94], 0.7], [[146, 114, 82], 0.25]];
    const tw = tones.reduce((s, t) => s + t[1], 0), pickTone = () => { let v = R() * tw; for (const t of tones) if ((v -= t[1]) <= 0) return t[0]; return tones[0][0]; };
    const spr = (rad, rgb) => { const n = Math.ceil(rad * 2 + 2), cv = document.createElement('canvas'); cv.width = cv.height = n; const g = cv.getContext('2d'), m = n / 2, gr = g.createRadialGradient(m - rad * 0.3, m - rad * 0.35, rad * 0.1, m, m, rad);
      gr.addColorStop(0, rgbS(Math.min(255, rgb[0] * 1.08 + 10), Math.min(255, rgb[1] * 1.08 + 10), Math.min(255, rgb[2] * 1.08 + 10))); gr.addColorStop(0.65, rgbS(...rgb)); gr.addColorStop(1, rgbS(rgb[0] * 0.9, rgb[1] * 0.88, rgb[2] * 0.85, 0));
      g.fillStyle = gr; g.beginPath(); g.ellipse(m, m, rad, rad * (0.8 + R() * 0.2), R() * 3, 0, 6.2832); g.fill(); return cv; };
    const bump = (rad, top) => { const n = Math.ceil(rad * 2 + 2), cv = document.createElement('canvas'); cv.width = cv.height = n; const g = cv.getContext('2d'), m = n / 2, gr = g.createRadialGradient(m, m, 0, m, m, rad); gr.addColorStop(0, grayA(top, 1)); gr.addColorStop(0.7, grayA(0.5 + (top - 0.5) * 0.5, 0.8)); gr.addColorStop(1, grayA(0.5, 0)); g.fillStyle = gr; g.fillRect(0, 0, n, n); return cv; };
    const SPR = [], BMP = [], sizes = [0.75, 0.95, 1.2, 1.5].map(v => v * q);
    for (let k = 0; k < 48; k++) SPR.push(spr(sizes[k % sizes.length] * (0.85 + R() * 0.3), pickTone()));
    for (const z of sizes) BMP.push(bump(z, 0.66));
    const N = Math.round(64000 * (S / 1024) * (S / 1024)), put2 = (g, im, x, y) => { const w = im.width; g.drawImage(im, x - w / 2, y - w / 2); if (x < w) g.drawImage(im, x + S - w / 2, y - w / 2); else if (x > S - w) g.drawImage(im, x - S - w / 2, y - w / 2); if (y < w) g.drawImage(im, x - w / 2, y + S - w / 2); else if (y > S - w) g.drawImage(im, x - w / 2, y - S - w / 2); };
    for (let i = 0; i < N; i++) { const k = (R() * SPR.length) | 0, x = R() * S, y = R() * S; put2(c, SPR[k], x, y); if (HI && (i & 1)) put2(h, BMP[k % sizes.length], x, y); }
    for (let i = 0; i < 900 * q * q; i++) { const v = R(); c.fillStyle = v < 0.5 ? `rgba(150,112,70,${0.1 + v * 0.18})` : `rgba(255,250,236,${0.14 + v * 0.2})`; c.fillRect(R() * S, R() * S, q, q); }
  }, 1.1),"""
src = src[:a] + SAND + src[b:]

# ---------- Graphics mode: the island's sand shaped and sparkling in its shader ----------
SAND_GLSL = r'''
uniform float uSandT;
// wind ripples: long crests a hand's width apart, meandering a little, steeper on the lee side, forking where two directions meet, calmer
// in patches. x: height (-1..1), yz: its slope along x and z, w: how sharply the crests pass per pixel (to fade them out before they alias)
vec4 sandRipple(vec3 w){
  vec2 p = w.xz;
  vec2 m = vec2(texture2D(uMacroT, p * 0.021).r, texture2D(uMacroT, p * 0.021 + 0.37).r) - 0.5;
  vec2 q = p + m * 3.4;
  const vec2 dA = vec2(0.866, 0.5), dB = vec2(0.643, 0.766); const float kA = 19.6, kB = 21.4;
  float phA = dot(q, dA) * kA, phB = dot(q, dB) * kB + 1.7;
  float mx = smoothstep(0.38, 0.62, texture2D(uMacroT, p * 0.013 + 0.71).r);
  float hA = sin(phA) + 0.3 * sin(2.0 * phA + 1.2), gA = cos(phA) + 0.6 * cos(2.0 * phA + 1.2);
  float hB = sin(phB) + 0.3 * sin(2.0 * phB + 1.2), gB = cos(phB) + 0.6 * cos(2.0 * phB + 1.2);
  float amp = 0.4 + 0.6 * smoothstep(0.22, 0.72, texture2D(uMacroT, p * 0.031 + 0.19).r);
  vec2 g = mix(gA * kA * dA, gB * kB * dB, mx) * amp;
  return vec4(mix(hA, hB, mx) * amp, g, fwidth(phA));
}
float sandHash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
// glints: here and there a grain turned just so catches the sun, a bright point that winks as you move (none in shadow)
float sandGlint(vec3 w, vec3 vV, vec3 vL){
  vec2 c = w.xz * 30.0, id = floor(c), f = fract(c) - 0.5;
  float h1 = sandHash(id); if (h1 > 0.16) return 0.0;
  float h2 = sandHash(id + 7.13), h3 = sandHash(id + 3.71), h4 = sandHash(id + 1.37);
  vec3 fn = normalize(vec3((h2 - 0.5) * 0.85, 1.0, (h3 - 0.5) * 0.85)), fv = normalize((viewMatrix * vec4(fn, 0.0)).xyz);
  float s = pow(max(dot(fv, normalize(vL + vV)), 0.0), 700.0);
  float dotK = 1.0 - smoothstep(0.06, 0.24, length(f - (vec2(h4, h2) - 0.5) * 0.4));
  float small = 1.0 - smoothstep(0.55, 1.1, length(fwidth(c)));
  return s * dotK * small * (0.75 + 0.25 * sin(uSandT * 6.0 + h4 * 40.0));
}
'''
HOOK = r"""
// Graphics mode: the island's sand gets its ripples and glints in its shader (the floor and the tops of the pieces, wherever they face up)
const sandT = { value: 0 };
function sandHook(sh) {
  aoHook(sh); sh.uniforms.uSandT = sandT;
  const L0 = THREE.ShaderChunk.lights_fragment_begin, di = L0.indexOf('directionalLights[ i ]'), re = L0.indexOf('RE_Direct(', di), ec = L0.indexOf(';', re) + 1;
  const Lmod = L0.slice(0, ec) + '\n\t\tif (sandUp > 0.0) reflectedLight.directSpecular += directLight.color * sandGlint(vAOw, geometryViewDir, directLight.direction) * 7.0 * sandUp * sandAA;' + L0.slice(ec);
  sh.fragmentShader = sh.fragmentShader.replace('void main() {', SAND_GLSL_SRC + '\nvoid main() {')
    .replace('#include <color_fragment>', '#include <color_fragment>\nfloat sandUp = smoothstep(0.66, 0.9, vAOn.y); vec4 sandR = sandUp > 0.0 ? sandRipple(vAOw) : vec4(0.0); float sandAA = 1.0 - smoothstep(0.9, 2.4, sandR.w);\ndiffuseColor.rgb *= 1.0 + sandR.x * 0.05 * sandAA * sandUp;')
    .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\nif (sandUp > 0.0) normal = normalize(normal + (viewMatrix * vec4(-sandR.y, 0.0, -sandR.z, 0.0)).xyz * 0.0115 * sandAA * sandUp);')
    .replace('#include <lights_fragment_begin>', Lmod);
}
const sandMat = m => { if (!HI || !m) return m; m.onBeforeCompile = sandHook; m.customProgramCacheKey = () => 'sand'; return m; };
"""
src = src.replace("const aoPatch = m => { if (HI && m && m.isMeshStandardMaterial && m.onBeforeCompile !== aoHook) m.onBeforeCompile = aoHook; return m; };",
    "const aoPatch = m => { if (HI && m && m.isMeshStandardMaterial && m.onBeforeCompile !== aoHook && m.onBeforeCompile !== sandHook) m.onBeforeCompile = aoHook; return m; };\nconst SAND_GLSL_SRC = `" + SAND_GLSL + "`;" + HOOK, 1)
assert 'function sandHook' in src
# the island's floor and tops use it
rep("  if (T.id === 'island') T.mats.sway = new Map(", "  if (T.sand) { sandMat(T.mats.floor); sandMat(T.mats.top); }\n  if (T.id === 'island') T.mats.sway = new Map(")
# the glints wink with time
rep("function updateSway(dt) {\n  SWAY_T.value = clock;", "function updateSway(dt) {\n  SWAY_T.value = clock; sandT.value = clock;")

open(P, 'w').write(src)
print('ok')
