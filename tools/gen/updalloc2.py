# the slime update's garbage in a live match, pinned down: the same call repeated with the blob's own options object, a plain copy of it,
# and with single options changed
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--js-flags=--allow-natives-syntax', '--enable-precise-memory-info'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, S = T.SLIME; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i = 0; i < 240; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const I = T.VP.slime, o = T.VP.so, mem = () => performance.memory.usedJSHeapSize;
          const run = (oo, n) => { let pos = 0, gcs = 0, last = mem(); for (let b = 0; b < n / 100; b++) { for (let i = 0; i < 100; i++) { oo.pos[2] += 0.01; S.update(I, oo); } const m = mem(); if (m < last) gcs++; else pos += m - last; last = m; } return Math.round(pos / n) + 'B/call, ' + gcs + ' gcs'; };
          const out = {};
          out.fastO = %HasFastProperties(o); out.fastSt = %HasFastProperties(I.st); out.fastI = %HasFastProperties(I); out.fastU = %HasFastProperties(I.U);
          out.liveO = run(o, 20000);
          const c = Object.assign({}, o); c.pos = o.pos.slice(); out.copy = run(c, 20000);
          const c2 = Object.assign({}, c, { look: null }); out.noLook = run(c2, 20000);
          const c3 = Object.assign({}, c, { look: [0.01, 0.02] }); out.freshLook = run(c3, 20000);
          out.lookType = Array.isArray(o.look) ? 'arr' + o.look.length : typeof o.look;
          out.lookVals = o.look ? [o.look[0], o.look[1]] : null;
          out.form = I.form; out.expr = I.st.exprB;
          return out; }""")
        print(PAGE, json.dumps(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
