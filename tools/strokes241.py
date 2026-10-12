"""The Strokes page: open at rank 3, craft the Giant, skip, equip; a shot of each state. usage: strokes241.py <page> <tag>"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ look: 1 }, drops: 120, runs: 9, xp: 900, owned: [], tut: { ph: 'done', strokes: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(4000)
        print('rank', await ev("document.getElementById('abilTag').textContent + ' / ' + document.getElementById('abilBtn').className"))
        fs = []
        f = f'{WS}/ui/st_{TAG}_0lobby.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': 390, 'height': 330}); fs.append(f)
        await ev("document.getElementById('abilBtn').click()"); await pg.wait_for_timeout(1500)
        f = f'{WS}/ui/st_{TAG}_1page.png'; await pg.screenshot(path=f); fs.append(f)
        await ev("document.querySelector('#stSpecialRail .stopt[data-st=\"giant\"]').click()"); await pg.wait_for_timeout(1500)
        f = f'{WS}/ui/st_{TAG}_2craft.png'; await pg.screenshot(path=f); fs.append(f)
        await ev("document.getElementById('stSkip').click()"); await pg.wait_for_timeout(1200)
        f = f'{WS}/ui/st_{TAG}_3ready.png'; await pg.screenshot(path=f); fs.append(f)
        await ev("document.querySelector('#stSpecialRail .stopt[data-st=\"giant\"]').click()"); await pg.wait_for_timeout(1200)
        f = f'{WS}/ui/st_{TAG}_4equip.png'; await pg.screenshot(path=f); fs.append(f)
        print('store', await ev("JSON.stringify(JSON.parse(localStorage.getItem('paint-world-red.v1')).strokes)"))
        await ev("document.getElementById('stBack').click()"); await pg.wait_for_timeout(1000)
        f = f'{WS}/ui/st_{TAG}_5back.png'; await pg.screenshot(path=f, clip={'x': 0, 'y': 0, 'width': 390, 'height': 330}); fs.append(f)
        print('errors', errs[:3]); await b.close()
    ims = [Image.open(f) for f in fs]; H = max(im.height for im in ims); sh = Image.new('RGB', (sum(im.width for im in ims) + 10 * len(ims), H), 'white'); x = 0
    for im in ims: sh.paste(im, (x, 0)); x += im.width + 10
    sh.save(f'{WS}/ui/st_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
