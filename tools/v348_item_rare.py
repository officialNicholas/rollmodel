"""v348: the Whirlwind and the Boomerang come up less: 12% of the time each (8 points under the 20% they had).

- Pick-ups still come in shuffled turns (v347), but only the Roller, the Turret and the Paint Trap are in every turn. The Whirlwind and
  the Boomerang are each in a turn a little under half the time (47%), so each makes up 12% of what comes up, and the other three about
  25% each. With a chance p for each of the two, a turn holds 3 + 2p kinds on average, so each one's share is p / (3 + 2p): 12% at
  p = 0.36 / 0.76.
- The turns now run on from one match to the next instead of starting over each match, so the shares hold whatever the match lengths
  (a fresh turn each match would favour whatever comes first in a turn). Never the same kind twice in a row, and an untaken pick-up's
  swap brings a different kind, as before. The first lesson is unchanged."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "// (v347) which kind comes up next: outside the first lesson, all five in turn, shuffled, so each one comes up before any comes again\n"
               "// (and never the same kind twice in a row); not: the next in the turn that isn't that kind. The first lesson keeps to rollers, and\n"
               "// turrets once the flower's found\n"
               "const ITEM_KINDS = ['roller', 'turret', 'trap', 'whirl', 'boom'];\n"
               "function itemTurn(not) {\n"
               "  const IS = itemSpawn, B = IS.bag || (IS.bag = []);\n"
               "  const more = () => { const ks = ITEM_KINDS.slice(); for",
               "// (v347) which kind comes up next: outside the first lesson, in turns, shuffled, so each one in a turn comes up before any comes again\n"
               "// (and never the same kind twice in a row); not: the next in the turn that isn't that kind. The first lesson keeps to rollers, and\n"
               "// turrets once the flower's found. (v348) The Roller, the Turret and the Paint Trap are in every turn, the Whirlwind and the Boomerang\n"
               "// each in a turn with a chance p (ITEM_RARE_P): a turn holds 3 + 2p kinds on average, so each of the two makes up p / (3 + 2p) of what\n"
               "// comes up, 12% (it was 20%), and the other three about 25%. The turns run on from one match to the next, so the shares hold\n"
               "const ITEM_KINDS = ['roller', 'turret', 'trap', 'whirl', 'boom'], ITEM_RARE = ['whirl', 'boom'], ITEM_RARE_SHARE = 0.12,\n"
               "  ITEM_RARE_P = (ITEM_KINDS.length - ITEM_RARE.length) * ITEM_RARE_SHARE / (1 - ITEM_RARE.length * ITEM_RARE_SHARE);\n"
               "function itemTurn(not) {\n"
               "  const IS = itemSpawn, B = IS.bag || (IS.bag = []);\n"
               "  const more = () => { const ks = ITEM_KINDS.filter(k => !ITEM_RARE.includes(k) || Math.random() < ITEM_RARE_P); for")
    s = rep(s, "itemSpawn.last = null; itemSpawn.bag = []; // (v347)", "itemSpawn.last = null; // (v348: the turns of pick-ups run on from one match to the next)")
    return s
