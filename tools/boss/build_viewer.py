"""Build the boss viewer page: the test build (tools/q260.py with --test), the Sunken Keep stage and the boss if q260 doesn't
apply them yet (both stay out of releases until the owner is happy with them), then the viewer (tools/boss/viewer.py).
usage: BASE=<base page> VER=259:311 python3 tools/boss/build_viewer.py game/_boss_view.html
Then serve game/ and open _boss_view.html; in the console (or through __T.ev) run bossView() (or bossView({ cam: null }) for the
game's own camera). The page needs game/boss-pack.txt beside it."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(1, TOOLS)
import viewer

out = sys.argv[1]
subprocess.run([sys.executable, os.path.join(TOOLS, 'q260.py'), out, '--test'], check=True, env=os.environ)
s = open(out).read()
if 'function conqPreview()' not in s:
    import v309_conquest_stage; s = v309_conquest_stage.apply(s); print('v309_conquest_stage ok')
if 'var BOSS = (() => {' not in s:
    import v311_conquest_boss; s = v311_conquest_boss.apply(s); print('v311_conquest_boss ok')
s = viewer.apply(s); open(out, 'w').write(s)
print('boss viewer ok', len(s), out)
