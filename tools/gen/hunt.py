import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        for trial in range(4):
            r = await pg.evaluate("""(tr)=>{ const T=__T, P=T.P, H=T.H; T.genWorld(7000+tr); T.mapUsed=false; T.setDiff('hard'); T.start(); T.setAI('hard'); for(let i=0;i<150;i++) T.step(0.012); T.setWx('clear', 60);
              // the player hides in a coffin; the CPU is 8 away with the pound ready
              const p=T.pots2.find(q=>T.potUp(q)); P.x=p.x; P.z=p.z; P.y=p.y; P.air=false; P.spd=0; P.paint=1; P.immuneT=0; T.step(0.012);
              const n=T.NAVo.nodes.filter(m=>m.h===0 && m.edge===0).sort((a,b)=>Math.abs(Math.hypot(a.x-p.x,a.z-p.z)-8)-Math.abs(Math.hypot(b.x-p.x,b.z-p.z)-8))[0]; H.x=n.x; H.z=n.z; H.y=n.h; H.air=false; H.st='play'; H.slamCD=0; H.paint=1; H.ai.thinkT=0;
              let t=0, hunted=false; while(t<8 && P.st==='hide'){ T.step(0.012); t+=0.012; if (H.ai.mode==='hunt') hunted=true; }
              return {Pst:P.st, reason:P.reason, t:+t.toFixed(2), hunted}; }""", trial)
            print('hunt trial', trial, r)
        for trial in range(4):
            r = await pg.evaluate("""(tr)=>{ const T=__T, P=T.P, H=T.H; T.genWorld(7100+tr); T.mapUsed=false; T.start(); T.setAI('hard'); for(let i=0;i<150;i++) T.step(0.012); T.setWx('clear', 60);
              const p=T.pots2.find(q=>T.potUp(q)); H.x=p.x; H.z=p.z; H.y=p.y; H.air=false; H.spd=0; H.paint=0.4; H.immuneT=0; H.st='play'; T.step(0.012); const hid=H.st;
              // the player rolls up with the pound ready
              P.x=p.x+3.8; P.z=p.z; P.y=p.y; P.air=false; P.st='play'; P.slamCD=0; P.paint=1; P.spd=0;
              let t=0; while(t<1.2 && H.st==='hide'){ T.step(0.012); t+=0.012; }
              return {hid, Hst:H.st, t:+t.toFixed(2), dist:+Math.hypot(H.x-P.x,H.z-P.z).toFixed(1)}; }""", trial)
            print('flee trial', trial, r)
        await b.close()
asyncio.run(main())
