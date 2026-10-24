"""v448: the canvas picker opens on Palette Island; Shuffle sits on its own between the canvases and the leaderboard; Play centred.

- The user: "why does pick a canvas start at spooky szn? start at palette island and they can move right". Opening Pick a canvas
  (or Vote for a canvas) always lands on the first canvas, Palette Island, and the rest are to its right. It used to open on the
  last canvas chosen, and Spooky SZN, the last in the row, is where a new save starts.
- "move the shuffle button in-between the canvas' and the leaderboard. centered, then center the play button": on a tall screen
  (any phone held upright, a tablet either way) Shuffle moves out of the row beside Play into the open space under the canvases,
  centred, and Play has the bottom row to itself, centred. On a phone held sideways there's no height for a row of its own, so it
  stays where it was, between the leaderboard and Play; on the Duo's folded layouts too."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v448) Shuffle on its own row under the canvases (tall screens), Play alone and centred */
.mworld>.shufslot{display:none}
@media (max-aspect-ratio:1/1),(min-aspect-ratio:1/1) and (min-height:521px){
  html:not(.fv):not(.fh) .menu:not(.tutoring) .mworld>.shufslot{display:flex;grid-row:6;grid-column:1/-1;justify-content:center;align-items:center;align-self:center;min-height:0}
  html:not(.fv):not(.fh) .menu:not(.tutoring) .mworld>.shufslot>#shuffleBtn{width:58px;height:58px}
  html:not(.fv):not(.fh) .menu:not(.tutoring) .mworld .wgo{justify-content:center}
  html:not(.fv):not(.fh) .menu:not(.tutoring) .mworld .wgo .btn.play{flex:0 1 auto;width:min(100%,360px)}
}
"""

JS = r"""
// (v448) Shuffle's place: its own row under the canvases where the screen is tall enough, else beside Play as before
function shufPlace() {
  const b = $('shuffleBtn'), slot = $('shufSlot'), row = $('mWorld').querySelector('.wgo'); if (!b || !slot || !row) return;
  const h = document.documentElement, tall = !matchMedia('(max-height:520px) and (min-aspect-ratio:1/1)').matches && !h.classList.contains('fv') && !h.classList.contains('fh') && !menu.classList.contains('tutoring');
  if (tall && b.parentElement !== slot) slot.appendChild(b); else if (!tall && b.parentElement !== row) row.insertBefore(b, row.firstChild);
}
addEventListener('resize', () => requestAnimationFrame(shufPlace));
"""

def apply(s):
    # opens on Palette Island, whatever was picked last
    s = rep(s, "  renderModes(); renderStages(); $('worldTitle').textContent = mode === 'solo' ? 'Pick a canvas' : 'Vote for a canvas';\n  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();",
               "  if (stageSel !== 'island' && worldBtns.some(b => b.dataset.s === 'island')) { stageSel = 'island'; store.stage = stageSel; save(); worldDirty = true; } /* (v448: always opens on the first canvas) */\n"
               "  renderModes(); renderStages(); $('worldTitle').textContent = mode === 'solo' ? 'Pick a canvas' : 'Vote for a canvas'; shufPlace();\n  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();")
    # the row Shuffle moves to on a tall screen
    s = rep(s, '<div class="gdots" id="gDots" aria-hidden="true">', '<div class="shufslot" id="shufSlot"></div><div class="gdots" id="gDots" aria-hidden="true">')
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    a = "function openWorlds() {"; s = rep(s, a, JS.strip() + "\n" + a)
    return s
