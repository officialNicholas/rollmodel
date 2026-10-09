# grooves: slide a dried-up blob in a slalom across open sand, then look at the marks it left (and the grains it kicks up)
import asyncio, sys, json, math
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'groove'; GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.freshMap(); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); const P = T.P, H = T.H, dt = 1 / 60; H.ai = null; H.x = 30; H.z = 30;
          // an open stretch of floor
          let best = null; for (let i = 0; i < 800; i++) { const x = (Math.random() * 2 - 1) * 16, z = (Math.random() * 2 - 1) * 16, a = Math.random() * 6.283; let ok = 0; for (let s = 0; s < 30; s++) { const px = x + Math.sin(a) * s * 0.4, pz = z + Math.cos(a) * s * 0.4; let clear = true; for (let w = -4; w <= 4; w++) { const qx = px + Math.cos(a) * w * 0.4, qz = pz - Math.sin(a) * w * 0.4; if (Math.abs(T.surfaceUnder(qx, qz, 3, true)) > 0.05 || T.blockedAt(qx, qz, 0)) clear = false; } if (!clear) break; ok++; } if (!best || ok > best[3]) best = [x, z, a, ok]; if (ok >= 30) break; }
          P.x = best[0]; P.z = best[1]; P.y = 0; P.yaw = best[2]; P.spd = 0;
          for (let i = 0; i < 60 * 3.2; i++) { P.paint = 0; P.dry = true; P.dryT = 0; T.steerIn = Math.sin(i / 60 * 2.6) * 0.9; T.step(dt); if (i % 6 === 0) T.visuals(dt * 6, dt * 6); T.matchLeft = 99; }
          window.__noStep = true; window.__noLoop = false; return { open: best[3], P: [P.x, P.y, P.z, P.yaw], start: best }; }""")
        print('ready', json.dumps(r))
        Px, Py, Pz, Pyaw = r['P']
        await pg.wait_for_timeout(1500); await pg.screenshot(path=SP + OUT + '_play.png', timeout=180000)
        cam = [[Px - math.sin(Pyaw) * 5.5 + 0.01, 7.5, Pz - math.cos(Pyaw) * 5.5], [Px - math.sin(Pyaw) * 1.8, 0, Pz - math.cos(Pyaw) * 1.8]]
        await pg.evaluate("(c) => { window.__cam = c; }", cam); await pg.wait_for_timeout(1500); await pg.screenshot(path=SP + OUT + '_top.png', timeout=180000)
        cam = [[Px - math.sin(Pyaw) * 1.2 + math.cos(Pyaw) * 1.6, 1.1, Pz - math.cos(Pyaw) * 1.2 - math.sin(Pyaw) * 1.6], [Px - math.sin(Pyaw) * 1.5, 0, Pz - math.cos(Pyaw) * 1.5]]
        await pg.evaluate("(c) => { window.__cam = c; }", cam); await pg.wait_for_timeout(1500); await pg.screenshot(path=SP + OUT + '_low.png', timeout=180000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
