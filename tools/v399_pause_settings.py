"""v399: Settings from the pause menu, and commissions that wait quietly until they open (the user: "Add ability to view the settings
menu from the pause menu. Even if in-game you can access the settings page from pause. Once that's in, we can actually remove the
turning sensitivity, since it will be redundant with the settings button" and "A character is not level three, but he's getting
notifications that he can claim something in commissions ... don't say in the results page to go to the page that doesn't exist").

- The pause menu has a Settings button where the Turning slider was (the slider is in Settings, as it always was). Settings opens over
  the paused match and Done (or Back, or Escape) goes back to the pause menu. Mid-match it leaves out what can't be done then: Visuals
  (a change restarts the game), Screen (turning the match round), Restart Game and Delete account. Sound, music, turning, How to play
  and the documents are all there. In an online match, which doesn't stop for a pause, the same.
- Commissions before rank 3: a job finished still counts (it's waiting, done, when Commissions open), but the results no longer say
  "Commission done ... Claim it in Commissions" while Commissions are locked. The match that takes you to rank 3 says it, and the
  lobby's badge counts what's waiting from then on."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

GEAR = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8.6a3.4 3.4 0 1 0 0 6.8 3.4 3.4 0 0 0 0-6.8z" fill="none" stroke="currentColor" stroke-width="2.4"/>'
        '<path d="M10.3 2.8h3.4l.5 2.6 1.7.9 2.4-1.2 2.4 2.4-1.2 2.4.9 1.7 2.6.5v3.4l-2.6.5-.9 1.7 1.2 2.4-2.4 2.4-2.4-1.2-1.7.9-.5 2.6h-3.4l-.5-2.6-1.7-.9-2.4 1.2-2.4-2.4 1.2-2.4-.9-1.7-2.6-.5v-3.4l2.6-.5.9-1.7-1.2-2.4 2.4-2.4 2.4 1.2 1.7-.9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>')

CSS = r"""
/* (v399) Settings in the pause menu, where the Turning slider was */
#pause .psets{display:flex;align-items:center;justify-content:center;gap:9px}
#pause .psets svg{width:20px;height:20px;flex:none}
@media (min-aspect-ratio:1/1){#pause .card>.psets{grid-column:2;align-self:center}}
html.fv #pause .card>.psets{grid-column:1/-1}
"""

def apply(s):
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    # the pause menu: Settings in the slider's place
    s = rep(s, '<div class="pturn" role="group" aria-labelledby="pTurnLab"><div class="pthd"><span class="ptlab" id="pTurnLab">Turning</span><b class="trnv" id="pTurnVal">80%</b></div><div class="trn"><span class="trnl" aria-hidden="true">Gentle</span><input type="range" id="pTurnPick" min="50" max="150" step="5" value="80" aria-label="Turning speed"><span class="trnl" aria-hidden="true">Quick</span></div></div>',
               '<button class="btn psets" id="pauseSet" type="button" aria-haspopup="dialog">' + GEAR + '<span>Settings</span></button>')
    # the Turning slider is Settings' alone again
    s = rep(s, "{ const pairs = [[$('turnPick'), $('turnVal')], [$('pTurnPick'), $('pTurnVal')]];",
               "{ const pairs = [[$('turnPick'), $('turnVal')]]; // (v399: the pause menu's copy gone: Settings opens from there)")
    # Settings over a paused match: back to the pause menu when it closes; what can't be done mid-match left out
    s = rep(s, "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return;",
               "let setInPlay = false;\n"
               "// (v399) from the pause menu: the rows that can't be used mid-match (Visuals restarts the game, Screen turns it, Restart Game, Delete account) hidden\n"
               "function setPlayRows(on) { for (const id of ['orientPick', 'gfxPick']) { const r = $(id).closest('.sopt'); if (r) r.hidden = on; } $('resetBtn').hidden = on; if (on) $('delAcBtn').hidden = true; else delPaint(); }\n"
               "function openSettingsInPlay() {\n"
               "  if (!(state === 'paused' || (NM && state === 'play')) || pauseEl.hidden) return;\n"
               "  setInPlay = true; pauseEl.hidden = true; gfxPick = GFX; paintSettings(); setPlayRows(true); if (window.__turnShow) window.__turnShow(); setModal.hidden = false; setFit();\n"
               "  setTimeout(() => $('setDone').focus({ preventScroll: true }), 30);\n"
               "}\n"
               "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return;")
    s = rep(s, "function closeSettings() { if (setModal.hidden) return; setModal.hidden = true; $('hamBtn').focus({ preventScroll: true }); }",
               "function closeSettings() { if (setModal.hidden) return; setModal.hidden = true;\n"
               "  if (setInPlay) { setInPlay = false; setPlayRows(false); if (state === 'paused' || (NM && state === 'play')) { pauseEl.hidden = false; setTimeout(() => $('resumeBtn').focus({ preventScroll: true }), 30); } return; } // (v399: back to the pause menu)\n"
               "  $('hamBtn').focus({ preventScroll: true }); }")
    s = rep(s, "$('setDone').addEventListener('click', uiClick(doneSettings));",
               "$('setDone').addEventListener('click', uiClick(doneSettings));\n"
               "$('pauseSet').addEventListener('click', () => { AU.init(); AU.ui(); openSettingsInPlay(); }); // (v399)")
    # the results: a finished commission is only mentioned once Commissions are open
    s = rep(s, "  $('commDone').innerHTML = (info.comms || []).map(",
               "  $('commDone').innerHTML = (repOf(info.xp0 + info.xp).lv >= COMM_RANK ? info.comms || [] : []).map( // (v399: locked, it waits quietly)\n    ")
    return s
