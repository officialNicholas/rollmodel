"""v454: no black ink stripe behind My Locker and Paint Shop.

- The user: "Let's remove that black stripe to make the buttons easier to see". Held upright, the Locker page's two tabs sat on a
  black brush stroke running the width of the screen; it's gone there, the tabs on the page's own background. (The Strokes page keeps
  its stripe.)"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v454) the Locker's tabs without the ink stripe behind them */
#mLocker.sgp .sgtabs::before{display:none}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    return s
