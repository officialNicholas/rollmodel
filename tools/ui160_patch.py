#!/usr/bin/env python3
"""v227: the axolotl's look. The original Meshy texture is back on it (the dorsal band, the cream belly, the flank stripes, the spot
clusters, the blue fin with its veins), the locker colours turn its hue and keep every bit of that detail, thin parts let light through,
and the head is one smooth bulbous dome with the face on its curve (no flat plate, no rim). The runtime and the pack come from the look
work (axo_base_v227.js, the textures inside the pack)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui159_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'USE_MAP' in s and 'texFromBytes' in s, 'the textured runtime is not in the build'
rep('<p class="ver">Version 226</p>', '<p class="ver">Version 227</p>')
open(DST, 'w').write(s)
print('ui160 ok', n0, '->', len(s))
