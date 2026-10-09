import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        shots = [(0, 'fx_c1')]
        for n, tag in shots:
            r = await pg.evaluate(r"""(n)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x = P.x + 30;
              let spot=null, bc=-1; for (const nd of T.NAVo.nodes) { if (nd.h!==0||nd.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=9; d+=0.5){ const x=nd.x+Math.sin(a/12*6.283)*d, z=nd.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=nd; } }
              P.x=spot.x; P.z=spot.z-6; P.y=0; P.air=false; P.vy=0; P.yaw=0; P.slamCD=0; P.paint=1; P.st='play';
              for (let i=0;i<40;i++) { T.step(0.012); T.visuals(0.012, 0.05); }
              P.charging=true; P.charge=0.8; T.fling(P,0.8); let t=0; while (P.vy>0.3 && t<2) { T.step(0.012); T.visuals(0.012,0.012); t+=0.012; }
              document.getElementById('flash').style.display='none'; document.getElementById('banner').style.display='none'; H.x = P.x + 3; H.z = P.z + 60; T.useSlam(P); let q=0; while (P.slam && q<300) { T.step(0.012); T.visuals(0.012,0.012); q++; } for (let i=0;i<22;i++) { T.step(0.012); T.visuals(0.012,0.012); } T.renderFrame(); return {missile:P.missile, slam:P.slam, y:P.y.toFixed(2)}; }""", n)
            print(tag, r); await pg.wait_for_timeout(150); await pg.screenshot(path=f'ui/{tag}.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
