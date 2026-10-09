import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, look:{eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); logs = []; pg.on('console', lambda m: logs.append(m.text[:400]) if m.type == 'error' and 'CORS' not in m.text and 'ERR_FAILED' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(8500); await pg.evaluate("window.__idleForce = 'still'"); await pg.wait_for_timeout(1500)
        for k in range(3): await pg.screenshot(path=f'{WS}/ui/eye_{TAG}_locker{k}.png', clip={'x': 60, 'y': 70, 'width': 270, 'height': 260}); await pg.wait_for_timeout(700)
        await pg.evaluate("window.__idleForce = 'yawn'"); await pg.wait_for_timeout(4800); await pg.screenshot(path=f'{WS}/ui/eye_{TAG}_face.png', clip={'x': 60, 'y': 70, 'width': 270, 'height': 260})
        await pg.evaluate("window.__idleForce = null; document.getElementById('lookDone').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1400); await pg.screenshot(path=f'{WS}/ui/eye_{TAG}_card.png', clip={'x': 0, 'y': 60, 'width': 195, 'height': 420})
        print(TAG, 'errors', errs[:3], logs[:3]); await b.close()
asyncio.run(main())
