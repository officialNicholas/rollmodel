import asyncio
from shot import *
D='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W=450
J=lambda m,j,yaw,pitch,dist,off=(0,0,0): f"(()=>{{const p=axo.joint('{m}','{j}'); axo.view({yaw},{pitch},{dist},p[1]+{off[1]},p[0]+{off[0]},p[2]+{off[2]},30)}})()"
WIRE='for (const M of [axo.S, axo.C]) M.mesh.material.wireframe = true; '; SOLID='for (const M of [axo.S, axo.C]) M.mesh.material.wireframe = false; '
cells=[('stand foot L front', 'axo.setState("stand"); axo.step(1/60,60); '+J('stand','toes.L',0.3,0.35,0.55,(0,0,0.05))), ('wire', WIRE+J('stand','toes.L',0.3,0.35,0.55,(0,0,0.05))), ('stand foot R below', SOLID+J('stand','toes.R',-0.4,-0.25,0.55,(0,0,0.05))),
 ('stand hand L palm', J('stand','hand.L',0.2,-0.5,0.5,(0.05,0,0.03))), ('wire', WIRE+J('stand','hand.L',0.2,-0.5,0.5,(0.05,0,0.03))), ('stand hand L back', SOLID+J('stand','hand.L',0.2,0.8,0.5,(0.05,0,0.03))),
 ('crawl foot L top', 'axo.setState("crawl"); axo.A.motion.speed=0; axo.step(1/60,120); '+J('crawl','toes.L',0.8,1.0,0.7,(0.05,0,0.05))), ('wire', WIRE+J('crawl','toes.L',0.8,1.0,0.7,(0.05,0,0.05))), ('crawl hand R top', SOLID+J('crawl','hand.R',-0.5,1.0,0.7,(-0.05,0,0.05))),
 ('crawl side', 'axo.view(1.57,0.0,2.4,0.25,0,0.1,30)'), ('crawl below', 'axo.view(1.2,-0.15,2.4,0.25,0,0.1,30)'), ('stand side', 'axo.setState("stand"); axo.step(1/60,60); axo.view(0.9,0.1,2.4,0.9,0,0.0,30)')]
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', W, W); await pg.evaluate(f'axo.size({W},{W})')
        ims=[]
        for lab, js in cells: ims.append(((await capture(pg,[js],'axo.shot()'))[0], lab))
        grid(ims, 3, W, W).save(D+'v6pre_web2.jpg', quality=85); print(errs[:3]); await b.close()
asyncio.run(main())
