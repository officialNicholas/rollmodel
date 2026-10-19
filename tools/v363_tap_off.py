"""v363: tapping something you have on takes it off.

- My Locker: tapping a thing you're wearing (the flower, the fangs, a hat...) takes it off, as Take off does; tapping it again puts it
  back on. It used to only give the banner a bump, so Take off (under the banner, once the thing was picked) was the only way.
- The Paint Shop (where what you buy stays listed till you leave): once a thing you've bought is picked, tapping it again takes it
  off, and again puts it back on. The first tap still just picks it.
- Eyes are swapped, never taken off (there's always a pair), so tapping the eyes you have on still only gives the banner a bump."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "// the locker: your paint, your eyes, and what you own (a tap puts it on)\n",
               "// the locker: your paint, your eyes, and what you own (a tap puts it on, and takes it off again)\n")
    s = rep(s, "// putting a thing of yours on\n",
               "// taking a thing of yours off (Take off, or a tap on it: v363)\n"
               "function lkTakeOff(w) { myLook[w.slot] = null; saveLook(); LKR.prev = null; lkDress(); AU.ui(); buzz(4); if (SGD.built) { const D = SGD.A.D; D.squash = Math.max(D.squash, 0.3); SGD.mood = 'pout'; SGD.moodT = 0.9; } }\n"
               "// putting a thing of yours on\n")
    s = rep(s, "  myLook[w.slot] = null; saveLook(); LKR.prev = null; lkDress(); AU.ui(); buzz(4); if (SGD.built) { const D = SGD.A.D; D.squash = Math.max(D.squash, 0.3); SGD.mood = 'pout'; SGD.moodT = 0.9; }\n",
               "  lkTakeOff(w);\n")
    s = rep(s, "  if (LKR.tab === 'mine') { if (!lkWorn(w)) { lkPutOn(w); AU.pop(); buzz(5); } else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); lkFreshOff(w.id); } }\n",
               "  const off = bought(w.id) && lkWorn(w) && w.slot !== 'eyes'; // (v363: on already, a tap takes it off; eyes only swap)\n"
               "  if (LKR.tab === 'mine') { if (!lkWorn(w)) { lkPutOn(w); AU.pop(); buzz(5); } else if (off) lkTakeOff(w); else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); lkFreshOff(w.id); } }\n")
    s = rep(s, "  else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); }\n",
               "  else if (off) lkTakeOff(w);\n"
               "  else if (bought(w.id) && !lkWorn(w)) { lkPutOn(w); AU.pop(); buzz(5); } // (and back on, as in your locker)\n"
               "  else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); }\n")
    return s
