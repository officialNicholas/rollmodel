import asyncio
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("__T.setDiff('hard')"); await pg.click('#startBtn'); await pg.wait_for_timeout(2600)
        await pg.evaluate("window.__noStep=true"); await pg.evaluate(HELP)
        await pg.evaluate("(()=>{ const op = window.__place; window.__place = (...a) => { __T.showBlobs(); op(...a); }; })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null;
          const n = __open(9) || __open(7) || __open(5); __place(P, n.x, n.z, n.h, 0); __place(H, n.x + 6, n.z + 9, n.h, 0); H.immuneT = 0;
          P.giantT = 4; P.slamCD = 0; P.paint = 1; T.useSlam(P); let k = 0; while ((P.air || P.slam) && k < 200) { T.step(0.012); P.charging = false; k++; }
          T.hold = 0; for (let i = 0; i < 12; i++) T.step(0.012);
          window.__cam = [[n.x - 9, n.h + 6.5, n.z - 11], [n.x, n.h + 1.2, n.z]];
          return { k, Hair: H.air, Hvy: +H.vy.toFixed(1) }; })()""")
        print(r); await pg.wait_for_timeout(120); await pg.screenshot(path='gen/s29_a.png')
        await pg.evaluate("(() => { for (let i = 0; i < 18; i++) __T.step(0.012); })()"); await pg.wait_for_timeout(80); await pg.screenshot(path='gen/s29_b.png')
        print(errs); await b.close()
asyncio.run(main())
