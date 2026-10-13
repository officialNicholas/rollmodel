import asyncio, sys
from playwright.async_api import async_playwright
PAGE, TAG = sys.argv[1], sys.argv[2]
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.wait_for_timeout(4000)
        for t in (300, 1500, 2300):
            await pg.evaluate(f"(() => {{ for (const a of document.getAnimations()) {{ a.pause(); a.currentTime = {t}; }} }})()"); await pg.wait_for_timeout(700)
            r = await pg.evaluate("(() => { const b = document.getElementById('homePlay').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; })()")
            await pg.screenshot(path=f'{WS}/ui/lobby_{TAG}_{t}.png', clip={'x': max(0, r[0] - 20), 'y': max(0, r[1] - 20), 'width': r[2] + 40, 'height': r[3] + 50})
        await pg.screenshot(path=f'{WS}/ui/lobby_{TAG}_full.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
