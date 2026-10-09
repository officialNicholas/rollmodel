# the jump as a leap: side-on (and three-quarter) frames from take-off to landing
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'lp'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 500}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'solo', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.setStage('blank'); T.genWorld(88, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 90; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const P = T.P, nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0), n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z) - Math.hypot(b.x, b.z))[0]; window.__n0 = n0;
          for (let i = 0; i < 30; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.yaw = 0; P.y = 0; P.air = false; P.spd = T.cfg.speed * 0.6; T.step(1 / 60); P.x = n0.x; P.z = n0.z; T.visuals(1 / 60, 1 / 60); }
          T.jump(P); window.__t = 0;
          window.__shot = (dt) => { const P = T.P; let n = Math.round(dt * 60); while (n-- > 0) { T.steerIn = 0; P.yaw = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); window.__t += 1 / 60; }
            const c = T.camera; c.position.set(P.x - 2.9, P.y + 1.0, P.z + 3.6); c.lookAt(P.x, P.y + 0.45, P.z + 0.3); c.fov = 34; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix();
            const I = T.VP.slime; return { t: +window.__t.toFixed(2), air: P.air, vy: +P.vy.toFixed(1), y: +P.y.toFixed(2), leap: +(I.st.leap || 0).toFixed(2), tip: +(I.st.tip || 0).toFixed(2), expr: I.st.exprB }; }; }""")
        rows = []
        for k, dt in enumerate([0.02, 0.08, 0.1, 0.1, 0.1, 0.1, 0.1, 0.08, 0.08, 0.12]):
            r = await pg.evaluate("(dt) => window.__shot(dt)", dt); rows.append(r); await pg.screenshot(path=SP + 'st/%s_%d.png' % (TAG, k))
        for r in rows: print(json.dumps(r))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
