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
        for na in [True, False]:
            await pg.evaluate(f"window.__noAssist = {'true' if na else 'false'}")
            r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; H.st = 'ko'; H.koT = 1e9; const res = [];
              const pot = T.pots2[0]; pot.x = 0; pot.z = 0; pot.y = 0; pot.g.position.set(0, 0, 0); pot.occ = null; pot.ink = 1; pot.cool = 0; pot.st = 'up';
              for (const [off, d, c] of [[0.15, 7, 0.5], [-0.2, 8, 0.6], [0.25, 6, 0.45], [0.3, 9, 0.62], [-0.12, 10, 0.75], [0.6, 7, 0.5]]) {
                if (P.pot) { P.pot.occ = null; P.pot = null; } pot.occ = null; pot.cool = 0; pot.ink = 1;
                __place(P, -d, 0, 0, Math.PI / 2 + off); P.paint = 0.6; T.flingIt(P, c); let k = 0, hid = false;
                while (k < 200) { T.step(0.012); k++; if (P.st === 'hide') { hid = true; break; } if (!P.air && k > 30) break; }
                res.push({ off, d, c, inCoffin: hid, miss: +Math.hypot(P.x - pot.x, P.z - pot.z).toFixed(2) });
                if (P.st === 'hide') { P.st = 'play'; P.pot = null; pot.occ = null; }
              }
              return res; })()""")
            print('no assist' if na else 'assist', json.dumps(r))
        print('errors', errs); await b.close()
asyncio.run(main())
