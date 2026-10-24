"""v459: the Time trial strip on the canvas picker, before you've run this week: "No best yet" in place of "No run here this week".

- The user, of the cut-off "NO RUN HERE THIS ...": "What is this trying to say? Say something shorter". It meant you have no Time trial
  score on this canvas yet this week. The title is now "No best yet"; the lines under it stay ("Set one on Blank Canvas", the week's clock).
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, ": 'No run here this week';", ": 'No best yet';")
