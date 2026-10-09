#!/usr/bin/env python3
"""Wide strokes (the roller, a giant) taper in toward the blob too, over a longer run. On top of ui33_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui33_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("// newest most), and each lets out a notch as the next is laid ahead of it. A roller or a giant lays its full width straight away\nconst TAPER_N = 9, TAPER_TIP = 0.3; let trailGen = 0;\nconst taperF = (a, k) => 1 - (1 - TAPER_TIP) * k * Math.pow(Math.max(0, 1 - a / TAPER_N), 2);",
    "// newest most), and each lets out a notch as the next is laid ahead of it. A roller or a giant tapers the same way over a longer run\nconst TAPER_N = 9, TAPER_NMAX = 22, TAPER_TIP = 0.3; let trailGen = 0;\nconst taperF = (a, k, n) => 1 - (1 - TAPER_TIP) * k * Math.pow(Math.max(0, 1 - a / (n || TAPER_N)), 2);")
rep("L: [x, yC, z], C: [x, yC, z], R: [x, yC, z], o: -1, o2: -1, f: -1, k: (wmul || 1) > 1.5 ? 0 : 1 };",
    "L: [x, yC, z], C: [x, yC, z], R: [x, yC, z], o: -1, o2: -1, f: -1, k: 1, n: TAPER_N * Math.min(2.4, Math.max(1, wmul || 1)) };")
rep("  Hs.push(h); if (Hs.length > TAPER_N + 1) Hs.shift();", "  Hs.push(h); if (Hs.length > TAPER_NMAX + 1) Hs.shift();")
rep("const q = Hs[Hs.length - 1 - a], f = taperF(a, q.k);", "const q = Hs[Hs.length - 1 - a], f = taperF(a, q.k, q.n);")
rep('<p class="ver">Version 103</p>', '<p class="ver">Version 104</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
