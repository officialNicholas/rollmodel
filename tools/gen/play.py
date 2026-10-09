import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_timeout(2500)
        await pg.screenshot(path='gen/menu.png')
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        print(await pg.evaluate("({...__T.GEN})"))
        # let the CPU drive P too for a bit: fast-forward
        for k in range(3):
            await pg.evaluate("(()=>{for(let i=0;i<250;i++){__T.P.paint=Math.max(__T.P.paint,0.6); __T.step(0.012);} })()")
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'gen/play{k}.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
