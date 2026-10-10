#!/usr/bin/env python3
"""Choosing a canvas reads as what it is. In 1v1 and 3-way the canvas you choose is your vote: the page says so, the Play button says so, the lobby card says so, and the vote itself tags your card and says one vote is drawn. In solo it is your canvas, full stop, and plays as chosen. The CPU difficulty stays a setting that is honoured. On top of ui85_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui85_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the note under the gallery: always there, saying what the choice is
rep("  $('stages').hidden = mode === 'solo'; const sn = $('soloNote'); sn.hidden = mode !== 'solo';", "  $('stages').hidden = mode === 'solo'; const sn = $('soloNote'); sn.hidden = false;")
rep("  $('cvName').textContent = TH.label; $('shuffleBtn').setAttribute('aria-label', 'Shuffle the canvas. Now: ' + TH.label);",
    "  $('cvName').textContent = (mode === 'solo' ? '' : 'Your vote \\u00b7 ') + TH.label; $('shuffleBtn').setAttribute('aria-label', (mode === 'solo' ? 'Shuffle the canvas. Now: ' : 'Shuffle your vote. Now: ') + TH.label);\n  { const sn = $('soloNote'); sn.innerHTML = mode === 'solo' ? '<b>Your canvas:</b> ' + escAttr(TH.label) + '. Solo plays the canvas you choose.' : '<b>Your vote:</b> ' + escAttr(TH.label) + '. Your rivals vote too, and one vote is drawn before the match.'; sn.hidden = false; }")
rep('<small>Canvases &middot; your pick</small>', '<small id="lobbyPickLbl">Canvases &middot; your vote</small>')
rep('<button class="show" id="stageBtn" type="button" aria-label="Pick the exhibition">', '<button class="show" id="stageBtn" type="button" aria-label="Canvases: the mode, the CPU difficulty, and your vote">')
rep("  $('lobbyStage').textContent = TH.label; const art = stageArt();", "  $('lobbyStage').textContent = TH.label; $('lobbyPickLbl').textContent = mode === 'solo' ? 'Canvases \\u00b7 your canvas' : 'Canvases \\u00b7 your vote'; const art = stageArt();")
# the vote itself: your card is tagged, and the draw is said up front
rep("$('vvLbl').textContent = 'Vote for a canvas';", "$('vvLbl').textContent = 'Vote for a canvas \\u00b7 one vote is drawn';")
css = '''
/* the canvas you chose is your vote, and the vote says so */
.vt{padding-bottom:16px}
.vt.mine::after{content:"Your vote";position:absolute;left:50%;bottom:0;transform:translateX(-50%);font:900 8.5px/1 var(--font-head);letter-spacing:.08em;text-transform:uppercase;color:var(--black);background:var(--gold);padding:3px 6px;border-radius:4px;border:1.5px solid var(--black);white-space:nowrap;box-shadow:1px 1px 0 var(--black)}
.snote b{color:var(--cream)}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
