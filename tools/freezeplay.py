import asyncio, sys, time
from playwright.async_api import async_playwright
async def main(mode, diff, secs):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{}, mode:'" + mode + "', runs: 3, stage:'island', diff:'" + diff + "' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:600])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and 'CORS' not in m.text and errs.append('console: ' + m.text[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300)
        print('mode', await pg.evaluate("[__T.mode, __T.ACTIVE.length, __T.diff]"))
        await pg.evaluate("window.__fr = 0; (function tick() { window.__fr++; requestAnimationFrame(tick); })()")
        t0 = time.time(); i = 0; lastFr = 0
        while time.time() - t0 < secs:
            i += 1
            key = 'ArrowLeft' if (i // 3) % 2 == 0 else 'ArrowRight'
            await pg.keyboard.down(key); await pg.wait_for_timeout(350); await pg.keyboard.up(key)
            if i % 4 == 0: await pg.keyboard.press('Space')
            if i % 6 == 0: await pg.keyboard.press('Shift')
            if i % 7 == 0: await pg.keyboard.down('s'); await pg.wait_for_timeout(700); await pg.keyboard.up('s')
            if i % 5 == 0: await pg.keyboard.press('e')
            if i % 9 == 0: await pg.keyboard.press('f')
            if i % 8 == 0:
                try:
                    r = await asyncio.wait_for(pg.evaluate("[+__T.runT.toFixed(1), __T.state, __T.P.st, __T.P.air, !!__T.P.slam, __T.P.held, !!__T.P.rocket, __T.orb.on, __T.wx, window.__fr]"), timeout=8)
                    print(round(time.time() - t0), r, 'frames+', r[9] - lastFr)
                    if r[9] == lastFr and i > 16: print('NO FRAMES'); break
                    lastFr = r[9]
                    if errs: break
                    if r[1] != 'play': break
                except asyncio.TimeoutError: print('HUNG'); break
        print('errors', errs[:6]); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'trio', sys.argv[2] if len(sys.argv) > 2 else 'medium', int(sys.argv[3]) if len(sys.argv) > 3 else 240))
