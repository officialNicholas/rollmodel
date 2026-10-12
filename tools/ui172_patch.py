#!/usr/bin/env python3
"""v239: the slime's head and floppy ears on the axolotl body (the slime-head agent's v10 A: axo/tools6). The head is the slime's own
surface sampled onto the axolotl head, with its flattened face front and crown; the two ears are the slime's ear meshes, hanging past the
cheeks on their bone chains, bending with the head's motion. The gill frills are gone. The mesh ships as axo-pack-239.txt."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui171_patch.py'], check=True, env=dict(os.environ, AXO_BASE=os.environ.get('AXO_BASE', S + '/tools/assets/axo_base_v239.js')))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'this.gillSpring.k = 75' in s, 'the v239 animator is not in the build'
rep("AXOC.load(window.AXO_PACK || 'axo-pack.txt')", "AXOC.load(window.AXO_PACK || 'axo-pack-239.txt')")
rep('<p class="ver">Version 238</p>', '<p class="ver">Version 239</p>')
open(DST, 'w').write(s)
print('ui172 ok', n0, '->', len(s))
