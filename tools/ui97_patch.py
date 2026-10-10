#!/usr/bin/env python3
"""The coach waited over the loading screen: on a phone the game holds at Tap to start until a tap, and the dim sat over that with its window on the Play button, so nothing could be tapped. No tip, and no dim, until the loading screen is gone. On top of ui96_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui96_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function tutMenuTick() {\n  const ph = tutPh();", "const tutBootEl = $('boot');\nfunction tutMenuTick() {\n  if (bootHold || !booted || !tutBootEl.classList.contains('gone')) return tutHide(); // (nothing over the loading screen: its tap to start must get through)\n  const ph = tutPh();")
rep("const type = itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret');", "const type = tut && tut.noTurret ? 'roller' : itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret'); // (the lesson: rollers only until the flower is found)")
rep("  D.power = null; D.rocket = { ph: 'up', t: 0, y0: D.y, top: Math.max(D.y, 0) + ROCKET_ALT, gy: D.y, id: Math.random() };", "  D.power = null; D.rocket = { ph: 'up', t: 0, y0: D.y, top: Math.max(D.y, 0) + ROCKET_ALT, gy: D.y, id: Math.random() }; D.inkRush = true; if (D === P) pingTank(1.4); // (a rocket comes with a full tank)")
rep('<p class="ver">Version 166</p>', '<p class="ver">Version 167</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui97 ok', n0, '->', len(s))
