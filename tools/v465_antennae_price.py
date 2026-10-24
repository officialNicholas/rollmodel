"""v465: the Antennae cost 50 dabs (was 195). The user: "This 100", then "Actually that one 50"."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "antennae: 195", "antennae: 50")
