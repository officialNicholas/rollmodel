"""v418: iPhone Duo's side column.

Closed, iPhone Duo puts its status bar and front camera in a column down the right-hand edge of the outer screen (84 points in the
simulator; the game reads whatever the phone reports). Apple's guidance for that screen: content stays to the left of the column, a
full-bleed background may run under it, and the buttons an app would put along the top go to the top of the column instead (and bottom
ones to its bottom), under the camera, within thumb reach.

- The game spots the column from the safe area: one side inset of 30 points or more with none on the other side (a phone held sideways
  has the same inset on both sides, so nothing changes there). It marks the page `scol` (column on the right) or `scolL` (on the left)
  and keeps the column's width in `--scw`, checking again on every resize and fold.
- Pop-ups keep clear of the column (the dab store's close button sat under the camera).
- The lobby's bell and menu buttons, the match's sound button, and the Locker's, Paint Shop's and Strokes page's dab counter and turn
  button move into the column under the camera.
- The Paint Shop on the cover screen: no filter chips (All, Spooky SZN, Skins...), the shop shows everything, and the stage and tabs
  above it are smaller so the list gets more of the screen.
- Opening iPhone Duo: on the way from closed to flat the hinge passes through partly folded for about a second, and the lobby moved you
  into the right-hand half (its partly folded layout) and back. A fold now counts only once it has held for 1.2 seconds; a fold going
  away still counts at once.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v418) iPhone Duo's side column (status bar and camera down one edge): pop-ups keep clear of it; the lobby's and the match's top
   buttons sit in it, one above the other, under the camera */
html.scol{--scw:84px;--sctop:max(92px,calc(env(safe-area-inset-top,0px) + 92px))}
html.scolL{--scw:84px;--sctop:max(92px,calc(env(safe-area-inset-top,0px) + 92px))}
html.scol .modal{padding-right:max(16px,env(safe-area-inset-right,0px))}
html.scolL .modal{padding-left:max(16px,env(safe-area-inset-left,0px))}
html.scol .mhome.lobby .ltools,html.scolL .mhome.lobby .ltools{position:fixed;z-index:5;top:var(--sctop);margin:0;width:var(--scw);flex-direction:column;justify-content:flex-start;gap:12px}
html.scol .mhome.lobby .ltools{right:0}
html.scolL .mhome.lobby .ltools{left:0}
html.scol .mhome.lobby .ltools .tape.exhib,html.scolL .mhome.lobby .ltools .tape.exhib{display:none}
html.scol .corner,html.scolL .corner{top:var(--sctop)!important;width:var(--scw);text-align:center}
html.scol .corner{right:0!important}
html.scolL .corner{left:0;right:auto!important}
/* (the top bar's roll-in moves to its parts: a moving bar would carry the buttons in the column with it) */
html:is(.scol,.scolL) .mhome.lobby .ltop{animation:none}
html:is(.scol,.scolL) .mhome.lobby .ltop>*{animation:rollin-t .55s var(--eo) both}
html:is(.scol,.scolL) .menu.leaving .mhome.lobby .ltop>*{animation:rollout-t .35s var(--ei) both}
/* the Locker's, the Paint Shop's and the Strokes page's dab counter (its + rides on it) and the turn button: in the column too */
html.scol :is(#mStrokes,#mLocker).sgp .sgbadge{top:var(--sctop);right:calc((var(--scw) - 50px) / 2)}
html.scolL :is(#mStrokes,#mLocker).sgp .sgbadge{top:var(--sctop);left:calc((var(--scw) - 50px) / 2);right:auto}
html.scol :is(#mStrokes,#mLocker).sgp .sgrot{right:calc(var(--scw) / 2 - 21px - var(--gr))}
html.scol #mLocker.sgp .sgrot,html.scol #mLocker.sgp.sgnoted .sgrot{top:calc(var(--sctop) + 66px - var(--gt));bottom:auto}
/* the locker and Paint Shop on the cover screen: no filter chips, a shorter stage and slimmer tabs, so the list gets the room */
html:is(.scol,.scolL) #mLocker.sgp .lkchips{display:none}
html:is(.scol,.scolL) #mLocker.sgp .sgshow{flex:0 0 auto;height:clamp(150px,30vh,210px);min-height:0}
html:is(.scol,.scolL) #mLocker.sgp .sgtabs{margin-top:6px}
html:is(.scol,.scolL) #mLocker.sgp .sgtab .sgti{display:none}
html:is(.scol,.scolL) #mLocker.sgp .sgtab .sgtb{padding:5px 8px 6px}
html:is(.scol,.scolL) #mLocker.sgp .sgpanel{flex:1 1 auto;max-height:none;margin-top:16px}
"""

JS = r"""
// (v418) iPhone Duo's side column: one side inset of 30 points or more with none opposite (a phone held sideways has both). Marks the
// page scol (right) or scolL (left) and keeps the column's width in --scw.
(function () {
  const d = document.createElement('div'); d.style.cssText = 'position:fixed;left:0;top:0;width:0;height:0;visibility:hidden;pointer-events:none;padding:0 env(safe-area-inset-right,0px) 0 env(safe-area-inset-left,0px)';
  let last = '';
  function mark() {
    if (!d.isConnected) document.body.appendChild(d);
    const c = getComputedStyle(d), r = parseFloat(c.paddingRight) || 0, l = parseFloat(c.paddingLeft) || 0;
    const side = r >= 30 && l < 8 ? 'scol' : l >= 30 && r < 8 ? 'scolL' : '', w = Math.round(Math.max(r, l)), k = side + w;
    if (k === last) return; last = k; const h = document.documentElement;
    h.classList.toggle('scol', side === 'scol'); h.classList.toggle('scolL', side === 'scolL');
    if (side) h.style.setProperty('--scw', w + 'px'); else h.style.removeProperty('--scw');
    // (no filter chips there: the shop shows everything)
    try { if (side && typeof LKR !== 'undefined' && LKR.filt && LKR.filt !== 'all') { LKR.filt = 'all'; const m = document.getElementById('mLocker'); if (m && m.offsetParent && typeof lkPaneRender === 'function') lkPaneRender(); } } catch (e) {}
  }
  window.__scolMark = mark;
  addEventListener('resize', () => requestAnimationFrame(mark)); addEventListener('orientationchange', () => setTimeout(mark, 120));
  addEventListener('nativefold', () => setTimeout(mark, 30));
  if (document.body) mark(); else addEventListener('DOMContentLoaded', mark);
})();
"""

def fold(s):
    s = rep(s, "let foldKey = '';\nfunction foldApply() {\n  const f = foldRead(), r = document.documentElement, M = 10, key = f ? f.axis + ':' + Math.round(f.a) + ':' + Math.round(f.b) : '';\n  if (key === foldKey) return; foldKey = key;\n",
               "let foldKey = '', foldWant = '', foldSince = 0, foldT = 0;\nfunction foldApply() {\n  const f = foldRead(), r = document.documentElement, M = 10, key = f ? f.axis + ':' + Math.round(f.a) + ':' + Math.round(f.b) : '';\n  if (key === foldKey) { foldWant = ''; return; }\n"
               "  // (v418) a new fold counts once it has held 2.5 s: opening the phone passes through partly folded for a moment on its way to flat\n"
               "  if (key) { const now = performance.now(); if (key !== foldWant) { foldWant = key; foldSince = now; } if (now - foldSince < 2500) { clearTimeout(foldT); foldT = setTimeout(foldApply, 2550 - (now - foldSince)); return; } }\n"
               "  foldWant = ''; foldKey = key;\n")
    return s

def apply(s):
    s = fold(s)
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    i = s.rfind("</script>"); s = s[:i] + JS + s[i:]
    return s
