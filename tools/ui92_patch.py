#!/usr/bin/env python3
"""The buzzer while you are knocked out: the paint flood parts at once instead of sitting over the ending with its respawn count (blobs stop stepping once the match is over, so the count never ran out). On top of ui91_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui91_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  state = 'dead'; for (const D of ACTIVE) if (D.charging) clearCharge(D);\n  aimRing.visible = false; arrow.visible = false; hintEl.classList.remove('on');",
    "  state = 'dead'; for (const D of ACTIVE) if (D.charging) clearCharge(D);\n  aimRing.visible = false; arrow.visible = false; hintEl.classList.remove('on'); if (kof) kofOpen(); // (out at the buzzer: the flood parts for the ending)")
rep('<p class="ver">Version 161</p>', '<p class="ver">Version 162</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui92 ok', n0, '->', len(s))
