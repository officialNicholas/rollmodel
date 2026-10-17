"""v330: the Sly eyes are everyone's from the start (and on the intro's card); the Zombie eyes, now the only eye style to find, are a
free gift that turns up the first time you play a Spooky SZN canvas.

- Sly eyes: not a shop item any more. Like Round, Aggressive and Dot they're there from the start, in the locker and on the intro's
  "Now give them some style." card (Round, Aggressive, Dot, Sly).
- Zombie eyes: no longer bought. The first match on a Spooky SZN canvas (The Crypt, The Cathedral, The Manor; not online) puts a gift
  box on the floor a little ahead of you, early on ("A free gift!", Ol' Bloop's "Grab it!", the arrow to it). Roll over it and they're
  yours, free; after the match the card says Free gift! with Put them on. Miss it and it's there again next time. In the Paint Shop and
  the locker they read "Free gift" until then. They no longer turn up in the second lesson match (Sludge Sewer).
- A save that found the Zombie eyes but never bought them has them now."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the eye items: Sly out of the shop (everyone has it), Zombie a gift
    s = rep(s, "const EXTRA = [{ id: 'zombie', name: 'Zombie eyes', slot: 'eyes', cat: 'eyes', season: 1, stage: 'halloween' }, { id: 'sly', name: 'Sly eyes', slot: 'eyes', cat: 'eyes' }], ITEMS = WEAR.concat(EXTRA);",
               "const EXTRA = [{ id: 'zombie', name: 'Zombie eyes', slot: 'eyes', cat: 'eyes', season: 1, stage: 'halloween', gift: 1 }], ITEMS = WEAR.concat(EXTRA); // (v330: the Sly eyes are everyone's from the start; the Zombie eyes, the one style to find, are a free gift)")
    s = rep(s, "if (w.id === 'zombie' && store.zombieDeal && !BOUGHT.has('zombie')) return Math.max(1, Math.floor((store.drops || 0) * 0.7)); /* (the first find of the season: always within reach) */",
               "if (w.gift) return 0; /* (v330: a gift costs nothing) */")
    s = rep(s, "if (!Array.isArray(store.bought)) { store.bought = [...BOUGHT]; }\n",
               "if (!Array.isArray(store.bought)) { store.bought = [...BOUGHT]; }\n"
               "for (const w of EXTRA) if (w.gift && OWNED.has(w.id) && !BOUGHT.has(w.id)) { BOUGHT.add(w.id); store.bought = [...BOUGHT]; } // (v330: found but never bought: a gift is yours)\n")
    # the intro's style card: Sly too
    s = rep(s, "const styles = ['round', 'edgy', 'dot'].map(", "const styles = ['round', 'edgy', 'dot', 'sly'].map(")
    # the gift: on your first Spooky SZN canvas, for sure, early and a little ahead of you (in match 3's lesson, after the orb's done its
    # part); never one of the random finds
    s = rep(s, "  Object.assign(gift, { id: null, on: false, got: false, pop: 0 }); giftM.visible = giftRing.visible = giftBeam.visible = false;\n  if (NM) return; // (v306: no rare finds online)\n",
               "  Object.assign(gift, { id: null, on: false, got: false, pop: 0, zg: false }); giftM.visible = giftRing.visible = giftBeam.visible = false;\n  if (NM) return; // (v306: no rare finds online)\n"
               "  if (TH && SEASON.themes.includes(TH.id) && !owns('zombie')) { gift.id = 'zombie'; gift.zg = true; gift.at = (mode === 'solo' ? SOLO_T : MATCH_T) * (tutPh() === 'done' && store.tut.m3 === 1 ? 0.5 : 0.14); return; } // (v330: the Zombie eyes, a free gift on your first Spooky SZN canvas)\n")
    s = rep(s, "const left = ITEMS.filter(w => needFind(w) && w.stage === stageSet() && !owns(w.id));",
               "const left = ITEMS.filter(w => needFind(w) && !w.gift && w.stage === stageSet() && !owns(w.id));")
    s = rep(s, "  if (state !== 'play') { if (gift.on) { gift.on = false; giftPoof(); } return; }\n",
               "  if (state !== 'play') { if (gift.on) { gift.on = false; giftPoof(); } if (gift.zg && tutTip && tutTip.key === 'zgift') tutHide(); return; }\n")
    s = rep(s, "const s = (tut2 && tutGiftSpot(6, 11)) || giftSpot();", "const s = ((tut2 || gift.zg) && tutGiftSpot(6, 11)) || giftSpot();")
    s = rep(s, "if (!tut && !tut2) banner('Something rare!', 'An item has turned up. Go grab it', true);",
               "if (gift.zg) banner('A free gift!', 'It\\u2019s Spooky SZN. Go grab it', true); else if (!tut && !tut2) banner('Something rare!', 'An item has turned up. Go grab it', true);")
    s = rep(s, "  gift.t += dt; gift.pop = Math.min(1, gift.pop + dt * 2.2);\n",
               "  gift.t += dt; gift.pop = Math.min(1, gift.pop + dt * 2.2);\n"
               "  if (gift.zg && !tutTip && P.st !== 'ko') tutShow('A gift has appeared on the canvas! *Grab it!*', null, 'zgift', true, true); // (v330: Ol' Bloop points it out, as the lesson did)\n")
    s = rep(s, "  unlockItem(gift.id); store.itemIn = 2 + Math.floor(Math.random() * 4); save(); newItem = gift.id; emote(P, 'glee', 1.3);\n",
               "  if (tutTip && tutTip.key === 'zgift') tutHide();\n"
               "  unlockItem(gift.id); if (gift.zg) { BOUGHT.add(gift.id); store.bought = [...BOUGHT]; } else store.itemIn = 2 + Math.floor(Math.random() * 4); save(); newItem = gift.id; emote(P, 'glee', 1.3); // (v330: a gift is yours, nothing to pay)\n")
    s = rep(s, "  const w = WEAR.find(x => x.id === gift.id); banner(tut && gift.id === 'flower' ? 'New items!' : 'New item!', tut && gift.id === 'flower' ? 'Flower + Fangs' : w ? w.name : '', true);",
               "  const w = ITEMS.find(x => x.id === gift.id); banner(gift.zg ? 'Free gift!' : tut && gift.id === 'flower' ? 'New items!' : 'New item!', tut && gift.id === 'flower' ? 'Flower + Fangs' : w ? w.name : '', true);")
    # Ol' Bloop's "Grab it!" stays up in a match after the onboarding
    s = rep(s, "if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring'); if (!(state === 'play' && tutTip && tutTip.key === 'protip')) tutHide(); return; }",
               "if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring'); if (!(state === 'play' && tutTip && (tutTip.key === 'protip' || tutTip.key === 'zgift'))) tutHide(); return; }")
    s = rep(s, "if (ph !== 'shop' && ph !== 'locker' && ph !== 'vote') { if (!(state === 'play' && tutTip && tutTip.key === 'protip')) tutHide(); return; }",
               "if (ph !== 'shop' && ph !== 'locker' && ph !== 'vote') { if (!(state === 'play' && tutTip && (tutTip.key === 'protip' || tutTip.key === 'zgift'))) tutHide(); return; }")
    # the second lesson match: no zombie eyes after the rain now
    s = rep(s, "  else if (t.ph === 'rain') { if (wxPhase !== 'rain') { if (owns('zombie')) { t.ph = 'done'; return; } t.ph = 'gift'; gift.id = 'zombie'; gift.got = false; gift.on = false; gift.at = runT + 0.8; wxLeft = Math.max(wxLeft, 30); } }\n",
               "  else if (t.ph === 'rain') { if (wxPhase !== 'rain') t.ph = 'done'; } // (v330: the zombie eyes are your first Spooky SZN canvas's gift now)\n")
    s = rep(s, "then the rain in one plain line, no slow-down, then the zombie eyes turn up close by.", "then the rain in one plain line, no slow-down.")
    # the card after the match: Free gift!, Put them on
    s = rep(s, "$('niKick').textContent = two ? 'New items!' : 'New item!';", "$('niKick').textContent = two ? 'New items!' : w.gift ? 'Free gift!' : 'New item!';")
    s = rep(s, "$('niWhere').innerHTML = two ? 'Two new items for your locker' : 'Found on '",
               "$('niWhere').innerHTML = two ? 'Two new items for your locker' : w.gift ? 'A Spooky SZN gift. They\\u2019re yours, free' : 'Found on '")
    s = rep(s, "$('niTry').textContent = ws.every(it => bought(it.id)) ? 'Try it on'", "$('niTry').textContent = !two && w.gift ? 'Put them on' : ws.every(it => bought(it.id)) ? 'Try it on'")
    # the Paint Shop and the locker: "Free gift", and where it comes from
    s = rep(s, "const foot = own ? (on ? 'Equipped' : tab === 'shop' ? 'Yours' : '') : found ? DROP_SVG + '<b>' + PRICE(w) + '</b>' : LOCK_ICON + 'Find it';",
               "const foot = own ? (on ? 'Equipped' : tab === 'shop' ? 'Yours' : '') : found ? DROP_SVG + '<b>' + PRICE(w) + '</b>' : LOCK_ICON + (w.gift ? 'Free gift' : 'Find it');")
    s = rep(s, ", locked. Find it on ' + WEAR_WHERE[w.stage])", ", locked. ' + (w.gift ? 'A free gift on ' : 'Find it on ') + WEAR_WHERE[w.stage])")
    s = rep(s, "aria-label=\"' + EYE_STYLES[k] + ' eyes' + (lk ? ', in the Paint Shop' : '') + '\"",
               "aria-label=\"' + EYE_STYLES[k] + ' eyes' + (lk ? (it.gift ? ', a free gift on the Spooky SZN stages' : ', in the Paint Shop') : '') + '\"")
    s = rep(s, "  $('lkKind').textContent = kind; nmSet($('lkName'), name);",
               "  if (w && w.gift) { line = bought(w.id) ? 'A free gift from the Spooky SZN' : 'A free gift on the Spooky SZN stages'; if (!bought(w.id)) { doH = STROKE_LOCK + 'Free gift'; doCls = ''; doDis = true; doLab = w.name + ', a free gift on the Spooky SZN stages'; note = 'They turn up as a free gift the first time you play a Spooky SZN stage'; } } // (v330)\n"
               "  $('lkKind').textContent = kind; nmSet($('lkName'), name);")
    # the locker page's note (how to get it, how many dabs short) on a paper slip: it sits over the pad's dark rim
    s = rep(s, "@media (prefers-reduced-motion:reduce){#mLocker.sgp .sgart .frface,#mLocker.sgp .lkcoin.bump,#mLocker.sgp .sgban.bump,#mLocker.sgp .tpop,#mLocker.sgp .sgdo.nope{animation:none}}\n</style>",
               "@media (prefers-reduced-motion:reduce){#mLocker.sgp .sgart .frface,#mLocker.sgp .lkcoin.bump,#mLocker.sgp .sgban.bump,#mLocker.sgp .tpop,#mLocker.sgp .sgdo.nope{animation:none}}\n"
               "#mLocker.sgp .sgnote{justify-self:center;width:fit-content;max-width:calc(100% - 12px);margin:0 auto;padding:4px 10px;border-radius:9px;background:rgba(255,250,238,.95);box-shadow:0 2px 0 rgba(23,19,32,.2);color:#3A3048}\n</style>")
    return s
