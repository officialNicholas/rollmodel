"""v426: online matches start from the basins, and an invite says it was sent.

- Online, everyone dropped in from the sky: the match start skipped the basin pick (`NM ? new Map()`), because each phone would have
  picked different basins (the pick is random) and the server puts everyone on the stage's spawn spots anyway, ruling anything far
  from them a teleport. Now, before the stage goes to the server, every phone picks the same basins (the pick runs on the stage's
  seed, players in slot order), and sends the end of each player's crawl-out as that slot's spawn spot. The server then starts each
  player exactly where the crawl-out lands, so the basin intro plays online as it does against CPUs, and the first move after Go is
  not a teleport (the cannon and twister ways out land within a metre of the crawl's end, inside the server's allowance). The game
  only goes live once your own way out is done, and a rival still in its basin or on its way out is left to the intro (it isn't
  dropped onto its spot).
- Invite: tapping Invite on a friend sent the invite, but the only feedback was a sound and a screen-reader line, and the button
  could keep saying Invite. Now a toast says the invite was sent, and the button turns to Invited at once.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the basin pick can run on a given random source and player order (online: the stage's seed, slot order)
    s = rep(s, "function introBasins() {\n  const all = pots.filter(p => potUp(p) && !p.occ), got = new Map(), who = ACTIVE.filter(D => D.st !== 'out');",
               "function introBasins(rand, order0) { // (v426: rand and order0 given online: the stage's seed, slot order, the same on every phone)\n"
               "  rand = rand || Math.random; const all = pots.filter(p => potUp(p) && !p.occ), got = new Map(), who = order0 || ACTIVE.filter(D => D.st !== 'out');")
    s = rep(s, "  const sc = new Map(all.map(p => [p, startRoom(p).score + Math.random() * 2.5]));", "  const sc = new Map(all.map(p => [p, startRoom(p).score + rand() * 2.5]));")
    s = rep(s, "  best.sort((a, b) => sc.get(b) - sc.get(a)); const order = who.slice().sort((a, b) => (a === P ? -1 : b === P ? 1 : 0));\n"
               "  if (best.length === 2 && half(best[0]) === 1 && half(best[1]) === 0 && sc.get(best[1]) > sc.get(best[0]) - 4) best.reverse();\n"
               "  if (mode === 'duo' && best.length >= 4) {",
               "  best.sort((a, b) => sc.get(b) - sc.get(a)); const order = order0 ? who : who.slice().sort((a, b) => (a === P ? -1 : b === P ? 1 : 0));\n"
               "  if (!order0 && best.length === 2 && half(best[0]) === 1 && half(best[1]) === 0 && sc.get(best[1]) > sc.get(best[0]) - 4) best.reverse();\n"
               "  if (!order0 && mode === 'duo' && best.length >= 4) {")
    # ---- online: the basins picked before the stage goes to the server; each slot's spawn spot is where its crawl-out ends
    s = rep(s, "function netSendLayout() {\n  const sp = NM.mode === 'duel' ? [START, CSTART] : NM.mode === 'trio' ? [START, CSTART, CSTART2] : [START, CSTART, CSTART2, CSTART3]; // (every phone builds the same stage: the spots in the stage's own order)\n",
               "function netSendLayout() {\n  const sp = (NM.mode === 'duel' ? [START, CSTART] : NM.mode === 'trio' ? [START, CSTART, CSTART2] : [START, CSTART, CSTART2, CSTART3]).map(q => ({ x: q.x, z: q.z, yaw: q.yaw })); // (every phone builds the same stage: the spots in the stage's own order)\n"
               "  // (v426) the basins, picked the same on every phone (the stage's seed, slot order): where each crawl-out ends is that slot's spawn spot\n"
               "  // (the live basins are still the lobby's, wandered about: the stage's own are placed first, and the pick is kept by basin number, since the\n"
               "  // match start places them again; the lobby's pick-ups are kept out of the pick, since each phone has its own)\n"
               "  NM.basins = new Map();\n"
               "  try {\n"
               "    placeObjects(level); const pw0 = powers; powers = [];\n"
               "    try {\n"
               "      const slots = [...NM.seats.keys()].sort((a, b) => a - b), who = slots.map(k => NM.seats.get(k)).filter(D => D && ACTIVE.includes(D));\n"
               "      const got = introBasins(rng((GEN.seed ^ 0x51a7) >>> 0), who);\n"
               "      for (const [k, D] of NM.seats) { const p = got.get(D); if (!p || !sp[k]) continue; NM.basins.set(k, pots.indexOf(p));\n"
               "        const yaw = basinLeap(p), fx = Math.sin(yaw), fz = Math.cos(yaw), R = basinRim(p, fx, fz), s1 = R.rw + CRAWL_PAST;\n"
               "        sp[k] = { x: p.x + fx * s1, z: p.z + fz * s1, yaw }; }\n"
               "    } finally { powers = pw0; }\n"
               "  } catch (e) { NM.basins = new Map(); }\n")
    # ---- at the match start: the picked basins, by seat
    s = rep(s, "  const basins = NM ? new Map() : introBasins();",
               "  const basins = NM ? (() => { const g = new Map(); if (NM.basins) for (const [k, p] of NM.basins) { const D = NM.seats.get(k); if (D && ACTIVE.includes(D) && potUp(p) && !p.occ) g.set(D, p); } return g; })() : introBasins(); // (v426: online, the basins every phone agreed on)")
    # ---- the game goes live once your crawl-out is done; a rival in its basin or crawling out is the intro's, not dropped onto its spot
    s = rep(s, "  if (state === 'play' && !NM.live && NM.phase !== 'end' && NM.startAt && P.st === 'play' && !P.air && netNow() >= NM.startAt) NM.live = true;\n  if (!NM.live || state !== 'play'",
               "  if (state === 'play' && !NM.live && NM.phase !== 'end' && NM.startAt && P.st === 'play' && !P.air && !P.introCrawl && !P.introAct && netNow() >= NM.startAt) NM.live = true; // (v426: once the way out of the basin is done)\n  if (!NM.live || state !== 'play'")
    s = rep(s, "  if (!D.netLive) { if (r.t > NM.startAt + 30) D.netLive = true; else return netDrop(D, dt); } // (until its first move after Go: still dropping onto its spot)",
               "  if (!D.netLive) { if (r.t > NM.startAt + 30) D.netLive = true; else return (D.st === 'hide' || D.introCrawl || D.introAct || (NM.basins && NM.basins.size)) ? undefined : netDrop(D, dt); } // (until its first move after Go: still dropping onto its spot; v426: or in its basin, the intro's)")
    # ---- the invite says it was sent
    s = rep(s, "    AU.pop(); onSay('Invited ' + hdOf(f.name)); pushAsk();",
               "    AU.pop(); onSay('Invited ' + hdOf(f.name)); frToast('<span>Invite sent to <b>' + frEsc(hdOf(f.name)) + '</b></span>'); // (v426: said on screen too)\n"
               "    for (const b of document.querySelectorAll('[data-py=\"inv\"][data-id=\"' + (CSS && CSS.escape ? CSS.escape(f.id) : f.id) + '\"]')) { b.disabled = true; b.classList.add('pkon'); b.textContent = 'Invited'; }\n"
               "    pushAsk();")
    return s
