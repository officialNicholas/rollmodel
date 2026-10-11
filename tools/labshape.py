"""The axolotl lab: the body's line seen from above (tail tip to snout) through a scenario, as the angle each segment turns from the
one behind it, plus a sheet of the lines drawn over each other.
usage: labshape.py <scenario> '<json opts>' <frames> <every> <out tag> [warm frames]"""
import asyncio, json, sys, os, math
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SC, OPT, N, EVERY, TAG = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
WARM = int(sys.argv[6]) if len(sys.argv) > 6 else 60
CH = ['tail6', 'tail5', 'tail4', 'tail3', 'tail2', 'tail1', 'hips', 'spine', 'spine1', 'chest', 'neck', 'head', 'headfront']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/lab/index.html?v=' + str(os.getpid()), timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate(f"LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        rows = []
        for i in range(N):
            await pg.evaluate(f"LAB.step({EVERY})")
            rows.append(await pg.evaluate("""(CH) => { const I = LAB.I, M = I.ax.P.m[I.ax.A.mesh]; I.root.updateWorldMatrix(true, true); const v = new THREE.Vector3();
              return { t: LAB.t, yaw: LAB.D.yaw, turn: LAB.D.turn, pts: CH.map(n => { const b = M.byName[n]; if (!b) return null; b.getWorldPosition(v); return [v.x, v.z]; }) }; }""", CH))
        await b.close()
    print('errors', errs[:3])
    W = 260; cols = min(N, 8); sh = Image.new('RGB', (cols * W, ((N + cols - 1) // cols) * W), 'white'); d = ImageDraw.Draw(sh)
    for i, r in enumerate(rows):
        pts = [q for q in r['pts'] if q]; c = [sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)]
        # turned so the travel direction points up
        cy, sy = math.cos(r['yaw']), math.sin(r['yaw'])
        P = [((q[0] - c[0]) * cy - (q[1] - c[1]) * sy, (q[0] - c[0]) * sy + (q[1] - c[1]) * cy) for q in pts]
        ox, oy = (i % cols) * W + W / 2, (i // cols) * W + W / 2; sc = 300
        d.line([(ox - x * sc, oy - z * sc) for x, z in P], fill=(200, 30, 50), width=4)
        for k, (x, z) in enumerate(P): d.ellipse([ox - x * sc - 3, oy - z * sc - 3, ox - x * sc + 3, oy - z * sc + 3], fill=(40, 40, 60) if CH[k] in ('hips', 'chest', 'head') else (150, 150, 160))
        # each joint's turn (deg) from the segment behind it
        ang = []
        for k in range(1, len(P) - 1):
            a1 = math.atan2(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]); a2 = math.atan2(P[k + 1][0] - P[k][0], P[k + 1][1] - P[k][1])
            da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi; ang.append(round(math.degrees(da)))
        d.text((ox - W / 2 + 4, oy - W / 2 + 4), f"t {r['t']:.2f} turn {r['turn']:+.1f}", fill='black')
        print(f"t {r['t']:.2f} turn {r['turn']:+.2f}  " + ' '.join(f'{CH[k + 1]}:{a:+d}' for k, a in enumerate(ang)))
    sh.save(f'{S}/lab/{TAG}_shape.png')
asyncio.run(main())
