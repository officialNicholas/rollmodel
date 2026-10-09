# three.js r128 -> r186, step one: the same picture on the new engine. Color management off and linear output (so colors
# behave exactly as before), lights scaled by pi for three's lights only (r155 dropped the old pi in the light math), and
# every removed API replaced.
import shutil
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:110]); s = s.replace(old, new)

shutil.copy(SP + '/t186/three.r186.iife.min.js', '/home/claude/three.r186.min.js')
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js">', '<script src="three.r186.min.js">')
rep("<script>\n(() => {\n'use strict';\n", "<script>\n(() => {\n'use strict';\nTHREE.ColorManagement.enabled = false; // colors are authored as-is: the picture handles its own tone and grade\n")
rep("const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });",
    "const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' }); renderer.outputColorSpace = THREE.LinearSRGBColorSpace;")
rep("shadowMap.type = THREE.PCFSoftShadowMap", "shadowMap.type = THREE.PCFShadowMap")

# the old soft-shadow chunk patch has nothing to patch any more (r186 filters its shadow lookups in hardware)
i = s.index('THREE.ShaderChunk.shadowmap_pars_fragment = THREE.ShaderChunk.shadowmap_pars_fragment.replace(')
j = s.index('`);', i) + 3
assert j - i < 3000
s = s[:i] + s[j:].lstrip('\n')

rep("THREE.LuminanceFormat", "THREE.RedFormat")

# lights: three's own lights get pi (the light math lost it in r155); our shaders read the old scale back
rep("const hemi = new THREE.HemisphereLight(NIGHT.sky.getHex(), NIGHT.gnd.getHex(), NIGHT.hemi);",
    "const LIGHT_K = Math.PI; // three.js lights since r155 have no built-in pi; everything of ours below keeps the old scale\nconst hemi = new THREE.HemisphereLight(NIGHT.sky.getHex(), NIGHT.gnd.getHex(), NIGHT.hemi * LIGHT_K);")
rep("const sun = new THREE.DirectionalLight(NIGHT.key.getHex(), NIGHT.keyI);", "const sun = new THREE.DirectionalLight(NIGHT.key.getHex(), NIGHT.keyI * LIGHT_K);")
rep("- 0.08 * rainK) * LK.hemi;", "- 0.08 * rainK) * LK.hemi * LIGHT_K;")
rep("- 0.18 * rainK) * LK.key;", "- 0.18 * rainK) * LK.key * LIGHT_K;")
rep("tcA.copy(hemi.color).multiplyScalar(hemi.intensity).add(envUp); tcB.copy(sun.color).multiplyScalar(sun.intensity * Ly).add(tcA);",
    "tcA.copy(hemi.color).multiplyScalar(hemi.intensity / LIGHT_K).add(envUp); tcB.copy(sun.color).multiplyScalar(sun.intensity / LIGHT_K * Ly).add(tcA);")
rep("U.uSunC.value.copy(sun.color).multiplyScalar(sun.intensity);", "U.uSunC.value.copy(sun.color).multiplyScalar(sun.intensity / LIGHT_K);")
rep("seaU.uSunC.value.copy(sun.color).multiplyScalar(sun.intensity * 1.1);", "seaU.uSunC.value.copy(sun.color).multiplyScalar(sun.intensity / LIGHT_K * 1.1);")
rep("hemi.intensity = Math.max(hi, 0.85); sun.intensity = Math.max(si, 0.95);", "hemi.intensity = Math.max(hi, 0.85 * LIGHT_K); sun.intensity = Math.max(si, 0.95 * LIGHT_K);")

# render targets: multisampling is an option now
rep("postRT = renderer.capabilities.isWebGL2 && THREE.WebGLMultisampleRenderTarget ? new THREE.WebGLMultisampleRenderTarget(w, h) : new THREE.WebGLRenderTarget(w, h);",
    "postRT = new THREE.WebGLRenderTarget(w, h, { samples: 4 });")
rep("const gl2 = renderer.capabilities.isWebGL2, opt =", "const opt =")
rep("const main = gl2 && THREE.WebGLMultisampleRenderTarget ? new THREE.WebGLMultisampleRenderTarget(4, 4, Object.assign({}, opt, { depthBuffer: true })) : new THREE.WebGLRenderTarget(4, 4, Object.assign({}, opt, { depthBuffer: true }));",
    "const main = new THREE.WebGLRenderTarget(4, 4, Object.assign({}, opt, { depthBuffer: true, samples: 4 }));")

# buffer uploads: ranges are added, and three uploads (and merges) every range added since the last upload
i = s.index('function upRange(a, o, c) {'); j = s.index('\n}\n', i) + 3
s = s[:i] + "function upRange(a, o, c) { a.addUpdateRange(o, c); a.needsUpdate = true; }\n" + s[j:]
rep("const mA = pl.im.instanceMatrix; mA.updateRange.offset = 0; mA.updateRange.count = n * 16; mA.needsUpdate = true; if (ca) { const cA = pl.im.instanceColor; cA.updateRange.offset = 0; cA.updateRange.count = n * 3; cA.needsUpdate = true; }",
    "const mA = pl.im.instanceMatrix; mA.clearUpdateRanges(); mA.addUpdateRange(0, n * 16); mA.needsUpdate = true; if (ca) { const cA = pl.im.instanceColor; cA.clearUpdateRanges(); cA.addUpdateRange(0, n * 3); cA.needsUpdate = true; }")

# shader names
rep("  vec4 worldPosition = w; vec3 transformedNormal = normalize(mat3(viewMatrix) * vec3(0.0, 1.0, 0.0));\n  #include <shadowmap_vertex>\n  #ifdef USE_FOG\n  fogDepth = -(viewMatrix * w).z;",
    "  vec4 worldPosition = w, mvPosition = viewMatrix * w; vec3 transformedNormal = normalize(mat3(viewMatrix) * vec3(0.0, 1.0, 0.0));\n  #include <shadowmap_vertex>\n  #ifdef USE_FOG\n  vFogDepth = -mvPosition.z;")
rep("float fogFactor = smoothstep(fogNear, fogFar, fogDepth);", "float fogFactor = smoothstep(fogNear, fogFar, vFogDepth);")
rep(", extensions: { derivatives: true } }", " }")
open(p, 'w').write(s)
print('ok', len(s))
