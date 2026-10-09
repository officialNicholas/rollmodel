#!/usr/bin/env python3
"""The lobby stats read as a readout, not as buttons. On top of ui23_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui23_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
css = '''
/* the lobby stats: ink written straight on the paper, no plate, no tape, no shadow: nothing that says "press me" */
.lcol.right .plate.stat{background:none;box-shadow:none;border:0;border-radius:0;width:76px;padding:2px 2px 6px;gap:0;animation:none;cursor:default}
.lcol.right .plate.stat::before,.lcol.right .plate.stat::after{display:none}
.lcol.right .plate.stat svg{width:20px;height:20px;color:var(--ink);opacity:.95}
.lcol.right .plate.stat b{font:900 27px/1 var(--font-head);font-style:italic;letter-spacing:-.03em;color:#17131F;padding-top:1px;text-shadow:.07em .07em 0 rgba(var(--ink-rgb),.28)}
.lcol.right .plate.stat span{font:800 8.5px/1 var(--font-ui);letter-spacing:.16em;color:var(--muted);margin-top:1px}
.lcol.right .plate.stat.drops b{gap:4px}
.lcol.right .plate.stat.drops b .dropi{width:13px;height:16px;filter:none}
.lcol.right .plate.stat+.plate.stat{border-top:2px dashed rgba(23,19,32,.14);padding-top:6px}
.lcol.right{gap:4px}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 93</p>', '<p class="ver">Version 94</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
