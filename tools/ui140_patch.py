#!/usr/bin/env python3
"""v212: commissions you can actually finish. Half the canvas (50% in one match) was out of reach; the coverage jobs now sit between 25%
and 35%. A job counts the whole number the results show (34.6% reads 35% and pays a Cover 35%), and a job retired from the list drops
out of today's set instead of breaking it."""
import subprocess, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui139_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the jobs: a quarter of the canvas and 35% in any match, and a solo show inside the same range
rep("{ id: 'solo40', t: 'Solo show', d: 'Cover 40% in a solo match', n: 1, k: 'solo', v: 40 }", "{ id: 'solo30', t: 'Solo show', d: 'Cover 30% in a solo match', n: 1, k: 'solo', v: 30 }")
rep("{ id: 'cov50', t: 'Half the canvas', d: 'Paint 50% of a canvas in one match', n: 1, k: 'cov', v: 50 }", "{ id: 'cov25', t: 'Quarter canvas', d: 'Paint 25% of a canvas in one match', n: 1, k: 'cov', v: 25 }")
# a job no longer on the list (saved in today's set before it changed) drops out, and a fresh one is dealt in its place
rep("store.commSeen = 0; } c.day = day; save(); } } /* (a fresh set every day) */ while (c.active.length < 3) {",
    "store.commSeen = 0; } c.day = day; save(); } } /* (a fresh set every day) */ c.active = c.active.filter(id => COMMS.some(x => x.id === id)); while (c.active.length < 3) {")
# judged on the whole number the results screen shows
rep("else if (k.k === 'cov' && info.you >= k.v) p = 1;", "else if (k.k === 'cov' && Math.round(info.you) >= k.v) p = 1;")
rep("else if (k.k === 'solo' && info.mode === 'solo' && info.you >= k.v) p = 1;", "else if (k.k === 'solo' && info.mode === 'solo' && Math.round(info.you) >= k.v) p = 1;")
rep('<p class="ver">Version 211</p>', '<p class="ver">Version 212</p>')
open(DST, 'w').write(s)
print('ui140 ok', n0, '->', len(s))
