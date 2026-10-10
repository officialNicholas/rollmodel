#!/usr/bin/env python3
"""The loading screen keeps just the bar: the stream pouring in from above (and the drops where it landed) are gone; the paint still spreads along the bar with its rolling top, wet shine and drips. On top of ui72_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui72_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
a = s.index("    // the stream: from the top of the screen down onto the paint, swaying a touch, thinner as it falls, with a shine down one side"); b = s.index("    } catch (e) { run = false; if (bar) bar.classList.add('plain'); return; }", a)
s = s[:a] + s[b:]
rep("const x = L + i / N * (xf - L), dl = (x - land) / 18, y = T + 1.5 + 1.2 * Math.sin(i * 0.8 + t * 4.4) + 0.9 * Math.sin(i * 1.9 - t * 6.1) - 3 * Math.exp(-dl * dl) * (0.6 + 0.4 * Math.sin(t * 11));",
    "const x = L + i / N * (xf - L), y = T + 1.5 + 1.2 * Math.sin(i * 0.8 + t * 4.4) + 0.9 * Math.sin(i * 1.9 - t * 6.1);")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
