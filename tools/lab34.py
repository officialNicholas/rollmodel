"""The lab with a camera following the axolotl at a fixed offset (a 3/4 view, or any): a sheet of frames.
usage: lab34.py <scen> '<json>' <frames> <every> <tag> [warm] [offx offy offz] [atdz]"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SC, OPT, N, EVERY, TAG = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
WARM = int(sys.argv[6]) if len(sys.argv) > 6 else 150
OFF = [float(x) for x in sys.argv[7:10]] if len(sys.argv) > 9 else [1.9, 1.1, 2.3]
ATDZ = float(sys.argv[10]) if len(sys.argv) > 10 else -0.4
W, H = int(os.environ.get('LW', 420)), int(os.environ.get('LH', 300))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/lab/index.html?v=' + str(os.getpid()), timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate(f"LAB.cam = 'fixed'; LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        frames = []
        for i in range(N):
            await pg.evaluate(f"LAB.step({EVERY})")
            await pg.evaluate(f"(() => {{ const D = LAB.D, c = Math.cos(D.yaw), s = Math.sin(D.yaw), o = {json.dumps(OFF)}; LAB.camPos = [D.x + o[0] * c + o[2] * s, o[1] + 0.8 * (D.y || 0), D.z - o[0] * s + o[2] * c]; LAB.camAt = [D.x + {ATDZ} * s, 0.3 + 0.8 * (D.y || 0), D.z + {ATDZ} * c]; LAB.render(); }})()")
            fn = f'{S}/lab/{TAG}_{i:02d}.png'; await pg.screenshot(path=fn); frames.append(fn)
        u = await pg.evaluate("(() => { const L = LAB.I.ax.A.loco; return L && L.sl ? [+L.sl.u.toFixed(2), +L.slK.toFixed(2)] : null; })()")
        print('end u/sl', u, 'errors', errs[:3]); await b.close()
    ims = [Image.open(f) for f in frames]; cols = min(len(ims), int(os.environ.get('COLS', 5))); rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (cols * W, rows * H), 'white'); [sh.paste(im, ((i % cols) * W, (i // cols) * H)) for i, im in enumerate(ims)]
    sh.save(f'{S}/lab/{TAG}_sheet.png'); [os.remove(f) for f in frames]
asyncio.run(main())
