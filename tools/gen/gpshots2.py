import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ diff: 'hard', seen: {steer:1,jump:1,hold:1,orb:1,burst:1,pound:1,airsling:1,dilute:1,dry:1}, wins: { hard: 3, medium: 5 }, played: { hard: 7, medium: 9 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(9); __T.mapUsed=false; __T.showMenu(); })()"); await pg.wait_for_timeout(500)
        await pg.click('#how summary'); await pg.wait_for_timeout(300); await pg.evaluate("document.getElementById('menu').scrollTop = 99999"); await pg.wait_for_timeout(200)
        await pg.screenshot(path='qol/h_how.png')
        await pg.evaluate("document.getElementById('how').open=false; document.getElementById('menu').scrollTop = 0")
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P)")
        await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<1200 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } P.ai = null; T.steerIn = 0; })()""")
        # dodge: the CPU pounds beside you, you jump at the right moment
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; if (P.st !== 'play') { P.st = 'play'; P.koT = 0; } const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw); H.st='play'; H.x = P.x + fx * 2.2 + fz * 0.8; H.z = P.z + fz * 2.2 - fx * 0.8; H.y = P.y; H.air=false; H.slamCD=0; H.paint=1; H.immuneT=0; window.__hai2 = H.ai; H.ai=null; P.immuneT = 0; T.useSlam(H); for (let i=0;i<34;i++) { T.step(0.012); P.spd = 0; } T.jump(P); for (let i=0;i<40 && H.slam;i++) T.step(0.012); for (let i=0;i<6;i++) T.step(0.012); })()""")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(160); await pg.evaluate("window.__noStep=true")
        print('after dodge', await pg.evaluate("[__T.P.st, document.getElementById('pop').textContent]"))
        await pg.screenshot(path='qol/h_dodge.png')
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; H.ai = window.__hai2; for (let i=0;i<80;i++) T.step(0.012); const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw); H.x = P.x - fx * 8 + fz * 4; H.z = P.z - fz * 8 - fx * 4; H.y = T.surfaceUnder(H.x, H.z, 9); H.air = false; })()""")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(250); await pg.evaluate("window.__noStep=true")
        print('ptr', await pg.evaluate("[document.getElementById('foePtr').className, __T.P.st, __T.H.st]"))
        await pg.screenshot(path='qol/h_ptr.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
