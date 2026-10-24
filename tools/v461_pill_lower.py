"""v461: upright, the steering bar sits closer to your thumb.

- The user: "Put this bar a little lower so it's closer to the finger". Held upright the pill showed 46 px above where your thumb
  went down; it now shows 20 px above it. Sideways (the round stick) nothing changes.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "(anchorY - r.top - (port ? 46 : 0)).toFixed(1)", "(anchorY - r.top - (port ? 20 : 0)).toFixed(1)")
