import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        n0 = await pg.evaluate("__T.GEN.n")
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        print('first start: gen.n', n0, '->', await pg.evaluate("__T.GEN.n"), 'state', await pg.evaluate("__T.state"))
        await pg.evaluate("__T.matchLeft = 0.05"); await pg.wait_for_timeout(3500)
        print('end shown', not await pg.evaluate("document.getElementById('end').hidden"))
        seed0 = await pg.evaluate("__T.GEN.seed")
        await pg.click('#endBtn'); await pg.wait_for_timeout(30)
        print('right after tap: state', await pg.evaluate("__T.state"), 'end hidden', await pg.evaluate("document.getElementById('end').hidden"), 'banner', await pg.evaluate("document.getElementById('bannerBig').textContent"))
        await pg.wait_for_timeout(800)
        print('after: state', await pg.evaluate("__T.state"), 'new seed', (await pg.evaluate("__T.GEN.seed")) != seed0, 'gen.n', await pg.evaluate("__T.GEN.n"), 'slamCD', await pg.evaluate("__T.P.slamCD.toFixed(1)"))
        # change difficulty -> menu shows a fresh map, then play uses it without another build
        await pg.evaluate("__T.matchLeft = 0.05"); await pg.wait_for_timeout(3500)
        await pg.click('#menuBtn'); await pg.wait_for_timeout(500)
        nm = await pg.evaluate("__T.GEN.n"); await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        print('menu->play builds again?', (await pg.evaluate("__T.GEN.n")) != nm)
        print('errors', errs)
        await b.close()
asyncio.run(main())
