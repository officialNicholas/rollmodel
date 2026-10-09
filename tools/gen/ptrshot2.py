import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ diff: 'hard', seen: {steer:1,jump:1,hold:1,orb:1,burst:1,pound:1,airsling:1,dilute:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ let s = 4242; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; __T.genWorld(11); __T.mapUsed=false; __T.showMenu(); })()"); await pg.wait_for_timeout(400)
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P)")
        await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<1300 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } P.ai = null; T.steerIn = 0; })()""")
        for attempt in range(6):
            ok = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; if (P.st !== 'play') return 'p ' + P.st; if (H.st !== 'play') { for (let i=0;i<200 && H.st!=='play';i++) T.step(0.012); }
              const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw); for (const side of [1, -1]) { const x = P.x - fx * 7 + fz * 5 * side, z = P.z - fz * 7 - fx * 5 * side, y = T.surfaceUnder(x, z, 9); if (y > -1 && !T.blockedAt(x, z, y)) { H.x = x; H.z = z; H.y = y; H.air = false; H.spd = 0; return 'ok'; } } return 'nospot'; })()""")
            if ok == 'ok': break
            await pg.evaluate("(()=>{ for (let i=0;i<120;i++) __T.step(0.012); })()")
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(260); await pg.evaluate("window.__noStep=true")
        print(ok, await pg.evaluate("[document.getElementById('foePtr').className, __T.P.st, __T.H.st]"))
        await pg.screenshot(path='qol/h_ptr.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
