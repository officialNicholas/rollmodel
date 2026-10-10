import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000, wait_until='commit')
        for i, ms in enumerate([900, 2500, 5000]):
            await pg.wait_for_timeout(ms); await pg.screenshot(path=f'{WS}/ui/boot_{i}.png'); print(i, await pg.evaluate("[document.getElementById('boot') && document.getElementById('boot').className, window.__bootP, document.getElementById('bootMsg') && document.getElementById('bootMsg').textContent]"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
