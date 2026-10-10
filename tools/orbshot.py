import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn')
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300)
        await pg.evaluate("__T.matchLeft = 400; __T.orb.spawnT = 0.01;"); await pg.wait_for_function("__T.orb.on", timeout=60000, polling=200)
        await pg.evaluate("(() => { const f = document.getElementById('orbFlash'); f.classList.remove('on'); void f.offsetWidth; f.classList.add('on'); f.style.animationPlayState = 'paused'; for (const i of document.querySelectorAll('#orbFlash i')) i.style.animationPlayState = 'paused'; })()")
        for k, at in enumerate(['0s', '0.45s', '0.9s']):
            await pg.evaluate("(at => { for (const i of document.querySelectorAll('#orbFlash i')) i.style.animationDelay = '-' + at; })('%s')" % at); await pg.wait_for_timeout(250)
            await pg.screenshot(path=f'{WS}/ui/orb_flash_{k}.png')
        print('flash', await pg.evaluate("[...document.querySelectorAll('#orbFlash i')].map(i => getComputedStyle(i).opacity)"), errs[:2]); await b.close()
asyncio.run(main())
