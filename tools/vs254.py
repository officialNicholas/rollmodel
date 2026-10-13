"""v254: the fight card for four, held on screen (its closing timers dropped) so a slow test browser can take it.
usage: vs254.py PAGE TAG MODE(ffa|duo) [--land]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]; LAND = '--land' in sys.argv
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        vp = (780, 390) if LAND else (390, 780); o = 'land' if LAND else 'port'
        ctx, pg, errs = await boot(b, PAGE, dict(SAVE, mode=MODE, orient=o), vp=vp, dpr=2, init='window.__instant = false; window.__noVote = true; window.__skipIntro = false; window.__noReveal = true;')
        await pg.evaluate("(() => { const st = window.setTimeout; window.__stOrig = st; window.setTimeout = (f, ms, ...a) => ms >= 900 && ms <= 2200 ? 0 : st(f, ms, ...a); })()")
        await pg.evaluate("__T.start()"); await pg.wait_for_function("!document.getElementById('vsx').hidden", timeout=180000, polling=50)
        print(await pg.evaluate("[...document.querySelectorAll('#vsRow .vcol')].map(c => c.className + ':' + c.querySelector('.vhead').innerText.replace(/\\n/g, ' '))"))
        for k in range(2):
            await pg.wait_for_timeout(4000); await pg.screenshot(path=f'{OUT}/{TAG}_{o}_{MODE}_vscard{k}.png', timeout=120000); print('shot', k)
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
