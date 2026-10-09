import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + (sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'qol/blobs.png'
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':700,'height':500}, device_scale_factor=2); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(HELP)
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("""(()=>{ window.__noStep = true; const T = __T, P = T.P, H = T.H; __flat(); __freezeAI(); T.setWx('clear', 999);
          for (let i = 0; i < 60; i++) T.step(0.012);
          __place(P, -0.55, 0, 0, Math.PI); __place(H, 0.65, 0, 0, Math.PI); P.immuneT = 0; H.immuneT = 0; P.paint = 1; H.paint = 1;
          window.__cam = [[0.05, 1.05, -2.9], [0.05, 0.38, 0]]; document.getElementById('hud').classList.add('off'); })()""")
        await pg.evaluate("window.__noStep = false"); await pg.wait_for_timeout(200); await pg.evaluate("window.__noStep = true")
        await pg.evaluate("(()=>{ const T=__T; T.P.spd=0; T.H.spd=0; })()")
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT); print(errs[:3]); await b.close()
asyncio.run(main())
