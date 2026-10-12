#!/usr/bin/env python3
"""v236 (on v234's look; v235's new head is set aside for the slime-head transplant): the swim stroke drives the blob's real pace. A short slow
beat as the limbs come out to reach, a surge through the pull, a touch fast through the glide, a touch slow through the steps; it averages
exactly 1 over a stroke, so the distance covered and the match's pace are unchanged. The game moves the blob (and lays its stream) by it."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui167_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'Animator.prototype.strokeMul' in s and 'D.strokeK = A.strokeMul' in s and 'gillSpring.k = 230' in s
rep("fz = Math.cos(D.yaw) * (back ? -1 : 1), d = D.spd * dt, x0 = D.x, z0 = D.z,", "fz = Math.cos(D.yaw) * (back ? -1 : 1), d = D.spd * dt * (D.air ? 1 : (D.strokeK || 1)) /* (swimming: the pace follows the stroke) */, x0 = D.x, z0 = D.z,")
rep("D.dist += D.spd * dt; const fx = D.x + Math.sin(D.yaw) * TRAIL_FWD,", "D.dist += D.spd * dt * (D.strokeK || 1); const fx = D.x + Math.sin(D.yaw) * TRAIL_FWD,")
rep('<p class="ver">Version 234</p>', '<p class="ver">Version 236</p>')
open(DST, 'w').write(s)
print('ui169 ok', n0, '->', len(s))
