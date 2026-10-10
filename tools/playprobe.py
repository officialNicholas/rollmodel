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
        # the pound dial on the button: paint short, then recharging
        await pg.evaluate("__T.matchLeft = 400; __T.P.slamCD = 0; __T.P.paint = 0.1;"); await pg.wait_for_timeout(900)
        r = await pg.evaluate("(() => { const d = document.getElementById('sbDial'), q = d.getBoundingClientRect(), b = document.getElementById('slamBtn').getBoundingClientRect(); return [d.hidden, d.dataset.k, Math.round(q.left - b.left), Math.round(q.top - b.top), Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height), document.getElementById('ptimer').hidden]; })()"); print('dial paint', r)
        await pg.screenshot(path=f'{WS}/ui/sbdial_paint.png', clip={'x': r[4] - 20, 'y': r[5] - 20, 'width': r[6] + 40, 'height': r[7] + 40})
        await pg.evaluate("__T.P.paint = 1; __T.P.slamCD = 3.7; __T.P.slamMax = 6;"); await pg.wait_for_timeout(900)
        print('dial cd', await pg.evaluate("[document.getElementById('sbDial').hidden, document.getElementById('sbDial').dataset.k, document.getElementById('sbN').textContent]"))
        await pg.screenshot(path=f'{WS}/ui/sbdial_cd.png', clip={'x': r[4] - 20, 'y': r[5] - 20, 'width': r[6] + 40, 'height': r[7] + 40})
        # the sun: it dries, it does not kill
        await pg.evaluate("__T.P.slamCD = 0; __T.setWx('sun', 60);"); await pg.wait_for_function("__T.wx === 'sun'", timeout=30000, polling=200); await pg.wait_for_timeout(200)
        await pg.evaluate("__T.P.paint = 0.08; __T.P.sunGrace = 0;"); await pg.wait_for_function("__T.P.dry || __T.P.st !== 'play'", timeout=60000, polling=200)
        print('sun', await pg.evaluate("[__T.wx, __T.P.exposed, __T.P.dry, __T.P.st, +__T.P.paint.toFixed(2)]"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
