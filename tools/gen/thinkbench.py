import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + (sys.argv[1] if len(sys.argv) > 1 else 'pc_prof.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        for m in ['duel','trio']:
            print(await pg.evaluate("""(m)=>{ const T=__T; window.__noLoop=true; Math.random = (()=>{ let s=777; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
              for (let i=0;i<900;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
              const PF = window.__PF || {}; for (const k in PF) PF[k]=0; const H=T.H; const N=150; const a=performance.now(); for (let i=0;i<N;i++){ H.ai.plan=null; T.aiThink(H); } const ms=(performance.now()-a)/N;
              const o={ m, thinkMs:+ms.toFixed(3) }; for (const k in PF) if (PF[k]>0) o[k]=+(PF[k]/N).toFixed(3); return o; }""", m))
        await b.close()
asyncio.run(main())
