#!/usr/bin/env python3
"""v243: the swipe-up dodge: for the roll's quick part the axolotl is the jelly ball (a pop of paint each way), as on a long slingshot."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui180_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("(flK0 > (V.balled ? 0.12 : 0.3) || D.rollOutT > (V.balled ? 0.1 : 0.16));",
    "(flK0 > (V.balled ? 0.12 : 0.3) || D.rollOutT > (V.balled ? 0.1 : 0.16) || D.rollT > (V.balled ? ROLL_T - ROLL_DASH : ROLL_T - ROLL_DASH + 0.06)); /* (the dodge roll: a ball for its tumble, the axolotl back as it comes round onto its feet) */")
rep('<p class="ver">Version 242</p>', '<p class="ver">Version 243</p>')
open(DST, 'w').write(s)
print('ui181 ok', n0, '->', len(s))
