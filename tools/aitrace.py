"""Why the CPU's steering flips hard left to hard right so often: every steering decision it makes for 40 s of a simulated match (its
target, the heading it wanted before and after steering clear of hazards, the steering it set), and each flip put down to a cause:
the target jumped, the hazard check swung the heading, or it simply overshot"""
import asyncio, json, math, sys, time
from playwright.async_api import async_playwright
ST = sys.argv[1] if len(sys.argv) > 1 else 'crypt'; DF = sys.argv[2] if len(sys.argv) > 2 else 'medium'; TEAM = int(sys.argv[3]) if len(sys.argv) > 3 else 1
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, flings: 99, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000)
        for i in range(200):
            if await pg.evaluate("typeof __T === 'object' && !!window.__pf"): break
            await pg.wait_for_timeout(2500)
        await pg.evaluate(f"(() => {{ __T.renderer.render = () => {{}}; __T.setStage('{ST}'); __T.setDiff('{DF}'); __T.setAI('{DF}'); __T.start(); }})()")
        t0 = time.time()
        while time.time() - t0 < 240 and await pg.evaluate("__T.state") != 'play': await pg.wait_for_timeout(500)
        await pg.evaluate(f"(() => {{ window.__noStep = true; window.__perfAI(); __T.setAI('{DF}'); window.__trace = []; window.__traceD = __T.ACTIVE.find(D => D.team === {TEAM}); }})()")
        await pg.evaluate("(() => { const T = __T, dt = 1 / 60; for (let i = 0; i < 2400 && T.state === 'play'; i++) { T.step(dt / 2); T.step(dt / 2); T.visuals(dt, dt); T.flushTrail(); } })()")
        tr = await pg.evaluate("__trace")
        json.dump(tr, open(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/aitrace_{ST}_{DF}_{TEAM}.json', 'w'))
        print('records', len(tr), 'errors', errs[:3])
        wrap = lambda a: math.atan2(math.sin(a), math.cos(a))
        flips = []; last = None
        for i, r in enumerate(tr):
            s = r[6]
            if abs(s) > 0.35:
                if last is not None and (s > 0) != (tr[last][6] > 0): flips.append((last, i))
                last = i
        causes = {'target jump': 0, 'hazard swing': 0, 'overshoot': 0, 'pivot/charging': 0}; ex = {}
        for a, b2 in flips:
            ra, rb = tr[a], tr[b2]
            moved = math.hypot(rb[1] - ra[1], rb[2] - ra[2]) > 0.5
            sa = None if ra[10] is None else wrap(ra[11] - ra[10]); sb = None if rb[10] is None else wrap(rb[11] - rb[10])
            swing = (sa is not None and abs(sa) > 0.25) or (sb is not None and abs(sb) > 0.25)
            k = 'pivot/charging' if ra[12] or rb[12] else 'target jump' if moved else 'hazard swing' if swing else 'overshoot'
            causes[k] += 1; ex.setdefault(k, []).append((ra, rb))
        dur = (tr[-1][0] - tr[0][0]) if tr else 1
        print(f'{ST}/{DF} team {TEAM}: {len(flips)} flips in {dur:.0f}s game time ({60 * len(flips) / max(1, dur):.0f}/min):', causes)
        for k, v in ex.items():
            for ra, rb in v[:3]: print('  ', k, '| before', ra, '| after', rb)
        # how big the weave is when going straight: heading error to the target while not charging
        errs2 = [abs(wrap(math.atan2(r[1] - r[3], r[2] - r[4]) - r[5])) for r in tr if not r[12]]
        if errs2: errs2.sort(); print('heading error to target (not charging): p50 %.2f p90 %.2f rad' % (errs2[len(errs2) // 2], errs2[int(len(errs2) * .9)]))
        await b.close()
asyncio.run(main())
