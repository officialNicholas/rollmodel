import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ __T.genWorld(5); __T.mapUsed=false; __T.showMenu(); __T.start(); window.__noStep = true; })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; H.ai = null; H.st = 'ko'; H.koT = 1e9; H.x = 99;
          for (let i = 0; i < 200; i++) T.step(0.012);
          for (let i = 0; i < 14; i++) T.addSplat(P.x - 3 + (i % 4) * 2, 0, P.z + 2 + Math.floor(i / 4) * 2, i, 1.6, T.dryClock, false, true, i % 2);
          P.st = 'ko'; P.koT = 1e9; window.__cam = [[P.x, 7, P.z - 3], [P.x, 0, P.z + 4]];
          T.forceSun(); let n = 0; for (; n < 4000 && !(T.wx === 'dusk' && T.wxLeft < 0.15); n++) T.step(0.012); return [T.wx, +T.wxLeft.toFixed(2)]; })()""")
        print(r)
        await pg.screenshot(path='qol/soak_0.png')
        await pg.evaluate("(()=>{ for (let i = 0; i < 14; i++) __T.step(0.012); })()")
        for k, t in enumerate([120, 340, 560, 1000]):
            await pg.evaluate(f"(()=>{{ for (let i = 0; i < {t // 12 if k == 0 else (t - [120,340,560,1000][k-1]) // 12}; i++) __T.step(0.012); }})()")
            await pg.wait_for_timeout(120)
            await pg.screenshot(path=f'qol/soak_{k+1}.png')
        print(await pg.evaluate("__T.wx"), errs[:2]); await b.close()
asyncio.run(main())
