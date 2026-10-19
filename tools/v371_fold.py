"""v371: iPhone Duo partly folded: boxes and words keep to one side of the fold.

- While iPhone Duo is partly open, its fold runs down the middle of the screen (held wide: a left and a right screen) or across it (held
  upright: a top and a bottom one). The game hears where from the app (iOS 27.1's reserved regions, sent as window.__NATIVE.fold and a
  'nativefold' event) or from the browser's viewport segments where it has them, and marks the page html.fold with .fv (down) or .fh
  (across), with --fa and --fb where the fold's strip starts and ends (10 points of room either side) and --fg its width.
- Down the screen (the "left or right screens"):
  - pop-ups come up in the right-hand screen, where iPhone Duo puts the view on top (Apple's overlay arrangement puts it in the trailing
    part): Info on a stroke, Commissions, Stats, the account sheets, Terms, How to play, the pause card (its rows stacked), Ol' Bloop's
    cards, the ad's wait, a nudge to allow notifications, a new item's card, the loading screen;
  - pages in two parts split at the fold: Settings (sound, music and turning on the left; visuals and the links on the right), the
    Strokes page and the Locker (the cards on the left, the stroke or your character on the right), Friends (you on the left, the list on
    the right), Choose Event (two cards a side), the vote for a canvas (the pictures on the left, difficulty and Play on the right), and
    the results (the painting on the left, the score on the right);
  - in a match, what sat in the middle goes to the right-hand screen: the score and clock, the banners ("Paint it red!"), the pound
    button, the countdown, the missile warning, the knocked-out badge, tips, the versus card's line, the tally; the winner's name stops
    short of the fold;
  - the lobby's rank bar sits right of the fold instead of on it; the toasts sit in one screen; the intro's title goes right of it and
    its two send-off lines either side (its cards already sit top left).
- Across the screen: pop-ups, the tally and the loading screen come up in the lower screen (scrolling if they're taller); the lobby's
  rank bar, the results' painting and the vote's pictures stay above the fold, difficulty and Play below; Choose Event puts two cards
  above and two below; the Strokes page and the Locker end their picture at the fold and start the tabs after it; Friends puts you above
  and the list below.
- Opened flat (the fold not active), closed, or any other phone: nothing changes."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v371) iPhone Duo partly folded (html.fold): boxes and words keep to one side of the fold. Down the screen (.fv), pop-ups and the
   match's middle go to the right-hand screen and two-part pages split at the fold; across it (.fh), pop-ups go to the lower screen.
   --fa and --fb: where the fold's strip starts and ends, with room either side; --fg: its width */
html.fv :is(.modal:not(#setModal):not(#friendsModal),.tutgo,.adw,.adst){padding-left:calc(var(--fb) + 12px);padding-right:max(12px,env(safe-area-inset-right))}
html.fv :is(.modal:not(#setModal):not(#friendsModal),.tutgo,.adw)>*{max-width:100%}
html.fh :is(.modal:not(#setModal):not(#friendsModal),.tutgo,.adw,.adst){padding-top:calc(var(--fb) + 8px);padding-bottom:max(10px,env(safe-area-inset-bottom))}
html.fh .modal:not(#setModal):not(#friendsModal)>*{max-height:100%}
html.fh .modal .stpop,html.fh .modal .ttcard{overflow-y:auto}
/* the pause card: its narrow layout in a screen's width */
html.fv #pause .card{width:min(100%,420px);grid-template-columns:minmax(0,1fr)}
html.fv #pause .card>:is(.pscore,.pturn){grid-column:1/-1}
/* Settings: the middle gap of its four columns is the fold (set in setFit, which may draw the rows smaller) */
/* the Strokes page and the Locker: the cards up to the fold, the stroke or your character after it */
html.fv :is(#mStrokes,#mLocker).sgp{--panw:var(--fa);--tabw:min(116px,calc((var(--fa) - var(--gx) - var(--bk) - 50px) / 3))}
html.fv :is(#mStrokes,#mLocker).sgp .sgshow{left:var(--fb)}
html.fv :is(#mStrokes,#mLocker).sgp:not(.sgx) .sgpanel{left:var(--gx);width:calc(var(--fa) - var(--gx));transform:none}
html.fv :is(#mStrokes,#mLocker).sgp:not(.sgx) .sgshow{left:var(--fb)}
html.fv :is(#mStrokes,#mLocker).sgp .sttoast{left:calc((100% + var(--fb)) / 2)}
/* Friends: you on the left, the list from the fold on */
html.fv #friendsModal .frpg{grid-template-columns:minmax(0,calc(var(--fa) - var(--gx))) minmax(0,1fr);column-gap:var(--fg)}
/* Choose Event: two cards a side */
html.fv .evgrid{column-gap:var(--fg)}
/* the vote for a canvas: the title and the pictures on the left, difficulty and Play on the right */
html.fv .mworld{grid-template-columns:minmax(0,var(--fa)) var(--fg) minmax(0,1fr);grid-template-rows:auto auto minmax(0,1fr) auto;align-items:center}
html.fv .mworld>.whead{grid-column:1/-1;grid-row:1;grid-template-columns:56px minmax(0,calc(var(--fa) - 80px)) minmax(0,1fr)}
html.fv .mworld #modes{grid-column:1;grid-row:2}
html.fv .mworld .gallery{grid-column:1;grid-row:3;padding-left:max(24px,calc(50% - 150px));padding-right:max(24px,calc(50% - 150px))}
html.fv .mworld .gdots{grid-column:1;grid-row:4}
html.fv .mworld .sgrid{grid-column:1;grid-row:3/5;width:calc(100% - 40px);grid-template-columns:repeat(2,minmax(0,1fr))}
html.fv .mworld .wfoot{grid-column:3;grid-row:2/5;align-self:center;width:min(calc(100% - 40px),420px);margin:0}
html.fv .mworld .gnav.next{right:calc(100% - var(--fa) + 4px)}
html.fv .mworld .gnav{top:calc(50% + 24px)}
/* in a match: what sits in the middle goes to the right-hand screen */
html.fv .hud .score,html.fv .slamBtn,html.fv .vsx .vstitle{translate:calc(var(--fb) / 2) 0}
html.fv .banner{left:var(--fb)}
html.fv .hint{left:calc(var(--fb) + 8px)}
html.fv :is(.pop,.threat,.tutpraise,.tutpips,.evtoast,.sdspec,.mstrokes .sttoast,.frtoast,.kofb,.tydabs){left:calc((100% + var(--fb)) / 2)}
/* the tally after a match: in the right-hand screen (or the lower one) */
html.fv .tally{padding-left:calc(var(--fb) + 16px);padding-right:max(16px,env(safe-area-inset-right))}
html.fh .tally{padding-top:var(--fb)}
html.fh .kofb{top:calc((100% + var(--fb)) / 2)}
/* a new item's card, and the loading screen: in the right-hand screen (or the lower one) */
html.fv :is(.newitem,#boot){padding-left:var(--fb)}
html.fv #boot .bootacct{left:calc((100% + var(--fb)) / 2)}
html.fh :is(.newitem,#boot){padding-top:var(--fb)}
/* the intro: its cards already sit top left on a wide screen (clear of the fold); its title in the right-hand screen, its two lines
   either side of the fold */
html.fv .fltitle{padding-left:var(--fb)}
html.fv .flsend b{font-size:24px;max-width:calc(var(--fa) - 16px)}
html.fh .flsend b:nth-child(1){top:calc(var(--fa) - 112px)}
html.fh .flsend b:nth-child(2){top:calc(var(--fb) + 28px)}
html.fv .count{padding-left:var(--fb)}
/* across the screen (held upright): the Strokes page and the Locker end their picture at the fold and start the tabs after it */
html.fh :is(#mStrokes,#mLocker).sgp .sgshow{flex:0 0 auto;height:calc(var(--fa) - var(--gt))}
html.fh :is(#mStrokes,#mLocker).sgp .sgtabs{margin-top:calc(var(--fg) + 14px)}
html.fh :is(#mStrokes,#mLocker).sgp .sgpanel{flex:1 1 auto;max-height:none}
/* Friends: you above the fold, the list below it */
html.fh #friendsModal .frsheet{flex:0 0 auto;height:calc(100% - var(--fb));margin-top:auto}
/* Choose Event: two cards above the fold, two below */
html.fh .evgrid{grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:minmax(0,calc(var(--fa) - max(14px,env(safe-area-inset-top)) - 76px)) minmax(0,1fr);align-content:stretch;gap:var(--fg) 16px}
html.fh .evgrid>.evcard:nth-child(-n+2){align-self:center}
html.fh .evgrid>.evcard:nth-child(n+3){align-self:start}
/* the vote for a canvas: the title and the pictures above the fold, difficulty and Play below it (out of the page's grid, whose rows would
   otherwise hold them) */
html.fh .menu .mworld .gallery{grid-area:auto;position:absolute;left:0;right:0;top:calc(max(12px,env(safe-area-inset-top)) + 70px);height:calc(var(--fa) - max(12px,env(safe-area-inset-top)) - 70px);padding-top:26px;padding-bottom:0;box-sizing:border-box}
html.fh .mworld .gnav{top:calc((var(--fa) + 70px) / 2 + 16px)}
html.fh .menu .mworld .gdots{grid-area:auto;position:absolute;left:0;right:0;top:calc(var(--fb) + 2px);justify-content:center}
html.fh .menu .mworld .sgrid{grid-area:auto;position:absolute;left:50%;top:calc(max(12px,env(safe-area-inset-top)) + 76px);width:min(calc(100% - 32px),calc((var(--fa) - 110px) * 1.16 + 14px));translate:-50% 0;max-height:none;overflow:visible;padding:0;gap:10px 14px}
/* Ol' Bloop's cards in the lower screen: his picture would sit on the fold, so the card goes alone */
html.fh .tutgo .tgcard .tava{display:none}
"""

JS_CORE = r"""
// (v371) iPhone Duo partly folded: where the fold runs (the app says, as __NATIVE.fold and 'nativefold', or the browser's viewport
// segments), so boxes and words keep to one side of it. html.fold with .fv (down the screen: a left and a right screen) or .fh (across
// it: a top and a bottom one); --fa and --fb where its strip starts and ends, with room either side, --fg its width. Pages placed by
// script (the lobby's rank bar, Settings' rows, the results' painting) read FOLD
const FOLD = { on: false, axis: '', a: 0, b: 0 };
function foldRead() {
  const W = innerWidth, H = innerHeight, n = window.__NATIVE && window.__NATIVE.fold; let f = null;
  // (one measured for another size is from before a turn, a moment old: the app sends the new one with the new layout)
  if (n && (n.axis === 'v' || n.axis === 'h') && +n.b >= +n.a && !(n.w && Math.abs(n.w - W) > 2) && !(n.h && Math.abs(n.h - H) > 2)) f = { axis: n.axis, a: +n.a, b: +n.b };
  else { const sg = (window.viewport && window.viewport.segments) || (window.visualViewport && window.visualViewport.segments);
    if (sg && sg.length === 2) { const p = sg[0], q = sg[1]; if (q.left >= p.right - 1) f = { axis: 'v', a: p.right, b: q.left }; else if (q.top >= p.bottom - 1) f = { axis: 'h', a: p.bottom, b: q.top }; } }
  // (a fold that doesn't leave a screen's worth either side of it isn't one to lay out around)
  if (f) { const L = f.axis === 'v' ? W : H; if (!(f.a > L * 0.25 && f.b < L * 0.75)) f = null; }
  return f;
}
let foldKey = '';
function foldApply() {
  const f = foldRead(), r = document.documentElement, M = 10, key = f ? f.axis + ':' + Math.round(f.a) + ':' + Math.round(f.b) : '';
  if (key === foldKey) return; foldKey = key;
  FOLD.on = !!f; FOLD.axis = f ? f.axis : ''; FOLD.a = f ? Math.max(0, f.a - M) : 0; FOLD.b = f ? f.b + M : 0;
  r.classList.toggle('fold', !!f); r.classList.toggle('fv', !!f && f.axis === 'v'); r.classList.toggle('fh', !!f && f.axis === 'h');
  if (f) { r.style.setProperty('--fa', FOLD.a.toFixed(1) + 'px'); r.style.setProperty('--fb', FOLD.b.toFixed(1) + 'px'); r.style.setProperty('--fg', (FOLD.b - FOLD.a).toFixed(1) + 'px'); }
  // (what's laid out by script goes round again)
  setTimeout(() => { try { dispatchEvent(new Event('resize')); } catch (e) {} }, 0);
}
addEventListener('nativefold', foldApply); addEventListener('resize', foldApply);
try { if (window.viewport && window.viewport.addEventListener) window.viewport.addEventListener('segmentschange', foldApply); } catch (e) {}
try { if (navigator.devicePosture) navigator.devicePosture.addEventListener('change', () => setTimeout(foldApply, 60)); } catch (e) {}
foldApply();"""

def apply(s):
    s = rep(s, "  #setModal #setDone{right:max(16px,calc(env(safe-area-inset-right) + 12px))}\n}\n</style>",
               "  #setModal #setDone{right:max(16px,calc(env(safe-area-inset-right) + 12px))}\n}" + CSS + "</style>")

    a = "{ const mark = () => document.documentElement.classList.toggle('roomy', roomy()); mark(); addEventListener('resize', mark); }"
    s = rep(s, a, a + JS_CORE)

    # Settings: the middle gap of the four columns is the fold (the rows may be drawn smaller, so the gap is set at their scale)
    s = rep(s, "  f.style.transform = ''; f.style.width = ''; r.style.overflowY = '';\n"
               "  const cs = getComputedStyle(r), room = r.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom); let k = 1, h = f.offsetHeight;\n"
               "  for (let i = 0; i < 4 && h * k > room + 0.5; i++) { k = Math.max(0.6, room / h); f.style.width = (100 / k).toFixed(3) + '%'; f.style.transform = 'scale(' + k.toFixed(4) + ')'; h = f.offsetHeight; }",
               "  f.style.transform = ''; f.style.width = ''; r.style.overflowY = '';\n"
               "  const fg = FOLD.on && FOLD.axis === 'v' && getComputedStyle(f).gridTemplateColumns.split(' ').length === 4 ? FOLD.b - FOLD.a : 0; f.style.columnGap = fg ? fg + 'px' : ''; // (v371: iPhone Duo's fold down the middle)\n"
               "  const cs = getComputedStyle(r), room = r.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom); let k = 1, h = f.offsetHeight;\n"
               "  for (let i = 0; i < 4 && h * k > room + 0.5; i++) { k = Math.max(0.6, room / h); f.style.width = (100 / k).toFixed(3) + '%'; f.style.transform = 'scale(' + k.toFixed(4) + ')'; if (fg) f.style.columnGap = (fg / k).toFixed(1) + 'px'; h = f.offsetHeight; }")

    # the lobby's rank bar: to the right of the fold (down the screen), or above it (across)
    s = rep(s, "    if ((r.left + r.right) / 2 - sr.left < viewW / 2) lo = Math.max(lo, r.right - sr.left + 8); else hi = Math.min(hi, r.left - sr.left - 8); }\n",
               "    if ((r.left + r.right) / 2 - sr.left < viewW / 2) lo = Math.max(lo, r.right - sr.left + 8); else hi = Math.min(hi, r.left - sr.left - 8); }\n"
               "  if (FOLD.on && FOLD.axis === 'v') lo = Math.max(lo, FOLD.b - sr.left); // (v371: iPhone Duo partly folded)\n"
               "  if (FOLD.on && FOLD.axis === 'h' && sy > FOLD.a - sr.top - 2 && sy - bh < FOLD.b - sr.top) sy = FOLD.a - sr.top - 2;\n")

    # the results: the painting in the screen the results leave (left of the fold, or above it)
    s = rep(s, "  if (outroSide) { ax0 = 20; ax1 = end.offsetLeft - 20; ay0 = top; ay1 = viewH - 34; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }\n"
               "  else { ax0 = 16; ax1 = viewW - 16; ay0 = top; ay1 = end.offsetTop - 30; outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }\n",
               "  if (outroSide) { ax0 = 20; ax1 = end.offsetLeft - 20; ay0 = top; ay1 = viewH - 34; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }\n"
               "  else { ax0 = 16; ax1 = viewW - 16; ay0 = top; ay1 = end.offsetTop - 30; outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }\n"
               "  if (FOLD.on && FOLD.axis === 'v' && outroSide) ax1 = Math.min(ax1, FOLD.a - 6); // (v371: iPhone Duo partly folded)\n"
               "  if (FOLD.on && FOLD.axis === 'h' && !outroSide) ay1 = Math.min(ay1, FOLD.a - 40); // (its plaque hangs below the frame)\n")
    # the winner's name behind them (drawn for the backdrop): on a wide screen it stops short of the fold, with the place's outline
    s = rep(s, "const widest = Math.max(1, ...lines.map(l => g.measureText(l).width)), maxW = land ? W * 0.56 : W - 28, maxH = land ? H * 0.6 : H * 0.34;",
               "const widest = Math.max(1, ...lines.map(l => g.measureText(l).width)), maxW = land ? (FOLD.on && FOLD.axis === 'v' ? Math.min(W * 0.56, FOLD.a - Math.max(W * 0.045, 24) - 12) : W * 0.56) : W - 28, maxH = land ? H * 0.6 : H * 0.34; // (v371: iPhone Duo's fold)")
    s = rep(s, "g.strokeText(vic.ghost, W * (land ? 0.6 : 1.06),", "g.strokeText(vic.ghost, land && FOLD.on && FOLD.axis === 'v' ? Math.min(W * 0.6, FOLD.a) : W * (land ? 0.6 : 1.06),")
    return s
