#!/usr/bin/env python3
"""v182: while onboarding runs, the canvas page hides the mode tabs (Solo, 1v1, 3-way) and the CPU difficulty row."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui106_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('.menu.tutoring #commBtn,.menu.tutoring #howBtn{display:none}', '.menu.tutoring #commBtn,.menu.tutoring #howBtn{display:none}\n.menu.tutoring #modes,.menu.tutoring .wfoot .critics,.menu.tutoring #stages{display:none}')
rep('<p class="ver">Version 181</p>', '<p class="ver">Version 182</p>')
open(DST, 'w').write(s)
print('ui107 ok', n0, '->', len(s))
