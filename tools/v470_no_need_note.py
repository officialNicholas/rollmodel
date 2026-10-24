"""v470: no "You need N more dabs. Matches pay in dabs" note. The user: "We don't need this disclaimer".

- The Locker's Paint Shop and the Strokes page no longer show it under the price of something you can't afford yet; the greyed-out
  price button already says so.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "doLab = w.name + ', ' + p + ' dabs'; note = 'You need ' + (p - n) + ' more dabs. Matches pay in dabs'; }", "doLab = w.name + ', ' + p + ' dabs'; }")
    s = rep(s, "(lack > 0 ? 'You need ' + lack + ' more dabs. Matches pay in dabs' : '')", "''")
    return s
