#!/usr/bin/env python3
"""v252: the character, more alive (v252_anim.py). Its ears curve through a turn, lift on a hop, flop about in a shake and twitch on
their own; new faces (sleepy, wink, worried, determined, a smile, a blep, a frown, a :3) and a face held for each mood; the home screen's
moods (dozing off and jolting awake, a sneeze, a wet-dog shake, a proud wink, a blep, a wave, a peekaboo); a sniff now and then; a
determined squint swimming flat out and a smirk when ahead; the locker's crawl-out climbs out of a hole in the paint instead of rising up
out of it; a cleaner swim stroke and a shorter scurry before it."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui191_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="ver">Version 251</p>', '<p class="ver">Version 252</p>')
import sys as _sys; _sys.path.insert(0, S + '/tools'); import v252_anim
s = v252_anim.apply(s)
open(DST, 'w').write(s); print('ui192 ok', n0, '->', len(s))
