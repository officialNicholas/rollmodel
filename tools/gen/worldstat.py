import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844})
        await ctx.add_init_script("localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} }));")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
        for key in ['island', 'blank']:
            r = await pg.evaluate(f"""(() => {{ const T = __T; T.setStage('{key}'); T.freshMap(); T.mapUsed = false; T.start(); for (let i = 0; i < 30; i++) T.step(0.016); T.endMatch(); return [T.TH.id, JSON.stringify(JSON.parse(localStorage.getItem('paint-world-red.v1')).world)]; }})()""")
            print(key, r)
            await pg.evaluate("(() => { if (__T.vic) __T.endVictory(); __T.state = 'menu'; __T.showMenu(); })()")
        print(errs[:3]); await b.close()
asyncio.run(main())
