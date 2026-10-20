"""v404 small asks:

- Strokes: the start-of-match pick-up tab says "Starters" (was "Transforms"); its cards say Starter (the user: 'change
  "Transforms" to "Starters" under strokes').
- The Whirlwind turns all the way through its wind-up (the user: "I should be able to curve or turn the whirlwind as long as it
  hasn't started yet"). The glint still comes at the same moment, as the warning to rivals, but your lane keeps following your
  turn until the dash; a CPU's still locks at the glint.
- The results' character pictures (the user: a free-for-all's results showed the drawn 2D faces): a portrait that came out
  empty (the graphics busy a moment) tried twice more at once and then gave up, and three of those in a whole session turned
  the pictures off for good, so every results page after showed the drawn faces. Now an empty one waits a moment between tries
  (up to five), a portrait that works clears the count, the pictures switch off only after six failures in a row, and they
  come back on after twenty seconds. A portrait that failed is made again the next time it's wanted.
- Paint Storm opens at rank 5 (the user: "make paint storm unlock after level 5"); the other strokes at rank 2 as before.
- The "Harsh critics" commission says "Win with the CPU on harsh" (the user; the title stays)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, 'aria-controls="stItemRail"><b class="sgtt">Transforms</b>', 'aria-controls="stItemRail"><b class="sgtt">Starters</b>')
    s = rep(s, "item: { h: 'Transforms', s: 'You start every match holding it', rail: 'stItemRail', slot: 'stItem', kind: 'Transform' }",
               "item: { h: 'Starters', s: 'You start every match holding it', rail: 'stItemRail', slot: 'stItem', kind: 'Starter' }")
    # the whirlwind: the player turns it until the dash
    s = rep(s, "  else { if (W.lock === undefined) { W.lock = D.yaw; W.len = whirlLaneLay(D, D.x, D.z, D.y, W.lock); whirlGlint(D, W); } D.yaw = W.lock; }",
               "  else { if (W.lock === undefined) { W.lock = D.yaw; W.len = whirlLaneLay(D, D.x, D.z, D.y, W.lock); whirlGlint(D, W); }\n"
               "    if (D.ai) D.yaw = W.lock; else if (Math.abs(wrapA(D.yaw - W.lock)) > 0.002) { W.lock = D.yaw; W.len = whirlLaneLay(D, D.x, D.z, D.y, D.yaw); } } // (v404: yours turns until it goes)")
    # portraits: patient retries, a success clears the count, back on after a while
    s = rep(s, "    if (n < 20) { if ((j.tries = (j.tries || 0) + 1) < 3) { PT.jobs.push(j); return; } throw new Error('empty portrait'); }",
               "    if (n < 20) { if ((j.tries = (j.tries || 0) + 1) < 5) { PT.jobs.push(j); PT.cool2 = 20; return; } throw new Error('empty portrait'); } // (v404: tried again after a moment, five times)")
    s = rep(s, "    j.url = await ptEncode(buf); PT.n++;\n  } catch (e) { j.fail = true; if (++PT.errs >= 3) PT.fail = true; try { console.warn('portrait:', e); } catch (x) {} }\n  finally { PT.busy = false; PT.cool = 2; ptSweep(); }",
               "    j.url = await ptEncode(buf); PT.n++; PT.errs = 0;\n  } catch (e) { j.fail = true; PT.map.delete(j.k); if (++PT.errs >= 6) { PT.fail = true; setTimeout(() => { PT.fail = false; PT.errs = 0; }, 20000); } try { console.warn('portrait:', e); } catch (x) {} } // (v404: made again when next wanted; off for a while only after six in a row)\n  finally { PT.busy = false; PT.cool = Math.max(2, PT.cool2 || 0); PT.cool2 = 0; ptSweep(); }")
    s = rep(s, "d: 'Win with the critics on harsh'", "d: 'Win with the CPU on harsh'")
    s = rep(s, "stRank = o => stIsItem(o.id) ? (o.rank || 1) : ABIL_RANK,", "stRank = o => stIsItem(o.id) ? (o.rank || 1) : o.rank || ABIL_RANK,")
    s = rep(s, "SPECIALS.push({ id: 'storm', name: 'Paint Storm', desc:", "SPECIALS.push({ id: 'storm', rank: 5, name: 'Paint Storm', desc:")
    return s
