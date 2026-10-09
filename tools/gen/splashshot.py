import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for seed, tag in [(int(sys.argv[1]) if len(sys.argv) > 1 else 31, 'a')]:
            ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ mode: 'duel', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.evaluate('window.__rect = ' + ('true' if len(sys.argv) > 2 and sys.argv[2] == 'rect' else 'false') + '; window.__back = ' + (sys.argv[3] if len(sys.argv) > 3 else '2.2')); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
            r = await pg.evaluate(r"""(seed)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.genWorld(seed); T.mapUsed=false; T.showMenu(); T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x=P.x+40; T.setWx('clear', 99);
              // a standing piece with open floor in front of it; prefer round ones (trees, drums)
              let best=null; for (const b of T.BOXES) { if (b[4] > 0.05 || b[5] < 1.2) continue; const cx=(b[0]+b[1])/2, cz=(b[2]+b[3])/2, hz = (b[3]-b[2])/2;
                const x = cx, z = b[2] - 1.5; let ok = T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0) && T.surfaceUnder(x, z - 5, 0.3) === 0; if (!ok) continue; const sc = (window.__rect ? (b[6]==='c'?-5:2) : (b[6]==='c'?2:0) + (b[7]==='column'?3:0)) + b[5]*0.2; if (!best || sc > best.sc) best = { b, x, z, sc }; }
              if (!best) return 'none';
              const x = best.x, z = best.z - 0.2; P.x=x; P.z=z; P.y=0; P.air=false; P.yaw=0; P.spd=0; P.st='play'; P.slamCD=0; P.paint=1;
              for (let i=0;i<20;i++){ T.step(0.012); P.spd=0; P.x=x; P.z=z; P.yaw=0; }
              P.giantT = window.__rect ? 0 : 6; T.useSlam(P); let t=0; while (P.slam && t < 2) { T.step(0.012); t+=0.012; }
              // walk back a bit so the camera sees the wall
              const bx = P.x, bz = P.z - (window.__back || 2.2); for (let i=0;i<90;i++) { T.step(0.012); P.spd=0; P.x=bx; P.z=bz; P.yaw=0; P.giantT=0; T.visuals(0.016, 0.05); } T.renderFrame(); return [best.b, T.theme || '']; }""", seed)
            print(seed, r); await pg.wait_for_timeout(6500); await pg.evaluate("(()=>{ for (let i=0;i<5;i++) __T.visuals(0.016,0.016); __T.renderFrame(); })()"); await pg.screenshot(path=f'ui/splash_{tag}.png')
            print('errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
