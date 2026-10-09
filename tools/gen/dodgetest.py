import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000)
        await pg.evaluate("window.__noLoop = true"); await pg.evaluate(HELP)
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, dt = 0.012, out = { you: [], cpu: [] };
          T.start(); __flat(); T.setWx('clear', 999);
          // the CPU pounds right next to you; you jump at different moments before impact
          for (const jumpAt of [-1, 0.15, 0.3, 0.45, 0.6, 0.7]) {
            __freezeAI(); __place(P, 0, 0, 0, 0); __place(H, 1.5, 0, 0, 0); H.slamCD = 0; H.paint = 1; H.ai = window.__hai; P.paint = 1;
            T.useSlam(H); const eta = H.slamEta; let t = 0, jumped = false;
            for (let i = 0; i < 120 && H.slam; i++) { t += dt; if (!jumped && jumpAt >= 0 && t >= jumpAt) { T.jump(P); jumped = true; } P.spd = 0; T.step(dt); }
            out.you.push({ jumpAt, eta: +eta.toFixed(2), impactAt: +t.toFixed(2), result: P.st === 'ko' ? 'KO' : 'dodged/safe' }); if (P.st === 'ko') { P.st = 'play'; P.koT = 0; }
            for (let i = 0; i < 30; i++) T.step(dt);
          }
          // you pound next to the hard CPU, 12 times: how often does it hop it?
          T.setAI('hard'); let dodges = 0, kos = 0;
          for (let k = 0; k < 12; k++) {
            __place(P, 0, 0, 0, 0); __place(H, 1.6, 0.5, 0, 0); T.aiReset(H); H.paint = 1; P.slamCD = 0; P.paint = 1; H.immuneT = 0;
            for (let i = 0; i < 20; i++) { T.step(dt); __place(P, 0, 0, 0, 0); P.paint = 1; }
            H.x = 1.6; H.z = 0.5; T.useSlam(P); for (let i = 0; i < 120 && P.slam; i++) T.step(dt);
            if (H.st === 'ko') { kos++; H.st = 'play'; H.koT = 0; } else dodges++; for (let i = 0; i < 40; i++) T.step(dt);
          }
          out.cpu = { dodges, kos }; return out; })()""")
        print(json.dumps(r, indent=1)); print(errs[:3]); await b.close()
asyncio.run(main())
