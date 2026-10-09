import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ window.__noLoop=true; __T.genWorld(11); __T.mapUsed=false; __T.showMenu(); __T.start(); })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, A = 26.4; H.ai = null; H.st = 'ko'; H.koT = 1e9; H.x = 99; T.setWx('clear', 999);
          for (let i = 0; i < 200; i++) T.step(0.012);
          const z0 = 18, th = 80, yaw = Math.PI / 2 - th * Math.PI / 180; P.st = 'play'; P.air = false; P.y = 0; P.x = A - 1.5; P.z = z0; P.yaw = yaw; P.spd = T.cfg.speed * 3; P.turn = 0; P.kx = P.kz = 0; P.paint = 1; P.charging = false; P.giantT = 0; P.immuneT = 0; P.dry=false;
          const tr = []; for (let i = 0; i < 200; i++) { T.steerIn = 0; T.step(0.012); if (i % 12 === 0 || P.air) tr.push([i, P.x.toFixed(2), P.y.toFixed(2), P.spd.toFixed(1), P.st, P.air, P.yaw.toFixed(2)]); } return tr; })()""")
        for x in r: print(x)
        await b.close()
asyncio.run(main())
