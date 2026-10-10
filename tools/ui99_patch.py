#!/usr/bin/env python3
"""The coach stays down while any dialog is up: the orientation chooser (which it sat over on a first launch), and every modal. On top of ui98_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui98_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("const tutBootEl = $('boot');\nfunction tutMenuTick() {\n  if (bootHold || !booted || !tutBootEl.classList.contains('gone')) return tutHide();",
    "const tutBootEl = $('boot'), tutOrientEl = $('orient');\nfunction tutMenuTick() {\n  if (bootHold || !booted || !tutBootEl.classList.contains('gone') || !tutOrientEl.hidden || document.querySelector('.modal:not([hidden])')) return tutHide(); // (nothing over the loading screen, the orientation chooser or any dialog)")
rep('<p class="errline" id="errLine" hidden></p>', '<p class="errline" id="errLine" hidden></p><i class="tuthand" id="tutHand" hidden aria-hidden="true"></i><i class="tutarrow" id="tutArrow" hidden aria-hidden="true"><svg viewBox="0 0 48 48"><path d="M8 17h18V7l17 17-17 17V31H8z"/></svg></i>')
rep('function aiRocket(D, dt) {\n  const R = D.rocket;', 'function aiRocket(D, dt) {\n  if (tut && tut.rocketLock === D) return tutRocket(D, dt); // (the lesson flies this one)\n  const R = D.rocket;')
rep("gift.on = true; gift.x = s[0]; gift.z = s[1]; gift.y = 0; gift.t = 0; gift.pop = 0; banner('Something rare!', 'An item has turned up. Go grab it', true);", "gift.on = true; gift.x = s[0]; gift.z = s[1]; gift.y = 0; gift.t = 0; gift.pop = 0; if (!tut) banner('Something rare!', 'An item has turned up. Go grab it', true); /* (the lesson says it itself) */")
rep("  if (D === P) { shake = Math.max(shake, 0.35); buzz([20, 15, 40]); flashScreen(); fovKick = 8; banner('Rocket!', say('Steer, then Boost down', 'Steer, then E to drop')); }\n  else { banner(", "  if (D === P) { shake = Math.max(shake, 0.35); buzz([20, 15, 40]); flashScreen(); fovKick = 8; if (!tut) banner('Rocket!', say('Steer, then Boost down', 'Steer, then E to drop')); }\n  else if (!tut) { banner(")
rep('<p class="ver">Version 168</p>', '<p class="ver">Version 172</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui99 ok', n0, '->', len(s))
