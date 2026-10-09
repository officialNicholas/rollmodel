import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        for tr in range(4):
            r = await pg.evaluate("""(tr)=>{ const T=__T, P=T.P, H=T.H; T.genWorld(8100+tr); T.mapUsed=false; T.setDiff('hard'); T.start(); T.setAI('hard'); for(let i=0;i<150;i++) T.step(0.012); T.setWx('clear', 60);
              const p=T.pots2.find(q=>T.potUp(q)&&q.y===0); H.x=p.x; H.z=p.z; H.y=p.y; H.air=false; H.spd=0; H.paint=0.9; H.st='play'; H.immuneT=0; T.step(0.012); const hid=H.st; H.slamCD=0; H.paint=1;
              // the player walks up to 4 units, facing the coffin, pound on cooldown so the CPU has no reason to flee early
              const a=Math.random()*6.28; P.st='play'; P.x=p.x+Math.cos(a)*4; P.z=p.z+Math.sin(a)*4; P.y=T.surfaceUnder(P.x,P.z,0.5); P.air=false; P.spd=0; P.slamCD=5; P.immuneT=0;
              let t=0; while(t<2 && H.st==='hide'){ T.step(0.012); t+=0.012; }
              return {hid, Hst:H.st, Hair:H.air, Pst:P.st, Preason:P.reason, t:+t.toFixed(2), coffin:p.st}; }""", tr)
            print(r)
        await b.close()
asyncio.run(main())
