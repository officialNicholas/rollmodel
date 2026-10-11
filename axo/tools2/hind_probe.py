import asyncio, time
from shot import *
D='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W=400
V="axo.view(2.6,0.5,3.0,0.2,0.1,-0.3,30)"
cells=[('turnL', f'axo.setState("crawl"); axo.A.motion.speed=1; axo.A.motion.turn=1; axo.step(1/60,90); {V}'), ('turnL+', f'axo.step(1/60,20); {V}'), ('turnR', f'axo.A.motion.turn=-1; axo.step(1/60,40); {V}'), ('turnR+', f'axo.step(1/60,20); {V}'),
 ('speed1.5', f'axo.A.motion.turn=0; axo.A.motion.speed=1.5; axo.step(1/60,60); {V}'), ('speed1.5+', f'axo.step(1/60,15); {V}'), ('speed0.3', f'axo.A.motion.speed=0.3; axo.step(1/60,120); {V}'), ('speed0.3+', f'axo.step(1/60,30); {V}'),
 ('jump', f'axo.A.motion.speed=1; axo.A.jump(); axo.step(1/60,10); {V}'), ('air', f'axo.step(1/60,15); {V}'), ('land', 'for (let i = 0; i < 60 && axo.A.inAir; i++) axo.step(1/60); axo.step(1/60, 3); ' + V), ('land+', f'axo.step(1/60,12); {V}'),
 ('exert', f'axo.A.motion.exert=1; axo.step(1/60,60); {V}'), ('exert+', f'axo.step(1/60,20); {V}'), ('exert++', f'axo.step(1/60,20); {V}'), ('exert+++', f'axo.step(1/60,20); {V}')]
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', W, W); await pg.evaluate(f'axo.size({W},{W})')
        ims=[]
        for lab, js in cells: ims.append(((await capture(pg,[js],'axo.shot()'))[0], lab))
        grid(ims, 4, W, W).save(D+'v6pre_hindprobe.jpg', quality=85); print(errs[:3]); await b.close()
asyncio.run(main())
