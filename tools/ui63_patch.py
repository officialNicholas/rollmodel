#!/usr/bin/env python3
"""The drip of paint hanging off the lobby logo goes. On top of ui62_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui62_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
a = s.index('.mhome.lobby .logo .tcard::after{content:"";position:absolute;left:30%;top:74%'); b = s.index('}', a) + 1
s = s[:a] + s[b:]
rep(".mhome.lobby .logo .tcard::after,.mhome.lobby .season,.slamBtn.ready,.slamBtn.boost.ready{animation:none}", ".mhome.lobby .season,.slamBtn.ready,.slamBtn.boost.ready{animation:none}")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
