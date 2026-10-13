#!/usr/bin/env python3
"""v253: the Strokes page's pictures painted with Ludo.ai in the game's glossy icon style (v253_icons.py)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui192_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
assert s.count('<p class="ver">Version 252</p>') == 1; s = s.replace('<p class="ver">Version 252</p>', '<p class="ver">Version 253</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v253_icons
s = v253_icons.apply(s)
open(DST, 'w').write(s); print('ui193 ok', n0, '->', len(s))
