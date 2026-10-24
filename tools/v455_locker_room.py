"""v455: upright, the Locker's preview rests small so My Locker and the Paint Shop get the room; touch it and it grows.

- The user: "in portrait, shrink the preview to give more room to my locker and the store. And when you interact with it, it
  temporarily gets bigger". Held upright the preview (your character on the plinth) now rests at about a quarter of the screen
  (150 to 230 px tall) and the list below takes the rest. Press on the preview (to spin it, tap it, or the turn-around button) and it
  swells to about half the screen while you're on it, then eases back 1.6 s after you let go. Trying things on from the list doesn't
  resize anything, so the list never jumps under your finger; the 3D view follows the box as it changes (it already refits to it).
  Sideways, and on the Duo's layouts, nothing changes.
- The canvas picker's dots (the user: "Place the pagination closer up to the name of the stage"): upright they sat about 40 px under
  the name plate (the strip of canvases keeps 30 px of room under itself); they now sit 10 px or so under it, and Shuffle keeps its
  own row under them."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v455) upright Locker: the preview small at rest, big while you handle it; the list gets the room */
@media (max-aspect-ratio:1/1){
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp .sgshow{flex:0 0 auto;height:clamp(150px,27vh,230px);min-height:0;transition:height .4s cubic-bezier(.3,1.15,.5,1)}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp.lkbig .sgshow{height:clamp(240px,50vh,440px)}
  html:not(.fh):not(.fv):not(.scol):not(.scolL) #mLocker.sgp .sgpanel{flex:1 1 auto;max-height:none;margin-top:18px}
  html:not(.fh):not(.fv) .menu:not(.tutoring) .mworld #gDots{margin-top:-26px}
}
"""

JS = r"""
// (v455) upright, the Locker's preview grows while you handle it and settles back a moment after
{ let lkBigT = 0; const pg = $('mLocker');
  const grow = () => { clearTimeout(lkBigT); pg.classList.add('lkbig'); };
  const settle = d => { clearTimeout(lkBigT); lkBigT = setTimeout(() => pg.classList.remove('lkbig'), d); };
  $('lkStage').addEventListener('pointerdown', grow); $('lkStage').addEventListener('pointerup', () => settle(1600)); $('lkStage').addEventListener('pointercancel', () => settle(1600));
  $('lkRot').addEventListener('click', () => { grow(); settle(2200); });
  new MutationObserver(() => { if (pg.hidden) { clearTimeout(lkBigT); pg.classList.remove('lkbig'); } }).observe(pg, { attributes: true, attributeFilter: ['hidden'] }); }
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    a = "function openLocker(tab, id)"; s = rep(s, a, JS.strip() + "\n" + a)
    return s
