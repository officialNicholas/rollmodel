"""v254 regression: a duel and a 3-way still play through to the tally, the winner screen and the results (screenshots).
usage: reg254.py PAGE TAG MODE(duel|trio|solo)"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        save = dict(SAVE, mode=MODE)
        await ctx.add_init_script("window.__instant = false; window.__noVote = true; window.__noReveal = true; window.__skipIntro = false; window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=500); await pg.wait_for_timeout(2000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=240000, polling=200); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_hud.png', timeout=120000)
        print(await pg.evaluate("__T.ev(`JSON.stringify({ mode, n: ACTIVE.length, side: SIDE, cols: TEAMS.map(t => t.css), arena: ARENA, hp: ACTIVE.map(D => D.hearts) })`)"))
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic || (__T.tal && __T.tal.t > 3)", timeout=120000, polling=200); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_tally.png', timeout=120000)
        await pg.wait_for_function("!!__T.vic", timeout=120000, polling=200); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_victory.png', timeout=120000)
        await pg.evaluate("document.getElementById('victory').click()"); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=20000); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f'{OUT}/{TAG}_{MODE}_end.png', timeout=120000)
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
