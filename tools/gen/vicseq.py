import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W, H, TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=2468; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Count Drip', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(400)
        await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; window.__noLoop = true; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i=0;i<900;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
          for (const n of T.NAVo.nodes) if (n.h === 0 && Math.random() < 0.06) T.addSplat(n.x, 0, n.z, 0, 1.2, T.dryClock, false, true, 0);
          for (let k=0;k<3 && T.state==='play';k++) { T.matchLeft = 0.01; for (let i=0;i<60 && T.state==='play';i++) T.step(0.012); }
          T.startVictory(); })()""")
        shots = []
        t = 0
        for target in [0.3, 0.55, 0.8, 1.1, 1.5, 1.9, 2.3, 2.7, 3.1, 3.5, 4.0, 4.4]:
            n = int(round((target - t) / 0.016)); t += n * 0.016
            r = await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016,0.016); __T.renderFrame(); const v=__T.vic; const D=v.feat[0]; return [+v.t.toFixed(2), +(v.cy||0).toFixed(3), +(v.room||0).toFixed(3)]; }})()")
            await pg.screenshot(path=f'ui/vs_{TAG}_{len(shots):02d}.png'); shots.append(r)
        print(shots, errs[:3]); await b.close()
asyncio.run(main())
