import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(500)
        names=[await pg.evaluate("document.getElementById('cvName').textContent")]
        for i in range(14):
            await pg.click('#shuffleBtn'); await pg.wait_for_timeout(120)
            names.append(await pg.evaluate("document.getElementById('cvName').textContent"))
        rep = sum(1 for a,b2 in zip(names,names[1:]) if a==b2)
        print(names, 'repeats', rep, errs); await b.close()
asyncio.run(main())
