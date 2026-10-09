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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null; H.st = 'ko'; H.koT = 1e9;
          let best = null; for (const n of T.NAVo.nodes) { if (n.h !== 0) continue; let run = 0; for (let d = 1; d <= 26; d++) { const x = n.x, z = n.z + d; if (T.surfaceUnder(x, z, 0.5, true) !== 0 || T.blockedAt(x, z, 0)) break; run = d; } if (run >= 24) { best = n; break; } }
          if (!best) return 'none'; __place(P, best.x, best.z, 0, 0); P.spd = 5.4; T.takeOrb(P); for (let i = 0; i < 110; i++) { T.step(0.012); P.yaw = 0; } return "ok"; })()""")
        print(r)
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(450); await pg.evaluate("window.__noStep=true"); await pg.wait_for_timeout(300)
        await pg.screenshot(path='gen/s27_giant.png')
        print(await pg.evaluate("({spd: +__T.P.spd.toFixed(1), g: +__T.P.giantT.toFixed(1)})"))
        r = await pg.evaluate(r'''(() => { const T = __T, P = T.P; P.slamCD = 0; P.paint = 1; T.useSlam(P); let k = 0; while ((P.air || P.slam) && k < 200) { T.step(0.012); k++; } for (let i = 0; i < 4; i++) T.step(0.012); return { g: P.giantT, k }; })()''')
        print('slam', r); await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(160); await pg.evaluate("window.__noStep=true"); await pg.wait_for_timeout(100)
        await pg.screenshot(path='gen/s27_slam.png'); print(errs); await b.close()
asyncio.run(main())
