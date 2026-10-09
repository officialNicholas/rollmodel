import asyncio, json
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read()
PREP = src.split('PREP = r"""')[1].split('"""')[0]; HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_v30.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate(PREP); await pg.evaluate(HELP); await pg.evaluate("__flat()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = []; window.__hai = H.ai; H.ai = null;
          const pot = T.pots2[0], pot2 = T.pots2[1];
          for (const [px, pz, edge] of [[1.5, 0, false], [3, 0.5, false], [2.2, 0, true], [4.1, 0, false]]) {
            const cx = edge ? 26.4 - 4.2 : 0, cz = edge ? 0 : -6;
            pot.x = cx; pot.z = cz; pot.y = 0; pot.st = 'up'; pot.occ = null; pot.ink = 1; pot.cool = 0; pot.g.visible = true;
            __place(H, cx, cz, 0, 0); T.enterPot(H, pot); H.slamCD = 0; H.paint = 1;
            __place(P, cx + px, cz + pz, 0, Math.PI); P.immuneT = 0; P.charging = true;
            const k0 = H.kos; T.useSlam(H); const sp = +P.spd.toFixed(1), vy = +P.vy.toFixed(1);
            let i = 0; for (; i < 300 && P.st === 'play'; i++) T.step(0.012);
            out.push({ dist: Math.hypot(px, pz).toFixed(1), edge, pushedSpd: sp, vy, stAfter: P.st, reason: P.reason, creditedToCPU: H.kos > k0, moved: +Math.hypot(P.x - cx - px, P.z - cz - pz).toFixed(1) });
            if (P.st === 'ko') { P.st = 'play'; P.koT = 0; }
          }
          // you're hiding in a coffin beside it
          pot.x = 0; pot.z = 6; pot.st = 'up'; pot.occ = null; pot.ink = 1; pot.cool = 0; pot2.x = 2.5; pot2.z = 6; pot2.y = 0; pot2.st = 'up'; pot2.occ = null; pot2.ink = 1; pot2.cool = 0; pot2.g.visible = true;
          __place(H, 0, 6, 0, 0); T.enterPot(H, pot); H.slamCD = 0; __place(P, 2.5, 6, 0, 0); T.enterPot(P, pot2); P.immuneT = 0; P.spawnImm = false;
          T.useSlam(H); out.push({ hiding: true, stAfter: P.st, spd: +P.spd.toFixed(1), air: P.air });
          return out; })()""")
        for x in r: print(x)
        print('errors', errs); await b.close()
asyncio.run(main())
