#!/usr/bin/env python3
"""v176: the lesson's flower waits a couple of seconds after the rocket dodge (the delay itself lives in tools/assets/tutorial.js)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui100_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="ver">Version 175</p>', '<p class="ver">Version 176</p>')
open(DST, 'w').write(s)
print('ui101 ok', n0, '->', len(s))
