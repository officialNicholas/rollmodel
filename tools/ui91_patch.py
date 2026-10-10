#!/usr/bin/env python3
"""Knocked out: the paint flood waits a beat so you see yourself splatted first (the burst, the ring, the slow-down), then it floods in with the badge. On top of ui90_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui90_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  kof = { ph: 'in', t: 0, col, cx: viewW * 0.5, cy: viewH * 0.5, seed: Math.random() * 100 };",
    "  kof = { ph: 'wait', t: 0, col, cx: viewW * 0.5, cy: viewH * 0.5, seed: Math.random() * 100 }; // (a beat first: you see yourself splatted, then the paint floods in)")
rep("  kofEl.style.setProperty('--kc', col); kofEl.hidden = false; kofEl.classList.remove('badge', 'out'); AU.kflood();\n}",
    "  kofEl.style.setProperty('--kc', col); kofEl.hidden = false; kofEl.classList.remove('badge', 'out');\n}\nconst KOF_WAIT = 0.85; // seconds of real time before the flood, long enough to read the splat under the slow-down")
rep("  if (kof.ph === 'in') { const u = Math.min(1, t / 0.5),",
    "  if (kof.ph === 'wait') { if (t >= KOF_WAIT) { kof.ph = 'in'; kof.t = 0; AU.kflood(); } return; }\n  if (kof.ph === 'in') { const u = Math.min(1, t / 0.5),")
# an early comeback while still waiting: nothing to part, just end
rep("function kofOpen() { if (!kof) return; kof.ph = 'out';", "function kofOpen() { if (!kof) return; if (kof.ph === 'wait') return kofEnd(); kof.ph = 'out';")
rep('<p class="ver">Version 160</p>', '<p class="ver">Version 161</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui91 ok', n0, '->', len(s))
