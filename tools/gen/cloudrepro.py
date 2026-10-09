# reproduce the clouds covering the stage: a match on a stage with drifting clouds, the AI driving you, a frame every so often from the game camera
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1]; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'crypt'; N = int(sys.argv[3]) if len(sys.argv) > 3 else 6; SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 7
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""([stage, seed]) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage); T.genWorld(seed, { themes: [stage] }); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); window.__drive = (sec) => { const dt = 1 / 60; for (let i = 0; i < 60 * sec; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); T.visuals(dt, dt); T.matchLeft = 99; } T.flushTrail(); };
          __drive(1); window.__noStep = true; window.__noLoop = false;
          return { theme: T.TH.id, movers: T.movers.filter(m => m.on).map(m => [m.cx, m.cz, m.axis, m.amp]) }; }""", [STAGE, SEED])
        print('ready', json.dumps(r)[:400])
        for i in range(N):
            await pg.evaluate("() => { window.__noStep = false; window.__noLoop = true; __drive(1.5); window.__noStep = true; window.__noLoop = false; }")
            await pg.wait_for_timeout(900)
            info = await pg.evaluate("() => { const T = __T, c = T.camera.position; return { cam: [c.x, c.y, c.z].map(v => +v.toFixed(2)), P: [T.P.x, T.P.y, T.P.z].map(v => +v.toFixed(2)), movers: T.movers.filter(m => m.on).map(m => [+m.cx.toFixed(1), +m.cz.toFixed(1)]), fades: T.moverMeshes.map(g => +g.userData.fade.toFixed(2)) }; }")
            print(i, json.dumps(info))
            await pg.screenshot(path=SP + OUT + '_%d.png' % i, timeout=180000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
