#!/usr/bin/env python3
"""v251: a name tag over each rival in a match, for multiplayer: its rank on a little shield in its colour, then its name; full up close,
fading out with distance, gone while that rival hides in a basin, is knocked out or is behind a wall (v251_tags.py). With it
(v251_play.py): the second match on Sludge Sewer; skills Weather Repel and Deep Pockets beside Swim faster, each tapped open to show what
it does; everyone 6% quicker; the Paint Trap pick-up; the Flash Freeze special."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui190_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="ver">Version 250</p>', '<p class="ver">Version 251</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v251_tags, v251_play
s = v251_tags.apply(s); s = v251_play.apply(s)
open(DST, 'w').write(s); print('ui191 ok', n0, '->', len(s))
