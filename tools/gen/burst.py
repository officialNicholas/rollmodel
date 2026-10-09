import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("__T.setDiff('hard')")
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true")
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 60); for(let i=0;i<150;i++) T.step(0.012);
          const p=T.pots2.find(q=>T.potUp(q)&&q.y===0); P.x=p.x; P.z=p.z; P.y=p.y; P.air=false; P.spd=0; P.paint=0.9; P.st='play'; T.step(0.012);
          const inC = P.st; P.slamCD = 0; P.paint = 1;
          // the holy water stands 4 away, inside the circle
          H.ai = null; H.st='play'; H.immuneT=0; H.x=p.x+4; H.z=p.z; H.y=T.surfaceUnder(H.x,H.z,0.5); H.air=false; H.spd=0;
          return {inC, x:p.x, z:p.z}; })()""")
        print('in coffin:', r)
        await pg.wait_for_timeout(300)
        print('button:', await pg.evaluate("document.getElementById('slamBtn').className"), '|', await pg.evaluate("document.getElementById('slamBtn').getAttribute('aria-label')"))
        await pg.screenshot(path='gen/burst0.png')
        r2 = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; const cov0=T.teamCov(0); const p=T.pots2.find(q=>Math.abs(q.x-P.x)<0.01&&Math.abs(q.z-P.z)<0.01);
          const ok=T.useSlam(P); const out={ok, Pst:P.st, air:P.air, vy:P.vy, coffin:p.st, Hst:H.st, Hreason:H.reason, cov:+(T.teamCov(0)-cov0).toFixed(2)};
          for(let i=0;i<14;i++) T.step(0.012);
          window.__cam=[[p.x+5.5, p.y+3.2, p.z+6.5],[p.x, p.y+2.4, p.z]]; out.debris=1; return out; })()""")
        print('burst:', r2)
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/burst1.png')
        await pg.evaluate("(()=>{ for(let i=0;i<16;i++) __T.step(0.012); })()")
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/burst2.png')
        r3 = await pg.evaluate("""(()=>{ const T=__T, P=T.P; let k=0; while(P.air && k<400){ T.step(0.012); k++; } return {landed:!P.air, t:+(k*0.012).toFixed(2), st:P.st, slamCD:+P.slamCD.toFixed(1)}; })()""")
        print('landing:', r3)
        print('errors', errs)
        await b.close()
asyncio.run(main())
