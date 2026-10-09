import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SETUP = r"""const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai = null;
  let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=9; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
  for (const D of [P,H]) { D.slam=false; D.missile=false; D.rollT=0; D.rollCD=0; D.charging=false; D.dry=false; D.giantT=0; D.st='play'; D.y=0; D.air=false; D.vy=0; D.spd=0; D.immuneT=0; D.flatT=0; D.slamCD=0; D.paint=1; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        # missile in flight, seen from the side-behind
        r = await pg.evaluate("(()=>{ " + SETUP + r"""
          P.x=spot.x-5; P.z=spot.z; H.x=spot.x+4; H.z=spot.z+1; P.yaw=Math.PI/2; P.charging=true; P.charge=0.8; T.fling(P,0.8);
          let t=0; while (P.vy>0.3 && t<2) { T.step(0.012); t+=0.012; } T.useSlam(P); for (let i=0;i<14;i++) T.step(0.012);
          window.__cam=[[P.x-3.2, P.y+1.4, P.z-3.0],[P.x+1.5, P.y-0.3, P.z]]; for (let k=0;k<3;k++) T.visuals(0.012,0.012); T.renderFrame(); return {missile:P.missile, y:P.y.toFixed(2), vy:P.vy.toFixed(2), spd:P.spd.toFixed(1)}; })()""")
        print('flight', r); await pg.wait_for_timeout(200); await pg.screenshot(path='ui/fx_missile.png')
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; let t=0; while (P.slam && t<2) { T.step(0.012); t+=0.012; } for (let i=0;i<8;i++) T.step(0.012); window.__cam=[[P.x-6, P.y+3.5, P.z-5],[P.x, P.y, P.z]]; for (let k=0;k<3;k++) T.visuals(0.012,0.012); T.renderFrame(); return {landedIn: t.toFixed(2)}; })()""")
        print('boom', r); await pg.wait_for_timeout(200); await pg.screenshot(path='ui/fx_boom.png')
        # giant rainbow, then the end strobe
        r = await pg.evaluate("(()=>{ " + SETUP + r"""
          P.x=spot.x; P.z=spot.z; P.giantT=4; for (let i=0;i<60;i++) T.step(0.012); window.__cam=[[P.x-4, 3.2, P.z-4.5],[P.x, 0.8, P.z]]; for (let k=0;k<20;k++) T.visuals(0.012,0.012); T.renderFrame(); return P.giantT.toFixed(2); })()""")
        print('giant', r); await pg.wait_for_timeout(200); await pg.screenshot(path='ui/fx_giant.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
