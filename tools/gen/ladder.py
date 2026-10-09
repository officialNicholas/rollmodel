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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = {}; H.st = 'ko'; H.koT = 1e9; let x = -20;
          const run = (name, giant, act) => { x += 9.5; const zz = x > 20 ? 9 : -9; __place(P, x > 20 ? x - 40 : x, zz, 0, 0); P.spd = 0; P.paint = 1; P.slamCD = 0; P.giantT = giant ? 4 : 0;
            // only the splat counts: stand still and freeze the trail
            const c0 = T.teamCov(0); act(); for (let i = 0; i < 200 && (P.air || P.slam); i++) { T.step(0.012); P.spd = Math.min(P.spd, 0.001); P.charging = true; }
            P.charging = false; out[name] = +(T.teamCov(0) - c0).toFixed(2); };
          run('hop', false, () => T.jump(P));
          run('pound', false, () => T.useSlam(P));
          run('giantHop', true, () => T.jump(P));
          run('giantPound', true, () => T.useSlam(P));
          return out; })()""")
        print(json.dumps(r), errs); await b.close()
asyncio.run(main())
