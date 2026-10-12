"""The lab: the axolotl put in a state (victory, idle stand...) and shot from a few fixed cameras. usage: labstand.py <state> <tag>"""
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
ST, TAG = sys.argv[1], sys.argv[2]
CAMS = [([0, 1.0, 3.2], [0, 0.95, 0]), ([2.4, 1.1, 2.2], [0, 0.95, 0]), ([3.2, 1.0, 0.0], [0, 0.95, 0])]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 360, 'height': 420}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/lab/index.html?v=' + str(os.getpid()), timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate("(() => { const h = document.getElementById('hud'); if (h) h.style.display = 'none'; })()")
        await pg.evaluate(f"LAB.cam = 'fixed'; LAB.set('idle'); LAB.step(30); LAB.I.ax.A.set('{ST}'); LAB.step(150)")
        fs = []
        for i, (pos, at) in enumerate(CAMS):
            await pg.evaluate(f"LAB.step(1); LAB.camPos = {pos}; LAB.camAt = {at}; LAB.render()"); fn = f'{S}/lab/{TAG}_{i}.png'; await pg.screenshot(path=fn); fs.append(fn)
        print('state', await pg.evaluate("LAB.I.ax.A.state + ' ' + LAB.I.ax.A.mesh"), 'errors', errs[:3]); await b.close()
    ims = [Image.open(f) for f in fs]; w, h = ims[0].size; sh = Image.new('RGB', (w * len(ims), h), 'white'); [sh.paste(im, (i * w, 0)) for i, im in enumerate(ims)]; sh.save(f'{S}/lab/{TAG}_sheet.png')
asyncio.run(main())
