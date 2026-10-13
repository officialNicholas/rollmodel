import asyncio
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 195, 'height': 422}, device_scale_factor=3, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'sewer', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        q = lambda: pg.evaluate("(() => { const x = __q(); return [x.lvl, x.n, x.pr, x.state, JSON.stringify(__T.store.qSt || null)]; })()")
        feed = lambda ft, n: pg.evaluate(f"(() => {{ for (let i = 0; i < {n}; i++) __tp({ft}); }})()")
        print('ladder', await pg.evaluate("__q().lad.map(l => [l.pr, l.sh, l.bloom ? 'b' : '', l.dof ? 'd' : '', l.grab ? 'g' : ''].join(''))"))
        await pg.evaluate("window.__tpManual = true; window.__fixedPR = false")
        print('menu start', await q())
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        print('play start', await q())
        await feed(0.0167, 70); await feed(0.03, 200); print('after 200 late frames in play', await q())
        await feed(0.0167, 900); print('after 900 clean frames in play (no step up expected)', await q())
        await pg.evaluate("__T.ev(\"state = 'dead'; qMatchEnd();\")"); print('match end (stepped down: memory kept)', await q())
        await pg.evaluate("__T.ev(\"state = 'menu';\")"); await feed(0.0167, 70); await feed(0.0167, 700); print('menu after 700 clean frames (steps up allowed)', await q())
        await pg.evaluate("__T.ev(\"state = 'intro'; qMatchStart();\")"); print('next match intro (back to the sewer notch)', await q())
        await pg.evaluate("__T.ev(\"state = 'play';\")"); await feed(0.0167, 900); await pg.evaluate("__T.ev(\"state = 'dead'; qMatchEnd();\")"); print('clean match end (memory eases one notch)', await q())
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
