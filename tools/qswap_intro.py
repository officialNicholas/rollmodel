#!/usr/bin/env python3
"""v257 intro, test build on the shipped page: game/index.html already carries the intro (built in on the main branch), so this swaps
its three blocks (the stylesheet, the music engine flm, var FL) for the files in tools/ as they are now, finding the shipped blocks as
they were in the commit the page came from. --test adds the probe hook window.__T (and FL.handoff, as q260.py does).
Usage: qswap_intro.py [out.html] [--test] [--rev=<commit the page's blocks came from; default: the last commit that changed the page>]"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = [a for a in sys.argv[1:] if not a.startswith('--')]
out = args[0] if args else os.path.join(ROOT, 'game', '_intro_test.html')
git = lambda *a: subprocess.run(['git', *a], capture_output=True, text=True, cwd=ROOT, check=True).stdout
rev = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--rev=')), None) or git('log', '-1', '--format=%H', '--', 'game/index.html').strip()
s = open(os.path.join(ROOT, 'game', 'index.html')).read()
for f in ['v257_intro.css', 'v257_intro_au.js', 'v257_intro.js']:
    old, new = git('show', f'{rev}:tools/{f}'), open(os.path.join(HERE, f)).read()
    c = s.count(old); assert c == 1, (f, 'shipped block found', c, 'times'); s = s.replace(old, new)
if '--test' in sys.argv:
    a = '\nrequestAnimationFrame(frame);\n};'; assert s.count(a) == 1; s = s.replace(a, '\nwindow.__T = { ev: s => eval(s) };' + a)
    a = '  api.after = after;\n'; assert s.count(a) == 1; s = s.replace(a, a + '  api.handoff = handoff; // (test build only: the probes jump straight to the end)\n')
open(out, 'w').write(s); print('wrote', out, len(s), 'blocks from', rev[:8])
