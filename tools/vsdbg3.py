import asyncio, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','lashes'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: print('PAGEERROR', str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(3000)
        fps = "(() => new Promise(ok => { let n = 0; const t0 = performance.now(), c0 = __T.clock; const f = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else ok([+(n / 2).toFixed(1), +(__T.clock - c0).toFixed(2), __T.renderer.getContext().isContextLost(), __T.state]); }; requestAnimationFrame(f); }))()"
        print(PAGE, 'menu fps/clock/lost/state', await pg.evaluate(fps))
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("__T.state === 'play'", timeout=90000)
        print(PAGE, 'play fps/clock/lost/state', await pg.evaluate(fps))
        print(PAGE, 'play again', await pg.evaluate(fps))
        await b.close()
asyncio.run(main())
