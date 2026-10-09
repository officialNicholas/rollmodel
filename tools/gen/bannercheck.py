import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(500)
        await pg.click('#startBtn')
        for t in [100, 300, 600, 1200]:
            await pg.wait_for_timeout(t if t == 100 else 300)
            r = await pg.evaluate("(()=>{ const e=document.getElementById('banner'); const cs=getComputedStyle(e); return [e.className, cs.opacity, cs.animationName, document.getElementById('bannerBig').textContent, document.getElementById('bannerSmall').textContent]; })()")
            print(t, r)
        await b.close()
asyncio.run(main())
