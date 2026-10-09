import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_timeout(2000); await pg.click('#startBtn'); await pg.wait_for_timeout(200)
        await pg.evaluate("__T.state='paused'")
        # 1) drain a coffin with the player in it: auto-eject, sink, rise elsewhere
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; T.state='play'; H.st='ko'; H.koT=999; while(P.air) T.step(0.012);
          const p=T.pots2[0]; P.x=p.x; P.z=p.z; P.y=p.y; P.paint=0.3; P.air=false; P.spd=0; T.step(0.012);
          const log=[]; log.push(['entered', P.st, p.st]); p.ink=0.05; let t=0, x0=p.x, z0=p.z, sinkAt=-1, downAt=-1, teleAt=-1, riseAt=-1, upAt=-1;
          while (t<9) { T.step(0.012); t+=0.012; if (T.wx==='sun'||T.wx==='warn') { T.setWx('clear', 30); }
            if (sinkAt<0 && p.st==='sink') sinkAt=t; if (downAt<0 && p.st==='down') downAt=t; if (teleAt<0 && p.tele.visible) teleAt=t; if (riseAt<0 && p.st==='rise') riseAt=t; if (upAt<0 && riseAt>0 && p.st==='up') { upAt=t; break; } }
          return {log, Pst:P.st, sinkAt, downAt, teleAt, riseAt, upAt, moved:Math.hypot(p.x-x0,p.z-z0), ink:p.ink, newPos:[p.x,p.y,p.z], gvis:p.g.visible}; })()""")
        print('drain cycle', json.dumps(r))
        # 2) pound a coffin with the holy water inside
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; H.st='play'; H.koT=0; H.immuneT=0;
          const p=T.pots2.find(q=>T.potUp(q)&&!q.occ); H.x=p.x; H.z=p.z; H.y=p.y; H.air=false; H.paint=0.5; T.step(0.012); const hid=H.st;
          P.x=p.x+1.2; P.z=p.z; P.y=p.y; P.air=false; P.slamCD=0; P.paint=1; P.st='play'; P.immuneT=0;
          const ok=T.useSlam(P); let n=0; while((P.air||P.slam)&&n<300){ T.step(0.012); n++; }
          return {hid, ok, Hst:H.st, reason:H.reason, kos:P.kos, potOcc:!!p.occ}; })()""")
        print('pound coffin', json.dumps(r))
        # 3) pound from out of range does nothing
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; H.st='play'; H.immuneT=0; H.koT=0;
          const p=T.pots2.find(q=>T.potUp(q)&&!q.occ); H.x=p.x; H.z=p.z; H.y=p.y; H.air=false; T.step(0.012); const hid=H.st; H.immuneT=0;
          P.x=p.x+4; P.z=p.z; P.y=p.y; P.air=false; P.slamCD=0; P.paint=1; P.st='play';
          const ok=T.useSlam(P); let n=0; while((P.air||P.slam)&&n<300){ T.step(0.012); n++; }
          return {hid, ok, Hst:H.st}; })()""")
        print('pound far', json.dumps(r))
        print('errors', errs)
        await b.close()
asyncio.run(main())
