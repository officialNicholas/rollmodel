#!/usr/bin/env python3
"""The pound button loses the old cooldown wedge (a dark pie over the disc, which never read as a circle): the corner dial alone counts the cooldown. On top of ui94_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui94_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep(".slamBtn::after{border-radius:50%;background:conic-gradient(rgba(23,19,32,.55) var(--cd,0deg),transparent 0)}", ".slamBtn::after{display:none} /* (the cooldown is the corner dial's; no pie over the disc) */")
rep("  if (b._cd !== cd) { b._cd = cd; b.style.setProperty('--cd', cd); }", "  if (b._cd !== cd) { b._cd = cd; } // (the disc no longer shades with the cooldown)")
rep('<p class="ver">Version 164</p>', '<p class="ver">Version 165</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui95 ok', n0, '->', len(s))
