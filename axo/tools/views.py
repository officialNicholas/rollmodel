import asyncio, base64, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 1200, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/axo/view.html?f=stand,crawl', timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        import math
        for fi, nm in ((0, 'stand'), (1, 'crawl')):
            for vn, yaw, pitch in (('front', 0, 0.1), ('side', math.pi / 2, 0.1), ('back', math.pi, 0.15), ('top', 0, 1.45), ('q34', 0.7, 0.35)):
                d = await pg.evaluate(f"shot({fi}, {yaw}, {pitch})"); open(OUT + f'{nm}_{vn}.png', 'wb').write(base64.b64decode(d.split(',')[1]))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
