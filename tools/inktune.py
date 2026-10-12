"""The axolotl's ink line at a few widths (window.__axoInk = [per-distance, min, max] in mesh metres): the lobby and the locker close-up for
each. usage: inktune.py <page> <tag> '<json list of triples>'"""
import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]; SETS = json.loads(sys.argv[3])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist']); fs = []
        for k, ink in enumerate(SETS):
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 20, runs: 3, owned: [], tut: { ph: 'done' } })); } catch (e) {} window.__axoInk = " + json.dumps(ink) + ";")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
            await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(6000)
            f1 = f'{WS}/ui/ink_{TAG}_{k}_lobby.png'; await pg.screenshot(path=f1, clip={'x': 40, 'y': 480, 'width': 310, 'height': 250})
            await ev("__T.openLook()"); await pg.wait_for_timeout(7000)
            f2 = f'{WS}/ui/ink_{TAG}_{k}_locker.png'; await pg.screenshot(path=f2, clip={'x': 40, 'y': 90, 'width': 310, 'height': 330})
            fs.append((f1, f2)); print(k, ink, 'errors', errs[:2]); await ctx.close()
        await b.close()
    cols = [Image.open(a) for a, _ in fs]; rows = [Image.open(c) for _, c in fs]; w = 310; sh = Image.new('RGB', (w * len(fs), 250 + 330), 'white')
    for i, (a, c) in enumerate(zip(cols, rows)): sh.paste(a, (i * w, 0)); sh.paste(c, (i * w, 250))
    sh.save(f'{WS}/ui/ink_{TAG}_sheet.png')
asyncio.run(main())
