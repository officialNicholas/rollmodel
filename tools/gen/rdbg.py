import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(500)
        await pg.click('#startBtn'); await pg.wait_for_timeout(800)
        await pg.keyboard.press('p'); await pg.wait_for_timeout(200)
        print('after p', await pg.evaluate("[__T.state, document.activeElement.id]"))
        await pg.keyboard.press('r')
        for i in range(5):
            await pg.wait_for_timeout(300); print(i, await pg.evaluate("[__T.state, document.activeElement.id]"))
        print(errs); await b.close()
asyncio.run(main())
