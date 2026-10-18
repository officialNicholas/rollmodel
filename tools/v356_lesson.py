"""v356: the first lesson, on your own.

- No rival: the lesson plays you alone on the Blank Canvas (like a Time trial: only you in the match, only you on the card before
  it), so every step that needed him is gone: pounding him, dodging his pound, rolling over him and dodging his rocket.
- No basins but the one you start in: you crawl out of it as ever, then it sinks once you're clear of it; the others stay down for
  the whole lesson. The refill step goes, so does "Full tank! Tap POUND to burst out", and the tank stays full.
- No timer and no coverage: the top bar (both percentages, the clock and the strip) is hidden for the lesson. Pause and sound stay.
- The steps: move and jump, sling, then the pound (its tip waits until you're down from the fling, so the button is a pound and not a
  missile; one that lands is the step), the Roller, the orb and its rocket, and the gift. Basics Complete lists them.
- The finish: Basics Complete, then the "New items!" card for the flower and the fangs, which goes on to the Paint Shop as before.
  No tally or victory screen, with nobody to beat and no coverage to count."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def cut(s, a, b, new=''):
    """Replace the text from marker a (included) up to marker b (kept) with new."""
    assert s.count(a) == 1 and s.count(b) == 1, (s.count(a), s.count(b), a[:80], b[:80])
    i, j = s.index(a), s.index(b); assert i < j, (a[:60], b[:60]); return s[:i] + new + s[j:]

POUND = r"""  // (v356) the pound, on your own: once you're down from the fling (in the air after one, the button fires a missile instead), its
  // button comes up, the tip points at it, and one that lands is the lesson (no rival to aim at, no tub to burst out of)
  { id: 'pound', max: 40, enter() { tut.keepAway = false; tut.slammed = false; tut.slowK = 1; tut.slowT = 0; tut.sub = ''; tut.poundUp = false; },
    tick(dt) { if (!tut.poundUp) { if (P.st !== 'play' || (P.air && (P.flingC || 0) > 0.15)) return false;
        tut.poundUp = true; tut.hidePound = false; tutGivePound(); tut.slowK = TUT_SLOW; tut.slowT = 2.5;
        tutShow(say('Tap *POUND* to splat paint all around you!', 'Press *E* to splat paint all around you!'), 'slamBtn', 'pound', true); }
      if (tut.slowT > 0) { tut.slowT -= dt / Math.max(tut.slowK, 0.05); if (tut.slowT <= 0) tut.slowK = 1; }
      if (P.slamCD > 1.5) P.slamCD = 1.5; if (P.slam) { tut.slammed = true; tut.slowK = 1; } // (the pound keeps coming back until one lands)
      return tut.slammed && !P.slam && P.st === 'play'; } },
"""

ORB = r"""  { id: 'orb', max: 55, enter() { orb.spawnT = 0; tut.orbMine = true; tut.hadRocket = false; tut.slowK = 1; tutShow('A special orb! Roll up to it for a super move', null, 'orb', false, true); },
    tick() { if (P.rocket && !tut.hadRocket) { tut.hadRocket = true; tut.slowK = 1; /* (full speed: the rocket ride is the fun part) */ tutShow(say('Steer it, then tap Boost to come down with a big splat!', 'Steer it, then press E to come down with a big splat!'), 'slamBtn', 'rocket'); }
      return tut.hadRocket && !P.rocket; },
    exit() { tut.orbMine = false; TUT_AI.orb = 0.35; } },
"""

CSS = """/* (v356) the first lesson has no timer and no coverage: the top bar's card is hidden (pause and sound stay where they are) */
.hud.lesson .top .score{visibility:hidden}
"""

def apply(s):
    # ---- you alone: only you in the match and on the card before it (as in a Time trial)
    s = rep(s, "ACTIVE = mode === 'solo' ? [P] : mode === 'trio'", "ACTIVE = mode === 'solo' || tutFlat ? [P] : mode === 'trio'")
    s = rep(s, "if (mode === 'solo') H.st = 'out';", "if (mode === 'solo' || tutFlat) H.st = 'out';")
    s = rep(s, "LH.drop.visible = LH.shadow.visible = mode !== 'solo';", "LH.drop.visible = LH.shadow.visible = mode !== 'solo' && !tutFlat;")
    s = rep(s, "else if (mode !== 'solo') { h += card(H, NAMES[1], 'foe');", "else if (mode !== 'solo' && !tutFlat) { h += card(H, NAMES[1], 'foe');")
    s = rep(s, "$('vsRow').classList.toggle('rows', viewH > viewW && mode !== 'solo');", "$('vsRow').classList.toggle('rows', viewH > viewW && mode !== 'solo' && !tutFlat);")
    s = rep(s, "const list = [[P, $('vbox0'), VS_POSE.me]]; if (mode !== 'solo') list.push", "const list = [[P, $('vbox0'), VS_POSE.me]]; if (mode !== 'solo' && !tutFlat) list.push")
    s = rep(s, "(mode === 'solo' ? 'Time trial, 60 seconds' : (NM ?", "(tutFlat ? 'Tutorial' : mode === 'solo' ? 'Time trial, 60 seconds' : (NM ?")
    # ---- no timer, no coverage: the top bar's card is hidden through the lesson
    s = rep(s, "hud.classList.add('off'); giftPlan(); newItem = null; tutBegin(); ptMatch();",
               "hud.classList.add('off'); giftPlan(); newItem = null; tutBegin(); ptMatch(); hud.classList.toggle('lesson', !!(tut && tutFlat)); // (v356)")
    s = rep(s, "</style>\n\n<div id=\"stage\">", CSS + "</style>\n\n<div id=\"stage\">")
    # ---- one basin: the one you start in. The others go down before the match opens and stay down; yours sinks once you're out of it
    s = rep(s, "  camYaw = P.yaw; camYawV = 0; introCam(true); gyCam = P.introY0 || 0; camSnap = true;",
               "  if (tut && tutFlat) for (const p of pots) if (p !== basins.get(P)) { p.st = 'down'; p.t = 0; p.g.visible = false; if (p.ring) p.ring.visible = false; if (p.tele) p.tele.visible = false; p.occ = null; p.next = null; } // (v356: the lesson's only basin is yours)\n"
               "  camYaw = P.yaw; camYawV = 0; introCam(true); gyCam = P.introY0 || 0; camSnap = true;")
    s = rep(s, "    if (p.st === 'up') continue;\n    p.t += dt;\n    if (p.st === 'sink') {",
               "    if (p.st === 'up') continue;\n    if (p.st === 'down' && tut && tutFlat) continue; // (v356: in the lesson a basin that's gone stays gone)\n    p.t += dt;\n    if (p.st === 'sink') {")
    s = rep(s, "function tutStep(dt) {\n  if (!tut || state !== 'play') return;\n",
               "function tutStep(dt) {\n  if (!tut || state !== 'play') return;\n"
               "  if (tutFlat) { if (P.st === 'play') P.paint = 1; /* (v356: no basins, so the tank stays full) */ if (P.st === 'play') for (const p of pots) if (potUp(p) && Math.hypot(p.x - P.x, p.z - P.z) > 3.2) sinkCoffin(p); } // (and a basin you're out of goes: the one you start in, or one you came back in)\n")
    # ---- the steps: the refill, the dodge, the roll-over and the rocket dodge go (they needed a basin or the rival); the pound and the
    # orb no longer aim at him
    s = cut(s, "  { id: 'basin', max: 55,", "  // (v270) you've held the Roller since the start", POUND)
    s = cut(s, "  // (v270) rolling: the rival comes round", "  { id: 'orb', max: 55,")
    s = cut(s, "  { id: 'orb', max: 55,", "  { id: 'free3', max: 99,", ORB)
    s = cut(s, "  { id: 'rocketdodge', max: 60,", "  { id: 'flower', max: 42,")
    # (back in a tub after a fall, the pound step waits like the others while the callout shows the way out: it no longer deals with the
    # tub itself)
    s = rep(s, "&& s.id !== 'pound' && s.id !== 'rest' && !(tut.gap > 0)", "&& s.id !== 'rest' && !(tut.gap > 0)")
    s = rep(s, "const TW_LIST = ['Steering', 'Flinging', 'Refilling', 'The pound', 'Dodging', 'Transforms', 'The orb', 'Finding items'];",
               "const TW_LIST = ['Steering and jumping', 'Flinging', 'The pound', 'Transforms', 'The orb', 'Finding items'];")
    # ---- the finish: Basics Complete, then the new items card (and from it the Paint Shop), with no tally or victory screen
    s = rep(s, "    tutSet('shop'); save(); tutWinDue = true; return;", "    endInfo.lesson = true; tutSet('shop'); save(); tutWinDue = true; return;")
    s = rep(s, "if (state === 'dead') startTally(); });",
               "if (state === 'dead') { if (endInfo && endInfo.lesson && newItem) showNewItem(newItem); else startTally(); } }); // (v356: the lesson goes on to its new items)")
    return s
