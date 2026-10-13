"""v254 Showdown probes. usage: sd254.py PAGE TAG MODE(ffa|duo) [scenario]
  flow    hearts HUD, knock everyone out in turn, the end, the victory screen and the results (screenshots)
  meout   you lose both hearts: the flood, then watching someone, then skip to results"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]; SC = sys.argv[4] if len(sys.argv) > 4 else 'flow'
LAND = '--land' in sys.argv
async def shot(pg, name):
    await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_{name}.png'); print('shot', name)
async def adv(pg, secs, dt=1/30):
    n = max(1, round(secs / dt)); 
    while n > 0: k = min(n, 15); await pg.evaluate(f"__adv({dt}, {k})"); n -= k
async def st(pg):
    return await pg.evaluate("__T.ev(`JSON.stringify({ state, mode, n: ACTIVE.length, side: SIDE, hp: ACTIVE.map(D => [nameOf(D), D.st, D.hearts, D.place, D.kos, D.selfOuts]), sdEndT, spec: spec && spec.D ? nameOf(spec.D) : null, left: +matchLeft.toFixed(1) })`)")
async def ko(pg, who, by, reason='pound'):
    # wait until it's back in play (or in a basin), then knock it out
    for _ in range(80):
        s = await pg.evaluate(f"__T.ev('{who}.st')")
        if s in ('play', 'hide'): break
        await adv(pg, 0.25)
    await pg.evaluate(f"__T.ev(`{who}.immuneT = 0; knockOut({who}, '{reason}', {by})`)")
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        vp = (780, 390) if LAND else (390, 780)
        save = dict(SAVE, mode=MODE, orient='land' if LAND else 'port')
        ctx, pg, errs = await boot(b, PAGE, save, vp=vp, dpr=2, init='window.__skipIntro = false; window.__noReveal = true;')
        await pg.evaluate("__T.start()")
        await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=180000, polling=50)
        await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(300)
        for _ in range(400):
            if await pg.evaluate("__T.state === 'play'"): break
            await pg.evaluate("__adv(1/30, 6)")
        await pg.evaluate("window.__tscale = 1"); await pg.wait_for_timeout(2000); await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(200)
        await adv(pg, 1.5)
        print(await st(pg)); await shot(pg, 'start')
        if SC == 'flow':
            foes = ['H3', 'H2', 'H'] if MODE == 'ffa' else ['H', 'H2']
            await ko(pg, foes[0], 'P'); await adv(pg, 0.6); print(await st(pg)); await shot(pg, 'ko1')
            await adv(pg, 4); await ko(pg, foes[0], 'P'); await adv(pg, 0.5); print(await st(pg)); await shot(pg, 'elim1')
            await adv(pg, 3); print(await st(pg))
            if MODE == 'ffa':
                await ko(pg, 'H2', 'H'); await adv(pg, 4); await ko(pg, 'H2', 'null', 'fall'); await adv(pg, 3); print(await st(pg)); await shot(pg, 'elim2')
                await ko(pg, 'H', 'P'); await adv(pg, 4); await ko(pg, 'H', 'P');
            else:
                await ko(pg, 'H2', 'H3'); await adv(pg, 4); await ko(pg, 'H2', 'P');
            await adv(pg, 0.8); print(await st(pg)); await shot(pg, 'last')
            for _ in range(60):
                if await pg.evaluate("!!__T.vic"): break
                await adv(pg, 0.25); await pg.wait_for_timeout(60)
            await pg.evaluate("window.__tscale = 1"); await pg.wait_for_timeout(2500); print(await st(pg)); await shot(pg, 'victory')
            await pg.evaluate("document.getElementById('victory').click()"); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=15000); await pg.wait_for_timeout(2600); await shot(pg, 'end')
        else:
            await ko(pg, 'P', 'H'); await adv(pg, 0.4); await pg.evaluate("window.__tscale = 1"); await pg.wait_for_timeout(1600); await pg.evaluate("window.__tscale = 1e-9"); await shot(pg, 'meko1')
            await adv(pg, 5); await ko(pg, 'P', 'H2'); await pg.evaluate("window.__tscale = 1"); await pg.wait_for_timeout(1800); await pg.evaluate("window.__tscale = 1e-9"); print(await st(pg)); await shot(pg, 'meout')
            await adv(pg, 3.5); print(await st(pg)); await shot(pg, 'spec')
            await pg.evaluate("document.getElementById('sdSkip').click()"); await pg.evaluate("window.__tscale = 1"); await pg.wait_for_timeout(1500)
            print('ff', await pg.evaluate("__T.ev(`JSON.stringify({ ff: spec && spec.ff, w: $('sdSpecW').textContent, l: $('sdSkipL').textContent, dis: $('sdSkip').disabled, left: +matchLeft.toFixed(1) })`)")); await shot(pg, 'ff')
            for _ in range(1600):
                if await pg.evaluate("!!__T.vic"): break
                await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(2500); print(await st(pg)); await shot(pg, 'victory2')
            await pg.evaluate("document.getElementById('victory').click()"); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=15000); await pg.wait_for_timeout(2600); await shot(pg, 'end2')
        print('errors', errs[:6]); await ctx.close(); await b.close()
asyncio.run(main())
