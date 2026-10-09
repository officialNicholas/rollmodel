import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SET = open('gen/threattest.py').read().split('SET = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{ " + SET + r"""
          const out = {};
          for (const [name, gt, air] of [['ground', 0.15, false], ['air', 0.1, true], ['notGiant', 0, false]]) {
            P.x=spot.x; P.z=spot.z; P.y=0; P.air=false; P.vy=0; P.slam=false; P.slamCD=0; P.paint=1; P.giantT=gt; P.st='play'; H.ai=null; H.x=spot.x+40;
            if (air) { P.air=true; P.vy=4; P.y=1.5; }
            T.useSlam(P); let t=0, minG=9, Rmax=0, gotGiantAtLand=null; while (P.slam && t<3) { const was = P.giantT; Rmax = Math.max(Rmax, T.slamRadius(P)); T.step(0.012); t+=0.012; if (P.slam) minG=Math.min(minG,P.giantT); else gotGiantAtLand = was > 0; }
            out[name] = { t: +t.toFixed(2), minGiantDuringPound: +minG.toFixed(3), landedAsGiant: gotGiantAtLand, radius: Rmax, giantAfter: P.giantT };
            for (let i=0;i<5;i++) T.step(0.012);
          }
          return out; })()""")
        print(json.dumps(r, indent=1)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
