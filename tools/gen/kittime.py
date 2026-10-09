import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1)
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_kit.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("window.__noLoop = true; __T.AU.init()")
        await pg.wait_for_timeout(15000)
        k = await pg.evaluate("window.__kit || []")
        print(len(k), 'jobs; ms each:', k, 'max', max(k) if k else 0, 'total', round(sum(k)))
        await b.close()
asyncio.run(main())
