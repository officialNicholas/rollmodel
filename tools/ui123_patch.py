#!/usr/bin/env python3
"""v198: the winner screen's bottom row (1st, the rival cards, Tap to see the canvas) sits lower. The page itself already stops above
the phone's home bar (the :root padding), so the screen's own bottom padding no longer adds that inset a second time."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui122_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep(".victory{padding:max(14px,calc(env(safe-area-inset-top) + 8px)) 16px max(14px,env(safe-area-inset-bottom))}", ".victory{padding:max(14px,calc(env(safe-area-inset-top) + 8px)) 16px 10px}")
rep('<p class="ver">Version 197</p>', '<p class="ver">Version 198</p>')
open(DST, 'w').write(s)
print('ui123 ok', n0, '->', len(s))
