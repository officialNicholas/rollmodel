# the turret up close: planted, aimed round to the side and behind (steering), mid-shot, and the game view with shots in the air
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'ts'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', look: { head: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('blank'); T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 90; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } const P = T.P, H = T.H; H.ai = null; H.x = P.x + Math.sin(P.yaw) * 30; H.z = P.z + Math.cos(P.yaw) * 30; H.spd = 0; H.steer = 0;
          T.startTurret(P); window.__yaw0 = P.yaw;
          window.__run = (n, steer) => { for (let i = 0; i < n; i++) { T.steerIn = steer || 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } T.steerIn = 0; };
          window.__close = (rel, h, d) => { const c = T.camera, a = window.__yaw0 + rel; c.position.set(P.x + Math.sin(a) * d, P.y + h, P.z + Math.cos(a) * d); c.lookAt(P.x, P.y + 0.5, P.z); c.updateMatrixWorld(); T.renderFrame(); }; }""")
        shots = [('start', 18, 0, 0.6, 1.3, 3.0), ('aim0', 30, 0, 0.6, 1.3, 3.0), ('side', 40, 0.9, 0.6, 1.3, 3.0), ('behind', 50, 0.9, 0.6, 1.3, 3.0), ('back2', 1, 0, 2.4, 1.5, 3.0)]
        for nm, n, st, rel, h, d in shots:
            await pg.evaluate("([n, st]) => window.__run(n, st)", [n, st])
            info = await pg.evaluate("([rel, h, d]) => { window.__close(rel, h, d); const T = __T, P = T.P; return { yaw: +(P.yaw - window.__yaw0).toFixed(2), shots: T.shots.length, form: T.VP.slime.form, tur: !!P.turret }; }", [rel, h, d])
            print(nm, json.dumps(info)); await pg.screenshot(path=SP + 'st/' + TAG + '_' + nm + '.png', timeout=180000)
        # the game camera with shots flying
        await pg.evaluate("() => { window.__run(20, 0); const T = __T; T.visuals(1 / 60, 1 / 60); T.renderFrame(); }")
        await pg.screenshot(path=SP + 'st/' + TAG + '_game.png', timeout=180000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
