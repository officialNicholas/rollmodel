import asyncio, sys, time
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 390, 'height': 700}); errs = []
        pg.on('pageerror', lambda e: errs.append('PE ' + str(e)[:300])); pg.on('console', lambda m: errs.append('C ' + m.text[:200]) if m.type == 'error' else None)
        t0 = time.time(); await pg.goto('http://localhost:8765/' + sys.argv[1], timeout=240000)
        for k in range(40):
            ok = await pg.evaluate('typeof __T === "object"')
            if ok: break
            await pg.wait_for_timeout(3000)
        print(sys.argv[1], 'booted' if ok else 'NOT booted', round(time.time() - t0, 1), 's', errs[:5]); await b.close()
asyncio.run(main())
