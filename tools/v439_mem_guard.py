"""v439: no false "ran short of memory" note, and none at all on a phone with memory to spare.

The v430 guard took any match that never ended as the page having been closed for want of memory, and stepped Visuals down to
Performance with a note in the lobby. A match is also left unfinished when the app is swiped away from the app switcher, when the
phone restarts or the app is updated, and the game's own restart when the graphics are lost after a trip away counted too. So the note
came up on phones that had plenty of memory (an iPhone Air, with 12 GB).

- In the iPhone app, only the app's word counts: it now tells the game when iOS closed the page while the game was on screen
  (__NATIVE.crash, from GameViewController). A match left unfinished and the graphics restart no longer count. In a browser the
  unfinished match still counts (there's nothing better there).
- A phone with 6 GB of memory or more (or a computer) never has its visuals stepped down and never sees the note: one closed page there
  isn't the visuals' doing.
- Such a phone that was stepped down before (the visuals moved to Performance by the guard, not picked in Settings) gets its visuals
  back, once.
- Picking Visuals in Settings is remembered as the player's own choice, which is never undone."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

OLD = """  const L = JSON.parse(localStorage.getItem('rm.live') || 'null'), C = JSON.parse(localStorage.getItem('rm.crashed') || 'null');
  localStorage.removeItem('rm.live'); localStorage.removeItem('rm.crashed');
  const hit = L && Date.now() - L.t < 10 * 60000 ? L : C && Date.now() - C.t < 10 * 60000 ? C : null; if (!hit) return null;
"""
NEW = """  const L = JSON.parse(localStorage.getItem('rm.live') || 'null');
  localStorage.removeItem('rm.live'); localStorage.removeItem('rm.crashed');
  // (v439) room to spare: 6 GB or more (an iPhone Air has 12), or a computer. A page closed there isn't the visuals' doing
  const roomy = NATIVE ? +NATIVE.memGB >= 6 : DEV_TIER >= 3;
  if (roomy && !store.memFix439) { store.memFix439 = 1; // (once: visuals the old guard stepped down come back, never the player's own pick)
    if (store.memCrash && !store.gfxUser) { if (store.gfx === 'perf') delete store.gfx; delete store.lowMem; }
    localStorage.setItem(KEY, JSON.stringify(store)); localStorage.setItem(KEY + '.t', String(Date.now())); }
  // (v439) in the app only its word counts: iOS closed the page while the game was on screen. Not a match left unfinished (the app
  // swiped away, the phone restarted, an update) nor the restart after the graphics were lost. A browser has only the stamp
  const hit = NATIVE ? (NATIVE.crash && NATIVE.crash.onScreen ? NATIVE.crash : null) : L && Date.now() - L.t < 10 * 60000 ? L : null;
  if (!hit || roomy) return null;
"""

def apply(s):
    s = rep(s, OLD, NEW)
    s = rep(s, "store.gfx = gfxPick; save();", "store.gfx = gfxPick; store.gfxUser = 1; save();")
    return s
