"""The crouch on a touch: a finger lands and holds (the character crouches), then lifts (a jump); a second finger lands and steers (the crouch
eases out, no jump). Logs preJ, the animator's crouch spring and the root height. usage: crouchtap.py [page]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
Q = "(() => { const P = __T.P, A = __T.VP.slime.ax.A; return [+(P.preJ || 0).toFixed(2), +(A.motion.crouch || 0), +(A.loco && A.loco.cr ? A.loco.cr.x : 0).toFixed(2), P.air ? 1 : 0]; })()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await pg.wait_for_function("!__T.P.air", timeout=60000, polling=100); await pg.wait_for_timeout(1500)
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 180, 'y': 400}]})
        for k in range(4): await pg.wait_for_timeout(40); print('hold', k, await ev(Q))
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); await pg.wait_for_timeout(60); print('lift', await ev(Q))
        await pg.wait_for_function("!__T.P.air", timeout=20000, polling=50); await pg.wait_for_timeout(800)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 180, 'y': 400}]}); await pg.wait_for_timeout(50); print('touch2', await ev(Q))
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 230, 'y': 400}]}); await pg.wait_for_timeout(120); print('steer', await ev(Q))
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); await pg.wait_for_timeout(200); print('after steer lift', await ev(Q))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
