"""Build the Conquest preview page (the current game + the cq modules) for the separate preview artifact.
usage: python3 tools/cq/mk_preview.py <out.html> [label]
The page is the release list + CQ below, not a test build. A first visit starts at the menu (the save is seeded with the first-launch
intro and the lessons done), so Choose Event > Season Conquest is two taps away. The assets are game/'s own files, published beside it."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
CQ = ['cq01_conquest_restore']
out = sys.argv[1]; label = sys.argv[2] if len(sys.argv) > 2 else '335 + Conquest'
base = os.environ.get('BASE') or sys.exit('BASE=<the v259 page> (git show 28d9d54:game/index.html)')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'q260.py'), out], check=True, cwd=ROOT,
               env=dict(os.environ, EXTRA=','.join(CQ), BASE=base, VER='259:' + label))
s = open(out).read()
SEED = ("<script>try { if (!localStorage.getItem('paint-world-red.v1')) localStorage.setItem('paint-world-red.v1', JSON.stringify({ introDone: 1, runs: 1, "
        "tut: { ph: 'done', m3: 1, modes: 1, strokes: 1, comms: 1, trySd: 1 } })); } catch (e) {}</script>") # (the preview only: straight to the menu)
a = '<head><meta charset=utf8>'; assert s.count(a) == 1; s = s.replace(a, a + SEED)
a = '<title>Roll Model</title>'; assert s.count(a) == 1; s = s.replace(a, '<title>Roll Model Conquest</title>')
open(out, 'w').write(s); print('preview ok', len(s), out)
