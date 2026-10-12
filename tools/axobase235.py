#!/usr/bin/env python3
"""The v235 runtime base: the look agent's v9b runtime ($S/fable2/out/axo.js: the v227 base plus axo/tools5/look9.py) with the gill motion
tuned for the hanging, ear-like lobes: more drag from the head's motion, and the lowest lobe moving nearly as much as the others."""
import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
src = open(S + '/fable2/out/axo.js').read()
def rep(old, new):
    global src
    assert src.count(old) == 1, old
    src = src.replace(old, new)
rep("const cm = hold, lo = 0.4;", "const cm = hold, lo = 0.7;")
rep("const stalkAmp = [cm, 0.9 * cm, lo * cm, cm, 0.9 * cm, lo * cm];", "const stalkAmp = [cm, 0.85 * cm, lo * cm, cm, 0.85 * cm, lo * cm];")
rep("cl(flutter - _v.z * 15 - this.accS.z * 6)", "cl(flutter - _v.z * 22 - this.accS.z * 6)")
rep("cl(-_v.x * 15 - this.accS.x * 5 * sgn)", "cl(-_v.x * 20 - this.accS.x * 5 * sgn)")
open(S + '/tools/assets/axo_base_v235.js', 'w').write(src); print('axo_base_v235 ok', len(src))
