#!/usr/bin/env python3
"""v196: the lesson opens straight on "drag to steer, tap to jump": its Paint it red! banner moves to the start of the real fight, right
after the Now win it card's Let's do it (that half lives in tools/assets/tutorial.js)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui120_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("setTimeout(() => { if (state === 'play') banner('Paint it ' + colorOf().name.toLowerCase() + '!',", "setTimeout(() => { if (state === 'play' && !tut) banner('Paint it ' + colorOf().name.toLowerCase() + '!',")
rep('<p class="ver">Version 195</p>', '<p class="ver">Version 196</p>')
open(DST, 'w').write(s)
print('ui121 ok', n0, '->', len(s))
