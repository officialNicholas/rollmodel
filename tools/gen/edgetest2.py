import asyncio, json, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        by = {}
        for sd in [11, 5, 9]:
            await pg.evaluate(f"(()=>{{ window.__noLoop=true; __T.genWorld({sd}); __T.mapUsed=false; __T.showMenu(); __T.start(); }})()")
            r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, A = 26.4; H.ai = null; H.st = 'ko'; H.koT = 1e9; H.x = 99; T.setWx('clear', 999);
              for (let i = 0; i < 200; i++) T.step(0.012);
              const zs = []; for (let z = -20; z <= 20; z += 0.5) { let ok = true; for (let x = A - 8; x < A - 0.2; x += 0.4) for (const dz of [-3, -1.5, 0, 1.5, 3, 4.5, 6]) if (T.surfaceUnder(x, z + dz, 0.3) !== 0 || T.blockedAt(x, z + dz, 0)) ok = false; if (ok) zs.push(z); }
              if (!zs.length) return null; const z0 = zs[Math.floor(zs.length / 2)], res = [];
              for (const m of [1, 1.5, 2, 2.5, 3]) for (const d0 of [1.5, 2.5, 3.5]) for (const th of [55, 80]) for (const inp of [0, 0.4, 0.7]) {
                const yaw = Math.PI / 2 - th * Math.PI / 180; T.matchLeft = 90; T.state = 'play'; P.st = 'play'; P.air = false; P.y = 0; P.x = A - d0; P.z = z0; P.yaw = yaw; P.spd = T.cfg.speed * m; P.turn = 0; P.kx = P.kz = 0; P.paint = 1; P.charging = false; P.giantT = 0; P.immuneT = 0; P.dry = false;
                let fell = false; for (let i = 0; i < 200; i++) { T.steerIn = i * 0.012 < 0.12 ? 0 : inp; T.step(0.012); if (P.st !== 'play' || P.y < -0.5 || P.air && P.y < -0.2) { fell = true; break; } }
                res.push([m, inp, fell ? 0 : 1]); }
              return res; })()""")
            if not r: print(sd, 'no spot'); continue
            for m, inp, ok in r:
                k = f"{m}x in{inp}"; by.setdefault(k, [0, 0]); by[k][0] += ok; by[k][1] += 1
        tot = sum(v[0] for v in by.values()); n = sum(v[1] for v in by.values())
        print(PAGE, 'made it', tot, 'of', n)
        for k, v in by.items(): print(f'  {k}: {v[0]}/{v[1]}')
        print(errs[:2]); await b.close()
asyncio.run(main())
