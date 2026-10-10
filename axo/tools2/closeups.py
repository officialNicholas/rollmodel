import asyncio, sys, time
from shot import *
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W = H = 500
SPOTS = {'stand': ('walking.glb?rest=1', [('handL', (0.53, 0.64, 0.80), 0.5), ('handR', (-0.51, 0.63, 0.72), 0.5), ('footL', (0.31, 0.06, 0.74), 0.5), ('footR', (-0.29, 0.06, 0.69), 0.5), ('gillsL', (0.4, 1.45, 0.42), 1.0), ('gillsR', (-0.4, 1.45, 0.42), 1.0), ('head', (-0.01, 1.4, 0.55), 1.7)]),
         'crawl': ('crawl.glb', [('handL', (-0.05, -0.39, 0.72), 0.5), ('handR', (-0.78, -0.39, 0.58), 0.5), ('footL', (0.36, -0.39, 0.12), 0.5), ('footR', (-0.3, -0.4, -0.5), 0.5), ('gillsL', (0.0, 0.15, 0.62), 1.0), ('gillsR', (-0.62, 0.15, 0.62), 1.0), ('head', (-0.3, 0.1, 0.68), 1.7)])}
VIEWS = [(0.0, 1.45, 'top'), (0.0, -1.45, 'below'), (0.0, 0.15, 'front'), (1.57, 0.15, 'side+x'), (-1.57, 0.15, 'side-x'), (2.4, 0.5, 'back3/4')]
async def main(which):
    async with async_playwright() as p:
        for name in which:
            file, spots = SPOTS[name]
            b, pg, errs = await open_page(p, f'http://localhost:8765/axo2/glbview.html?f=/axo2/{file}', W, H); t0 = time.time()
            await pg.evaluate('v.noEmis()')
            for lab, c, dist in spots:
                cells = []
                for (yaw, pitch, vl) in VIEWS:
                    for wire in (0, 1):
                        ims = await capture(pg, [f'v.wire({wire}); v.view({yaw},{pitch},{dist},{c[0]},{c[1]},{c[2]},28)'], 'v.shot()'); cells.append((ims[0], f'{name} {lab} {vl}{" wire" if wire else ""}'))
                grid(cells, 4, W, H).save(D + f'close_{name}_{lab}.jpg', quality=80)
            print(name, 'done', round(time.time() - t0, 1), errs[:3]); await b.close()
asyncio.run(main(sys.argv[1:] or ['stand', 'crawl']))
