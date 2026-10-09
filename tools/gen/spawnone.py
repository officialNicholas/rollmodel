# one canvas, many comebacks: how often does hopping out of the basin hands-off end in a fall (and where it went)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'cathedral'
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 17117
N = int(sys.argv[4]) if len(sys.argv) > 4 else 30
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""([stage, seed, N]) => { const T = __T, P = T.P; window.__noLoop = true; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'solo'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(seed, { themes: [stage] }); T.mapUsed = false;
          T.start(); T.setWx('clear', 999); let n = 0; while (T.state === 'intro' && n++ < 400) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const out = { runs: 0, falls: 0, bad: [] };
          for (let k = 0; k < N; k++) {
            if (P.st === 'play') T.knockOut(P, 'fall', null);
            for (let i = 0; i < 400 && P.st !== 'hide'; i++) { T.steerIn = 0; T.step(1 / 60); }
            if (P.st !== 'hide') continue; for (let i = 0; i < 20; i++) T.step(1 / 60); const pot = P.pot, y0 = P.yaw; T.jump(P); let f2 = false, path = [];
            for (let i = 0; i < 180; i++) { T.steerIn = 0; T.step(1 / 60); if (i % 10 === 0) path.push([+P.x.toFixed(1), +P.z.toFixed(1), +P.y.toFixed(1)]); if (P.st === 'ko') { f2 = true; break; } }
            out.runs++; if (f2) { out.falls++; out.bad.push({ pot: [+pot.x.toFixed(1), +pot.z.toFixed(1), +pot.y.toFixed(2)], yaw: +y0.toFixed(2), path }); }
            T.matchLeft = 99;
          }
          return out; }""", [STAGE, SEED, N])
        print(PAGE, STAGE, SEED, json.dumps(r)[:1500]); print('errors', errs[:3]); await b.close()
asyncio.run(main())
