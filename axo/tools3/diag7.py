# v7 successor of axo2/diag_final.py: each preview loads (window.ready) with no page errors (python3 -I diag7.py URL...)
import asyncio, sys
from playwright.async_api import async_playwright
async def main(urls):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for url in urls:
            pg = await b.new_page(viewport={'width': 300, 'height': 300}); errs = []
            pg.on('pageerror', lambda e, errs=errs: errs.append('pageerror: ' + str(e)[:300])); pg.on('console', lambda m, errs=errs: m.type == 'error' and errs.append('console error: ' + m.text[:300]))
            await pg.goto(url, timeout=300000)
            try: await pg.wait_for_function('window.ready', timeout=300000); ok = 'ready'
            except Exception as e: ok = 'NOT READY ' + str(e)[:100]
            print(url, ok, 'errors:', errs[:5] or 'none'); await pg.close()
        await b.close()
asyncio.run(main(sys.argv[1:]))
