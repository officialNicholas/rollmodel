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
        # coffin lock: aiming a fling at a coffin
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; H.ai = null; H.x = 40; H.z = 40; H.st = 'ko'; H.koT = 1e9;
          const p = T.pots2.find(q => T.potUp(q) && !q.occ && q.y === 0); if (!p) return 'none';
          let a = 0, ok = false; for (let k = 0; k < 16 && !ok; k++) { a = k / 16 * 6.283; ok = true; for (let d = 1; d <= 7; d += 0.5) { const x = p.x - Math.sin(a) * d, z = p.z - Math.cos(a) * d; if (T.surfaceUnder(x, z, 0.5, true) !== 0 || T.blockedAt(x, z, 0)) ok = false; } }
          T.showBlobs(); __place(P, p.x - Math.sin(a) * 6.5, p.z - Math.cos(a) * 6.5, 0, a + 0.18); P.paint = 0.5; T.startCharge(P); P.charge = 0.42;
          window.__cam = [[P.x - Math.sin(P.yaw) * 5, 3.8, P.z - Math.cos(P.yaw) * 5], [p.x, 0, p.z]]; return { ok }; })()""")
        print('coffin', r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s23_coffin.png')
        # a match: the holy water slingshot-painting, seen from above after ~50 s
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; P.charging = false; window.__cam = null; T.start(); return T.state; })()""")
        await pg.wait_for_timeout(2600)
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.aiReset(P); T.setAI('hard'); for (let i = 0; i < 4200 && T.state === 'play'; i++) { T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012); }
          window.__cam = [[H.x - 9, H.y + 15, H.z - 9], [H.x, H.y, H.z]]; return { you: +T.teamCov(0).toFixed(1), cpu: +T.teamCov(1).toFixed(1) }; })()""")
        print('match', r); await pg.wait_for_timeout(600); await pg.screenshot(path='gen/s23_cpu.png')
        print('errors', errs); await b.close()
asyncio.run(main())
