import asyncio, sys, os
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
LAND = '--land' in sys.argv; TAG = sys.argv[1]
MODE = 'trio' if '--trio' in sys.argv else ('solo' if '--solo' in sys.argv else 'duel')
VP = {'width': 780, 'height': 360} if LAND else ({'width': 360, 'height': 640} if '--small' in sys.argv else {'width': 390, 'height': 780})
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, name:'Dusk', orient:'" + ('land' if LAND else 'port') + "', mode:'" + MODE + "' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000); await pg.wait_for_timeout(1500)
        if '--look' in sys.argv:
            await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(3200); await pg.screenshot(path=f'{WS}/ui/{TAG}_look.png'); await pg.evaluate("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(400)
        await pg.wait_for_function("__T.state === 'play'", timeout=20000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=40000, polling=200); await pg.wait_for_timeout(1500)
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(1800); await pg.screenshot(path=f'{WS}/ui/{TAG}_end.png')
        await pg.wait_for_timeout(5000); await pg.screenshot(path=f'{WS}/ui/{TAG}_end2.png')
        print(TAG, 'errors', errs[:5]); await b.close()
asyncio.run(main())
