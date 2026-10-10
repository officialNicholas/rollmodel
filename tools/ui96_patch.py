#!/usr/bin/env python3
"""The freeze: the steering lean (v158) added to a const, which threw the moment you steered hard near a basin, a pick-up, the orb or a ramp, and the frame loop died with it. The lean now has its own variable. On top of ui95_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui95_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  if (D === P && !P.ai && !D.air && !D.charging && Math.abs(input) > 0.4 && D.spd > 0.8) { const st = steerTarget(D, input); if (st) want += -clamp(st.err, -1, 1) * TURN * 0.6 * Math.min(1, Math.abs(input) * 1.4); } // (the lean the rest of the way)\n  D.turn += (want - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (want * D.turn < 0 ? 50 : 36) : 20));",
    "  let lean = 0; if (D === P && !P.ai && !D.air && !D.charging && Math.abs(input) > 0.4 && D.spd > 0.8) { const st = steerTarget(D, input); if (st) lean = -clamp(st.err, -1, 1) * TURN * 0.6 * Math.min(1, Math.abs(input) * 1.4); } // (the lean the rest of the way, on top of what you asked for)\n  const wantL = want + lean; D.turn += (wantL - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (wantL * D.turn < 0 ? 50 : 36) : 20));")
rep('<p class="ver">Version 165</p>', '<p class="ver">Version 166</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui96 ok', n0, '->', len(s))
