#!/usr/bin/env python3
"""v254: a dash out of a basin curls into a ball and can go either way (a plain jump's dash only goes forward) (v254_dodge.py);
the body answers being spun round, the lower trunk, tail and ears trailing it (v254_spin.py); Showdown, four of you or two pairs
with two hearts each, last one standing wins (v254_show.py with v254_show.js and v254_show.css)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui193_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
assert s.count('<p class="ver">Version 253</p>') == 1; s = s.replace('<p class="ver">Version 253</p>', '<p class="ver">Version 254</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v254_dodge, v254_spin, v254_show
for m in (v254_dodge, v254_spin, v254_show): s = m.apply(s)
open(DST, 'w').write(s); print('ui194 ok', n0, '->', len(s))
