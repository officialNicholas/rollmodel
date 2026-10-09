import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--js-flags=--trace-gc'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        r = await pg.evaluate("""(()=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
          for (let i=0;i<600;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
          console.log('BENCH-START'); const a=performance.now(); for (let f=0; f<900; f++){ for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} T.visuals(0.016,0.016); T.flushTrail(); if (P.st==='ko') { P.st='play'; P.koT=0; } if (T.state!=='play') T.state='play'; } console.log('BENCH-END'); return performance.now()-a; })()""")
        print('ms', r); await b.close()
asyncio.run(main())
