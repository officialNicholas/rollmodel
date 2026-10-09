import asyncio
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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); T.knockOut(P, 'dry'); let k = 0; while (P.st === 'ko' && k < 400) { T.step(0.012); k++; }
          const p = P.pot; H.ai = null; H.st = 'play'; H.koT = 0; T.showBlobs(); H.x = p.x + 1.8; H.z = p.z + 0.4; H.y = p.y; H.air = false; H.slamCD = 0; H.paint = 1; H.immuneT = 0;
          for (let i = 0; i < 40; i++) T.step(0.012); T.useSlam(H); let j = 0; while ((H.air || H.slam) && j < 200) { T.step(0.012); j++; } for (let i = 0; i < 5; i++) T.step(0.012);
          return { st: P.st, imm: +P.immuneT.toFixed(2) }; })()""")
        print(r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s28_grace.png'); print(errs); await b.close()
asyncio.run(main())
