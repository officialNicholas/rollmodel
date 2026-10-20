"""v401: the Giant lasts a second longer (the user: "Let giant last for one second longer"): 6 seconds instead of 5, whether it comes from
the orb or the Giant stroke. The countdown on its ring, How to play and the Giant's card on the Strokes page say 6 too. (The game server's
own Giant, for online pick-ups when they're turned on, lasts 6 seconds as well.)"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const GIANT_T = 5, GIANT_K = 3,", "const GIANT_T = 6, GIANT_K = 3,") # (v401: 5 before)
    s = rep(s, "go giant for 5 seconds", "go giant for 6 seconds")
    s = rep(s, "'Grow three times your size for 5 seconds'", "'Grow three times your size for 6 seconds'")
    return s
