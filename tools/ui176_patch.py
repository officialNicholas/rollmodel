#!/usr/bin/env python3
"""v240: Season One is called Spooky SZN everywhere a player reads it (the lobby tag and the logo, the canvases page, the shop banner and
heading, the locker wall sign, the credits, the lesson's line). The stage keys stay as they were."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui175_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<span class="tape exhib" id="seasonTag"><b>Season 1</b> Halloween</span>', '<span class="tape exhib" id="seasonTag"><b>Season 1</b> Spooky SZN</span>')
rep('<span class="season"><b>Season 1</b>Halloween</span>', '<span class="season"><b>Season 1</b>Spooky SZN</span>')
rep('<span class="ribbon">Season 1</span><span class="plaque"><b class="wn">Halloween</b></span>', '<span class="ribbon">Season 1</span><span class="plaque"><b class="wn">Spooky SZN</b></span>')
rep('aria-label="Halloween canvases"', 'aria-label="Spooky SZN canvases"')
rep("const SEASON = { n: 1, name: 'Halloween',", "const SEASON = { n: 1, name: 'Spooky SZN',")
rep("halloween: 'the Halloween stages' }", "halloween: 'the Spooky SZN stages' }")
rep("['season', 'Season One · <em class=\"hw\">Halloween</em>']", "['season', 'Season One · <em class=\"hw\">Spooky SZN</em>']")
rep('<b class="sbtitle">Halloween</b><small>Find these on the Halloween canvases</small>', '<b class="sbtitle">Spooky SZN</b><small>Find these on the Spooky SZN canvases</small>')
rep('<p>Season 1: Halloween</p>', '<p>Season 1: Spooky SZN</p>')
rep("tutShow('It\\u2019s Halloween season! Fangs are also on sale! Grab it'", "tutShow('It\\u2019s Spooky SZN! Fangs are also on sale! Grab it'")
rep("g.strokeText('HALLOWEEN', 34, 228)", "g.strokeText('SPOOKY SZN', 34, 228)")
rep("g.fillText('HALLOWEEN', 34, 228)", "g.fillText('SPOOKY SZN', 34, 228)")
open(DST, 'w').write(s)
print('ui176 ok', n0, '->', len(s))
