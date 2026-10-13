"""v256 colours with CPUs: 2v2 teams (your teammate in your colour, the other pair in its leader's), free-for-all apart from yours.
usage: col256.py PAGE TAG"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG = sys.argv[1], sys.argv[2]
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
Q = "JSON.stringify({ mode, mine: colorOf().id, own: rivalCol.map(c => c && c.id), show: TEAMS.map(t => t.css), H3: TEAMS[3].css === TEAMS[0].css, H12: TEAMS[1].css === TEAMS[2].css, d: +colDist(TEAMS[0].wet, TEAMS[1].wet).toFixed(3) })"
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        for mode, col in [('duo', 'red'), ('duo', 'green'), ('ffa', 'red')]:
            save = dict(SAVE, mode=mode, diff='medium', color=col)
            ctx, pg, errs = await boot(b, PAGE, save, vp=(390, 780), dpr=2, init='window.__skipIntro = false; window.__noReveal = true;')
            for k in range(3):
                await ev(pg, "(rollRivalCols(), teamTint = true, teamHues(), 0)")
                print(mode, col, await ev(pg, Q), flush=True)
            await pg.evaluate("__T.start()")
            await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=240000, polling=50)
            await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(300)
            for _ in range(500):
                if await pg.evaluate("__T.state === 'play'"): break
                await pg.evaluate("__adv(1/30, 6)")
            await pg.evaluate("__adv(1/30, 30)")
            print(mode, col, 'match', await ev(pg, Q), flush=True)
            await pg.screenshot(path=f'{OUT}/{TAG}_{mode}_{col}.png', timeout=120000)
            print('errors', errs[:4]); await ctx.close()
        await b.close()
asyncio.run(main())
