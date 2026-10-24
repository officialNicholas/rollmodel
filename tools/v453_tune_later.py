"""v453: a few seconds of free rolling after Move before the steering settings card.

- The user: "Let the player move for a few seconds in the tutorial before bringing the steering settings". After the Move lesson
  is done you roll on your own for 4 s, then the Your steering card (Turning slider and Invert) comes up."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "{ id: 'freetune', max: 99, enter() { tutHide(); lsnDue('tune'); }, tick() { return true; } },",
               "{ id: 'freetune', max: 99, enter() { tutHide(); tut.tuneWait = 4; }, tick(dt) { if ((tut.tuneWait -= dt) > 0) return false; lsnDue('tune'); return true; } }, /* (v453: 4 s of rolling first) */")
    return s
