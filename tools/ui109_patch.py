#!/usr/bin/env python3
"""v184: the tally no longer throws the big full-screen splat (with its burst and flash) when the winner is called."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui108_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("""  const sp = $('tySplash'); sp.style.setProperty('--c', e ? e.col : '#F4EEE3'); sp.className = 'tysplash'; void sp.offsetWidth; sp.className = 'tysplash go';
  AU.tsplash(); buzz(w === P ? [30, 40, 30] : 20); flashScreen(); tyBurst(talEl, viewW / 2, viewH / 2, Math.min(viewW, viewH) * 1.6, w ? w.team : 0); // (the winner screen says who; here the paint says it)""",
"""  AU.tsplash(); buzz(w === P ? [30, 40, 30] : 20); /* (no full-screen splat here: the winner screen right after says who) */""")
rep('<p class="ver">Version 183</p>', '<p class="ver">Version 184</p>')
open(DST, 'w').write(s)
print('ui109 ok', n0, '->', len(s))
