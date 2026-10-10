#!/usr/bin/env python3
"""The pound button's corner dial drops its paint state. Short of paint the dial stays hidden (the button itself still reads as off); the dial shows only the cooldown's count. On top of ui88_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui88_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("let frac = -1, n = '', kind = ''; // the dial on the button's corner: short of paint it shows a drop and your paint, else the cooldown's count\n    if (!rk && P.st === 'play' && !P.slam) { if (P.paint < POUND_MIN) { frac = Math.min(1, P.paint / POUND_MIN); kind = 'paint'; } else if (P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = String(Math.ceil(P.slamCD)); kind = 'cd'; } }",
    "let frac = -1, n = '', kind = ''; // the dial on the button's corner: the cooldown's count (short of paint, nothing: the button is simply off)\n    if (!rk && P.st === 'play' && !P.slam && P.paint >= POUND_MIN && P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = String(Math.ceil(P.slamCD)); kind = 'cd'; }")
rep("      const v = kind === 'paint' ? '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M12 2.5C9.2 7.2 6.4 10.6 6.4 14.1a5.6 5.6 0 0 0 11.2 0c0-3.5-2.8-6.9-5.6-11.6z\"/></svg>' : n; if ($('sbN').dataset.v !== v)",
    "      const v = n; if ($('sbN').dataset.v !== v)")
rep('.sbdial[data-k="paint"]{--pc:#CFC6E0}\n.sbdial[data-k="paint"] b svg{width:14px;height:14px;fill:#fff;filter:drop-shadow(0 1.5px 0 var(--black))}\n', '')
rep('<p class="ver">Version 158</p>', '<p class="ver">Version 159</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui89 ok', n0, '->', len(s))
