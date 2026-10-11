"""The sly eyes up close in the locker (and the round ones beside them), a few moments apart; the eye style picker with it."""
import asyncio
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=2)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, owned:['sly'], bought:['sly'], tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(2000)
        await pg.evaluate("(() => { try { __T.openLook(); } catch (e) {} })()"); await pg.wait_for_timeout(4000)
        for name in ('round', 'sly'):
            await pg.evaluate(f"__T.myLook.eyes = '{name}'"); await pg.wait_for_timeout(1500)
            for k in range(3):
                await pg.screenshot(path=f'{OUT}/sly_{name}{k}.png', clip={'x': 95, 'y': 120, 'width': 240, 'height': 190}); await pg.wait_for_timeout(700)
        await pg.evaluate("document.getElementById('lc-eyes') && document.getElementById('lc-eyes').click()"); await pg.wait_for_timeout(900)
        await pg.screenshot(path=f'{OUT}/sly_picker.png')
        print('eyes', await pg.evaluate("[__T.myLook.eyes, [...document.querySelectorAll('#eyeStyles button')].map(b => b.dataset.es + (b.classList.contains('locked') ? '(locked)' : ''))]"), 'errors', errs[:4])
        await b.close()
asyncio.run(main())
