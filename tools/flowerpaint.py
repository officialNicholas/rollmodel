"""v179: during the lesson's flower step the paint tank never drops below where it was."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=200)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })()")
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'rocketdodge' && n++ < 20) __T.tutNext(); })()"); await pg.wait_for_timeout(300)
        await wait("__T.P.st === 'play'"); await pg.evaluate("__T.P.paint = 0.72; __T.tutNext(); 0")
        await pg.keyboard.down('ArrowLeft'); lo = 9
        for i in range(10):
            v = await pg.evaluate("[__T.TUT_STEPS[__T.tut.step].id, __T.P.st, +__T.P.paint.toFixed(3), __T.gift.on, __T.tutTip && __T.tutTip.key, +__T.tut.st.toFixed(1)]"); print('t', i, v, flush=True)
            if v[0] == 'flower' and v[1] == 'play': lo = min(lo, v[2])
            await pg.wait_for_timeout(700)
        print('lowest paint during flower step', lo)
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(1500); await pg.screenshot(path=S + '/ws/ui/flower_paint.png')
        print('errors', errs); await b.close()
asyncio.run(main())
