# garbage made per call, by function, inside a live 3-way match (the CPU brains driving all three): chosen functions are wrapped to read
# the heap before and after each call
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-precise-memory-info'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""(stage) => { const T = __T, P = T.P, S = T.SLIME; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(77, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          const mem = () => performance.memory.usedJSHeapSize, acc = {};
          const wrap = (obj, k, name) => { const f = obj[k]; obj[k] = function (...a) { const h = mem(); const r = f.apply(this, a); const d = mem() - h; const e = acc[name] || (acc[name] = [0, 0]); e[0] += d > 0 ? d : 0; e[1]++; return r; }; };
          wrap(S, 'update', 'slime.update');
          for (let i = 0; i < 240; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          for (const k in acc) acc[k] = [0, 0];
          let tStep = 0, tVis = 0, hS = 0, hV = 0, hR = 0; const N = 300;
          for (let i = 0; i < N; i++) { let h = mem(); T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); let d = mem() - h; hS += d > 0 ? d : 0; h = mem(); T.visuals(1 / 60, 1 / 60); d = mem() - h; hV += d > 0 ? d : 0; h = mem(); T.flushTrail && T.flushTrail(); if (i % 2 === 0) T.renderFrame(); d = mem() - h; hR += d > 0 ? d : 0; }
          const out = { stepKBf: +(hS / N / 1024).toFixed(1), visualsKBf: +(hV / N / 1024).toFixed(1), renderKBper2f: +(hR / N / 1024).toFixed(1) };
          for (const k in acc) out[k + ' B/call'] = Math.round(acc[k][0] / Math.max(1, acc[k][1]));
          return out; }""", STAGE)
        print(PAGE, STAGE, json.dumps(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
