import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = r"""(args)=>{ const [who, off, targetRolls] = args; const T=__T, P=T.P, H=T.H; window.__noLoop = true;
  if (T.state !== 'play') { T.start(); for (let i=0;i<110;i++) T.step(0.012); }
  T.showBlobs(); const ai = H.ai; H.ai = null;
  let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=9; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
  for (const D of [P,H]) { D.slam=false; D.missile=false; D.rollT=0; D.rollCD=0; D.rollBuf=0; D.charging=false; D.knockT=0; D.dry=false; D.flung=false; D.flingC=0; D.giantT=0; D.pot=null; D.lastHit=null; D.koT=0; D.reason=null; D.st='play'; D.y=0; D.air=false; D.vy=0; D.spd=0; D.immuneT=0; D.flatT=0; D.kx=D.kz=0; D.slamCD=0; D.paint=1; }
  const A = who==='P'?P:H, B = who==='P'?H:P;
  A.x = spot.x - 3.5; A.z = spot.z; B.x = spot.x + 3.2; B.z = spot.z;  // B straight ahead along +x, about 6.7 away
  const toB = Math.atan2(B.x - A.x, B.z - A.z); A.yaw = toB + off;
  // fling A, then fire the missile near the top of the arc
  A.charging = true; A.charge = 0.75; T.fling(A, 0.75); const btn = document.getElementById('slamBtn');
  let t = 0, fwdSeen = false; while (A.vy > 0.5 && t < 2) { T.step(0.012); t += 0.012; T.visuals(0.0001, 0.012); if (btn.classList.contains('fwd')) fwdSeen = true; }
  const yaw0 = A.yaw, pred0 = T.missileHit ? null : null;
  T.useSlam(A); const isMissile = A.missile; const yawAfterAssist = A.yaw;
  if (targetRolls) { B.yaw = toB + Math.PI/2; } // B sidesteps
  let rolledB = false; while (A.slam && t < 4) { if (targetRolls && !rolledB && A.slamT > 0.05) { rolledB = T.dodgeRoll(B); } T.step(0.012); t += 0.012; }
  const miss = Math.hypot(A.x - B.x, A.z - B.z);
  H.ai = ai;
  return { who, off, isMissile, fwdSeen, turnAssist: +(yawAfterAssist - yaw0).toFixed(2), turnFlight: +(A.yaw - yawAfterAssist).toFixed(2), landGap: +miss.toFixed(2), Bst: B.st, reason: B.reason, rolledB }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':400,'height':300}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(300)
        for args in [['P', 0.0, False], ['P', 0.45, False], ['P', 0.9, False], ['H', 0.0, False], ['H', 0.45, False], ['H', 0.9, False], ['H', 0.2, True], ['P', 0.2, True]]:
            print(json.dumps(await pg.evaluate(JS, args)), errs[:2])
        await b.close()
asyncio.run(main())
