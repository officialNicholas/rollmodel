# quick build: v252's output + the v253 module (the full chain is ui193_patch.py)
import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/tools'); import v253_icons
s = open(S + '/base252.html').read()
assert s.count('<p class="ver">Version 252</p>') == 1; s = s.replace('<p class="ver">Version 252</p>', '<p class="ver">Version 253</p>')
s = v253_icons.apply(s)
open('/home/claude/paint-the-canvas.html', 'w').write(s); print('q253 ok', len(s))
