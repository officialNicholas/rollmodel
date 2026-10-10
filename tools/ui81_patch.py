#!/usr/bin/env python3
"""The tally bar: the paints share the bar by their final totals, so they meet when the count is done instead of leaving a dark gap; in a three-way the middle one grows from its own place in the row. The splat on the bar at each elimination is gone (the tick and the sound stay). The bar is the same dark glass as the results bar. On top of ui80_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui80_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("scale = Math.min(100, Math.max(30, sum * 1.18)), koq = [], maxK = Math.max(0, ...ppl.map(e => e.kos));",
    "scale = Math.max(1, sum), koq = [], maxK = Math.max(0, ...ppl.map(e => e.kos)); { let x = 0; for (const e of ppl) { e.c = (x + e.tot / 2) / scale; x += e.tot; } } // (each one's place in the finished row: the middle one grows from its own)")
rep("const tySeg = (e, f) => e.side === 'l' ? { x0: 0, x1: f, col: e.col } : e.side === 'r' ? { x0: 1 - f, x1: 1, col: e.col } : { x0: 0.5 - f / 2, x1: 0.5 + f / 2, col: e.col };",
    "const tySeg = (e, f) => e.side === 'l' ? { x0: 0, x1: f, col: e.col } : e.side === 'r' ? { x0: 1 - f, x1: 1, col: e.col } : { x0: (e.c || 0.5) - f / 2, x1: (e.c || 0.5) + f / 2, col: e.col };")
rep("restartCls(e.nu, 'tick'); tySplat(e, (e.cov + e.shown * KO_PCT) / tal.scale);", "restartCls(e.nu, 'tick');")
css = '''
.tybar{background:#221B2E}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
