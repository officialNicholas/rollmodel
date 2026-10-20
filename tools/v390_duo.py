"""v390: two iPhone Duo fixes from the user's screenshots.

- Partly folded, held wide (the fold down the middle): the lesson's callouts in a match ("HOLD, PULL DOWN, then let go to fling!") sat
  in the middle of the screen, across the fold and under the pause card (which comes up in the right-hand screen). They now sit in the
  middle of the left-hand screen, as wide as it allows, and the hand showing the gesture under them goes with them.
- Opened flat (and any other landscape screen too tall for the phone's sideways layout: a small tablet): the match used the upright
  phone's controls, the pound button in the middle at the foot of the screen, under your character. A landscape screen at least 1.15
  times as wide as it is tall now gets the sideways controls whatever its height: the pound button in the bottom right corner, the
  transform beside it, the orb's button beside that, and Ol' Bloop's corner on the left, clear of them. (Under that ratio, nearly square,
  the upright layout stays.)
- Partly folded, held wide, in a match: the pound button stays in its bottom right corner (an older rule slid it right by half the
  fold, off the screen).
- The vote for a canvas, partly folded and held wide: the paintings run across both screens, and none sits on the fold: the one you're
  on is in the middle of the left-hand screen, the paintings are a screen's width apart, so the next one sits in the middle of the
  right-hand screen; the arrows at the far edges. Shuffle under the left-hand screen, Play (and the note over it) under the right.
- The vote for a canvas opened flat (any landscape screen taller than a phone's): the paintings and their dots sit in the middle of the
  space between the title and Play, not up under the title.
- Near-square screens (iPhone Duo open or folded, an iPad): the match's pause and sound buttons sit further in from the corners, clear of
  the screen's rounded corners.
- Near-square screens, upright, on the Strokes page and the Locker: the black ink band behind the tabs fades out at its ends instead of
  stopping in a straight edge where the screen is wider than the band.
- Partly folded, held wide: the dab store's packs two to a row (four squeezed out of the card, which sits in the right-hand screen).
- An upright screen 560 wide or more (iPhone Duo opened flat and held upright, an iPad): the Paint Shop's, the Locker's and the Strokes
  page's cards four to a row, a little smaller, so more fit."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

TALLWIDE = "@media (min-height:521px) and (min-aspect-ratio:23/20)"

VOTE_CSS = r"""
/* (v390) the vote for a canvas on a landscape screen taller than a phone's: the paintings and their dots in the middle of the space
   between the title and the footer, as upright */
@media (min-aspect-ratio:1/1) and (min-height:521px){
  .menu:not(.tutoring) .mworld{grid-template-rows:auto auto minmax(6px,1fr) auto auto minmax(6px,1fr) auto}
  .menu:not(.tutoring) .mworld .whead{grid-row:1}
  .menu:not(.tutoring) .mworld #modes{grid-row:2}
  .menu:not(.tutoring) .mworld .gallery{grid-row:4;height:auto;padding-top:30px;padding-bottom:30px}
  .menu:not(.tutoring) .mworld #gDots{grid-row:5}
  .menu:not(.tutoring) .mworld .sgrid{grid-row:3/7;max-height:100%;overflow:auto}
  .menu:not(.tutoring) .mworld .wfoot{grid-row:7}
}
/* (v390) partly folded, held wide: the paintings across both screens (the one you're on in the middle of the left-hand one, the next in
   the middle of the right-hand one: the script spaces them a screen apart), the arrows at the far edges; shuffle under the left-hand
   screen, Play and its note under the right */
html.fv.fold .mworld{grid-template-columns:minmax(0,var(--fa)) var(--fg) minmax(0,1fr);grid-template-rows:auto auto minmax(6px,1fr) auto auto minmax(6px,1fr) auto}
html.fv.fold .mworld .gallery{grid-column:1/-1;grid-row:4;height:auto;padding-top:30px;padding-bottom:30px}
html.fv.fold .mworld .world{max-width:calc(var(--fa) - 120px)}
html.fv.fold .mworld #gDots{grid-column:1;grid-row:5}
html.fv.fold .mworld .wfoot{grid-column:1/-1;grid-row:7;align-self:end;width:100%;margin:0;grid-template-columns:minmax(0,var(--fa)) var(--fg) minmax(0,1fr);column-gap:0}
html.fv.fold .mworld .wfoot>*{grid-column:3;justify-self:center;width:min(calc(100% - 40px),420px);box-sizing:border-box}
html.fv.fold .mworld .wfoot>.wgo{grid-column:1/-1;width:100%;display:grid;grid-template-columns:minmax(0,var(--fa)) var(--fg) minmax(0,1fr);gap:0}
html.fv.fold .mworld .wgo #shuffleBtn{grid-column:1;justify-self:center}
html.fv.fold .mworld .wgo #startBtn{grid-column:3;justify-self:center;width:min(calc(100% - 40px),420px)}
html.fv.fold .mworld .gnav{top:var(--gmid,54%)}
html.fv.fold .mworld .gnav.next{right:max(10px,calc(env(safe-area-inset-right,0px) + 4px))}
"""

def vote(s):
    s = rep(s, "/* the count under the title on a line of its own */", VOTE_CSS + "/* the count under the title on a line of its own */")
    # where the painting you're on sits: the gallery's middle, or (partly folded, held wide) the middle of the left-hand screen, the
    # paintings then a screen's width apart so the next one is in the middle of the right-hand one
    s = rep(s, "const gallery = $('stagePick'), worldBtns = [...gallery.querySelectorAll('.world')];\n",
               "const gallery = $('stagePick'), worldBtns = [...gallery.querySelectorAll('.world')];\n"
               "// (v390) where the painting you're on sits across the gallery: its middle; or, iPhone Duo partly folded and held wide, the middle of\n"
               "// the left-hand screen (none on the fold)\n"
               "const galFold = () => FOLD.on && FOLD.axis === 'v' && document.documentElement.classList.contains('fv');\n"
               "function galMid() { const cw = gallery.clientWidth; if (!galFold()) return cw / 2; return Math.max(60, FOLD.a / 2 - gallery.getBoundingClientRect().left); }\n")
    s = rep(s, "    const pl = Math.max(12, Math.round(cw / 2 - fl - fw / 2)), pr = Math.max(12, Math.round(cw / 2 + fl + fw / 2 - ww)); if (pl + ',' + pr !== gpW)",
               "    const A = galMid(), pl = Math.max(12, Math.round(A - fl - fw / 2)), pr = Math.max(12, Math.round(cw - A + fl + fw / 2 - ww));\n"
               "    { const g = galFold() ? Math.max(16, Math.round((FOLD.b + innerWidth) / 2 - FOLD.a / 2 - ww)) + 'px' : ''; if (gallery.style.columnGap !== g) gallery.style.columnGap = g;\n"
               "      const sl = galFold() ? Math.max(0, Math.round(2 * A - cw)) + 'px' : '', sr = galFold() ? Math.max(0, Math.round(cw - 2 * A)) + 'px' : ''; // (and the snap's centre there too)\n"
               "      if (gallery.style.scrollPaddingLeft !== sl) gallery.style.scrollPaddingLeft = sl; if (gallery.style.scrollPaddingRight !== sr) gallery.style.scrollPaddingRight = sr; } // (v390: a screen apart)\n"
               "    if (pl + ',' + pr !== gpW)")
    s = rep(s, "    if (gallery.scrollWidth > cw + 4) gallery.scrollLeft = on.offsetLeft + fl + fw / 2 - cw / 2; };",
               "    if (gallery.scrollWidth > cw + 4) gallery.scrollLeft = on.offsetLeft + fl + fw / 2 - A; };")
    s = rep(s, "  if (window.ResizeObserver) new ResizeObserver(gpSoon).observe(gallery); addEventListener('resize', gpSoon); window.__gpFit = gpSoon; }",
               "  if (window.ResizeObserver) new ResizeObserver(gpSoon).observe(gallery); addEventListener('resize', gpSoon); addEventListener('nativefold', () => setTimeout(gpSoon, 30)); window.__gpFit = gpSoon; }")
    s = rep(s, "const mid = gallery.scrollLeft + gallery.clientWidth / 2;", "const mid = gallery.scrollLeft + galMid();")
    s = rep(s, "fr.offsetLeft + fr.offsetWidth / 2 : b.offsetWidth / 2) - gallery.clientWidth / 2, behavior", "fr.offsetLeft + fr.offsetWidth / 2 : b.offsetWidth / 2) - galMid(), behavior")
    return s

def apply(s):
    # ---- the fold down the middle: the lesson's callouts and their gesture hand in the left-hand screen
    s = rep(s, "html.fv .hud .score,html.fv .slamBtn,html.fv .vsx .vstitle{translate:calc(var(--fb) / 2) 0}",
               "html.fv .hud .score,html.fv .slamBtn,html.fv .vsx .vstitle{translate:calc(var(--fb) / 2) 0}\n"
               "/* (v390) the lesson's callouts in a match, and the hand showing the gesture, in the left-hand screen (the pause card has the right) */\n"
               "html.fv .tut[data-pos=\"play\"]{left:calc(var(--fa) / 2);max-width:calc(var(--fa) - 28px)}\n"
               "html.fv .tutgest{left:calc(var(--fa) / 2)}")
    # ---- a landscape screen too tall for the phone's sideways layout: the sideways controls all the same (the buttons in the bottom
    # right corner, a little bigger for the bigger screen), Ol' Bloop on the left
    s = rep(s, "/* cards: how to play and pause sit over a dimmed game */",
               "/* (v390) a wide screen taller than a phone's (iPhone Duo open, a small tablet): the pound button in the bottom right corner, as sideways */\n"
               + TALLWIDE + "{.slamBtn{position:absolute;margin:0;right:max(30px,calc(env(safe-area-inset-right) + 22px));bottom:max(28px,calc(env(safe-area-inset-bottom) + 18px))}html.fv .slamBtn{translate:none}}\n"
               "/* cards: how to play and pause sit over a dimmed game */")
    s = rep(s, "@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn{left:auto;right:max(156px,calc(env(safe-area-inset-right) + 148px));",
               TALLWIDE + "{.itemBtn{left:auto;right:max(150px,calc(env(safe-area-inset-right) + 142px));bottom:max(36px,calc(env(safe-area-inset-bottom) + 26px))}} /* (v390) */\n"
               "@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn{left:auto;right:max(156px,calc(env(safe-area-inset-right) + 148px));")
    s = rep(s, "@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn.ib2,.itemBtn.orbBtn{left:auto;",
               TALLWIDE + "{.itemBtn.ib2,.itemBtn.orbBtn{left:auto;right:calc(max(150px,calc(env(safe-area-inset-right) + 142px)) + 94px);bottom:calc(max(36px,calc(env(safe-area-inset-bottom) + 26px)) + 8px)}.itemBtn.orbBtn.up{right:calc(max(150px,calc(env(safe-area-inset-right) + 142px)) + 168px)}} /* (v390) */\n"
               "@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn.ib2,.itemBtn.orbBtn{left:auto;")
    # ---- held wide and partly folded: the pound button in its corner (not slid right by half the fold, off the screen)
    s = rep(s, "html.fv .tutgest{left:calc(var(--fa) / 2)}", "html.fv .tutgest{left:calc(var(--fa) / 2)}\n@media (min-aspect-ratio:23/20),(max-height:520px) and (min-aspect-ratio:1/1){html.fv.fold .hud .slamBtn{translate:none}} /* (v390: in its corner there) */")
    s = vote(s)
    # ---- near-square screens: the match's corner buttons clear of the rounded corners; the tabs' ink band fades at its ends
    s = rep(s, "/* cards: how to play and pause sit over a dimmed game */",
               "/* (v390) a near-square screen (iPhone Duo, an iPad): the match's pause and sound buttons further in from its rounded corners */\n"
               "html.roomy .hud{padding-top:max(22px,calc(env(safe-area-inset-top) + 10px));padding-left:max(24px,calc(env(safe-area-inset-left) + 12px));padding-right:max(24px,calc(env(safe-area-inset-right) + 12px))}\n"
               "html.roomy .corner{top:max(22px,calc(env(safe-area-inset-top) + 10px));right:max(24px,calc(env(safe-area-inset-right) + 12px))}\n"
               "/* (v390) and the ink band behind the Strokes page's and the Locker's tabs fades out at its ends (it can end short of the screen's edge there) */\n"
               "html.roomy :is(#mStrokes,#mLocker).sgp .sgtabs::before{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 14%,#000 86%,transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 14%,#000 86%,transparent 100%)}\n"
               "/* cards: how to play and pause sit over a dimmed game */")
    # ---- a wide upright screen: the cards four to a row
    s = rep(s, "#mLocker.sgp .sggrid{gap:18px 14px}",
               "#mLocker.sgp .sggrid{gap:18px 14px}\n"
               "/* (v390) an upright screen 560 wide or more (iPhone Duo open, an iPad): the cards four to a row, a little smaller */\n"
               "@media (max-aspect-ratio:1/1) and (min-width:560px){:is(#mStrokes,#mLocker).sgp .sggrid,#mLocker.sgp .sggrid{grid-template-columns:repeat(4,minmax(0,1fr));gap:14px 12px}}")
    # ---- partly folded, held wide: the dab store's card is in one screen, so its packs two to a row (not four, by the whole width)
    s = rep(s, "@media (min-width:620px){.dspacks{grid-template-columns:repeat(4,minmax(0,1fr))}}",
               "@media (min-width:620px){.dspacks{grid-template-columns:repeat(4,minmax(0,1fr))}}\nhtml.fv.fold .dspacks{grid-template-columns:repeat(2,minmax(0,1fr))} /* (v390: the card is in one screen there) */")
    s = rep(s, "const coachSide = () => viewW > viewH && viewH <= 520 ? 'l' : 'r';",
               "const coachSide = () => viewW > viewH && (viewH <= 520 || viewW >= viewH * 1.15) ? 'l' : 'r'; /* (v390: any wide screen, its buttons on the right) */")
    return s
