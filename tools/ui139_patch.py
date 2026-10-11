#!/usr/bin/env python3
"""v211: the axolotl's head, round like the old character's. Its two bodies come from a reshaped pack (tools/headround.py: the flat plate
under its head and the hard edge along its jaw filled out into a ball round the face sphere, normals and the skin's pattern moved with
it), and its face spans a wider angle on that ball (tools/mk_axo_embed.py), so its eyes and mouth come out bigger, as the slime's did.
What sits on its face (glasses, the hockey mask) grows with it."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui138_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the face's size on the head, for what's worn on it (the axolotl's face spans 1.1 / 0.9 of the angle it did)
rep("return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, headR0: HEAD_R0 };", "return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, headR0: HEAD_R0, faceK: 1.18 };")
rep("W.hockey.scale.multiplyScalar(mk * HOCKEY_FIT.s);", "W.hockey.scale.multiplyScalar(mk * HOCKEY_FIT.s * (CH.faceK || 1));")
rep("W.glasses.scale.multiplyScalar(mk * 0.56);", "W.glasses.scale.multiplyScalar(mk * 0.56 * (CH.faceK || 1));")
rep('<p class="ver">Version 210</p>', '<p class="ver">Version 211</p>')
open(DST, 'w').write(s)
print('ui139 ok', n0, '->', len(s))
