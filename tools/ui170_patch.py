#!/usr/bin/env python3
"""v237: the feel pass. A finger landing on the screen crouches the character at once (the jump's anticipation, and feedback before the tap
even ends; a steer eases it back out); a spring off the ground, the tail whipped, the nose arcing over the flight, a braced wider landing
from a hard fall; a lurch onto the hands when braking; the swim's first pull is a bigger launch; a decisive tuck into the ball. And the
slingshot's jelly ball now stays a ball through the whole flight, unfurling back into the axolotl just before it lands (it used to give
the axolotl back at the top of the arc)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui169_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'A.motion.crouch = D && D.preJ > 0' in s and 'SL.first = 1' in s and 'riseK' in s
# ---- the crouch: a finger lands (the steering finger, with nothing else going on) and the character gathers itself; it lets go when the
# finger steers or lifts, and the jump itself clears it
rep("  if (steerId === null) { steerId = e.pointerId; anchorX = e.clientX; anchorY = e.clientY; rangeIn = 0; } else if (state === 'play') jump(P);",
    "  if (steerId === null) { steerId = e.pointerId; anchorX = e.clientX; anchorY = e.clientY; rangeIn = 0; if (state === 'play' && P.st === 'play' && !P.air && !P.charging && !P.slam) P.preJ = 0.3; /* (it may be a jump: a crouch at once) */ } else if (state === 'play') jump(P);")
rep("  if (Math.abs(sx) > 9 || Math.abs(dy) > 9) t.moved = true;", "  if (Math.abs(sx) > 9 || Math.abs(dy) > 9) { t.moved = true; P.preJ = 0; }")
rep("  steerId = null; steerIn = 0; rangeIn = 0; holdCharge = false; slingOff();\n};", "  steerId = null; steerIn = 0; rangeIn = 0; holdCharge = false; slingOff(); P.preJ = 0;\n};")
rep("  D.air = true; D.vy = JUMP_V; D.airSling = true; D.stroke++; D.squash = 0; D.buf = 0; fxLaunch(D, 1);", "  D.air = true; D.vy = JUMP_V; D.airSling = true; D.stroke++; D.squash = 0; D.buf = 0; D.preJ = 0; fxLaunch(D, 1);")
rep("  if (D.buf > 0) D.buf -= dt;", "  if (D.buf > 0) D.buf -= dt; if (D.preJ > 0) D.preJ -= dt;")
# ---- the slingshot's ball: a ball for the whole flight, the axolotl back just before it lands (to land on its feet)
rep("  const flK0 = flA0 ? smoothstep(0.3, 0.78, D.flingC || 0) * smoothstep(-0.15, 0.55, (D.vy || 0) / V.flV0) : 0;",
    "  let tl0 = 9; if (flA0) { const gg = surfaceUnder(D.x, D.z, D.y + STEP, true), hh = Math.max(0, D.y - (gg > -Infinity ? gg : D.y - 9)), vy = D.vy || 0, g2 = GRAV * 1.45; tl0 = vy > 0 ? vy / GRAV + Math.sqrt(2 * (hh + vy * vy / (2 * GRAV)) / g2) : (vy + Math.sqrt(vy * vy + 2 * g2 * hh)) / g2; } /* (how soon it lands) */\n  const flK0 = flA0 ? smoothstep(0.3, 0.78, D.flingC || 0) * (tl0 > (V.balled ? 0.22 : 0.3) ? 1 : 0) : 0; /* (a ball for the whole flight, back to the axolotl just before it lands) */")
rep('<p class="ver">Version 236</p>', '<p class="ver">Version 237</p>')
open(DST, 'w').write(s)
print('ui170 ok', n0, '->', len(s))
