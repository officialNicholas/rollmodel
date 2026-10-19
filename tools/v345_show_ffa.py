"""v345: the Showdown card says "Free for all".

- On Choose Event, the Showdown card's line under its name said "Three hearts each". It says "Free for all" now. The start-of-match
  banner in a Showdown still says three hearts each."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<span class="evtx"><b>Showdown</b><small>Three hearts each</small></span>', '<span class="evtx"><b>Showdown</b><small>Free for all</small></span>')
    return s
