"""Render the game's own orb (its shader, outline hull, glow and sparks) for the Deep Pockets picture. usage: orbshot257.py PAGE
Writes core_<t>_b/w.png (orb on black and on white: exact alpha) and glow_<t>.png (the additive glow and sparks on black)."""
import asyncio, sys, json, base64
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/art/orb257'
PAGE = sys.argv[1]
JS = r"""((T) => {
  const W = 512, E = 0.95, cv = document.createElement('canvas'); cv.width = cv.height = W;
  const R = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: true, preserveDrawingBuffer: true });
  R.outputColorSpace = THREE.SRGBColorSpace; R.toneMapping = renderer.toneMapping; R.toneMappingExposure = renderer.toneMappingExposure; R.setPixelRatio(1); R.setSize(W, W, false);
  const mk = () => { const s = new THREE.Scene(); return s; }, coreS = mk(), glowS = mk();
  const mat = new THREE.ShaderMaterial({ uniforms: { uTime: { value: T } }, vertexShader: ORB_VS, fragmentShader: ORB_FS });
  const core = new THREE.Mesh(new THREE.SphereGeometry(ORB_R, 96, 64), mat); core.rotation.y = T * 1.4; core.rotation.x = Math.sin(T * 0.7) * 0.4; coreS.add(core);
  const hull = new THREE.Mesh(new THREE.SphereGeometry(ORB_R, 96, 64), new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hull.scale.setScalar(1.1); coreS.add(hull);
  const col = new THREE.Color().setHSL((T * 0.2) % 1, 0.9, 0.62, THREE.SRGBColorSpace);
  const halo = glowSprite(1.55); halo.material = halo.material.clone(); halo.material.color.copy(col); halo.material.opacity = 0.8; glowS.add(halo);
  for (let i = 0; i < 4; i++) { const sp = glowSprite(0.2); sp.material = sp.material.clone(); const a = T * 2.2 + i / 4 * 6.283 + 0.6, r = 0.66; sp.position.set(Math.cos(a) * r, Math.sin(a * 1.5 + i) * 0.3 + 0.12, Math.sin(a) * r * 0.2 + 0.5); sp.material.color.setHSL(((T * 0.2) + i / 6) % 1, 0.9, 0.7, THREE.SRGBColorSpace); glowS.add(sp); }
  const cam = new THREE.OrthographicCamera(-E, E, E, -E, 0.1, 20); cam.position.set(0, 0.55, 3); cam.lookAt(0, 0, 0);
  const out = {};
  for (const [k, c] of [['b', 0x000000], ['w', 0xffffff]]) { R.setClearColor(c, 1); R.render(coreS, cam); out[k] = cv.toDataURL('image/png'); }
  R.setClearColor(0x000000, 1); R.render(glowS, cam); out.g = cv.toDataURL('image/png');
  R.dispose(); return JSON.stringify(out);
})"""
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        ctx, pg, errs = await boot(b, PAGE, dict(SAVE), vp=(390, 780), dpr=1)
        for t in [0.5, 1.5, 2.5, 3.5, 4.5]:
            r = json.loads(await pg.evaluate("__T.ev(" + json.dumps(JS + '(' + str(t) + ')') + ")"))
            for k, n in (('b', 'core_%s_b' % t), ('w', 'core_%s_w' % t), ('g', 'glow_%s' % t)):
                open(f'{OUT}/{n}.png', 'wb').write(base64.b64decode(r[k].split(',', 1)[1]))
            print('t', t, flush=True)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
