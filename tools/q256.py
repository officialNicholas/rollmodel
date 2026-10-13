# quick build: v255's output + the v256 modules (the full chain is ui196_patch.py)
import sys, importlib
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, S + '/tools')
MODS = [m for m in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['v256_play', 'v256_colors', 'v256_zone', 'v256_load', 'v256_sdhud'])]
s = open(S + '/base255.html').read()
assert s.count('<p class="ver">Version 255</p>') == 1; s = s.replace('<p class="ver">Version 255</p>', '<p class="ver">Version 256</p>')
for m in MODS:
    try: mod = importlib.import_module(m)
    except ModuleNotFoundError: print('skip', m); continue
    s = mod.apply(s); print(m, 'ok')
out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/paint-the-canvas.html'
open(out, 'w').write(s); print('q256 ok', len(s), out)
