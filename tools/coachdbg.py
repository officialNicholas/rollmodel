import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'rest' && n++ < 30) __T.tutNext(); })(); 0")
        await wait("!document.getElementById('tutGo').hidden", 60000)
        m = "(() => { const c = document.querySelector('.coachpop'), bb = c.querySelector('b'), r = e => { const q = e.getBoundingClientRect(); return [Math.round(q.left), Math.round(q.top), Math.round(q.width), Math.round(q.height)]; }, cs = getComputedStyle(c), bs = getComputedStyle(bb); return { cls: c.className, c: r(c), b: r(bb), w: cs.width, h: cs.height, tr: cs.transform, btr: bs.transform, bsc: bs.scale, banim: bs.animationName, bgs: bs.backgroundSize, ar: cs.aspectRatio, card: document.getElementById('tutGo').className }; })()"
        for t in (300, 1200, 3000):
            await pg.wait_for_timeout(t); print(t, await pg.evaluate(m))
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(800); print('at shot', await pg.evaluate(m)); await pg.screenshot(path=WS + '/ui/cdbg_land_card.png')
        print('errors', errs); await b.close()
asyncio.run(main())
