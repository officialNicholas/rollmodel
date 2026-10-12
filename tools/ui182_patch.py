#!/usr/bin/env python3
"""v244: turning on the spot with the arms and a curved torso (the animator)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui181_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
assert 'L.pv = clamp01' in s, 'the pivot is not in the animator'
s = s.replace('<p class="ver">Version 243</p>', '<p class="ver">Version 244</p>')
open(DST, 'w').write(s); print('ui182 ok', n0, '->', len(s))
