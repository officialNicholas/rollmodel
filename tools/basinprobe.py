"""v194: fling tip a second after the move step; the refill tip waits for an empty tank, then the arrow and a finger point to the nearest basin."""
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
        await pg.evaluate("__T.tutNext(); 0"); await wait("__T.TUT_STEPS[__T.tut.step].id === 'sling'")
        print('sling after free0 (step s)', await pg.evaluate("[__T.TUT_STEPS[__T.tut.step].id, __T.tutTip && __T.tutTip.key]"))
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'basin' && n++ < 20) __T.tutNext(); })(); 0")
        await pg.wait_for_timeout(400); print('basin start', await pg.evaluate("[__T.tutTip && __T.tutTip.key, +__T.P.paint.toFixed(2), document.getElementById('tutArrow').hidden]"))
        await pg.keyboard.down('ArrowLeft'); await wait("__T.tutTip && __T.tutTip.key === 'basin'", 120000); await pg.keyboard.up('ArrowLeft')
        await pg.wait_for_timeout(300)
        print('basin tip', await pg.evaluate("[__T.tutTip.text, +__T.P.paint.toFixed(2), +__T.tut.st.toFixed(1), document.getElementById('tutArrow').hidden, [...document.querySelectorAll('.tuthand')].map(h => h.id + ':' + h.hidden + ':' + h.style.left + ',' + h.style.top)]"))
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(1500); await pg.screenshot(path=S + '/ws/ui/basin_point.png')
        print('errors', errs); await b.close()
asyncio.run(main())
