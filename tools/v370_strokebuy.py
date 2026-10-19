"""v370: strokes bought with dabs, not crafted. All but the Giant.

- The special strokes, skills and transforms that were crafted on a timer (with Skip as a rewarded ad) are bought outright with dabs now,
  like the Paint Shop's pieces: Flash Freeze; Weather Repel and Deep Pockets; the Turret, Paint Trap, Whirlwind and Boomerang. They cost
  20 dabs for each minute their craft took: Turret 200, Weather Repel 300, Paint Trap 300, Deep Pockets 400, Whirlwind 400, Flash
  Freeze 500, Boomerang 500 (a live price from the dashboard wins, as in the Paint Shop). The transforms still open at their ranks first.
- The Giant is still crafted: it's Ol' Bloop's lesson (Craft, then Skip with a quick ad, then Equip), and it stays free.
- The button says Buy and the price when you can pay, the price alone (greyed, with "You need N more dabs" under it) when you can't, and
  the rank while it's locked. A tag shows its price where it showed the craft time. Buying puts it on straight away.
- The Strokes page shows your dabs where it showed your rank (top right), as the Locker does; while the Giant is on the bench it shows
  its countdown, as before.
- A stroke on the bench when this arrives (anything but the Giant) is finished there and then: it's yours."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

PRICES = "{ turret: 200, repel: 300, trap: 300, pockets: 400, whirl: 400, freeze: 500, boom: 500 }"

def apply(s):
    # the prices, and the strokes that carry one aren't crafted any more
    a = "{ const R = { roller: [1, 0], turret: [3, 10], trap: [5, 15], whirl: [7, 20], boom: [9, 25] }; ST_ITEMS.sort((a, b) => R[a.id][0] - R[b.id][0]); for (const o of ST_ITEMS) { o.rank = R[o.id][0]; if (R[o.id][1]) o.craft = R[o.id][1]; } }"
    s = rep(s, a, a + "\n"
               "// (v370) bought with dabs, not crafted: every stroke but the Giant (Ol' Bloop's lesson crafts that one), at 20 dabs for each minute\n"
               "// its craft took. A live price from the dashboard wins, as in the Paint Shop\n"
               "const ST_PRICE = " + PRICES + ";\n"
               "for (const o of [...SPECIALS, ...SKILLS, ...ST_ITEMS]) if (ST_PRICE[o.id]) { o.price = ST_PRICE[o.id]; delete o.craft; }\n"
               "const stBuys = o => !!(o && o.price), stPrice = o => { const lp = stLive(o.id); return lp >= 0 ? lp : o.price; };")

    # a save with one of them on the bench: done now, it's yours
    a = "  if (!d.it286) { d.it286 = 1;"
    s = rep(s, a, "  if (!d.b370) { d.b370 = 1; if (d.craft && ST_PRICE[d.craft.id]) { if (!d.own.includes(d.craft.id)) d.own.push(d.craft.id); d.fresh = d.craft.id; d.craft = null; } } // (v370: what was on the bench when strokes went on sale is done)\n" + a)

    # buying one: the dabs paid, it's yours and it goes on
    a = "function equipSpecial(id) {"
    s = rep(s, a, "// (v370) buying a stroke: the dabs paid, and it's yours and on straight away\n"
                  "function stBuy(id) {\n"
                  "  const d = strokesOf(), o = stDef(id); if (!stBuys(o) || d.own.includes(id)) return;\n"
                  "  if (!stDue(o)) { AU.nope(); hap('error'); kick($('sgDo'), 'nope'); stToast('Reach rank ' + stRank(o) + ' to buy ' + spName(id)); return; }\n"
                  "  const p = stPrice(o), n = store.drops || 0; if (n < p) { AU.nope(); hap('error'); kick($('sgDo'), 'nope'); stToast('You need ' + (p - n) + ' more dabs'); return; }\n"
                  "  store.drops = n - p; d.own.push(id); if (d.fresh === id) d.fresh = null; stEv({ k: 'buy', i: id, p }); save(); showDrops();\n"
                  "  sgEquip(id); AU.power(); hap('success'); kick($('sgBadge'), 'bump');\n"
                  "  stToast('Bought! ' + o.name + ' is ' + (stIsItem(id) ? 'your starting transform' : stIsSkill(id) ? 'your skill' : 'your special stroke'));\n"
                  "}\n" + a)

    # a tag: its price where it showed the craft time
    s = rep(s, "  const st = on ? 'equipped' : cr ? 'crafting, ' + mmss(craftLeft()) + ' left' : own ? (ST_STARTERS.includes(o.id) ? 'yours' : 'owned') : lock ? 'locked until rank ' + stRank(o) : 'craft it in ' + o.craft + ' minutes';",
               "  const st = on ? 'equipped' : cr ? 'crafting, ' + mmss(craftLeft()) + ' left' : own ? (ST_STARTERS.includes(o.id) ? 'yours' : 'owned') : lock ? 'locked until rank ' + stRank(o) : stBuys(o) ? stPrice(o) + ' dabs' : 'craft it in ' + o.craft + ' minutes';")
    s = rep(s, "  const foot = on ? 'Equipped' : cr ? '<b>' + mmss(craftLeft()) + '</b>' : !own && !lock ? o.craft + ' min' : '';",
               "  const foot = on ? 'Equipped' : cr ? '<b>' + mmss(craftLeft()) + '</b>' : !own && !lock ? (stBuys(o) ? DROP_SVG + stPrice(o) : o.craft + ' min') : ''; // (v370: a price)")

    # the info card: how you get it
    s = rep(s, "  const ow = $('stPopOwn'); ow.hidden = !own; ow.innerHTML = ST_CHECK + (on ? 'Equipped' : ST_STARTERS.includes(id) ? 'Yours' : 'Crafted');",
               "  const ow = $('stPopOwn'); ow.hidden = !own; ow.innerHTML = ST_CHECK + (on ? 'Equipped' : ST_STARTERS.includes(id) || stBuys(o) ? 'Yours' : 'Crafted');")
    s = rep(s, "  const how = ST_STARTERS.includes(id) ? 'Yours from the start' : own ? 'Crafted: it’s yours' : cr ? 'On the bench: ' + mmss(craftLeft()) + ' to go' : (item ? 'Opens at rank ' + stRank(o) + ', then craft it in ' + o.craft + ' minutes' : 'Craft it in ' + o.craft + ' minutes, from rank ' + stRank(o));",
               "  const how = ST_STARTERS.includes(id) ? 'Yours from the start' : own ? (stBuys(o) ? 'It’s yours' : 'Crafted: it’s yours') : cr ? 'On the bench: ' + mmss(craftLeft()) + ' to go'\n"
               "    : stBuys(o) ? (item ? 'Opens at rank ' + stRank(o) + ', then buy it for ' + stPrice(o) + ' dabs' : 'Buy it for ' + stPrice(o) + ' dabs, from rank ' + stRank(o)) // (v370)\n"
               "    : (item ? 'Opens at rank ' + stRank(o) + ', then craft it in ' + o.craft + ' minutes' : 'Craft it in ' + o.craft + ' minutes, from rank ' + stRank(o));")
    s = rep(s, "  $('sgHow').innerHTML = (own ? ST_CHECK : cr ? ST_GLASS : stDue(o) ? ST_HAMMER : STROKE_LOCK) + '<span>' + how + '</span>';",
               "  $('sgHow').innerHTML = (own ? ST_CHECK : cr ? ST_GLASS : stDue(o) ? (stBuys(o) ? DROP_SVG : ST_HAMMER) : STROKE_LOCK) + '<span>' + how + '</span>';")

    # the button: Buy and the price; the price alone, greyed, when you can't pay yet; the rank while it's locked
    s = rep(s, "  else if (!cr) { b.disabled = busy || !due;",
               "  else if (stBuys(o)) { const p = stPrice(o), can = due && (store.drops || 0) >= p; b.classList.toggle('craft', can); b.disabled = !can; // (v370)\n"
               "    b.innerHTML = '<span>' + (!due ? STROKE_LOCK + 'Rank ' + stRank(o) : can ? 'Buy<small>' + DROP_SVG + p + '</small>' : DROP_SVG + p) + '</span>';\n"
               "    b.setAttribute('aria-label', !due ? o.name + ' opens at rank ' + stRank(o) : can ? 'Buy ' + o.name + ' for ' + p + ' dabs' : o.name + ', ' + p + ' dabs'); }\n"
               "  else if (!cr) { b.disabled = busy || !due;")
    s = rep(s, "  const note = own ? '' : cr ? (adFree() ? '' : 'Watch an ad to finish it now') : !due ? 'Reach rank ' + stRank(o) + ' to craft it' : busy ? 'One craft at a time: ' + spName(d.craft.id) + ' is on the bench' : '';",
               "  const lack = stBuys(o) ? stPrice(o) - (store.drops || 0) : 0;\n"
               "  const note = own ? '' : cr ? (adFree() ? '' : 'Watch an ad to finish it now') : !due ? 'Reach rank ' + stRank(o) + ' to ' + (stBuys(o) ? 'buy' : 'craft') + ' it' : stBuys(o) ? (lack > 0 ? 'You need ' + lack + ' more dabs. Matches pay in dabs' : '') : busy ? 'One craft at a time: ' + spName(d.craft.id) + ' is on the bench' : '';")
    s = rep(s, "  if (d.own.includes(id)) { if (stOnOf(stCat) !== id) sgEquip(id); return; }",
               "  if (d.own.includes(id)) { if (stOnOf(stCat) !== id) sgEquip(id); return; }\n"
               "  if (stBuys(o)) return stBuy(id); // (v370)")

    # the badge: your dabs, as the Locker shows them (the bench's countdown while the Giant's on it)
    s = rep(s, "  else { if ($('sgBadgeI').dataset.k !== 'rank') { $('sgBadgeI').dataset.k = 'rank'; $('sgBadgeI').innerHTML = SG_RANK; } $('sgBadgeT').textContent = lv; b.setAttribute('aria-label', 'Your rank: ' + lv); }",
               "  else { if ($('sgBadgeI').dataset.k !== 'dabs') { $('sgBadgeI').dataset.k = 'dabs'; $('sgBadgeI').innerHTML = DROP_SVG; } const n = store.drops || 0; $('sgBadgeT').textContent = n; b.setAttribute('aria-label', 'Dabs: ' + n); } // (v370: your dabs, not your rank)")
    s = rep(s, "  b.classList.toggle('cr', !!c);", "  b.classList.toggle('cr', !!c); b.classList.toggle('dabs', !c);")
    s = rep(s, "AU.ui(); stToast('Rank ' + repOf(store.xp || 0).lv); });", "AU.ui(); kick($('sgBadge'), 'bump'); stToast((store.drops || 0) + ' dabs to spend. Matches pay in dabs'); }); // (v370)")

    # a look at one on sale counts as a view for the dashboard (as the Paint Shop's do), once a session
    s = rep(s, "  sgDemoPick(cat !== 'skill' ? id : null); // (v322: specials too)",
               "  stStrokeView(o); // (v370)\n  sgDemoPick(cat !== 'skill' ? id : null); // (v322: specials too)")
    s = rep(s, "function stView(w) {",
               "function stStrokeView(o) { try { if (!stBuys(o) || strokesOf().own.includes(o.id) || ST.seen.has(o.id)) return; ST.seen.add(o.id); stEv({ k: 'view', i: o.id, a: stDue(o) && (store.drops || 0) >= stPrice(o) }); } catch (e) {} } // (v370: a stroke on sale)\n"
               "function stView(w) {")

    # the dab icons on the Strokes page, sized as the Locker's
    a = "#mLocker.sgp .sgcard .sgcf .dropi{width:13px;height:13px;flex:none}"
    s = rep(s, a, a + "\n"
               "/* (v370) the Strokes page's prices and dabs, as the Locker's */\n"
               "#mStrokes.sgp .sgcard .sgcf{gap:4px}\n"
               "#mStrokes.sgp .sgcard .sgcf .dropi{width:13px;height:13px;flex:none}\n"
               "#mStrokes.sgp .sgdo small{display:inline-flex;align-items:center;gap:3px;font-size:12px}\n"
               "#mStrokes.sgp .sgdo .dropi{width:14px;height:14px}\n"
               "#mStrokes.sgp .sgdo:disabled .dropi{opacity:.8}\n"
               "#mStrokes.sgp .sgdo.nope{animation:lknope .35s}\n"
               "#mStrokes.sgp .sgbadge.dabs .sgbi svg{width:20px;height:20px}\n"
               "#mStrokes.sgp .sgbadge.bump{animation:tilepop .42s cubic-bezier(.2,1.6,.4,1)}\n"
               "#mStrokes.sgp .sghow .dropi{flex:none}\n"
               "@media (prefers-reduced-motion:reduce){#mStrokes.sgp .sgdo.nope,#mStrokes.sgp .sgbadge.bump{animation:none}}")
    return s
