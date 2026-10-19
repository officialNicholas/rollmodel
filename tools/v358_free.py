"""v358: free once the locker's done.

- After the locker lesson nothing in the lobby tells you what to play next: no "Time for a real match. Tap Play" (and no dimmed lobby round
  the Play button), no "Play the CPU: tap Versus CPU" or "Tap 1 v 1" on Choose event, and no "pick a painting, then Play" on the canvas
  vote. The lobby is the full one from then on (it was kept simple, with things hidden, until the second match was over).
- The match you play next, whatever you pick, is still the second lesson match (its sun, shade and missile tips, on Sludge Sewer), unless
  it's online: the lesson tips never run in an online match (they slow time down), and the third match's orb help doesn't either.
- At rank 2 there's no "New game modes!" card with its Show me, and no "Try this one!" on the Showdown card. Time trial and Showdown still
  show as new on Choose event. The Strokes lesson at rank 2 and the Commissions welcome at rank 3 stay: they're not about modes."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def cut(s, a, b, new=''):
    """Replace the text from marker a (included) up to marker b (kept) with new."""
    assert s.count(a) == 1 and s.count(b) == 1, (s.count(a), s.count(b), a[:80], b[:80])
    i, j = s.index(a), s.index(b); assert i < j, (a[:60], b[:60]); return s[:i] + new + s[j:]

def apply(s):
    # ---- the lobby after the locker: no tip on Play, Choose event or the canvas vote (the locker's own "Take a look around" stays)
    s = cut(s, "  if (menuPage === 'worlds') return innerWidth > innerHeight && innerHeight < 520 ? tutShow('*SWIPE* to pick your painting, then tap *PLAY*'",
               "// the lesson's finish, in place of the tally for a beat: the canvas through the window",
               "  return tutHide(); // (v358: done with the locker, you're free: nothing says what to play next, and nothing in the lobby is dimmed)\n}\n")
    # ---- and the full lobby from then on, not the simple one (the lessons before the locker, and the Strokes lesson, keep it simple)
    s = rep(s, "  const ph = tutPh(); if (menu.classList.contains('tutoring') !== (ph !== 'done')) menu.classList.toggle('tutoring', ph !== 'done');",
               "  const ph = tutPh(), simple = ph !== 'done' && ph !== 'vote' && ph !== 'match2'; if (menu.classList.contains('tutoring') !== simple) menu.classList.toggle('tutoring', simple); /* (v358: not after the locker) */")
    # ---- the next match is the second lesson match, and the one after it the third, but never online (their tips slow time down, and the
    # third match's orb is moved for you)
    s = rep(s, "  if (tutPh() === 'vote') tutSet('match2');\n  tut2 = null; if (tutPh() === 'match2') tut2Begin();\n  tut3 = null; if (tutPh() === 'done' && store.tut.m3 === 1) tut3Begin();",
               "  if (tutPh() === 'vote' && !NM) tutSet('match2'); // (v358: whatever you play next, unless it's online)\n  tut2 = null; if (tutPh() === 'match2' && !NM) tut2Begin();\n  tut3 = null; if (tutPh() === 'done' && store.tut.m3 === 1 && !NM) tut3Begin();")
    s = rep(s, "  if (tutPh() === 'match2') { tut2 = null; tutHide(); delete store.tut.price; store.tut.m3 = 1; tutSet('done'); save(); }",
               "  if (tutPh() === 'match2' && tut2) { tut2 = null; tutHide(); delete store.tut.price; store.tut.m3 = 1; tutSet('done'); save(); }")
    # ---- rank 2: no "New game modes!" card and no "Try this one!" on Showdown (a save waiting on either just has it marked done)
    s = rep(s, "store.tut.strokes = 1; if (!store.tut.modes) store.tut.modes = 'due'; tutSet('done');",
               "store.tut.strokes = 1; if (!store.tut.modes) store.tut.modes = 1; /* (v358: no modes card: they show as new on Choose event) */ tutSet('done');")
    s = rep(s, "  if (tutPh() === 'done' && tutModesDue()) { if (!tutModesAt) tutModesAt = performance.now(); if (performance.now() - tutModesAt > 700) tutModesCard(); return; } else tutModesAt = 0;\n",
               "  if (store.tut.modes === 'due') { store.tut.modes = 1; save(); } // (v358: the modes card is gone)\n")
    s = cut(s, "  // (v283) the modes are open: the first time you're on Choose event, Ol' Bloop's pick sits on the Showdown card",
               "  if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring');",
               "  if (store.tut.trySd === 'due') { store.tut.trySd = 1; save(); } // (v358: no pick on the Showdown card)\n")
    return s
