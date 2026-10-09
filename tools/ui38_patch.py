#!/usr/bin/env python3
"""Item prices set against what matches pay: four wins for the cheapest, thirty for the dearest. Builds on ui36 (the ink-board locker of ui37 is set aside; the paper locker stays)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui36_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# a win pays about 43 dabs (8 base, a third of your coverage, 30 for the win); a loss about 13. So: the flower after four wins, the halo after thirty
rep("const PRICE = w => w.season ? 150 : w.slot === 'head' ? 120 : 80;",
    "const PRICES = { flower: 170, bowtie: 220, lashes: 260, glasses: 320, patch: 390, fangs: 470, tiara: 560, tophat: 680, pirate: 820, hat: 1000, halo: 1300 };\nconst PRICE = w => PRICES[w.id] || (w.season ? 1000 : w.slot === 'head' ? 600 : 300);")
rep('<p class="ver">Version 106</p>', '<p class="ver">Version 108</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
