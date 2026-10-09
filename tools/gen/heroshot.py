import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 11
OUT = sys.argv[2] if len(sys.argv) > 2 else 'gen/hero.png'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ xp: 720, streak: 2, bestStreak: 3, diff: 'hard', seen: {steer:1,sling:1,slam:1,pull:1}, wins: { hard: 4 }, played: { hard: 9 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(f"(()=>{{ __T.genWorld({SEED}); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); }})()")
        await pg.click('#startBtn'); await pg.wait_for_timeout(200)
        await pg.evaluate("window.__noStep=true; __T.aiReset(__T.P)")
        for sec in range(26):
            await pg.evaluate("""(()=>{ const T=__T, P=T.P; for (let i=0;i<83 && T.state==='play';i++){ T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); } })()""")
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 999); P.ai = null; T.steerIn = 0;
          const fl = T.BOXES.filter(b => b[4] > 0.5 && (b[1]-b[0]) > 3.5 && (b[3]-b[2]) > 3.5).sort((a, b) => (b[1]-b[0])*(b[3]-b[2]) - (a[1]-a[0])*(a[3]-a[2]));
          if (!fl.length) return 'none'; const b = fl[0], cx = (b[0]+b[1])/2, cz = (b[2]+b[3])/2;
          P.st = 'play'; P.x = cx; P.z = cz; P.y = b[5]; P.air = false; P.spd = 0; P.paint = 1; P.slamCD = 0; P.immuneT = 0; T.useSlam(P); for (let i = 0; i < 90; i++) T.step(0.012);
          P.x = cx - 0.8; P.z = b[3] - 0.9; P.y = b[5]; P.air = false; P.yaw = Math.PI; P.spd = 0; for (let i = 0; i < 40; i++) { P.yaw = Math.PI; T.step(0.012); }
          return { b, theme: T.genLayout(%d).theme }; })()""" % SEED)
        print(r)
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(1300); await pg.evaluate("window.__noStep=true")
        await pg.screenshot(path=OUT); print(errs[:3]); await b.close()
asyncio.run(main())
