import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = r"""(mode)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start();
  for (let i=0;i<110;i++) T.step(0.012); T.showBlobs();
  const ai = H.ai; H.ai = null;
  // open ground for both
  let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=7; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
  if (!spot) return 'no spot';
  for (const D of [P,H]) { D.slam=false; D.missile=false; D.rollT=0; D.rollCD=0; D.rollBuf=0; D.charging=false; D.knockT=0; D.dry=false; D.flung=false; D.flingC=0; D.giantT=0; D.pot=null; D.lastHit=null; D.koT=0; D.reason=null; D.st='play'; }
  P.x=spot.x; P.z=spot.z; P.y=0; P.air=false; P.vy=0; P.st='play'; P.spd=0; P.paint=1; P.immuneT=0; P.rollCD=0; P.flatT=0; P.kx=P.kz=0;
  H.x=spot.x+1.2; H.z=spot.z; H.y=0; H.air=false; H.vy=0; H.st='play'; H.spd=0; H.slamCD=0; H.paint=1; H.immuneT=0; H.flatT=0; H.kx=H.kz=0;
  const out = {};
  if (mode === 'speed') {
    P.yaw = Math.atan2(-1, 0); H.x = spot.x + 30; // H far away
    for (let i=0;i<120;i++) T.step(0.012); const cruise = P.spd, x0=P.x, z0=P.z;
    T.dodgeRoll(P); const prof=[]; let t=0; for (let i=0;i<100;i++){ T.step(0.012); t+=0.012; if (i%6===5) prof.push([t.toFixed(2), P.spd.toFixed(2), P.rollT.toFixed(2)]); }
    // distance in 1.2 s vs cruising 1.2 s
    out.cruise = cruise.toFixed(2); out.prof = prof; out.dist = Math.hypot(P.x-x0, P.z-z0).toFixed(2); out.cruiseDist = (cruise*1.2).toFixed(2); out.cd = P.rollCD.toFixed(2); out.paint = P.paint.toFixed(3);
    out.again = T.dodgeRoll(P); return out;
  }
  const toward = mode === 'into', faceAway = Math.atan2(P.x - H.x, P.z - H.z);
  P.yaw = toward ? faceAway + Math.PI : mode === 'side' ? faceAway + Math.PI/2 : faceAway;
  T.useSlam(H); let rolled=false, t=0, hitDuringRoll=null;
  while ((H.slam || t < 0.05) && t < 2.5) { const eta = H.slamEta - H.slamT; if (mode !== 'none' && mode !== 'side' && !rolled && eta < 0.2) { rolled = T.dodgeRoll(P); } const was = P.rollT > 0; T.step(0.012); t+=0.012; if (!H.slam && hitDuringRoll === null) hitDuringRoll = was; }
  out.clear=bc; out.mode=mode; out.rolled=rolled; out.P=P.st; out.dist=Math.hypot(P.x-H.x,P.z-H.z).toFixed(2); out.landedDuringRoll=hitDuringRoll; out.Hst=H.st; out.Hflat=H.flatT.toFixed(2); out.Pflat=P.flatT.toFixed(2); out.pop=document.getElementById('pop').textContent; out.reason=P.reason; document.getElementById('pop').textContent='';
  H.ai = ai; return out; }"""
JS2 = r"""(who)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true;
  // ram test: the roller runs straight into a standing blob
  const A = who==='P'?P:H, B = who==='P'?H:P; const ai=H.ai; H.ai=null;
  let spot=null; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let ok=true; for (let d=0.5; d<=7; d+=0.5){ for (const s of [-1,0,1]) { const x=n.x+d, z=n.z+s*0.6; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) { ok=false; break; } } if(!ok)break; } if (ok) { spot=n; break; } }
  for (const D of [P,H]) { D.st='play'; D.y=0; D.air=false; D.vy=0; D.spd=0; D.immuneT=0; D.flatT=0; D.rollCD=0; D.paint=1; D.kx=D.kz=0; D.charging=false; }
  A.x=spot.x; A.z=spot.z; A.yaw=Math.PI/2; B.x=spot.x+2.2; B.z=spot.z; B.yaw=-Math.PI/2;
  T.dodgeRoll(A); let t=0, flatB=false, flatA=false; while (t<0.6) { T.step(0.012); t+=0.012; if (B.flatT>0) flatB=true; if (A.flatT>0) flatA=true; }
  H.ai=ai; return {who, flatB, flatA, gap: Math.hypot(A.x-B.x,A.z-B.z).toFixed(2)}; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':400,'height':300}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for mode in ['none', 'away', 'into', 'side', 'away', 'into', 'side']:
            print(json.dumps(await pg.evaluate(JS, mode)), errs[:2])
        for who in ['P','H','P','H']:
            print(json.dumps(await pg.evaluate(JS2, who)), errs[:2])
        await b.close()
asyncio.run(main())
