# the basin intro: frames through the countdown (under the paint, the eyes up, the look round) and the leap out at Go
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1]; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; TIMES = [float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else '0.3,0.75,1.15,1.6,2.2,2.6,2.9,3.4').split(',')]
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 5; MODE = sys.argv[5] if len(sys.argv) > 5 else 'duel'; GFX = sys.argv[6] if len(sys.argv) > 6 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: '" + MODE + "', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("""([stage, seed, mode]) => { const T = __T; T.mode = mode; T.applyMode(); T.setStage(stage); T.genWorld(seed, { themes: [stage] }); T.mapUsed = false; T.setDiff('easy');
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.start(); }""", [STAGE, SEED, MODE])
        await pg.wait_for_function("__T.state === 'intro'", polling=50, timeout=60000)
        await pg.evaluate("() => { window.__noLoop = true; window.__tt = 0; }")
        for t in TIMES:
            info = await pg.evaluate("""(t) => { const T = __T, dt = 1 / 60; while (window.__tt < t - 1e-6) { T.step(dt); T.visuals(dt, dt); T.flushTrail(); window.__tt += dt; } T.renderFrame();
              return { t: +window.__tt.toFixed(2), state: T.state, P: [T.P.x, T.P.y, T.P.z].map(v => +v.toFixed(2)), st: T.P.st, air: T.P.air, sink: +(T.VP.sink || 0).toFixed(2), H: [T.H.x, T.H.z].map(v => +v.toFixed(1)), Hst: T.H.st }; }""", t)
            print(json.dumps(info))
            await pg.screenshot(path=SP + OUT + '_%0.2f.png' % t, timeout=180000)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
