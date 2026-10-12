#!/usr/bin/env python3
"""v244: turning on the spot (and slow turns) is done with the arms and the torso: the outside hand reaches out and forward and pulls the
body round, the inside hand steps back and in and pushes, the feet shuffle the same way, and the trunk curves into a deeper C while it
pivots. Before, the body turned as one piece with the limbs shuffling under it."""
P = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools/assets/axolife.js'
s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  const sl = L.slK = smooth(SL.k);\n", "  const sl = L.slK = smooth(SL.k);\n  const pv = L.pv = clamp01(Math.abs(L.yr) / 1.6) * (1 - clamp01(L.vc / 2.5)) * on; // (a pivot: turning fast while hardly moving forward)\n")
rep("const bU = bend * (1 - 0.6 * sl), T = 50 * Math.tanh((-amp * c1 + bU * 0.92 + HT * 0.45 * (1 - 0.5 * sl)) / 50);",
    "const bU = bend * (1 - 0.6 * sl) * (1 + 0.3 * pv), Tc = 50 + 18 * pv, T = Tc * Math.tanh((-amp * c1 + bU * 0.92 + HT * 0.45 * (1 - 0.5 * sl)) / Tc); /* (pivoting, the trunk takes a deeper C) */")
rep("        l.tgt.copy(l.hb).addScaledVector(l.gv, -Ts * 0.5); LV1.copy(l.tgt).sub(l.hb); LV1.y = 0; const r = (l.arm ? GAIT.reachH : GAIT.reachF) * 0.92; if (LV1.length() > r) LV1.setLength(r);",
    """        l.tgt.copy(l.hb).addScaledVector(l.gv, -Ts * 0.5);
        if (pv > 0.01) { const side = Math.max(-1, Math.min(1, bend / 45)) * l.m, inn = Math.max(0, side), outr = Math.max(0, -side); // (pivoting: the outside hand reaches out and forward to pull the body round, the inside hand steps back and in to push; the feet the same, less)
          l.tgt.z += (l.arm ? 0.1 * outr - 0.07 * inn : 0.05 * outr - 0.03 * inn) * pv; l.tgt.x += l.m * (l.arm ? 0.06 * outr - 0.04 * inn : 0.03 * outr) * pv; }
        LV1.copy(l.tgt).sub(l.hb); LV1.y = 0; const r = (l.arm ? GAIT.reachH : GAIT.reachF) * (0.92 + 0.16 * pv); if (LV1.length() > r) LV1.setLength(r);""")
open(P, 'w').write(s); print('turn244 ok')
