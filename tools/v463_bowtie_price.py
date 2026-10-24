"""v463: the Bow tie costs 100 dabs (was 185). The user: "Make this 100"."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "bowtie: 185,", "bowtie: 100,")
