import asyncio, sys
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'gen/s31_splats.png'
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(5131); __T.mapUsed=false; })()")
        await pg.evaluate("__T.setDiff('hard')"); await pg.click('#startBtn'); await pg.wait_for_timeout(2600)
        await pg.evaluate("window.__noStep=true"); await pg.evaluate(HELP)
        await pg.evaluate("(()=>{ const op = window.__place; window.__place = (...a) => { __T.showBlobs(); op(...a); }; })()")
        r = await pg.evaluate(r"""(() => { Math.random = (() => { let s = 4242; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null; H.st = 'ko'; H.koT = 0.01; H.x = 999;
          const n = __open(9) || __open(7); const cx = n.x, cz = n.z;
          const at = (x, z, yaw) => { __place(P, cx + x, cz + z, n.h, yaw); P.paint = 1; P.slamCD = 0; };
          const run = k => { for (let i = 0; i < k; i++) { T.step(0.012); } };
          // a few hops, some flings, a pound, and the holy water's pound over it
          at(-6, -6, 0.6); P.spd = 5.4; for (let j = 0; j < 4; j++) { run(25); T.jump(P); run(40); }
          at(5, -7, -0.4); T.flingIt(P, 0.5); run(90); at(-7, 3, 1.9); T.flingIt(P, 0.9); run(110);
          at(1, 1, 0); T.useSlam(P); run(90);
          H.st = 'play'; H.koT = 0; __place(H, cx + 4, cz + 4, n.h, 0); H.slamCD = 0; H.paint = 1; T.useSlam(H); run(90); __place(H, cx + 30, cz + 30, n.h, 0);
          at(-3, 6, 3); P.spd = 5; run(80); P.giantT = 0;
          P.charging = true; P.spd = 0;
          window.__cam = [[cx - 2, n.h + 17, cz - 9], [cx, n.h, cz + 0.5]]; return 'ok'; })()""")
        print(r); await pg.wait_for_timeout(500); await pg.screenshot(path=OUT); print(errs); await b.close()
asyncio.run(main())
