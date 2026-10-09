import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    k=int(sys.argv[1]); t0=float(sys.argv[2]); t1=float(sys.argv[3])
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(f"(()=>{{ __T.genWorld({5000 + k * 131}); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); }})()")
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        r = await pg.evaluate("""([sd,t0,t1])=>{ __T.clock=0; Math.random = (()=>{ let s = sd; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })(); __T.start(); const T=__T, P=T.P, H=T.H; T.setAI('hard'); P.st='ko'; P.koT=1e9; const log=[];
          for (let i=0;i<7600 && T.state==='play';i++){ T.step(0.012); const t=90-T.matchLeft; if (t>t0&&t<t1){ const a=H.ai, w=T.aiFollow(H);
             log.push([t.toFixed(3), a.mode, H.x.toFixed(2), H.z.toFixed(2), 'yaw'+H.yaw.toFixed(2), 'st'+H.steer.toFixed(2), 'v'+H.spd.toFixed(2), H.charging?'CH':'', 'hz'+T.hazardAt(H,H.yaw,true).toFixed(1), w?('w'+w.x.toFixed(1)+','+w.z.toFixed(1)):'', 'pi'+a.pi+'/'+(a.path?a.path.length:0), a.pivotT.toFixed(2)].join(' ')); } }
          return log; }""", [1234 + k * 977, t0, t1])
        for l in r[::2]: print(l)
        await b.close()
asyncio.run(main())
