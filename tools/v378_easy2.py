"""v378: the second match (the first after the lesson) is always on easy, with no CPU difficulty anywhere; the choice turns up once it's done.

- From the locker lesson's end (the tutorial's 'vote' step) until the second match has been played to the end ('match2' done), the CPUs
  play on easy whatever was saved, and the difficulty is nowhere to be seen: not on the vote page (its heading and its switch), not on
  the lobby's Canvases card ("Versus" rather than "Versus · CPU fair"), not on the versus card before the match. A second match left
  part way through is still the second match.
- Once it's done, the difficulty you had saved (medium for a new player) comes back, and the vote page shows the switch again."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "let diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';\n",
               "let diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';\n"
               "// (v378) the second match (from the locker lesson's end until it's played through): easy, and no difficulty shown anywhere\n"
               "const diffLock = () => { const p = store.tut && store.tut.ph; return p === 'vote' || p === 'match2'; };\n"
               "let diffLocked = false;\n"
               "function diffSync() { const on = diffLock(); document.documentElement.classList.toggle('difflock', on);\n"
               "  if (on) diff = 'easy'; else if (diffLocked) diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';\n"
               "  diffLocked = on; }\n"
               "diffSync();\n")
    s = rep(s, "const tutPh = () => store.tut.ph, tutSet = ph => { if (store.tut.ph === ph) return; store.tut.ph = ph; save(); };",
               "const tutPh = () => store.tut.ph, tutSet = ph => { if (store.tut.ph === ph) return; store.tut.ph = ph; save(); diffSync(); }; // (v378: the second match's easy comes and goes with its steps)")
    s = rep(s, "$('stages').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return;",
               "$('stages').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || diffLock()) return;")
    s = rep(s, "md[1] + ' \\u00b7 CPU ' + (CRITICS[diff] || 'fair').toLowerCase();\n",
               "md[1] + (diffLock() ? '' : ' \\u00b7 CPU ' + (CRITICS[diff] || 'fair').toLowerCase()); // (v378: none in the second match)\n")
    s = rep(s, "(NM ? md[1] + ', online' : md[1] + ', CPU ' + (CRITICS[diff] || 'fair').toLowerCase())",
               "(NM ? md[1] + ', online' : diffLock() ? md[1] : md[1] + ', CPU ' + (CRITICS[diff] || 'fair').toLowerCase())")
    s = rep(s, "/* CPU difficulty: a heading between two fine rules, one dark switch, the pick on cream paper */\n",
               "/* CPU difficulty: a heading between two fine rules, one dark switch, the pick on cream paper */\n"
               "html.difflock #stages,html.difflock #wDiffHd{display:none!important} /* (v378: not in the second match) */\n")
    return s
