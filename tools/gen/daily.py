import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.click('#dailyBtn'); await pg.wait_for_timeout(1200)
        s1 = await pg.evaluate("__T.GEN.seed")
        await pg.evaluate("(()=>{ const T=__T; for(let i=0;i<40;i++) T.addSplat(-20+Math.random()*40, 0, -20+Math.random()*40, 0, 1.5, 0, false, true, 0); T.matchLeft=0.05; })()")
        await pg.wait_for_timeout(3800)
        print('eyebrow:', await pg.evaluate("document.getElementById('endEyebrow').textContent"), '| note:', await pg.evaluate("document.getElementById('xpNote').textContent"))
        await pg.click('#endBtn'); await pg.wait_for_timeout(1200)
        print('rematch is the same canvas:', s1 == await pg.evaluate("__T.GEN.seed"), 'state', await pg.evaluate("__T.state"))
        await pg.evaluate("__T.state='dead'"); await pg.evaluate("__T.showMenu()"); await pg.wait_for_timeout(500)
        print('menu daily info:', await pg.evaluate("document.getElementById('dailyInfo').textContent"))
        print('errors', errs)
        await b.close()
asyncio.run(main())
