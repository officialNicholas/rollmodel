# draw calls and triangles per frame (all passes) per theme, Graphics and Performance mode: python3 gen/perfstats.py [page]
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for gfx in ['hi', 'perf']:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(500)
            r = await pg.evaluate("""() => { const T = __T, R = T.renderer; window.__noLoop = true; R.info.autoReset = false; const out = {};
              for (const th of ['garden', 'cathedral', 'crypt', 'manor', 'island', 'blank']) { T.genWorld(77, { themes: [th] }); T.mapUsed = false; T.start(); for (let i = 0; i < 90; i++) { T.step(0.016); if (i % 3 === 2) T.visuals(0.048, 0.048); } T.renderFrame(); T.renderFrame();
                R.info.reset(); T.renderFrame(); const gl = R.getContext(), px = new Uint8Array(4); R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
                const t0 = performance.now(); for (let k = 0; k < 3; k++) T.renderFrame(); R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
                out[th] = { calls: R.info.render.calls, tris: R.info.render.triangles, ms: Math.round((performance.now() - t0) / 3), progs: R.info.programs.length, geos: R.info.memory.geometries, tex: R.info.memory.textures }; T.state = 'menu'; T.showMenu(); }
              return out; }""")
            print(gfx, json.dumps(r)); await ctx.close()
        await b.close()
asyncio.run(main())
