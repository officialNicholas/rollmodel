import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
# the Eyes tab with zombie eyes locked, the shop's Eyes row, then the eyes bought and worn (a close look at the face)
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        for owned, bought, tag in [(['zombie', 'flower'], ['flower'], 'locked'), (['zombie', 'flower'], ['zombie', 'flower'], 'owned')]:
            ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:" + json.dumps(owned) + ", bought:" + json.dumps(bought) + ", drops:1400, look:{head:null, eyes:'" + ('zombie' if 'zombie' in bought else 'round') + "', iris:'violet'} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type in ('error', 'warning') and 'Failed to load' not in m.text and errs.append(m.text[:300]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(7000)
            await pg.evaluate("document.getElementById('lc-eyes').click()"); await pg.wait_for_timeout(1200)
            print(tag, 'eyes tab', await pg.evaluate("[...document.querySelectorAll('#eyeStyles .eyes')].map(b => [b.dataset.es, b.className, b.getAttribute('aria-pressed')]).concat([document.getElementById('irises').className, __T.myLook.eyes])"))
            await pg.screenshot(path=f'{WS}/ui/zombie_{tag}_eyes.png')
            if tag == 'locked':
                await pg.evaluate("document.querySelector('#eyeStyles .eyes[data-es=\"zombie\"]').click()"); await pg.wait_for_timeout(400)
                print(tag, 'tap locked', await pg.evaluate("[document.getElementById('lookNote').textContent, __T.myLook.eyes]"))
                await pg.evaluate("document.getElementById('lkBal').click()"); await pg.wait_for_timeout(900)
                print(tag, 'shop', await pg.evaluate("[...document.querySelectorAll('#shopGrid .shcat, #shopGrid .shitem')].map(t => t.textContent.trim().slice(0, 40))"))
                await pg.screenshot(path=f'{WS}/ui/zombie_{tag}_shop.png')
                await pg.evaluate("document.querySelector('#shopGrid .shitem[data-w=\"zombie\"]').click()"); await pg.wait_for_timeout(500)
                print(tag, 'bought', await pg.evaluate("[__T.store.drops, document.getElementById('shopNote').textContent, JSON.stringify(__T.store.bought)]"))
                await pg.evaluate("document.getElementById('shopBack').click()"); await pg.wait_for_timeout(800)
                await pg.evaluate("document.querySelector('#eyeStyles .eyes[data-es=\"zombie\"]').click()"); await pg.wait_for_timeout(2500)
                print(tag, 'picked', await pg.evaluate("[__T.myLook.eyes, document.getElementById('irises').className, document.querySelector('#lc-eyes b').textContent]"))
                await pg.screenshot(path=f'{WS}/ui/zombie_{tag}_picked.png')
            else:
                await pg.wait_for_timeout(2000); await pg.screenshot(path=f'{WS}/ui/zombie_{tag}_face.png')
                # a closer look: crop the upper half at full scale
                await pg.screenshot(path=f'{WS}/ui/zombie_{tag}_close.png', clip={'x': 60, 'y': 120, 'width': 270, 'height': 270})
            print(tag, 'errors', errs[:5]); await ctx.close()
        await b.close()
asyncio.run(run())
