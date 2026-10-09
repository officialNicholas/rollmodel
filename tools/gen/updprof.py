# sampling heap profile of the slime update alone, in a live match's state: what it allocates, by function (and in the menu state too)
import asyncio, sys, json, collections
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
WHAT = sys.argv[2] if len(sys.argv) > 2 else 'update'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate("""() => { const T = __T, P = T.P; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i = 0; i < 240; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } }""")
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('HeapProfiler.enable'); await cdp.send('HeapProfiler.collectGarbage')
        await cdp.send('HeapProfiler.startSampling', {'samplingInterval': 128, 'includeObjectsCollectedByMajorGC': True, 'includeObjectsCollectedByMinorGC': True})
        if WHAT == 'update':
            n = await pg.evaluate("() => { const T = __T, S = T.SLIME, I = T.VP.slime, o = T.VP.so; for (let i = 0; i < 5000; i++) { o.pos[2] += 0.01; S.update(I, o); } return 5000; }")
        else:
            n = await pg.evaluate("() => { const T = __T, P = T.P; for (let i = 0; i < 300; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } return 300; }")
        prof = (await cdp.send('HeapProfiler.stopSampling'))['profile']
        agg = collections.Counter(); tot = 0
        def walk(nd, stack):
            nonlocal tot
            cf = nd['callFrame']; name = (cf['functionName'] or '(anon)') + ':' + str(cf['lineNumber'] + 1) + ':' + str(cf['columnNumber'] + 1)
            st = stack + [name]
            if nd['selfSize']: tot += nd['selfSize']; agg[' < '.join(st[-1:-4:-1])] += nd['selfSize']
            for c in nd.get('children', []): walk(c, st)
        walk(prof['head'], [])
        print(PAGE, WHAT, 'calls', n, 'B/call %.0f' % (tot / n))
        for k, v in agg.most_common(16): print('%9.0f B/call  %s' % (v / n, k[:220]))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
