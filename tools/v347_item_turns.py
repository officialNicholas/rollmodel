"""v347: every pick-up comes up, from your second match on, whatever your rank.

- Which pick-up came up next was a weighted draw (the Roller most likely, the kind just seen less likely), and the onboarding's second
  and third matches, like the first lesson, only ever put out Rollers and Turrets. Now, outside the first lesson, the kinds come in
  turns: all five (Roller, Turret, Paint Trap, Whirlwind, Boomerang) in a shuffled order, so every one comes up before any comes again,
  and never the same kind twice in a row. A new match starts a new turn.
- An untaken pick-up's swap (v310) still brings a different kind: the next one in the turn that isn't it.
- The first lesson keeps its Rollers (and Turrets once the flower's found). Online matches have no pick-ups, as before, and the item you
  start a match holding is still the one equipped on the Strokes page (the Roller until others are crafted)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const itemType = () => tut && tut.noTurret ? 'roller' : (tut || tut2 || tut3) ? (itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret')) : (() => { const w = { roller: 0.42, turret: 0.3, trap: 0.28, whirl: 0.3, boom: 0.3 }; if (w[itemSpawn.last]) w[itemSpawn.last] *= 0.45; const ks = Object.keys(w); let r = Math.random() * ks.reduce((q, k) => q + w[k], 0); for (const k of ks) if ((r -= w[k]) <= 0) return k; return 'roller'; })();\n",
               "// (v347) which kind comes up next: outside the first lesson, all five in turn, shuffled, so each one comes up before any comes again\n"
               "// (and never the same kind twice in a row); not: the next in the turn that isn't that kind. The first lesson keeps to rollers, and\n"
               "// turrets once the flower's found\n"
               "const ITEM_KINDS = ['roller', 'turret', 'trap', 'whirl', 'boom'];\n"
               "function itemTurn(not) {\n"
               "  const IS = itemSpawn, B = IS.bag || (IS.bag = []);\n"
               "  const more = () => { const ks = ITEM_KINDS.slice(); for (let i = ks.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)), t = ks[i]; ks[i] = ks[j]; ks[j] = t; }\n"
               "    if (ks[0] === (B.length ? B[B.length - 1] : IS.last)) ks.push(ks.shift()); B.push(...ks); };\n"
               "  if (!B.length) more(); let i = not ? B.findIndex(k => k !== not) : 0; if (i < 0) { more(); i = B.findIndex(k => k !== not); }\n"
               "  return B.splice(i, 1)[0];\n"
               "}\n"
               "const itemType = () => tut && tut.noTurret ? 'roller' : tut ? (itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret')) : itemTurn();\n")
    s = rep(s, "function itemTypeNot(t) { for (let k = 0; k < 12; k++) { const q = itemType(); if (q !== t) return q; } return ['roller', 'turret', 'trap', 'whirl', 'boom'].find(q => q !== t); }",
               "function itemTypeNot(t) { return tut ? (t === 'roller' ? 'turret' : 'roller') : itemTurn(t); } // (v347: the next in the turn)")
    # a new match starts a new turn
    s = rep(s, "powers = []; itemSpawn.t = 6 + Math.random() * 3; itemSpawn.last = null;", "powers = []; itemSpawn.t = 6 + Math.random() * 3; itemSpawn.last = null; itemSpawn.bag = []; // (v347)")
    s = rep(s, "const type = itemType(); // (the lessons keep to rollers and turrets) // (the lesson: rollers only until the flower is found)",
               "const type = itemType(); // (the first lesson: rollers only until the flower is found, then turrets too; v347: otherwise all five in turn)")
    return s
