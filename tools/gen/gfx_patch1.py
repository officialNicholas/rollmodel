P = '/home/claude/paint-the-canvas.html'
s = open(P).read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:150]); s = s.replace(old, new)

# ---------- renderer per mode ----------
rep("""const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;""",
"""// graphics mode, picked in Settings: Graphics (physically based light from the sky, reflections, glow, soft shadows, more
// polygons) or Performance (the lean toon look, smaller buffers, no post effects). Changing it restarts the game.
const GFX = store.gfx === 'perf' ? 'perf' : 'hi', HI = GFX === 'hi';
const MOBILE = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) || (navigator.maxTouchPoints > 1 && /Macintosh/.test(navigator.userAgent));
const SEG = n => Math.max(6, Math.round(n * (HI ? 1.5 : 0.75))); // how round round things are
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(HI ? 2 : 1.5, window.devicePixelRatio || 1));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;""")
rep("sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0006;", "sun.shadow.mapSize.set(HI ? (MOBILE ? 2048 : 4096) : 1024, HI ? (MOBILE ? 2048 : 4096) : 1024); sun.shadow.bias = -0.0006; sun.shadow.normalBias = HI ? 0.02 : 0;")

# ---------- one material factory ----------
rep("const toon = (c, extra) => new THREE.MeshToonMaterial(Object.assign({ color: c, gradientMap: grad }, extra || {}));",
"""// every surface comes from here: the toon look in Performance mode, physically based in Graphics mode (lit by the sky
// through scene.environment, so it picks up soft ambient light and reflections). pbr: roughness and metalness for that mode
const toon = (c, extra, pbr) => HI ? new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.78, metalness: 0 }, extra || {}, pbr || {})) : new THREE.MeshToonMaterial(Object.assign({ color: c, gradientMap: grad }, extra || {}));""")
rep("const decalOf = tex => new THREE.MeshToonMaterial({ map: tex, gradientMap: grad, color: 0xE0E0E0, transparent: false,",
    "const decalOf = tex => toon(0xE0E0E0, { map: tex, transparent: false,")
open(P, 'w').write(s); print('ok')
