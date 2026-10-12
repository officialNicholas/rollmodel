#!/usr/bin/env python3
"""v243: a cleaner jump in the air. The hands let go of the ground sooner (no arms stretched down to it as the body rises), and in flight the
limbs tuck tight: the hands folded up under the chest, elbows back; the feet drawn up and back beside the belly; the back arched a touch
more with the tail up. The reach down to land is as it was."""
P = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools/assets/axolife.js'
s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("if (l.held) { const d = l.p.distanceTo(pos[l.root]); if (d > 0.94 * l.len || L.airT > 0.12 || !rising) { l.held = false; l.p0.copy(l.p); } }",
    "if (l.held) { const d = l.p.distanceTo(pos[l.root]); if (d > 0.82 * l.len || L.airT > 0.07 || !rising) { l.held = false; l.p0.copy(l.p); } } /* (the hands let go early: never stretched down to the ground as it rises) */")
rep("LV1.copy(l.rr).add(l.arm ? LV2.set(0.06 * l.m, -0.12, -0.3) : LV2.set(0.05 * l.m, 0.07, -0.02)).add(LV4.set(l.hb.x - l.home.x, 0, l.hb.z - l.home.z));",
    "LV1.copy(l.rr).add(l.arm ? LV2.set(0.03 * l.m, -0.03, -0.24) : LV2.set(0.04 * l.m, 0.1, -0.1)).add(LV4.set(l.hb.x - l.home.x, 0, l.hb.z - l.home.z)); /* (tucked tight: hands up under the chest, feet up and back) */")
rep("if (air) { rot(out, sp[1], -5 - 3 * riseK + 9 * fallK, 0, 0); rot(out, sp[2], -4 - 2 * riseK + 7 * fallK, 0, 0); }",
    "if (air) { rot(out, sp[1], -7 - 3 * riseK + 9 * fallK, 0, 0); rot(out, sp[2], -6 - 2 * riseK + 7 * fallK, 0, 0); } /* (a touch more arch in the air) */")
open(P, 'w').write(s); print('jump243 ok')
