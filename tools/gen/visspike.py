import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate(r"""(()=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
          for (let i=0;i<600;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
          const out=[]; for (let pass=0; pass<3; pass++) { const V=[]; for (let f=0; f<900; f++){ for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} const b=performance.now(); T.visuals(0.016,0.016); T.flushTrail(); V.push([performance.now()-b, f, P.st, T.wx]); if (P.st==='ko') { P.st='play'; P.koT=0; } if (T.state!=='play') T.state='play'; }
            V.sort((a,b)=>b[0]-a[0]); out.push(V.slice(0,4).map(v=>[+v[0].toFixed(1), v[1], v[2], v[3]])); }
          return out; })()""")
        for x in r: print(x)
        print(errs[:3]); await b.close()
asyncio.run(main())
