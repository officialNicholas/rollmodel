# line-level CPU profile of chosen functions (Chrome's sampler with position ticks) over a 3-way match: which lines of the CPU brain take
# the time
import asyncio, sys, json, collections
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
FN = sys.argv[2].split(',') if len(sys.argv) > 2 else ['aiThink']
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
          for (let i = 0; i < 600; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } }""")
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 100})
        await cdp.send('Profiler.start')
        await pg.evaluate("() => { const T = __T, P = T.P; for (let i = 0; i < 2400; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(0.0083); T.step(0.0083); if (i % 4 === 0) T.visuals(1 / 15, 1 / 15); } }")
        prof = (await cdp.send('Profiler.stop'))['profile']
        lines = collections.Counter(); fnTot = collections.Counter(); hz = prof['endTime'] - prof['startTime']; ns = len(prof['samples'])
        us = hz / max(1, ns)
        for n in prof['nodes']:
            cf = n['callFrame']; name = cf['functionName']
            if name in FN or any(name == f for f in FN):
                for pt in n.get('positionTicks', []): lines[(name, pt['line'])] += pt['ticks']
                fnTot[name] += n.get('hitCount', 0)
        src = open(SP + PAGE).read().split('\n')
        print('us/sample %.0f' % us, 'fn self ms', {k: round(v * us / 1000, 1) for k, v in fnTot.items()})
        for (name, ln), t in lines.most_common(30): print('%7.1f ms  %s:%d  %s' % (t * us / 1000, name, ln, src[ln - 1].strip()[:150]))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
