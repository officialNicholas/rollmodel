# Where a live match allocates memory (garbage = GC pauses = stutter): sampling heap profile over ~12s of play, by function
import asyncio, sys, json, collections
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + PAGE + '.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("""() => { const T = __T; T.mode = 'trio'; T.applyMode(); T.setStage('island'); T.genWorld(77, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          window.__steer = setInterval(() => { T.steerIn = Math.sin(performance.now() / 700) * 0.8; }, 50); }""")
        await pg.wait_for_timeout(4000)
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('HeapProfiler.enable'); await cdp.send('HeapProfiler.collectGarbage')
        await cdp.send('HeapProfiler.startSampling', {'samplingInterval': 512, 'includeObjectsCollectedByMajorGC': True, 'includeObjectsCollectedByMinorGC': True})
        await pg.evaluate("() => { window.__noLoop = true; clearInterval(window.__steer); const T = __T; window.__ft = []; for (let i = 0; i < 400; i++) { T.steerIn = Math.sin(i / 40) * 0.8; const t0 = performance.now(); T.step(0.008); T.step(0.008); T.visuals(0.016, 0.016); T.flushTrail(); T.renderFrame(); __ft.push(performance.now() - t0); } }")
        prof = (await cdp.send('HeapProfiler.stopSampling'))['profile']
        ft = await pg.evaluate("__ft")
        agg = collections.Counter(); tot = 0
        def walk(n, stack):
            nonlocal tot
            cf = n['callFrame']; name = (cf['functionName'] or '(anon)') + ':' + str(cf['lineNumber'] + 1)
            st = stack + [name]
            if n['selfSize']:
                tot += n['selfSize']
                # attribute to the innermost frame from the game file, with its caller
                agg[' < '.join(st[-1:-4:-1])] += n['selfSize']
            for c in n.get('children', []): walk(c, st)
        walk(prof['head'], [])
        frames = len(ft); ms = sum(ft)
        print(PAGE, 'frames', frames, 'avg ms %.1f' % (ms / max(1, frames)), 'KB/frame %.1f' % (tot / 1024 / max(1, frames)))
        for k, v in agg.most_common(28): print('%7.0f KB  %s' % (v / 1024, k[:200]))
        await b.close()
asyncio.run(main())
