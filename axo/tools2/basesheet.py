# render the user's own Walking / Running clips (GLTFLoader, their skin, their rig) from several angles / times
import asyncio, sys, time
from shot import *
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W = H = 400
async def main():
    async with async_playwright() as p:
        for clip, dur in (('walking', 1.067), ('running', 0.667)):
            b, pg, errs = await open_page(p, f'http://localhost:8765/axo2/glbview.html?f=/axo2/{clip}.glb', W, H); t0 = time.time()
            await pg.evaluate('v.noEmis()')
            cells = []
            for (yaw, pitch, dist, ty, lab) in [(0.0, 0.1, 5.0, 0.9, 'front'), (1.57, 0.1, 5.0, 0.9, 'side'), (0.7, 0.3, 5.0, 0.9, '3/4'), (2.5, 0.2, 5.0, 0.9, 'back 3/4')]:
                for t in [0, dur * 0.25, dur * 0.5, dur * 0.75, dur * 0.95]:
                    ims = await capture(pg, [f'v.setTime({t}); v.view({yaw},{pitch},{dist},0,{ty},0)'], 'v.shot()'); cells.append((ims[0], f'{clip} {lab} t={t:.2f}'))
            grid(cells, 5, W, H).save(D + f'base_{clip}.jpg', quality=85); print(clip, 'done', round(time.time() - t0, 1), errs[:3]); await b.close()
asyncio.run(main())
