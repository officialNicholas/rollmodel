"""v192: the menu song starts on its downbeat (past the lone bell)."""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 3, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        await pg.mouse.click(200, 400)
        await pg.wait_for_function("__T.AU.beat()", timeout=60000, polling=20)
        print('song position at first sight (s)', await pg.evaluate("__T.AU.beat().t.toFixed(3)")); await b.close()
asyncio.run(main())
