import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SEED="Math.random = (()=>{ let s = %d; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })()"
async def main():
    m = int(sys.argv[1]); t0=float(sys.argv[2]); t1=float(sys.argv[3])
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_timeout(1500)
        await pg.evaluate(f"(()=>{{ __T.genWorld({m}); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); }})()")
        await pg.evaluate(SEED % m)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {}; __T.clock=0; ' + (SEED % m) + '; __T.start()')
        r = await pg.evaluate("""([t0,t1])=>{ const T=__T, P=T.P, H=T.H; T.setAI('hard'); P.st='ko'; P.koT=1e9; const log=[];
          for (let i=0;i<7600 && T.state==='play';i++){ const pl=H.ai.plan?JSON.stringify(H.ai.plan):''; T.step(0.012); const t=90-T.matchLeft;
            if (t>t0 && t<t1 && i%3===0) log.push([t.toFixed(2), H.ai.mode, H.st, H.x.toFixed(2), H.y.toFixed(2), H.z.toFixed(2), H.yaw.toFixed(2), H.spd.toFixed(1), H.air?'AIR':'', H.charging?('ch'+H.charge.toFixed(2)):'', pl, H.ai.flight||'', H.paint.toFixed(2)].join(' ')); }
          return log; }""", [t0,t1])
        for l in r: print(l)
        await b.close()
asyncio.run(main())
