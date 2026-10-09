import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SET = r"""const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); const ai=H.ai;
  let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=9; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
  for (const D of [P,H]) { D.slam=false; D.missile=false; D.rollT=0; D.rollCD=0; D.charging=false; D.dry=false; D.giantT=0; D.st='play'; D.y=0; D.air=false; D.vy=0; D.spd=0; D.immuneT=0; D.flatT=0; D.stunT=0; D.stunGuard=0; D.slamCD=0; D.paint=1; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        # roll: H 2 units ahead-left of P, facing P, AI forced into the stun-roll wind-up
        r = await pg.evaluate("(()=>{ " + SET + r"""
          P.x=spot.x; P.z=spot.z; P.yaw=0; H.x=spot.x+1.4; H.z=spot.z+1.6; H.yaw=Math.atan2(P.x-H.x, P.z-H.z); P.spd=0;
          H.ai.rollWind = 0.28; H.ai.rollAt = P; const seen=[]; for (let i=0;i<40;i++) { T.step(0.012); P.spd = 0; T.visuals(0.012, 0.012); const th=document.getElementById('threat'); if (i%5===0) seen.push([i, th.classList.contains('on') ? document.getElementById('threatText').textContent : '-', H.rollT.toFixed(2), P.stunT.toFixed(2)]); if (i===8) { T.renderFrame(); window.__shot=true; } }
          return seen; })()""")
        print('roll', r)
        await pg.evaluate("(()=>{ const T=__T; T.H.ai.rollWind=0.28; T.H.ai.rollAt=T.P; T.H.rollT=0; T.H.rollCD=0; T.P.stunT=0; T.P.stunGuard=0; T.H.x=T.P.x+1.4; T.H.z=T.P.z+1.6; T.H.yaw=Math.atan2(T.P.x-T.H.x, T.P.z-T.H.z); for (let i=0;i<6;i++){ T.step(0.012); T.visuals(0.012,0.012);} T.renderFrame(); })()")
        await pg.wait_for_timeout(150); await pg.screenshot(path='ui/threat_roll.png')
        # missile at you
        r = await pg.evaluate("(()=>{ " + SET + r"""
          window.__noAssist = true; P.x=spot.x; P.z=spot.z; P.yaw=0; H.x=spot.x; H.z=spot.z-13; H.yaw=0; H.ai=null; H.charging=true; H.charge=0.8; T.fling(H,0.8); let t=0; while (H.vy>0.3 && t<2) { T.step(0.012); P.spd=0; t+=0.012; }
          T.useSlam(H); const seen=[]; for (let i=0;i<10;i++) { T.step(0.012); P.spd=0; T.visuals(0.012,0.012); seen.push([document.getElementById("threat").classList.contains("on") ? document.getElementById("threatText").textContent : "-", T.state, H.missile, H.slam, H.st, P.st, JSON.stringify(T.missileHit(H) && {x:+T.missileHit(H).x.toFixed(1), z:+T.missileHit(H).z.toFixed(1)}), +P.x.toFixed(1), +P.z.toFixed(1), +H.x.toFixed(1), +H.z.toFixed(1)].join(" ")); } T.renderFrame(); H.ai=ai; return seen.join('\n'); })()""")
        print('missile', r); await pg.wait_for_timeout(150); await pg.screenshot(path='ui/threat_missile.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
