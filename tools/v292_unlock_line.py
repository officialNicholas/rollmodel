"""v292: Ol' Bloop's "Let's learn some more" card, when Strokes open up, says it in one short line: "Strokes, Time trial and Showdown
are unlocked. Let's start with Strokes." (was three sentences)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "'You’ve unlocked Strokes: your special move, a skill and the transform you start with. Time trial and Showdown are open now too. Strokes first: come see.'",
                  "'Strokes, Time trial and Showdown are unlocked. Let’s start with Strokes.'")
