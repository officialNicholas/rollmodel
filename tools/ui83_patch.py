#!/usr/bin/env python3
"""The Season One sign comes off the locker's wall (the pumpkins, candles and bat stay). On top of ui82_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui82_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("sign.position.set(0, 1.28, -2.33); sign.scale.setScalar(0.4); sign.renderOrder = 32; lobbyProps.add(sign);", "sign.position.set(0, 1.28, -2.33); sign.scale.setScalar(0.4); sign.renderOrder = 32; sign.visible = false; // (the sign is off the wall)")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
