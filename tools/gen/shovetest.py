import asyncio, json
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read()
PREP = src.split('PREP = r"""')[1].split('"""')[0]; HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e) + str(getattr(e,'stack',''))[:400]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(PREP); await pg.evaluate(HELP); await pg.evaluate("__flat()")
        for lv in ['hard', 'hard22', 'medium']:
            r = await pg.evaluate(r"""(lv) => { const T = __T, P = T.P, H = T.H; T.setAI(lv); let off = 0, plans = 0, trials = 0, traps = 0, trapTry = 0;
              for (let t = 0; t < 10; t++) {
                const A = 26.4, ez = -12 + t * 2.6, d = 5 + (t % 3) * 1.5;
                __place(P, A - 2.5, ez, 0, 0); P.charging = true; P.charge = 0; P.immuneT = 0;
                __place(H, A - 2.5 - d, ez + (t % 2 ? 1 : -1), 0, Math.PI / 2); T.aiReset(H); H.slamCD = 4; H.paint = 1; H.immuneT = 0; T.matchLeft = 60;
                const k0 = H.kos; let planned = false;
                for (let i = 0; i < 400 && P.st === "play"; i++) { if (!(P.knockT > 0) && !P.air) { P.charging = true; P.spd = 0; } T.step(0.012); if (H.ai && H.ai.plan && H.ai.plan.kind === 'shove') planned = true; }
                trials++; if (planned) plans++; if (P.st === 'ko' && H.kos > k0) off++;
                if (P.st === 'ko') { P.st = 'play'; P.koT = 0; } if (H.st === 'ko') { H.st = 'play'; H.koT = 0; }
              }
              // landing trap: you fling past it with its pound ready
              for (let t = 0; t < 10; t++) {
                const n = __open(9); __place(H, n.x + 1.5, n.z + (t % 3 - 1) * 1.2, 0, -Math.PI / 2); T.aiReset(H); H.slamCD = 0; H.paint = 1; T.matchLeft = 60;
                const c = 0.55 + (t % 4) * 0.12, L = T.flightFor(c, 0).d; __place(P, n.x + 1.5 - L - 0.5 + (t % 2), n.z, 0, Math.PI / 2); P.immuneT = 0;
                for (let i = 0; i < 6; i++) T.step(0.012);
                const s0 = H.slams; T.flingIt(P, c); trapTry++;
                for (let i = 0; i < 160 && P.st === 'play'; i++) T.step(0.012);
                if (H.slams > s0 && P.st === 'ko') traps++;
                if (P.st === 'ko') { P.st = 'play'; P.koT = 0; } if (H.st === 'ko') { H.st = 'play'; H.koT = 0; }
              }
              return { lv, trials, plans, knockedOff: off, trapTry, traps }; }""", lv)
            print(r)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
