#!/usr/bin/env python3
"""v186: commissions show both rewards they pay, XP and dabs, on the cards, on the results and in the note."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui110_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('const COMM_XP = 60;', 'const COMM_XP = 60, COMM_DABS = 20;')
rep('+ fin.length * 20;', '+ fin.length * COMM_DABS;')
rep("<b class=\"cr\">+' + COMM_XP + ' XP</b>", "<b class=\"cr\"><span>+' + COMM_XP + ' XP</span><span>+' + COMM_DABS + DROP_SVG + '</span></b>")
rep("Commission done: ' + k.t + '<b>+' + COMM_XP + ' XP</b>", "Commission done: ' + k.t + '<b>+' + COMM_XP + ' XP &middot; +' + COMM_DABS + ' dabs</b>")
rep('<p class="cnote small">Three jobs at a time. Finish one for reputation, and a new one comes in.</p>', '<p class="cnote small">Three jobs at a time, fresh every day. Each one pays XP and dabs, and a new one comes in.</p>')
rep('.comm .cr{font:900 12px/1 var(--font-head);color:var(--gold-lo);white-space:nowrap}', '.comm .cr{font:900 12px/1 var(--font-head);color:var(--gold-lo);white-space:nowrap;display:grid;justify-items:end;gap:6px}\n.comm .cr span{display:inline-flex;align-items:center;gap:3px}\n.comm .cr .dropi{width:15px;height:15px}')
rep('<p class="ver">Version 185</p>', '<p class="ver">Version 186</p>')
open(DST, 'w').write(s)
print('ui111 ok', n0, '->', len(s))
