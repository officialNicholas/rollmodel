#!/usr/bin/env python3
"""The Paint Shop tile at the end of each locker rail is gone; the shop is reached from the dabs in the locker's header. An empty rail says so in a line instead. On top of ui76_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui76_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
a = s.index("+ (forSale ? '<button class=\"ltile shopgo\""); b = s.index("</button>' : '');", a) + len("</button>' : '');")
s = s[:a] + "+ (mine.length ? '' : '<p class=\"lnone\">Nothing here yet. The Paint Shop has ' + forSale + ' to buy.</p>');" + s[b:]
css = '''
.lnone{align-self:center;margin:0 auto;padding:6px 12px;font:700 12px/1.3 var(--font-ui);color:var(--muted);text-align:center;max-width:26ch}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
