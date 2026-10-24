"""v464: the Lashes cost 100 dabs (was 220). The user, of the eye with lashes in the Paint Shop: "This 100"."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "lashes: 220,", "lashes: 100,")
