"""v257 Strokes page probe. usage: skills257.py PAGE TAG MODE(port|land|lesson)
port/land: an old save (every skill handed out, Weather Repel on) opens the page; Deep Pockets' card, Craft, the countdown, Skip,
Equip; the Giant's card; Escape closes. lesson: a fresh rank-2 save walks the Bloop lesson through the Giant's card."""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/a257s'
import os; os.makedirs(OUT, exist_ok=True)
PAGE, TAG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
ST = "JSON.stringify({ own: store.strokes && store.strokes.own, skill: store.strokes && store.strokes.skill, special: store.strokes && store.strokes.special, craft: store.strokes && store.strokes.craft && store.strokes.craft.id, pop: stPopId, popHidden: $('stPop').hidden, craftBtn: $('stPopCraftBtn').hidden ? 'hidden' : ($('stPopCraftBtn').disabled ? 'off:' : 'on:') + $('stPopCraftBtn').textContent, equipBtn: ($('stPopEquip').disabled ? 'off:' : 'on:') + $('stPopEquip').textContent, timer: !$('stPopTimer').hidden, tip: tutTip && tutTip.key, tipText: tutTip && tutTip.text, labels: [...document.querySelectorAll('#stSkillRail .stopt, #stSpecialRail .stopt')].map(b => (b.dataset.sk || b.dataset.st || 'soon') + ':' + [...b.querySelectorAll('.sts:not(.nil)')].map(x => x.textContent).join('')) })"
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        land = MODE == 'land'; vp = (780, 390) if land else (390, 780)
        if MODE == 'lesson': save = dict(SAVE, xp=170, orient='port', tut={'ph': 'done', 'comms': 1, 'm3': 2})
        else: save = dict(SAVE, xp=400, orient='land' if land else 'port', tut={'ph': 'done', 'strokes': 1, 'comms': 1, 'm3': 2}, strokes={'special': 'rocket', 'skill': 'repel', 'own': ['rocket', 'swim', 'repel', 'pockets']})
        ctx, pg, errs = await boot(b, PAGE, save, vp=vp, dpr=2, init='window.__instant = false; window.__noVote = true; window.__skipIntro = true; window.__noReveal = true;')
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': 0 if land else 59, 'bottom': 21 if land else 34, 'left': 47 if land else 0, 'right': 47 if land else 0}})
        async def shot(n, ms=700): await pg.wait_for_timeout(ms); await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_{n}.png'); print(n, await ev(pg, ST), flush=True)
        click = lambda sel: pg.evaluate("document.querySelector(" + json.dumps(sel) + ").click()")
        await pg.wait_for_timeout(1500)
        if MODE == 'lesson':
            print('rank', await ev(pg, "repOf(store.xp).lv"))
            for _ in range(40):
                if await pg.evaluate("!document.getElementById('tutGo').hidden"): break
                await pg.wait_for_timeout(250)
            await shot('card1', 600); await click('#tgGo'); await shot('card2', 700); await click('#tgGo'); await shot('giant', 1400)
            await click('.stopt[data-st="giant"]'); await shot('craft', 900)
            await click('#stPopCraftBtn'); await shot('skip', 900)
            await click('#stPopSkip'); await shot('equip', 900)
            await click('#stPopEquip'); await shot('equipped', 250); await shot('done', 1300)
            await pg.wait_for_timeout(5500); print('after', await ev(pg, "JSON.stringify({ tut: store.tut, ph: tutPh(), special: strokeSpecial() })"))
        else:
            await click('#abilBtn'); await shot('page', 1500)
            await click('.stopt[data-sk="pockets"]'); await shot('pop_raw')
            await click('#stPopCraftBtn'); await shot('pop_crafting')
            if not land:
                await click('#stPopX'); await shot('page_crafting', 600)
                await click('.stopt[data-sk="pockets"]'); await shot('pop_crafting2', 600)
                await click('#stPopSkip'); await shot('pop_ready', 900)
                await click('#stPopEquip'); await shot('pop_equipped', 200); await shot('page_equipped', 900)
                await click('.stopt[data-st="giant"]'); await shot('pop_special')
                await pg.keyboard.press('Escape'); await shot('closed', 500)
                await click('.stopt[data-st="giant"]'); await pg.wait_for_timeout(300); await click('#stPopCraftBtn'); await pg.wait_for_timeout(300); await click('#stPopX'); await pg.wait_for_timeout(300)
                await click('.stopt[data-st="freeze"]'); await shot('pop_busy')
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
