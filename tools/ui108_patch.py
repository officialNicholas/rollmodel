#!/usr/bin/env python3
"""v183: in the first real match, the coach's sun and rain tips slow time and dim the screen for a couple of seconds (timing in tools/assets/tutorial.js)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui107_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK;", "if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK; else if (tut2 && tut2.slowK < 1 && state === 'play') dt *= tut2.slowK;")
rep('<p class="ver">Version 182</p>', '<p class="ver">Version 183</p>')
open(DST, 'w').write(s)
print('ui108 ok', n0, '->', len(s))
