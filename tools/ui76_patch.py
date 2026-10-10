#!/usr/bin/env python3
"""The pearl necklace sits on the neck: a tighter, higher strand that wraps back round the sides instead of hanging out in front of the chest. On top of ui75_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui75_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("const pts = [[-0.9, 0.55, -0.42], [-0.7, 0.1, -0.1], [-0.38, -0.25, 0.08], [0, -0.36, 0.14], [0.38, -0.25, 0.08], [0.7, 0.1, -0.1], [0.9, 0.55, -0.42]]",
    "const pts = [[-0.6, 0.5, -0.78], [-0.56, 0.32, -0.42], [-0.3, 0.1, -0.08], [0, 0.02, 0.04], [0.3, 0.1, -0.08], [0.56, 0.32, -0.42], [0.6, 0.5, -0.78]]")
rep("r = 0.052 + 0.03 * Math.sin(u * Math.PI); parts.push(new THREE.SphereGeometry(r, HI ? 14 : 10, HI ? 10 : 8)", "r = 0.048 + 0.026 * Math.sin(u * Math.PI); parts.push(new THREE.SphereGeometry(r, HI ? 14 : 10, HI ? 10 : 8)")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
