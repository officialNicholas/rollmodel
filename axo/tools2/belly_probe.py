import asyncio
from shot import *
D='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W=500
cells=[('side', 'axo.setState("crawl"); axo.A.motion.speed=1; axo.step(1/60,120); axo.view(1.57,0.0,2.4,0.25,0,0.1,30)'),
 ('side wire', 'for (const M of [axo.S, axo.C]) M.mesh.material.wireframe = true; axo.view(1.57,0.0,2.4,0.25,0,0.1,30)'),
 ('below wire', 'axo.view(1.2,-0.05,2.4,0.25,0,0.1,30)'),
 ('rest wire', 'for (const M of [axo.S, axo.C]) M.mesh.material.wireframe = false; axo.A.motion.speed=0; axo.step(1/60,120); axo.view(1.57,0.0,2.4,0.25,0,0.1,30)'),
 ('rest', 'axo.view(1.2,0.05,2.4,0.25,0,0.1,30)'), ('rest below', 'axo.view(1.2,-0.1,2.4,0.25,0,0.1,30)')]
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', W, W); await pg.evaluate(f'axo.size({W},{W})')
        ims=[]
        for lab, js in cells: ims.append(((await capture(pg,[js],'axo.shot()'))[0], lab))
        grid(ims, 3, W, W).save(D+'v6pre_belly.jpg', quality=85); print(errs[:3]); await b.close()
asyncio.run(main())
