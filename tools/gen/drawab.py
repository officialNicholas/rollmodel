import asyncio, json, sys
from playwright.async_api import async_playwright
B='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for f in ['pc_v36.html', 'pc_t.html']:
            for seed in [11, 22, 33]:
                ctx = await b.new_context(viewport={'width':390,'height':844})
                await ctx.add_init_script("Math.random = (()=>{ let s=%d; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();" % seed)
                pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
                await pg.goto(B+f); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
                r = await pg.evaluate("""(()=>{ const T=__T; window.__noLoop=true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
                  for (let i=0;i<1200;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
                  for (let i=0;i<5;i++) T.visuals(0.016,0.016); const R=T.renderer; R.info.autoReset=false; R.info.reset(); T.renderFrame(); const c=R.info.render.calls, t=R.info.render.triangles; R.info.autoReset=true; return [c, t]; })()""")
                print(f, seed, r, errs[:2]); await ctx.close()
        await b.close()
asyncio.run(main())
