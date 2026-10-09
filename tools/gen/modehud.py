import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ color:'orange', bestCov: {solo: 21}, seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(500)
        for m in ['trio', 'solo']:
            await pg.click(f'#modes button[data-m="{m}"]'); await pg.wait_for_timeout(500)
            await pg.evaluate("""()=>{ const T=__T; window.__noLoop = true; T.start(); T.aiReset(T.P); const P=T.P; for (let i=0;i<2600 && T.state==='play'; i++) { T.aiStep(P, 0.012); T.steerIn = P.steer; T.step(0.012); } P.ai = null; T.steerIn = 0; for (let i=0;i<40;i++) T.visuals(0.012, 0.05); T.renderFrame(); }""")
            await pg.wait_for_timeout(300); await pg.screenshot(path=f'ui/hud_{m}.png')
            print(m, await pg.evaluate("[...document.querySelectorAll('.vsrow .vsn')].map(e=>getComputedStyle(e).display+':'+e.textContent)"))
            await pg.evaluate("window.__noLoop=false; __T.showMenu()"); await pg.wait_for_timeout(500)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
