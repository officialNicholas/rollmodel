"""v452: a beat after the slingshot before Out of paint?, and "Dodged!" when you get out from under the pound.

- The user: "Wait a couple seconds more until it says out of paint in the tutorial after the slingshot". After the fling lands the
  game runs on for 2.5 s (your paint as it was) before the Out of paint? card and the tank draining.
- The user: "During the swipe up before it lands tutorial. When they do it, in that yellow text ... say Dodged!": the gold pop says
  Dodged! the moment the dodge counts (the roll timed under his pound, or it coming down and missing you)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "tut.potQ = null; tut.potTry = 0; tutHide(); lsnDue('basin'); },",
               "tut.potQ = null; tut.potTry = 0; tutHide(); tut.basinWait = 2.5; /* (v452: a beat after the fling, then the card) */ },")
    s = rep(s, "    tick(dt) { if (P.dryT) P.dryT = 0; /* (no running dry into a knock-out in the lesson) */\n",
               "    tick(dt) { if (P.dryT) P.dryT = 0; /* (no running dry into a knock-out in the lesson) */\n"
               "      if (tut.basinWait > 0) { tut.basinWait -= dt; if (tut.basinWait <= 0) lsnDue('basin'); return false; } /* (v452) */\n")
    s = rep(s, "      if (coming && P.rollT > 0 && !tut.rolled) tut.rolled = true; // (a roll while its pound is in the air: that is the timing)",
               "      if (coming && P.rollT > 0 && !tut.rolled) { tut.rolled = true; popText('Dodged!'); } // (a roll while its pound is in the air: that is the timing) (v452: said)")
    s = rep(s, "if (tut.thr && tut.hits === tut.h0 && H.st === 'play' && P.st === 'play') tut.escaped = true;",
               "if (tut.thr && tut.hits === tut.h0 && H.st === 'play' && P.st === 'play') { if (!tut.escaped && !tut.rolled) popText('Dodged!'); tut.escaped = true; }")
    return s
