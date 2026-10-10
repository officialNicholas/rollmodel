# render sheets from rigview.html: each cell = (label, js) ; args: mesh name, out name, cells spec module
import asyncio, sys, time, json
from shot import *
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
async def run(mesh, out, cells, W=500, H=500, ncol=4, tex=None):
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, f'http://localhost:8765/axo2/rigview.html?m={mesh}' + (f'&tex={tex}' if tex else ''), W, H); t0 = time.time()
        ims = []
        for lab, js in cells:
            im = (await capture(pg, [js], 'rv.shot()'))[0]; ims.append((im, lab))
        grid(ims, ncol, W, H).save(D + out, quality=82); print(out, 'done', round(time.time() - t0, 1), errs[:3]); await b.close()
if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); asyncio.run(run(spec['mesh'], spec['out'], spec['cells'], spec.get('W', 500), spec.get('H', 500), spec.get('ncol', 4), spec.get('tex')))
