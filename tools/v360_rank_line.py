"""v360: Play online's lock says "Reach rank 2", without ", then open Strokes".

- Tapping the locked Play online card under rank 2 says "Reach rank 2" (it said "Reach rank 2, then open Strokes"). At rank 2
  before Strokes has been opened it still says "Open Strokes in the lobby to unlock it".
- The card's label for screen readers follows: "Play online, locked: reach rank 2" under rank 2."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "'Reach rank ' + ABIL_RANK + ', then open Strokes' : 'Open Strokes in the lobby to unlock it'",
               "'Reach rank ' + ABIL_RANK : 'Open Strokes in the lobby to unlock it'")
    s = rep(s, "b.setAttribute('aria-label', on ? 'Play online: 1v1 against real people' : 'Play online, locked: open Strokes in the lobby to unlock it');",
               "b.setAttribute('aria-label', on ? 'Play online: 1v1 against real people' : lv < ABIL_RANK ? 'Play online, locked: reach rank ' + ABIL_RANK : 'Play online, locked: open Strokes in the lobby to unlock it');")
    return s
