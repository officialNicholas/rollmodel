import asyncio, base64, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
# axes per view: (screen x axis label, screen y axis label); world range [-1,1] maps to 0..1000 px
AX = {'front': ('x', 'y'), 'side': ('-z', 'y'), 'top': ('x', '-z')}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for f in ('stand', 'crawl'):
            pg = await b.new_page(viewport={'width': 1000, 'height': 1000}); await pg.goto('http://localhost:8765/axo/ortho.html?f=' + f, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
            for v in ('front', 'side', 'top'):
                d = await pg.evaluate(f"shot('{v}')"); im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'); g = ImageDraw.Draw(im)
                for k in range(-10, 11):
                    t = int((k / 10 + 1) * 500); col = (60, 60, 200) if k == 0 else (200, 200, 220)
                    g.line([(t, 0), (t, 999)], fill=col, width=1); g.line([(0, t), (999, t)], fill=col, width=1)
                    g.text((t + 2, 2), f'{k/10:.1f}', fill=(40, 40, 120)); g.text((2, t + 2), f'{-k/10:.1f}', fill=(40, 40, 120))
                g.text((900, 980), f'{f} {v}: x={AX[v][0]} y={AX[v][1]}', fill=(0, 0, 0)); im.save(D + f'o_{f}_{v}.png')
            await pg.close()
        await b.close()
asyncio.run(main())
