import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true")
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 60); for(let i=0;i<120;i++) T.step(0.012);
          const ok=m=>m.h===0&&m.edge===0&&T.NAVo.nodes.filter(k=>k.h===0&&k.edge===0&&Math.hypot(k.x-m.x,k.z-m.z)<6).length>95;
          const n=T.NAVo.nodes.find(ok) || T.NAVo.nodes.find(m=>m.h===0&&m.edge===0);
          H.ai=null; H.st='play'; H.x=n.x; H.z=n.z; H.y=0; H.air=false; H.spd=0; H.paint=1; H.slamCD=0; H.immuneT=0;
          P.st='play'; P.x=n.x-4.6; P.z=n.z-1.2; P.y=0; P.air=false; P.spd=0; P.yaw=Math.atan2(H.x-P.x,H.z-P.z)+0.35; P.immuneT=0;
          T.useSlam(H); for(let i=0;i<26;i++) T.step(0.012); })()""")
        await pg.wait_for_timeout(500); await pg.screenshot(path='gen/ring.png')
        r = await pg.evaluate("""(()=>{ const T=__T; let k=0; while(T.H.slam&&k<200){ T.step(0.012); k++; } return T.P.st; })()""")
        print('player after landing', r, 'errors', errs)
        await b.close()
asyncio.run(main())
