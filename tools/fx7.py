import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
LAND = '--land' in sys.argv; MODE = 'trio' if '--trio' in sys.argv else 'duel'; TAG = sys.argv[1]
VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = window.__INST === undefined ? false : window.__INST; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if LAND else 'port') + "', name:'Dusk', mode:'" + MODE + "', stage:'crypt', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','lashes','pirate','tophat','tiara','halo','fangs','patch','glasses','flower','bowtie'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f'{WS}/ui/{TAG}_lobby.png')
        await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/{TAG}_pick.png')
        await pg.evaluate("document.getElementById('gPrev').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/{TAG}_pick2.png')
        await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(600); await pg.screenshot(path=f'{WS}/ui/{TAG}_vs.png')
        await pg.wait_for_function("__T.state === 'play'", timeout=90000); await pg.wait_for_timeout(1500)
        await pg.evaluate("window.__noLoop = true"); await pg.wait_for_timeout(300)
        v = "document.getElementById('vig')"
        await pg.evaluate(v + ".className = 'vig low'"); await pg.wait_for_timeout(400); await pg.screenshot(path=f'{WS}/ui/{TAG}_low.png')
        await pg.evaluate(v + ".className = 'vig heat'"); await pg.wait_for_timeout(400); await pg.screenshot(path=f'{WS}/ui/{TAG}_heat.png')
        await pg.evaluate(v + ".className = 'vig'; " + v + ".style.setProperty('--hc', '#2E9BFF'); " + v + ".classList.add('hit')"); await pg.wait_for_timeout(200); await pg.screenshot(path=f'{WS}/ui/{TAG}_hit.png')
        print(TAG, 'errors', errs[:4]); await b.close()
asyncio.run(main())
