"""v431: skill lines say what they do: Jackpot (a win pays 1.5x the dabs), Paint Boost (more paint capacity), Deep Pockets (two power-ups at a time)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "desc: 'Win, and the dabs pay out big.'", "desc: 'Winning pays 1.5x the dabs.'")
    s = rep(s, "desc: 'Your paint goes further.'", "desc: 'Increases your paint capacity.'")
    s = rep(s, "desc: 'Carry more, use it when you like.'", "desc: 'Hold two power-ups at a time.'")
    return s
