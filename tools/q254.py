# quick build: v253's output + the v254 modules (the full chain is ui194_patch.py)
import sys, importlib
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/tools')
MODS = ['v254_dodge', 'v254_spin', 'v254_show']
s = open(S + '/base253.html').read()
assert s.count('<p class="ver">Version 253</p>') == 1; s = s.replace('<p class="ver">Version 253</p>', '<p class="ver">Version 254</p>')
for m in MODS:
    try: mod = importlib.import_module(m)
    except ModuleNotFoundError: print('skip', m); continue
    s = mod.apply(s); print(m, 'ok')
out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/paint-the-canvas.html'
open(out, 'w').write(s); print('q254 ok', len(s), out)
