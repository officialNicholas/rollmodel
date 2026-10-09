import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("if (!sessionStorage.getItem('s')) { sessionStorage.setItem('s','1'); localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); }")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(1000)
        for key, th in [('island', 'island'), ('blank', 'blank'), ('standard', 'studio'), ('season', None)]:
            await pg.click('#homePlay'); await pg.wait_for_timeout(700)
            await pg.evaluate(f"document.querySelector('.world[data-s=\"{key}\"]').click()"); await pg.wait_for_timeout(900)
            st = await pg.evaluate("[__T.stageSel, __T.TH.id, __T.GEN.key, document.getElementById('cvName').textContent, document.getElementById('shuffleBtn').hidden]")
            await pg.click('#startBtn'); await pg.wait_for_timeout(1500)
            st2 = await pg.evaluate("[__T.state, __T.TH.id, __T.GEN.key]")
            await pg.evaluate("(() => { __T.matchLeft = 0.01; })()"); await pg.wait_for_timeout(2500)
            st3 = await pg.evaluate("[__T.state, JSON.stringify(JSON.parse(localStorage.getItem('paint-world-red.v1')).world || {})]")
            print(key, 'menu:', st, 'play:', st2, 'end:', st3[0])
            await pg.evaluate("(() => { if (__T.vic) __T.endVictory(); __T.state = 'menu'; __T.showMenu(); })()"); await pg.wait_for_timeout(800)
        print('stats', st3[1]); print('errors', errs[:4]); await b.close()
asyncio.run(main())
