import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_prof.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        for m in ['duel','trio']:
            print(await pg.evaluate("""(m)=>{ const T=__T; window.__noLoop=true; T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P; T.setAI('hard');
              for (let i=0;i<300;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
              let cnt=0; const N=T.NAVo.nodes; let smp=0; for (const n of N) smp+=n.smp.length;
              const c0 = {}; const orig = __PF; let thinks=0; const t0 = __PF.aiThink||0;
              // count thinks via wrapper time deltas is not possible; count by patching thinkT
              let k=0; for (let i=0;i<500;i++){ const before=[T.H.ai.thinkT, T.H2 && T.H2.ai ? T.H2.ai.thinkT : 0]; T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (T.H.ai.thinkT > before[0] + 0.05) k++; if (T.H2 && T.H2.ai && T.H2.ai.thinkT > before[1] + 0.05) k++; }
              return { m, NN: N.length, smpTotal: smp, thinksPerSec: +(k/6).toFixed(1), diff: T.diff }; }""", m))
        await b.close()
asyncio.run(main())
