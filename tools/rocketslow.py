"""v195: grabbing the lesson's orb (the rocket) brings no slow motion."""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'orb' && n++ < 20) __T.tutNext(); })(); 0")
        await wait("__T.orb.on", 60000); await wait("__T.P.st === 'play'", 60000)
        for i in range(60):
            if await pg.evaluate("!!__T.P.rocket"): break
            await pg.evaluate("(() => { const P = __T.P, o = __T.orb; P.x = o.x; P.z = o.z; })(); 0"); await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(600)
        print('after grab', await pg.evaluate("[!!__T.P.rocket, __T.tut.hadRocket, __T.tut.slowK, __T.tutTip && __T.tutTip.key, document.getElementById('tutSlow').className]"))
        print('errors', errs); await b.close()
asyncio.run(main())
