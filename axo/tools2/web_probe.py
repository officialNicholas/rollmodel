import asyncio
from shot import *
D='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W=450
J=lambda m,j,yaw,pitch,dist,off=(0,0,0): f"(()=>{{const p=axo.joint('{m}','{j}'); axo.view({yaw},{pitch},{dist},p[1]+{off[1]},p[0]+{off[0]},p[2]+{off[2]},30)}})()"
cells=[('stand foot L', 'axo.setState("stand"); axo.step(1/60,60); '+J('stand','toes.L',0.4,0.7,0.7)), ('stand foot L low', J('stand','toes.L',0.6,0.15,0.7)), ('stand hand L', J('stand','hand.L',0.2,-0.4,0.6)),
 ('stand hand L top', J('stand','hand.L',0.2,0.9,0.6)), ('stand side', 'axo.view(1.57,0.05,4.2,0.85)'), ('stand front', 'axo.view(0,0.05,4.2,0.85)'),
 ('crawl foot L', 'axo.setState("crawl"); axo.A.motion.speed=0; axo.step(1/60,120); '+J('crawl','toes.L',0.8,0.9,0.8)), ('crawl hand L', J('crawl','hand.L',0.5,0.9,0.8)), ('crawl side', 'axo.view(1.57,0.0,2.4,0.25,0,0.1,30)'),
 ('crawl below', 'axo.view(1.2,-0.1,2.4,0.25,0,0.1,30)'), ('crawl 3/4', 'axo.view(0.6,0.25,4.6,0.3)'), ('crawl back', 'axo.view(2.3,0.45,3.4,0.2,0,-0.2,30)')]
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', W, W); await pg.evaluate(f'axo.size({W},{W})')
        ims=[]
        for lab, js in cells: ims.append(((await capture(pg,[js],'axo.shot()'))[0], lab))
        grid(ims, 3, W, W).save(D+'v6pre_web.jpg', quality=85); print(errs[:3]); await b.close()
asyncio.run(main())
