import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.evaluate("__T.setDiff('hard')")
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true")
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 60); for(let i=0;i<150;i++) T.step(0.012);
          const n=T.NAVo.nodes.find(m=>m.h===0&&m.edge===0&&T.NAVo.nodes.filter(k=>k.h===0&&k.edge===0&&Math.hypot(k.x-m.x,k.z-m.z)<7).length>130);
          H.st='play'; H.x=n.x; H.z=n.z+5; H.y=0; H.air=false; H.spd=0; H.yaw=Math.PI; H.ai.o.st='lost'; H.ai.alert=null; H.ai.thinkT=99; H.ai.seenT=0;
          P.st='play'; P.x=n.x+0.8; P.z=n.z-3; P.y=0; P.air=false; P.spd=0; P.yaw=0.3;
          T.step(0.012); return {st:H.ai.o.st, alert:H.ai.alert&&H.ai.alert.k, vis:H.ai.oVis}; })()""")
        print(r)
        await pg.wait_for_timeout(250); await pg.screenshot(path='gen/spot.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
