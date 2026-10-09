#!/usr/bin/env python3
"""A polish pass: How to play covers the items and the orb's two gifts; Escape closes the commissions board. On top of ui41_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui41_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# How to play: a card for the pick-ups, and the orb's two gifts
rep('''<span class="cap">The orb</span></div><div><b>Go giant</b><p id="howOrb"></p></div></div>''',
    '''<span class="cap">The orb</span></div><div><b>Go giant</b><p id="howOrb"></p></div></div>
        <div class="pol"><div class="pic" style="--pc:#2ECC71"><span class="ink stroke"></span><span class="glyph sm">&#9733;</span><span class="cap">Pick-ups</span></div><div><b>Hold it, then use it</b><p id="howItems"></p></div></div>''')
rep("  $('howOrb').textContent = 'Roll up to the glowing orb (or jump into it) to go giant for 5 seconds. Roll into ' + riv + ' while you\\'re giant and it\\'s out.';",
    "  $('howOrb').textContent = 'Roll up to the glowing orb (or jump into it) for a super move: go giant for 5 seconds, or ride a rocket and come down like a giant\\'s pound. Roll into ' + riv + ' while you\\'re giant and it\\'s out.';\n  $('howItems').textContent = 'A roller or a turret turns up on the canvas now and then. Grab it and it waits in your hand: ' + say('tap its button', 'press F') + ' when you want it. The roller lays wide stripes and refills you; the turret plants you and fires paint. Picking up another drops the one you hold.';")
# Escape closes the commissions board like the other sheets
rep("  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }",
    "  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }\n  if (!$('commModal').hidden) { if (k === 'Escape' || k === 'Backspace') { e.preventDefault(); closeComms(); } return; }")
rep('<p class="ver">Version 111</p>', '<p class="ver">Version 112</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
