# is the hot code optimized? V8's optimization status for chosen functions after a stretch of a live 3-way match, and the deopts the slime
# update and the CPU brain go through (from V8's trace)
import asyncio, sys, json, re
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
FLAGS = '--allow-natives-syntax --trace-opt --trace-deopt' if len(sys.argv) > 2 and sys.argv[2] == 'trace' else '--allow-natives-syntax'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--js-flags=' + FLAGS])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, S = T.SLIME; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i = 0; i < 900; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const st = f => { const s = %GetOptimizationStatus(f); const bits = []; const names = ['isFunction','neverOpt','alwaysOpt','maybeDeopted','optimized','maglevved','turbofanned','interpreted','markedForOpt','markedForConcOpt','optimizingConc','isExecuting','topmostFrameTurbofanned','liteMode','markedForDeopt','baseline','topmostFrameInterpreted','topmostFrameBaseline','isLazy','topmostFrameMaglev','optOsrCached']; for (let i = 0; i < names.length; i++) if (s & (1 << i)) bits.push(names[i]); return bits.join(','); };
          const raw = f => %GetOptimizationStatus(f); const small = { surfaceUnder: raw(T.surfaceUnder), blockedAt: raw(T.blockedAt), knockOut: raw(T.knockOut), dodgeRoll: raw(T.dodgeRoll), jump: raw(T.jump) }; return { small, ua: navigator.userAgent.slice(-30), rawUpdate: raw(S.update), rawRender: raw(T.renderFrame), rawStep: raw(T.step), update: st(S.update), visuals: st(T.visuals), step: st(T.step), aiThink: st(T.aiThink), aiStep: st(T.aiStep), renderFrame: st(T.renderFrame) }; }""")
        print(PAGE, json.dumps(r, indent=0)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
