#!/usr/bin/env python3
"""v232: motion fixes in the animator. The left hand no longer flips round for a frame at the end of each swim stroke (its facing turns
from forward to back by way of pointing out, instead of being blended straight through); a swinging foot's lift-off point lets go of the
ground over the first part of the swing, and each step lands moving back with the ground (no jolt at touchdown); and the swim takes over
a little sooner, so the crawl's top end, where the short hind legs can only scurry, is passed through quickly."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui164_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'Math.PI - 0.08 - a0' in s and 'lets go of the ground over the first part' in s and 'it lands moving back with the ground' in s and 'on: 3.8, off: 2.8' in s
rep('<p class="ver">Version 231</p>', '<p class="ver">Version 232</p>')
open(DST, 'w').write(s)
print('ui165 ok', n0, '->', len(s))
