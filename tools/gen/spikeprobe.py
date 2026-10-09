# frame-time spikes in a 3-way match: per frame the simulation (with the CPU brains) and the visuals are timed, and each frame where a brain
# thought is marked. Reports the spread (median, 95th, 99th, worst) and how much the thinking frames cost over the others
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""(stage) => { const T = __T, P = T.P; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(77, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i = 0; i < 600; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const st = [], vi = [], th = []; let thinks = 0; const orig = T.aiThink;
          for (let i = 0; i < 1200; i++) { const t0 = performance.now(); T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(0.0083); T.step(0.0083); const t1 = performance.now(); T.visuals(1 / 60, 1 / 60); const t2 = performance.now(); st.push(t1 - t0); vi.push(t2 - t1); }
          const q = (a, p) => { const s = a.slice().sort((x, y) => x - y); return +s[Math.min(s.length - 1, Math.floor(s.length * p))].toFixed(2); };
          return { step: [q(st, 0.5), q(st, 0.95), q(st, 0.99), q(st, 1)], visuals: [q(vi, 0.5), q(vi, 0.95), q(vi, 0.99), q(vi, 1)] }; }""", STAGE)
        print(PAGE, STAGE, 'ms (median, p95, p99, max)', json.dumps(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
