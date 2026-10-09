import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
exec(open('gen/threattest.py').read().split('async def main')[0].split("U='")[0])
SET = open('gen/threattest.py').read().split('SET = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{ " + SET + r"""
          P.x=spot.x; P.z=spot.z; P.yaw=0; H.x=spot.x; H.z=spot.z-13; H.yaw=0; H.ai=null; H.charging=true; H.charge=0.8; T.fling(H,0.8); let t=0; const o=[]; while (H.vy>0.3 && t<2) { T.step(0.012); P.spd=0; t+=0.012; }
          o.push(['pre', H.air, H.flingC, H.y.toFixed(2), H.vy.toFixed(2), (H.z-P.z).toFixed(2)]);
          T.useSlam(H); o.push(['slam', H.slam, H.missile]); for (let i=0;i<10;i++) { T.step(0.012); P.spd=0; T.visuals(0.012,0.012); const c = T.missileHit(H); o.push([i, H.slam, H.missile, H.y.toFixed(2), (H.z-P.z).toFixed(2), T.threat ? T.threat.k : '-', c ? (c.z-P.z).toFixed(2) : 'nf', c ? Math.hypot(c.x-P.x,c.z-P.z).toFixed(2) : 'nf', document.getElementById('threat').classList.contains('on')]); } return o; })()""")
        for x in r: print(x)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
