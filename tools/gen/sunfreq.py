import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        r = await pg.evaluate("""(()=>{ const T=__T; let suns=0, rains=0, n=200, sunT=[]; 
          for (let m=0;m<n;m++){ T.mapUsed=false; T.start(); T.P.st='ko'; T.P.koT=1e9; T.H.st='ko'; T.H.koT=1e9; T.H.ai=null; let rained=false, sunAt=-1;
            for (let i=0;i<7600 && T.state==='play';i++){ T.step(0.012); if (T.wx==='rain') rained=true; if (T.wx==='warn' && sunAt<0) sunAt=90-T.matchLeft; }
            if (sunAt>=0) { suns++; sunT.push(Math.round(sunAt)); } if (rained) rains++; T.aiReset(T.H); }
          return {n, sunMatches:suns, rainMatches:rains, sunStarts:sunT.slice(0,20)}; })()""")
        print(r, errs)
        await b.close()
asyncio.run(main())
