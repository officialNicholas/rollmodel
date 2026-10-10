#!/usr/bin/env python3
"""Two things. In the locker, a paint change no longer makes the blob hop every time: it hops for the first pick, then once in a while (the splat and the sound stay). The vote goes to the canvas with the most votes; only a tie is drawn. On top of ui93_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui93_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  menuReact = 0.7; AU.pop(); AU.splat(same ? 0.4 : 0.8);\n  if (state === 'menu') { addSplat(P.x, P.y, P.z, P.yaw, 0.9, -8, false, false, 0);",
    "  { const now = performance.now(); if (!(now - (pickColor.hopAt || -1e9) < 5000)) { menuReact = 0.7; pickColor.hopAt = now; } } AU.pop(); AU.splat(same ? 0.4 : 0.8); // (a hop for the first pick, then no more than one every few seconds: browsing the swatches is not a trampoline)\n  if (state === 'menu') { addSplat(P.x, P.y, P.z, P.yaw, 0.9, -8, false, false, 0);")
rep("const tickets = [...votes.values()], win = tutV || tickets[(Math.random() * tickets.length) | 0],",
    "const tickets = [...votes.values()], tally = {}; for (const t of tickets) tally[t] = (tally[t] || 0) + 1; const top = Math.max(...Object.values(tally)), lead = Object.keys(tally).filter(k => tally[k] === top); // (most votes wins; only a tie is drawn)\n    const win = tutV || (lead.length === 1 ? lead[0] : lead[(Math.random() * lead.length) | 0]),")
rep("$('vvLbl').textContent = 'Vote for a canvas \\u00b7 one vote is drawn';", "$('vvLbl').textContent = 'Vote for a canvas \\u00b7 most votes wins, a tie is drawn';")
rep("Your rivals vote too, and one vote is drawn before the match.'", "Your rivals vote too. Most votes wins, and a tie is drawn.'")
if "tutShow('Pick a canvas: that is your vote. Rivals vote too, and one vote is drawn. Then Start', 'startBtn', 'start')" in s: rep("tutShow('Pick a canvas: that is your vote. Rivals vote too, and one vote is drawn. Then Start', 'startBtn', 'start')", "tutShow('Pick a canvas: that is your vote. Rivals vote too, and most votes wins. Then Start', 'startBtn', 'start')")
rep('<p class="ver">Version 163</p>', '<p class="ver">Version 164</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui94 ok', n0, '->', len(s))
