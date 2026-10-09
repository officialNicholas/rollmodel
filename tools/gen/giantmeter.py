import asyncio, json
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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = {}; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null; H.st = 'ko'; H.koT = 1e9;
          const n = __open(9) || __open(7) || __open(5) || __open(3.5); __place(P, n.x - 3, n.z, n.h, Math.PI / 2); P.paint = 0.4; P.spd = 5.4;
          T.takeOrb(P); for (let i = 0; i < 60; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.afterPickup = +P.paint.toFixed(3);
          for (let i = 0; i < 40; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.afterRolling = +P.paint.toFixed(3);
          P.slamCD = 0; T.useSlam(P); for (let i = 0; i < 80 && (P.air || P.slam); i++) T.step(0.012); out.afterPound = +P.paint.toFixed(3);
          out.barClassMid = document.getElementById('bar').className; T.flingIt(P, 0.3); for (let i = 0; i < 120 && P.air; i++) T.step(0.012); out.afterFling = +P.paint.toFixed(3); out.giantLeft = +P.giantT.toFixed(2);
          out.barClass = document.getElementById('bar').className;
          return out; })()""")
        print(r)
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(400); await pg.evaluate("window.__noStep=true"); await pg.wait_for_timeout(200)
        await pg.screenshot(path='gen/s26_meter.png', clip={'x': 0, 'y': 744, 'width': 390, 'height': 100})
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P; P.giantT = 0; const n = __open(5) || __open(3.5); __place(P, n.x - 3, n.z, n.h, Math.PI / 2); P.spd = 5.4; T.step(0.012); const p0 = P.paint; for (let i = 0; i < 100; i++) { T.step(0.012); P.yaw = Math.PI / 2; } return { drainAfter: +(p0 - P.paint).toFixed(3), barClass: document.getElementById('bar').className }; })()""")
        print('after giant', r, errs); await b.close()
asyncio.run(main())
