import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(2); __T.mapUsed=false; __T.showMenu(); __T.start(); window.__noStep = true; })()")
        await pg.evaluate("(()=>{ const T=__T, P=T.P; T.aiReset(P); for (let i=0;i<900;i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('medium'); T.step(0.012); } P.ai = null; T.steerIn = 0.15; P.paint = 0.015; for (let i=0;i<60;i++) T.step(0.012); })()")
        await pg.evaluate("window.__noStep = false"); await pg.wait_for_timeout(500); await pg.evaluate("window.__noStep = true")
        await pg.screenshot(path='qol/dry.png'); print(await pg.evaluate("[__T.P.st, __T.P.dry, +__T.P.spd.toFixed(2)]"), errs[:2]); await b.close()
asyncio.run(main())
