import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 390, 'height': 780}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8790/index.html'); await pg.wait_for_function('window.ready', timeout=240000); await pg.wait_for_timeout(4000)
        await pg.screenshot(path=sys.argv[1]); print('ready, errors:', errs); await b.close()
asyncio.run(main())
