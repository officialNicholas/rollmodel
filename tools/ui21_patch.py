#!/usr/bin/env python3
"""The locker tile pop no longer shares a class with the hidden score float. On top of ui20_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui20_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# .pop is the floating score text (opacity 0 until it rises); the tiles and eye chips borrowed its name for their bounce and vanished with it
rep('.ltile.pop,.eyec.pop', '.ltile.tpop,.eyec.tpop', 2)
rep('.eyes.pop{animation:tilepop', '.eyes.tpop{animation:tilepop')
rep("kick(t, 'pop')", "kick(t, 'tpop')", 3)
rep('<p class="ver">Version 90</p>', '<p class="ver">Version 91</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
