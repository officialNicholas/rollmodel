import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Juliana', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(200); print(await pg.evaluate("(() => { __T.LH.wearing.head = 'halo'; return JSON.stringify(__T.LH.wearing); })()")); await pg.wait_for_timeout(1300); await pg.screenshot(path=f'{WS}/ui/vshalo_{TAG}.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 520})
        print(TAG, 'errors', errs[:3]); await b.close()
asyncio.run(main())
