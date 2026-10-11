#!/usr/bin/env python3
"""v229: the lesson's gift line reads "A gift has appeared on the canvas! Grab it!". And after the shop lesson, Ol' Bloop no longer points
you straight at Back: he says take a look around, squirt, express yourself, up top with nothing dimmed, then steps aside after a few seconds
so you can browse; once you leave the shop on your own the locker step carries on."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui161_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("tutShow('Something rare! *GRAB IT!*',", "tutShow('A gift has appeared on the canvas! *Grab it!*',", 2)
rep("let tut2 = null, tut = null, tutPrev = null, tutTip = null, tutWinDue = false, tutNiAt = 0, tutFirstAt = 0;",
    "let tut2 = null, tut = null, tutPrev = null, tutTip = null, tutWinDue = false, tutNiAt = 0, tutFirstAt = 0, tutBrowseAt = 0; // tutBrowseAt: when the free look round the shop began")
rep("  if (ph === 'locker') {\n    if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back');",
    "  if (ph === 'locker') {\n    if (shopOpen) { if (!tutBrowseAt) tutBrowseAt = performance.now(); if (performance.now() - tutBrowseAt > 4200) return tutHide(); return tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); } /* (a free look round the shop: no pointing at Back, he steps aside after a few seconds; leaving on your own goes on to the locker) */")
rep('<p class="ver">Version 228</p>', '<p class="ver">Version 229</p>')
open(DST, 'w').write(s)
print('ui162 ok', n0, '->', len(s))
