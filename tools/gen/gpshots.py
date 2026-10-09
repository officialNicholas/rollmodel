import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ diff: 'hard', seen: {steer:1,jump:1,hold:1,orb:1,burst:1,pound:1,airsling:1,dilute:1,dry:1}, wins: { hard: 3, medium: 5 }, played: { hard: 7, medium: 9 }, bestCov: { hard: 24 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(5); __T.mapUsed=false; __T.showMenu(); })()"); await pg.wait_for_timeout(800)
        await pg.screenshot(path='qol/g_menu.png')
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P)")
        await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<1500 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } P.ai = null; T.steerIn = 0; })()""")
        # the CPU pounds right beside you: catch the telegraph mid-hang
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw); H.st='play'; H.x = P.x + fx * 2.2 + fz * 0.8; H.z = P.z + fz * 2.2 - fx * 0.8; H.y = P.y; H.air=false; H.slamCD=0; H.paint=1; H.immuneT=0; window.__hai2 = H.ai; H.ai=null; T.useSlam(H); for (let i=0;i<42;i++) { T.step(0.012); P.spd = 0; } })()""")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(120); await pg.evaluate("window.__noStep=true")
        await pg.screenshot(path='qol/g_tele.png')
        # jump it
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.jump(P); for (let i=0;i<30 && H.slam;i++) T.step(0.012); })()""")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(250); await pg.evaluate("window.__noStep=true")
        await pg.screenshot(path='qol/g_dodge.png')
        # the holy water behind you: the edge marker
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; H.ai = window.__hai2; for (let i=0;i<60;i++) T.step(0.012); const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw); H.x = P.x - fx * 9 + fz * 3; H.z = P.z - fz * 9 - fx * 3; H.y = T.surfaceUnder(H.x, H.z, 9); })()""")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(300); await pg.evaluate("window.__noStep=true")
        await pg.screenshot(path='qol/g_ptr.png')
        await pg.evaluate("""(()=>{ const T=__T, P=T.P; T.aiReset(P); for (let i=0;i<6500 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } })()""")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(5200)
        await pg.screenshot(path='qol/g_end.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
