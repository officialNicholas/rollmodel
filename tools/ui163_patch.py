#!/usr/bin/env python3
"""v230: the swim reworked (the hands pull it forward, it glides, slows a touch into a couple of crawl steps, pulls again; the lower trunk
and the tail do the swinging, the head and chest held to the line; turns steered with the arms, the tail following in a C; the gills
swing out round turns). And the win screen: the winner lands on all fours, rises up for its jumps, and settles back down onto all fours
between them, one smooth morph each way."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui162_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'swMark' in s and "D.vicPose.stand === false" in s
# the win screen's rhythm: down on all fours from the drop until it rises (a morph of about three quarters of a second), the big jump and two
# little ones standing, then back down for a beat; and again
rep("""  else { const c = (tt - 0.78) % 2.7;
    // (its tail swings round to the left for one jump, the right for the next)
    const cyc = Math.floor((tt - 0.78) / 2.7), dir = cyc % 2 ? -1 : 1;
    if (vic.happy) { if (c < 1.08) { vicJump(c, 0.47, 0.26, 0.62, o, dir); o.side = dir; } else { const j = Math.floor((c - 1.08) / 0.54); vicJump((c - 1.08) % 0.54, 0.17, 0.13, 0.3, o); o.side = j % 2 ? 1 : -1; } }
    else { vicJump(c % 0.9, 0.07, 0.17, 0.24, o); o.side = Math.floor(c / 0.9) % 2 ? 1 : -1; } }
  return o;""",
"""  else if (tt >= VIC_C0) { const T = vic.happy ? VIC_T : VIC_TS, c = (tt - VIC_C0) % T;
    // (its tail swings round to the left for one jump, the right for the next)
    const cyc = Math.floor((tt - VIC_C0) / T), dir = cyc % 2 ? -1 : 1;
    if (vic.happy) { if (c < 1.08) { vicJump(c, 0.47, 0.26, 0.62, o, dir); o.side = dir; } else if (c < 2.16) { const j = Math.floor((c - 1.08) / 0.54); vicJump((c - 1.08) % 0.54, 0.17, 0.13, 0.3, o); o.side = j % 2 ? 1 : -1; } }
    else if (c < 1.8) { vicJump(c % 0.9, 0.07, 0.17, 0.24, o); o.side = Math.floor(c / 0.9) % 2 ? 1 : -1; } }
  // up on its hind legs for the jumps (rising a beat before them), down on all fours from the drop and between rounds
  { const T = vic.happy ? VIC_T : VIC_TS, c = tt - VIC_C0 < 0 ? tt - VIC_C0 : (tt - VIC_C0) % T; o.stand = tt > 0.6 && (c < 0 || c < (vic.happy ? 2.3 : 1.9) || c > T - 1.0); }
  return o;""")
rep("function vicPose(i, t) {", "const VIC_C0 = 1.9, VIC_T = 5.2, VIC_TS = 4.2; // (the jumps' first round, after the drop and the rise; one round, happy or not)\nfunction vicPose(i, t) {")
rep("cyc = Math.floor((tt - 0.78 - 0.9) / 2.7);", "cyc = Math.floor((tt - VIC_C0 - 0.9) / (vic.happy ? VIC_T : VIC_TS));")
rep('<p class="ver">Version 229</p>', '<p class="ver">Version 230</p>')
open(DST, 'w').write(s)
print('ui163 ok', n0, '->', len(s))
