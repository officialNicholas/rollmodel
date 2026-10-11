#!/usr/bin/env python3
"""v228: the axolotl swims at speed instead of thrashing. It crawls up to speed, then goes into strokes, a push then a glide: on the
push the arms sweep back, the body surges forward and the head dips into it; on the glide the arms and legs lie along its sides like a
swimmer's with the fingers closed, a slow gentle wave runs down the body, the tail sways slowly side to side, and the head comes up, held
to the way it's going. (The animator, axolife.js, carries it.)"""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui160_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'SL.reach' in s and 'SLITHER.pw' in s, 'the swimming runtime is not in the build'
rep('<p class="ver">Version 227</p>', '<p class="ver">Version 228</p>')
open(DST, 'w').write(s)
print('ui161 ok', n0, '->', len(s))
