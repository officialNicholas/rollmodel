#!/usr/bin/env python3
"""v256: Flash Freeze 5 s with tap-to-break-out, the orb in your slot with a 10 s clock (Deep Pockets keeps it), a darker bigger Paint
Trap, the turret draining paint like health, Showdown CPUs saving the pound for rivals, the results leading only to the lobby when a
lesson waits there, Solo renamed Time trial (v256_play.py); everyone's own colours with rivals shown apart from yours and 2v2 team
colours mixed from each pair (v256_colors.py); the Showdown canvas closing in each minute (v256_zone.py); a quicker start (v256_load.py); the Showdown's top bar as just
the faces and hearts with the time between the sides (v256_sdhud.py)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui195_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
assert s.count('<p class="ver">Version 255</p>') == 1; s = s.replace('<p class="ver">Version 255</p>', '<p class="ver">Version 256</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v256_play, v256_colors, v256_zone, v256_load, v256_sdhud
for m in (v256_play, v256_colors, v256_zone, v256_load, v256_sdhud): s = m.apply(s)
open(DST, 'w').write(s); print('ui196 ok', n0, '->', len(s))
