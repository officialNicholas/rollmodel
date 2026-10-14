#!/usr/bin/env python3
"""v257: the Strokes page reworked: skills crafted like the special strokes, a card for each stroke with Craft and Equip, tiles
with just Equipped on the one you have on, no downsides or plus signs listed (v257_skills.py); the ground pound ready 4 seconds into a match, not 10 (v257_play.py); Time trial and Showdown opening at rank 2
with the Strokes (v257_lock.py)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui196_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
assert s.count('<p class="ver">Version 256</p>') == 1; s = s.replace('<p class="ver">Version 256</p>', '<p class="ver">Version 257</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v257_skills, v257_play, v257_lock
for m in (v257_skills, v257_play, v257_lock): s = m.apply(s)
open(DST, 'w').write(s); print('ui197 ok', n0, '->', len(s))
