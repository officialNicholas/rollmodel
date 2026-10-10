import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=1, has_touch=True, is_mobile=True, reduced_motion='no-preference')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn')
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(500)
        await pg.evaluate("__T.matchLeft = 400; __T.knockOut(__T.P, 'splat', __T.H);")
        for i, ms in enumerate([60, 300, 400, 300, 400]):
            await pg.wait_for_timeout(ms)
            st = await pg.evaluate("[__T.P.st, document.getElementById('kof').hidden, document.getElementById('kof').className, document.getElementById('kofSmall').textContent, document.getElementById('kofBy').textContent]")
            print('ko', i, st); await pg.screenshot(path=f'{WS}/ui/ko_{i}.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
