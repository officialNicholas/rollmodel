# quick build: v257's output + the v258 modules (the full chain is ui197_patch.py)
import sys, importlib
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/tools')
MODS = [m for m in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['v258_audio'])]
s = open(S + '/build257.html').read()
assert s.count('<p class="ver">Version 257</p>') == 1; s = s.replace('<p class="ver">Version 257</p>', '<p class="ver">Version 258</p>')
for m in MODS:
    mod = importlib.import_module(m); s = mod.apply(s); print(m, 'ok')
out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/paint-the-canvas.html'
open(out, 'w').write(s); print('q258 ok', len(s), out)
