#!/usr/bin/env python3
"""The canvas vote stays open a little longer. On top of ui29_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui29_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep(".vvote.ticking .vtimer i{transition:transform var(--vt,3.2s) linear;transform:scaleX(0)}", ".vvote.ticking .vtimer i{transition:transform var(--vt,4.9s) linear;transform:scaleX(0)}")
rep("who.slice(1).forEach((D, i) => at(1300 + i * 650 + Math.random() * 500,", "who.slice(1).forEach((D, i) => at(1700 + i * 900 + Math.random() * 600,")
rep("  at(3300, () => {", "  at(5000, () => {")
rep('<p class="ver">Version 99</p>', '<p class="ver">Version 100</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
