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
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 60); H.ai.thinkT=99;
          const n=T.NAVo.nodes.find(m=>m.h===0&&m.edge===0&&Math.hypot(m.x-H.x,m.z-H.z)>12&&T.NAVo.nodes.filter(k=>k.h===0&&Math.hypot(k.x-m.x,k.z-m.z)<5).length>50) || T.NAVo.nodes.find(m=>m.h===0&&m.edge===0&&Math.hypot(m.x-H.x,m.z-H.z)>12);
          P.x=n.x; P.z=n.z; P.y=0; P.air=false; P.spd=0; P.paint=1; P.slamCD=0; P.st='play';
          T.matchLeft = 0.2; T.useSlam(P); const before = T.teamCov(0); const log=[];
          let k=0; while(T.state==='play' && k<300){ T.step(0.012); k++; if (k%5===0) log.push([T.matchLeft.toFixed(2), P.slam, P.air, T.state].join(' ')); }
          return {before:+before.toFixed(2), after:+T.teamCov(0).toFixed(2), endYou:+T.endInfo.you.toFixed(2), steps:k, state:T.state, log}; })()""")
        print({k: v for k, v in r.items() if k != 'log'}); print(r['log'][:14])
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='gen/buzzer.png')
        # control: no pound in the air, the match ends right on time
        await pg.wait_for_timeout(3000); await pg.click('#endBtn'); await pg.wait_for_timeout(900)
        r = await pg.evaluate("""(()=>{ const T=__T; T.matchLeft=0.05; for(let i=0;i<10;i++) T.step(0.012); return T.state; })()""")
        print('control state after time', r)
        print('errors', errs)
        await b.close()
asyncio.run(main())
