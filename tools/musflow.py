import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat'], bought:['hat'] })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2000)
        # log every music() and say() call with a timestamp
        await pg.evaluate("""(() => { const A = __T.AU; window.__log = []; const t0 = performance.now(); for (const k of ['music', 'say']) { const f = A[k]; A[k] = (...a) => { if (k !== 'say' || a[1] !== 0) __log.push([k, a[0], Math.round(performance.now() - t0)]); return f.apply(A, a); }; } })()""")
        await pg.tap('#homePlay')
        await pg.wait_for_function("__T.state === 'play'", timeout=120000)
        await pg.wait_for_timeout(500)
        print(await pg.evaluate("__log")); print('errors', errs[:3]); await b.close()
asyncio.run(main())
