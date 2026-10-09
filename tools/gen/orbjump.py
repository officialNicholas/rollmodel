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
        for assist in [False, True]:
            r = await pg.evaluate(r"""(assist) => { const T = __T, P = T.P, H = T.H, o = T.orb; H.st = 'ko'; H.koT = 1e9; const res = []; let got = 0;
              for (const [off, d] of [[0.3, 3], [-0.45, 3.5], [0.6, 2.5], [0.2, 4.5], [-0.7, 3], [0.5, 4], [1.2, 3]]) {
                const n = __open(7); T.orbSpawn(); o.k = 1; o.x = n.x; o.z = n.z; o.base = 0; o.tx = n.x; o.tz = n.z;
                __place(P, n.x - d, n.z, 0, Math.PI / 2 + off); P.spd = 5.4; P.giantT = 0; P.ai = assist ? null : {};
                T.step(0.012); T.jump(P);
                let k = 0; while (k < 100 && P.giantT <= 0) { T.step(0.012); o.tx = n.x; o.tz = n.z; k++; }
                res.push(P.giantT > 0); if (P.giantT > 0) got++; P.giantT = 0; P.ai = null;
              }
              return { assist, got, res: res.join(',') }; }""", assist)
            print(r)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
