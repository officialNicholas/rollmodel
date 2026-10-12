#!/usr/bin/env python3
"""v240: the wet-dog shake before the paint flies off, out of the basin at a match start and out of the locker's pool."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui176_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'Animator.prototype.stepShake' in s, 'the shake is not in the animator'
# the match: the paint flies off a third of a second into the shake (it used to go at a fifth)
rep("if (!SH || SH.t >= 0.2 || state !== 'intro') { I.coatBurst(0.001);", "if (!SH || SH.t >= 0.32 || state !== 'intro') { I.coatBurst(0.001);")
# the locker: it shakes as it lands out of the pool, and the paint goes a third of a second in
rep("if (t >= CR.land && !I.landed) { I.landed = true; I.rip = 0.6; buzz(10); shake = Math.max(shake, 0.03); }",
    "if (t >= CR.land && !I.landed) { I.landed = true; I.rip = 0.6; buzz(10); shake = Math.max(shake, 0.03); if (V && V.slime && V.slime.shake) V.slime.shake(1); }")
rep("(D === P && lookIntro && lookIntro.crawl && lookIntro.t < lookIntro.land))", "(D === P && lookIntro && lookIntro.crawl && lookIntro.t < lookIntro.land + 0.32))")
open(DST, 'w').write(s)
print('ui177 ok', n0, '->', len(s))
