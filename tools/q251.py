# quick build: v250's output + the v251 modules (the full chain is ui191_patch.py)
import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/tools'); import importlib, v251_tags, v251_play
s = open(S + '/base250.html').read()
assert s.count('<p class="ver">Version 250</p>') == 1; s = s.replace('<p class="ver">Version 250</p>', '<p class="ver">Version 251</p>')
s = v251_tags.apply(s); s = v251_play.apply(s)
open('/home/claude/paint-the-canvas.html', 'w').write(s); print('q251 ok', len(s))
