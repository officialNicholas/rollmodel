"""v316: the Sunken Keep's look. Brighter in the shadows, underwater light glistening over the floor, and the slime purple.

- Brighter in the shadows: the light from below (the hemisphere's ground colour) is a lighter blue and a little stronger, the picture's
  contrast is eased (1.1 to 1.05) and its blacks lifted a touch toward blue, and the vignette is lighter (0.36 to 0.3). The lit parts
  stay much as they were.
- Light on the floor: the faint web of caustics becomes the light you see on a sea floor. A web of bright, wavy lines with brighter
  knots where they meet is drawn once (a tiling map, made the first time the keep is built, not at launch) and slid over itself two
  ways at once, so where the two meet the light gathers into little blotches that wander and glisten. Broad patches of it are brighter
  and drift slowly (the light coming down in beams), and its edges split a little into colour. It lies over the floor's ring and fades
  out a little way up the wall and into the distance. On lower graphics settings it's the same without the colour split.
- The slime is purple: the pool, the spout, the sheets over the wall top, the drips, the puddles, the glow and the light they throw,
  the pit under the pool, the drops when something falls in, and the boss's own slime (the line where it comes out of the pool and the
  slime it throws off). A vivid violet, a little brighter than the green was, so it stands apart from the boss's pink.
  (The drops' colour comes from the theme now, `slimeC`; the sewer's slime stays green.)
- Choose Event's Season Conquest card has a new picture: the keep as it is now, purple, with the boss over the pool and you in front."""

import base64, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v309_conquest_tex import TEX
# Choose Event's card: a new picture of the keep, purple, the boss over the pool (tools/v316_conquest_card.webp, 720 x 495)
CARD = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v316_conquest_card.webp'), 'rb').read()).decode()

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CAUSTIC = r"""// (v316) caustics: the light on a sea floor. A web of bright wavy lines with brighter knots where they meet (each pixel's nearest
// two and three points of a jittered 6 x 6 grid, warped by whole waves so it still tiles), made the first time the keep is built
let CONQ_CAUSTIC = null;
function conqCausticTex() {
  if (CONQ_CAUSTIC) return CONQ_CAUSTIC;
  const S = 256, N = 6, W = 6.2832, cv = document.createElement('canvas'); cv.width = cv.height = S;
  const g = cv.getContext('2d'), im = g.createImageData(S, S), D = im.data, R = rng(3073), pts = [];
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) pts.push((i + 0.15 + R() * 0.7) / N, (j + 0.15 + R() * 0.7) / N);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const u = x / S, v = y / S, wu = u + 0.03 * Math.sin(W * (2 * v + 0.3)) + 0.016 * Math.sin(W * (3 * v + 5 * u)), wv = v + 0.03 * Math.sin(W * (2 * u + 0.7)) + 0.016 * Math.sin(W * (4 * u - 3 * v));
    const cx = Math.floor(wu * N), cy = Math.floor(wv * N); let f1 = 9, f2 = 9, f3 = 9;
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
      const ii = cx + di, jj = cy + dj, iw = ((ii % N) + N) % N, jw = ((jj % N) + N) % N, k = (jw * N + iw) * 2, d = Math.hypot(wu - pts[k] - (ii - iw) / N, wv - pts[k + 1] - (jj - jw) / N);
      if (d < f1) { f3 = f2; f2 = f1; f1 = d; } else if (d < f2) { f3 = f2; f2 = d; } else if (d < f3) f3 = d;
    }
    const e = (f2 - f1) * N, e3 = (f3 - f1) * N, c = Math.min(1, Math.exp(-e * e / 0.03) * 0.8 + Math.exp(-e3 * e3 / 0.05) * 0.5 + 0.02), o = (y * S + x) * 4;
    D[o] = D[o + 1] = D[o + 2] = c * 255; D[o + 3] = 255;
  }
  g.putImageData(im, 0, 0);
  const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy()); return (CONQ_CAUSTIC = t);
}
// the light on the floor: the web slid over itself two ways (where both are bright, the light gathers into blotches that wander and
// glisten), brighter in broad patches drifting slowly (the beams), its edges split a little into colour (not on lower settings), fading
// up the wall and into the distance
const conqCausticMat = () => new THREE.ShaderMaterial({ uniforms: { uTime: { value: 0 }, uMap: { value: conqCausticTex() }, uK: { value: HI ? 0.36 : 0.3 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  defines: HI ? { CQ_RGB: 1 } : {},
  vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `uniform float uTime, uK; uniform sampler2D uMap; varying vec3 vW;
    float cH(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float cN(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(cH(i), cH(i + vec2(1.0, 0.0)), f.x), mix(cH(i + vec2(0.0, 1.0)), cH(i + vec2(1.0, 1.0)), f.x), f.y); }
    void main(){ vec2 p = vW.xz * 0.075 + vec2(0.0, vW.y * 0.06), q1 = p + vec2(uTime * 0.019, uTime * 0.011), q2 = p * 1.31 + vec2(-uTime * 0.014, uTime * 0.021) + 0.37;
      #ifdef CQ_RGB
      vec2 o = vec2(0.0016, 0.001);
      vec3 a = vec3(texture2D(uMap, q1 + o).r, texture2D(uMap, q1).r, texture2D(uMap, q1 - o).r), b = vec3(texture2D(uMap, q2 + o.yx).r, texture2D(uMap, q2).r, texture2D(uMap, q2 - o.yx).r);
      #else
      vec3 a = vec3(texture2D(uMap, q1).r), b = vec3(texture2D(uMap, q2).r);
      #endif
      vec3 c = min(a, b) * 1.6 + (a + b) * 0.12;
      float beam = smoothstep(0.2, 0.85, cN(vW.xz * 0.11 + vec2(uTime * 0.03, -uTime * 0.02))), fade = (1.0 - smoothstep(15.0, 30.0, distance(cameraPosition, vW))) * (1.0 - smoothstep(0.25, 2.6, vW.y));
      gl_FragColor = vec4(vec3(0.6, 0.92, 1.0) * c * uK * (0.45 + 0.85 * beam) * fade, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>"""


def apply(s):
    # 1. brighter in the shadows (the theme's light from below, the grade), and the slime's colour for its drops
    s = rep(s, "hemi: [0x9CB0D8, 0x141E36], sunPos: [3, 30, 7],\n    kit: {}, fill: 'drum', pot: 'barrel', enclosed: true, slime: true,",
               "hemi: [0x9CB0D8, 0x2A3C62], sunPos: [3, 30, 7], /* (v316: lighter from below) */\n    kit: {}, fill: 'drum', pot: 'barrel', enclosed: true, slime: true, slimeC: 0xB25CFF,")
    s = rep(s, "base: { hemiI: 0.62, key: 0xC8DCF4, keyI: 0.46 }", "base: { hemiI: 0.72, key: 0xC8DCF4, keyI: 0.46 }")
    s = rep(s, "grade: { sat: 1.24, con: 1.1, vig: 0.36, bloom: 1.1, expo: 1.1, tint: [1.03, 0.99, 1.0] }, jglow: 0.7,",
               "grade: { sat: 1.24, con: 1.05, vig: 0.3, bloom: 1.1, expo: 1.1, tint: [1.03, 0.99, 1.0], lift: [0.012, 0.02, 0.03] }, jglow: 0.7, /* (v316: softer contrast, lifted blacks, lighter vignette) */")
    # the drops when something falls into slime: the theme's slime colour (the keep's purple; the sewer's green as before)
    s = rep(s, "let coneSndT = 0, coneDrop = null;",
               "let coneSndT = 0, coneDrop = null;\nconst SLIME_DROP = {}, slimeDrop = () => { const c = (TH && TH.slimeC) || 0x9CFF4A; return SLIME_DROP[c] || (SLIME_DROP[c] = colMat(c)); }; // (v316: by the theme's slime)")
    s = rep(s, "const m = TH && TH.slime ? (coneDrop = coneDrop || colMat(0x9CFF4A)) : (waterDrop = waterDrop || colMat(0xEAF8FF));",
               "const m = TH && TH.slime ? slimeDrop() : (waterDrop = waterDrop || colMat(0xEAF8FF));")
    s = rep(s, "const dropM = TH.slime ? (coneDrop = coneDrop || colMat(0x9CFF4A)) : waterDrop;", "const dropM = TH.slime ? slimeDrop() : waterDrop;")
    # 2. the light on the floor
    a = s.index("// caustics: a web of bright ripples (two copies of it drift over each other on the floor and the walls)\nconst CONQ_CAUSTIC = makeTex(256,")
    b = s.index("      #include <tonemapping_fragment>", a)
    s = s[:a] + CAUSTIC + "\n" + s[b + len("      #include <tonemapping_fragment>\n      #include <colorspace_fragment>"):]
    assert s.count("conqCausticTex()") == 2 and s.count("const conqCausticMat") == 1
    # 3. the slime: purple. Its look (deep, body, inner glow; the highlights and the rim lean violet)
    s = rep(s, "uDeep: { value: new THREE.Color(0x03200A) }, uBody: { value: new THREE.Color(0x167A10) }, uGlow: { value: new THREE.Color(0x0A4005) } };",
               "uDeep: { value: new THREE.Color(0x1E0838) }, uBody: { value: new THREE.Color(0x9B3CFF) }, uGlow: { value: new THREE.Color(0x5A18B0) } }; // (v316: purple)")
    s = rep(s, "col += vec3(0.92, 1.0, 0.9) * s1 * 3.4 + vec3(1.0, 0.8, 0.5) * s2 * 1.0 + vec3(0.8, 0.98, 0.9) * s3 * 1.4 + vec3(0.1, 0.4, 0.13) * fr * (0.35 + 0.65 * max(N.y, 0.0));",
               "col += vec3(0.97, 0.92, 1.0) * s1 * 3.4 + vec3(1.0, 0.8, 0.5) * s2 * 1.0 + vec3(0.9, 0.82, 1.0) * s3 * 1.4 + vec3(0.38, 0.14, 0.58) * fr * (0.35 + 0.65 * max(N.y, 0.0));")
    # its glow and the light it throws, in the pool and where it hangs over the wall; the pit under the pool
    s = rep(s, "K.glow(0, 0.35, 0, 2.2, 0x3C9A20); K.glow(0, 1.3, 0, 1.0, 0x4CB028);\n      K.light(0, 0.3, 0, 7.5, 0x7CE83A, 1.5);",
               "K.glow(0, 0.35, 0, 2.2, 0x7A30D8); K.glow(0, 1.3, 0, 1.0, 0x9A48F0);\n      K.light(0, 0.3, 0, 7.5, 0xB46CFF, 1.5);")
    s = rep(s, "K.glow(lip.x + nx * 0.9, 0.3, lip.z + nz * 0.9, 1.4, 0x3C9A20); K.light(lip.x + nx * 0.9, 0.3, lip.z + nz * 0.9, 5.0, 0x7CE83A, 1.25);",
               "K.glow(lip.x + nx * 0.9, 0.3, lip.z + nz * 0.9, 1.4, 0x7A30D8); K.light(lip.x + nx * 0.9, 0.3, lip.z + nz * 0.9, 5.0, 0xB46CFF, 1.25);")
    s = rep(s, "M.void = new THREE.MeshBasicMaterial({ color: 0x03100A });", "M.void = new THREE.MeshBasicMaterial({ color: 0x0E0420 });")
    # the boss's slime: the line where it comes out of the pool, and the slime it throws off
    s = rep(s, "C_SLIME = new THREE.Color(0.35, 1.0, 0.3)", "C_SLIME = new THREE.Color(0.74, 0.38, 1.0)")
    s = rep(s, "totalEmissiveRadiance = mix(totalEmissiveRadiance, vec3(0.35, 1.0, 0.25), sl * 0.85);", "totalEmissiveRadiance = mix(totalEmissiveRadiance, vec3(0.7, 0.32, 1.0), sl * 0.85);")
    # 4. the card's picture: the keep as it is now, with the boss
    s = rep(s, TEX['card'], CARD)
    return s
