# evaluate JS expressions in a page (after ready); prints JSON results
import asyncio, sys, json
from playwright.async_api import async_playwright
async def main(url, exprs):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type in ('error', 'warning') and errs.append(m.text[:300]))
        await pg.goto(url, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        for e in exprs:
            try: r = await pg.evaluate(e); print(json.dumps(r) if not isinstance(r, str) else r)
            except Exception as ex: print('ERR', str(ex)[:500])
        await b.close(); print('page errors:', errs[:5])
if __name__ == '__main__': asyncio.run(main(sys.argv[1], sys.argv[2:]))
