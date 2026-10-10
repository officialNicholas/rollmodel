"""v190: the lesson's start banner is short, the move tip follows right after, and gesture tips carry the animated finger."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        g = "[document.querySelector('.tutgest') && document.querySelector('.tutgest').dataset.g, document.querySelector('.tutgest') && document.querySelector('.tutgest').hidden, __T.tutTip && __T.tutTip.key]"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("document.getElementById('banner').classList.contains('on') && /Paint it/.test(document.getElementById('bannerBig').textContent)")
        t0 = await pg.evaluate("performance.now()"); print('banner', await pg.evaluate("[document.getElementById('bannerBig').textContent, document.getElementById('banner').className, Math.round(__T.bannerUntil - performance.now())]"))
        await wait("__T.tut && __T.tut.step === 0"); t1 = await pg.evaluate("performance.now()"); print('move tip after banner start (ms)', round(t1 - t0), await pg.evaluate(g))
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(1500); await pg.screenshot(path=S + '/ws/ui/gest_move.png'); await pg.evaluate("__T.renderer.render = () => {}; 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'sling' && n++ < 20) __T.tutNext(); })()"); await pg.wait_for_timeout(800); print('sling', await pg.evaluate(g))
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(1500); await pg.screenshot(path=S + '/ws/ui/gest_sling.png'); await pg.evaluate("__T.renderer.render = () => {}; 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'basin' && n++ < 20) __T.tutNext(); })()"); await pg.wait_for_timeout(800); print('basin', await pg.evaluate(g))
        print('errors', errs); await b.close()
asyncio.run(main())
