# Palette Island look-dev: the usual view behind the blob, a palm on its planter close up, the sand at a low angle, and from above
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'isle'; GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'; W = int(sys.argv[3]) if len(sys.argv) > 3 else 390; H = int(sys.argv[4]) if len(sys.argv) > 4 else 844
VIEWS = sys.argv[5].split(',') if len(sys.argv) > 5 else ['play', 'palm', 'low', 'top']
SEED = int(sys.argv[6]) if len(sys.argv) > 6 else 0
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2 if W < 700 else 1, has_touch=True, is_mobile=W < 700)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""(seed) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); if (seed) T.genWorld(seed, { themes: ['island'] }); else T.freshMap(); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); const dt = 1 / 60; T.aiReset(T.P); for (let i = 0; i < 60 * 2; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0) { T.visuals(dt * 10, dt * 10); T.flushTrail(); } T.matchLeft = 99; }
          window.__noStep = true; window.__noLoop = false;
          const cols = T.BOXES.filter(b => b[6] === 'c' && b[7] === 'column').map(b => [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[1] - b[0]) / 2, b[5]]);
          return { theme: T.TH.id, cols, P: [T.P.x, T.P.y, T.P.z, T.P.yaw] }; }""", SEED)
        print('ready', json.dumps(r)[:400])
        cols = r['cols']; Px, Py, Pz, Pyaw = r['P']
        import math
        for v in VIEWS:
            cam = None
            if v == 'palm' and cols:
                cx, cz, rad, top = cols[0]; a = 0.7
                cam = [[cx + math.sin(a) * (rad + 4.2), top + 1.6, cz + math.cos(a) * (rad + 4.2)], [cx, top + 0.9, cz]]
            elif v == 'base' and cols:
                cx, cz, rad, top = cols[0]; a = 0.7
                cam = [[cx + math.sin(a) * (rad + 2.0), top * 0.6 + 0.6, cz + math.cos(a) * (rad + 2.0)], [cx, top * 0.45, cz]]
            elif v == 'low':
                cam = [[Px - math.sin(Pyaw) * 3.2, 1.0, Pz - math.cos(Pyaw) * 3.2], [Px + math.sin(Pyaw) * 2.0, 0.0, Pz + math.cos(Pyaw) * 2.0]]
            elif v == 'top':
                cam = [[Px + 0.01, 13, Pz + 4], [Px, 0, Pz]]
            elif v == 'wide':
                cam = [[Px - math.sin(Pyaw) * 9, 6.5, Pz - math.cos(Pyaw) * 9], [Px + math.sin(Pyaw) * 4, 0.0, Pz + math.cos(Pyaw) * 4]]
            await pg.evaluate("(c) => { window.__cam = c; }", cam)
            await pg.wait_for_timeout(1600)
            await pg.screenshot(path=SP + OUT + '_' + v + '.png', timeout=180000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
