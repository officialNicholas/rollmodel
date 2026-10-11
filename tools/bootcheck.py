import asyncio, sys
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=3, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 5, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:400])); pg.on('console', lambda m: errs.append('CONSOLE ' + m.type + ' ' + m.text[:300]) if m.type in ('error', 'warning') else None)
        await pg.goto('http://localhost:8765/' + sys.argv[1], timeout=300000)
        for i in range(40):
            await pg.wait_for_timeout(5000)
            ok = await pg.evaluate("[typeof __T, typeof window.__tp, document.getElementById('boot') && document.getElementById('boot').className]")
            if ok[0] == 'object' or errs: break
        print(ok); print('\n'.join(errs[:12]))
        await b.close()
asyncio.run(main())
