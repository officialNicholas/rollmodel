"""Match 2's missile lesson: when the pound fills, the slingshot tip (slowed), a fling, the pound-in-the-air tip, the missile, then Ol' Bloop's
corner line. Shots at each tip. usage: missilelesson.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
ST = "[+__T.runT.toFixed(1), __T.tut2 && __T.tut2.ms, __T.tut2 && __T.tut2.slowK, __T.tutTip && __T.tutTip.key, __T.P.air, __T.P.slam, __T.P.missile, +__T.matchLeft.toFixed(1)]"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 2, xp: 300, tut: { ph: 'match2' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        wait = lambda f, t=240000: pg.wait_for_function(f, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await ev("__T.start()"); await wait("__T.state === 'play' && __T.tut2", 400000); print('tut2', await ev("__T.tut2.ph"))
        print("at", await ev(ST)); await wait("__T.runT > 5 && !__T.P.air && __T.P.st === 'play'", 400000)
        await ev("__T.P.slamCD = 0; __T.P.paint = 1"); await wait("__T.tutTip && __T.tutTip.key === 'msling'", 60000); print('sling', await ev(ST))
        await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{WS}/ui/ml_{TAG}_1.png'); print(await ev(ST))
        await ev("__T.flingIt(__T.P, 0.85)"); await wait("__T.tutTip && __T.tutTip.key === 'mpound'", 30000); print('pound tip', await ev(ST))
        await pg.wait_for_timeout(400); await pg.screenshot(path=f'{WS}/ui/ml_{TAG}_2.png'); print('slamReady', await ev("__T.slamReadyP"))
        await ev("__T.useSlam(__T.P)"); await wait("__T.tutTip && __T.tutTip.key === 'melim'", 30000); print('elim', await ev(ST))
        await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/ml_{TAG}_3.png')
        await wait("__T.tut2.ms === 'done'", 60000); print('done', await ev(ST)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
