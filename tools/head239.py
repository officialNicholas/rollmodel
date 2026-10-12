#!/usr/bin/env python3
"""v239: the ears on the slime head: a looser spring (1.4 Hz, lightly damped), both ears thrown the same way (to the outside) round a turn
in the new ear frames, a smaller breath flare, a trail back at a run that swings forward on a stop, a sweep back on each swim pull and a
flap on landing."""
P = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools/assets/axolife.js'
s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("this.gillSpring2 = 1; this.gillSpring.k = 230; this.gillSpring.c = 10; }", "this.gillSpring2 = 1; this.gillSpring.k = 75; this.gillSpring.c = 5; }")
rep("for (let j = 0; j < 6; j++) { const sgn = j < 3 ? 1 : -1; add[j * 2] = -fl * 2.5 * (1 - L.act); add[j * 2 + 1] = swing * 24 * sgn + fl * 7 * (1 - L.act); } this.gillAddOn = true; }",
    "for (let j = 0; j < 6; j++) { add[j * 2] = -fl * 1.0 * (1 - L.act) + Math.min(1, L.v / 4) * 9; add[j * 2 + 1] = -swing * 24 + fl * 2 * (1 - L.act); } this.gillAddOn = true; } /* (the ears: hang back a little at a run and swing forward on a stop; both thrown to the outside of a turn) */")
rep("this.kickGills(0, -0.28 * sl); SL.pu = u;", "this.kickGills(0, 0.28 * sl); SL.pu = u;")
rep("L.dip.v -= 44 * k; L.dipR.v += 40 * k * L.lead; L.landK = k;", "L.dip.v -= 44 * k; L.dipR.v += 40 * k * L.lead; L.landK = k; this.kickGills(0, 0.6 * k); /* (the ears slap down on landing) */")
open(P, 'w').write(s); print('head239 ok')
