import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        bad = 0
        for i in range(30):
            pg = await b.new_page(viewport={'width':390,'height':844})
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' | '+(e.stack or '')[:500]))
            await pg.goto(U); await pg.wait_for_timeout(2500)
            ok = await pg.evaluate("typeof __T")
            if ok != 'object' or errs: bad += 1; print(i, ok, errs[:1])
            await pg.close()
        print('bad', bad)
        await b.close()
asyncio.run(main())
