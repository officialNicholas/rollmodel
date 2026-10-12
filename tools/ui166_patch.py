#!/usr/bin/env python3
"""v233: the paint starts flowing a second into the crawl: when a match starts and when a blob comes back from a knock-out, it crawls a
second clean, then the stream comes out from under it, thin at first and swelling to full width over half a second. The stream comes
from further forward (laid under the head, full width under the chest). And out of paint, the axolotl only crawls, it never swims."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui165_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert '!M.dry && M.spin === undefined' in s and "A.motion.dry = !!(D && D.dry && D.st === 'play')" in s
# ---- the stream further forward: laid under the head, full width under the chest
rep("const TAPER_N = 5, TAPER_NMAX = 22, TAPER_TIP = 0.3, TRAIL_FWD = 0.1; /* (the stream laid a touch ahead of the blob's centre, under its chin, and full width by its hips) */",
    "const TAPER_N = 3, TAPER_NMAX = 22, TAPER_TIP = 0.3, TRAIL_FWD = 0.3; /* (the stream laid under the head, ahead of the blob's centre, and full width under the chest) */")
# ---- a second of crawling first, then the stream swells in (flowT: the clean crawl left; flowK: how far the stream has swelled)
rep("      if (D.flatT <= 0 && !D.dry) { D.dist += D.spd * dt; const fx = D.x + Math.sin(D.yaw) * TRAIL_FWD, fz = D.z + Math.cos(D.yaw) * TRAIL_FWD, fy = hugY(fx, fz, D.y); while (D.dist >= SPACING) { D.dist -= SPACING; addPoint(fx, fy, fz, D.yaw, dryClock, D.stroke, (D.giantT > 0 ? GIANT_K : D.power && D.power.type === 'roller' ? 2.6 : 1) * (D.rollT > ROLL_T - ROLL_DASH ? 0.45 : 1), tcode(D), D.rb); } }",
    "      if (D.flatT <= 0 && !D.dry) { if (D.flowT > 0) { D.flowT -= dt; D.dist = 0; if (D.flowT <= 0) D.stroke++; } /* (a second of crawling clean first) */ else { D.flowK = Math.min(1, (D.flowK === undefined ? 1 : D.flowK) + dt / 0.5); const fk = 0.3 + 0.7 * D.flowK * D.flowK * (3 - 2 * D.flowK); /* (then the stream swells in) */ D.dist += D.spd * dt; const fx = D.x + Math.sin(D.yaw) * TRAIL_FWD, fz = D.z + Math.cos(D.yaw) * TRAIL_FWD, fy = hugY(fx, fz, D.y); while (D.dist >= SPACING) { D.dist -= SPACING; addPoint(fx, fy, fz, D.yaw, dryClock, D.stroke, (D.giantT > 0 ? GIANT_K : D.power && D.power.type === 'roller' ? 2.6 : 1) * (D.rollT > ROLL_T - ROLL_DASH ? 0.45 : 1) * fk, tcode(D), D.rb); } } }")
# (armed at the match's Go, for everyone, and on the way back from a knock-out, when it leaves its pot)
rep("  for (const D of ACTIVE) { D.eyeSink = D.eyeShut = D.eyeWide = 0; } // (whatever an intro was doing with the peeking eyes)",
    "  for (const D of ACTIVE) { D.eyeSink = D.eyeShut = D.eyeWide = 0; D.flowT = 1; D.flowK = 0; } // (whatever an intro was doing with the peeking eyes; and a second of crawling before the paint flows)")
rep("  D.vy = 0; D.air = false; D.slam = false; D.spd = 0; D.flatT = 0; D.paint = Math.max(D.paint, 0.5); best.cool = 0; D.spawnImm = true;",
    "  D.vy = 0; D.air = false; D.slam = false; D.spd = 0; D.flatT = 0; D.paint = Math.max(D.paint, 0.5); best.cool = 0; D.spawnImm = true; D.flowArm = true;")
rep("  const p = D.pot; if (!p) return;\n  p.cool = 1.0; p.bounce = 0.7; p.occ = null; D.pot = null; D.st = 'play'; D.stroke++;",
    "  const p = D.pot; if (!p) return;\n  if (D.flowArm) { D.flowArm = false; D.flowT = 1; D.flowK = 0; } /* (back from a knock-out: a second of crawling before the paint flows) */\n  p.cool = 1.0; p.bounce = 0.7; p.occ = null; D.pot = null; D.st = 'play'; D.stroke++;")
# (the stream is drawn ahead of the blob, but the paint it covers is counted where the blob is, as it always was: the check for your own
# color reads the floor just ahead of you, refilling you and speeding you up, and must never see your own fresh stream)
rep("function addPoint(x, y, z, yaw, t, stroke, wmul, team, rb) {", "function addPoint(x, y, z, yaw, t, stroke, wmul, team, rb, sp) { /* (sp: where the paint is counted, if not where it is drawn) */")
rep("  stamp(x, y, z, W / 2, team);\n  if (nP === 1)", "  if (sp) stamp(sp[0], sp[1], sp[2], W / 2, team); else stamp(x, y, z, W / 2, team);\n  if (nP === 1)")
rep("* (D.rollT > ROLL_T - ROLL_DASH ? 0.45 : 1) * fk, tcode(D), D.rb); } } }", "* (D.rollT > ROLL_T - ROLL_DASH ? 0.45 : 1) * fk, tcode(D), D.rb, [D.x, D.y, D.z]); } } }")
# ---- the lesson's first dodge: once you've swiped clear, a second more of the slow-down (real time), then it eases back to full speed
# over a quarter of a second (it used to hold till the rival's pound came down)
rep("    tick() { if (!H.slam && P.st === 'play') tutRivalIn(6.5);", "    tick(dt) { if (!H.slam && P.st === 'play') tutRivalIn(6.5);")
rep("      if (coming && P.rollT > 0) tut.rolled = true; // (a roll while its pound is in the air: that is the timing)",
    "      if (coming && P.rollT > 0 && !tut.rolled) { tut.rolled = true; tut.rollRT = 0; } // (a roll while its pound is in the air: that is the timing)\n      if (tut.rolled) tut.rollRT = (tut.rollRT || 0) + (dt || 0) / Math.max(tut.slowK, 0.05); /* (real seconds since the swipe) */")
rep("      const now = coming && eta < 0.42; tut.slowK = now ? 0.14 : coming ? 0.45 : 1;",
    "      const now = coming && eta < 0.42, base = now ? 0.14 : coming ? 0.45 : 1, back = tut.rolled ? Math.min(1, Math.max(0, (tut.rollRT - 1) / 0.25)) : 0; tut.slowK = base + (1 - base) * back; /* (swiped clear: a second more, then back to speed) */")
rep('<p class="ver">Version 232</p>', '<p class="ver">Version 233</p>')
open(DST, 'w').write(s)
print('ui166 ok', n0, '->', len(s))
