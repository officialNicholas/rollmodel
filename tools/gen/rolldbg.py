import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SET = open('gen/threattest.py').read().split('SET = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{ " + SET + r"""
          P.x=spot.x; P.z=spot.z; P.yaw=0; H.x=spot.x+1.4; H.z=spot.z+1.6; H.yaw=Math.atan2(P.x-H.x, P.z-H.z); P.spd=0;
          H.ai.rollWind = 0.28; H.ai.rollAt = P; const seen=[]; for (let i=0;i<40;i++) { T.step(0.012); P.spd = 0; T.visuals(0.012,0.012); if (i>=18 && i<=30) seen.push([i, H.ai.rollWind.toFixed(3), H.rollT.toFixed(2), H.rollCD.toFixed(2), H.air, H.st, H.charging, H.slam, H.knockT, P.stunT.toFixed(2), H.dashT]); }
          return seen; })()""")
        for x in r: print(x)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
