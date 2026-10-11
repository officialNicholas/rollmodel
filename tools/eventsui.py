"""v209: Play opens Choose Event; Versus CPU drops down 1v1 / 3-way; the canvases (vote) with no mode tabs; back to the events; Showdown
says soon; then a 3-way from the canvases, and the fight card's reel spinning and landing with the votes. usage: eventsui.py [p|l]"""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
W, H, T = (390, 844, 'p') if (len(sys.argv) < 2 or sys.argv[1] == 'p') else (844, 390, 'l')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, runs: 9, drops: 168, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{OUT}/ev_{T}_home.png', timeout=120000)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/ev_{T}_events.png', timeout=120000)
        print('events', await pg.evaluate("[document.getElementById('mEvents').hidden, document.getElementById('mHome').hidden, document.getElementById('menu').dataset.page]"))
        await pg.evaluate("document.getElementById('evVs').click()"); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{OUT}/ev_{T}_vsdrop.png', timeout=120000)
        await pg.evaluate("document.getElementById('evShow').click()"); await pg.wait_for_timeout(500); await pg.screenshot(path=f'{OUT}/ev_{T}_soon.png', timeout=120000)
        await pg.evaluate("document.querySelector('#evVsPick [data-m=duel]').click()"); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{OUT}/ev_{T}_canvases.png', timeout=120000)
        print('canvases', await pg.evaluate("[document.getElementById('mWorld').hidden, document.getElementById('worldTitle').textContent, getComputedStyle(document.getElementById('modes')).display, document.getElementById('stages').hidden, __T.mode]"))
        await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(800)
        print('back', await pg.evaluate("[document.getElementById('mEvents').hidden, document.getElementById('mWorld').hidden, document.getElementById('menu').dataset.page]"))
        await pg.evaluate("document.getElementById('evVs').click()"); await pg.wait_for_timeout(400); await pg.evaluate("document.querySelector('#evVsPick [data-m=trio]').click()"); await pg.wait_for_timeout(2500)
        print('trio', await pg.evaluate("[__T.mode, document.getElementById('worldTitle').textContent]"))
        await pg.evaluate("document.getElementById('startBtn').click()")
        await pg.wait_for_function("document.getElementById('vvote') && !document.getElementById('vvote').hidden", timeout=90000, polling=100)
        await pg.wait_for_timeout(600); await pg.screenshot(path=f'{OUT}/ev_{T}_reel0.png', timeout=120000)
        await pg.wait_for_function("!!document.querySelector('.vcard.win')", timeout=30000, polling=50); await pg.wait_for_timeout(350)
        for k in (1, 2):
            await pg.screenshot(path=f'{OUT}/ev_{T}_reel{k}.png', timeout=120000)
            print('reel', k, await pg.evaluate("[document.getElementById('vvLbl').textContent, document.getElementById('vvWin').textContent, document.getElementById('vtally') ? document.getElementById('vtally').textContent : null, !!document.querySelector('.vcard.win')]"))
        await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=60000, polling=200)
        print('match started', await pg.evaluate("[__T.state, __T.mode]"), 'errors', errs[:6])
        await b.close()
asyncio.run(main())
