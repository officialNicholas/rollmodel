"""A match to its end, then the results' Menu button back to the home screen: the power bar, the dabs and the menu button come back."""
import asyncio
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(1500)
        await pg.evaluate("__T.start()")
        for i in range(45):
            st = await pg.evaluate("[__T.state, document.getElementById('menu').dataset.page, !document.getElementById('vsx').hidden]")
            if st[0] == 'play': break
            if i % 5 == 0: print('waiting', st, flush=True)
            await pg.wait_for_timeout(2000)
        print('state', st, flush=True); await pg.wait_for_timeout(1500)
        await pg.evaluate("__T.matchLeft = 0.3")
        for i in range(45):
            st = await pg.evaluate("[__T.state, !!__T.vic, __T.matchLeft]")
            if st[1] or st[0] == 'dead': break
            if i % 5 == 0: print('ending', st, flush=True)
            await pg.wait_for_timeout(2000)
        print('ended', st, flush=True)
        for i in range(60):
            st = await pg.evaluate("[__T.state, !!__T.vic, !document.getElementById('end').hidden]")
            if st[2]: break
            await pg.evaluate("(() => { try { document.getElementById('vic').click(); } catch (e) {} const t = document.querySelector('#vic, .vic'); if (t) t.dispatchEvent(new PointerEvent('pointerup', { bubbles: true })); })()")
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(1500)
        print('end screen', await pg.evaluate("[__T.state, !document.getElementById('end').hidden]"))
        await pg.evaluate("document.getElementById('menuBtn').click()"); await pg.wait_for_function("__T.state === 'menu'", timeout=60000, polling=300); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f'{OUT}/endmenu.png', timeout=120000)
        print('home again', await pg.evaluate("[__T.state, document.getElementById('pbar').hidden, document.body.classList.contains('homeon'), document.getElementById('menu').dataset.page, document.getElementById('hamBtn').getAttribute('aria-expanded')]"), 'errors', errs[:5])
        await b.close()
asyncio.run(main())
