#!/usr/bin/env python3
"""v241: the axolotl's neck and chest reworked (the head ball fillets into a fuller neck out of a fuller chest, no ledge or ring), fuller
upper arms and thighs, a soft toon ramp on the shading (the dark side lifted, a warm fill, a crisper small highlight; the material kept),
and calmer idle eyes (glances 2.5 to 6 s apart, eased, smaller darts). The slime-head agent's v10c. The mesh ships as axo-pack-241.txt."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui178_patch.py'], check=True, env=dict(os.environ, AXO_BASE=os.environ.get('AXO_BASE', S + '/tools/assets/axo_base_v241.js')))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'uToon' in s and '0.57 * H.r' in s, 'the v241 runtime or the neck anchor is not in the build'
rep("AXOC.load(window.AXO_PACK || 'axo-pack-239.txt')", "AXOC.load(window.AXO_PACK || 'axo-pack-241.txt')")
open(DST, 'w').write(s)
print('ui179 ok', n0, '->', len(s))
