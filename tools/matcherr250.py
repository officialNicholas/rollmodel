"""v250 smoke test with drawing on: boot, the lobby, the locker (a colour change), a match with steering, jumps, a fling, a pound, rain and
the heat, the winner screen; every page error and console error collected, and a few shots. usage: matcherr250.py [page] [stage]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; SID = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; cons = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: cons.append(m.text[:300]) if m.type == 'error' and 'CORS' not in m.text and 'ERR_FAILED' not in m.text and 'favicon' not in m.text else None)
        ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=900000); await pg.wait_for_function('typeof __T === "object"', timeout=900000, polling=100); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/me250_lobby.png')
        await ev("__T.openLook()"); await pg.wait_for_timeout(2500); await ev("(() => { const s = document.querySelector('#swatches [data-c], .swatch, .sw'); if (s) s.click(); })()"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/me250_locker.png'); await ev("__T.closeLook()"); await pg.wait_for_timeout(1000)
        await ev("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=900000, polling=100); await pg.wait_for_timeout(2000)
        await ev("__T.wxLeft = 999")
        for i, js in enumerate(["__T.steerIn = 0.8", "__T.jump(__T.P)", "__T.steerIn = -0.8", "__T.flingIt(__T.P, 0.7)", "__T.steerIn = 0", "__T.useSlam(__T.P)", "__T.ev('setWx(\"rain\", 3)')", "__T.ev('setWx(\"warn\", 2)')"]):
            try: await ev(js)
            except Exception as e: print('step', i, str(e)[:120])
            await pg.wait_for_timeout(1500)
            if i in (1, 3, 5, 7): await pg.screenshot(path=f'{WS}/ui/me250_play{i}.png')
        await ev("__T.matchLeft = 0.2"); await pg.wait_for_function("!!__T.vic", timeout=600000, polling=200); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/me250_vic.png')
        print('state', await ev("[__T.state, __T.P.st]")); print('page errors', errs[:5]); print('console errors', cons[:8]); await b.close()
asyncio.run(main())
