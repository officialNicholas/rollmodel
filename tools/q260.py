# quick build: v259 (game/index.html) + the first-launch intro (v257_intro.py) + its v260 glue -> argv[1]; --test adds window.__T
import sys, os, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
src = os.path.join(os.path.dirname(HERE), 'game', 'index.html')
s = open(src).read()
assert s.count('<p class="ver">Version 259</p>') == 1; s = s.replace('<p class="ver">Version 259</p>', '<p class="ver">Version 260</p>')
for m in ['v257_intro', 'v260_intro_glue']:
    s = importlib.import_module(m).apply(s); print(m, 'ok')
if '--test' in sys.argv:
    a = '\nrequestAnimationFrame(frame);\n};'; assert s.count(a) == 1; s = s.replace(a, '\nwindow.__T = { ev: s => eval(s) };' + a)
out = sys.argv[1]; open(out, 'w').write(s); print('q260 ok', len(s), out)
