import asyncio, base64, io
from playwright.async_api import async_playwright
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for f in ('stand', 'crawl'):
            pg = await b.new_page(viewport={'width': 900, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/axo/debug.html?f=' + f, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
            ims = []
            for v in ('front', 'side', 'top'):
                d = await pg.evaluate(f"shot('{v}')"); ims.append(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB').resize((600, 600)))
            sh = Image.new('RGB', (1812, 600), (255, 255, 255)); [sh.paste(im, (i * 606, 0)) for i, im in enumerate(ims)]; sh.save(D + f'dbg_{f}.jpg', quality=88); print(f, 'errors', errs[:2])
            await pg.close()
        await b.close()
asyncio.run(main())
