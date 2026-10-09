import asyncio, json
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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); H.ai = null; H.x = 40; H.z = 40; H.st = 'ko'; H.koT = 1e9;
          T.rainPuddles(); for (let i = 0; i < 500; i++) { P.spd = 0; T.step(0.012); }
          const ok = (x, z, y) => Math.abs(T.surfaceUnder(x, z, y + 0.5, true) - y) < 0.05 && !T.blockedAt(x, z, y);
          let pick = null;
          for (const r of T.rivals) { if (!r.on) continue; for (let k = 0; k < 16 && !pick; k++) { const a = k / 16 * 6.283; let good = true; for (let d = -4; d <= 10; d += 0.5) for (const sd of [0]) { const x = r.x + Math.sin(a) * d + Math.cos(a) * sd, z = r.z + Math.cos(a) * d - Math.sin(a) * sd; if (!ok(x, z, r.y) || (d > 1.5 && T.rivals.some(q => q !== r && q.on && Math.hypot(q.x - x, q.z - z) < q.rad + 0.6))) good = false; } if (good) pick = { r, a }; } if (pick) break; }
          if (!pick) return 'no path';
          const { r, a } = pick; __place(P, r.x - Math.sin(a) * 4, r.z - Math.cos(a) * 4, r.y, a); P.spd = 5.4;
          let k = 0; while (k < 400) { T.step(0.012); P.yaw = a; k++; if ((P.x - r.x) * Math.sin(a) + (P.z - r.z) * Math.cos(a) > 6.5) break; }
          const mx = r.x + Math.sin(a) * 1.5, mz = r.z + Math.cos(a) * 1.5; window.__cam = [[mx - Math.sin(a) * 6.5 + Math.cos(a) * 1.5, r.y + 9.5, mz - Math.cos(a) * 6.5 - Math.sin(a) * 1.5], [mx + Math.sin(a) * 1.0, r.y, mz + Math.cos(a) * 1.0]];
          return { on: T.rivals.filter(q => q.on).length, dil: +P.dilT.toFixed(2) }; })()""")
        print(r); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s21_puddle.png')
        print('errors', errs); await b.close()
asyncio.run(main())
