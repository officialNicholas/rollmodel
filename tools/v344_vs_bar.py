"""v344: no "Most paint wins" on the Versus CPU card.

- On Choose Event, the dark strip over the Versus CPU card said "Most paint wins" on its right. The strip stays, empty, so the card keeps
  the same shape as the others; their words (Live online, Last one standing, Weekly leaderboard, Coming soon) stay."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<span class="evbar"><i>Most paint wins</i></span>', '<span class="evbar"></span>')
    return s
