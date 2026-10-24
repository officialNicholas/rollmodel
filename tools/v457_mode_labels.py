"""v457: the event cards' drop-down choices (1 v 1, 3-way, Free-for-all, 2 v 2) are just their names.

- The user: "We don't need those subtexts under 2v2, free for all, etc". The small lines under each choice ("You and one rival",
  "Four of you, one left", "You and a teammate"...) are hidden; the strip is a little shorter and the names a touch bigger.
"""

CSS = """
/* (v457) the drop-down choices without their small lines */
.evdrop small{display:none}
.evdrop{height:66px}
.evdrop b{font-size:22px}
"""

def apply(s):
    i = s.rfind("</style>"); return s[:i] + CSS + s[i:]
