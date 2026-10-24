"""v453: a few seconds of free rolling after Move before the steering settings card.

- The user: "Let the player move for a few seconds in the tutorial before bringing the steering settings". After the Move lesson
  is done you roll on your own for 4 s, then the Your steering card (Turning slider and Invert) comes up.
- The lobby's Play button a little smaller (the user: "Make the play button on the bottom slightly smaller"): held upright it was
  the full width of the bottom row (347 px on a 393 px phone) and 84 px tall; now 86% of that row at most 310 px, 76 px tall, and
  its word 38 px (was 42), centred."""

CSS = """
/* (v453) the lobby's Play, upright: a little smaller, centred */
@media (max-aspect-ratio:1/1){#homePlay.playbtn{justify-self:center;width:min(86%,310px);min-width:0;min-height:76px}#homePlay.playbtn .pbl{font-size:38px}}
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "{ id: 'freetune', max: 99, enter() { tutHide(); lsnDue('tune'); }, tick() { return true; } },",
               "{ id: 'freetune', max: 99, enter() { tutHide(); tut.tuneWait = 4; }, tick(dt) { if ((tut.tuneWait -= dt) > 0) return false; lsnDue('tune'); return true; } }, /* (v453: 4 s of rolling first) */")
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    return s
