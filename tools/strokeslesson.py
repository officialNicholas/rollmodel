"""Ol' Bloop's Strokes lesson: rank 3, first lessons done: the praise card, the second card, then the page with its tips through the craft,
the skip and the equip. usage: strokeslesson.py <page> <tag>"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ look: 1 }, drops: 120, runs: 9, xp: 900, owned: [], tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(5000)
        fs = []; shot = lambda n: f'{WS}/ui/sl_{TAG}_{n}.png'
        f = shot('1praise'); await pg.screenshot(path=f); fs.append(f); print('card', await ev("document.getElementById('tutGo').hidden + ' ' + document.getElementById('tgTitle').textContent"))
        await ev("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(900)
        f = shot('2learn'); await pg.screenshot(path=f); fs.append(f)
        await ev("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(2200)
        f = shot('3giant'); await pg.screenshot(path=f); fs.append(f); print('tip', await ev("document.getElementById('tutText').textContent"))
        await ev("document.querySelector('#stSpecialRail .stopt[data-st=\"giant\"]').click()"); await pg.wait_for_timeout(1500)
        f = shot('4skip'); await pg.screenshot(path=f); fs.append(f); print('tip', await ev("document.getElementById('tutText').textContent"))
        await ev("document.getElementById('stSkip').click()"); await pg.wait_for_timeout(1500)
        f = shot('5equip'); await pg.screenshot(path=f); fs.append(f); print('tip', await ev("document.getElementById('tutText').textContent"))
        await ev("document.querySelector('#stSpecialRail .stopt[data-st=\"giant\"]').click()"); await pg.wait_for_timeout(1500)
        f = shot('6done'); await pg.screenshot(path=f); fs.append(f); print('tip', await ev("document.getElementById('tutText').textContent"))
        await pg.wait_for_timeout(6000); print('after', await ev("JSON.stringify(JSON.parse(localStorage.getItem('paint-world-red.v1')).tut) + ' tip hidden ' + document.getElementById('tut').hidden"))
        print('errors', errs[:3]); await b.close()
    ims = [Image.open(f) for f in fs]; H = max(im.height for im in ims); sh = Image.new('RGB', (sum(im.width for im in ims) + 10 * len(ims), H), 'white'); x = 0
    for im in ims: sh.paste(im, (x, 0)); x += im.width + 10
    sh.resize((sh.width * 3 // 4, sh.height * 3 // 4)).save(f'{WS}/ui/sl_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
