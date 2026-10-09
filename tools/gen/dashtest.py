import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = r"""(mode)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x = P.x + 40;
  // the most open coffin
  let best=null, bc=-1; for (const p of T.pots) { if (!T.potUp(p) || p.occ) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=7; d+=0.5){ const x=p.x+Math.sin(a/12*6.283)*d, z=p.z+Math.cos(a/12*6.283)*d; if (Math.abs(T.surfaceUnder(x,z,p.y+0.3)-p.y)>0.05) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; best=p; } }
  const p = best; P.st='play'; P.x=p.x; P.z=p.z; P.y=p.y; P.air=false; P.slamCD=0; P.paint=1; P.immuneT=0; T.enterPot(P, p); P.yaw = 0.4; P.spawnImm=false;
  T.useSlam(P); let t=0; while (P.vy > 2.5 && t < 2) { T.step(0.012); t+=0.012; }
  const x0=P.x, z0=P.z, yaw0=P.yaw, sling = mode==='old' ? T.airShot(P, 0.75, P.yaw) : null;
  let ok = false; if (mode==='fwd') ok = T.dodgeRoll(P); else if (mode==='back') ok = (window.__T.airDash ? false : null);
  if (mode==='back') { const cv=document.getElementById('cv'); const ev=(tp,yy)=>cv.dispatchEvent(new PointerEvent(tp,{pointerId:9,pointerType:'touch',clientX:195,clientY:yy,bubbles:true,isPrimary:true})); ev('pointerdown',400); ev('pointermove',430); ev('pointermove',470); ok = P.dashDir === -1; ev('pointerup',470); }
  const dashT0 = P.dashT; let t2=0, minDash = 9; while (P.air && t2 < 3) { T.step(0.012); t2+=0.012; }
  const fx=Math.sin(yaw0), fz=Math.cos(yaw0), along = (P.x-x0)*fx + (P.z-z0)*fz;
  return { mode, ok, along: +along.toFixed(2), dist: +Math.hypot(P.x-x0,P.z-z0).toFixed(2), sling: sling ? +Math.hypot(sling.x-x0, sling.z-z0).toFixed(2) : null, yawKept: Math.abs(P.yaw-yaw0) < 0.3, dashT0: +dashT0.toFixed(2), flight: +t2.toFixed(2), st: P.st, airSlingLeft: P.airSling }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for m in ['old','fwd','back','fwd','back']: print(json.dumps(await pg.evaluate(JS, m)))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
