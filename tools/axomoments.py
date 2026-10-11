"""The axolotl's big moments: a won match (the victory screen) and riding the rocket. Prints its animator state at each shot.
usage: axomoments.py [tag] [vic|rocket|both]"""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'mo'; WHAT = sys.argv[2] if len(sys.argv) > 2 else 'both'
Q = "(() => { const I = __T.VP.slime, X = I && I.ax; if (!X) return null; const A = X.A; return { st: A.state, mesh: A.mesh, fade: +A.fade.toFixed(2), vis: I.root.visible, coat: +X.coat.toFixed(2), uw: +X.look.U.uCoat.value.w.toFixed(2) }; })()"
async def boot(b, look):
    ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', stage:'manor', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, owned:['hat','lashes'], bought:['hat','lashes'], look:" + json.dumps(look) + " })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' and 'CORS' not in m.text and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
    await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=240000, polling=1000); await pg.wait_for_timeout(1500)
    return ctx, pg, errs
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        if WHAT in ('vic', 'both'):
            ctx, pg, errs = await boot(b, {'head': 'hat', 'lash': 'lashes', 'iris': 'violet'})
            await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000, polling=500); await pg.wait_for_timeout(1500)
            await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
            await pg.wait_for_function("!!__T.vic", timeout=60000, polling=200)
            for k, w in enumerate([1600, 2000, 2500]):
                await pg.wait_for_timeout(w); await pg.screenshot(path=f'{OUT}/{TAG}_vic{k}.png'); print('vic', k, json.dumps(await pg.evaluate(Q)))
            print('vic errors', errs[:4]); await ctx.close()
        if WHAT in ('rocket', 'both'):
            ctx, pg, errs = await boot(b, {'head': None, 'eyes': 'round', 'iris': 'brown'})
            await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000, polling=500)
            await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(800)
            await pg.evaluate("__T.matchLeft = 400; for (const D of __T.ACTIVE) if (D !== __T.P) { D.ai && (D.ai.thinkT = 99); D.spd = 0; } __T.startRocket(__T.P);")
            await pg.wait_for_timeout(1500); await pg.evaluate("window.__camRel = [[3.0, 0.6, 3.0], [0, 0.6, 0]]"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{OUT}/{TAG}_rk_up.png'); print('rocket up', json.dumps(await pg.evaluate(Q)))
            await pg.wait_for_function("__T.P.rocket && __T.P.rocket.ph === 'hover'", timeout=120000, polling=300)
            for name, off in [('back', [2.2, 0.6, -3.0]), ('side', [3.2, 0.3, 1.2]), ('front', [0.4, 0.4, 3.2])]:
                await pg.evaluate("window.__camRel = [%s, [0, 0.6, 0]]" % json.dumps(off)); await pg.wait_for_timeout(1500)
                await pg.screenshot(path=f'{OUT}/{TAG}_rk_{name}.png'); print('rocket', name, json.dumps(await pg.evaluate(Q)))
            print('rocket errors', errs[:4]); await ctx.close()
        await b.close()
asyncio.run(main())
