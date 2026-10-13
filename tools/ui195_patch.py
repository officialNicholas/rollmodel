#!/usr/bin/env python3
"""v255: Rematch (New canvas) opens the canvas vote first, to pick another canvas or change the CPUs' difficulty; the fight card's top
labels keep clear of the notch or the app's bar (v255_rematch.py)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui194_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
assert s.count('<p class="ver">Version 254</p>') == 1; s = s.replace('<p class="ver">Version 254</p>', '<p class="ver">Version 255</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v255_rematch
s = v255_rematch.apply(s)
open(DST, 'w').write(s); print('ui195 ok', n0, '->', len(s))
