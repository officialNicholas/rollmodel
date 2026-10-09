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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, o = T.orb; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null;
          const n = __open(7) || __open(5.5); __place(P, n.x - 4.5, n.z, n.h, Math.PI / 2); __place(H, n.x + 30, n.z + 30, 0, 0); H.st = 'ko'; H.koT = 1e9;
          T.orbSpawn(); o.x = n.x; o.z = n.z; o.base = n.h; o.tx = n.x + 0.01; o.tz = n.z; for (let i = 0; i < 70; i++) { P.spd = 0; P.charging = true; T.step(0.012); o.tx = n.x; o.tz = n.z; }
          window.__cam = [[P.x - 3.2, n.h + 2.6, P.z + 1.2], [n.x, n.h + 1, n.z]]; return { on: o.on, k: o.k }; })()""")
        print('orb', r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s25_orb.png')
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, o = T.orb; window.__cam = null; P.charging = false; const n = __open(9) || __open(7);
          __place(P, n.x - 7, n.z, n.h, Math.PI / 2); P.spd = 5.4; T.takeOrb(P); H.st = 'play'; H.koT = 0; __place(H, n.x + 2.5, n.z + 0.4, n.h, 0); H.immuneT = 0;
          let k = 0, sq = -1; for (; k < 160; k++) { H.spd = 0; T.step(0.012); P.yaw = Math.PI / 2; if (sq < 0 && H.flatT > 0) sq = k; if (sq >= 0 && k - sq > 2) break; }
          return { giant: +P.giantT.toFixed(2), sq }; })()""")
        print('giant', r); await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(260); await pg.evaluate("window.__noStep=true"); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s25_giant.png')
        print('errors', errs); await b.close()
asyncio.run(main())
