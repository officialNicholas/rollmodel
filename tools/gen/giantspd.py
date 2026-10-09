import asyncio, json
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read()
PREP = src.split('PREP = r"""')[1].split('"""')[0]; HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(PREP); await pg.evaluate(HELP); await pg.evaluate("__flat()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = {}; H.st = 'ko'; H.koT = 1e9;
          __place(P, -20, 0, 0, Math.PI / 2); P.spd = 5.4; for (let i = 0; i < 60; i++) T.step(0.012); out.normal = +P.spd.toFixed(2);
          P.giantT = 5; let t05 = 0; for (let i = 0; i < 120; i++) { T.step(0.012); P.yaw = Math.PI / 2; if (i === 41) t05 = P.spd; } out.giantAfterHalfSec = +t05.toFixed(2); out.giantTop = +P.spd.toFixed(2);
          out.dist1s = 'n/a'; P.giantT = 0; for (let i = 0; i < 160; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.after2s = +P.spd.toFixed(2);
          T.setWx('rain', 99); for (let i = 0; i < 200; i++) T.step(0.012); __place(P, -20, 3, 0, Math.PI / 2); P.spd = 10; P.giantT = 5; for (let i = 0; i < 120; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.giantInRain = +P.spd.toFixed(2);
          return out; })()""")
        print(r, errs); await b.close()
asyncio.run(main())
