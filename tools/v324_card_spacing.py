"""v324: the Strokes cards' spacing, cleaned up.

The yellow ring on the card you're looking at ran into the card beside it, the hook of the card below and the "Unlock everything"
link, and came close to the panel's edge. Now:
- the ring sits a little closer round the card, matches the tabs' ring (3px yellow, 2.5px ink), and the card grows a touch about its
  middle (3%, was 6% down from the hook), so it no longer spills downward;
- the gaps between cards are even both ways (18px), with the panel's side padding to match, so the ring has the same ~8px of clear
  space from a neighbour, the card below, and the panel's edge;
- the "Unlock everything" link sits a little further below the cards.
Sideways and on narrow phones, the same."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the ring: closer round the card and the tabs' weight; the card a touch bigger about its middle
    s = rep(s, "#mStrokes.sgp .sgcard.sel{transform:scale(1.06);z-index:1}", "#mStrokes.sgp .sgcard.sel{transform:scale(1.03);transform-origin:50% 55%;z-index:1}")
    s = rep(s, "#mStrokes.sgp .sgcard.sel::after{content:\"\";position:absolute;left:-4px;right:-4px;top:7px;bottom:-4px;border-radius:14px;box-shadow:0 0 0 4px var(--sel),0 0 0 6px var(--ink0);pointer-events:none}",
        "#mStrokes.sgp .sgcard.sel::after{content:\"\";position:absolute;left:-3px;right:-3px;top:7px;bottom:-3px;border-radius:13px;box-shadow:0 0 0 3px var(--sel),0 0 0 5.5px var(--ink0);pointer-events:none}")
    # even gaps, and side padding to match (the ring keeps ~8px clear all round)
    s = rep(s, "#mStrokes.sgp .sggrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px 12px;padding:2px 2px 4px}", "#mStrokes.sgp .sggrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;padding:2px 2px 4px}")
    s = rep(s, "overscroll-behavior:contain;padding:22px 14px 18px;", "overscroll-behavior:contain;padding:22px 16px 18px;")
    s = rep(s, "#mStrokes.sgp .stucode{position:relative;display:flex;flex-direction:column;align-items:center;gap:8px;margin:12px 0 2px}", "#mStrokes.sgp .stucode{position:relative;display:flex;flex-direction:column;align-items:center;gap:8px;margin:16px 0 2px}")
    # sideways
    s = rep(s, "  #mStrokes.sgp .sgscroll{padding:21px 14px 18px}\n  #mStrokes.sgp .sggrid{gap:12px 14px}\n", "  #mStrokes.sgp .sgscroll{padding:21px 16px 18px}\n  #mStrokes.sgp .sggrid{gap:18px}\n")
    # narrow phones
    s = rep(s, "#mStrokes.sgp .sggrid{gap:12px 9px}}", "#mStrokes.sgp .sggrid{gap:16px 14px}}")
    return s
