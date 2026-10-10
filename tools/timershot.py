import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn')
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(500)
        await pg.evaluate("__T.matchLeft = 400; for (const D of __T.ACTIVE) if (D !== __T.P) { D.ai && (D.ai.thinkT = 99); D.spd = 0; } __T.P.held = 'turret'; __T.useHeld(__T.P); if (__T.P.turret) __T.P.turret.t = 4.2;")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/timer_turret.png'); print('turret', await pg.evaluate("[document.getElementById('ptimer').hidden, document.getElementById('ptimer').dataset.k, document.getElementById('ptN').textContent, document.getElementById('ptimer').style.transform]"))
        await pg.evaluate("__T.P.turret = null; __T.P.slamCD = 3.6; __T.P.slamMax = 6;"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{WS}/ui/timer_slam.png'); print('slam', await pg.evaluate("[document.getElementById('ptimer').hidden, document.getElementById('ptimer').dataset.k, document.getElementById('ptN').textContent]"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
