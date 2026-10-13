"""v250 locker: Ol' Bloop's 'Take a look around' with a finger swiping across the character (it shows you can turn yourself round);
it goes once you've had a turn. Shots at a couple of moments; portrait and landscape."""
import asyncio, os, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; PAGE = os.environ.get('PAGE', 'pc_h.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h in [(390, 780), (780, 390)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{}, drops: 0, runs: 3, tut: { ph: 'vote' }, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
            await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
            await ev("__T.openLook()"); await pg.wait_for_timeout(3500)
            await ev("__T.ev(\"tutBrowseAt = performance.now(); tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true)\")"); await pg.wait_for_timeout(500)
            g = "(() => { const g = document.querySelector('.tutgest'); return g ? [g.dataset.g, g.hidden, g.style.left, g.style.top] : null; })()"
            print(w, h, 'gesture', await ev(g)); await pg.screenshot(path=f'{WS}/ui/spin250_{w}x{h}_a.png'); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/spin250_{w}x{h}_b.png')
            await pg.wait_for_timeout(2500); print('  after 3 s of the idle turning on its own', await ev(g))
            gx = await ev("parseFloat(document.querySelector('.tutgest').style.left) || innerWidth / 2"); gy = await ev("parseFloat(document.querySelector('.tutgest').style.top) || innerHeight / 2")
            await pg.mouse.move(gx - 40, gy); await pg.mouse.down(); await pg.mouse.move(gx + 60, gy, steps=8); await pg.mouse.up(); await pg.wait_for_timeout(300)
            print('  after a drag', await ev(g), 'swiped', await ev("__T.ev('lookSwiped')"))
            print('  errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
