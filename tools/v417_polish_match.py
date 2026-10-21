"""v417: a polish pass on the match and its results (the user: "Get two other agents to look at different parts of the game and polish.
Polish spacing, continuity, corners, performance and radius. Micro animations. Everything that makes this game feel very premium").
The menus are the other pass's (v417_polish_menus); this one is everything in and around a match. Most of it was already moving and
pressing well; what was off or missing:
- Spacing: on a 320 px wide phone the three-way score card grew past its column and ran under the sound button (the grid's middle
  column couldn't shrink below the row of numbers). The column can now shrink, and on that width the card's inside is a little
  tighter (side padding 10, the clock's 10) so the row fits.
- Spacing: Showdown's hearts were wider than the face above them (three 14 px hearts under a 31 to 38 px face), so neighbours' hearts
  ran together into one row. They now size to the face (up to the old 14 px).
- Spacing: the pointers to rivals, orbs, gifts and rings sat on the top edge of the pound button and the item button when the thing
  was low on the screen; they now stop just above those buttons (only when they would overlap; everywhere else they're unchanged).
- Continuity and corners: in a match the sound button was the dark rounded one from the menus while the pause button across from it
  is the taped paper square; now both are paper, the same size, the same distance from their edges (landscape: 40 px at 8 px, as the
  pause is) and the sound button drops in with the score card when the match starts.
- Micro animations: rival pointers pop in when they appear; the pause card's contents rise in one after another behind the card; the
  results sheet's title, score bar and buttons rise in one after another as the sheet comes up (the reputation row keeps its own
  later beat). All of it is transform/opacity only, on the shared motion tokens, and off with reduced motion.
- Performance: the item buttons rewrote an empty data-k attribute every frame (three buttons, about 2 attribute writes a frame in
  Showdown); now only when it changes. The Showdown card and time trial card heights were re-measured twice a second with
  getBoundingClientRect (a forced layout in the middle of the frame); now only when the screen, the HUD or the card's size changes
  (a ResizeObserver), once more after the HUD's slide-in settles.
- A crash fixed on the way: a Showdown you lost where two or more rivals tied for first (no single winner) threw while the results
  sheet built its label (nameOf of no one), so the Showdown board never filled in; that label now just says Defeat."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v417) match polish: the score card fits a 320 px phone, Showdown hearts the width of their face, the in-match sound button
   paper like the pause, and a few entrances (rival pointers, the pause card's contents, the results sheet's rows) */
@media (max-width:359px) and (max-aspect-ratio:1/1){.hud .top{grid-template-columns:44px minmax(0,1fr) 44px}.hud .score{padding-left:10px;padding-right:10px}.hud .score .vsrow{padding:0 2px}.hud .score .clock{padding-left:10px;padding-right:10px}}
.hud.sdmode .sdh{gap:0;height:auto}
.hud.sdmode .sdh svg{width:min(14px,calc((var(--sdb) + 6px) / 3));height:auto;aspect-ratio:14/13}
html:not(.roomy) #hud:not(.off)~.corner{right:max(14px,calc(env(safe-area-inset-right) + 8px))}
#hud:not(.off)~.corner .ib{background:#FBF8F1 url(art/m_paperbg.webp) center/300px;color:var(--black);border-radius:3px;box-shadow:3px 4px 0 rgba(23,19,32,.28)}
@media (max-height:520px) and (min-aspect-ratio:1/1){html:not(.roomy) #hud:not(.off)~.corner{top:max(8px,env(safe-area-inset-top))}#hud:not(.off)~.corner .ib{width:40px;height:40px}}
@keyframes p17drop{from{translate:0 -38px;opacity:0}}
@keyframes p17up{from{translate:0 12px;opacity:0}}
@keyframes p17pop{from{scale:.5;opacity:0}}
@media (prefers-reduced-motion:no-preference){
#hud:not(.off)~.corner .ib{animation:p17drop .55s cubic-bezier(.3,1.55,.5,1) backwards}
.foeptr.on>*{animation:p17pop var(--d-med,.24s) var(--ease-pop,cubic-bezier(.3,1.55,.5,1)) backwards}
#pause .card>*{animation:p17up var(--d-med,.24s) var(--ease-out,cubic-bezier(.2,.8,.2,1)) backwards}
#pause .card>:nth-child(1){animation-delay:.05s}#pause .card>:nth-child(2){animation-delay:.09s}#pause .card>:nth-child(3){animation-delay:.13s}#pause .card>:nth-child(4){animation-delay:.17s}#pause .card>:nth-child(n+5){animation-delay:.21s}
#end>.rhead,#end>.judge,#end>#endBtn,#end>.row{animation:p17up var(--d-slow,.38s) var(--ease-out,cubic-bezier(.2,.8,.2,1)) backwards}
#end>.rhead{animation-delay:.06s}#end>.judge{animation-delay:.12s}#end>#endBtn{animation-delay:.3s}#end>.row{animation-delay:.36s}
}
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    # the item buttons: an empty data-k written only when it isn't already
    s = rep(s, "} else if (!held) ib.dataset.k = ''; }", "} else if (!held && ib.dataset.k) ib.dataset.k = ''; }")
    s = rep(s, "} else if (!h2) b2.dataset.k = '';", "} else if (!h2 && b2.dataset.k) b2.dataset.k = '';")
    s = rep(s, "} else if (!os) ob.dataset.k = '';", "} else if (!os && ob.dataset.k) ob.dataset.k = '';")
    # the HUD's measured heights: again only when something could have moved them
    s = rep(s, "function sdCardBot() { if (Math.abs(clock - sdCardAt) > 0.5) { sdCardAt = clock; const c = ",
               """// (v417) a layout value is measured again only when something could have moved it: the screen's size, the HUD's classes, or a
// size change the observer saw (the score card, the pound and item buttons); and once more 0.7 s later, when the HUD's slide-in has
// settled. (They were read twice a second, each read a forced layout in the middle of the frame.)
function p17Stale(n) {
  const S = p17Stale.st || (p17Stale.st = { gen: 0 });
  if (!S.ro && typeof ResizeObserver === 'function') { S.ro = new ResizeObserver(() => { S.gen++; }); for (const e of hud.querySelectorAll('.score,.slamBtn,.itemBtn')) S.ro.observe(e); }
  const o = S[n] || (S[n] = { k: '', due: -1 }), k = viewW + 'x' + viewH + ' ' + hud.className + ' ' + S.gen;
  if (k !== o.k) { o.k = k; o.due = clock + 0.7; return true; }
  if (o.due >= 0 && (clock >= o.due || clock < o.due - 1)) { o.due = -1; return true; }
  return false;
}
// (v417) an edge pointer that would sit on the pound or item button stops just above it
function p17Dodge(px, py) {
  if (p17Stale('dodge') || !p17Dodge.b) { p17Dodge.b = []; // (the layout box, not the drawn one: a button mid-pop is scaled)
    for (const e of hud.querySelectorAll('.slamBtn,.itemBtn')) { let x = 0, y = 0, n = e; while (n && n !== stage) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
      if (n && e.offsetWidth) p17Dodge.b.push([x - 26, y - 24, x + e.offsetWidth + 26]); } }
  for (const b of p17Dodge.b) if (px > b[0] && px < b[2] && py > b[1]) py = b[1];
  return py;
}
function sdCardBot() { if (p17Stale('sd')) { sdCardAt = clock; const c = """)
    s = rep(s, "const trHudBot = () => { if (clock - trHudAt > 0.5) { trHudAt = clock; const e",
               "const trHudBot = () => { if (p17Stale('tr')) { trHudAt = clock; const e")
    # the edge pointers (rival, orb, gift, ring, +1): clear of the pound and item buttons
    s = rep(s, "py = (-y * 0.5 + 0.5) * Hh; rot = Math.atan2(x, y) * 180 / Math.PI; }",
               "py = p17Dodge(px, (-y * 0.5 + 0.5) * Hh); rot = Math.atan2(x, y) * 180 / Math.PI; }", 4)
    s = rep(s, "py = (-y * 0.5 + 0.5) * Hh, rot = Math.atan2(x, y) * 180 / Math.PI, dHP",
               "py = p17Dodge(px, (-y * 0.5 + 0.5) * Hh), rot = Math.atan2(x, y) * 180 / Math.PI, dHP")
    # the results sheet: a Showdown lost to a tie between rivals (no single winner) threw building its label
    s = rep(s, "info.win < 0 ? 'Defeat. ' + nameOf(info.winner) + ' wins' : 'Draw'",
               "info.win < 0 ? (info.winner ? 'Defeat. ' + nameOf(info.winner) + ' wins' : 'Defeat') : 'Draw'")
    return s
