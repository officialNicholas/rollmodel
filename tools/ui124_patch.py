#!/usr/bin/env python3
"""v199: the coach in person, and his name: Ol’ Bloop. The user's render, cut to half his body (art/coach.webp), replaces the little face icon: in a match he comes up
out of a bottom corner with his line in a bubble over him; between matches he leans up out of his plate; over a card he looks over its top
edge (that half lives in tools/assets/tutorial.js and .css)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui123_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<b class="tname">Coach</b>', '<b class="tname">Ol&rsquo; Bloop</b>', 2)  # (the coach has a name now)
rep('<p class="ver">Version 198</p>', '<p class="ver">Version 199</p>')
open(DST, 'w').write(s)
print('ui124 ok', n0, '->', len(s))
