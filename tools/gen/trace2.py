import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_timeout(1500)
        await pg.evaluate("(()=>{ __T.genWorld(777); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); })()")
        await pg.click('#startBtn'); await pg.wait_for_timeout(50)
        r = await pg.evaluate("""()=>{ const T=__T, P=T.P, H=T.H; T.setAI('hard'); P.st='ko'; P.koT=1e9; const log=[];
          for (let i=0;i<1400 && T.state==='play';i++){ T.step(0.012);
            const t=90-T.matchLeft; if (t>11.5 && t<16 && i%8===0){ const a=H.ai, gp=a.goPot, n=a.tgt>=0?T.NAVo.nodes[a.tgt]:null;
              log.push([t.toFixed(2), a.mode, H.x.toFixed(1), H.z.toFixed(1), H.y.toFixed(2), H.spd.toFixed(1), H.yaw.toFixed(2), H.charging, gp?[gp.x,gp.z,gp.y,gp.st,gp.ink.toFixed(2)].join('/'):'-', n?[n.x,n.z,n.h].join('/'):'-', a.pi+'/'+(a.path?a.path.length:0), H.steer.toFixed(2), a.plan?a.plan.kind:'-'].join(' ')); } }
          return log; }""")
        for l in r: print(l)
        await b.close()
asyncio.run(main())
