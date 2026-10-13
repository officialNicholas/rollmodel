import asyncio, os, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 3, tut: { ph: 'vote' }, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000, polling=100)
        await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0"); await pg.wait_for_timeout(1500)
        await ev("__T.openLook()"); await pg.wait_for_timeout(2500)
        S = "__T.ev(`[lookOpen, tutPh(), tutTip && tutTip.key, tutGestEl.dataset.g, tutGestEl.hidden, tutGestEl.style.left, !!tutGestEl.parentNode, keysUI, document.querySelector('.modal:not([hidden])') && document.querySelector('.modal:not([hidden])').id, booted, bootHold, menuPage, state]`)"
        print('before', await ev(S))
        print('show', await ev("__T.ev(`tutBrowseAt = performance.now(); tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); [tutGestEl.dataset.g, tutGestEl.hidden]`)"))
        for i in range(4): await pg.wait_for_timeout(150); print('after', await ev(S))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
