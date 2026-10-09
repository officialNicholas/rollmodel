# how often does coming back (or starting) kill you if you don't touch the controls? Across many canvases on every stage: knocked out,
# back in a basin, hop out, then 3 s with no steering; and the match start through Go then 3 s with no steering. Counts the falls
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 240, 'height': 420}, device_scale_factor=1)
        await ctx.add_init_script("window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""(N) => { const T = __T, P = T.P; window.__noLoop = true; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'solo'; T.applyMode(); const out = { respawn: { runs: 0, falls: 0 }, start: { runs: 0, falls: 0 }, bad: [] };
          for (const stage of ['island', 'blank', 'crypt', 'cathedral', 'manor']) for (let s = 0; s < N; s++) {
            const seed = 1000 + s * 7919 + stage.length * 31; T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(seed, { themes: [stage] }); T.mapUsed = false;
            // the start: through the countdown to Go, then 3 s hands off
            T.start(); T.setWx('clear', 999); let n = 0; while (T.state === 'intro' && n++ < 400) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
            let fell = false; for (let i = 0; i < 180; i++) { T.steerIn = 0; T.step(1 / 60); if (i % 6 === 0) T.visuals(0.1, 0.1); if (P.st === 'ko') { fell = true; break; } }
            out.start.runs++; if (fell) { out.start.falls++; out.bad.push(['start', stage, seed]); }
            // three comebacks per canvas: knocked out, back in a basin, hop out, 3 s hands off
            for (let k = 0; k < 3; k++) {
              if (P.st !== 'play') { for (let i = 0; i < 300 && P.st !== 'hide'; i++) { T.steerIn = 0; T.step(1 / 60); } }
              if (P.st === 'play') { T.knockOut(P, 'fall', null); for (let i = 0; i < 300 && P.st !== 'hide'; i++) { T.steerIn = 0; T.step(1 / 60); } }
              if (P.st !== 'hide') continue; for (let i = 0; i < 20; i++) T.step(1 / 60); T.jump(P); let f2 = false;
              for (let i = 0; i < 180; i++) { T.steerIn = 0; T.step(1 / 60); if (P.st === 'ko') { f2 = true; break; } }
              out.respawn.runs++; if (f2) { out.respawn.falls++; out.bad.push(['respawn', stage, seed, k]); }
            }
            T.matchLeft = 99;
          }
          return out; }""", N)
        print(PAGE, json.dumps(r)[:900]); print('errors', errs[:3]); await b.close()
asyncio.run(main())
