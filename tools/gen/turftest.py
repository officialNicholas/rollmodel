import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000)
        await pg.evaluate("window.__noLoop = true"); await pg.evaluate(HELP)
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, dt = 0.012, out = {};
          T.start(); __flat(); T.setWx('clear', 999); __freezeAI(); H.st = 'ko'; H.koT = 1e9; H.x = 99;
          const lane = (team) => { for (let x = -20; x <= 20; x += 0.8) T.addSplat(x, 0, 0, Math.PI / 2, 1.4, 0, false, true, team); };
          const run = (team) => { __place(P, -18, 0.5, 0, Math.PI / 2); P.spd = 5.4; P.paint = 0.5; for (let i = 0; i < 40; i++) { T.step(dt); P.power = null; } P.paint = 0.5; const p0 = P.paint; let sp = 0, n = 0; for (let i = 0; i < 120; i++) { T.step(dt); P.power = null; P.yaw = Math.PI / 2; sp += P.spd; n++; } return { spd: +(sp / n).toFixed(2), paintPerSec: +((P.paint - p0) / (120 * dt)).toFixed(3), turf: P.turf }; };
          out.bare = run(-1);
          lane(0); out.own = run(0);
          lane(1); out.enemy = run(1);
          return out; })()""")
        print(json.dumps(r)); print(errs[:3]); await b.close()
asyncio.run(main())
