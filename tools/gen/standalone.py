import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        await pg.goto('file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/out_test.html'); await pg.wait_for_timeout(5000)
        print(await pg.evaluate("[document.compatMode, document.title, document.getElementById('boot').className, !document.getElementById('menu').hidden, document.fonts.check('30px \"Bowlby One\"')]"), errs[:4])
        await pg.screenshot(path='ui/standalone.png'); await b.close()
asyncio.run(main())
