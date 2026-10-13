#!/usr/bin/env python3
"""Quick build of the v257 intro on its own: reads game/index.html, applies tools/v257_intro.py, writes the build.
Usage: q257_intro.py [out.html] [--test]   (default out: game/_intro_test.html; --test adds the probe hook window.__T)"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location('v257_intro', os.path.join(HERE, 'v257_intro.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
args = [a for a in sys.argv[1:] if not a.startswith('--')]
out = args[0] if args else os.path.join(ROOT, 'game', '_intro_test.html')
s = open(os.path.join(ROOT, 'game', 'index.html')).read()
s = mod.apply(s)
if '--test' in sys.argv:
    a = '\nrequestAnimationFrame(frame);\n};'
    assert s.count(a) == 1, s.count(a)
    s = s.replace(a, '\nwindow.__T = { ev: s => eval(s) };\nrequestAnimationFrame(frame);\n};')
open(out, 'w').write(s); print('wrote', out, len(s))
