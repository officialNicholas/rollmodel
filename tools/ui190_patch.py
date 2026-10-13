#!/usr/bin/env python3
"""v250: the new crawl model (the user's cleaned-up Meshy model) in place of the v246 body: rigged onto the same 73-bone skeleton (bone
heat weights, a symmetric crawl rest, the IK's limb frames, level hands and feet), its own texture recoloured onto the runtime's pink so
team tints work, the same runtime; its pack is axo-pack-250.txt. With it (v250_play.py, v250_ui.py, v250_art.py): the lesson finale
without rollers, the orb timed so the rocket lands on the buzzer; the locker's swipe finger; the kill cam steering you clear of drops;
blobs settling after the buzzer; less paint used; shop prices down about 15%; rain that waters paint down; a floor pointer to the nearest
basin; the winner screen's portrait framing; a smoother canvas vote page; fresh gallery photos."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui189_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("const axoLoad = AXOC.load(window.AXO_PACK || 'axo-pack-246.txt')", "const axoLoad = AXOC.load(window.AXO_PACK || 'axo-pack-250.txt')")
rep('<p class="ver">Version 249</p>', '<p class="ver">Version 250</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v250_play, v250_ui, v250_abil, v250_art
s = v250_play.apply(s); s = v250_ui.apply(s); s = v250_abil.apply(s); s = v250_art.apply(s)
open(DST, 'w').write(s); print('ui190 ok', n0, '->', len(s))
