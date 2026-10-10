import asyncio, time
from shot import *
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
async def main():
    async with async_playwright() as p:
        cells = []
        b, pg, e = await open_page(p, 'http://localhost:8765/axo2/rigview.html?m=axo_stand', 500, 500)
        for lab, js in [('stand cc front', "rv.reset(); rv.mode('tex'); rv.view(0.3,0.15,4.6,0,0.9,0,30)"), ('stand cc side', "rv.view(1.57,0.1,4.6,0,0.9,0,30)"), ('stand cc head', "rv.view(0.4,0.2,1.6,0,1.4,0.4,30)")]:
            cells.append(((await capture(pg, [js], 'rv.shot()'))[0], lab))
        await b.close()
        b, pg, e = await open_page(p, 'http://localhost:8765/axo2/glbview.html?f=/axo2/crawl.glb', 500, 500)
        for lab, js in [('crawl front', "v.view(0.3,0.25,4.0,-0.2,0,0,30)"), ('crawl side', "v.view(1.57,0.2,4.0,-0.2,0,0,30)"), ('crawl head', "v.view(0.4,0.3,1.6,-0.3,0.1,0.7,30)")]:
            cells.append(((await capture(pg, [js], 'v.shot()'))[0], lab))
        await b.close()
        b, pg, e = await open_page(p, 'http://localhost:8765/axo2/glbview.html?f=/axo2/stand_unrigged.glb', 500, 500)
        for lab, js in [('unrigged stand front', "v.view(0.3,0.15,4.6,0,0,0,30)"), ('unrigged side', "v.view(1.57,0.1,4.6,0,0,0,30)"), ('unrigged head', "v.view(0.4,0.2,1.6,0,0.5,0.0,30)")]:
            cells.append(((await capture(pg, [js], 'v.shot()'))[0], lab))
        await b.close()
        grid(cells, 3, 500, 500).save(D + 'colour_cmp.jpg', quality=85); print('done')
asyncio.run(main())
