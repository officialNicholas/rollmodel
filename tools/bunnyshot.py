import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
FIT = sys.argv[1] if len(sys.argv) > 1 else ''
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script((("window.__bunnyFit = " + FIT + ";") if FIT else "") + "try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['bunny','hockey'], bought:['bunny','hockey'], drops:300, look:{head:'bunny', eye:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(7500); await pg.evaluate("window.__idleForce = 'still'"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{WS}/ui/bunny_locker.png'); await pg.screenshot(path=f'{WS}/ui/bunny_close.png', clip={'x': 40, 'y': 60, 'width': 310, 'height': 300})
        await pg.evaluate("document.getElementById('lc-head').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/bunny_tab.png')
        print('tiles', await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile')].map(t => t.getAttribute('aria-label'))"), await pg.evaluate("[__T.myLook.eye, __T.VP && __T.VP.W ? 'W' : 'noW']"))
        await pg.evaluate("window.__idleForce = null; document.getElementById('lookDone').click()"); await pg.wait_for_timeout(500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/bunny_card.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(run())
