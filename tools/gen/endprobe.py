import asyncio, json, time
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 760})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(500)
        fps = "new Promise(r => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < 3000) requestAnimationFrame(f); else r([n, (performance.now() - t0) | 0]); }; requestAnimationFrame(f); })"
        print('menu frames/3s', await pg.evaluate(fps))
        await pg.evaluate("(() => { __T.start(); })()"); await pg.wait_for_timeout(1500)
        print('play frames/3s', await pg.evaluate(fps), await pg.evaluate("[__T.renderer.info.render.calls, __T.renderer.info.render.triangles]"))
        await pg.evaluate("__T.matchLeft = 0.05")
        t0 = time.time()
        await pg.wait_for_function("!document.getElementById('end').hidden", polling=250, timeout=240000)
        print('end shown after', round(time.time() - t0, 1), 's')
        await pg.wait_for_timeout(1500)
        print('end frames/3s', await pg.evaluate(fps), await pg.evaluate("[__T.renderer.info.render.calls, __T.renderer.info.render.triangles, __T.state]"))
        print(errs[:3]); await b.close()
asyncio.run(main())
