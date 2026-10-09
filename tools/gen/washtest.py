import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(300)
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); H.ai=null; H.x=P.x+40;
          const r0 = T.rivals.find(r => r.y === 0) || T.rivals[0]; r0.on = true; r0.k = 1; r0.target = 1; r0.g.visible = true; r0.life = 99;
          // holy water paint all around the puddle, some of yours too
          for (let a=0;a<12;a++) for (const d of [2,3.5,5,6.5]) T.addSplat(r0.x+Math.cos(a/12*6.283)*d, 0, r0.z+Math.sin(a/12*6.283)*d, 0, 1.2, 0, false, true, a%4===0 ? 0 : 1);
          const before = [T.teamCov(0), T.teamCov(1)];
          P.x=r0.x; P.z=r0.z; P.y=0; P.air=false; P.st='play'; P.slamCD=0; P.paint=1; P.spd=0; T.useSlam(P); let t=0; while (P.slam && t<3) { T.step(0.012); t+=0.012; }
          return { before: before.map(v=>+v.toFixed(2)), after: [T.teamCov(0), T.teamCov(1)].map(v=>+v.toFixed(2)), pop: document.getElementById('pop').textContent }; })()""")
        print(json.dumps(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
