"""v406: the canvas vote on a landscape phone (the user: "The name is cut, fix").

The row for the paintings there was shorter than the painting you're on and its name plate together, so the plate (and the bottom of
the frame) went under the controls. Three things, on landscape phones only (a phone held upright, and the iPhone Duo folded, are as
they were):
- the controls take one row, not two: the difficulty under its label, beside Shuffle and Play; the paintings get the height back.
- the note about the vote ("Your rivals vote too...") goes under the page's title, where there's room for it.
- the script sizes the painting you're on to the row it has, so the painting and its plate always fit, whatever the phone (the frame's
  moulding gets thinner on a small painting). The frame is now exactly the width of its button (it used to come out 31 px wider)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v406) the canvas vote on a landscape phone: the controls in one row, the note under the title, and the painting you're on sized
   by the script (--ww, --fb) so it and its name plate fit the row the paintings have */
.wnote{display:none}
@media (max-height:520px) and (min-aspect-ratio:1/1){
  html:not(.fold) .mworld .whead{grid-template-rows:auto auto;row-gap:5px}
  html:not(.fold) .mworld .whead .back{grid-row:1/3}
  html:not(.fold) .mworld .whead h2{grid-column:2;grid-row:1;align-self:end;text-align:left}
  html:not(.fold) .mworld .wnote{display:block;grid-column:2;grid-row:2;align-self:start;max-width:440px;margin:0;font:700 12.5px/1.25 var(--font-ui);color:#B8B0C8;text-align:left;text-wrap:balance}
  html:not(.fold) .mworld .wnote b{color:var(--cream)}
  html:not(.fold) .menu.tutoring .mworld .wnote,html:not(.fold) .mworld #soloNote{display:none}
  html:not(.fold) .mworld .wfoot{grid-template-rows:auto auto;row-gap:7px}
  html:not(.fold) .mworld #wDiffHd{grid-column:1;grid-row:1}
  html:not(.fold) .mworld #stages{grid-column:1;grid-row:2}
  html:not(.fold) .mworld #ttStrip{grid-column:1;grid-row:1/3}
  html:not(.fold) .mworld .wfoot>.wgo{grid-column:2;grid-row:1/3}
  html.difflock:not(.fold) .mworld .wfoot>.wgo,html:not(.fold) .menu.tutoring .mworld .wfoot>.wgo{grid-column:1/-1;justify-self:center;width:min(100%,400px)}
  html:not(.fold) .mworld .world{width:var(--ww,min(26vw,36vh*1.45,250px));grid-template-columns:minmax(0,1fr)}
  html:not(.fold) .mworld .frame{min-width:0;aspect-ratio:auto;border-width:var(--fb,34px)}
  html:not(.fold) .mworld .frame img.art{height:auto;aspect-ratio:320/220}
}
"""

JS = """/* (v406) a landscape phone: the painting you're on is sized to the row the paintings have, so it and its name plate fit (the plate was
   cut off under the controls), with a thinner moulding on a small one; and the note about the vote is shown under the title (.wnote) */
const GP_LAND = matchMedia('(max-height:520px) and (min-aspect-ratio:1/1)');
function gpSize(on) { const mw = $('mWorld');
  if (!GP_LAND.matches || document.documentElement.classList.contains('fold')) { if (mw.style.getPropertyValue('--ww')) { mw.style.removeProperty('--ww'); mw.style.removeProperty('--fb'); } return; }
  const gs = getComputedStyle(gallery), pq = on.querySelector('.plaque'), gap = parseFloat(getComputedStyle(on).rowGap) || 0;
  const fh = gallery.clientHeight - parseFloat(gs.paddingTop) - parseFloat(gs.paddingBottom) - 2 - (pq ? pq.offsetHeight : 0) - gap; // (the frame's height that leaves the plate its room)
  const b = Math.max(14, Math.min(34, Math.round(fh * 0.185))), ww = Math.max(120, Math.min(Math.round(Math.min(innerWidth * 0.26 + 31, 281)), Math.floor(2 * b + (fh - 2 * b) * 320 / 220)));
  mw.style.setProperty('--fb', b + 'px'); mw.style.setProperty('--ww', ww + 'px'); }
{ const sn = $('soloNote'), wn = $('worldNote'), sync = () => { wn.innerHTML = sn.innerHTML; wn.hidden = sn.hidden || sn.classList.contains('ttoff'); };
  new MutationObserver(sync).observe(sn, { attributes: true, attributeFilter: ['hidden', 'class'], childList: true, characterData: true, subtree: true }); sync(); }
"""

def apply(s):
    s = rep(s, '<h2 id="worldTitle">Canvases</h2></div>', '<h2 id="worldTitle">Canvases</h2><p class="wnote" id="worldNote" hidden></p></div>')
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n</style>",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS + "</style>")
    s = rep(s, "{ let gpW = 0, gpQ = 0; const gpFit = () => {", JS + "{ let gpW = 0, gpQ = 0; const gpFit = () => {")
    s = rep(s, "if (!on || !gallery.clientWidth || !on.offsetWidth) return;\n    const mw = $('mWorld'), gr = gallery.getBoundingClientRect()",
               "if (!on || !gallery.clientWidth || !on.offsetWidth) return;\n    gpSize(on); // (v406)\n    const mw = $('mWorld'), gr = gallery.getBoundingClientRect()")
    return s
