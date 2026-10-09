# CPU cost of a Graphics mode frame (tiny viewport, so the software GPU's share is small): step + visuals + render, ms per frame,
# plus draw calls, triangles and garbage per frame. python3 gen/cpubench.py page1 page2 ...
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--js-flags=--expose-gc'])
        for page in sys.argv[1:]:
            for theme in ['manor', 'cathedral']:
                ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1, has_touch=True, is_mobile=True)
                await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
                await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
                pg = await ctx.new_page(); await pg.goto(SP + page + '.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
                r = await pg.evaluate("""(theme) => { const T = __T, R = T.renderer; window.__noLoop = true; T.genWorld(77, { themes: [theme] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
                  const gl = R.getContext(), px = new Uint8Array(4), sync = () => { R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
                  const fr = () => { T.step(0.008); T.step(0.008); T.visuals(0.016, 0.016); T.flushTrail(); T.renderFrame(); };
                  for (let i = 0; i < 40; i++) fr(); sync(); R.info.autoReset = false; R.info.reset();
                  const m0 = performance.memory ? performance.memory.usedJSHeapSize : 0, N = 50; let tr = 0;
                  const t0 = performance.now(); for (let i = 0; i < N; i++) { T.steerIn = Math.sin(i / 30) * 0.8; const a = performance.now(); T.step(0.008); T.step(0.008); T.visuals(0.016, 0.016); T.flushTrail(); const b = performance.now(); T.renderFrame(); tr += performance.now() - b; } sync();
                  const ms = (performance.now() - t0) / N;
                  return { ms: +ms.toFixed(2), renderJs: +(tr / N).toFixed(2), calls: R.info.render.calls / N | 0, tris: R.info.render.triangles / N | 0, programs: R.info.programs.length }; }""", theme)
                print(page, theme, json.dumps(r))
                await ctx.close()
        await b.close()
asyncio.run(main())
