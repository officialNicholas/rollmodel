#!/usr/bin/env python3
"""The tally's names and numbers each keep their own column (left, middle, right), so in a duel, with the middle one hidden, the rival's score sits at the right edge instead of sliding into the middle. On top of ui99_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui99_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep(".tyname.r,.tynum.r{text-align:right;justify-self:end}", ".tyname.r,.tynum.r{text-align:right;justify-self:end}\n.tyname.l,.tynum.l{grid-column:1}.tyname.m,.tynum.m{grid-column:2}.tyname.r,.tynum.r{grid-column:3} /* (fixed columns: a hidden middle does not pull the right one in) */")
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui100 ok', n0, '->', len(s))
