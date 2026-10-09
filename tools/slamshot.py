import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for col, tag in [('red', 'red'), ('green', 'green')]:
            ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', color:'" + col + "', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(800)
            r = await pg.evaluate("(() => { const r = document.getElementById('slamBtn').getBoundingClientRect(); return [r.left|0, r.top|0, r.width|0, r.height|0]; })()")
            clip = {'x': r[0] - 14, 'y': r[1] - 14, 'width': r[2] + 28, 'height': r[3] + 28}
            await pg.evaluate("__T.P.slamCD = 2.5"); await pg.wait_for_timeout(700); print(tag, 'off', await pg.evaluate("document.getElementById('slamBtn').className")); await pg.screenshot(path=f'{WS}/ui/slam_{tag}_off.png', clip=clip)
            await pg.evaluate("__T.P.slamCD = 0"); await pg.wait_for_timeout(900); print(tag, 'ready', await pg.evaluate("document.getElementById('slamBtn').className")); await pg.screenshot(path=f'{WS}/ui/slam_{tag}_on.png', clip=clip)
            print('errors', errs[:2]); await ctx.close()
        await b.close()
asyncio.run(main())
