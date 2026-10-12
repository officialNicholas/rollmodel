#!/usr/bin/env python3
"""v240: the crawl steps less often with longer strides (it looked like scrabbling), and the body curves harder round a turn."""
P = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools/assets/axolife.js'
s = open(P).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("sMax: 0.54, fMax: 5.6, fMin: 1.7 };", "sMax: 0.64, fMax: 4.7, fMin: 1.6 };")
rep("S = Math.min(GAIT.sMax, 0.24 + 0.08 * v);", "S = Math.min(GAIT.sMax, 0.28 + 0.095 * v); /* (longer strides, fewer steps: an unhurried crawl) */")
rep("Math.max(-64, Math.min(64, kap * 90))) * on, spun ? 48 : 55, spun ? 10 : 11, dt);", "Math.max(-78, Math.min(78, kap * 118))) * on, spun ? 48 : 55, spun ? 10 : 11, dt); /* (a deeper C round a turn) */")
rep("this.worldTurn(out, sp[1], bend * 0.3 * sl, 0); this.worldTurn(out, sp[2], bend * 0.12 * sl, 0);", "this.worldTurn(out, sp[1], bend * 0.4 * sl, 0); this.worldTurn(out, sp[2], bend * 0.17 * sl, 0);")
rep("this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.16 + 0.2 * (L.slK || 0))", "this.tailLat += L.bend * (this.motion.spin !== undefined ? 0 : 0.22 + 0.2 * (L.slK || 0))")
open(P, 'w').write(s); print('gait240 ok')
