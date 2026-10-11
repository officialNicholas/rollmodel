"""The axolotl lab (ws/lab): run a scenario, film it frame by frame into a sheet, and measure how far planted feet slide.
usage: lab.py <scenario> '<json opts>' <cam> <frames> <every> <out tag> [warm frames] [info]"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SC, OPT, CAM, N, EVERY, TAG = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
WARM = int(sys.argv[7]) if len(sys.argv) > 7 else 60; INFO = len(sys.argv) > 8 and sys.argv[8] == 'info'
W, H = int(os.environ.get('LW', 520)), int(os.environ.get('LH', 340))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' else None)
        await pg.goto('http://localhost:8765/lab/index.html?v=' + str(os.getpid()), timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        if INFO:
            print(await pg.evaluate("""(() => { const A = LAB.I.ax.A, P = A.P; return JSON.stringify({ names: P.names.map((n, i) => n + ':' + P.par[i]).join(' '), hand: A.crawlHand, foot: A.crawlFoot, stride: A.stride, H: A.H,
              len: Object.fromEntries(['upperarm.L', 'forearm.L', 'hand.L', 'thigh.L', 'shin.L', 'foot.L', 'hips', 'spine', 'spine1', 'chest', 'neck', 'head'].map(n => [n, +P.len[P.idx[n]].toFixed(3)])), bind: A.limbBind, LSroot: A.LS.root }); })()"""))
        await pg.evaluate(f"LAB.cam = '{CAM}'; LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        frames = []; track = []
        for i in range(N):
            for k in range(EVERY):
                await pg.evaluate("LAB.step(1)"); track.append(await pg.evaluate("[LAB.t, LAB.D.x, LAB.D.z, LAB.D.y, LAB.feet()]"))
            await pg.evaluate("LAB.render()"); fn = f'{S}/lab/{TAG}_{i:02d}.png'; await pg.screenshot(path=fn); frames.append(fn)
        # slip: a foot near the ground (within 2.5 cm of its lowest) is taken as planted; its horizontal speed there, against the body's
        out = {}
        for n in ['hand.L', 'hand.R', 'foot.L', 'foot.R']:
            sp = []; bs = []
            for a, c in zip(track, track[1:]):
                if a[4]['st'].get(n) == 'stance' and c[4]['st'].get(n) == 'stance':
                    dtt = c[0] - a[0]; sp.append(((c[4][n][0] - a[4][n][0]) ** 2 + (c[4][n][2] - a[4][n][2]) ** 2) ** 0.5 / dtt); bs.append(((c[1] - a[1]) ** 2 + (c[2] - a[2]) ** 2) ** 0.5 / dtt)
            out[n] = (round(sum(sp) / max(1, len(sp)), 2), round(sum(bs) / max(1, len(bs)), 2), len(sp))
        print('gait f', [tr[4]['f'] for tr in track[-3:]], 'v', [tr[4]['v'] for tr in track[-3:]])
        print('slip (planted foot speed, body speed, frames):', out)
        json.dump(track, open(f'{S}/lab/{TAG}_track.json', 'w'))
        print('errors', errs[:5]); await b.close()
    ims = [Image.open(f) for f in frames]; cols = min(len(ims), int(os.environ.get('COLS', 4))); rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (cols * W, rows * H), 'white'); [sh.paste(im, ((i % cols) * W, (i // cols) * H)) for i, im in enumerate(ims)]
    sh.save(f'{S}/lab/{TAG}_sheet.png'); [os.remove(f) for f in frames]
asyncio.run(main())
