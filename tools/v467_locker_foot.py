"""v467: upright Locker, the item's line, price and "you need more dabs" note fit under the character again.

- The user (a screenshot of the Zombie skin: the description over the character's head, the price under it and the note cut off at
  the left edge): "Fix spacing". Since the preview rests small (v455) the three stacked lines covered most of it, and the turn-around
  button rose up under the dabs counter.
- Upright, at rest the preview is a little taller (190 to 260 px, about 30% of the screen). When there's a note, the price button and
  the note share one row (button left, note beside it, wrapping to two short lines), so the footer is two rows, not three. The
  turn-around button sits just above that footer at the right, clear of the counter. Holding the preview still grows it as before.
"""

CSS = """
/* (v467) upright Locker: a compact footer (description, then the price and its note side by side) and the turn-around button above it */
@media (max-aspect-ratio:1/1){
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp:not(.lkbig) .sgshow{height:clamp(190px,30vh,260px)}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp.sgnoted .sgfoot{display:grid;grid-template-columns:auto minmax(0,1fr);column-gap:10px;row-gap:5px;align-items:center;justify-items:start;box-sizing:border-box;padding:0 12px 6px;bottom:0}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp.sgnoted .sgfoot .sgline{grid-column:1/-1;grid-row:1;justify-self:center}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp.sgnoted .sgfoot .sgact{grid-column:1;grid-row:2}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp.sgnoted .sgfoot .sgnote{grid-column:2;grid-row:2;order:0;justify-self:start;max-width:100%;margin:0;text-align:left;text-wrap:balance}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp .sgrot,html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp.sgnoted .sgrot{top:auto;bottom:74px}
}
"""

def apply(s):
    i = s.rfind("</style>"); return s[:i] + CSS + s[i:]
