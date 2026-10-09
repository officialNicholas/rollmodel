# how soon the hot functions get optimized and stay that way: their V8 tier sampled every 300 frames through a 3-way match
# (B baseline, M maglev, T turbofan, O optimized, I interpreted, L lazy)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--js-flags=--allow-natives-syntax'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, S = T.SLIME; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          const tier = f => { const s = %GetOptimizationStatus(f); return (s & 64 ? 'T' : s & 32 ? 'M' : s & 16 ? 'O' : s & (1 << 14) ? 'B' : s & 128 ? 'I' : s & (1 << 17) ? 'L' : '?'); };
          const fns = { update: S.update, visuals: T.visuals, step: T.step, aiThink: T.aiThink, aiStep: T.aiStep };
          const rows = [];
          for (let f = 1; f <= 3600; f++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(0.0083); T.step(0.0083); T.visuals(1 / 60, 1 / 60); T.matchLeft = 99;
            if (f % 300 === 0) rows.push(f + ' ' + Object.entries(fns).map(([k, fn]) => k + ':' + tier(fn)).join(' ')); }
          return rows; }""")
        for row in r: print(row)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
