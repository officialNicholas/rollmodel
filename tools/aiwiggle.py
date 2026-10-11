"""Where the CPU's visible wiggles come from: runs a simulated match on each stage given, traces every steering decision one CPU makes
for 60 s, and puts each wiggle (a hard turn one way, then a hard turn the other way within a second, rolling at speed) down to what
changed in between: a new target (re-plan), the next waypoint on the same route, the hazard check bending the heading, or nothing
(the steering itself overshooting).
usage: aiwiggle.py <stages comma list> [difficulty] [team]"""
import asyncio, os, json, math, sys, time
from playwright.async_api import async_playwright
STS = sys.argv[1].split(','); DF = sys.argv[2] if len(sys.argv) > 2 else 'medium'; TEAM = int(sys.argv[3]) if len(sys.argv) > 3 else 1
wrap = lambda a: math.atan2(math.sin(a), math.cos(a))
def analyse(tr):
    # tr rows: t, tx, tz, x, z, yaw, steer, mode, urgent, precise, safeWant, safeRes, charging, spd, pi, pathLen, tgt, turn
    wig = []; lastS = 0; lastI = None
    for i, r in enumerate(tr):
        if r[12] or r[13] < 2 or abs(r[17]) < 1.2: continue
        sg = 1 if r[17] > 0 else -1
        if lastI is not None and sg != lastS and r[0] - tr[lastI][0] < 1: wig.append((lastI, i))
        lastS = sg; lastI = i
    causes = {}; ex = {}
    for a, b in wig:
        seg = tr[a:b + 1]
        if any(s[16] != seg[0][16] for s in seg): k = 'replan'
        elif any(s[10] is not None and abs(wrap(s[11] - s[10])) > 0.25 for s in seg): k = 'hazard'
        elif any(s[14] != seg[0][14] for s in seg) or any(math.hypot(s[1] - seg[0][1], s[2] - seg[0][2]) > 0.6 for s in seg): k = 'waypoint'
        elif any(s[7] != seg[0][7] for s in seg): k = 'mode'
        else: k = 'overshoot'
        causes[k] = causes.get(k, 0) + 1; ex.setdefault(k, []).append((tr[a], tr[b]))
    return wig, causes, ex
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, flings: 99, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + os.environ.get('PAGE', 'pc_perf.html'), timeout=300000)
        for i in range(200):
            if await pg.evaluate("typeof __T === 'object' && !!window.__pf"): break
            await pg.wait_for_timeout(2500)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        tot = {}; n = 0; dur = 0
        for ST in STS:
            await pg.evaluate(f"(() => {{ window.__noStep = false; __T.setStage('{ST}'); __T.setDiff('{DF}'); __T.setAI('{DF}'); __T.start(); }})()")
            t0 = time.time()
            while time.time() - t0 < 240 and await pg.evaluate("__T.state") != 'play': await pg.wait_for_timeout(500)
            await pg.evaluate(f"(() => {{ window.__noStep = true; window.__perfAI(); __T.setAI('{DF}'); window.__trace = []; window.__traceD = __T.ACTIVE.find(D => D.team === {TEAM}); }})()")
            await pg.evaluate("(() => { const T = __T, dt = 1 / 60; for (let i = 0; i < 3600 && T.state === 'play'; i++) { T.step(dt / 2); T.step(dt / 2); T.visuals(dt, dt); T.flushTrail(); } })()")
            tr = await pg.evaluate("__trace")
            json.dump(tr, open(f'/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/aiwig_{ST}_{DF}_{TEAM}' + os.environ.get('TAG', '') + '.json', 'w'))
            wig, causes, ex = analyse(tr); d = (tr[-1][0] - tr[0][0]) if tr else 1; dur += d; n += len(wig)
            for k, v in causes.items(): tot[k] = tot.get(k, 0) + v
            print(f'{ST}/{DF} team {TEAM}: {len(wig)} wiggles in {d:.0f}s ({60 * len(wig) / max(1, d):.1f}/min)', causes)
            for k, v in ex.items():
                for ra, rb in v[:2]: print('    ', k, '|', ra, '|', rb)
            await pg.evaluate("window.__noStep = false")
            await pg.evaluate("(() => { try { __T.toMenu(); } catch (e) {} })()"); await pg.wait_for_timeout(3000)
        print(f'ALL: {n} wiggles in {dur:.0f}s ({60 * n / max(1, dur):.1f}/min)', tot, 'errors', errs[:3])
        await b.close()
asyncio.run(main())
