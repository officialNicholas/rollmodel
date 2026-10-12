"""Hats on the new head, each shot after the pop-in has settled. usage: hats239.py [page] [tag]"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
HATS = ['hat', 'tophat', 'pirate', 'tiara', 'bunny', 'skull', 'halo']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 800}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 2000, runs: 3, owned: ['hat','tophat','pirate','tiara','bunny','skull','halo'], bought: [], tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
        await pg.wait_for_timeout(2500); await ev("__T.openLook()"); await pg.wait_for_timeout(9000)
        fs = []
        for h in HATS:
            await ev("(h) => { __T.myLook.head = h; __T.renderLook(); }", h); await pg.wait_for_timeout(4000)
            fn = f'{WS}/ui/hat_{TAG}_{h}.png'; await pg.screenshot(path=fn, clip={'x': 0, 'y': 60, 'width': 390, 'height': 400}); fs.append(fn)
        print('errors', errs[:3]); await b.close()
    ims = [Image.open(f) for f in fs]; w, h = ims[0].size; sh = Image.new('RGB', (w * len(ims), h), 'white'); [sh.paste(im, (i * w, 0)) for i, im in enumerate(ims)]; sh.save(f'{WS}/ui/hat_{TAG}_sheet.png')
asyncio.run(main())
