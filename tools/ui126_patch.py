#!/usr/bin/env python3
"""v201: the lobby character keeps its lines to itself while the onboarding runs (Ol' Bloop does the talking then): no timed lines and no line
on a tap until the lesson, the shop, the locker, the vote and the welcome are all done."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui125_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function sayTick(rdt) { if (!(state === 'menu' && menuPage === 'home' && !lookOpen && $('orient').hidden)) {",
    "const onboarding = () => !!(store.tut && store.tut.ph && store.tut.ph !== 'done'); // (Ol' Bloop is talking: the lobby character keeps quiet)\nfunction sayTick(rdt) { if (!(state === 'menu' && menuPage === 'home' && !lookOpen && $('orient').hidden) || onboarding()) {")
rep("AU.init(); menuReact = 0.7; AU.pop(); sayRandom(); if (Math.random() < 0.6)", "AU.init(); menuReact = 0.7; AU.pop(); if (!onboarding()) sayRandom(); if (Math.random() < 0.6)")
rep('<p class="ver">Version 200</p>', '<p class="ver">Version 201</p>')
open(DST, 'w').write(s)
print('ui126 ok', n0, '->', len(s))
