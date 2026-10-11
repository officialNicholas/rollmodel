import asyncio, time
from playwright.async_api import async_playwright
async def main():
    t0=time.time()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 400}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/axo2/preview.html?manual', timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        print('loaded', round(time.time()-t0,1))
        t1=time.time(); await pg.evaluate('axo.setState("crawl"); axo.step(1/60,60)'); print('60 steps', round(time.time()-t1,2))
        t1=time.time(); d=await pg.evaluate('axo.shot()'); print('shot', round(time.time()-t1,2), len(d))
        t1=time.time(); n=await pg.evaluate('axo.skinned().length'); print('skinned', round(time.time()-t1,2), n)
        print(errs)
        await b.close()
asyncio.run(main())
