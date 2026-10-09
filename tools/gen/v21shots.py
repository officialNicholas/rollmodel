import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
HELP = open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/gen/v20test.py').read().split('HELP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("__T.setDiff('hard')")
        await pg.click('#startBtn'); await pg.wait_for_timeout(2600)
        await pg.evaluate("window.__noStep=true")
        await pg.evaluate(HELP)
        await pg.evaluate("(()=>{ const op = window.__place; window.__place = (...a) => { __T.showBlobs(); op(...a); }; })()")
        # paint a bit of the floor first so the splats read against something
        await pg.evaluate("(()=>{ const T=__T; T.setWx('clear', 999); })()")
        # 1) aim lock: pulling back with the holy water roughly ahead
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; const n = __open(7) || __open(5.5) || __open(4.5);
          __place(H, n.x + 3.5, n.z + 0.8, n.h, 0); window.__hai = H.ai; H.ai = null; H.immuneT = 0;
          __place(P, n.x - 4, n.z, n.h, Math.PI / 2 + 0.22); P.paint = 1; T.startCharge(P); P.charge = 0.62;
          window.__cam = [[P.x - Math.sin(P.yaw) * 5.5, n.h + 3.6, P.z - Math.cos(P.yaw) * 5.5], [n.x + 2, n.h, n.z]];
          return { lock: true }; })()""")
        await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s21_lock.png')
        # 2) missile mid-dive from the side
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; P.charging = false; P.charge = 0; window.__cam = null; const n = __open(7) || __open(5.5) || __open(4.5);
          const c = 1, L = T.flightFor(c, 0).d; __place(P, n.x - 9, n.z, n.h, Math.PI / 2); P.slamCD = 0; P.paint = 1; __place(H, n.x - 1, n.z + 0.6, n.h, 0); H.ai = null;
          T.flingIt(P, c); for (let i = 0; i < 30; i++) { T.step(0.012); H.x = n.x - 1; H.z = n.z + 0.6; H.spd = 0; } T.useSlam(P); for (let i = 0; i < 11; i++) { T.step(0.012); H.x = n.x - 1; H.z = n.z + 0.6; H.spd = 0; }
          window.__cam = [[P.x + 2.5, P.y + 2.2, P.z + 12.5], [P.x + 2.5, P.y - 1.2, P.z]];
          return { missile: P.missile, y: P.y, vy: P.vy, spd: P.spd }; })()""")
        print('missile', r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s21_missile_side.png')
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; let k = 0; while ((P.air || P.slam) && k < 300) { T.step(0.012); H.spd = 0; k++; } for (let i = 0; i < 6; i++) T.step(0.012); return { Hst: H.st }; })()""")
        print('missile land', r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s21_missile_land.png'); await pg.evaluate("window.__cam = null")
        # 3) burst sling aim
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; if (H.st === 'ko') { H.st = 'play'; H.koT = 0; } __place(H, 40, 40, 0); H.st = 'ko'; H.koT = 1e9;
          const p = T.pots2.filter(q => T.potUp(q) && !q.occ).sort((a, b) => a.y - b.y)[0]; let yw = 0; for (let k = 0; k < 16; k++) { const a = k / 16 * 6.283, x = p.x + Math.sin(a) * 2.7, z = p.z + Math.cos(a) * 2.7; if (T.surfaceUnder(x, z, p.y + 0.5, true) > -Infinity && T.surfaceUnder(x + Math.sin(a), z + Math.cos(a), p.y + 0.5, true) > -Infinity) { yw = a; break; } } __place(P, p.x, p.z, p.y, yw); T.enterPot(P, p); P.slamCD = 0; P.paint = 1;
          T.useSlam(P); let k = 0; while (P.vy > -0.5 && k < 300) { T.step(0.012); k++; }
          T.startCharge(P); P.charge = 0.85; for (let i = 0; i < 6; i++) T.step(0.012); P.charge = 0.85;
          const sh = T.airShot(P, 0.85, P.yaw); const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw);
          window.__cam = [[P.x - fz * 7 - fx * 2, P.y + 1.5, P.z + fx * 7 - fz * 2], [P.x + fx * 1.5, P.y - 3, P.z + fz * 1.5]];
          return { ch: P.charging, air: P.air, sling: P.airSling, y: P.y, ringY: sh.y, dist: sh.dist }; })()""")
        print('sling aim', r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s21_sling.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
