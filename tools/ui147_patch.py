#!/usr/bin/env python3
"""v219: the axolotl's body bends with it (tools/assets/axolife.js). Round a turn the whole body curves into a C: the trunk takes most
of it, the neck and head carry the curve on instead of kinking at the neck, the tail follows it round; the bend eases in on a spring and
swings back past straight when the turn ends. Running straight, the back throws a stronger salamander wave with each pair of steps, the
tail answering it in an S. The hands and feet step from where the bent body carries the shoulders and hips, so they still never slide."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui146_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'l.hb.set(' in s and 'this.tailLat += L.bend' in s, 'the bending runtime is not in the build'
rep('<p class="ver">Version 218</p>', '<p class="ver">Version 219</p>')
open(DST, 'w').write(s)
print('ui147 ok', n0, '->', len(s))
