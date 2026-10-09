# the drum kit should be made in the menu, before any tap; then starting the audio should cost nothing big
import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(SP + 'pc_kit.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.wait_for_timeout(8000)
        before = await pg.evaluate("(window.__kit || []).length")
        t = await pg.evaluate("() => { const t0 = performance.now(); __T.AU.init(); return performance.now() - t0; }")
        await pg.wait_for_timeout(3000)
        k = await pg.evaluate("window.__kit || []")
        print('jobs done before any tap:', before, 'of', len(k), '| AU.init took %.1f ms' % t, '| errors', errs[:3])
        await b.close()
asyncio.run(main())
