# instrumented build: per-function timers, and per-frame breakdown of the slowest frames
import re
src = open('pc_t.html').read()
FN = ['washOut','slamLand','knockOut','burstCoffin','missileLaunch','spawnCrown','aiThink','aiSee','flingLanding','aiFlingPaint','aiShovePlan','aiAttackPlan','hazardAt','aiSafe','aiSteer','aiFollow','aiDoPlan','aiAir','aiTryPound','aiEvade','aiCoffin','dijkstra','lineClear','stepBlob','blobContact','updateParts','surfaceUnder','blockedAt','addPoint','addSplat','flushTrail','aiAirSling']
pre = "window.__PF = {};\n"
for f in FN:
    m = re.search(r'\nfunction ' + f + r'\(([^)]*)\) \{', src)
    assert m, f
    args = m.group(1)
    names = ','.join(a.split('=')[0].strip() for a in args.split(',')) if args.strip() else ''
    src = src[:m.start()] + f"\nfunction {f}({args}) {{ const __a = performance.now(); try {{ return {f}__({names}); }} finally {{ __PF['{f}'] = (__PF['{f}']||0) + performance.now() - __a; }} }}\nfunction {f}__({args}) {{" + src[m.end():]
src = src.replace('<script>', '<script>' + pre, 1)
open('pc_prof.html', 'w').write(src)
print('ok')
src = open('pc_prof.html').read()
marks = [
 ("function aiThink__(D) {\n", "function aiThink__(D) {\n  let __t0 = performance.now(), __t = __t0; const __m = k => { const n = performance.now(); __PF['T:' + k] = (__PF['T:' + k] || 0) + n - __t; __t = n; };\n"),
 ("  for (const r of rivals) if (r.on && !(Math.random() < AI.slip)) NAV.near(", "  __m('gain'); for (const r of rivals) if (r.on && !(Math.random() < AI.slip)) NAV.near("),
 ("  dijkstra(src.id, sunny ||", "  __m('mults'); dijkstra(src.id, sunny ||"),
 ("  // coffins we could use\n", "  __m('dij');\n  // coffins we could use\n"),
 ("  // 6) paint: the route", "  __m('mid');\n  // 6) paint: the route"),
 ("  if (!nTop) { ai.path = null; return; }", "  __m('cand'); if (!nTop) { ai.path = null; return; }"),
 ("  const tn = NAV.nodes[pick[1]];\n", "  __m('fling'); const tn = NAV.nodes[pick[1]];\n"),
]
for a, b in marks:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
open('pc_prof.html', 'w').write(src)
print('marks ok')
