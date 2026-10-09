import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs();
          const out = {};
          // H hiding in a coffin, P flings into it
          const p = T.pots.find(q => T.potUp(q) && !q.occ); if (!p) return 'no coffin';
          H.ai_ = H.ai; H.ai = null; H.slamCD = 0; H.paint = 1; T.enterPot(H, p); H.immuneT = 0; H.spawnImm = false;
          P.x = p.x - 0.2; P.z = p.z - 0.2; P.y = p.y + 0.5; P.air = true; P.vy = -1; P.flung = true; P.spd = 9; P.st = 'play'; P.yaw = Math.atan2(p.x - P.x, p.z - P.z);
          for (let i=0;i<3;i++) T.step(0.012);
          out.bounced = H.st === 'play' && !H.pot; out.banner = document.getElementById('bannerBig').textContent; out.cd = +H.slamCD.toFixed(2);
          out.canPoundNow = T.useSlam(H); let t = 0; while (H.slamCD > 0 && t < 2) { T.step(0.012); t += 0.012; } out.lockedFor = +t.toFixed(2);
          // the dash sound runs clean
          T.AU.init(); try { T.AU.dash(); out.dash = 'ok'; } catch (e) { out.dash = String(e); }
          return out; })()""")
        print(json.dumps(r))
        # the pound button turns forward mid-fling
        await pg.evaluate("""(()=>{ const T=__T, P=T.P; window.__noLoop = false; P.slamCD = 0; P.paint = 1; P.st='play'; P.air=false; P.y=T.surfaceUnder(P.x,P.z,9); P.charging = true; P.charge = 0.8; T.fling(P, 0.8); })()""")
        await pg.wait_for_timeout(250)
        print('fwd class', await pg.evaluate("document.getElementById('slamBtn').className"), await pg.evaluate("document.getElementById('slamBtn').getAttribute('aria-label')"))
        await pg.screenshot(path='ui/m_fwd.png', clip={'x': 120, 'y': 640, 'width': 150, 'height': 200})
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
