import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':400,'height':300}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); const log=[];
          for (let i=0;i<500;i++) T.step(0.012);
          log.push(['after land', T.state, P.st, P.air, P.spd.toFixed(2), P.y.toFixed(2), !!P.dry, P.charging, P.flatT, P.slam, P.rollCD]);
          H.ai=null; P.spd=0; for (let i=0;i<20;i++) { T.step(0.012); } log.push(['20 steps', P.st, P.air, P.spd.toFixed(2), !!P.dry, P.charging, P.paint.toFixed(2), P.slowK, P.turfK]);
          log.push(['roll?', T.dodgeRoll(P), P.rollT, P.rollCD, P.air, P.st]);
          return log; })()""")
        for l in r: print(l)
        print(errs[:3]); await b.close()
asyncio.run(main())
