import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':360,'height':720}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000)
        await pg.wait_for_timeout(1500)
        await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        await pg.fill('#nameInput', 'Dusk'); await pg.tap('#nameOk')
        await pg.wait_for_function("__T.state === 'play'", timeout=10000)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 6; i++) __T.addSplat(P.x + (i % 3 - 1) * 3, P.y, P.z + (i / 3 | 0) * 3 - 1.5, 0, 2.6, __T.clock, false, true, 0); __T.flushTrail(); __T.matchLeft = 0.2; })()")
        for i in range(12):
            r = await pg.evaluate("[__T.state, +__T.matchLeft.toFixed(2), +__T.teamCov(0).toFixed(2), +__T.teamCov(1).toFixed(2), __T.mode, __T.runT.toFixed(2), __T.clock.toFixed(2), __T.P.st, __T.H.st]")
            print(r)
            await pg.wait_for_timeout(1000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
