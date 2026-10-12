# The idle eyes measured (v10c): 150 s of stand idle at 60 fps in the lab, the pupil target sampled every frame; the moves (a new spot
# more than 0.02 face units away), the gaps between them, how long each move takes to get 90% there, and how often a move comes with a
# blink. usage: eyetest.py [lab dirs = lab lab_v239]
import asyncio, sys, json
import numpy as np
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
LABS = sys.argv[1:] or ['lab', 'lab_v239']
JS = """() => { LAB.set('idle'); LAB.step(20); LAB.I.ax.A.set('stand'); LAB.step(120); const L = LAB.I.ax.look, out = [];
  for (let i = 0; i < 9000; i++) { LAB.step(1); out.push([L.look[0], L.look[1], L.blinkK > 0 ? 1 : 0, L.att.eye[0], L.att.eye[1], L.dart[0], L.dart[1]]); }
  L.att.eye[0] = 0; L.att.eye[1] = 0; L.att.t = 100; L.dart[0] = 0; L.dart[1] = 0; L.dartT = 100; LAB.step(60); L.att.eye[0] = 0.1; const resp = [];
  for (let i = 0; i < 16; i++) { LAB.step(1); resp.push(L.look[0]); } return { out, resp }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for lab in LABS:
            pg = await b.new_page(viewport={'width': 200, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto(f'http://localhost:8767/fable3/{lab}/index.html', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
            r = await pg.evaluate(JS); a = np.array(r['out']); resp = np.array(r['resp']); await pg.close()
            lk = a[:, :2]; bl = a[:, 2] > 0; dt = 1 / 60
            # a move: the pupil displaced more than 0.02 over the next 0.3 s, taken from the first such frame; its end once 0.4 s of calm
            d = np.linalg.norm(lk[18:] - lk[:-18], axis=1); moving = d > 0.02
            starts = []; i = 0
            while i < len(moving):
                if moving[i]:
                    starts.append(i); j = i
                    while j < len(moving) and moving[max(0, j - 24):j + 1].any(): j += 1
                    i = j
                else: i += 1
            gaps = np.diff(starts) * dt if len(starts) > 1 else np.zeros(0)
            t90 = []
            for s0 in starts:
                p0 = lk[s0]; seg = lk[s0:s0 + 40]; dd = np.linalg.norm(seg - p0, axis=1); tot = dd.max()
                if tot < 0.02: continue
                k = int(np.argmax(dd >= 0.9 * tot)); t90.append(k * dt)
            wb = sum(bl[max(0, s0 - 6):s0 + 26].any() for s0 in starts)   # (the move is seen about 15 frames before the spot changes; the blink comes at the change)
            # the biggest single-frame jump (the snap)
            jump = np.linalg.norm(np.diff(lk, axis=0), axis=1)
            ch = lambda c: np.where(np.abs(np.diff(a[:, c], axis=0)).sum(1) > 1e-6)[0]; ga = np.diff(ch([3, 4])) * dt; gd = np.diff(ch([5, 6])) * dt
            print(f'{lab}: attention/glance changes {len(ga) + 1} (gap mean {ga.mean():.2f} s, min {ga.min():.2f}, max {ga.max():.2f}, > 6 s: {int((ga > 6).sum())}), darts {len(gd) + 1} (gap mean {gd.mean():.2f} s, amp max {np.abs(a[:, 5]).max():.3f}); step response to a 0.1 glance, per frame: ' + ' '.join(f'{x / 0.1:.2f}' for x in resp))
            print(f'{lab}: {len(a) * dt:.0f} s idle, {len(starts)} moves ({len(starts) / (len(a) * dt):.2f}/s), gap mean {gaps.mean() if len(gaps) else 0:.2f} s, median {np.median(gaps) if len(gaps) else 0:.2f}, min {gaps.min() if len(gaps) else 0:.2f}, max {gaps.max() if len(gaps) else 0:.2f}; '
                  f'gaps > 6 s: {int((gaps > 6).sum())}; time to 90% of a move: mean {np.mean(t90) if t90 else 0:.3f} s (max {max(t90) if t90 else 0:.3f}); largest one-frame step {jump.max():.3f}; moves with a blink {wb}/{len(starts)}; errors {errs}')
        await b.close()
asyncio.run(main())
