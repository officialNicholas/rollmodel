import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1,dilute:1,dry:1}, runs: 1, drops: 40, stage:'crypt', tut: { ph: 'match2' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=90000): await pg.wait_for_function(js, timeout=t, polling=150)
        tip = "[__T.tut2 && __T.tut2.ph, __T.wx, __T.tutTip && __T.tutTip.key, __T.tutTip && __T.tutTip.text, document.getElementById('banner').classList.contains('on'), document.getElementById('tutArrow').hidden]"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"', 240000); await pg.wait_for_timeout(1200)
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'")
        await pg.wait_for_timeout(1500); print('calm', await pg.evaluate(tip), await pg.evaluate("[__T.wxLeft > 1000, __T.gift.id]"))
        await pg.evaluate("__T.matchLeft = 46"); await wait("__T.tut2 && __T.tut2.ph === 'sun'"); await pg.wait_for_timeout(500); print('sun', await pg.evaluate(tip)); await pg.screenshot(path=f'{WS}/ui/m2_sun.png')
        for k in range(12):
            if await pg.evaluate("__T.tut2.ph") != 'sun': break
            await pg.evaluate("__T.setWx(__T.wx, 0.02)"); await pg.wait_for_timeout(500)
        await wait("__T.tut2.ph === 'rain'"); await pg.wait_for_timeout(400); print('rain', await pg.evaluate(tip)); await pg.screenshot(path=f'{WS}/ui/m2_rain.png')
        await pg.evaluate("__T.setWx('rain', 0.02)"); await wait("__T.tut2.ph === 'gift'"); await wait("__T.gift.on", 60000); await pg.wait_for_timeout(800)
        print('gift', await pg.evaluate(tip), await pg.evaluate("[__T.gift.id, +__T.matchLeft.toFixed(1)]")); await pg.screenshot(path=f'{WS}/ui/m2_gift.png')
        await pg.evaluate("__T.P.x = __T.gift.x; __T.P.z = __T.gift.z;"); await wait("__T.gift.got", 30000); await pg.wait_for_timeout(500)
        print('got', await pg.evaluate("[__T.tut2.ph, __T.store.zombieDeal, __T.OWNED.has('zombie'), __T.store.drops]"))
        await pg.evaluate("__T.P.kos = 2; __T.matchLeft = 0.05;"); await wait("__T.state === 'dead'", 60000)
        await wait("!document.getElementById('victory').hidden", 90000); await wait("__T.vic && __T.vic.t >= 1", 90000); await pg.evaluate("document.getElementById('victory').click()")
        await wait("!document.getElementById('newItem').hidden || !document.getElementById('end').hidden", 90000); await pg.wait_for_timeout(1200)
        if await pg.evaluate("!document.getElementById('newItem').hidden"): print('newitem shown'); await pg.evaluate("document.getElementById('niGo').click()"); await wait("!document.getElementById('end').hidden", 60000); await pg.wait_for_timeout(800)
        await pg.evaluate("document.getElementById('menuBtn').click()"); await wait("!document.getElementById('tutGo').hidden", 120000); await pg.wait_for_timeout(900)
        print('welcome', await pg.evaluate("[__T.tutPh(), document.getElementById('tgTitle').textContent, document.getElementById('tgText').textContent]")); await pg.screenshot(path=f'{WS}/ui/m2_welcome.png')
        await pg.evaluate("document.getElementById('tgLater').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1200)
        print('shop', await pg.evaluate("[__T.store.drops, (document.querySelector('#shopGrid .shitem[data-w=\"zombie\"]') || {}).textContent]")); await pg.screenshot(path=f'{WS}/ui/m2_shop.png')
        print('done', await pg.evaluate("[__T.tutPh(), document.getElementById('commBtn').offsetParent !== null, JSON.stringify(__T.store.comm && { day: __T.store.comm.day, n: __T.store.comm.active.length })]"))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
