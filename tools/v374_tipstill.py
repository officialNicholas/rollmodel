"""v374: Ol' Bloop's plate over a control holds still for real, and no "Giant it is!" after the Giant.

- The flicker on the Paint Shop page ("All yours! Now open your locker" going round three places, a few frames each: over the tabs,
  under them, and off the top of the screen with only the hand showing). In a match his line sits docked by his corner, held there by
  its bottom (tutPlace sets the plate's inline bottom). Every other place clears the plate's inline style as it takes over, but the
  place over a control (above or below it) only ever set its left and top, so after the lesson match that bottom stayed on, through the
  new items, the shop's tips and the locker's. Held by both its top and that bottom, the plate's box stretched down to it: its measured
  height came out of where it had been put the frame before, which moved where it went next, round and round (v362's hold only slowed
  that down to three frames a place). Now the place over a control drops a bottom left on the plate, and measures the plate itself (or
  the callout), never the box round it, so nothing about where it was put can feed back into where it goes.
- Once the Giant is equipped in Strokes, the lesson ends there: Ol' Bloop's closing line ("Giant it is! Grab the orb in a match and go
  big. Skills and transforms have their own tabs", five seconds) is gone.
- The craft's wait in the lesson: Ol' Bloop says "Crafting takes 20 minutes. You can skip the wait!" (it said "Tap Skip and watch a
  quick ad"), and Back is the other way out: leaving the page while the Giant crafts ends the lesson (the Giant finishes on its own),
  where he used to keep pointing you back at Strokes until the 20 minutes were up."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the plate over a control: no bottom left on it from the match, and its own height measured, not its box's
    s = rep(s, "  const r = el.getBoundingClientRect(), cx = r.left - r0.left + r.width * (lookOpen && el.classList.contains('lcat') ? 0.28 : 0.5), cw = Math.min(tutEl.offsetWidth, viewW - 24); /* (a locker category card: the hand on its left part, clear of the name pill) */\n",
               "  // (v374) placed by its top alone, and measured by the plate itself (or the callout), never by the box round it: in a match the plate\n"
               "  // sits docked by his corner, held by its bottom, and a bottom left on it here stretched its box down to that, so the height measured\n"
               "  // came from where it had been put the frame before, and it went round three places (on the Paint Shop page after the lesson: over\n"
               "  // the tabs, under them, and off the top with only the hand showing)\n"
               "  if (tutEl.style.bottom) tutEl.style.bottom = '';\n"
               "  const r = el.getBoundingClientRect(), cx = r.left - r0.left + r.width * (lookOpen && el.classList.contains('lcat') ? 0.28 : 0.5), cw = Math.min(tutEl.offsetWidth, viewW - 24); /* (a locker category card: the hand on its left part, clear of the name pill) */\n")
    s = rep(s, "  const ph = tutEl.offsetHeight + over, roomUp = r.top - r0.top,",
               "  const ph = (tutTip.call ? tutCall : tutBust.parentNode).offsetHeight + over, roomUp = r.top - r0.top,")
    # ---- the Giant equipped: the lesson ends there, with no closing line
    s = rep(s, "  if (!tutSDone) { tutSDone = performance.now(); tutShow('Giant it is! Grab the orb in a match and go big. Skills and transforms have their own tabs', null, 'sDone', false, true, null, false, true); }\n"
               "  else if (performance.now() - tutSDone > 5200) tutStrokesEnd();\n",
               "  tutStrokesEnd(); // (v374: equipped, that's the lesson: no closing line from him)\n")
    s = rep(s, "function tutStrokesEnd() { $('mStrokes').classList.remove('sglearn'); tutSDone = 0; store.tut.strokes = 1;",
               "function tutStrokesEnd() { $('mStrokes').classList.remove('sglearn'); store.tut.strokes = 1;")
    s = rep(s, "let tutStrokesAt = 0, tutSDone = 0, tutCommsAt = 0,", "let tutStrokesAt = 0, tutCommsAt = 0,")
    # ---- the craft's wait: skipping it is up to you, and Back is the way out of it
    s = rep(s, "return tutShow('Crafting takes 20 minutes. Tap Skip and watch a quick ad',",
               "return tutShow('Crafting takes 20 minutes. You can skip the wait!',")
    s = rep(s, "  if (!strokesOpen()) return tutShow('Tap Strokes to open it', 'abilBtn', 'sOpen');\n",
               "  if (!strokesOpen() && strokesOf().craft && strokesOf().craft.id === 'giant') return tutStrokesEnd(); // (v374: Back out of the wait rather than Skip it: the lesson's over, the Giant finishes on its own)\n"
               "  if (!strokesOpen()) return tutShow('Tap Strokes to open it', 'abilBtn', 'sOpen');\n")
    # ---- no "Look at you, rookie!" card: the Strokes lesson opens on "Let's learn some more" (with the first card's fanfare and its marks)
    s = rep(s, "// strokes: once you're rank 3 (and the first lessons are done), Ol' Bloop stops you in the lobby: look how far you've come; then let's\n"
               "// learn some more: the Strokes page, the Giant crafted (Skip, this one's on him) and equipped\n",
               "// strokes: once you're rank 3 (and the first lessons are done), Ol' Bloop stops you in the lobby: let's learn some more (v374: no\n"
               "// \"look how far you've come\" card first): the Strokes page, the Giant crafted and equipped\n")
    s = rep(s, "function tutStrokesCard(n) {\n"
               "  const el = $('tutGo'); el.dataset.mode = 'strokes' + n;\n"
               "  if (n === 1) tutCardText(['Look at <em>you</em>, rookie!', 'Rank ' + repOf(store.xp || 0).lv + ' already. You’ve come a long way since that first canvas, and I’ve been watching.', 'Aw, thanks', '']);\n"
               "  else tutCardText(['Let’s learn <em>some more</em>', 'Strokes, Time trial and Showdown are unlocked. Let’s start with Strokes.', 'Show me', '']);\n"
               "  if (el.hidden) { el.hidden = false; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); } tutCardCoach(); if (n === 1) { store.evNew = { solo: 1, showdown: 1 }; AU.fanfare && AU.fanfare(); AU.bloop(0.55); menu.classList.add('tutoring'); } else AU.bloop(0.5); setTimeout(() => $('tgGo').focus({ preventScroll: true }), 60);\n",
               "function tutStrokesCard() {\n"
               "  const el = $('tutGo'); el.dataset.mode = 'strokes2';\n"
               "  tutCardText(['Let’s learn <em>some more</em>', 'Strokes, Time trial and Showdown are unlocked. Let’s start with Strokes.', 'Show me', '']);\n"
               "  if (el.hidden) { el.hidden = false; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); } tutCardCoach(); store.evNew = { solo: 1, showdown: 1 }; AU.fanfare && AU.fanfare(); AU.bloop(0.55); menu.classList.add('tutoring'); setTimeout(() => $('tgGo').focus({ preventScroll: true }), 60);\n")
    s = rep(s, "function tutStrokesGo() { const el = $('tutGo'), m = el.dataset.mode; if (m === 'strokes1') return tutStrokesCard(2); el.classList.remove('on');",
               "function tutStrokesGo() { const el = $('tutGo'); el.classList.remove('on');")
    s = rep(s, "if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(1); return; } else tutStrokesAt = 0; /* (a beat of the lobby, then the praise;",
               "if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(); return; } else tutStrokesAt = 0; /* (a beat of the lobby, then the card;")
    return s
