"""v400: the results' buttons say what they do (the user: "The buttons should say as follows. 'Continue (new canvas)', rematch, and
menu"). Against CPUs: the big button is Continue, with New canvas under it (it opens the canvas vote, as before); Same canvas is now
Rematch (the same canvas and rivals again); Menu stays. Online, where the big button is a rematch vote with the same players on a new
canvas, it keeps its words."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<button class="btn play two" id="endBtn" type="button"><span>Rematch</span><small>New canvas</small></button>',
               '<button class="btn play two" id="endBtn" type="button"><span>Continue</span><small>New canvas</small></button>')
    s = rep(s, '<button class="btn" id="replayBtn" type="button">Same canvas</button>', '<button class="btn" id="replayBtn" type="button">Rematch</button>')
    # back from an online match, and after a lesson's gate: the offline words again
    s = rep(s, "const b = $('endBtn'); b.disabled = false; b.innerHTML = '<span>Rematch</span><small>New canvas</small>';",
               "const b = $('endBtn'); b.disabled = false; b.innerHTML = '<span>Continue</span><small>New canvas</small>';")
    s = rep(s, ": '<span>Rematch</span><small>New canvas</small>';\n  $('replayBtn').closest('.row').hidden = due;",
               ": '<span>Continue</span><small>New canvas</small>';\n  $('replayBtn').closest('.row').hidden = due;")
    return s
