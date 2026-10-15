"""v273: when you leave the Strokes (Abilities) page at the end of its lesson, Ol' Bloop pops up in the lobby: new game modes, Time trial
and Showdown, are open. "Show me" opens Choose event (the two cards carry their New! tags), "Later" just closes it. It shows once, only
for a player finishing the Strokes lesson. Leaving the page while his last line is still up ends the lesson there and then (it used
to ask you to open Strokes again)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = """// (v273) back in the lobby after the Strokes lesson: Ol' Bloop tells you the new game modes are open. Once, for whoever has just finished it
function tutModesDue() { return tutPh() === 'done' && store.tut.modes === 'due' && evUnlocked() && state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !building && !irisBusy && setModal.hidden && nameModal.hidden && howModal.hidden && $('tutGo').hidden && !vic; }
function tutModesCard() {
  const el = $('tutGo'); if (!el.hidden) return; el.dataset.mode = 'modes'; store.evNew = Object.assign(store.evNew || {}, { solo: 1, showdown: 1 }); menu.classList.add('tutoring');
  tutCardText(['New game <em>modes!</em>', 'Time trial and Showdown are open now. Time trial: paint all you can in 60 seconds and beat your best. Showdown: two hearts each, last one standing wins.', 'Show me', 'Later']);
  el.hidden = false; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); tutCardCoach(); AU.fanfare && AU.fanfare(); AU.bloop(0.55); setTimeout(() => $('tgGo').focus({ preventScroll: true }), 60);
}
function tutModesDone(open) { const el = $('tutGo'); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = ''; store.tut.modes = 1; save(); menu.classList.remove('tutoring'); if (open) setTimeout(() => openEvents(), 250); }
"""

def apply(s):
    # the lesson's end marks the card due; leaving the page with the Giant equipped ends the lesson at once
    s = rep(s, "function tutStrokesEnd() { tutSDone = 0; store.tut.strokes = 1;", "function tutStrokesEnd() { tutSDone = 0; store.tut.strokes = 1; if (!store.tut.modes) store.tut.modes = 'due';")
    s = rep(s, "  if (!strokesOpen()) return tutShow('Tap Strokes to open it', 'abilBtn', 'sOpen');",
            "  if (!strokesOpen() && strokeSpecial() === 'giant' && strokesOf().own.includes('giant')) return tutStrokesEnd(); // (v273: done, and back out: the lesson's over)\n"
            "  if (!strokesOpen()) return tutShow('Tap Strokes to open it', 'abilBtn', 'sOpen');")
    s = rep(s, "function tutWelcome() {", JS + "function tutWelcome() {")
    # in the lobby: after a short beat, before the commissions card
    s = rep(s, "  if (tutPh() === 'done' && tutCommsDue()) {",
            "  if (tutPh() === 'done' && tutModesDue()) { if (!tutModesAt) tutModesAt = performance.now(); if (performance.now() - tutModesAt > 700) tutModesCard(); return; } else tutModesAt = 0;\n"
            "  if (tutPh() === 'done' && tutCommsDue()) {")
    s = rep(s, "let tutStrokesAt = 0, tutSDone = 0, tutCommsAt = 0;", "let tutStrokesAt = 0, tutSDone = 0, tutCommsAt = 0, tutModesAt = 0;")
    # its buttons
    s = rep(s, "if (m === 'welcome') tutWelcomeDone(true); else if (m === 'strokes1'", "if (m === 'welcome') tutWelcomeDone(true); else if (m === 'modes') tutModesDone(true); else if (m === 'strokes1'")
    s = rep(s, "$('tgLater').addEventListener('click', () => { AU.init(); AU.ui(); tutWelcomeDone(false); });",
            "$('tgLater').addEventListener('click', () => { AU.init(); AU.ui(); if ($('tutGo').dataset.mode === 'modes') return tutModesDone(false); tutWelcomeDone(false); });")
    return s
