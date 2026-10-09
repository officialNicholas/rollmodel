import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
seeds = [int(x) for x in sys.argv[1:]] or [1, 2, 11, 5, 9]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ xp: 720, streak: 2, bestStreak: 3, diff: 'hard', seen: {steer:1,sling:1,slam:1,pull:1}, wins: { hard: 4 }, played: { hard: 9 } })); } catch (e) {}")
        for sd in seeds:
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
            await pg.evaluate(f"(()=>{{ Math.random = (() => {{ let s = {sd} * 99991; return () => {{ s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }}; }})(); __T.genWorld({sd}); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); }})()")
            await pg.click('#startBtn'); await pg.wait_for_timeout(200)
            await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P); __T.setWx('clear', 999)")
            for sec in range(32):
                await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<83 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } })()""")
            await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(700); await pg.evaluate("window.__noStep=true")
            await pg.screenshot(path=f'gen/nat_{sd}.png'); print(sd, await pg.evaluate(f"__T.genLayout({sd}).theme"), errs[:2]); await pg.close()
        await b.close()
asyncio.run(main())
