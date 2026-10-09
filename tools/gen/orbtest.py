import asyncio, json
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read()
PREP = src.split('PREP = r"""')[1].split('"""')[0]; HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e) + str(getattr(e,'stack',''))[:300]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000)
        await pg.evaluate(PREP); await pg.evaluate(HELP)
        # 1) spawn timing and drifting on the real map
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, o = T.orb; T.start(); T.setWx('clear', 999); P.st = 'ko'; P.koT = 1e9; H.st = 'ko'; H.koT = 1e9;
          let spawnAt = -1, minH = 9, maxH = -9, moved = 0, lx = 0, lz = 0, voidT = 0;
          for (let i = 0; i < 4000; i++) { T.step(0.012); if (o.on && spawnAt < 0) { spawnAt = +T.runT.toFixed(1); lx = o.x; lz = o.z; }
            if (o.on) { const g = T.surfaceUnder(o.x, o.z, o.y, true); if (g === -Infinity) voidT += 0.012; else { minH = Math.min(minH, o.y - g); maxH = Math.max(maxH, o.y - g); } moved += Math.hypot(o.x - lx, o.z - lz); lx = o.x; lz = o.z; } }
          return { spawnAt, minH: +minH.toFixed(2), maxH: +maxH.toFixed(2), moved: +moved.toFixed(1), voidT: +voidT.toFixed(1) }; })()""")
        print('drift', r)
        await pg.evaluate("__flat()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, o = T.orb, out = {}; T.start(); __flat(); T.setWx('clear', 999); H.st = 'ko'; H.koT = 1e9;
          const n = __open(9);
          // jump into it
          T.orbSpawn(); o.k = 1; o.x = n.x; o.z = n.z; o.tx = n.x; o.tz = n.z; o.base = 0;
          __place(P, n.x - 2.4, n.z, 0, Math.PI / 2); P.spd = 5.4; let took = -1;
          for (let i = 0; i < 120; i++) { if (i === 20) T.P.air || (P.air = true, P.vy = 5.6); T.step(0.012); o.tx = n.x; o.tz = n.z; if (P.giantT > 0 && took < 0) took = i; }
          out.jumpTake = took > 0; out.giantT = +P.giantT.toFixed(2);
          // trail width: coverage per second giant vs normal
          __place(P, n.x - 8, n.z + 4, 0, Math.PI / 2); P.spd = 5.4; P.giantT = 3.5; const c0 = T.teamCov(0); for (let i = 0; i < 80; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.giantGain = +(T.teamCov(0) - c0).toFixed(3);
          __place(P, n.x - 8, n.z - 4, 0, Math.PI / 2); P.spd = 5.4; P.giantT = 0; const c1 = T.teamCov(0); for (let i = 0; i < 80; i++) { T.step(0.012); P.yaw = Math.PI / 2; } out.normalGain = +(T.teamCov(0) - c1).toFixed(3);
          // squish: giant rolls into the holy water
          window.__hai = H.ai; __place(H, n.x + 2, n.z, 0, 0); H.ai = null; H.immuneT = 0; __place(P, n.x - 1.5, n.z, 0, Math.PI / 2); P.spd = 5.4; P.giantT = 3;
          let sq = false; for (let i = 0; i < 80; i++) { H.spd = 0; T.step(0.012); P.yaw = Math.PI / 2; if (H.flatT > 0) { sq = true; break; } } out.squish = sq;
          // a normal blob can't flatten a giant
          __place(H, n.x + 2, n.z - 3, 0, -Math.PI / 2); H.spd = 6; __place(P, n.x - 1, n.z - 3, 0, Math.PI / 2); P.spd = 0; P.giantT = 3; P.immuneT = 0; H.immuneT = 0.0;
          let pf = false, hf = false; for (let i = 0; i < 80; i++) { T.step(0.012); if (P.flatT > 0) pf = true; if (H.flatT > 0) hf = true; } out.giantFlattened = pf; out.normalSquishedInstead = hf;
          // a pound under it takes it
          P.giantT = 0; P.flatT = 0; T.orbSpawn(); o.k = 1; o.x = n.x + 1; o.z = n.z + 1; o.tx = o.x; o.tz = o.z; o.base = 0; __place(P, n.x, n.z, 0, 0); P.slamCD = 0; P.paint = 1; T.useSlam(P);
          for (let i = 0; i < 120 && (P.air || P.slam); i++) { T.step(0.012); o.tx = o.x; o.tz = o.z; } out.poundTake = P.giantT > 0;
          // ends after 4 seconds
          P.giantT = 4; for (let i = 0; i < 350; i++) T.step(0.012); out.endsAfter4 = P.giantT === 0;
          return out; })()""")
        print('player', json.dumps(r))
        # CPU goes for it, then hunts while giant
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, o = T.orb; T.setAI('hard'); let took = 0, tries = 0, squished = 0, times = [], kod = 0, modes = [];
          for (let t = 0; t < 8; t++) { T.start(); __flat(); T.setWx('clear', 999); T.aiReset(H); const n = __open(9);
            __place(H, n.x - 8 + t, n.z - 3, 0, t); T.aiReset(H); H.paint = 1; __place(P, n.x + 6, n.z + 4 - t, 0, 2); P.charging = true;
            T.orbSpawn(); o.k = 1; o.x = n.x; o.z = n.z; o.base = 0; tries++; let k = 0;
            for (; k < 900 && o.on; k++) { P.charging = true; P.spd = 0; T.step(0.012); }
            if (H.giantT > 0) { took++; times.push(+(k * 0.012).toFixed(1)); for (let i = 0; i < 380 && H.giantT > 0; i++) { P.charging = true; P.spd = 0; T.step(0.012); if (P.flatT > 0) { squished++; break; } if (P.st === 'ko') { kod++; break; } } modes.push(H.ai.mode); if (P.st === 'ko') { P.st = 'play'; P.koT = 0; } }
          }
          return { tries, took, times, squished, kod, modes }; })()""")
        print('cpu', r)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
