import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 300}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:500])); pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]))
        await pg.goto('http://localhost:8765/axo/preview.html?manual', timeout=60000)
        try: await pg.wait_for_function('window.ready', timeout=45000); print('ready')
        except Exception as e: print('not ready:', str(e)[:100])
        print('\n'.join(errs[:10])); await b.close()
asyncio.run(main())
