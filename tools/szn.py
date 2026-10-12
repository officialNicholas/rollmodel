"""Where the season's name shows: the lobby tag and logo, the canvases page, the shop banner, the locker wall sign. usage: szn.py <page> <tag>"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ look: 1 }, drops: 500, runs: 3, owned: [], tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(5000)
        fs = []
        f = f'{WS}/ui/szn_{TAG}_lobby.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': 390, 'height': 300}); fs.append(f)
        await ev("(() => { const b = document.getElementById('worldsBtn') || document.querySelector('[data-page=\"worlds\"]'); if (b) b.click(); })()"); await pg.wait_for_timeout(1500)
        f = f'{WS}/ui/szn_{TAG}_worlds.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': 390, 'height': 420}); fs.append(f)
        await ev("(() => { const b = document.getElementById('worldBack'); if (b) b.click(); })()"); await pg.wait_for_timeout(800)
        await ev("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(2500)
        f = f'{WS}/ui/szn_{TAG}_shop.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': 390, 'height': 420}); fs.append(f)
        await ev("(() => { const b = document.getElementById('shopBack'); if (b) b.click(); })()"); await pg.wait_for_timeout(800)
        await ev("__T.openLook(); __T.lookSpinTo && __T.lookSpinTo(0);"); await pg.wait_for_timeout(5000)
        await pg.mouse.move(195, 400); await pg.mouse.down(); await pg.mouse.move(60, 400, steps=12); await pg.mouse.up(); await pg.wait_for_timeout(1500)
        f = f'{WS}/ui/szn_{TAG}_locker.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': 60, 'width': 390, 'height': 520}); fs.append(f)
        print('errors', errs[:3]); await b.close()
    ims = [Image.open(f) for f in fs]; H = max(im.height for im in ims); sh = Image.new('RGB', (sum(im.width for im in ims) + 30, H), 'white'); x = 0
    for im in ims: sh.paste(im, (x, 0)); x += im.width + 10
    sh.save(f'{WS}/ui/szn_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
