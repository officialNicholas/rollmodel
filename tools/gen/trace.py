import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    lvl = sys.argv[1] if len(sys.argv)>1 else 'hard'
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_timeout(1500)
        await pg.evaluate("(()=>{ __T.genWorld(777); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); })()")
        await pg.click('#startBtn'); await pg.wait_for_timeout(50)
        r = await pg.evaluate("""(lvl)=>{ const T=__T, P=T.P, H=T.H; T.setAI(lvl); P.st='ko'; P.koT=1e9; const log=[]; let last='';
          for (let i=0;i<7600 && T.state==='play';i++){ T.step(0.012);
            if (i%25===0){ const a=H.ai; const s=[(90-T.matchLeft).toFixed(1), a.mode, a.poundAt, H.slamCD.toFixed(1), H.paint.toFixed(2), (a.need||0).toFixed(2), H.st, T.wx].join(' '); log.push(s); } }
          return {log, slams:H.slams, cov:T.teamCov(1)}; }""", lvl)
        print('slams', r['slams'], 'cov', round(r['cov'],1))
        for l in r['log'][::2][:160]: print(l)
        print(errs)
        await b.close()
asyncio.run(main())
