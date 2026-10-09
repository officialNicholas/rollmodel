import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = r"""(who)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); const ai=H.ai; H.ai = null;
  let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=8; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
  for (const D of [P,H]) { D.slam=false; D.rollT=0; D.rollCD=0; D.charging=false; D.dry=false; D.giantT=0; D.power=null; D.st='play'; D.y=0; D.air=false; D.vy=0; D.spd=0; D.immuneT=0; D.flatT=0; D.stunT=0; D.stunGuard=0; D.paint=1; }
  const A = who==='P'?P:H, B = who==='P'?H:P; A.x=spot.x-1.6; A.z=spot.z; B.x=spot.x+0.6; B.z=spot.z; A.yaw=Math.PI/2; B.yaw=Math.PI/2;
  T.dodgeRoll(A); let t=0, stunAt=null; while (t<0.6) { T.step(0.012); t+=0.012; if (stunAt===null && B.stunT>0) stunAt=t; }
  const x0=B.x, z0=B.z; let t2=0; while (B.stunT>0 && t2<3) { T.step(0.012); t2+=0.012; } const moved=Math.hypot(B.x-x0,B.z-z0);
  const guard=B.stunGuard; H.ai=ai; return { who, stunned: stunAt!==null, stunLasted: +(t2 + (0.6-stunAt)).toFixed(2), movedWhileStunned: +moved.toFixed(2), guard: +guard.toFixed(2), banner: document.getElementById('bannerBig').textContent }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':400,'height':300}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for w in ['P','H']: print(json.dumps(await pg.evaluate(JS, w)))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
