import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W, H, TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if W < 600 else 1, has_touch=W < 600)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(700)
        await pg.screenshot(path=f'qol/{TAG}_1menu.png')
        await pg.click('#how summary'); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('menu').scrollTop = 99999"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=f'qol/{TAG}_2how.png')
        await pg.evaluate("document.getElementById('how').open=false; document.getElementById('menu').scrollTop = 0")
        await pg.click('#startBtn'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'qol/{TAG}_3start.png')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'qol/{TAG}_4early.png')
        await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P)")
        for sec in range(20):
            await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<83 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } })()""")
        await pg.evaluate("window.__noStep=false; __T.P.ai=null; __T.steerIn=0"); await pg.wait_for_timeout(600)
        await pg.screenshot(path=f'qol/{TAG}_5mid.png')
        await pg.click('#pauseBtn'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'qol/{TAG}_6pause.png')
        await pg.click('#resumeBtn'); await pg.wait_for_timeout(200)
        await pg.evaluate("__T.matchLeft = 0.05"); await pg.wait_for_timeout(4500)
        await pg.screenshot(path=f'qol/{TAG}_7end.png')
        print(TAG, errs[:4]); await b.close()
asyncio.run(main())
