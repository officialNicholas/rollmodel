"""v283, three things.
1. Skip tutorial: in the first lesson match, Pause offers "Skip tutorial" where it said "Menu". Skipping ends the lesson there: you're
   back in the lobby with what the match would have given you (the flower and the fangs, yours already, since there are no dabs from a
   match you skipped), and Ol' Bloop goes straight on to the locker lesson: open your locker and put them on. Then the lesson carries on
   as ever (the canvas vote, the second match).
2. The first launch's puddle and shake-off get their own sounds (made with Ludo): the paint puddle blorping as it bubbles, a deep wet
   gloop with drips falling back as the eyes come up out of it, squishy pulls as it hauls itself out, and a rubbery flap-flap with a
   splatter of paint as it shakes itself off. Fetched while the barrel rocks, so they're ready for their moments.
3. Once the new game modes are open (after the "New game modes!" card), Ol' Bloop suggests Showdown the first time you're on Choose
   event: his pick sits on the Showdown card (his face in a gold ring and a "Try this one!" tag, bobbing), a suggestion only: nothing
   dimmed or blocked, any card works. It goes once you leave the page."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SKIP = """// (v283) Skip tutorial, from the first lesson's pause: the match ends there and you're back in the lobby with what it would have given you,
// the flower and the fangs, already yours (there are no dabs from a match you skipped), and Ol' Bloop goes on to putting them on
function tutSkip() {
  if (!tut || state !== 'paused') return;
  tutCard(false); tut = null; tutHide(); if (tutSlowEl.classList.contains('on')) AU.slow(false, true); tutSlowEl.classList.remove('on'); tutPipsEl.classList.remove('on');
  for (const id of ['flower', 'fangs']) { OWNED.add(id); BOUGHT.add(id); } store.owned = [...OWNED]; store.bought = [...BOUGHT]; store.fresh = [...new Set([...(store.fresh || []), 'flower', 'fangs'])];
  newItem = null; delete store.tut.price; store.tut.skipped = 1; tutSet('locker'); save(); toMenu();
}
"""

SUGGEST = """  // (v283) the modes are open: the first time you're on Choose event, Ol' Bloop's pick sits on the Showdown card (his face and "Try this
  // one!"), a suggestion only: nothing dimmed or blocked, any card works; it goes once you leave the page
  if (tutPh() === 'done' && store.tut.trySd === 'due') { const sd = document.querySelector('.evcard[data-ev="showdown"]');
    if (state === 'menu' && menuPage === 'events' && sd) { if (!sd.querySelector('.evbloop')) { sd.classList.add('bpick'); sd.insertAdjacentHTML('beforeend', '<span class="evbloop" aria-hidden="true"><i></i><b>Try this one!</b></span>'); } tutTrySdAt = 1; }
    else if (tutTrySdAt) { store.tut.trySd = 1; save(); tutTrySdAt = 0; document.querySelectorAll('.evbloop').forEach(e => e.remove()); document.querySelectorAll('.evcard.bpick').forEach(e => e.classList.remove('bpick')); }
  }
"""

CSS = ("\n/* (v283) Ol' Bloop's pick on the Showdown card: his face in a gold ring and a gold tag, bobbing on the card's picture; taps go through */"
       "\n.evbloop{position:absolute;right:12px;bottom:14px;z-index:4;display:flex;align-items:center;pointer-events:none;animation:evbloopin .5s cubic-bezier(.2,1.5,.35,1) .35s both,evbloopbob 2.4s ease-in-out .9s infinite}"
       "\n.evbloop i{position:relative;z-index:1;flex:none;width:46px;height:46px;border-radius:50%;background:#2A2437 url(art/coach.webp) 50% 16%/165% no-repeat;box-shadow:0 0 0 2.5px #F2C14E,0 0 0 5px #171320,0 5px 0 5px rgba(0,0,0,.25)}"
       "\n.evbloop b{margin-left:-12px;padding:8px 13px 7px 19px;border-radius:999px;background:#F2C14E;color:#171320;font:900 12px/1 var(--font-head);letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;box-shadow:0 0 0 2.5px #171320,0 4px 0 #171320}"
       "\n@keyframes evbloopin{from{opacity:0;transform:translateY(10px) scale(.55)}}"
       "\n@keyframes evbloopbob{50%{transform:translateY(-4px) rotate(-2deg)}}"
       "\n@media (prefers-reduced-motion:reduce){.evbloop{animation:none}}\n")


def apply(s):
    # 1. Skip tutorial
    s = rep(s, "$('pauseClock').textContent = fmtClock(matchLeft) + ' left'; pauseEl.hidden = false;",
               "$('pauseClock').textContent = fmtClock(matchLeft) + ' left'; $('quitBtn').textContent = tut ? 'Skip tutorial' : 'Menu'; pauseEl.hidden = false;")
    s = rep(s, "$('quitBtn').addEventListener('click', uiClick(toMenu));", "$('quitBtn').addEventListener('click', uiClick(() => tut ? tutSkip() : toMenu())); // (v283: the first lesson's pause skips it)")
    s = rep(s, "function tutFangsSale() {", SKIP + "function tutFangsSale() {")
    # 2. the intro's puddle and shake-off sounds
    s = rep(s, "if (t >= 0.5 && once('w1')) snd('wobble', 0.75);",
               "if (t >= 0.5 && once('w1')) { snd('wobble', 0.75); if (AU.xwant) for (const n of ['i_bubble', 'i_rise', 'i_climb', 'i_shake']) AU.xwant(n); } // (v283: the puddle's and the shake's sounds, fetched now)")
    s = rep(s, "for (const [k, at, v] of [['b1', 5.55, 0.18], ['b2', 5.85, 0.26]]) if (t >= at && once(k)) { ripple(C0.x + rnd(-0.05, 0.05), C0.z + rnd(-0.05, 0.05), v); AU.glug && AU.glug(0.4 + v); }",
               "for (const [k, at, v] of [['b1', 5.55, 0.18], ['b2', 5.85, 0.26]]) if (t >= at && once(k)) { ripple(C0.x + rnd(-0.05, 0.05), C0.z + rnd(-0.05, 0.05), v); if (!(k === 'b1' && AU.xplay && AU.xplay('i_bubble', { v: 0.75 }))) AU.glug && AU.glug(0.4 + v); }")
    s = rep(s, "if (t >= 6.2 && once('pop')) { X.hold.visible = true; snd('eyes', 1);",
               "if (t >= 6.2 && once('pop')) { X.hold.visible = true; snd('eyes', 1); AU.xplay && AU.xplay('i_rise', { v: 0.85 });")
    s = rep(s, "if (once('f0')) { snd('form', 1);", "if (once('f0')) { snd('form', 1); AU.xplay && AU.xplay('i_climb', { v: 0.8, d: 0.12 });")
    s = rep(s, "if (t >= J1 + 0.38 && once('shake')) { I.shake && I.shake(1);", "if (t >= J1 + 0.38 && once('shake')) { AU.xplay && AU.xplay('i_shake', { v: 0.95 }); I.shake && I.shake(1);")
    # 3. Ol' Bloop suggests Showdown
    s = rep(s, "function tutModesDone(open) { const el = $('tutGo'); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = ''; store.tut.modes = 1;",
               "function tutModesDone(open) { const el = $('tutGo'); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = ''; store.tut.modes = 1; if (!store.tut.trySd) store.tut.trySd = 'due';")
    s = rep(s, "let tutStrokesAt = 0, tutSDone = 0, tutCommsAt = 0, tutModesAt = 0;", "let tutStrokesAt = 0, tutSDone = 0, tutCommsAt = 0, tutModesAt = 0, tutTrySdAt = 0;")
    s = rep(s, "  if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring');", SUGGEST + "  if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring');")
    a = '.evcard:not(.fresh) .evnew{display:none}'
    s = rep(s, a, a + CSS)
    return s
