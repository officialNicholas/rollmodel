"""v217: Choose Event's more-below hint: the fade and the arrow while the list runs on, gone at the end; portrait with a notch, landscape."""
import asyncio
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, it, ib, tag in [(430, 790, 59, 34, 'p'), (844, 390, 0, 21, 'l')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Glossy', seen:{look:1}, runs: 9, xp: 300, drops: 120, tut: { ph: 'done' } })); } catch (e) {}")
            pg = await ctx.new_page(); cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': it, 'bottom': ib, 'left': 0, 'right': 0}})
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1500)
            st = "[document.getElementById('evGrid').className, document.getElementById('evMore').className, Math.round(document.getElementById('evGrid').scrollTop)]"
            print(tag, 'open', await pg.evaluate(st)); await pg.screenshot(path=f'{OUT}/ev_{tag}_top.png')
            await pg.evaluate("document.getElementById('evMore').click()"); await pg.wait_for_timeout(900); print(tag, 'after tap', await pg.evaluate(st)); await pg.screenshot(path=f'{OUT}/ev_{tag}_mid.png')
            await pg.evaluate("(() => { const g = document.getElementById('evGrid'); g.scrollTop = g.scrollHeight; })()"); await pg.wait_for_timeout(500); print(tag, 'end', await pg.evaluate(st)); await pg.screenshot(path=f'{OUT}/ev_{tag}_end.png')
            print(tag, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
