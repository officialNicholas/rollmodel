import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(300)
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<60;i++) T.step(0.012); T.showBlobs();
          // an open patch of floor
          let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=9; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
          const out = [];
          for (const [dz, yawOff, label] of [[-5, 0, 'aimed'], [-5, 0.9, 'off to the side'], [-5, Math.PI, 'flying away']]) {
            Object.assign(P, { x: spot.x, z: spot.z, y: 0, yaw: 0, spd: 0, st: 'play', air: false, slam: false, missile: false, immuneT: 0 });
            Object.assign(H, { x: spot.x, z: spot.z + dz, y: 2.6, yaw: yawOff, spd: 7, st: 'play', air: true, vy: 0, slam: true, missile: true, missileHang: 0 });
            T.visuals(0.016, 0.016); const th = document.getElementById('threat'), c = T.missileHit(H);
            out.push([label, th.classList.contains('on') ? document.getElementById('threatText').textContent : '-', c && +Math.hypot(c.x - P.x, c.z - P.z).toFixed(2)]);
          }
          H.slam = false; H.missile = false; H.air = false; H.y = 0; T.visuals(0.016, 0.016);
          return out; })()""")
        print(r, errs[:3]); await b.close()
asyncio.run(main())
