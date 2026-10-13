"""v254 Showdown screens in real time: the event card and its two choices, the fight card for four, the match HUD with tags.
usage: ui254.py PAGE TAG MODE(ffa|duo) [--land]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]; LAND = '--land' in sys.argv
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        vp = {'width': 780, 'height': 390} if LAND else {'width': 390, 'height': 780}
        ctx = await b.new_context(viewport=vp, device_scale_factor=2, has_touch=True, is_mobile=True)
        save = dict(SAVE, mode='duel', orient='land' if LAND else 'port')
        await ctx.add_init_script("window.__instant = false; window.__noVote = true; window.__skipIntro = false; window.__noReveal = true; window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=500); await pg.wait_for_timeout(2500)
        o = 'land' if LAND else 'port'
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1400)
        await pg.evaluate("document.getElementById('evShow').click()"); await pg.wait_for_timeout(900)
        await pg.screenshot(path=f'{OUT}/{TAG}_{o}_events.png'); print('events')
        await pg.evaluate(f"document.querySelector('#evShowPick [data-m={MODE}]').click()"); await pg.wait_for_timeout(1500)
        print('mode now', await pg.evaluate("__T.mode"), await pg.evaluate("__T.ev('menuPage')"))
        await pg.screenshot(path=f'{OUT}/{TAG}_{o}_{MODE}_canvases.png')
        await pg.evaluate("__T.start()"); await pg.wait_for_function("!document.getElementById('vsx').hidden", timeout=120000, polling=50)
        for k in range(4):
            await pg.wait_for_timeout(450); await pg.screenshot(path=f'{OUT}/{TAG}_{o}_{MODE}_vs{k}.png', timeout=120000)
        print('vs')
        await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=180000, polling=100)
        await pg.evaluate("window.__tscale = 1e-9"); await pg.evaluate(ADV)
        for _ in range(400):
            if await pg.evaluate("__T.state === 'play'"): break
            await pg.evaluate("__adv(1/30, 6)")
        await pg.evaluate("__adv(1/30, 40)"); await pg.evaluate("window.__tscale = 1"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/{TAG}_{o}_{MODE}_hud.png', timeout=120000); print('hud')
        # walk the camera's subject next to a rival so a tag shows, then look again
        await pg.evaluate("__T.ev(`(() => { const R = ACTIVE.find(D => D !== P && D.st === 'play'); if (R) { R.x = P.x + Math.sin(P.yaw) * 5; R.z = P.z + Math.cos(P.yaw) * 5; R.y = P.y; } })()`)"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f'{OUT}/{TAG}_{o}_{MODE}_tag.png', timeout=120000); print('tag')
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
