import asyncio, sys, time
from playwright.async_api import async_playwright
async def main(kind, secs):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        tut = kind == 'tut'
        await ctx.add_init_script("window.__tut = " + ('true' if tut else 'false') + "; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, mode:'trio', runs: " + ('0' if tut else '3') + ", stage:'island', diff:'medium' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append((str(e) + ' | ' + str(getattr(e, 'stack', ''))[:500])[:900])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and 'CORS' not in m.text and errs.append('console: ' + m.text[:300]))
        cdp = await ctx.new_cdp_session(pg)
        async def touch(seq):  # seq: list of (type, x, y, holdMs)
            for typ, x, y, ms in seq:
                await cdp.send('Input.dispatchTouchEvent', { 'type': typ, 'touchPoints': [] if typ == 'touchEnd' else [{ 'x': x, 'y': y, 'id': 1 }] })
                if ms: await pg.wait_for_timeout(ms)
        async def drag(x0, y0, x1, y1, steps=8, hold=40, end=True):
            await touch([('touchStart', x0, y0, 30)])
            for i in range(1, steps + 1): await touch([('touchMove', x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, hold)])
            if end: await touch([('touchEnd', 0, 0, 30)])
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300)
        print('mode', await pg.evaluate("[__T.mode, __T.ACTIVE.length, __T.diff, __T.tutPh(), !!__T.tut]"))
        await pg.evaluate("window.__fr = 0; (function tick() { window.__fr++; requestAnimationFrame(tick); })()")
        t0 = time.time(); i = 0; lastFr = -1
        while time.time() - t0 < secs:
            i += 1; cx, cy = 195, 520
            k = i % 9
            if k in (0, 1, 2): await drag(cx, cy, cx + (90 if k != 1 else -90), cy, steps=6, hold=60)        # steer drags
            elif k == 3: await touch([('touchStart', cx, cy, 40), ('touchEnd', 0, 0, 40)])                     # tap: jump
            elif k == 4: await drag(cx, cy, cx, cy - 110, steps=4, hold=25)                                      # swipe up: roll
            elif k == 5: await touch([('touchStart', cx, cy, 500)]); await drag(cx, cy, cx, cy + 90, steps=5, hold=120)  # hold, pull, release: fling
            elif k == 6: await drag(cx, cy, cx, cy + 120, steps=4, hold=25)                                      # swipe down
            elif k == 7: await pg.evaluate("const b = document.getElementById('slamBtn'); if (!b.hidden) b.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerType: 'touch' }))"); await pg.wait_for_timeout(60); await pg.evaluate("const b = document.getElementById('slamBtn'); if (!b.hidden) { b.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerType: 'touch' })); b.click(); }")
            else: await pg.evaluate("const b = document.getElementById('itemBtn'); if (!b.hidden) b.click()")
            if i % 6 == 0:
                try:
                    r = await asyncio.wait_for(pg.evaluate("[+__T.runT.toFixed(1), __T.state, __T.P.st, __T.P.air, !!__T.P.slam, __T.P.held, !!__T.P.rocket, __T.tut && __T.tut.step, __T.tutTip && __T.tutTip.key, window.__fr]"), timeout=8)
                    print(round(time.time() - t0), r, 'frames+', r[9] - lastFr if lastFr >= 0 else r[9])
                    if lastFr >= 0 and r[9] == lastFr: print('NO FRAMES'); break
                    lastFr = r[9]
                    if errs or r[1] != 'play': break
                except asyncio.TimeoutError: print('HUNG'); break
        print('errors', errs[:4]); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'tut', int(sys.argv[2]) if len(sys.argv) > 2 else 300))
