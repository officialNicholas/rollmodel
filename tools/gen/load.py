import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for i in range(12):
            pg = await b.new_page(viewport={'width':390,'height':844})
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' | '+(e.stack or '')[:600]))
            await pg.goto(U); await pg.wait_for_timeout(1200)
            ok = await pg.evaluate("typeof __T")
            print(i, ok, errs[:1])
            await pg.close()
        await b.close()
asyncio.run(main())
