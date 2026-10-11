#!/usr/bin/env python3
"""v204: the window round what a tip points at shows on iPhones too. The dim was one sheet with a clip-path hole, which Safari didn't
always repaint when the hole moved (taps still went through, the picture stayed dark). Now it is four panes round the window
(the panes and their styles live in tools/assets/tutorial.js and tutorial.css; the markup is here)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui128_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<div class="tutdim" id="tutDim" aria-hidden="true"></div>', '<div class="tutdim" id="tutDim" aria-hidden="true"><b></b><b></b><b></b><b></b></div>')
rep('<p class="ver">Version 203</p>', '<p class="ver">Version 204</p>')
open(DST, 'w').write(s)
print('ui129 ok', n0, '->', len(s))
