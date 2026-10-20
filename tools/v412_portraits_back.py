"""v412: the skins in the Paint Shop showed blank cards (the user: "Skins aren't showing anything. Fix that"). Since v391 the party
code had its own function called ptRender (it redraws the lobby's party spots), the same name as the portraits' renderer, and the
later one won: every portrait the game made since was of nothing, so the skin cards (and the results' and Showdown's faces) waited
on a blank one. The party's is partyRender now, and the portraits draw the character again."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    assert s.count('function ptRender() {') == 2 and 'partyRender' not in s
    cut = s.index('function ptRender() {', s.index('function ptRender() {') + 1)  # (the second: the party's)
    first_party_call = s.index('ptRender()', s.index('ptPose(j.s); ptRender();') + 30)
    k = min(cut, first_party_call)
    return s[:k] + s[k:].replace('ptRender(', 'partyRender(')
