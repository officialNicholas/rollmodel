# smoke trails: a bounced blob flying off, and the rocket climbing
import asyncio, sys, json, math
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'smoke'; KIND = sys.argv[2] if len(sys.argv) > 2 else 'bounce'; GFX = sys.argv[3] if len(sys.argv) > 3 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""(kind) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('blank'); T.freshMap(); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); const P = T.P, H = T.H, dt = 1 / 60; H.ai = null; for (let i = 0; i < 30; i++) { T.step(dt); T.visuals(dt, dt); }
          let D = P;
          if (kind === 'bounce') { H.x = P.x - Math.sin(P.yaw) * 0.6; H.z = P.z - Math.cos(P.yaw) * 0.6; H.yaw = P.yaw; H.spd = 8; T.shove(H, P); }
          else if (kind === 'rocket') { P.power = { type: 'rocket', t: 9 }; T.startRocket(P); }
          for (let i = 0; i < (kind === 'rocket' ? 26 : 22); i++) { T.steerIn = 0; T.step(dt); T.visuals(dt, dt); T.matchLeft = 99; }
          window.__noStep = true; window.__noLoop = false; return { P: [P.x, P.y, P.z, P.yaw], air: P.air, rocket: !!P.rocket, knock: P.knockT }; }""", KIND)
        print('ready', json.dumps(r))
        Px, Py, Pz, Pyaw = r['P']
        await pg.wait_for_timeout(1200); await pg.screenshot(path=SP + OUT + '_play.png', timeout=180000)
        a = Pyaw + 1.7
        cam = [[Px + math.sin(a) * 6.5, Py + 2.2, Pz + math.cos(a) * 6.5], [Px - math.sin(Pyaw) * 1.5, Py - 0.6, Pz - math.cos(Pyaw) * 1.5]]
        await pg.evaluate("(c) => { window.__cam = c; }", cam); await pg.wait_for_timeout(1200); await pg.screenshot(path=SP + OUT + '_side.png', timeout=180000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
