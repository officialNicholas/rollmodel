"""v407: the locker's buttons sat on the tabs (the user: "Fix the spacing on these UI buttons"). Upright, Equipped / Take off (and
Equip, Buy) are at the foot of the character's window, and the ink band behind My Locker / Paint Shop reaches about 23 px up past
the tabs, so the buttons sat on it, touching the tabs. Upright only (the Strokes page has the same window and band): the foot and the
turn button go up 22 px, a clear gap over the band. Landscape is as it was."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v407) upright: the window's buttons clear of the ink band behind the tabs */
@media (max-aspect-ratio:1/1){
  :is(#mStrokes,#mLocker).sgp .sgfoot{bottom:26px}
  :is(#mStrokes,#mLocker).sgp .sgrot{bottom:106px}
  :is(#mStrokes,#mLocker).sgp.sgnoted .sgrot{bottom:122px}
}
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    return s
