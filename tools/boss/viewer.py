"""The boss viewer (test builds only): applied over a built test page by build_viewer.py, never by q260.py. It adds bossView() (the
Sunken Keep's stage preview with the boss over the pool, cycling through every move) and its tick in the frame loop."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)


def apply(s):
    js = open(os.path.join(HERE, 'viewer.js')).read()
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, js.rstrip('\n') + '\n' + a)
    # each frame, after the game has placed its camera and before it draws
    a = "  visuals(dt, rdt); flushTrail();"
    s = rep(s, a, "  visuals(dt, rdt); bvTick(rdt); flushTrail();")
    return s
