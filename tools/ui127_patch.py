#!/usr/bin/env python3
"""v202: behind a tip between matches the screen is darker (0.66) and softly blurred, outside the window round what the tip is about; the
coach's cards blur what is behind them too (that half lives in tools/assets/tutorial.css)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui126_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="ver">Version 201</p>', '<p class="ver">Version 202</p>')
open(DST, 'w').write(s)
print('ui127 ok', n0, '->', len(s))
