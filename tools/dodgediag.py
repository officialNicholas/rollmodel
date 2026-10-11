import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'dodge' && n++ < 20) __T.tutNext(); })(); 0")
        for i in range(30):
            print(await pg.evaluate("(() => { const P = __T.P, H = __T.H, t = __T.tut; return [__T.TUT_STEPS[t.step].id, +t.st.toFixed(1), +Math.hypot(H.x - P.x, H.z - P.z).toFixed(1), H.st, H.slam, +H.slamCD.toFixed(2), H.air, +(H.y - P.y).toFixed(2), P.st, P.air, t.sub, +H.paint.toFixed(2)]; })()"))
            await pg.wait_for_timeout(2000)
        print('errors', errs); await b.close()
asyncio.run(main())
