#!/usr/bin/env python3
"""Drying up no longer knocks you out: you crawl until you reach your own colour or a refill, and the dried-up respawn screen is gone with it. Plus an app-wide polish pass (see the CSS block). On top of ui81_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui81_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("if (D.dry && D.st === 'play' && state === 'play') { D.dryT = (D.dryT || 0) + dt; if (D.dryT >= DRY_KO) { knockOut(D, 'dry'); return; } } else if (!D.dry) D.dryT = 0;",
    "if (D.dry && D.st === 'play' && state === 'play') D.dryT = (D.dryT || 0) + dt; else if (!D.dry) D.dryT = 0; // (drying up slows you; it no longer knocks you out)")
POLISH_CSS = open(S + '/tools/assets/polish.css').read() if __import__('os').path.exists(S + '/tools/assets/polish.css') else ''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + POLISH_CSS + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
