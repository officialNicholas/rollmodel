#!/usr/bin/env python3
"""The lineup chips leave the lobby. On top of ui17_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui17_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('        <div class="lineup" id="lineup" aria-label="Who\'s in the exhibition"></div>\n', '')
rep("  const lu = [swatchOf(P, playerName(), true)]; if (mode !== 'solo') { lu.push('<span class=\"vs\">vs</span>', swatchOf(H, NAMES[1], false)); if (mode === 'trio') lu.push(swatchOf(H2, NAMES[2], false)); }\n  $('lineup').innerHTML = lu.join('');\n", '')
rep("if (typeof renderLobbyUI === 'function' && $('lineup')) renderLobbyUI();", "if (typeof renderLobbyUI === 'function' && $('lobbyStage')) renderLobbyUI();")
# the bottom block is just the canvas pick and Play now, kept to the right in landscape
rep('  .lbot{display:grid;grid-template-columns:minmax(0,1fr) auto;grid-template-areas:"lineup go";width:100%;gap:14px;align-items:end}\n  .lineup{grid-area:lineup;justify-content:flex-start;padding-left:4px}\n', '  .lbot{display:grid;grid-template-columns:minmax(0,1fr) auto;grid-template-areas:"lineup go";width:100%;gap:14px;align-items:end}\n')
rep('<p class="ver">Version 87</p>', '<p class="ver">Version 88</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
