"""v285: hiding in a basin as the Roller. With the Roller on, the body drawn is the old jelly roller (its own face), and that one was
never lowered into the basin: it sat up in it, above the paint, with the basin's pair of eyes on top. Now in a basin it's always the
axolotl, sunk out of sight like any other time, so only the eyes show; climbing out with the Roller still on, it's the roller again."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "on = L.roll < 0.5 && !tur && !V.balled", "on = (L.roll < 0.5 || D.st === 'hide') && !tur && !V.balled")
    return s
