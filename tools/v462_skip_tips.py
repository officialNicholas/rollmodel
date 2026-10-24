"""v462: skipping the tutorial leaves only the essential tips, about half as many.

- The user: "Reduce the amount of "tips" when you skip the tutorial by about half. Down to the essentials".
- Those who skip the lesson (Just play, or Skip tutorial in its pause) still get the one-time match tips for the basics, eight of them:
  steer, jump, fling (pull down and let go), out of paint (refill), ground pound, dodge roll, using an item, and the time trial's rings.
- The other eleven are now marked as seen for them, so they never pop up: the boomerang and how to dodge it, rolling over rivals, the
  trap dodge, the orb, the rocket's steering, rolling on when out of paint, the air dash, pounding to burst out, the missile, and the
  "you start with your item" line. A save that already skipped gets the same trim when it loads.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "function tutSkipAll() {\n",
        "function tipsTrim() { // (v462) the tips not shown to those who skipped the lesson\n"
        "  for (const k of ['boom', 'boomdodge', 'rroll', 'trapdodge', 'orb', 'rocket', 'dryroll', 'airdash', 'burst', 'missile', 'startitem']) store.seen[k] = 1; store.tut.lite = 1; }\n"
        "function tutSkipAll() {\n  tipsTrim();\n")
    a = "if (store.tut.ph === 'shop' || store.tut.ph === 'locker') {"
    s = rep(s, a, "if (store.tut.skipped && !store.tut.lite) { tipsTrim(); save(); } /* (v462: a save that skipped already) */ " + a)
    return s
