import asyncio, json, base64
from shot import *
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', 600, 600)
        await pg.evaluate('axo.size(600,600); axo.setState("stand"); axo.step(1/60, 60); axo.view(0.3,0.1,4.2,0.85)')
        ims = await capture(pg, ['0'], 'axo.shot()')
        await pg.evaluate('axo.view(0.0,0.1,1.6,1.3,0,0.4,30)'); ims += await capture(pg, ['0'], 'axo.shot()')
        await pg.evaluate('axo.look.setPaint(0.5); axo.look.setExpression("happy"); axo.step(1/60, 30); axo.view(0.5,0.15,4.2,0.85)'); ims += await capture(pg, ['0'], 'axo.shot()')
        await pg.evaluate('axo.setState("crawl"); axo.step(1/60, 120); axo.view(0.6,0.25,4.6,0.3)'); ims += await capture(pg, ['0'], 'axo.shot()')
        grid([(im, l) for im, l in zip(ims, ['stand', 'face', 'paint .5 happy', 'crawl'])], 2, 600, 600).save('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/smoke.jpg', quality=85)
        print('errors:', errs[:6]); await b.close()
asyncio.run(main())
