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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; H.st = 'ko'; H.koT = 1e9; const n = __open(9), out = {};
          const run = (z, dil) => { __place(P, n.x - 8, z, 0, Math.PI / 2); P.spd = 5.4; P.paint = 1; for (let i = 0; i < 100; i++) { T.step(0.012); P.yaw = Math.PI / 2; P.dilT = dil ? 99 : 0; } return +(1 - P.paint).toFixed(4); };
          out.bare = run(n.z, false); out.ownFull = run(n.z, false); out.bare2 = run(n.z + 3, true); out.ownDil = run(n.z + 3, false);
          return out; })()""")
        print('drain over 1.2s', r, errs); await b.close()
asyncio.run(main())
