import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000)
        await pg.evaluate("__T.setDiff('hard')")
        await pg.click('#startBtn'); await pg.wait_for_timeout(100)
        await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P)")
        shots = {20: 'v20', 45: 'v45', 70: 'v70'}
        for sec in range(1, 96):
            st = await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<83 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } return T.state; })()""")
            await pg.wait_for_timeout(40)
            if sec in shots: await pg.screenshot(path=f'gen/{shots[sec]}.png')
            if st != 'play': break
        await pg.evaluate("window.__noStep=false")
        await pg.wait_for_timeout(4000)
        await pg.screenshot(path='gen/v_end.png')
        r = await pg.evaluate("({info: __T.endInfo, P: {kos: __T.P.kos, outs: __T.P.outWhy}, H: {kos: __T.H.kos, outs: __T.H.outWhy}, endHidden: document.getElementById('end').hidden, title: document.getElementById('endTitle').textContent, pct: document.getElementById('endPct').textContent + ' / ' + document.getElementById('endPctC').textContent})")
        print(r)
        print('errors', errs[:4])
        await b.close()
asyncio.run(main())
