# The ears' sideways and fore-aft response, filmed: a weave (turns both ways) from the front and from above, a stop from a run from the
# side, a sideways lurch (a turn on the spot), every few frames. usage: lateral.py [lab dir = lab] [out name = lateral]
import asyncio, sys, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
LAB = sys.argv[1] if len(sys.argv) > 1 else 'lab'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'lateral'
try: FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except Exception: FONT = None
def cam(off, at): return (f"{{ const D = LAB.D, h = LAB.feet().head, sy = Math.sin(D.yaw), cy = Math.cos(D.yaw), o = {off}, a = {at}; LAB.cam = 'fixed'; "
                          "LAB.camPos = [h[0] + o[0] * cy + o[2] * sy, h[1] + o[1], h[2] - o[0] * sy + o[2] * cy]; LAB.camAt = [h[0] + a[0] * cy + a[2] * sy, h[1] + a[1], h[2] - a[0] * sy + a[2] * cy]; LAB.render(); }")
RUNS = [('weave, from the front (turning both ways)', "LAB.set('weave', {v: 5.4, k: 0.9, T: 1.4}); LAB.step(60);", 7, cam([0, 0.2, 1.7], [0, -0.05, 0])),
        ('weave, from above', "LAB.set('weave', {v: 5.4, k: 0.9, T: 1.4}); LAB.step(60);", 7, cam([0, 2.0, 0.3], [0, 0, 0])),
        ('spin on the spot, from the front', "LAB.set('spin', {k: 0.8}); LAB.step(10);", 4, cam([0, 0.2, 1.7], [0, -0.05, 0])),
        ('stop from a run, from the side', "LAB.set('walk', {v: 5.4}); LAB.step(80); LAB.set('idle');", 4, cam([1.6, 0.25, 0], [0, -0.05, -0.1])),
        ('start of a run, from the side', "LAB.set('idle'); LAB.step(60); LAB.set('walk', {v: 5.4});", 4, cam([1.6, 0.25, 0], [0, -0.05, -0.1]))]
async def main():
    W, H = 300, 260; rows = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(f'http://localhost:8767/fable3/{LAB}/index.html', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate("document.getElementById('hud').style.display = 'none'")
        for name, setup, every, c in RUNS:
            await pg.evaluate(f"LAB.D.x = 0; LAB.D.z = 0; LAB.D.y = 0; LAB.D.air = false; LAB.D.dry = true; LAB.D.yaw = 0; LAB.set('idle'); LAB.step(40); {setup}")
            ims = []
            for i in range(8):
                await pg.evaluate(f"LAB.step({every if i else 0}); " + c); ims.append(Image.open(io.BytesIO(await pg.screenshot())).convert('RGB'))
            rows.append((f'{name}, every {every} frames', ims))
        await b.close()
    sh = Image.new('RGB', (8 * W, len(rows) * (H + 18)), 'white'); d = ImageDraw.Draw(sh)
    for r, (lab, ims) in enumerate(rows):
        d.text((6, r * (H + 18) + 2), lab, fill=(10, 10, 10), font=FONT)
        for i, im in enumerate(ims): sh.paste(im, (i * W, r * (H + 18) + 18))
    sh.save(f'{S}/fable3/shots/{OUT}.jpg', quality=86); print('ok', errs[:2])
asyncio.run(main())
