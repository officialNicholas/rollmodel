import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SETUP = r"""const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); const ai = H.ai; H.ai = null;
  let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=8; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
  for (const D of [P,H]) { D.slam=false; D.missile=false; D.rollT=0; D.rollCD=0; D.rollBuf=0; D.charging=false; D.knockT=0; D.dry=false; D.flung=false; D.flingC=0; D.giantT=0; D.power=null; D.pot=null; D.lastHit=null; D.koT=0; D.reason=null; D.st='play'; D.y=0; D.air=false; D.vy=0; D.spd=0; D.immuneT=0; D.flatT=0; D.kx=D.kz=0; D.slamCD=0; D.paint=1; }"""
TIMING = "(rollAt)=>{ " + SETUP + r"""
  P.x=spot.x; P.z=spot.z; H.x=spot.x+1.0; H.z=spot.z; P.yaw = Math.atan2(H.x-P.x, H.z-P.z); H.yaw = P.yaw + Math.PI;
  T.useSlam(H); const eta0 = H.slamEta; let t=0, rolled=false, intoRoll=null;
  while ((H.slam || t < 0.05) && t < 2.5) { if (!rolled && eta0 - t <= rollAt) { rolled = T.dodgeRoll(P); var t0 = t; } P.x = Math.min(P.x, H.x - 0.5); T.step(0.012); t += 0.012; }
  H.ai = ai; return { impactIntoRoll: +(t - t0).toFixed(2), rolled, P: P.st }; }"""
DIST = "(dry)=>{ " + SETUP + r"""
  H.x = spot.x + 40; P.x=spot.x-4; P.z=spot.z; P.yaw=Math.PI/2; P.dry = !!dry; if (dry) P.paint = 0;
  for (let i=0;i<120;i++) T.step(0.012); const cruise=P.spd, x0=P.x; const rolled = T.dodgeRoll(P); let peak=0; for (let i=0;i<100;i++) { T.step(0.012); peak=Math.max(peak,P.spd); }
  H.ai = ai; return { dry: !!dry, rolled, cruise: +cruise.toFixed(2), peak: +peak.toFixed(2), extra: +((P.x - x0) - cruise*1.2).toFixed(2), paint: +P.paint.toFixed(3) }; }"""
CRUSH = "(kind)=>{ " + SETUP + r"""
  P.x=spot.x-1.6; P.z=spot.z; H.x=spot.x+0.6; H.z=spot.z; P.yaw=Math.PI/2; H.yaw=Math.PI/2; H.spd=0;
  if (kind==='giant') P.giantT = 4; else if (kind==='roller') P.power = { type: 'roller', t: 5 };
  T.dodgeRoll(P); let t=0; while (t<0.5 && H.st==='play') { T.step(0.012); t+=0.012; }
  H.ai = ai; return { kind, H: H.st, reason: H.reason, flat: H.flatT > 0, banner: document.getElementById('bannerBig').textContent }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':400,'height':300}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for ra in [0.15, 0.4, 0.47, 0.56, 0.65]:
            print('timing', ra, json.dumps(await pg.evaluate(TIMING, ra)))
        for d in [False, True]: print('dist', json.dumps(await pg.evaluate(DIST, d)))
        for k in ['plain', 'giant', 'roller']: print('crush', json.dumps(await pg.evaluate(CRUSH, k)))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
