"""v255: Rematch (New canvas) from the results opens the canvas vote for the same event (difficulty and canvas can change there), Play goes
on to the fight card; Back from the vote goes to the events. Run with a phone's insets emulated (59 top, 34 bottom) to check the fight
card's top label. usage: rm255.py PAGE TAG MODE [--land]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]; LAND = '--land' in sys.argv
ST = "__T.ev(`JSON.stringify({ state, menuPage, mode, diff, stageSel, evFrom, title: $('worldTitle').textContent, vsx: !$('vsx').hidden, iris: irisBusy, ev: !evEl.hidden })`)"
async def shot(pg, n): await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_{n}.png', timeout=120000); print('shot', n)
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        vp = (780, 390) if LAND else (390, 780)
        ctx, pg, errs = await boot(b, PAGE, dict(SAVE, mode=MODE, diff='medium', orient='land' if LAND else 'port'), vp=vp, dpr=2, init='window.__instant = false; window.__noVote = true; window.__skipIntro = false; window.__noReveal = true;')
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': 0 if LAND else 59, 'bottom': 21 if LAND else 34, 'left': 47 if LAND else 0, 'right': 47 if LAND else 0}})
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000, polling=200); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.3; })()")
        for _ in range(400):
            if await pg.evaluate("!document.getElementById('end').hidden"): break
            if await pg.evaluate("!!__T.vic && !window.vicClicked"): await pg.wait_for_timeout(2500); await pg.evaluate("window.vicClicked = true; document.getElementById('victory').click()")
            await pg.wait_for_timeout(750)
        await pg.wait_for_timeout(2500)
        print('end', await pg.evaluate(ST)); await shot(pg, 'end')
        await pg.evaluate("document.getElementById('endBtn').click()")
        await pg.wait_for_function("__T.ev('state') === 'menu' && __T.ev('menuPage') === 'worlds' && !__T.ev('irisBusy')", timeout=120000, polling=100); await pg.wait_for_timeout(1500)
        print('after rematch', await pg.evaluate(ST)); await shot(pg, 'vote')
        # back goes to the events, and the events' pick comes back to the vote
        await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(1200); print('after back', await pg.evaluate(ST)); await shot(pg, 'events')
        await pg.evaluate(f"__T.ev(`evPick('{MODE}')`)"); await pg.wait_for_timeout(1200); print('picked again', await pg.evaluate(ST))
        # a harder field and the next canvas, then Play: the fight card (held on screen for the picture)
        await pg.evaluate("document.querySelector('#stages [data-d=hard]').click()"); await pg.evaluate("document.getElementById('gNext').click()"); await pg.wait_for_timeout(900)
        print('changed', await pg.evaluate(ST))
        await pg.evaluate("(() => { const st = window.setTimeout; window.setTimeout = (f, ms, ...a) => ms >= 900 && ms <= 2200 ? 0 : st(f, ms, ...a); })()")
        await pg.evaluate("document.getElementById('startBtn').click()"); await pg.wait_for_function("!document.getElementById('vsx').hidden", timeout=180000, polling=50); await pg.wait_for_timeout(5000)
        print('play', await pg.evaluate(ST)); await shot(pg, 'vscard')
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
