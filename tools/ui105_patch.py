#!/usr/bin/env python3
"""v180: Let's do it on the lesson's win card refills the paint tank and readies the pound (change in tools/assets/tutorial.js)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui104_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="ver">Version 179</p>', '<p class="ver">Version 180</p>')
open(DST, 'w').write(s)
print('ui105 ok', n0, '->', len(s))
