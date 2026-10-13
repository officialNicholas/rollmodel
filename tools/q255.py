# quick build: v254's output + the v255 modules (the full chain is ui195_patch.py)
import sys, importlib
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/tools')
MODS = ['v255_rematch']
s = open(S + '/base254.html').read()
assert s.count('<p class="ver">Version 254</p>') == 1; s = s.replace('<p class="ver">Version 254</p>', '<p class="ver">Version 255</p>')
for m in MODS: s = importlib.import_module(m).apply(s); print(m, 'ok')
out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/paint-the-canvas.html'
open(out, 'w').write(s); print('q255 ok', len(s), out)
