"""v257: Time trial and Showdown locked below rank 2. usage: lock257.py PAGE TAG"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/a257s'
PAGE, TAG = sys.argv[1], sys.argv[2]
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
Q = "JSON.stringify({ rank: repOf(store.xp).lv, mode, page: menuPage, cards: [...document.querySelectorAll('#mEvents .evcard')].map(c => c.dataset.ev + (c.classList.contains('lock') ? ':lock' : '') + (c.classList.contains('fresh') ? ':new' : '')), toast: [...document.querySelectorAll('#mEvents .evtoast')].map(t => t.textContent), showOpen: !$('evShowPick').hidden, evNew: store.evNew || null })"
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        save = dict(SAVE, xp=50, mode='solo', tut={'ph': 'done', 'strokes': 1, 'comms': 1, 'm3': 2})
        ctx, pg, errs = await boot(b, PAGE, save, vp=(390, 780), dpr=2, init='window.__instant = false; window.__noVote = true;')
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': 59, 'bottom': 34, 'left': 0, 'right': 0}})
        await pg.wait_for_timeout(1500)
        print('boot', await ev(pg, Q))
        click = lambda sel: pg.evaluate("document.querySelector(" + json.dumps(sel) + ").click()")
        await click('#homePlay'); await pg.wait_for_timeout(1300); print('events', await ev(pg, Q)); await pg.screenshot(path=f'{OUT}/{TAG}_locked.png')
        await click('#evSolo'); await pg.wait_for_timeout(250); print('tap solo', await ev(pg, Q)); await pg.screenshot(path=f'{OUT}/{TAG}_locked_tap.png')
        await pg.wait_for_timeout(1800); await click('#evShow'); await pg.wait_for_timeout(250); print('tap show', await ev(pg, Q))
        await click('#evBack'); await pg.wait_for_timeout(700)
        await ev(pg, "(store.xp = 170, store.evNew = { solo: 1, showdown: 1 }, renderLobbyUI(), 0)")
        await click('#homePlay'); await pg.wait_for_timeout(1300); print('rank2', await ev(pg, Q)); await pg.screenshot(path=f'{OUT}/{TAG}_open.png')
        await click('#evShow'); await pg.wait_for_timeout(500); print('show opens', await ev(pg, Q))
        await click('#evSolo'); await pg.wait_for_timeout(1200); print('solo picked', await ev(pg, Q))
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
