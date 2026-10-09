import asyncio, sys, time
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
LAND = '--land' in sys.argv; MODE = 'trio' if '--trio' in sys.argv else 'duel'; TAG = sys.argv[1]
VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if LAND else 'port') + "', name:'Dusk', mode:'" + MODE + "', stage:'crypt', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','lashes'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        t0 = time.time(); await pg.evaluate("document.getElementById('homePlay').click()")
        n = 0
        for target in (1.9, 3.4, 5.2, 6.3, 7.6):
            d = target - (time.time() - t0)
            if d > 0: await pg.wait_for_timeout(int(d * 1000))
            st = await pg.evaluate("(() => { const v = document.getElementById('vvote'); return [document.getElementById('vsx').hidden, v.hidden, v.className, document.getElementById('vvWin').textContent, [...document.querySelectorAll('.vt')].map(b => b.dataset.s + ':' + b.querySelectorAll('.vch i').length + (b.classList.contains('win') ? '*' : '')).join(' ')]; })()")
            print(round(time.time() - t0, 1), st); await pg.screenshot(path=f'{WS}/ui/{TAG}_vote{n}.png'); n += 1
        await pg.wait_for_function("__T.state === 'play'", timeout=120000); print('match on', await pg.evaluate("[__T.TH ? __T.TH.id : 'n/a', document.getElementById('vvote').hidden, document.getElementById('vsx').hidden]"))
        print(TAG, 'errors', errs[:4]); await b.close()
asyncio.run(main())
