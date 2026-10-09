import asyncio, time
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("document.getElementById('vvote').classList.contains('ticking')", timeout=30000); t0 = time.time()
        await pg.wait_for_function("document.getElementById('vvote').classList.contains('done')", timeout=30000); t1 = time.time()
        print('vote open for %.1f s (wall clock, slow renderer)' % (t1 - t0), await pg.evaluate("getComputedStyle(document.querySelector('.vvote.ticking .vtimer i')).transitionDuration")); await b.close()
asyncio.run(main())
