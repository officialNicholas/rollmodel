# The ear spring compared: the ears after a stop from a run and after a landing, filmed every few frames, under the animator's present
# gill spring (k 110, c 7.5, set by axolife.js) and looser ones for floppy ears. The spring's k and c are set on the animator after its
# first step (axolife sets them once, then leaves them). usage: springtest.py [lab dir = lab]
import asyncio, sys, io, base64
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
LAB = sys.argv[1] if len(sys.argv) > 1 else 'lab'
SPRINGS = [('present k110 c7.5', 110, 7.5), ('proposed k75 c5', 75, 5.0), ('loose k55 c4', 55, 4.0)]
try: FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except Exception: FONT = None
CAM = "{ const D = LAB.D, h = LAB.feet().head, sy = Math.sin(D.yaw), cy = Math.cos(D.yaw); LAB.cam = 'fixed'; LAB.camPos = [h[0] + 1.6 * cy, h[1] + 0.25, h[2] - 1.6 * sy]; LAB.camAt = [h[0], h[1] - 0.05, h[2] - 0.1]; LAB.render(); }"
async def main():
    W, H = 300, 260; rows = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(f'http://localhost:8767/fable3/{LAB}/index.html', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate("document.getElementById('hud').style.display = 'none'")
        for name, k, c in SPRINGS:
            for scen, setup, every in [('stop from a run', "LAB.set('walk', {v: 5.4}); LAB.step(80); LAB.set('idle');", 4), ('landing', "LAB.set('jump', {v: 3, at: 0.3}); LAB.step(28); while (LAB.D.air) LAB.step(1);", 3)]:
                await pg.evaluate(f"LAB.D.x = 0; LAB.D.z = 0; LAB.D.y = 0; LAB.D.air = false; LAB.D.dry = true; LAB.set('idle'); LAB.step(5); LAB.I.ax.A.gillSpring.k = {k}; LAB.I.ax.A.gillSpring.c = {c}; LAB.step(60); {setup}")
                ims = []
                for i in range(8):
                    await pg.evaluate(f"LAB.step({every if i else 0}); " + CAM); ims.append(Image.open(io.BytesIO(await pg.screenshot())).convert('RGB'))
                rows.append((f'{name}: {scen}, every {every} frames', ims))
        await b.close()
    sh = Image.new('RGB', (8 * W, len(rows) * (H + 18)), 'white'); d = ImageDraw.Draw(sh)
    for r, (lab, ims) in enumerate(rows):
        d.text((6, r * (H + 18) + 2), lab, fill=(10, 10, 10), font=FONT)
        for i, im in enumerate(ims): sh.paste(im, (i * W, r * (H + 18) + 18))
    sh.save(f'{S}/fable3/shots/springs.jpg', quality=86); print('ok', errs[:2])
asyncio.run(main())
