# the turret firing, frame by frame up close (the gulp and kick each shot), wearing the witch hat
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'tq'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 600}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('blank'); T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 90; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } const P = T.P, H = T.H; H.ai = null; H.x = P.x + Math.sin(P.yaw) * 30; H.z = P.z + Math.cos(P.yaw) * 30;
          T.startTurret(P); window.__yaw0 = P.yaw; for (let i = 0; i < 50; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          window.__f = (st) => { for (let k = 0; k < 4; k++) { T.steerIn = st || 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } T.steerIn = 0; const c = T.camera, a = window.__yaw0 + 0.4; c.position.set(P.x + Math.sin(a) * 3.0, P.y + 1.6, P.z + Math.cos(a) * 3.0); c.lookAt(P.x, P.y + 0.55, P.z); c.updateMatrixWorld(); T.renderFrame(); const I = T.VP.slime, Tt = I.tur; return { yaw: +(P.yaw - window.__yaw0).toFixed(2), body: +(Tt.by - window.__yaw0).toFixed(2), push: +Tt.push.toFixed(2) }; }; }""")
        for i in range(8):
            r = await pg.evaluate("(st) => window.__f(st)", 0.7 if i < 6 else 0); await pg.screenshot(path=SP + 'st/%s_%d.png' % (TAG, i)); print(i, r)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
