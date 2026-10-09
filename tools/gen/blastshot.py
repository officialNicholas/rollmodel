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
        await pg.evaluate("(()=>{ const op = window.__place; window.__place = (...a) => { __T.showBlobs(); op(...a); }; })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null;
          let pot = null, a = 0; for (const q of T.pots2) { if (!T.potUp(q) || q.occ) continue; for (let k = 0; k < 8; k++) { const aa = k / 8 * 6.283; let ok = true; for (let d = 1; d <= 9; d += 0.5) { const x = q.x + Math.sin(aa) * d, z = q.z + Math.cos(aa) * d; if (Math.abs(T.surfaceUnder(x, z, q.y + 0.5, true) - q.y) > 0.05 || T.blockedAt(x, z, q.y)) ok = false; } if (ok) { pot = q; a = aa; break; } } if (pot) break; }
          if (!pot) return 'none';
          __place(H, pot.x, pot.z, pot.y, 0); T.enterPot(H, pot); H.slamCD = 0; H.paint = 1;
          __place(P, pot.x + Math.sin(a) * 1.8, pot.z + Math.cos(a) * 1.8, pot.y, a + Math.PI); P.immuneT = 0; P.charging = true;
          T.useSlam(H); T.hold = 0; for (let i = 0; i < 22; i++) T.step(0.012);
          const mx = (pot.x + P.x) / 2, mz = (pot.z + P.z) / 2; window.__cam = [[mx - Math.cos(a) * 7 - Math.sin(a) * 3, pot.y + 8, mz + Math.sin(a) * 7 - Math.cos(a) * 3], [mx, pot.y + 0.8, mz]];
          return { st: P.st, spd: +P.spd.toFixed(1), y: +P.y.toFixed(2) }; })()""")
        print(r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s30_blast.png'); print(errs); await b.close()
asyncio.run(main())
