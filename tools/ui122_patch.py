#!/usr/bin/env python3
"""v197: the dodge lessons lock the pound button (greyed, taps fall through to the swipe) and the swipe hand sits mid-screen; the dodge
timing is forgiving (NOW comes late enough that an instant swipe covers the landing, and a roll in the window holds till it lands); and two
seconds after the fling the tank drains and a basin rises just ahead of you (that half lives in tools/assets/tutorial.js and .css)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui121_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function useSlam(D) {\n  if (D === P) kick($('slamBtn'), 'press');", "function useSlam(D) {\n  if (D === P && tut && tut.noPound) return false; /* (the dodge lessons: the pound is locked) */\n  if (D === P) kick($('slamBtn'), 'press');")
rep("  if (!show) { wasReady = false; return; }\n", "  if (!show) { wasReady = false; return; }\n  { const lk = !!(tut && tut.noPound); if (b._lk !== lk) { b._lk = lk; b.classList.toggle('locked', lk); } }\n")
rep(".slamBtn svg{width:40px;", ".slamBtn.locked{opacity:.35;filter:grayscale(1);pointer-events:none!important}\n.slamBtn svg{width:40px;")
rep('<p class="ver">Version 196</p>', '<p class="ver">Version 197</p>')
open(DST, 'w').write(s)
print('ui122 ok', n0, '->', len(s))
