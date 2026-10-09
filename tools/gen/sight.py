import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.genWorld(4242); T.mapUsed=false; T.setDiff('hard'); T.start(); T.setAI('hard'); for(let i=0;i<150;i++) T.step(0.012);
          const out = {};
          // a tall box to hide behind
          const b = T.BOXES.filter(b=>b[4]===0 && b[5]>1.8 && Math.abs((b[0]+b[1])/2)<14 && Math.abs((b[2]+b[3])/2)<14)[0] || T.BOXES.filter(b=>b[4]===0 && b[5]>1.2)[0];
          const cx=(b[0]+b[1])/2, cz=(b[2]+b[3])/2, hw=(b[1]-b[0])/2;
          const put=(D,x,z,yaw)=>{ D.x=x; D.z=z; D.y=T.surfaceUnder(x,z,0.3); D.st='play'; D.air=false; if (yaw!==undefined) D.yaw=yaw; };
          // clear view straight ahead, 12 away
          put(H, cx - hw - 1.5, cz - 12, 0); put(P, cx - hw - 1.5, cz - 0.5); out.clear12 = T.aiCanSee(H,P);
          // same spot, CPU facing away
          H.yaw = Math.PI; out.facingAway = T.aiCanSee(H,P);
          // facing away but you're right behind it (it hears you)
          put(P, H.x, H.z + 3); out.behindClose = T.aiCanSee(H,P);
          // the tower between you
          put(H, cx - hw - 4, cz, Math.PI/2); put(P, cx + hw + 4, cz); out.towerBetween = T.aiCanSee(H,P); out.hy=[H.y,P.y];
          // too far
          put(H, -20, -20, Math.atan2(40,40)); put(P, 20, 20); out.far = T.aiCanSee(H,P);
          // a pound leap is loud: behind it, out of sight, 15 away
          put(H, cx - hw - 4, cz, -Math.PI/2); put(P, cx + hw + 4, cz); P.slam = true; out.poundBehindTower = T.aiCanSee(H,P); P.slam=false;
          return {out, tower:[cx,cz,b[5]]}; })()""")
        print(r)
        # memory: it sees you, you duck behind the tower, it keeps a guess then loses you
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; const ai=H.ai; ai.o=null; T.aiSee(H); const s0=ai.o.st;
          P.x=H.x; P.z=H.z+8; P.y=H.y; H.yaw=0; P.st='play'; T.aiSee(H); const s1=[ai.o.st, ai.oVis];
          P.x=H.x+40; P.z=H.z+40; const res=[]; for (let k=0;k<100;k++){ T.step(0.06); } T.aiSee(H); res.push(ai.o.st, ai.alert&&ai.alert.k);
          return {start:s0, seen:s1, afterGone:res}; })()""")
        print(r)
        print('errors', errs)
        await b.close()
asyncio.run(main())
