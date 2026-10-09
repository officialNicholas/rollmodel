import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("window.__noLoop = true"); await pg.evaluate(HELP)
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, dt = 0.012, out = [];
          T.start(); out.push(['after start', T.teamCov(0).toFixed(2), T.teamCov(1).toFixed(2), T.NSv]); __flat(); out.push(['after flat', T.teamCov(0).toFixed(2), T.NSv]);
          T.setWx('clear', 999); __freezeAI(); H.st = 'ko'; H.koT = 1e9; H.x = 99;
          __place(P, -18, 0, 0, Math.PI / 2); P.spd = 5.4; for (let i = 0; i < 40; i++) T.step(dt);
          out.push(['run', P.turf, P.x.toFixed(2), P.st, T.teamCov(0).toFixed(3), T.teamCov(1).toFixed(3), T.paintedA.slice(0,0).length]);
          return out; })()""")
        for l in r: print(l)
        print(errs[:3]); await b.close()
asyncio.run(main())
