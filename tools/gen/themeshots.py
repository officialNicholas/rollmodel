import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
themes = sys.argv[1:] or ['studio', 'crypt', 'cathedral', 'manor', 'garden']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ xp: 720, streak: 2, bestStreak: 3, diff: 'hard', seen: {steer:1,sling:1,slam:1}, wins: { hard: 4 }, played: { hard: 9 } })); } catch (e) {}")
        pg = await ctx.new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.wait_for_timeout(600)
        for th in themes:
            sd = await pg.evaluate(f"(()=>{{ for (let s = 1; s < 600; s++) if (__T.genLayout(s).theme === '{th}') return s; return -1; }})()")
            await pg.evaluate(f"(()=>{{ __T.genWorld({sd}); __T.mapUsed=false; __T.showMenu(); }})()")
            await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'gen/th_menu_{th}.png')
            await pg.click('#startBtn'); await pg.wait_for_timeout(300)
            await pg.evaluate("window.__noStep=true")
            r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; for(let i=0;i<180;i++) T.step(0.012);
              for (let i = 0; i < 70; i++) { const x = -24 + Math.random() * 48, z = -24 + Math.random() * 48, y = T.surfaceUnder(x, z, 99); if (y < -1) continue; T.addSplat(x, y, z, Math.random() * 6.28, 1.2 + Math.random() * 1.6, 0, false, false, i % 2); }
              P.x = T.START.x * 0.55; P.z = T.START.z * 0.55; P.y = T.surfaceUnder(P.x, P.z, 99); P.air = false; P.spd = 0; P.yaw = Math.atan2(-P.x, -P.z);
              return { y: P.y }; })()""")
            await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(1500); await pg.evaluate("window.__noStep=true")
            await pg.screenshot(path=f'gen/th_{th}.png')
            print(th, sd, r, await pg.evaluate("__T.GEN.arch"))
            await pg.evaluate("__T.showMenu()"); await pg.wait_for_timeout(200)
        print('errors', errs)
        await b.close()
asyncio.run(main())
