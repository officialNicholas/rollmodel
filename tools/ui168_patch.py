#!/usr/bin/env python3
"""v235: the axolotl's new look (the look agent's v9b: axo/tools5): a flatter face front and chin, a thicker, shorter neck, a rounder back,
the gills as soft lobes hanging from the ear position like the slime's floppy ears (on a looser spring that lags, swings out on turns and
settles), a crisp catchlight, a little more saturated colour, a gentle wobble, and the paint coat after the slime's: a soft wet edge, runs
and beads sliding down, the wading band swelling round it, the skin staying wet then drying from the top, and the face kept clear. The new
mesh ships as axo-pack-235.txt, so a phone never pairs a cached old mesh with the new runtime."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui167_patch.py'], check=True, env=dict(os.environ, AXO_BASE=S + '/tools/assets/axo_base_v235.js'))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'sCatch' in s and 'gillSpring.k = 110' in s and 'lo = 0.7' in s, 'the v235 runtime and animator are not in the build'
rep("AXOC.load(window.AXO_PACK || 'axo-pack.txt')", "AXOC.load(window.AXO_PACK || 'axo-pack-235.txt')")
rep('<p class="ver">Version 234</p>', '<p class="ver">Version 235</p>')
open(DST, 'w').write(s)
print('ui168 ok', n0, '->', len(s))
