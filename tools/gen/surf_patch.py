# Surfaces with depth: every stage surface is painted as color + height + gloss together (gen/surfaces.js), so Graphics mode
# gets real relief (beveled tiles in grout, cracks, veining, brick and leaf relief) and gloss that varies across a surface.
p = '/home/claude/paint-the-canvas.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:110]); s = s.replace(old, new)
def cut(a, b):  # remove from the start of a up to (not including) b
    global s
    i = s.index(a); j = s.index(b, i); s = s[:i] + s[j:]

# the old theme-only textures go (leafAt, leafTex and barkTex stay: the garden's canopies and trunks use them)
cut('// crypt: worn cobbles and dark brick\n', '// night garden: leafy groundcover and clipped hedge, drawn leaf by leaf')
rep("// night garden: leafy groundcover and clipped hedge, drawn leaf by leaf (their normal maps give every leaf an edge)\n", "")
cut('const mossTex = makeTex(512,', '// leaves for canopies and bushes')
cut('// Palette Island: wind-rippled sand flecked with shell, and sun-bleached boardwalk planks\n', 'const THEMES = [')
rep("const THEMES = [", open(SP + 'gen/surfaces.js').read() + "const THEMES = [")

for tid, a, b, sf in [('crypt', 'cobbleTex', 'brickTex', "['cobble', 'brick']"), ('cathedral', 'marbleTex', 'ashlarTex', "['marble', 'ashlar']"),
                      ('manor', 'parquetTex', 'damaskTex', "['parquet', 'damask']"), ('garden', 'mossTex', 'hedgeTex', "['moss', 'hedge']"),
                      ('island', 'sandTex', 'plankTex', "['sand', 'plank']"), ('blank', 'blankTex', 'blankSideTex', "['blank', 'blankSide']")]:
    rep("floor: () => %s, side: () => %s," % (a, b), "sf: %s," % sf)

# materials: painted surfaces bring their own normal and roughness maps; the studio's plain textures still derive theirs
rep("""  const fl = T.floor(), sd = T.side(), lighten = (c, k) => new THREE.Color(c).multiplyScalar(k).getHex();
  // Graphics mode: each theme's surfaces get relief from their own textures and their own sheen (polished marble, waxed boards, rough moss)
  const nk = T.nrm || [0.7, 0.8], rk = T.rough || [0.78, 0.82];
  const fp = HI ? { normalMap: normalFrom(fl, 1.3), normalScale: new THREE.Vector2(nk[0], nk[0]), roughness: rk[0] } : null, sp = HI ? { normalMap: normalFrom(sd, 1.3), normalScale: new THREE.Vector2(nk[1], nk[1]), roughness: rk[1] } : null;""",
"""  const SF = T.sf ? [surf(T.sf[0]), surf(T.sf[1])] : null, fl = SF ? SF[0].map : T.floor(), sd = SF ? SF[1].map : T.side(), lighten = (c, k) => new THREE.Color(c).multiplyScalar(k).getHex();
  // Graphics mode: relief and gloss come painted with each surface (polished marble, waxed boards, leafy moss); nrm and rough scale them
  const nk = T.nrm || (SF ? [1, 1] : [0.7, 0.8]), rk = T.rough || (SF ? [1, 1] : [0.78, 0.82]);
  const pb = (sv, tex, n, r) => !HI ? null : sv && sv.normalMap ? { normalMap: sv.normalMap, normalScale: new THREE.Vector2(n, n), roughnessMap: sv.roughnessMap, roughness: r } : { normalMap: normalFrom(tex, 1.3), normalScale: new THREE.Vector2(n, n), roughness: r };
  const fp = pb(SF && SF[0], fl, nk[0], rk[0]), sp = pb(SF && SF[1], sd, nk[1], rk[1]);""")
# the island and blank stages had hand-set relief and gloss for their old flat textures: the painted ones carry their own now
rep("trim: { c: 0x8C6A48, m: 0, r: 0.62 }, nrm: [0.7, 1.0], rough: [0.92, 0.8], cloud: 0xFFFFFF }", "trim: { c: 0x8C6A48, m: 0, r: 0.62 }, cloud: 0xFFFFFF }")
rep("trim: { c: 0xF2F2F0, m: 0, r: 0.5 }, nrm: [0.25, 0.4], rough: [0.6, 0.6], cloud: 0xF7F8FA }", "trim: { c: 0xF2F2F0, m: 0, r: 0.5 }, cloud: 0xF7F8FA }")
rep("lamps: { post: 0.3, wall: 0.45, up: 0.25 }, pond: true, nrm: [1.0, 1.1], rough: [0.8, 0.75], lk:", "lamps: { post: 0.3, wall: 0.45, up: 0.25 }, pond: true, lk:")

# macro variation: a slow world-space mottling of tone (and a little of gloss), so big floors never read as a repeating tile
rep("const aoU = { uAOMap: { value: aoTex }, uLitMap: { value: litTex }, uAORect: { value: new THREE.Vector4(-30, -30, 1 / 60, 0) } };",
    "const aoU = { uAOMap: { value: aoTex }, uLitMap: { value: litTex }, uAORect: { value: new THREE.Vector4(-30, -30, 1 / 60, 0) }, uMacro: { value: 0.12 } };")
rep("const AO_GLSL = `uniform sampler2D uAOMap, uLitMap; uniform vec4 uAORect;",
    "const AO_GLSL = `uniform sampler2D uAOMap, uLitMap; uniform vec4 uAORect; uniform float uMacro;\n"
    "float vnz(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); float a = fract(sin(dot(i, vec2(127.1, 311.7))) * 43758.55), b = fract(sin(dot(i + vec2(1.0, 0.0), vec2(127.1, 311.7))) * 43758.55), c = fract(sin(dot(i + vec2(0.0, 1.0), vec2(127.1, 311.7))) * 43758.55), d = fract(sin(dot(i + vec2(1.0, 1.0), vec2(127.1, 311.7))) * 43758.55); return mix(mix(a, b, f.x), mix(c, d, f.x), f.y); }\n"
    "float macroN(vec3 w){ return vnz(w.xz * 0.11 + w.y * 0.07) * 0.65 + vnz(w.xz * 0.37 - w.y * 0.21 + 7.3) * 0.35; }")
rep("sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect;",
    "sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect; sh.uniforms.uMacro = aoU.uMacro;", 2)
rep(".replace('#include <aomap_fragment>', '#include <aomap_fragment>\\n{ float sao",
    ".replace('#include <color_fragment>', '#include <color_fragment>\\n{ float mz = macroN(vAOw) - 0.5; diffuseColor.rgb *= 1.0 + uMacro * mz * 1.6; }').replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\\nroughnessFactor = clamp(roughnessFactor * (1.0 + uMacro * (macroN(vAOw.zyx + 3.1) - 0.5) * 2.2), 0.03, 1.0);').replace('#include <aomap_fragment>', '#include <aomap_fragment>\\n{ float sao")
open(p, 'w').write(s)
print('ok', len(s))
