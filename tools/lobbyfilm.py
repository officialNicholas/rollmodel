"""The lobby idle filmed: the character crop every 0.25 s for a few seconds, as a strip. usage: lobbyfilm.py <page> <tag> [seconds]"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]; SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 8
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 20, runs: 3, owned: [], tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(5000)
        fs = []; n = int(SECS * 4)
        for i in range(n):
            fn = f'{WS}/ui/lf_{TAG}_{i:02d}.png'; await pg.screenshot(path=fn, clip={'x': 70, 'y': 520, 'width': 250, 'height': 200}); fs.append(fn); await pg.wait_for_timeout(250)
        print('acts', await ev("(() => { try { return __T.idle ? __T.idle.act : 'n/a'; } catch (e) { return 'n/a'; } })()")); await b.close()
    ims = [Image.open(f) for f in fs]; w, h = ims[0].size; cols = 8; rows = (len(ims) + cols - 1) // cols; sh = Image.new('RGB', (w * cols, h * rows), 'white')
    for i, im in enumerate(ims): sh.paste(im, ((i % cols) * w, (i // cols) * h))
    sh.save(f'{WS}/ui/lf_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
