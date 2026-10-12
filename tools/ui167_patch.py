#!/usr/bin/env python3
"""v234: the first real match's gift comes again. Its spot finder had the same name as the lesson finale's (added in v223), so the later one
replaced it: the gift's call handed it plain numbers and it threw "number is not iterable" every frame, an error box came up and the gift
never appeared. The gift's own finder is now tutGiftSpot."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui166_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function tutNearSpot(d0, d1) {", "function tutGiftSpot(d0, d1) { /* (the first real match's gift: open floor d0 to d1 ahead of you; it once shared its name with the finale's spot finder below, which replaced it) */")
rep("const s = (tut2 && tutNearSpot(6, 11)) || giftSpot();", "const s = (tut2 && tutGiftSpot(6, 11)) || giftSpot();")
assert s.count('function tutNearSpot(') == 1
rep('<p class="ver">Version 233</p>', '<p class="ver">Version 234</p>')
open(DST, 'w').write(s)
print('ui167 ok', n0, '->', len(s))
