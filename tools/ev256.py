import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
async def main():
    async with async_playwright() as p:
        b = await launch(p); ctx, pg, errs = await boot(b, sys.argv[1], dict(SAVE, mode='duel'), vp=(390, 780), dpr=1, init='window.__instant = false;')
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1500)
        print(await pg.evaluate("JSON.stringify({ solo: document.querySelector('#evSolo .evtx b').textContent, sub: document.querySelector('#evSolo .evtx small').textContent, modes: __T.ev('MODES.map(m => m[1])') })"))
        await pg.evaluate("document.getElementById('evSolo').scrollIntoView()"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{OUT}/ev256_events.png'); print('errors', errs[:4]); await b.close()
asyncio.run(main())
