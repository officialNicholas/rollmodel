"""v431: the Jackpot skill's line says what it does: a win pays 1.5x the dabs."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "desc: 'Win, and the dabs pay out big.'", "desc: 'Winning pays 1.5x the dabs.'")
