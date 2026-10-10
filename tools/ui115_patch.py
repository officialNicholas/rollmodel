#!/usr/bin/env python3
"""v190: in the lesson the "Paint it red!" start banner stays up half as long, the first tip follows straight after it, and the tips
that ask for a gesture show an animated finger acting it out (drag and tap, hold and pull down, flick up; the finger itself is in
tools/assets/tutorial.js and .css)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui114_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function banner(big, small, long) { bannerUntil = performance.now() + (long ? 3400 : 2100);", "function banner(big, small, long, quick) { bannerUntil = performance.now() + (quick ? 1700 : long ? 3400 : 2100);")
rep("bannerEl.classList.toggle('long', !!long);", "bannerEl.classList.toggle('long', !!long); bannerEl.classList.toggle('quick', !!quick);")
rep("banner('Paint it ' + colorOf().name.toLowerCase() + '!', mode === 'solo' ? '60 seconds' : mode === 'trio' ? 'Everyone for themselves' : TH.label, true); }, 900);",
    "banner('Paint it ' + colorOf().name.toLowerCase() + '!', mode === 'solo' ? '60 seconds' : mode === 'trio' ? 'Everyone for themselves' : TH.label, true, !!tut); }, 900); /* (the lesson: half as long, the first tip right after) */")
rep(".banner.on.long{animation-duration:3.4s}", ".banner.on.long{animation-duration:3.4s}\n.banner.on.long.quick{animation-duration:1.7s}")
rep(".banner.on.long .plate{animation-duration:3.4s}", ".banner.on.long .plate{animation-duration:3.4s}\n.banner.on.long.quick .plate{animation-duration:1.7s}")
rep('<p class="ver">Version 189</p>', '<p class="ver">Version 190</p>')
open(DST, 'w').write(s)
print('ui115 ok', n0, '->', len(s))
