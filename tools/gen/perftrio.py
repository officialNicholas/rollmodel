import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for m in ['duel','trio']:
            r = await pg.evaluate("""(m)=>{ const T=__T; window.__noLoop=true; T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
              for (let i=0;i<1500;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
              let ts=0, tv=0; const r=T.renderer.info; for (let f=0; f<60; f++){ const a=performance.now(); for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} const b2=performance.now(); T.visuals(0.016,0.016); ts+=b2-a; tv+=performance.now()-b2; }
              T.renderFrame(); return { mode: m, arena: T.ARENA, stepMs: +(ts/60).toFixed(2), visMs: +(tv/60).toFixed(2), calls: r.render.calls, tris: r.render.triangles, samples: T.NSv }; }""", m)
            print(json.dumps(r))
        print(errs[:3]); await b.close()
asyncio.run(main())
