"""v373: the Locker's eyes have room for what's chosen, and the lock on a locked style shows.

- The chosen eye colour is drawn bigger (x1.18) with a white and a black ring, and the chosen eye style lifts with its own ring; with
  10px between the rows and the buttons, those rings touched: the colour's ring ran into the style above it (3px over) and almost into
  the next colour (half a pixel), and the chosen style's ring nearly touched the next style.
- The five styles and the five colours now stand in the same five columns (each colour under a style), 14px apart, with 22px between
  the two rows, so a chosen colour's ring keeps about 9px from the style over it and 14px from the colours beside it. A little more room
  under the colours before the next heading. On a screen under 360 points wide, the smaller buttons stand 13px apart.
- The lock on a style you don't have yet (the Zombie eyes) shows again: the rule that sizes the eye pictures caught the lock's picture
  too, so a big cream lock spilled out of its dark badge onto the paper. It keeps its own size now, in a slightly bigger dark badge with
  a paper-coloured ring."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""/* (v373) the Locker's eyes: the styles and the colours in the same five columns, the rows apart, so the rings of the chosen ones (the
   colour grows x1.18 with a white and a black ring; the style lifts with its ring) never touch a neighbour */
#mLocker.sgp .lkeyes{gap:22px;padding:4px 2px 10px}
#mLocker.sgp .lkstyles,#mLocker.sgp .lkirises{display:grid;grid-template-columns:repeat(auto-fill,44px);column-gap:14px;row-gap:22px;justify-items:center;align-items:center}
@media (max-width:359px){#mLocker.sgp .lkstyles,#mLocker.sgp .lkirises{grid-template-columns:repeat(auto-fill,38px);column-gap:13px}}
/* (v373) the lock on a style you don't have yet: the rule that sizes the eye pictures (36px) caught the lock's picture too, so a big cream
   lock spilled out of its little dark badge onto the paper and only the badge's corner showed. The lock keeps its own size, in a dark
   badge a little bigger than before, ringed in the paper's colour so it stands off the tile's corner */
#mLocker.sgp .lkstyles .eyes .lk{right:-7px;top:-7px;width:20px;height:20px;border-radius:6px;background:var(--black);color:var(--cream);box-shadow:0 0 0 2px var(--paper)}
#mLocker.sgp .lkstyles .eyes .lk svg{width:12px;height:12px;filter:none;opacity:1}
"""

def apply(s):
    s = rep(s, "html.fh .tutgo .tgcard .tava{display:none}\n</style>", "html.fh .tutgo .tgcard .tava{display:none}\n" + CSS + "</style>")
    return s
