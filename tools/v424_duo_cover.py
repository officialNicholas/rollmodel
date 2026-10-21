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
/* the dock: a box at the page root (no card's transform or blur can hold or clip it) that the open page's Back or close button is
   moved into by script, under the camera; the match's sound button and the lobby's bell and menu sit below whatever is docked */
#scolDock{display:none}
html:is(.scol,.scolL) #scolDock{position:fixed;z-index:60;top:var(--sctop);width:var(--scw);display:flex;flex-direction:column;align-items:center;gap:12px;pointer-events:none}
html.scol #scolDock{right:0} html.scolL #scolDock{left:0}
#scolDock>*{position:static!important;margin:0!important;pointer-events:auto;flex:none}
#scolDock>.pback,#scolDock>.sgback{transform:none}
html:is(.scol,.scolL){--scdk:0px}
html:is(.scol,.scolL) .corner{top:calc(var(--sctop) + var(--scdk))!important}
html:is(.scol,.scolL) .corner .ib{margin:0 auto}
html:is(.scol,.scolL) #hud:not(.off)~.corner{right:0!important}
html:is(.scol,.scolL) .mhome.lobby .ltools{top:calc(var(--sctop) + var(--scdk))}
#dsX{display:grid;place-items:center;width:46px;height:44px;padding:0;border:0;border-radius:9px;color:#fff;background:linear-gradient(180deg,#4A4561 0%,#353049 60%,#2A2539 100%);box-shadow:0 0 0 2.5px #171320,inset 0 2px 0 rgba(255,255,255,.2),inset 0 -3px 0 rgba(0,0,0,.25),0 4px 0 #171320;transform:skewX(-5deg);opacity:1}
#dsX svg{width:22px;height:22px;color:#fff;stroke-width:3.4;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.45))}
#dsX:active{transform:skewX(-5deg) translateY(2px)}
#scolDock>#dsX{transform:skewX(-5deg)!important}
/* the vote for a canvas: its title across the top in one line (Back is in the dock) */
html:is(.scol,.scolL) .mworld .whead{grid-template-columns:1fr;padding:0 max(14px,env(safe-area-inset-left))}
html:is(.scol,.scolL) .mworld .whead h2{text-align:left;white-space:nowrap;font-size:clamp(22px,6vw,30px)}
/* the match's pound button centred in the screen left of the column (the hud's padding had centred it in the narrower width) */
html.scol .hud .slamBtn{position:relative;left:calc(var(--scw) / -2 + 46px)}
html:is(.scol,.scolL) :is(#mStrokes,#mLocker).sgp .sgbadge{top:calc(var(--sctop) + 70px)}
html.scol #mLocker.sgp .sgrot,html.scol #mLocker.sgp.sgnoted .sgrot{top:calc(var(--sctop) + 136px - var(--gt))}
html.scol #mStrokes.sgp .sgrot{top:calc(var(--sctop) + 136px - var(--gt));bottom:auto}
/* Settings closes with its Back button only (Done did the same) */
#setDone{display:none!important}
html:is(.scol,.scolL) .mhome.lobby #homePlay{scale:.84}
html:is(.scol,.scolL) .mhome.lobby #pbar{scale:.86}
html:is(.scol,.scolL) .mhome.lobby .lcol.left{gap:20px}
"""

JS_DOCK = r"""
// (v424) the dock: on the cover screen, the open page's Back or close button moves into #scolDock (a box at the page root, under the
// camera) while its page shows, and back to its place when the page hides. Checked a few times a second; cheap.
(function () {
  const IDS = ['stBack', 'lkBack', 'frX', 'evBack', 'setBack', 'worldBack', 'dsX', 'smClose', 'stPopX', 'ttX', 'acX', 'onX', 'pkX', 'ibX'];
  const home = new Map(); let dock = null;
  const shown = el => { for (let p = el; p && p !== document.body; p = p.parentElement) { if (p.hidden) return false; const c = getComputedStyle(p); if (c.display === 'none' || c.visibility === 'hidden') return false; } return true; };
  function tick() {
    const on = document.documentElement.classList.contains('scol') || document.documentElement.classList.contains('scolL');
    if (!dock) { dock = document.createElement('div'); dock.id = 'scolDock'; document.body.appendChild(dock); }
    let n = 0;
    for (const id of IDS) {
      const b = document.getElementById(id); if (!b) continue;
      const h = home.get(id);
      if (h) { // docked: back home once its page hides (or the column goes)
        const vis = on && shown(h.parent);
        if (!vis) { h.parent.insertBefore(b, h.next && h.next.parentNode === h.parent ? h.next : null); home.delete(id); } else n++;
      } else if (on && shown(b.parentElement) && shown(b)) { home.set(id, { parent: b.parentElement, next: b.nextSibling }); dock.appendChild(b); n++; }
    }
    document.documentElement.style.setProperty('--scdk', (n ? n * 68 : 0) + 'px');
  }
  setInterval(tick, 250); addEventListener('resize', () => setTimeout(tick, 50));
})();
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    i = s.rfind("</script>"); s = s[:i] + JS_DOCK + s[i:]
    # the framing offset eases to its new value (snapped while the menu isn't showing, so coming back to it doesn't slide)
    s = rep(s, "const hero = { yaw: 0, mx: 0, mz: 0 }, heroOff = { x: 0, y: 0 },",
               "const hero = { yaw: 0, mx: 0, mz: 0 }, heroOff = { x: 0, y: 0 }, heroOS = { x: 0, y: 0, on: false } /* (v424: heroOff eased) */,")
    s = rep(s, "  if (heroK > 0.003 || outK > 0.003) { const vw = viewW, vh = viewH; camera.setViewOffset(vw, vh, heroOff.x * heroK + outroOffX * outK, heroOff.y * heroK + outroOffY * outK, vw, vh); }",
               "  if (heroK < 0.05 || !heroOS.on) { heroOS.x = heroOff.x; heroOS.y = heroOff.y; heroOS.on = heroK >= 0.05; } else { const e = 1 - Math.exp(-rdt * 4.5); heroOS.x += (heroOff.x - heroOS.x) * e; heroOS.y += (heroOff.y - heroOS.y) * e; }\n"
               "  if (heroK > 0.003 || outK > 0.003) { const vw = viewW, vh = viewH; camera.setViewOffset(vw, vh, heroOS.x * heroK + outroOffX * outK, heroOS.y * heroK + outroOffY * outK, vw, vh); }")
    # (Done is hidden: the note under Visuals says a change restarts the game, and focus goes to Back)
    s = rep(s, "$('gfxNote').textContent = GFX_NOTE[gfxPick]; $('setDone').textContent",
               "$('gfxNote').textContent = GFX_NOTE[gfxPick] + (gfxPick === GFX ? '' : ' Going back restarts the game to apply it.'); $('setDone').textContent")
    s = rep(s, "setTimeout(() => $('setDone').focus({ preventScroll: true }), 30);", "setTimeout(() => $('setBack').focus({ preventScroll: true }), 30);")
    s = rep(s, "(b.hidden ? $('setDone') : b).focus({ preventScroll: true })", "(b.hidden ? $('setBack') : b).focus({ preventScroll: true })")
    return s
