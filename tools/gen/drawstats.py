import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for GFX in ['hi', 'perf']:
            ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
            await ctx.add_init_script("localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} }));")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            for th in ['garden', 'island', 'studio']:
                r = await pg.evaluate("""(th) => { const T = __T; window.__noLoop = true; if (th === 'studio') T.loadStd(); else T.genWorld(4242, { themes: [th] }); T.mapUsed = false; T.start();
                  for (let i = 0; i < 60; i++) T.step(0.016); for (let i = 0; i < 10; i++) T.visuals(0.016, 0.016);
                  const R = T.renderer; R.info.autoReset = false; R.info.reset(); const t0 = performance.now(); T.renderFrame(); const ms = performance.now() - t0;
                  const i = R.info; const o = { calls: i.render.calls, tris: i.render.triangles, programs: i.programs.length, geos: i.memory.geometries, tex: i.memory.textures, ms: Math.round(ms) }; R.info.autoReset = true; return o; }""", th)
                print(GFX, th, r)
                await pg.evaluate("(() => { __T.state = 'menu'; __T.showMenu(); })()")
            print(errs[:2]); await ctx.close()
        await b.close()
asyncio.run(main())
