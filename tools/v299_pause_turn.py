"""v299: the Turning slider is in the pause menu too, and it starts at 80%.

- Pausing a match shows a Turning strip under the score: the same slider as in Settings (Gentle to Quick, 50% to 150% in steps of 5,
  the gold knob and the gold value tag), on the paper card. It takes effect when you resume, and Settings shows the same value:
  moving either one moves both, and it's saved.
- In landscape the card is wider and the strip sits beside the score, so the card is no taller than before.
- With a keyboard, the arrow keys move the slider while it has focus, and Escape or P still resumes. In Settings, Escape now closes the
  page even while the slider has focus.
- The default is now 80% (was 100%). Anyone who hasn't moved the slider gets 80%. A value someone picked themselves stays as it was."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

PTURN = ('<div class="pturn" role="group" aria-labelledby="pTurnLab"><div class="pthd"><span class="ptlab" id="pTurnLab">Turning</span><b class="trnv" id="pTurnVal">80%</b></div>'
         '<div class="trn"><span class="trnl" aria-hidden="true">Gentle</span><input type="range" id="pTurnPick" min="50" max="150" step="5" value="80" aria-label="Turning speed"><span class="trnl" aria-hidden="true">Quick</span></div></div>\n      ')

CSS = r"""
/* (v299) the Turning slider in the pause card: a strip like the score's, holding the same gold slider as Settings */
.pturn{display:grid;gap:2px;padding:10px 14px 4px;border-radius:6px;background:var(--paper-2)}
.pthd{display:flex;align-items:center;gap:10px}
.ptlab{font:900 16px/1 var(--font-head);letter-spacing:.02em;text-transform:uppercase;color:var(--black);transform:skewX(-6deg)}
.pturn .trn{height:40px}
.pturn .trnl{color:var(--muted)}
#pTurnPick{--v:30%;-webkit-appearance:none;appearance:none;width:100%;height:30px;margin:0;padding:0;background:none;cursor:pointer;touch-action:pan-y}
#pTurnPick:focus{outline:none}
#pTurnPick::-webkit-slider-runnable-track{height:16px;border-radius:9px;background:linear-gradient(90deg,#F2C14E 0,#FFE08A var(--v),#28243A var(--v));box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(0,0,0,.3)}
#pTurnPick::-moz-range-track{height:16px;border-radius:9px;background:linear-gradient(90deg,#F2C14E 0,#FFE08A var(--v),#28243A var(--v));box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(0,0,0,.3)}
#pTurnPick::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:30px;height:30px;margin-top:-7px;border:0;border-radius:9px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(255,255,255,.5),inset 0 -4px 0 rgba(0,0,0,.18),0 4px 0 #171320;transform:skewX(-6deg)}
#pTurnPick::-moz-range-thumb{width:30px;height:30px;border:0;border-radius:9px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(255,255,255,.5),inset 0 -4px 0 rgba(0,0,0,.18),0 4px 0 #171320}
#pTurnPick:focus-visible::-webkit-slider-thumb{outline:3px solid #171320;outline-offset:3px}
@media (min-aspect-ratio:1/1){#pause .card{width:min(100%,620px);grid-template-columns:repeat(2,minmax(0,1fr))}#pause .card>*{grid-column:1/-1}#pause .card>.pscore{grid-column:1}#pause .card>.pturn{grid-column:2}}
"""

JS_OLD = """// (v295) the Turning slider in Settings
{ const el = $('turnPick'), show = () => { const v = turnPct(); el.value = String(v); el.style.setProperty('--v', ((v - 50) / 100 * 100).toFixed(1) + '%'); $('turnVal').textContent = v + '%'; el.setAttribute('aria-valuetext', v + '%'); };
  let last = turnPct();
  el.addEventListener('input', () => { const v = Math.round(+el.value / 5) * 5; store.turn = clamp(v, 50, 150); show(); if (v !== last) { last = v; try { AU.tick && AU.tick(0); } catch (e) {} } });
  el.addEventListener('change', () => { save(); });
  window.__turnShow = show; show(); }
"""
JS_NEW = """// (v295) the Turning slider in Settings (v299: and the same one in the pause menu; moving either moves both)
{ const pairs = [[$('turnPick'), $('turnVal')], [$('pTurnPick'), $('pTurnVal')]];
  const show = () => { const v = turnPct(); for (const [el, lab] of pairs) { el.value = String(v); el.style.setProperty('--v', ((v - 50) / 100 * 100).toFixed(1) + '%'); lab.textContent = v + '%'; el.setAttribute('aria-valuetext', v + '%'); } };
  let last = turnPct();
  for (const [el] of pairs) {
    el.addEventListener('input', () => { const v = Math.round(+el.value / 5) * 5; store.turn = clamp(v, 50, 150); show(); if (v !== last) { last = v; try { AU.tick && AU.tick(0); } catch (e) {} } });
    el.addEventListener('change', () => { save(); });
    el.addEventListener('keydown', e => { // (the game's keys skip inputs, so while the slider has focus Escape and P are handled here)
      if (e.key !== 'Escape' && e.key !== 'p' && e.key !== 'P') return;
      if (state === 'paused' && !pauseEl.hidden) { e.preventDefault(); resume(); } else if (e.key === 'Escape' && !setModal.hidden) { e.preventDefault(); closeSettings(); } });
  }
  window.__turnShow = show; show(); }
"""

def apply(s):
    # 80% unless you've picked something else
    s = rep(s, "const turnPct = () => { const v = +store.turn; return v >= 50 && v <= 150 ? Math.round(v / 5) * 5 : 100; },",
               "const turnPct = () => { const v = +store.turn; return v >= 50 && v <= 150 ? Math.round(v / 5) * 5 : 80; }, // (v299: 80% unless you've picked something else)\n ")
    s = rep(s, '<b class="trnv" id="turnVal">100%</b>', '<b class="trnv" id="turnVal">80%</b>')
    s = rep(s, '<input type="range" id="turnPick" min="50" max="150" step="5" value="100"', '<input type="range" id="turnPick" min="50" max="150" step="5" value="80"')
    # the strip in the pause card, under the score
    a = '<div class="pscore"><b class="you" id="pauseYou">0%</b><span id="pauseClock">1:30 left</span><b class="cpu" id="pauseCpu">0%</b></div>\n      '
    s = rep(s, a, a + PTURN)
    s = rep(s, JS_OLD, JS_NEW)
    s = rep(s, "$('quitBtn').textContent = tut ? 'Skip tutorial' : 'Menu'; pauseEl.hidden = false;",
               "$('quitBtn').textContent = tut ? 'Skip tutorial' : 'Menu'; if (window.__turnShow) window.__turnShow(); pauseEl.hidden = false;")
    b = "@media (max-height:520px) and (min-aspect-ratio:1/1){.trn{height:40px}}"
    s = rep(s, b, b + CSS.rstrip('\n'))
    return s
