# where a CPU's thinking spends its time: a copy of the test page with the brain's main functions wrapped in timers, a 3-way match run,
# and per function: calls, total, average, worst, and the worst frames' breakdown
import asyncio, sys, json, re
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
FNS = ['aiThink', 'dijkstra', 'aiFlingPaint', 'aiAttackPlan', 'aiShovePlan', 'flingLanding', 'aiSee', 'aiSteer', 'aiEvade', 'aiTryPound', 'aiDoPlan', 'aiAir', 'aiCoffin', 'pickFocus', 'aiRocketDodge', 'detectThreat', 'localGain', 'poundVal', 'solveFling', 'lineClear', 'aiFollow', 'hazardAt', 'aiSafe', 'stepBlob', 'blobContact', 'updateParts', 'stepCoffins', 'updateTrail', 'aiStep']
src = open(SP + PAGE).read()
for f in FNS:
    m = re.search(r'\nfunction ' + f + r'\(([^)]*)\) \{', src)
    if not m: print('missing', f); continue
    args = m.group(1)
    call = ', '.join(a.split('=')[0].strip() for a in args.split(',')) if args.strip() else ''
    rep = '\nfunction ' + f + '(' + args + ') { const __t0 = performance.now(); try { return ' + f + '__(' + call + '); } finally { const __d = performance.now() - __t0, __s = (window.__ap || (window.__ap = {}))[\'' + f + '\'] || (window.__ap[\'' + f + '\'] = [0, 0, 0]); __s[0]++; __s[1] += __d; if (__d > __s[2]) __s[2] = __d; if (window.__fr) window.__fr[\'' + f + '\'] = (window.__fr[\'' + f + '\'] || 0) + __d; } }\nfunction ' + f + '__(' + args + ') {'
    src = src[:m.start()] + rep + src[m.end():]
open(SP + 'pc_ai.html', 'w').write(src)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_ai.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""(stage) => { const T = __T, P = T.P; window.__noLoop = true;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(77, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i = 0; i < 600; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          window.__ap = {}; const frames = [];
          for (let i = 0; i < 1500; i++) { window.__fr = {}; const t0 = performance.now(); T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(0.0083); T.step(0.0083); const d = performance.now() - t0; T.visuals(1 / 60, 1 / 60); frames.push([d, window.__fr]); }
          frames.sort((a, b) => b[0] - a[0]);
          const top = frames.slice(0, 8).map(f => [+f[0].toFixed(1), Object.entries(f[1]).filter(e => e[1] > 0.3).sort((a, b) => b[1] - a[1]).map(e => e[0] + ':' + e[1].toFixed(1)).join(' ')]);
          const tab = Object.entries(window.__ap).map(([k, v]) => [k, v[0], +v[1].toFixed(1), +(v[1] / v[0]).toFixed(3), +v[2].toFixed(2)]).sort((a, b) => b[2] - a[2]);
          return { tab, top }; }""", STAGE)
        print('fn, calls, total ms, avg, worst')
        for row in r['tab']: print('  ', row)
        print('worst frames (ms: breakdown)')
        for row in r['top']: print('  ', row)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
