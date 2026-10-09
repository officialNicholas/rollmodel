import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate('window.__noLoop=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        # 1) the player slingshots into the holy water's coffin
        for tr in range(3):
            r = await pg.evaluate("""(tr)=>{ const T=__T, P=T.P, H=T.H; T.genWorld(9100+tr); T.mapUsed=false; T.setDiff('hard'); T.start(); T.setAI('hard'); for(let i=0;i<150;i++) T.step(0.012); T.setWx('clear', 60);
              const p=T.pots2.find(q=>T.potUp(q)&&q.y===0); H.x=p.x; H.z=p.z; H.y=0; H.air=false; H.spd=0; H.paint=0.5; H.st='play'; T.step(0.012); const hid=H.st; H.ai=null;
              // find a clear lane 5 units out
              let best=null; for (let k=0;k<16;k++){ const a=k/16*6.283, x=p.x+Math.sin(a)*5, z=p.z+Math.cos(a)*5; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) continue; let ok=true; for(let d=0.5;d<5;d+=0.5){ const px=p.x+Math.sin(a)*d, pz=p.z+Math.cos(a)*d; if (T.blockedAt(px,pz,0.6)) ok=false; } if (ok){ best=a; break; } }
              if (best===null) return {skip:true};
              P.st='play'; P.x=p.x+Math.sin(best)*5; P.z=p.z+Math.cos(best)*5; P.y=0; P.air=false; P.spd=0; P.yaw=best+Math.PI; P.paint=1; P.slamCD=5; P.immuneT=0;
              // the fling power that lands right on the coffin
              let c=0.08; while(c<1 && (5.4*(0.9+1.7*c))*((5.6*(0.55+0.8*c))/15 + Math.sqrt(2*((5.6*(0.55+0.8*c))**2/30)/(15*1.45))) < 4.9) c+=0.01;
              P.charging=true; P.charge=c; T.step(0.012); P.charging=true; P.charge=c;
              const fl = (()=>{ return true; })();
              return {hid, c:+c.toFixed(2)}; }""", tr)
            if r.get('skip'): print('skip'); continue
            r2 = await pg.evaluate("""(c)=>{ const T=__T, P=T.P, H=T.H; T.P.charging=true; T.P.pullTgt=c; T.P.charge=c; T.flingP && 0;
              // simulate the release through the public path
              const ok = (function(){ try { T.P.charging=true; return true; } catch(e){ return false; } })();
              return ok; }""", r['c'])
            r3 = await pg.evaluate("""(c)=>{ const T=__T, P=T.P, H=T.H; T.flingIt(P, c); let k=0, ev=false; while(k<200){ T.step(0.012); k++; if (H.st!=='hide') { ev=true; break; } } return {evicted:ev, Hst:H.st, Hair:H.air, t:+(k*0.012).toFixed(2), Pst:P.st}; }""", r['c'])
            print('player flings into its coffin:', r['hid'], r3)
        # 2) Hard bounces the hiding player out
        for tr in range(3):
            r = await pg.evaluate("""(tr)=>{ const T=__T, P=T.P, H=T.H; T.genWorld(9200+tr); T.mapUsed=false; T.start(); T.setAI('hard'); T.aiReset(H); for(let i=0;i<150;i++) T.step(0.012); T.setWx('clear', 60);
              const p=T.pots2.find(q=>T.potUp(q)&&q.y===0); P.x=p.x; P.z=p.z; P.y=0; P.air=false; P.spd=0; P.paint=1; P.st='play'; P.immuneT=0; T.step(0.012); const hid=P.st;
              const n=T.NAVo.nodes.filter(m=>m.h===0&&m.edge===0).sort((a,b)=>Math.abs(Math.hypot(a.x-p.x,a.z-p.z)-7)-Math.abs(Math.hypot(b.x-p.x,b.z-p.z)-7))[0];
              H.x=n.x; H.z=n.z; H.y=0; H.air=false; H.st='play'; H.spd=0; H.paint=1; H.slamCD=5; H.yaw=Math.atan2(p.x-H.x,p.z-H.z); H.ai.thinkT=0; H.ai.seenT=0;
              let t=0, kinds=[]; while(t<6 && P.st==='hide'){ T.step(0.012); t+=0.012; if (H.ai.plan && !kinds.includes(H.ai.plan.kind)) kinds.push(H.ai.plan.kind); }
              return {hid, Pst:P.st, t:+t.toFixed(2), plans:kinds}; }""", tr)
            print('hard evicts hider:', r)
        print('errors', errs)
        await b.close()
asyncio.run(main())
