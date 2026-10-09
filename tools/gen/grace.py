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
        await pg.evaluate(PREP); await pg.evaluate(HELP)
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = []; T.setAI('hard'); T.setWx('clear', 999);
          for (let t = 0; t < 4; t++) {
            T.knockOut(P, 'dry'); let k = 0; while (P.st === 'ko' && k < 400) { T.step(0.012); k++; }
            const p = P.pot; if (!p) { out.push('no coffin'); continue; }
            // the hard CPU waits right beside the coffin with its pound ready
            H.st = 'play'; H.koT = 0; H.x = p.x + 1.6; H.z = p.z; H.y = p.y; H.air = false; H.slamCD = 0; H.paint = 1; H.immuneT = 0; T.aiReset(H);
            const s0 = H.slams; let safeIn = true; const stay = 1 + t * 0.9;
            for (let i = 0; i < stay / 0.012; i++) { T.step(0.012); if (P.st === 'ko') { safeIn = false; break; } }
            const res = { stay: +stay.toFixed(1), aliveInCoffin: safeIn, cpuPoundsWhileInCoffin: H.slams - s0 };
            if (safeIn) { T.jump(P); const ex = T.runT; let i = 0; for (; i < 300; i++) { T.step(0.012); if (P.st === 'ko') break; } res.immAtExit = 1; res.koAfterExit = P.st === 'ko' ? +(T.runT - ex).toFixed(2) : 'survived 3.6s'; }
            out.push(res); if (P.st === 'ko') { let q = 0; while (P.st === 'ko' && q < 600) { T.step(0.012); q++; } }
          }
          return out; })()""")
        for x in r: print(x)
        print('errors', errs); await b.close()
asyncio.run(main())
