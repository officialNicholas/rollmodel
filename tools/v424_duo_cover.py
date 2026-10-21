"""v424: iPhone Duo, round two.

- The lobby's framing glides when the screen changes shape: the shot was moved to its new spot at once (opening the phone, a fold
  coming or going), the character jumping across and shrinking. The offset that places the character on screen now eases towards
  its new value (the camera already did).
- The cover screen (the side column, html.scol / scolL):
  - The Back buttons (Locker and Paint Shop, Strokes, Friends, Settings, Choose Event, the vote for a canvas) sit in the column under
    the camera, as Apple's own apps put theirs; the dab counter and the turn button move down one step to make room.
  - The close buttons (the dab store, its X now the side menu's chunky slate key everywhere, the side menu, Info on a stroke, the time trial board, the account sheets, online, the party
    picker, the inbox) sit there too.
  - The lobby: Play a little smaller, the rank bar a little smaller, and the Locker, Commissions and Strokes plates spaced so each
    rank tag clears the next plate.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v424) the cover screen: Back and close buttons in the side column under the camera (fixed, so their cards' entrance can't carry
   them: the cards keep still there), the dab counter and turn button a step lower; the lobby's Play and rank bar a little smaller,
   the left plates spaced */
html:is(.scol,.scolL) :is(#stBack,#lkBack,#frX,#evBack,#setBack,#worldBack){position:fixed!important;z-index:30;top:var(--sctop)!important;bottom:auto!important;margin:0!important;transform:none}
html.scol :is(#stBack,#lkBack,#frX,#evBack,#setBack,#worldBack){left:auto!important;right:calc((var(--scw) - 56px) / 2)!important}
html.scolL :is(#stBack,#lkBack,#frX,#evBack,#setBack,#worldBack){right:auto!important;left:calc((var(--scw) - 56px) / 2)!important}
html:is(.scol,.scolL) :is(#dsX,#smClose,#stPopX,#ttX,#acX,#onX,#pkX,#ibX){position:fixed!important;z-index:30;top:calc(var(--sctop) + 4px)!important;bottom:auto!important;margin:0!important}
html.scol :is(#dsX,#smClose,#stPopX,#ttX,#acX,#onX,#pkX,#ibX){left:auto!important;right:calc((var(--scw) - 48px) / 2)!important}
html.scolL :is(#dsX,#smClose,#stPopX,#ttX,#acX,#onX,#pkX,#ibX){right:auto!important;left:calc((var(--scw) - 48px) / 2)!important}
/* (a card that lifts in carries its close button with it, so on the cover screen those cards fade in instead) */
/* the dab store's close button (and, on the cover screen, every close button in the column) is the side menu's: a chunky slate key, a bold white X */
#dsX,html:is(.scol,.scolL) :is(#stPopX,#ttX,#acX,#onX,#pkX,#ibX){display:grid;place-items:center;width:46px;height:44px;padding:0;border:0;border-radius:9px;color:#fff;background:linear-gradient(180deg,#4A4561 0%,#353049 60%,#2A2539 100%);box-shadow:0 0 0 2.5px #171320,inset 0 2px 0 rgba(255,255,255,.2),inset 0 -3px 0 rgba(0,0,0,.25),0 4px 0 #171320;transform:skewX(-5deg);opacity:1}
#dsX svg,html:is(.scol,.scolL) :is(#stPopX,#ttX,#acX,#onX,#pkX,#ibX) svg{width:22px;height:22px;color:#fff;stroke-width:3.4;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.45))}
#dsX:active{transform:skewX(-5deg) translateY(2px)}
html:is(.scol,.scolL) :is(#dsX,#stPopX,#ttX,#acX,#onX,#pkX,#ibX){translate:0}
html:is(.scol,.scolL) .card:has(> :is(#dsX,#stPopX,#ttX,#acX,#onX,#pkX,#ibX)){animation-name:fadein!important;transform:none}
html:is(.scol,.scolL) :is(#mStrokes,#mLocker).sgp .sgbadge{top:calc(var(--sctop) + 70px)}
html.scol #mLocker.sgp .sgrot,html.scol #mLocker.sgp.sgnoted .sgrot{top:calc(var(--sctop) + 136px - var(--gt))}
html.scol #mStrokes.sgp .sgrot{top:calc(var(--sctop) + 136px - var(--gt));bottom:auto}
html:is(.scol,.scolL) .mhome.lobby #homePlay{scale:.84}
html:is(.scol,.scolL) .mhome.lobby #pbar{scale:.86}
html:is(.scol,.scolL) .mhome.lobby .lcol.left{gap:20px}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    # the framing offset eases to its new value (snapped while the menu isn't showing, so coming back to it doesn't slide)
    s = rep(s, "const hero = { yaw: 0, mx: 0, mz: 0 }, heroOff = { x: 0, y: 0 },",
               "const hero = { yaw: 0, mx: 0, mz: 0 }, heroOff = { x: 0, y: 0 }, heroOS = { x: 0, y: 0, on: false } /* (v424: heroOff eased) */,")
    s = rep(s, "  if (heroK > 0.003 || outK > 0.003) { const vw = viewW, vh = viewH; camera.setViewOffset(vw, vh, heroOff.x * heroK + outroOffX * outK, heroOff.y * heroK + outroOffY * outK, vw, vh); }",
               "  if (heroK < 0.05 || !heroOS.on) { heroOS.x = heroOff.x; heroOS.y = heroOff.y; heroOS.on = heroK >= 0.05; } else { const e = 1 - Math.exp(-rdt * 4.5); heroOS.x += (heroOff.x - heroOS.x) * e; heroOS.y += (heroOff.y - heroOS.y) * e; }\n"
               "  if (heroK > 0.003 || outK > 0.003) { const vw = viewW, vh = viewH; camera.setViewOffset(vw, vh, heroOS.x * heroK + outroOffX * outK, heroOS.y * heroK + outroOffY * outK, vw, vh); }")
    return s
