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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = {}; window.__hai = H.ai; H.ai = null;
          // the holy water pounds you while you're giant
          __place(P, 0, 0, 0, 0); P.giantT = 4; P.charging = true; __place(H, 3, 0, 0, 0); H.slamCD = 0; H.paint = 1; T.useSlam(H);
          for (let i = 0; i < 120 && (H.air || H.slam); i++) { P.charging = true; P.spd = 0; T.step(0.012); }
          out.youAfter = { st: P.st, giantT: P.giantT, imm: +P.immuneT.toFixed(2), air: P.air };
          // you pound the giant holy water
          P.charging = false; __place(P, -8, 6, 0, 0); P.slamCD = 0; P.paint = 1; __place(H, -5, 6, 0, 0); H.giantT = 4; T.useSlam(P);
          for (let i = 0; i < 120 && (P.air || P.slam); i++) { H.spd = 0; T.step(0.012); }
          out.cpuAfter = { st: H.st, giantT: H.giantT };
          // a normal-size one still gets knocked out
          __place(P, 8, 6, 0, 0); P.slamCD = 0; __place(H, 11, 6, 0, 0); H.giantT = 0; H.immuneT = 0; T.useSlam(P);
          for (let i = 0; i < 120 && (P.air || P.slam); i++) { H.spd = 0; T.step(0.012); }
          out.normalAfter = H.st;
          return out; })()""")
        print(json.dumps(r), errs); await b.close()
asyncio.run(main())
