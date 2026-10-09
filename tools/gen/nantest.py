# A bad pixel next to a power-up bubble: before, the bloom smears it into a black square; after, it's scrubbed before any blur.
# Also a plain close-up of the bubble (no planted pixel) to check its look is unchanged.
import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
JS = """(plant) => { const T = __T, S = T.scene, cam = T.camera; T.genWorld(77, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
  for (let i = 0; i < 30; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
  let bub = null; S.traverse(o => { if (!bub && o.isMesh && o.material && o.material.type === 'ShaderMaterial' && o.geometry.parameters && o.geometry.parameters.radius === 0.66) bub = o; });
  if (!bub) return 'no bubble';
  const bp = new THREE.Vector3(); bub.getWorldPosition(bp);
  if (plant) { const m = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 6), new THREE.ShaderMaterial({ uniforms: { uZ: { value: 0 } }, vertexShader: 'void main(){ gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }', fragmentShader: 'uniform float uZ; void main(){ gl_FragColor = vec4(vec3(sqrt(-1.0 - uZ)), 1.0); }' }));
    m.position.copy(bp).add(new THREE.Vector3(0.5, 0.35, 0.5)); S.add(m); }
  document.getElementById('banner').style.display = 'none';
  T.visuals(0.016, 0.016); cam.position.copy(bp).add(new THREE.Vector3(2.6, 1.3, 2.6)); cam.lookAt(bp); cam.updateMatrixWorld(); T.renderFrame();
  return [bp.x, bp.y, bp.z]; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name in sys.argv[1:]:
            for plant in (True, False):
                ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
                await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
                await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
                pg = await ctx.new_page(); await pg.goto('file://' + SP + name + '.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
                await pg.evaluate("window.__noLoop = true"); await pg.wait_for_timeout(300)
                r = await pg.evaluate(JS, plant); print(name, plant, r)
                await pg.screenshot(path=f'{SP}st/nan_{name}_{int(plant)}.png')
                await ctx.close()
        await b.close()
asyncio.run(main())
