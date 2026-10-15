"""v290: Ol' Bloop's "Try this one!" on the Showdown card goes for good the moment you open that card (tap it and its two options,
Free-for-all and 2v2, come up). It sat over the 2v2 button. As before, it also goes once you leave the page."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # (opened: the suggestion's done, so the same frame's other branch takes it off and records it)
    s = rep(s, "if (state === 'menu' && menuPage === 'events' && sd) { if (!sd.querySelector('.evbloop'))",
               "if (state === 'menu' && menuPage === 'events' && sd && !sd.classList.contains('open')) { if (!sd.querySelector('.evbloop'))")
    s = rep(s, "\n@media (prefers-reduced-motion:reduce){.evbloop{animation:none}}\n",
               "\n@media (prefers-reduced-motion:reduce){.evbloop{animation:none}}\n.evcard.open .evbloop{display:none}\n")
    return s
