#!/usr/bin/env python3
"""The shop's season plate is pinned to pumpkin orange (it used to take your paint color) and writes "Halloween" in red. On top of ui89_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui89_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("const SHOP_CATS = [['season', 'Season One · Halloween'],", "const SHOP_CATS = [['season', 'Season One · <em class=\"hw\">Halloween</em>'],")
rep(".shcat.season small{color:rgba(255,255,255,.8)}", ".shcat.season small{color:rgba(255,255,255,.8)}\n.shcat.season{background:#F08A24}\n.shcat.season b{color:#fff}\n.shcat.season b .hw{font-style:normal;color:#E3122F;text-shadow:2px 2px 0 rgba(23,19,32,.45)}")
rep('<p class="ver">Version 159</p>', '<p class="ver">Version 160</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui90 ok', n0, '->', len(s))
