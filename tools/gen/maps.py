import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
seeds=[int(x) for x in sys.argv[1:]] or [11,22,33,44,55,66]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':700,'height':700})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_timeout(2000)
        await pg.evaluate("document.getElementById('menu').hidden=true")
        for sd in seeds:
            g = await pg.evaluate(f"(()=>{{ __T.genWorld({sd}); __T.mapUsed=false; __T.showMenu(); document.getElementById('menu').hidden=true; window.__cam=[[0,62,0.01],[0,0,0]]; return {{...__T.GEN, start:__T.START, cstart:__T.CSTART}}; }})()")
            await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'gen/map_{sd}.png')
            print(sd, g['sym'], g['arch'], 'tries', g['tries'], 'ms', round(g['ms']), 'fallback', g['fallback'])
        print('errors', errs)
        await b.close()
asyncio.run(main())
