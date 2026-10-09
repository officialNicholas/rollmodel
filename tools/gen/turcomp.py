import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'hi', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=100, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer; window.__noLoop = true; T.setStage('island'); T.start(); for (let i = 0; i < 60; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame();
          const keys0 = new Set(R.info.programs.map(p => p.cacheKey)); T.startTurret(T.P); for (let i = 0; i < 80; i++) { T.step(0.016); T.visuals(0.016, 0.016); if (i % 4 == 0) T.renderFrame(); }
          return R.info.programs.filter(p => !keys0.has(p.cacheKey)).map(p => ({ name: p.name, key: String(p.cacheKey).slice(0, 400) })); }""")
        for x in r: print(json.dumps(x)[:700]); print()
        await b.close()
asyncio.run(main())
