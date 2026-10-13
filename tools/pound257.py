"""v257: the first ground pound is ready 4 s into a match. usage: pound257.py PAGE"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE = sys.argv[1]
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        ctx, pg, errs = await boot(b, PAGE, dict(SAVE, mode='duel', diff='medium'), init='window.__skipIntro = false; window.__noReveal = true;')
        await pg.evaluate("__T.start()")
        await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=240000, polling=50)
        await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(300)
        for _ in range(500):
            if await pg.evaluate("__T.state === 'play'"): break
            await pg.evaluate("__adv(1/30, 6)")
        q = "JSON.stringify({ t: +runT.toFixed(2), p: +P.slamCD.toFixed(2), pmax: P.slamMax, h: +H.slamCD.toFixed(2), ready: slamReady(P), btn: $('slamBtn').className })"
        print('at go', await ev(pg, q))
        for k in range(9): await pg.evaluate("__adv(1/30, 15)"); print('+0.5s', await ev(pg, q))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
