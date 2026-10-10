import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, is_mobile=True)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/boot_only.html'); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/boot_only_a.png')
        await pg.evaluate("window.__bootP = 0.95"); await pg.wait_for_timeout(1800); await pg.screenshot(path=f'{WS}/ui/boot_only_b.png'); print('errors', errs); await b.close()
asyncio.run(main())
