"""v441: the tutorial is optional, every mode is open, nothing has to be bought, and Ol' Bloop mostly steps back.

- After the intro, in place of Ol' Bloop pointing at Play ("Your first match is a little training session"), a card asks:
  Learn the basics? "Teach me" plays the training match as before; "Just play" skips it (nothing taught, nothing pointed at)
  and opens Choose Event. Skip tutorial in the lesson's pause menu now skips the same way.
- Every game mode is open from the start: Versus (1v1, 3-way), Time trial and Showdown. Play online keeps its own lock.
- The flower and the fangs are never forced on anyone: after the lesson there is no guided trip to the Paint Shop and the locker
  (no "half price, buy it", no "fangs on sale, grab them"). Both are in the Paint Shop from the start, cheap (25 and 40 dabs; the
  fangs no longer have to be found on a Spooky SZN canvas first).
- Ol' Bloop stays for the training match (and the second match's sun and rain tips, for whoever took the lesson). Gone: the second
  match's slingshot reminder ("Don't forget to SLINGSHOT!"), the slingshot pro tip in later matches, the third match's Giant script,
  and his cards in the lobby at rank 3 (Strokes, Commissions) along with the match-end "Main menu" gate that led to them.
- Saves already partway through: one at the forced shop or locker step moves on past it; one owed the third match's script doesn't
  get it."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CARD = r"""
// (v441) the first thing after the intro: learn the basics (the training match) or just play (skip it, straight to Choose Event)
function tutBasicsCard() {
  const el = $('tutGo'); if (!el.hidden) return; el.dataset.mode = 'basics';
  tutCardText(['Learn <em>the basics?</em>', 'A quick training match shows you how to roll, fling, pound and dodge. Or skip it and jump straight in.', 'Teach me', 'Just play']);
  el.hidden = false; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); tutCardCoach(); AU.bloop(0.55); menu.classList.add('tutoring'); setTimeout(() => $('tgGo').focus({ preventScroll: true }), 60);
}
function tutBasicsPick(learn) {
  const el = $('tutGo'); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = '';
  if (learn) { start(); return; } // (the training match, as Play does while it's due)
  tutSkipAll(); setTimeout(() => { if (state === 'menu' && menuPage === 'home' && !building) playEvents(); }, 200);
}
// skipped: the onboarding is over, nothing taught and nothing owed (no lesson, no shop trip, no later scripts or cards)
function tutSkipAll() {
  store.tut.skipped = 1; store.tut.m3 = 2; store.tut.comms = 1; store.tut.modes = 1; store.tut.trySd = 1; delete store.tut.price;
  tutSet('done'); save(); tutHide(); menu.classList.remove('tutoring');
}
"""

def apply(s):
    # saves partway through: past the forced shop and locker steps, and no third-match script
    s = rep(s, "if (!store.tut || typeof store.tut !== 'object' || !store.tut.ph) store.tut = { ph: (store.runs || 0) > 0 ? 'done' : 'match' };",
            "if (!store.tut || typeof store.tut !== 'object' || !store.tut.ph) store.tut = { ph: (store.runs || 0) > 0 ? 'done' : 'match' };\n"
            "if (store.tut.ph === 'shop' || store.tut.ph === 'locker') { store.tut.ph = 'match2'; delete store.tut.price; } if (store.tut.m3 === 1) store.tut.m3 = 2; // (v441: nothing forced, no Giant script)")
    # the question in place of the pointer at Play
    s = rep(s, "tutShow('Hey, rookie! Ready to roll? Your first match is a little training session.', 'homePlay', 'first');",
            "{ tutHide(); tutBasicsCard(); } /* (v441: learn the basics, or just play) */")
    s = rep(s, "$('tgGo').addEventListener('click', () => { AU.init(); AU.ui(); const m = $('tutGo').dataset.mode; if (m === 'welcome')",
            "$('tgGo').addEventListener('click', () => { AU.init(); AU.ui(); const m = $('tutGo').dataset.mode; if (m === 'basics') return tutBasicsPick(true); if (m === 'welcome')")
    s = rep(s, "$('tgLater').addEventListener('click', () => { AU.init(); AU.ui(); if ($('tutGo').dataset.mode === 'modes')",
            "$('tgLater').addEventListener('click', () => { AU.init(); AU.ui(); if ($('tutGo').dataset.mode === 'basics') return tutBasicsPick(false); if ($('tutGo').dataset.mode === 'modes')")
    i = s.index("function tutWelcome() {"); s = s[:i] + CARD.lstrip('\n') + s[i:]
    # Skip tutorial (the lesson's pause): skipped the same way, nothing handed out, no equip lesson
    s = rep(s, "for (const id of ['flower', 'fangs']) { OWNED.add(id); BOUGHT.add(id); } store.owned = [...OWNED]; store.bought = [...BOUGHT]; store.fresh = [...new Set([...(store.fresh || []), 'flower', 'fangs'])];\n"
               "  newItem = null; delete store.tut.price; store.tut.skipped = 1; tutSet('locker'); save(); toMenu();",
            "newItem = null; tutSkipAll(); toMenu(); /* (v441: skipped like Just play) */")
    # after the lesson: no forced shop trip (no half-price flower, no fangs sale); the next match is the second lesson match
    s = rep(s, "store.tut.price = { flower: Math.max(1, Math.round((endInfo.drops || 0) / 2)) }; // (half what this match paid)", "")
    s = rep(s, "endInfo.lesson = true; tutSet('shop'); save(); tutWinDue = true; return;", "endInfo.lesson = true; tutSet('match2'); save(); tutWinDue = true; return; /* (v441: no shop trip) */")
    # second match: no slingshot reminder; and no third-match Giant script after it
    s = rep(s, "held: 0, ms: '', msT: 0, msN: 0 };", "held: 0, ms: 'done', msT: 0, msN: 0 }; /* (v441: no slingshot reminder) */")
    s = rep(s, "delete store.tut.price; store.tut.m3 = 1; tutSet('done');", "delete store.tut.price; store.tut.m3 = 2; tutSet('done'); /* (v441: no Giant script) */")
    # no slingshot pro tip in later matches
    s = rep(s, "function tutProTip() {", "function tutProTip() { if (tutTip && tutTip.key === 'protip') tutHide(); return; // (v441: no slingshot pro tip)\n")
    # no Ol' Bloop cards in the lobby at rank 3, and no match-end gate leading to them
    s = rep(s, "function tutStrokesDue() { return $('friendsModal').hidden &&", "function tutStrokesDue() { return false && $('friendsModal').hidden &&")
    s = rep(s, "function tutCommsDue() { return $('friendsModal').hidden &&", "function tutCommsDue() { return false && $('friendsModal').hidden &&")
    s = rep(s, "const due = tutPh() === 'done' && ((!store.tut.strokes && strokesDue()) || (!store.tut.comms && commsDue()))", "const due = false")
    # every mode open from the start (Play online has its own lock)
    s = rep(s, "evUnlocked = () => repOf(store.xp || 0).lv >= ABIL_RANK;", "evUnlocked = () => true; /* (v441: every mode open from the start) */")
    # the flower and the fangs: cheap, and both in the shop from the start
    s = rep(s, "flower: 145,", "flower: 25,")
    s = rep(s, "fangs: 400,", "fangs: 40,")
    s = rep(s, "const OUTRIGHT = new Set(['flower', ", "const OUTRIGHT = new Set(['flower', 'fangs', ")
    return s
