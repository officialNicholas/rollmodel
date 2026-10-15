"""v286: the starting transforms (the item you hold as every match begins) are earned now, like the strokes.

- In the order they open up: Roller, Turret, Paint Trap, Whirlwind (the Turret and the Paint Trap swap places).
- The Roller is yours from the start. Each of the others opens at a rank (Turret 3, Paint Trap 5, Whirlwind 7) and is then crafted on
  the bench like a stroke (10, 15 and 20 minutes, one craft at a time, Skip as before). Until then its tile and card show the rank it
  opens at, then its craft time; once crafted it's yours to equip.
- A save from before keeps the one you had equipped (as when skills became crafted); the rest go to the bench.
- A newly crafted one puts a dot on the Transform slot, as a new stroke or skill does on theirs."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

ORDER = """Leaves a wide trail and ends in a burst. Steer as you go'] }); // (v271)
// (v286) in the order they open up: the Roller yours from the start, each of the others from a rank and then crafted on the bench
{ const R = { roller: [1, 0], turret: [3, 10], trap: [5, 15], whirl: [7, 20] }; ST_ITEMS.sort((a, b) => R[a.id][0] - R[b.id][0]); for (const o of ST_ITEMS) { o.rank = R[o.id][0]; if (R[o.id][1]) o.craft = R[o.id][1]; } }"""

def apply(s):
    s = rep(s, "Leaves a wide trail and ends in a burst. Steer as you go'] }); // (v271)", ORDER)
    s = rep(s, "const ST_STARTERS = ['rocket', 'swim'];", "const ST_STARTERS = ['rocket', 'swim', 'roller'];")
    # (a save from before: the transform you had on stays yours, the rest go to the bench; and only one you own can be on)
    s = rep(s, "if (!SKILLS.some(x => x.id === d.skill) || !d.own.includes(d.skill)) d.skill = 'swim'; if (!stIsItem(d.item)) d.item = 'roller'; return d; }",
               "if (!d.it286) { d.it286 = 1; if (stIsItem(d.item) && d.item !== 'roller' && !d.own.includes(d.item)) d.own.push(d.item); } /* (v286: transforms are crafted now; the one you had on stays yours) */"
               " if (!SKILLS.some(x => x.id === d.skill) || !d.own.includes(d.skill)) d.skill = 'swim'; if (!stIsItem(d.item) || !d.own.includes(d.item)) d.item = 'roller'; return d; }")
    s = rep(s, "const strokeOwned = id => stIsItem(id) || strokesOf().own.includes(id)",
               "const stRank = o => stIsItem(o.id) ? (o.rank || 1) : ABIL_RANK, stDue = o => repOf(store.xp || 0).lv >= stRank(o); // (v286: a transform opens at its own rank)\n"
               "const strokeOwned = id => strokesOf().own.includes(id)")
    # the tiles
    s = rep(s, "own = item || d.own.includes(o.id)", "own = d.own.includes(o.id)")
    s = rep(s, "lock = !own && !cr && !strokesDue();", "lock = !own && !cr && !stDue(o);")
    s = rep(s, "lock ? 'locked until rank ' + ABIL_RANK : 'craft it in '", "lock ? 'locked until rank ' + stRank(o) : 'craft it in '")
    s = rep(s, "(item || ST_STARTERS.includes(o.id) ? 'Yours' : 'Owned')", "(ST_STARTERS.includes(o.id) ? 'Yours' : 'Owned')")
    s = rep(s, "STROKE_LOCK + 'Rank ' + ABIL_RANK + '</span>'", "STROKE_LOCK + 'Rank ' + stRank(o) + '</span>'")
    # the card
    s = rep(s, "own = item || d.own.includes(id)", "own = d.own.includes(id)")
    s = rep(s, "busy = !!d.craft && !cr, due = strokesDue();", "busy = !!d.craft && !cr, due = stDue(o);")
    s = rep(s, "item || ST_STARTERS.includes(id) ? 'Yours' : 'Crafted'", "ST_STARTERS.includes(id) ? 'Yours' : 'Crafted'")
    s = rep(s, "!due ? 'Reach rank ' + ABIL_RANK + ' to craft it'", "!due ? 'Reach rank ' + stRank(o) + ' to craft it'")
    s = rep(s, "if (!strokesDue()) { AU.nope(); stToast('Reach rank ' + ABIL_RANK + ' to craft ' + spName(id)); return; }",
               "if (!stDue(stDef(id))) { AU.nope(); stToast('Reach rank ' + stRank(stDef(id)) + ' to craft ' + spName(id)); return; }")
    s = rep(s, "function equipItem(id) { const d = strokesOf(); if (!stIsItem(id) || d.item === id) return;",
               "function equipItem(id) { const d = strokesOf(); if (!stIsItem(id) || !d.own.includes(id) || d.item === id) return;")
    s = rep(s, "for (const k of ['special', 'skill']) $(ST_CATS[k].slot).classList.toggle('fresh'", "for (const k of ['special', 'skill', 'item']) $(ST_CATS[k].slot).classList.toggle('fresh'")
    return s
