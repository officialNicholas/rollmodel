import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['flower','pirate'], bought:[], drops:200 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(3000); await pg.screenshot(path=f'{WS}/ui/price_head.png')
        print(await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile')].map(t => t.getAttribute('aria-label'))"))
        await pg.evaluate("document.querySelectorAll('#lookCats .lcat')[1].click()"); await pg.wait_for_timeout(600); print(await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile')].map(t => t.getAttribute('aria-label'))"))
        await pg.evaluate("document.querySelectorAll('#lookCats .lcat')[2].click()"); await pg.wait_for_timeout(600); print(await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile')].map(t => t.getAttribute('aria-label'))"))
        print('errors', errs[:2]); await b.close()
asyncio.run(main())
