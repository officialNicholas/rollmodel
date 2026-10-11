#!/usr/bin/env python3
"""v192: the menu song no longer opens with its lone bell. Started fresh, it begins at the downbeat (1.08 s in), so the first thing you
hear a couple of seconds after the menu loads (when the song has decoded) is the song, not a chime."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui116_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(lvl, t + (fadeIn || 0.03)); src.connect(g); g.connect(trkBus); off = Math.max(0, Math.min(off || 0, src.loopEnd - 0.01));",
    "if (!off && key === 'menu') { off = 1.08; fadeIn = Math.max(fadeIn || 0, 0.25); } /* (the menu song opens on a lone bell before its first beat: start on the beat) */\n    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(lvl, t + (fadeIn || 0.03)); src.connect(g); g.connect(trkBus); off = Math.max(0, Math.min(off || 0, src.loopEnd - 0.01));")
rep('<p class="ver">Version 191</p>', '<p class="ver">Version 192</p>')
open(DST, 'w').write(s)
print('ui117 ok', n0, '->', len(s))
