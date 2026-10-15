"""Build the boss viewer page: the test build (tools/q260.py with --test) plus the viewer (tools/boss/viewer.py).
usage: BASE=<base page> VER=259:311 python3 tools/boss/build_viewer.py game/_boss_view.html
Then serve game/ and open _boss_view.html; in the console (or through __T.ev) run bossView() (or bossView({ cam: null }) for the
game's own camera). The page needs game/boss-pack.txt beside it."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import viewer

out = sys.argv[1]
subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), 'q260.py'), out, '--test'], check=True, env=os.environ)
s = open(out).read(); s = viewer.apply(s); open(out, 'w').write(s)
print('boss viewer ok', len(s), out)
