#!/usr/bin/env python3
"""The gear lines up with the sound button. On top of ui42_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui42_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
css = '''
/* the gear sits at the top of the bar, at the same height as the sound button beside it, whatever the nametag's height or the notch */
.mhome.lobby .ltools{align-self:flex-start;margin-top:calc(max(12px,env(safe-area-inset-top)) - max(8px,env(safe-area-inset-top)))}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 112</p>', '<p class="ver">Version 113</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
