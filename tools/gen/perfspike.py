import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_prof.html'
JS = r"""(m)=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; Math.random = (()=>{ let s=12345; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();
  T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
  for (let i=0;i<600;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
  const frames=[]; const tot={}; for (let f=0; f<900; f++){ for (const k in __PF) __PF[k]=0; const a=performance.now(); for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} const ms=performance.now()-a; const pf={}; for (const k in __PF) { pf[k]=+__PF[k].toFixed(2); tot[k]=(tot[k]||0)+__PF[k]; } frames.push({ms, pf}); if (P.st==='ko') { P.st='play'; P.koT=0; } if (T.state!=='play') T.state='play'; }
  frames.sort((x,y)=>y.ms-x.ms); const top = frames.slice(0,8).map(f=>({ms:+f.ms.toFixed(1), top:Object.entries(f.pf).filter(e=>e[1]>0.3).sort((x,y)=>y[1]-x[1]).slice(0,6)}));
  const totS = Object.entries(tot).map(([k,v])=>[k,+(v/900).toFixed(3)]).sort((x,y)=>y[1]-x[1]).slice(0,16);
  return { mode:m, top, perFrameAvg: totS }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for m in (sys.argv[1:] or ['trio']):
            r = await pg.evaluate(JS, m)
            print(m); print(' avg', r['perFrameAvg'])
            for t in r['top']: print(' ', t)
        print(errs[:3]); await b.close()
asyncio.run(main())
